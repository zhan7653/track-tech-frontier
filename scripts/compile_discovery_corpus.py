#!/usr/bin/env python3
"""Import replayable discovery JSONL into a schema-2.0 research bundle.

The importer is deliberately a breadth-stage tool. It writes queries,
discovery occurrences, and deduplicated entities; it never promotes an entity
past ``discovered`` or invents repository activity counters. GitHub repository
observations are imported only when the spec supplies a complete, API-derived
observation for a matching occurrence.

Spec shape (paths may be relative to the spec file)::

  {"queries": [{
    "query_id": "Q001", "occurrence_jsonl": "crossref.jsonl",
    "run_metadata": "crossref-run.json", "stage": "discover",
    "lanes": ["paper"], "windows": ["W12M"], "parents": [],
    "gaps": [], "information_gain": "Broad paper recall.",
    "repository_observations": [{"provider_result_id": "...", ...}]
  }]}

``repository_observations`` is optional. If present, every entry must contain
the schema's complete API-derived counters (including open issues, commits,
and contributors); omitted observations are reported as unmeasured in the
summary rather than represented as zero.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


QUERY_STAGES = {"pilot", "discover", "map", "gap-fill", "deep-focus", "verify", "adversarial", "refresh"}
QUERY_STATUSES = {"succeeded", "partial", "failed", "blocked"}
OBSERVATION_FIELDS = {
    "provider_result_id", "node_id", "owner_repo", "stars", "forks", "open_issues", "created", "pushed",
    "latest_release", "default_commit", "archived", "fork", "license", "commits_in_window",
    "contributors_in_window", "window_id", "api_url", "note", "observed_at",
}


class CompileError(RuntimeError):
    """A preflight failure; no bundle files have been changed yet."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_url(value: Any) -> bool:
    parsed = urlsplit(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme in {"http", "https"} and parsed.netloc)


