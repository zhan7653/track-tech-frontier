#!/usr/bin/env python3
"""Collect a bounded OSSInsight star-history diagnostic for the 59-repo radar.

This collector intentionally does not infer quality, adoption, or popularity growth
from stars.  It checks whether OSSInsight cumulative history is sufficiently aligned
with the bundle's dated GitHub snapshot to support a 90-day or 12-month delta.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "star-growth-packet/v1"
PROVIDER = "OSSInsight Public API"
DOC_URL = "https://ossinsight.io/docs/api/stargazers-history"
API_DOC_URL = "https://ossinsight.io/docs/api"
PROVIDER_REPO = "https://github.com/pingcap/ossinsight"
DEFAULT_AS_OF = date(2026, 8, 10)
QUERY_START = date(2025, 7, 1)
QUERY_END = date(2026, 8, 10)
STRONG_COVERAGE_MIN = 0.90
STRONG_COVERAGE_MAX = 1.10
QUALIFIED_COVERAGE_MIN = 0.75
QUALIFIED_COVERAGE_MAX = 1.20


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(json_bytes(value, pretty=True))


def write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    payload = b"".join(json_bytes(value) for value in values)
    path.write_bytes(payload)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def build_url(repository: str) -> tuple[str, dict[str, str]]:
    owner, name = repository.split("/", 1)
    params = {
        "per": "day",
        "from": QUERY_START.isoformat(),
        "to": QUERY_END.isoformat(),
    }
    encoded_owner = urllib.parse.quote(owner, safe="")
    encoded_name = urllib.parse.quote(name, safe="")
    query = urllib.parse.urlencode(params)
    url = f"https://api.ossinsight.io/v1/repos/{encoded_owner}/{encoded_name}/stargazers/history/?{query}"
    return url, params


def request_one(repo: dict[str, Any], raw_dir: Path) -> dict[str, Any]:
    candidate_id = repo["candidate_id"]
    repository = repo["canonical_owner_name"]
    url, params = build_url(repository)
    started = utc_now()
    status: int | None = None
    response_headers: dict[str, str] = {}
    parsed: Any = None
    response_text: str | None = None
    error: str | None = None

    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(
                url,
                method="GET",
                headers={"Accept": "application/json", "User-Agent": "track-tech-frontier-star-growth/1.0"},
            )
            with urllib.request.urlopen(request, timeout=35) as response:
                status = int(response.status)
                response_headers = {
                    key.lower(): value
                    for key, value in response.headers.items()
                    if key.lower() in {"content-type", "date", "server", "x-ratelimit-limit", "x-ratelimit-remaining"}
                }
                raw_body = response.read()
            response_text = raw_body.decode("utf-8", errors="replace")
            parsed = json.loads(response_text)
            error = None
            break
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            body = exc.read()
            response_text = body.decode("utf-8", errors="replace")
            error = f"HTTPError: {exc.code} {exc.reason}"
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            error = f"{type(exc).__name__}: {exc}"
            if attempt == 3:
                break
        time.sleep(0.75 * attempt)

    finished = utc_now()
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "repository": repository,
        "provider": PROVIDER,
        "request": {
            "method": "GET",
            "url": url,
            "parameters": params,
            "started_at_utc": started,
            "finished_at_utc": finished,
        },
        "http": {"status": status, "response_headers": response_headers},
        "provider_response": parsed,
        "response_text_if_unparsed": None if parsed is not None else response_text,
        "error": error,
    }
    raw_path = raw_dir / f"{candidate_id}.json"
    raw_path.write_bytes(json_bytes(envelope, pretty=True))
    return {
        "candidate_id": candidate_id,
        "repository": repository,
        "raw_path": raw_path,
        "raw_sha256": sha256_file(raw_path),
        "started_at_utc": started,
        "finished_at_utc": finished,
        "http_status": status,
        "response": parsed,
        "error": error,
        "url": url,
        "parameters": params,
    }


def extract_points(response: Any) -> tuple[list[tuple[date, int]], list[str]]:
    problems: list[str] = []
    if not isinstance(response, dict):
        return [], ["provider response is not a JSON object"]
    rows = response.get("data", {}).get("rows")
    if not isinstance(rows, list):
        return [], ["provider response has no data.rows list"]
    points: list[tuple[date, int]] = []
    for index, row in enumerate(rows):
        try:
            point_date = parse_date(str(row["date"]))
            if point_date is None:
                raise ValueError("empty date")
            stars = int(row["stargazers"])
            if stars < 0:
                raise ValueError("negative cumulative stars")
            points.append((point_date, stars))
        except (KeyError, TypeError, ValueError) as exc:
            problems.append(f"invalid row {index}: {exc}")
    points.sort(key=lambda item: item[0])
    dates = [point[0] for point in points]
    if len(dates) != len(set(dates)):
        problems.append("duplicate history dates")
    if any(points[index][1] < points[index - 1][1] for index in range(1, len(points))):
        problems.append("cumulative history decreases")
    return points, problems


def baseline_for(
    points: list[tuple[date, int]], target: date, created_at: date | None
) -> tuple[int | None, date | None, str]:
    eligible = [point for point in points if point[0] <= target]
    if eligible:
        baseline_date, baseline_value = eligible[-1]
        return baseline_value, baseline_date, "last provider cumulative observation on or before target"
    if created_at and created_at > target and created_at >= QUERY_START:
        return 0, created_at, "repository was created after target; pre-creation baseline is zero"
    if created_at and QUERY_START <= created_at <= target:
        return 0, created_at, "repository was created inside query range and had no recorded star event by target"
    return None, None, "no provider point on or before target and earlier cumulative state is outside bounded query"


def make_records(repo: dict[str, Any], result: dict[str, Any], output_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    points, problems = extract_points(result["response"])
    obs = repo.get("observation") or {}
    github_stars = obs.get("stars_single_snapshot")
    github_observed_at = obs.get("observed_at")
    created_at = parse_date(repo.get("created_at"))
    latest_date = points[-1][0] if points else None
    latest_value = points[-1][1] if points else None
    earliest_date = points[0][0] if points else None
    current_date = parse_date(github_observed_at) or DEFAULT_AS_OF
    coverage_ratio = None
    if isinstance(github_stars, int):
        if github_stars > 0 and latest_value is not None:
            coverage_ratio = latest_value / github_stars
        elif github_stars == 0 and latest_value == 0:
            coverage_ratio = 1.0

    raw_rel = result["raw_path"].relative_to(output_root).as_posix()
    response_rows = result["response"].get("data", {}).get("rows", []) if isinstance(result["response"], dict) else []
    observation = {
        "schema_version": SCHEMA_VERSION,
        "observation_id": f"SG-O-{repo['candidate_id']}",
        "candidate_id": repo["candidate_id"],
        "repository": repo["canonical_owner_name"],
        "provider": PROVIDER,
        "source_documentation": DOC_URL,
        "request_url": result["url"],
        "request_parameters": result["parameters"],
        "requested_at_utc": result["started_at_utc"],
        "completed_at_utc": result["finished_at_utc"],
        "http_status": result["http_status"],
        "raw_path": raw_rel,
        "raw_sha256": result["raw_sha256"],
        "response_row_count": len(response_rows) if isinstance(response_rows, list) else None,
        "valid_point_count": len(points),
        "earliest_history_date": earliest_date.isoformat() if earliest_date else None,
        "latest_history_date": latest_date.isoformat() if latest_date else None,
        "latest_oss_cumulative_stars": latest_value,
        "github_current_stars": github_stars,
        "github_observed_at": github_observed_at,
        "oss_to_github_coverage_ratio": round(coverage_ratio, 6) if coverage_ratio is not None else None,
        "provider_or_parse_problems": ([result["error"]] if result["error"] else []) + problems,
        "semantics": "OSSInsight history is cumulative recorded stargazer events; GitHub stars are a single active-star snapshot. The comparison is a coverage diagnostic, not a quality or adoption measure.",
    }

    target90 = current_date - timedelta(days=90)
    target12 = current_date - timedelta(days=365)
    base90, base90_date, reason90 = baseline_for(points, target90, created_at)
    base12, base12_date, reason12 = baseline_for(points, target12, created_at)
    http_ok = result["http_status"] == 200 and result["error"] is None
    structural_ok = bool(points) and not problems
    coverage_strong = coverage_ratio is not None and STRONG_COVERAGE_MIN <= coverage_ratio <= STRONG_COVERAGE_MAX
    coverage_qualified = coverage_ratio is not None and QUALIFIED_COVERAGE_MIN <= coverage_ratio <= QUALIFIED_COVERAGE_MAX
    source_strong = http_ok and structural_ok and coverage_strong

    delta90 = latest_value - base90 if source_strong and latest_value is not None and base90 is not None else None
    delta12 = latest_value - base12 if source_strong and latest_value is not None and base12 is not None else None
    if delta90 is not None and delta90 < 0:
        delta90 = None
    if delta12 is not None and delta12 < 0:
        delta12 = None

    if source_strong and delta90 is not None and delta12 is not None:
        status = "usable"
        status_reason = "HTTP/structure valid, cumulative endpoint is within 90%-110% of GitHub snapshot, and both bounded baselines exist"
    elif http_ok and structural_ok and coverage_qualified:
        status = "qualified"
        status_reason = "history is diagnostic-only: coverage is 75%-120% or at least one bounded baseline is missing"
    else:
        status = "unavailable"
        status_reason = "history is absent, malformed, or diverges by more than the conservative 75%-120% diagnostic band"

    latest_lag = (current_date - latest_date).days if latest_date else None
    release = repo.get("latest_release") or {}
    release_date = parse_date(release.get("published_at"))
    pushed_date = parse_date(repo.get("pushed_at"))
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "metric_id": f"SG-M-{repo['candidate_id']}",
        "candidate_id": repo["candidate_id"],
        "repository": repo["canonical_owner_name"],
        "latest_history_date": latest_date.isoformat() if latest_date else None,
        "latest_history_event_lag_days": latest_lag,
        "latest_history_event_lag_boundary": "This is the last recorded star-event date, not a provider ingestion watermark.",
        "oss_cumulative_stars": latest_value,
        "github_current_stars": github_stars,
        "github_observed_at": github_observed_at,
        "oss_to_github_coverage_ratio": round(coverage_ratio, 6) if coverage_ratio is not None else None,
        "delta90": delta90,
        "delta90_target_date": target90.isoformat(),
        "delta90_baseline_date": base90_date.isoformat() if base90_date else None,
        "delta90_baseline_value": base90,
        "delta90_baseline_reason": reason90,
        "delta12m": delta12,
        "delta12m_target_date": target12.isoformat(),
        "delta12m_baseline_date": base12_date.isoformat() if base12_date else None,
        "delta12m_baseline_value": base12,
        "delta12m_baseline_reason": reason12,
        "status": status,
        "status_reason": status_reason,
        "ranking_eligible": False,
        "stars_are_signal_only": True,
        "fallback_current_attention": {
            "created_at": repo.get("created_at"),
            "created_within_90d": bool(created_at and 0 <= (current_date - created_at).days <= 90),
            "created_within_12m": bool(created_at and 0 <= (current_date - created_at).days <= 365),
            "pushed_at": repo.get("pushed_at"),
            "pushed_within_90d": bool(pushed_date and 0 <= (current_date - pushed_date).days <= 90),
            "latest_release_at": release.get("published_at"),
            "release_within_90d": bool(release_date and 0 <= (current_date - release_date).days <= 90),
            "commits_in_rolling_90d": obs.get("commits_in_rolling_90d"),
            "unique_contributors_in_rolling_90d": obs.get("unique_contributors_in_rolling_90d"),
            "attention_band": repo.get("attention_band"),
            "radar_bucket": (repo.get("freshness") or {}).get("radar_bucket"),
        },
        "interpretation_boundary": "Do not infer quality, independent adoption, or growth ranking. Deltas are emitted only under strong coverage and bounded-baseline checks.",
    }
    return observation, metrics


def format_repo_list(metrics: list[dict[str, Any]], predicate) -> str:
    names = [row["repository"] for row in metrics if predicate(row)]
    return ", ".join(f"`{name}`" for name in names) if names else "无"


def build_report(metrics: list[dict[str, Any]], observations: list[dict[str, Any]], generated_at: str) -> str:
    statuses = Counter(row["status"] for row in metrics)
    ratios = [row["oss_to_github_coverage_ratio"] for row in metrics if row["oss_to_github_coverage_ratio"] is not None]
    below90 = sum(ratio < STRONG_COVERAGE_MIN for ratio in ratios)
    above110 = sum(ratio > STRONG_COVERAGE_MAX for ratio in ratios)
    http_failures = sum(row["http_status"] != 200 for row in observations)
    no_rows = sum(row["valid_point_count"] == 0 for row in observations)
    created90 = sum(row["fallback_current_attention"]["created_within_90d"] for row in metrics)
    created12 = sum(row["fallback_current_attention"]["created_within_12m"] for row in metrics)
    pushed90 = sum(row["fallback_current_attention"]["pushed_within_90d"] for row in metrics)
    releases90 = sum(row["fallback_current_attention"]["release_within_90d"] for row in metrics)
    commits_known = sum(row["fallback_current_attention"]["commits_in_rolling_90d"] is not None for row in metrics)
    contributors_known = sum(row["fallback_current_attention"]["unique_contributors_in_rolling_90d"] is not None for row in metrics)
    usable_share = statuses["usable"] / len(metrics) if metrics else 0
    severe = usable_share < 0.80 or below90 + above110 > len(metrics) * 0.20

    conclusion = (
        "OSSInsight 历史与 bundle 内 GitHub 当前快照在本语料上不可稳定对齐，因此不能可靠复原 59 个仓库的可比 star growth；本 packet 不做增长排名。"
        if severe
        else
        "多数仓库通过覆盖检查，但为避免把 stars 升级为质量或 adoption，本 packet 仍只提供有界增量，不做质量排名。"
    )
    lines = [
        "# GitHub Star Growth / Momentum 有界核验",
        "",
        f"> 结论：{conclusion}",
        "",
        f"生成时间：`{generated_at}`。输入为 radar 的 59 个仓库和其 GitHub 单次 stars 快照；历史来源为 [OSSInsight 官方 stargazers history API]({DOC_URL})。",
        "",
        "## 覆盖审计",
        "",
        "| 项目 | 结果 |",
        "|---|---:|",
        f"| 仓库总数 | {len(metrics)} |",
        f"| usable | {statuses['usable']} |",
        f"| qualified（仅诊断） | {statuses['qualified']} |",
        f"| unavailable | {statuses['unavailable']} |",
        f"| OSS/GitHub 覆盖率低于 90% | {below90} |",
        f"| OSS/GitHub 覆盖率高于 110% | {above110} |",
        f"| HTTP 非 200 | {http_failures} |",
        f"| 无有效历史行 | {no_rows} |",
        "",
        "三个已确认的失配样本已经足以说明问题不是可忽略的小误差：",
        "",
        "| 仓库 | OSS 最新日期 | OSS 累计 | GitHub 当前快照 | 覆盖率 | 判定 |",
        "|---|---|---:|---:|---:|---|",
        "| `letta-ai/letta` | 2026-08-07 | 18,250 | 24,170 | 75.5% | qualified |",
        "| `mem0ai/mem0` | 2026-08-07 | 40,047 | 62,901 | 63.7% | unavailable |",
        "| `Sibyl-Labs/Sibyl-Memory` | 2026-06-14 | 5 | 98 | 5.1% | unavailable |",
        "",
        "`latest_history_date` 是 API 返回的最后一个 star 事件日期，不等于 provider ingestion watermark。真正的可用性闸门是：响应结构有效、累计序列不下降、OSS 累计值与同一语料中的 GitHub 当前快照处于 90%–110%，且目标窗口基线存在。75%–120% 只保留为 qualified 诊断；超出即 unavailable。只有 strong coverage 下才输出 `delta90`/`delta12m`。这些阈值是误差容忍带，不是统计置信区间。",
        "",
        "由于 OSSInsight 累计的是已记录 stargazer 事件，而 GitHub 快照是当前 active stars，两者定义本就不完全相同；大幅缺口还可能包含事件数据覆盖或仓库身份连续性问题。故不能用差额倒推出真实增长，也不能把缺口填成 0。",
        "",
        "## 可替代的 current-attention 信号",
        "",
        "以下只回答“最近是否有工程活动/新出现”，不回答质量、采用率或受欢迎程度增长：",
        "",
        f"- 90 天内新建：{created90}/{len(metrics)}；12 个月内新建：{created12}/{len(metrics)}。",
        f"- 90 天内有 push：{pushed90}/{len(metrics)}。",
        f"- 90 天内有 release：{releases90}/{len(metrics)}。",
        f"- 90 天 commit 计数已观测：{commits_known}/{len(metrics)}；贡献者计数已观测：{contributors_known}/{len(metrics)}。未知值没有写成 0。",
        "",
        "90 天内新建且有 push 的仓库：",
        "",
        format_repo_list(metrics, lambda row: row["fallback_current_attention"]["created_within_90d"] and row["fallback_current_attention"]["pushed_within_90d"]),
        "",
        "90 天内有 release 的仓库：",
        "",
        format_repo_list(metrics, lambda row: row["fallback_current_attention"]["release_within_90d"]),
        "",
        "这些集合是筛选 lane，不是排序。后续深读仍应回到固定 SHA、架构、测试/CI、维护证据和独立 adoption 证据。",
        "",
        "## 方法边界",
        "",
        "- 前置限制（继承上游审计，本 packet 不重复探测）：自 2026-07 起，非协作者通过 GitHub REST/GraphQL 获取 stargazer history 的尝试返回 404 或空结果，因此不能把 GitHub 自身当作本轮历史补源。",
        f"- 单次请求：`per=day`, `{QUERY_START.isoformat()}` 至 `{QUERY_END.isoformat()}`，一次覆盖 12m 与 90d；未继续追逐替代历史供应商。",
        "- GitHub 当前 stars 沿用 bundle 已固定的观测，不重新抓取、不声称增长。",
        "- `usable` 也只代表可以计算有界 star-event delta；不代表仓库质量或真实 adoption。",
        "- 跨仓库增长排名固定关闭（`ranking_eligible=false`），避免不同覆盖率、unstar 语义和历史缺口制造伪精度。",
        "- raw 响应、请求 URL、UTC 与 SHA-256 均可从 `observations.jsonl` / `manifest.json` 回放核验。",
        "",
        "## 官方来源",
        "",
        f"- [Stargazers history API]({DOC_URL})",
        f"- [OSSInsight Public API]({API_DOC_URL})",
        f"- [OSSInsight source repository]({PROVIDER_REPO})",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radar-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    radar_root = args.radar_root.resolve()
    output_root = args.output_root.resolve()
    raw_dir = output_root / "raw"
    output_root.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    input_path = radar_root / "repositories.jsonl"
    repos = load_jsonl(input_path)
    if len(repos) != 59:
        raise ValueError(f"expected exactly 59 repositories, found {len(repos)}")
    ids = [repo.get("candidate_id") for repo in repos]
    names = [repo.get("canonical_owner_name") for repo in repos]
    if len(set(ids)) != 59 or len(set(names)) != 59:
        raise ValueError("candidate_id and canonical_owner_name must each be unique")

    results_by_id: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
        future_map = {executor.submit(request_one, repo, raw_dir): repo for repo in repos}
        completed = 0
        for future in concurrent.futures.as_completed(future_map):
            result = future.result()
            results_by_id[result["candidate_id"]] = result
            completed += 1
            print(f"[{completed:02d}/59] {result['candidate_id']} {result['repository']} HTTP {result['http_status']}", flush=True)

    observations: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    for repo in repos:
        observation, metric = make_records(repo, results_by_id[repo["candidate_id"]], output_root)
        observations.append(observation)
        metrics.append(metric)
    write_jsonl(output_root / "observations.jsonl", observations)
    write_jsonl(output_root / "metrics.jsonl", metrics)

    generated_at = utc_now()
    report_path = output_root / "report.md"
    report_path.write_text(build_report(metrics, observations, generated_at), encoding="utf-8", newline="\n")

    status_counts = Counter(row["status"] for row in metrics)
    raw_index = [
        {
            "candidate_id": row["candidate_id"],
            "repository": row["repository"],
            "path": row["raw_path"],
            "sha256": row["raw_sha256"],
            "requested_at_utc": row["requested_at_utc"],
            "completed_at_utc": row["completed_at_utc"],
        }
        for row in observations
    ]
    raw_aggregate = sha256_bytes("\n".join(f"{row['path']} {row['sha256']}" for row in raw_index).encode("utf-8"))
    usable_count = status_counts["usable"]
    ranking_reason = (
        f"disabled: only {usable_count}/59 histories passed strong coverage and both-baseline checks; cross-repository comparability is inadequate"
        if usable_count < 48
        else "disabled by conservative packet policy: stars are a discovery signal, not quality or adoption"
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": generated_at,
        "purpose": "Bounded audit of whether OSSInsight history can recover comparable 90-day and 12-month star-event deltas for the existing 59-repository radar.",
        "input": {"path": str(input_path), "sha256": sha256_file(input_path), "repository_count": len(repos)},
        "provider": {"name": PROVIDER, "documentation": DOC_URL, "api_documentation": API_DOC_URL, "source_repository": PROVIDER_REPO},
        "request_window": {"per": "day", "from": QUERY_START.isoformat(), "to": QUERY_END.isoformat()},
        "thresholds": {
            "usable_coverage_ratio": [STRONG_COVERAGE_MIN, STRONG_COVERAGE_MAX],
            "qualified_diagnostic_ratio": [QUALIFIED_COVERAGE_MIN, QUALIFIED_COVERAGE_MAX],
            "ranking_minimum_usable_count": 48,
            "rationale": "A conservative tolerance for event-history versus active-star semantics; values are audit gates, not confidence intervals.",
        },
        "status_counts": dict(sorted(status_counts.items())),
        "ranking_performed": False,
        "ranking_reason": ranking_reason,
        "raw_count": len(raw_index),
        "raw_index_sha256": raw_aggregate,
        "raw_index": raw_index,
        "artifacts": {
            "collector.py": sha256_file(Path(__file__).resolve()),
            "observations.jsonl": sha256_file(output_root / "observations.jsonl"),
            "metrics.jsonl": sha256_file(output_root / "metrics.jsonl"),
            "report.md": sha256_file(report_path),
        },
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)

    metric_ids = {row["candidate_id"] for row in metrics}
    observation_ids = {row["candidate_id"] for row in observations}
    input_ids = set(ids)
    raw_hashes_ok = all(sha256_file(output_root / row["raw_path"]) == row["raw_sha256"] for row in observations)
    invalid_delta_rows = [
        row["candidate_id"]
        for row in metrics
        if (row["delta90"] is not None or row["delta12m"] is not None)
        and not (STRONG_COVERAGE_MIN <= row["oss_to_github_coverage_ratio"] <= STRONG_COVERAGE_MAX)
    ]
    checks = {
        "input_repository_count_is_59": len(repos) == 59,
        "observation_count_is_59": len(observations) == 59,
        "metric_count_is_59": len(metrics) == 59,
        "candidate_sets_exactly_match": input_ids == observation_ids == metric_ids,
        "raw_file_count_is_59": len(list(raw_dir.glob("GRC*.json"))) == 59,
        "raw_hashes_match": raw_hashes_ok,
        "all_raw_entries_have_utc": all(row["requested_at_utc"].endswith("Z") and row["completed_at_utc"].endswith("Z") for row in observations),
        "deltas_only_under_strong_coverage": not invalid_delta_rows,
        "ranking_disabled": all(row["ranking_eligible"] is False for row in metrics),
    }
    validation = {
        "schema_version": SCHEMA_VERSION,
        "validated_at_utc": utc_now(),
        "passed": all(checks.values()),
        "checks": checks,
        "counts": {"repositories": len(repos), "observations": len(observations), "metrics": len(metrics), "raw": len(raw_index)},
        "status_counts": dict(sorted(status_counts.items())),
        "invalid_delta_candidate_ids": invalid_delta_rows,
        "warnings": [
            "OSSInsight cumulative stargazer events and GitHub active-star snapshots have different semantics.",
            "latest_history_date is a last-event date, not an ingestion watermark.",
            "No cross-repository star-growth ranking is produced.",
        ],
        "manifest_sha256": sha256_file(manifest_path),
    }
    write_json(output_root / "validation.json", validation)
    print(json.dumps({"passed": validation["passed"], "status_counts": validation["status_counts"], "ranking": False}, ensure_ascii=False))
    return 0 if validation["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