def is_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def is_utc(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def _path(value: Any, base: Path, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise CompileError(f"{label} must be a non-empty path string")
    path = Path(value)
    return path if path.is_absolute() else base / path


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompileError(f"{label}: cannot read valid UTF-8 JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompileError(f"{label}: expected a JSON object")
    return value


def read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CompileError(f"{label}: cannot read {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CompileError(f"{label}:{number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise CompileError(f"{label}:{number}: expected a JSON object")
        rows.append(value)
    return rows


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


def _date_interval(value: Any) -> tuple[date | None, date | None, str, str | None]:
    """Return an internal interval; only provider-supplied full dates are output."""
    if type(value) is int and 1 <= value <= 9999:
        value = f"{value:04d}"
    if not isinstance(value, str) or not value:
        return None, None, "unknown", None
    value = value.strip()
    candidate = value[:10]
    if is_date(candidate) and (len(value) == 10 or value[10:11] in {"T", " "}):
        point = date.fromisoformat(candidate)
        return point, point, "exact", candidate
    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, number = (int(part) for part in value.split("-"))
        if 1 <= number <= 12:
            return date(year, number, 1), date(year, number, calendar.monthrange(year, number)[1]), "month", None
    if re.fullmatch(r"\d{4}", value):
        year = int(value)
        return date(year, 1, 1), date(year, 12, 31), "year", None
    return None, None, "unknown", None


def _confidence(values: list[str]) -> str:
    for value in ("exact", "month", "year", "unknown"):
        if value in values:
            return value
    return "unknown"


def _matching_windows(start: date, end: date, confidence: str, windows: dict[str, dict[str, Any]], as_of: date) -> list[str]:
    """Classify an evidence-date interval without overstating recency.

    Exact dates behave as points.  Month/year metadata must fit wholly inside a
    recent window, whose effective end is also capped at the bundle as-of date.
    Foundational/established/custom windows remain interval classifications and
    therefore use ordinary overlap.
    """
    matches = []
    for window_id, window in windows.items():
        window_start, window_end = window.get("start"), window.get("end")
        if not is_date(window_start) or not is_date(window_end):
            raise CompileError(f"time_windows.jsonl: {window_id!r} must have ISO start/end dates")
        lower, upper = date.fromisoformat(window_start), date.fromisoformat(window_end)
        if window.get("kind") in {"recent-12m", "recent-90d"}:
            upper = min(upper, as_of)
            matched = lower <= start <= upper if confidence == "exact" else lower <= start and end <= upper
        else:
            matched = lower <= end and start <= upper
        if matched:
            matches.append(window_id)
    return matches


def _classified_windows(date_infos: list[tuple[date, date, str, str | None, str]],
                        windows: dict[str, dict[str, Any]], as_of: date) -> list[str]:
    return list(dict.fromkeys(
        window_id
        for start, end, confidence, _exact, _raw in date_infos
        for window_id in _matching_windows(start, end, confidence, windows, as_of)
    ))


def _list_of_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise CompileError(f"{label} must be a list of non-empty strings")
    return value


def _jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records).encode("utf-8")


def _atomic_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(handle, "wb") as output:
            output.write(_jsonl_bytes(records))
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _existing(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path, path.name) if path.is_file() else []


def _index(rows: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise CompileError(f"{label}: existing record has no usable {key}")
        if value in result:
            raise CompileError(f"{label}: duplicate existing {key} {value!r}")
        result[value] = row
    return result


def _run_requests(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    requests = metadata.get("requests")
    return [item for item in requests if isinstance(item, dict)] if isinstance(requests, list) else []


def _query_from_spec(spec: dict[str, Any], metadata: dict[str, Any], occurrence_count: int, known_queries: set[str], known_lanes: set[str], known_windows: set[str], known_clusters: set[str], known_gaps: set[str]) -> dict[str, Any]:
    query_id = spec.get("query_id")
    if not isinstance(query_id, str) or not query_id:
        raise CompileError("query spec: query_id must be a non-empty string")
    if query_id in known_queries:
        raise CompileError(f"query spec {query_id}: query_id already exists; refusing to overwrite prior discovery")
    stage = spec.get("stage")
    if stage not in QUERY_STAGES:
        raise CompileError(f"query spec {query_id}: stage must be one of {', '.join(sorted(QUERY_STAGES))}")
    lanes = _list_of_strings(spec.get("lanes"), f"query spec {query_id}.lanes")
    windows = _list_of_strings(spec.get("windows"), f"query spec {query_id}.windows")
    parents = _list_of_strings(spec.get("parents", []), f"query spec {query_id}.parents") if spec.get("parents", []) else []
    gaps = _list_of_strings(spec.get("gaps", []), f"query spec {query_id}.gaps") if spec.get("gaps", []) else []
    clusters = _list_of_strings(spec.get("clusters", []), f"query spec {query_id}.clusters") if spec.get("clusters", []) else []
    if any(value not in known_lanes for value in lanes):
        raise CompileError(f"query spec {query_id}: lanes must already be declared in research_plan.json")
    if any(value not in known_windows for value in windows):
        raise CompileError(f"query spec {query_id}: windows must already exist in time_windows.jsonl")
    if any(value not in known_queries for value in parents) or query_id in parents:
        raise CompileError(f"query spec {query_id}: parents must be earlier bundle/spec query IDs and cannot self-reference")
    if any(value not in known_gaps for value in gaps):
        raise CompileError(f"query spec {query_id}: gaps must already exist in gaps.jsonl")
    if any(value not in known_clusters for value in clusters):
        raise CompileError(f"query spec {query_id}: clusters must already exist in clusters.jsonl")
    requests = _run_requests(metadata)
    provider = spec.get("provider", metadata.get("provider"))
    query_text = spec.get("query_text", metadata.get("query"))
    request_url = spec.get("request_url") or next((item.get("url") for item in requests if is_url(item.get("url"))), None)
    status = spec.get("status", metadata.get("status", "succeeded"))
    note = spec.get("result_count_note", metadata.get("result_count_note", ""))
    if not isinstance(provider, str) or not provider or not isinstance(query_text, str) or not query_text or status not in QUERY_STATUSES:
        raise CompileError(f"query spec {query_id}: provider, query_text, and status are required")
    if request_url is not None and not is_url(request_url):
        raise CompileError(f"query spec {query_id}: request_url must be an HTTP(S) URL or null")
    executed_at = spec.get("executed_at") or metadata.get("started_at") or next((item.get("observed_at") for item in requests if is_utc(item.get("observed_at"))), None) or metadata.get("finished_at")
    if not is_utc(executed_at):
        raise CompileError(f"query spec {query_id}: run metadata needs a UTC started_at/finished_at or request observed_at")
    raw_paths = [item.get("raw_snapshot_path") for item in requests if isinstance(item.get("raw_snapshot_path"), str) and item["raw_snapshot_path"]]
    if not isinstance(note, str):
        raise CompileError(f"query spec {query_id}: result_count_note must be a string")
    if status in {"failed", "partial", "blocked"} and not note.strip():
        note = f"Imported {status} run metadata; no result count is inferred from missing occurrences."
    if not note:
        note = f"Imported {occurrence_count} discovery occurrence(s) from replayable provider metadata."
    iteration = spec.get("iteration", 1)
    if type(iteration) is not int or iteration < 1 or not isinstance(spec.get("information_gain"), str) or not spec["information_gain"].strip():
        raise CompileError(f"query spec {query_id}: iteration must be positive and information_gain must be non-empty")
    return {"query_id": query_id, "stage": stage, "iteration": iteration, "provider": provider, "query_text": query_text,
            "request_url": request_url, "status": status, "raw_snapshot_paths": raw_paths, "target_lanes": lanes,
            "target_window_ids": windows, "target_cluster_ids": clusters, "parent_query_ids": parents, "gap_ids": gaps,
            "information_gain": spec["information_gain"], "executed_at": executed_at, "result_count": occurrence_count,
            "result_count_note": note}


def _occurrence(record: dict[str, Any], query: dict[str, Any], source_path: Path) -> tuple[dict[str, Any], str, dict[str, Any]]:
    entity = record.get("entity")
    if not isinstance(entity, dict):
        raise CompileError(f"{source_path}: occurrence lacks object entity")
    provider = record.get("provider", query["provider"])
    title, url = entity.get("title"), entity.get("url")
    observed_at = record.get("observed_at")
    if not isinstance(provider, str) or not provider or not isinstance(title, str) or not title.strip() or not is_url(url) or not is_utc(observed_at):
        raise CompileError(f"{source_path}: occurrence requires provider, entity title/http URL, and UTC observed_at")
    dedupe_key = entity.get("dedupe_key")
    if not isinstance(dedupe_key, str) or not dedupe_key:
        raise CompileError(f"{source_path}: occurrence entity lacks dedupe_key; run normalize before compilation")
    raw_id = str(record.get("raw_id") or entity.get("provider_id") or entity.get("node_id") or "")
    if not raw_id:
        raise CompileError(f"{source_path}: occurrence lacks raw/provider result ID")
    request = record.get("request") if isinstance(record.get("request"), dict) else {}
    discovery_id = _stable_id("D", query["query_id"], provider, raw_id, str(record.get("rank", "")), str(observed_at), str(url))
    result = {"discovery_id": discovery_id, "query_id": query["query_id"], "provider": provider, "provider_result_id": raw_id,
              "title": title.strip(), "url": url, "identifier": dedupe_key, "observed_at": observed_at, "rank": record.get("rank"),
              "page_cursor": {"page": request.get("page"), "cursor": request.get("cursor")},
              "metadata": {"dedupe_key": dedupe_key, "possible_duplicate": bool(entity.get("possible_duplicate")), "request": request,
                           "source_occurrence_jsonl": str(source_path), "entity": entity}}
    return result, dedupe_key, entity


def _entity(entity_id: str, key: str, candidates: list[tuple[dict[str, Any], dict[str, Any], list[str]]],
            windows: dict[str, dict[str, Any]], as_of: date, now: str,
            prior: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge occurrences, deriving windows from dates rather than query scope."""
    if not candidates:
        raise CompileError(f"entity {entity_id}: no discovery candidates")
    first_discovery, first_source, _first_targets = candidates[0]
    kind = first_source.get("kind")
    entity_type = "repository" if kind == "repository" else "paper" if kind == "paper" else "other"
    aliases = {str(item) for item in (prior or {}).get("aliases", []) if isinstance(item, str) and item}
    aliases.update(discovery["title"] for discovery, _source, _targets in candidates)
    discovery_ids = list((prior or {}).get("discovery_ids", [])) + [discovery["discovery_id"] for discovery, _source, _targets in candidates]
    if prior is not None and prior.get("identifier") not in {None, key}:
        raise CompileError(f"entity {entity_id}: deterministic ID collides with a different identifier")

    date_infos: list[tuple[date, date, str, str | None, str]] = []
    observed_raw_dates: set[str] = set()
    for _discovery, source, _targets in candidates:
        raw_candidates = ([source.get("created_at")] if source.get("kind") == "repository" else
                          [source.get("published_at"), source.get("year")])
        for raw_date in raw_candidates:
            if raw_date not in (None, ""):
                observed_raw_dates.add(str(raw_date))
            start, end, confidence, published = _date_interval(raw_date)
            if start is not None and end is not None:
                # Repository creation dates classify freshness but are not paper
                # publication dates, so never copy them into published_at.
                date_infos.append((start, end, confidence, published if source.get("kind") != "repository" else None, str(raw_date)))
                break
    if not date_infos and prior and prior.get("published_at"):
        start, end, confidence, published = _date_interval(prior.get("published_at"))
        if start is not None and end is not None:
            date_infos.append((start, end, confidence, published, str(prior["published_at"])))
            observed_raw_dates.add(str(prior["published_at"]))

    if not date_infos:
        # A query target describes search intent, not an entity date.  Unknown
        # dates remain empty and explicit so they cannot inflate freshness.
        time_window_ids = []
        confidence = "unknown"
        status = "unknown"
    else:
        time_window_ids = _classified_windows(date_infos, windows, as_of)
        confidence = _confidence([item[2] for item in date_infos])
        status = "classified" if time_window_ids else "known-unclassified"
    exact_published = next((published for _start, _end, _confidence_value, published, _raw in date_infos if published), None)
    result = {"entity_id": entity_id, "canonical_name": prior.get("canonical_name") if prior else first_discovery["title"],
             "url": prior.get("url") if prior else first_discovery["url"], "identifier": key, "aliases": sorted(aliases),
             "discovery_ids": list(dict.fromkeys(discovery_ids)), "stage": prior.get("stage", "discovered") if prior else "discovered",
             "published_at": prior.get("published_at") if prior else exact_published, "created_at": prior.get("created_at", now) if prior else now,
             "updated_at": now, "date_confidence": confidence, "time_window_ids": time_window_ids,
             "source_ids": list((prior or {}).get("source_ids", [])), "entity_type": prior.get("entity_type", entity_type) if prior else entity_type}
    basis = {"entity_id": entity_id, "entity_type": entity_type,
             "basis": "repository_created_at" if entity_type == "repository" else "paper_published_at",
             "raw_dates": sorted(observed_raw_dates), "parsed_raw_dates": sorted({item[4] for item in date_infos}),
             "date_confidence": confidence,
             "time_window_ids": time_window_ids, "status": status}
    return result, basis


def _observation(spec: dict[str, Any], entity_id: str, query: dict[str, Any], known_windows: set[str]) -> dict[str, Any]:
    missing = sorted(OBSERVATION_FIELDS - spec.keys())
    if missing:
        raise CompileError(f"query {query['query_id']} repository observation {spec.get('provider_result_id')!r}: incomplete API-derived observation; missing {', '.join(missing)}")
    if spec.get("window_id") not in known_windows or spec["window_id"] not in query["target_window_ids"]:
        raise CompileError(f"query {query['query_id']} repository observation: window_id must be one of the query windows")
    if not all(isinstance(spec.get(name), str) and spec[name] for name in ("provider_result_id", "node_id", "owner_repo", "note")) or not is_url(spec.get("api_url")) or not is_date(spec.get("created")) or not is_date(spec.get("pushed")) or not is_utc(spec.get("observed_at")):
        raise CompileError(f"query {query['query_id']} repository observation: IDs, API URL, dates, note, and observed_at are invalid")
    if any(type(spec.get(name)) is not int or spec[name] < 0 for name in ("stars", "forks", "open_issues", "commits_in_window", "contributors_in_window")) or not isinstance(spec.get("archived"), bool) or not isinstance(spec.get("fork"), bool):
        raise CompileError(f"query {query['query_id']} repository observation: counters must be API-derived non-negative integers and archived/fork booleans")
    result = {name: spec[name] for name in OBSERVATION_FIELDS - {"provider_result_id"}}
    result.update({"observation_id": _stable_id("O", query["query_id"], entity_id, spec["node_id"], spec["window_id"], spec["observed_at"]), "entity_id": entity_id})
    return result


def _normalized_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).split())


def _paper_duplicate_signature(source: dict[str, Any]) -> tuple[str, str, str] | None:
    """Build a conservative mapper-review signature, never an entity key."""
    if source.get("kind") != "paper" or source.get("doi") or source.get("arxiv_id"):
        return None
    title = _normalized_text(source.get("title"))
    if not title:
        return None
    authors = source.get("authors")
    author = ""
    if isinstance(authors, list) and authors:
        first = authors[0]
        if isinstance(first, dict):
            first = first.get("name") or " ".join(
                str(first.get(part) or "").strip() for part in ("given", "family")
            ).strip()
        author = _normalized_text(first)
    raw_year = source.get("year")
    if raw_year in (None, "") and isinstance(source.get("published_at"), str):
        raw_year = source["published_at"][:4]
    year = str(raw_year) if re.fullmatch(r"\d{4}", str(raw_year or "")) else ""
    return title, author, year


def _possible_duplicate_groups(discoveries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for discovery in discoveries:
        metadata = discovery.get("metadata") if isinstance(discovery.get("metadata"), dict) else {}
        source = metadata.get("entity") if isinstance(metadata.get("entity"), dict) else {}
        signature = _paper_duplicate_signature(source)
        if signature is None:
            continue
        identifier = discovery.get("identifier")
        if not isinstance(identifier, str) or not identifier:
            continue
        title, author, year = signature
        buckets.setdefault(title, []).append({
            "entity_id": _stable_id("E", identifier), "discovery_id": discovery.get("discovery_id"),
            "provider": discovery.get("provider"), "provider_result_id": discovery.get("provider_result_id"),
            "title": discovery.get("title"), "url": discovery.get("url"), "identifier": identifier,
            "normalized_first_author": author, "year": year,
        })
    groups: list[dict[str, Any]] = []
    for title, title_members in sorted(buckets.items()):
        author_choices = sorted({item["normalized_first_author"] for item in title_members if item["normalized_first_author"]}) or [""]
        year_choices = sorted({item["year"] for item in title_members if item["year"]}) or [""]
        # Missing author/year values are compatible with each populated anchor;
        # conflicting populated values are kept in separate review groups.
        candidate_groups: dict[tuple[str, ...], tuple[str, str, list[dict[str, Any]]]] = {}
        for author in author_choices:
            for year in year_choices:
                members = [item for item in title_members
                           if (not item["normalized_first_author"] or item["normalized_first_author"] == author)
                           and (not item["year"] or item["year"] == year)]
                entity_ids = tuple(sorted({item["entity_id"] for item in members}))
                providers = {str(item["provider"]) for item in members if item.get("provider")}
                if len(entity_ids) < 2 or len(providers) < 2:
                    continue
                previous = candidate_groups.get(entity_ids)
                if previous is None or bool(author) + bool(year) > bool(previous[0]) + bool(previous[1]):
                    candidate_groups[entity_ids] = (author, year, members)
        for entity_ids, (author, year, members) in sorted(candidate_groups.items()):
            providers = sorted({str(item["provider"]) for item in members if item.get("provider")})
            groups.append({
                "group_id": _stable_id("PD", title, author, year, *entity_ids),
                "normalized_title": title, "normalized_first_author": author or None, "year": year or None,
                "providers": providers, "entity_ids": list(entity_ids),
                "discovery_ids": sorted({str(item["discovery_id"]) for item in members if item.get("discovery_id")}),
                "candidates": members, "requires_mapper_review": True,
                "reason": "Cross-provider papers lack DOI/arXiv identity and have a matching normalized title with compatible available first-author/year metadata; they were not automatically merged.",
            })
    return groups


def _repository_freshness_basis(discoveries: list[dict[str, Any]], observations: list[dict[str, Any]],
                                windows: dict[str, dict[str, Any]], as_of: date) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int]]:
    grouped: dict[str, dict[str, Any]] = {}
    for discovery in discoveries:
        metadata = discovery.get("metadata") if isinstance(discovery.get("metadata"), dict) else {}
        source = metadata.get("entity") if isinstance(metadata.get("entity"), dict) else {}
        identifier = discovery.get("identifier")
        if source.get("kind") != "repository" or not isinstance(identifier, str) or not identifier:
            continue
        entity_id = _stable_id("E", identifier)
        item = grouped.setdefault(entity_id, {"entity_id": entity_id, "identifier": identifier,
                                               "discovery_ids": [], "created_at_values": set(), "pushed_at_values": set()})
        if discovery.get("discovery_id"):
            item["discovery_ids"].append(discovery["discovery_id"])
        for field, target in (("created_at", "created_at_values"), ("pushed_at", "pushed_at_values")):
            if isinstance(source.get(field), str) and source[field]:
                item[target].add(source[field])
    for observation in observations:
        entity_id = observation.get("entity_id")
        if not isinstance(entity_id, str) or entity_id not in grouped:
            continue
        for field, target in (("created", "created_at_values"), ("pushed", "pushed_at_values")):
            if isinstance(observation.get(field), str) and observation[field]:
                grouped[entity_id][target].add(observation[field])

    creation_counts = {window_id: 0 for window_id in windows}
    activity_counts = {window_id: 0 for window_id in windows}
    rows: list[dict[str, Any]] = []
    for entity_id, item in sorted(grouped.items()):
        classifications: dict[str, tuple[list[tuple[date, date, str, str | None, str]], list[str]]] = {}
        for label, values_key in (("creation", "created_at_values"), ("activity", "pushed_at_values")):
            infos = []
            for raw in sorted(item[values_key]):
                start, end, confidence, exact = _date_interval(raw)
                if start is not None and end is not None:
                    infos.append((start, end, confidence, exact, raw))
            classifications[label] = (infos, _classified_windows(infos, windows, as_of))
        creation_infos, creation_windows = classifications["creation"]
        activity_infos, activity_windows = classifications["activity"]
        for window_id in creation_windows:
            creation_counts[window_id] += 1
        for window_id in activity_windows:
            activity_counts[window_id] += 1
        recent_activity = [window_id for window_id in activity_windows
                           if windows[window_id].get("kind") in {"recent-12m", "recent-90d"}]
        rows.append({
            "entity_id": entity_id, "identifier": item["identifier"],
            "discovery_ids": list(dict.fromkeys(item["discovery_ids"])),
            "entity_freshness_basis": "repository_created_at",
            "created_at_values": sorted(item["created_at_values"]),
            "creation_date_confidence": _confidence([entry[2] for entry in creation_infos]) if creation_infos else "unknown",
            "creation_time_window_ids": creation_windows,
            "creation_status": "classified" if creation_windows else "known-unclassified" if creation_infos else "unknown",
            "activity_basis": "repository_pushed_at",
            "pushed_at_values": sorted(item["pushed_at_values"]),
            "activity_date_confidence": _confidence([entry[2] for entry in activity_infos]) if activity_infos else "unknown",
            "activity_time_window_ids": activity_windows, "recent_activity_window_ids": recent_activity,
            "activity_status": "classified" if activity_windows else "known-unclassified" if activity_infos else "unknown",
        })
    return rows, creation_counts, activity_counts


def compile_spec(bundle: Path, spec_path: Path, summary_path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    spec_document = read_json(spec_path, "spec")
    query_specs = spec_document.get("queries")
    if not isinstance(query_specs, list) or not query_specs or not all(isinstance(item, dict) for item in query_specs):
        raise CompileError("spec.queries must be a non-empty array of objects")
    if not bundle.is_dir():
        raise CompileError(f"bundle directory does not exist: {bundle}")
    plan = read_json(bundle / "research_plan.json", "research_plan.json")
    plan_as_of = plan.get("as_of")
    if plan_as_of is not None and not is_date(plan_as_of):
        raise CompileError("research_plan.json: as_of must be an ISO date when present")
    as_of = date.fromisoformat(plan_as_of) if isinstance(plan_as_of, str) else date.today()
    as_of_source = "research_plan.json" if isinstance(plan_as_of, str) else "compiler-current-date"
    known_lanes = set(plan.get("lanes", []))
    windows = _index(_existing(bundle / "time_windows.jsonl"), "window_id", "time_windows.jsonl"); known_windows = set(windows)
    known_clusters = set(_index(_existing(bundle / "clusters.jsonl"), "cluster_id", "clusters.jsonl"))
    known_gaps = set(_index(_existing(bundle / "gaps.jsonl"), "gap_id", "gaps.jsonl"))
    queries = _existing(bundle / "queries.jsonl"); discoveries = _existing(bundle / "discovery_results.jsonl")
    entities = _existing(bundle / "entities.jsonl"); observations = _existing(bundle / "repository_observations.jsonl")
    query_by_id = _index(queries, "query_id", "queries.jsonl"); discovery_by_id = _index(discoveries, "discovery_id", "discovery_results.jsonl")
    entity_by_id = _index(entities, "entity_id", "entities.jsonl"); observation_by_id = _index(observations, "observation_id", "repository_observations.jsonl")
    now = utc_now(); imported_queries: list[dict[str, Any]] = []; imported_discoveries: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []; pending_observations: list[dict[str, Any]] = []
    entity_candidates: dict[str, tuple[str, list[tuple[dict[str, Any], dict[str, Any], list[str]]]]] = {}
    for query_spec in query_specs:
        metadata_path = _path(query_spec.get("run_metadata"), spec_path.parent, "run_metadata")
        metadata = read_json(metadata_path, f"query run metadata {query_spec.get('query_id')!r}")
        occurrence_path_value = query_spec.get("occurrence_jsonl")
        status = query_spec.get("status", metadata.get("status", "succeeded"))
        if occurrence_path_value is None and status not in {"failed", "blocked"}:
            raise CompileError(f"query spec {query_spec.get('query_id')!r}: occurrence_jsonl is required unless status is failed/blocked")
        occurrence_path = _path(occurrence_path_value, spec_path.parent, "occurrence_jsonl") if occurrence_path_value is not None else None
        occurrence_rows = read_jsonl(occurrence_path, "occurrence_jsonl") if occurrence_path else []
        query = _query_from_spec(query_spec, metadata, len(occurrence_rows), set(query_by_id), known_lanes, known_windows, known_clusters, known_gaps)
        query_by_id[query["query_id"]] = query; imported_queries.append(query)
        occurrence_matches: dict[str, tuple[str, dict[str, Any]]] = {}
        for occurrence_row in occurrence_rows:
            discovery, key, source_entity = _occurrence(occurrence_row, query, occurrence_path)  # type: ignore[arg-type]
            if discovery["discovery_id"] in discovery_by_id:
                raise CompileError(f"query {query['query_id']}: duplicate occurrence {discovery['discovery_id']}; refusing to overwrite")
            discovery_by_id[discovery["discovery_id"]] = discovery; imported_discoveries.append(discovery)
            entity_id = _stable_id("E", key)
            candidate_key, candidate_rows = entity_candidates.setdefault(entity_id, (key, []))
            if candidate_key != key:
                raise CompileError(f"entity {entity_id}: deterministic ID collision between distinct dedupe keys")
            candidate_rows.append((discovery, source_entity, query["target_window_ids"]))
            occurrence_matches[discovery["provider_result_id"]] = (entity_id, source_entity)
        explicit = query_spec.get("repository_observations", [])
        if explicit is None: explicit = []
        if not isinstance(explicit, list) or not all(isinstance(item, dict) for item in explicit):
            raise CompileError(f"query {query['query_id']}: repository_observations must be an array when provided")
        explicit_ids: set[str] = set()
        for observation_spec in explicit:
            provider_result_id = observation_spec.get("provider_result_id")
            if not isinstance(provider_result_id, str) or provider_result_id not in occurrence_matches:
                raise CompileError(f"query {query['query_id']}: repository observation must match an imported provider_result_id")
            entity_id, source_entity = occurrence_matches[provider_result_id]
            if source_entity.get("kind") != "repository":
                raise CompileError(f"query {query['query_id']}: repository observation matched a non-repository occurrence")
            observation = _observation(observation_spec, entity_id, query, known_windows)
            if observation["observation_id"] in observation_by_id:
                raise CompileError(f"query {query['query_id']}: observation already exists: {observation['observation_id']}")
            observation_by_id[observation["observation_id"]] = observation; pending_observations.append(observation); explicit_ids.add(provider_result_id)
        for provider_result_id, (_entity_id, source_entity) in occurrence_matches.items():
            if source_entity.get("kind") == "repository" and provider_result_id not in explicit_ids:
                skipped.append({"query_id": query["query_id"], "provider_result_id": provider_result_id,
                                "reason": "repository_observation_skipped_unmeasured: complete API-derived counters were not supplied by spec"})
    unknown_dates: list[dict[str, Any]] = []
    known_unclassified_dates: list[dict[str, Any]] = []
    entity_date_basis: list[dict[str, Any]] = []
    for entity_id, (key, candidates) in entity_candidates.items():
        merged_entity, basis = _entity(entity_id, key, candidates, windows, as_of, now, entity_by_id.get(entity_id))
        entity_by_id[entity_id] = merged_entity
        entity_date_basis.append(basis)
        if basis["status"] == "unknown":
            unknown_dates.append({"entity_id": entity_id, "dedupe_key": key, "raw_dates": basis["raw_dates"], "time_window_ids": [],
                                  "reason": "entity_date_unknown_query_target_windows_not_inherited"})
        elif basis["status"] == "known-unclassified":
            known_unclassified_dates.append({"entity_id": entity_id, "dedupe_key": key, "raw_dates": basis["raw_dates"],
                                             "date_confidence": basis["date_confidence"], "time_window_ids": [],
                                             "reason": "known_date_did_not_satisfy_any_window_classification_rule"})
    merged_queries = queries + imported_queries; merged_discoveries = discoveries + imported_discoveries
    merged_entities = list(entity_by_id.values()); merged_observations = observations + pending_observations
    possible_duplicate_groups = _possible_duplicate_groups(merged_discoveries)
    repository_basis, repository_creation_counts, repository_activity_counts = _repository_freshness_basis(
        merged_discoveries, merged_observations, windows, as_of
    )
    recent_window_ids = {window_id for window_id, window in windows.items()
                         if window.get("kind") in {"recent-12m", "recent-90d"}}
    repository_recent_activity_counts = {window_id: repository_activity_counts[window_id]
                                         for window_id in windows if window_id in recent_window_ids}
    repositories_with_recent_activity = sum(bool(set(item["recent_activity_window_ids"])) for item in repository_basis)
    summary = {"schema_version": "1.0", "record_type": "discovery-compile-summary", "compiled_at": now, "bundle": str(bundle),
               "spec": str(spec_path), "dry_run": dry_run, "as_of": as_of.isoformat(), "as_of_source": as_of_source,
               "queries_imported": len(imported_queries), "occurrences_imported": len(imported_discoveries),
               "entities_total": len(merged_entities), "repository_observations_imported": len(pending_observations),
               "repository_observations_skipped_unmeasured": skipped, "repository_observations_skipped_unmeasured_count": len(skipped),
               "entity_date_basis": entity_date_basis,
               "entity_time_windows_unknown_date": unknown_dates,
               "entity_time_windows_unknown_date_count": len(unknown_dates),
               "entity_time_windows_known_unclassified": known_unclassified_dates,
               "entity_time_windows_known_unclassified_count": len(known_unclassified_dates),
               "repository_freshness_basis": repository_basis,
               "repository_creation_counts_by_window": repository_creation_counts,
               "repository_activity_counts_by_window": repository_activity_counts,
               "repository_recent_activity_counts_by_window": repository_recent_activity_counts,
               "repositories_with_recent_activity_count": repositories_with_recent_activity,
               "possible_duplicate_groups": possible_duplicate_groups,
               "possible_duplicate_group_count": len(possible_duplicate_groups),
               "possible_duplicate_policy": "mapper-review-only; no title/author/year group is automatically merged"}
    if not dry_run:
        _atomic_jsonl(bundle / "queries.jsonl", merged_queries)
        _atomic_jsonl(bundle / "discovery_results.jsonl", merged_discoveries)
        _atomic_jsonl(bundle / "entities.jsonl", merged_entities)
        _atomic_jsonl(bundle / "repository_observations.jsonl", merged_observations)
    _atomic_json(summary_path, summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path, help="existing schema-2.0 bundle root")
    parser.add_argument("--spec", required=True, type=Path, help="JSON query/import specification")
    parser.add_argument("--summary", required=True, type=Path, help="output compiler summary JSON")
    parser.add_argument("--dry-run", action="store_true", help="validate and write only the summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = compile_spec(args.bundle, args.spec, args.summary, dry_run=args.dry_run)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (CompileError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
