#!/usr/bin/env python3
"""Create, validate, and compare replayable frontier-research bundles.

The tool deliberately has no network dependency: it manages the local research
artifacts described by the Track Tech Frontier evidence contract. Reports place
each supported, qualified, or conflicted claim's exact statement immediately
before its ``<!-- claim:C001 -->`` marker. Semantic checks are structured,
clause-level audit records; they do not assert automated entailment.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit


SCHEMA_VERSION = "1.7"
V2_SCHEMA_VERSION = "2.0"
BASE_FILES = (
    "brief.md", "queries.md", "requirements.jsonl", "queries.jsonl", "sources.jsonl", "claims.jsonl",
    "evidence.jsonl", "semantic_checks.jsonl", "candidates.jsonl", "executions.jsonl", "repositories.jsonl", "papers.jsonl", "coverage.jsonl", "report.md", "run.json", "schema.json",
)
SOURCE_TIERS = {"T1", "T2", "T3", "T4"}
SOURCE_TYPES = {
    "paper", "official-doc", "standard", "repository", "release", "issue",
    "dataset", "industry", "journalism", "community", "research-log",
}
CLAIM_TYPES = {"fact", "comparison", "inference", "forecast"}
CLAIM_RISKS = {"high", "normal"}
CLAIM_CONFIDENCES = {"high", "medium", "low"}
CLAIM_STATUSES = {"supported", "qualified", "conflicted", "unsupported"}
SOURCE_FIELDS = {
    "source_id", "title", "url", "source_type", "tier", "published_at", "fetched_at",
    "organization", "independence_group", "version", "queries", "limitations", "access_status", "access_note",
}
CLAIM_FIELDS = {
    "claim_id", "statement", "claim_type", "risk",
    "scope", "as_of", "confidence", "status",
}
EVIDENCE_FIELDS = {
    "evidence_id", "claim_id", "source_id", "locator", "support_summary", "relation", "checked_at",
}
EVIDENCE_RELATIONS = {"supports", "partial", "contradicts"}
ACCESS_STATUSES = {"opened", "metadata-only", "blocked", "unverified"}
QUERY_FIELDS = {
    "query_id", "pass", "query", "channel", "executed_at", "result_count",
    "result_count_note", "retained_source_ids", "followup_reason",
}
CANDIDATE_FIELDS = {"candidate_id", "query_id", "title", "url", "decision", "source_id", "reason", "checked_at"}
CANDIDATE_DECISIONS = {"retained", "excluded", "deferred"}
REPOSITORY_FIELDS = {
    "source_id", "owner_repo", "pinned_commit", "latest_release", "pushed_at", "license",
    "setup", "tests_ci", "setup_execution_id", "tests_execution_id", "affiliation", "adoption_evidence", "checked_at",
}
SETUP_STATUSES = {"executed", "documented", "partial", "missing", "unknown"}
TESTS_CI_STATUSES = {"executed", "present", "missing", "unknown"}
AFFILIATION_STATUSES = {"reciprocal", "official-owner", "one-way", "unverified"}
PAPER_FIELDS = {"source_id", "identifier", "publication_status", "venue", "revision", "code_links", "data_source_ids", "status_locator", "evidence_role", "code_search_note", "checked_at"}
PAPER_STATUSES = {"peer-reviewed", "preprint", "workshop", "withdrawn", "unknown"}
PAPER_EVIDENCE_ROLES = {"original-study", "benchmark", "survey", "position", "system-report"}
CODE_LINK_FIELDS = {"source_id", "relation", "paper_locator", "repo_locator"}
CODE_LINK_RELATIONS = {"reciprocal", "paper-only", "repo-only", "unverified"}
COVERAGE_FIELDS = {"question_id", "question", "required_lanes", "status", "claim_ids", "source_ids", "gap", "updated_at"}
COVERAGE_LANES = {"paper", "github", "standards", "product", "benchmark", "adoption", "negative", "history", "mechanism"}
COVERAGE_STATUSES = {"covered", "partial", "no-reliable-evidence", "out-of-scope"}
REQUIREMENT_FIELDS = {"requirement_id", "text", "priority", "required_lanes", "acceptance", "frozen_at"}
REQUIREMENT_PRIORITIES = {"must", "should"}
EXECUTION_FIELDS = {"execution_id", "source_id", "purpose", "command", "environment", "started_at", "ended_at", "exit_code", "output_summary"}
EXECUTION_PURPOSES = {"setup", "tests"}
SEMANTIC_CHECK_FIELDS = {"claim_id", "verdict", "evidence_ids", "uncovered_terms", "rationale", "checked_at"}
SEMANTIC_VERDICTS = {"pass", "revise", "drop"}
RUN_FIELDS = {"schema_version", "topic", "as_of", "mode", "created_at", "previous", "review_profile"}
MARKDOWN_URL_PATTERN = re.compile(r"\]\((https?://[^)\s]+)\)", re.IGNORECASE)
AUTOLINK_URL_PATTERN = re.compile(r"<(https?://[^>\s]+)>", re.IGNORECASE)
BARE_URL_PATTERN = re.compile(
    r"(?<![<(])https?://[^\s<>()\[\]{}\"'，。；：、]+",
    re.IGNORECASE,
)
CURRENT_PATTERN = re.compile(
    r"\b(current|currently|latest|today|active|maintained|maintenance|deprecated)\b"
    r"|当前|最新|截至|活跃|维护中|已弃用|现行版本",
    re.IGNORECASE,
)
HIGH_RISK_PATTERN = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?%?\b|\bv?\d+(?:\.\d+){1,3}\b|\bpreview\s*\d+\b|"
    r"\b(release[ds]?|version|benchmark|performance|latency|throughput|security|"
    r"vulnerability|limitation|unsupported|support status|production[- ]ready|adoption|"
    r"commit|license|setup|tests?|ci|peer-reviewed|preprint|venue|repository)\b|"
    r"发布|版本|基准|性能|延迟|吞吐|安全|漏洞|限制|不支持|生产就绪|采用|提交|许可证|测试",
    re.IGNORECASE,
)
PINNED_COMMIT_PATTERN = re.compile(r"[0-9a-fA-F]{7,40}\Z")
CLAIM_MARKER_PATTERN = re.compile(r"<!--\s*claim:([A-Za-z0-9._-]+)\s*-->")
PROCESS_MARKER_PATTERN = re.compile(r"<!--\s*process:(method|limitation|source-list)\s*-->")
SECTION_NAMES = (
    "executive", "scope-method", "field-map", "evolution", "landscape", "deep-analysis",
    "benchmarks", "implementation", "negative-open", "outlook", "practical", "limitations-sources",
)
CORE_SECTION_NAMES = tuple(name for name in SECTION_NAMES if name not in {"scope-method", "limitations-sources"})
SECTION_MARKER_PATTERN = re.compile(r"^<!--\s*section:([a-z-]+)\s*-->$")

V2_BASE_FILES = (
    "brief.md", "queries.md", "research_plan.json", "queries.jsonl", "discovery_results.jsonl", "entities.jsonl",
    "screening.jsonl", "stage_events.jsonl", "clusters.jsonl", "cluster_assignments.jsonl", "cluster_coverage.jsonl",
    "time_windows.jsonl", "sources.jsonl", "claims.jsonl", "evidence.jsonl", "repositories.jsonl", "repository_observations.jsonl", "repository_engineering_profiles.jsonl",
    "papers.jsonl", "executions.jsonl", "semantic_checks.jsonl", "trend_metrics.jsonl", "saturation_events.jsonl", "saturation.jsonl",
    "research_questions.jsonl", "gaps.jsonl", "syntheses.jsonl", "relations.jsonl", "deliverables.jsonl", "report.md", "run.json", "schema.json",
)
V2_PLAN_FIELDS = {"schema_version", "topic", "as_of", "lanes", "time_windows", "important_cluster_policy", "required_deliverable_kinds", "targets"}
V2_QUERY_FIELDS = {
    "query_id", "stage", "iteration", "provider", "query_text", "request_url",
    "status", "raw_snapshot_paths", "target_lanes", "target_window_ids",
    "target_cluster_ids", "parent_query_ids", "gap_ids", "information_gain",
    "executed_at", "result_count", "result_count_note",
}
V2_QUERY_STAGES = {"pilot", "discover", "map", "gap-fill", "deep-focus", "verify", "adversarial", "refresh"}
V2_QUERY_STATUSES = {"succeeded", "partial", "failed", "blocked"}
V2_ENTITY_STAGES = {"discovered", "mapped", "deep-verified"}
V2_DISCOVERY_FIELDS = {"discovery_id", "query_id", "provider", "provider_result_id", "title", "url", "identifier", "observed_at", "rank", "page_cursor", "metadata"}
V2_ENTITY_FIELDS = {"entity_id", "canonical_name", "url", "identifier", "aliases", "discovery_ids", "stage", "published_at", "created_at", "updated_at", "date_confidence", "time_window_ids", "source_ids", "entity_type"}
V2_CLUSTER_FIELDS = {"cluster_id", "label", "importance", "parent_ids", "definition", "inclusion", "exclusion", "problem", "architecture_patterns", "implementation_patterns", "tradeoffs", "required_lanes", "confidence"}
V2_CLUSTER_COVERAGE_FIELDS = {"cluster_id", "lane", "window_id", "status"}
V2_COVERAGE_PROOF_FIELDS = {
    "proof_id", "cluster_id", "lane", "window_id", "applicability", "status",
    "coverage_basis", "positive_entity_count", "scope_claim", "missing_gates",
    "provenance", "rationale", "checked_at",
}
V2_COVERAGE_PROVENANCE_FIELDS = {
    "query_ids", "successful_query_ids", "discovery_ids", "screening_ids",
    "excluded_discovery_ids", "entity_ids", "source_ids", "claim_ids",
    "deliverable_ids", "saturation_ids", "saturation_event_ids", "gap_ids",
}
V2_DELIVERABLE_FIELDS = {"deliverable_id", "kind", "path", "sha256", "cluster_ids", "entity_ids", "engineering_profile_ids", "publication_status", "required", "claim_ids", "synthesis_ids", "generated_at"}
V2_SCREENING_FIELDS = {"screening_id", "discovery_id", "decision", "reason", "checked_at"}
V2_STAGE_EVENT_FIELDS = {"event_id", "entity_id", "from_stage", "to_stage", "occurred_at", "rationale"}
V2_ASSIGNMENT_FIELDS = {"assignment_id", "entity_id", "cluster_id", "membership", "confidence", "rationale", "method", "time"}
V2_WINDOW_FIELDS = {"window_id", "label", "start", "end", "kind"}
V2_REPOSITORY_OBSERVATION_FIELDS = {"observation_id", "entity_id", "node_id", "owner_repo", "stars", "forks", "open_issues", "created", "pushed", "latest_release", "default_commit", "archived", "fork", "license", "commits_in_window", "contributors_in_window", "window_id", "api_url", "note", "observed_at"}
V2_REPOSITORY_ENGINEERING_PROFILE_FIELDS = {"profile_id", "entity_id", "source_ids", "pinned_commit", "architecture_summary", "components", "data_flow", "dependencies_services", "integration_constraints", "maintenance_evidence", "issue_pr_findings", "failure_modes", "adoption_boundary", "unknowns", "checked_at"}
V2_TREND_FIELDS = {"metric_id", "entity_id", "cluster_id", "observation_ids", "metric_type", "start", "end", "delta", "rate", "acceleration", "method", "completeness", "status", "followup", "signal_only", "checked_at"}
V2_SATURATION_EVENT_FIELDS = {"cycle_id", "scope_type", "scope_id", "iteration", "query_ids", "new_entities", "new_entity_ids", "new_high_signal_items", "new_high_signal_ids", "new_first_order_clusters", "new_first_order_cluster_ids", "new_stances", "new_stance_ids", "boundary_changed", "proposition_changed", "material_change", "remaining_gap_ids", "observed_gain", "checked_at"}
V2_SATURATION_FIELDS = {"saturation_id", "scope_type", "scope_id", "stop_rule", "observed_gain", "status", "final_cycle_ids", "remaining_gap_ids", "checked_at"}
V2_QUESTION_FIELDS = {"question_id", "text", "origin", "cluster_ids", "lanes", "window_ids", "status", "created_at"}
V2_GAP_FIELDS = {"gap_id", "question_id", "cluster_ids", "lanes", "window_ids", "perspectives", "status", "rationale", "created_at"}
V2_SYNTHESIS_FIELDS = {"synthesis_id", "action", "proposition", "claim_ids", "evidence_ids", "supporting_evidence_ids", "opposing_evidence_ids", "supporting_group_ids", "opposing_group_ids", "assessment", "minority_view", "unknowns", "weighting_method", "conditions", "confidence", "limitations", "reversal_criteria", "cluster_ids", "publication_status", "deliverable_ids"}
V2_RELATION_FIELDS = {"relation_id", "from_entity_id", "to_entity_id", "relation_type", "assertion_type", "evidence_ids", "conditions", "confidence"}
V2_PUBLICATION_STATUSES = {"published", "ledger-only", "superseded"}
V2_DELIVERABLE_KINDS = {
    "report", "readme", "executive", "field-tree", "landscape", "timeline",
    "consensus", "repository-radar", "benchmark-map", "security-failure", "method", "source-index",
    "cluster-deep-dive", "project-deep-dive",
}
V2_COMPREHENSIVE_DELIVERABLE_KINDS = {
    "readme", "executive", "field-tree", "landscape", "timeline", "consensus",
    "repository-radar", "benchmark-map", "method", "source-index",
    "cluster-deep-dive", "project-deep-dive",
}
V2_CLUSTER_COVERAGE_STATUSES = {"covered", "partial", "gap", "not-applicable"}
V2_COVERAGE_APPLICABILITY = {"required", "adjacent", "not-applicable"}
V2_COVERAGE_BASES = {"positive_evidence", "bounded_scarcity", "inherited", "incomplete", "not_applicable"}
V2_SATURATION_PERSPECTIVES = {"mechanism", "implementation", "benchmark", "adoption", "negative"}
V2_RELATION_ASSERTION_TYPES = {"fact", "hypothesis", "event", "source-influence", "inference", "forecast"}
V2_TREND_STATUSES = {"signal", "confirmed", "qualified", "dismissed", "unresolved", "follow-up"}
V2_SYNTHESIS_ASSESSMENTS = {"dominant", "mixed", "disputed", "evidence-thin"}
V2_SYNTHESIS_MARKER_PATTERN = re.compile(r"<!--\s*synthesis:([A-Za-z0-9._-]+)(?:\s+[^>]*)?-->")
V2_TARGETS = {"discovered_entities", "mapped_entities", "deep_verified_entities", "papers_discovered", "repositories_discovered", "papers_mapped", "repositories_mapped", "deep_papers", "deep_repositories", "recent_discovered", "recent_mapped", "queries", "sources", "claims", "evidence", "clusters", "deliverables"}


class BundleError(Exception):
    """An expected, human-actionable bundle error."""


@dataclass
class Findings:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def advisory(self, message: str) -> None:
        self.advisories.append(message)


def _iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def _parse_utc_timestamp(value: Any) -> datetime | None:
    if not _utc_timestamp(value):
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _validate_timestamp_window(value: Any, label: str, findings: Findings, now: datetime, run_created_at: datetime | None) -> None:
    timestamp = _parse_utc_timestamp(value)
    if timestamp is None:
        return
    skew = timedelta(minutes=5)
    if timestamp > now + skew:
        findings.error(f"{label}: timestamp is later than current UTC time plus 5 minutes")
    if run_created_at is not None and timestamp < run_created_at - skew:
        findings.error(f"{label}: timestamp is earlier than run.json created_at minus 5 minutes")


def _http_url(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    parsed = urlsplit(value)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def normalize_url(value: str) -> str:
    """Normalize only URL details that do not change its resource identity."""
    parsed = urlsplit(value)
    host = parsed.hostname.lower() if parsed.hostname else ""
    if parsed.port and not ((parsed.scheme.lower() == "https" and parsed.port == 443) or
                            (parsed.scheme.lower() == "http" and parsed.port == 80)):
        host = f"{host}:{parsed.port}"
    path = parsed.path
    if path == "/":
        path = ""
    return urlunsplit((parsed.scheme.lower(), host, path, parsed.query, ""))


def _require_fields(record: Any, fields: set[str], label: str, findings: Findings) -> bool:
    if not isinstance(record, dict):
        findings.error(f"{label}: record must be a JSON object")
        return False
    missing = sorted(fields - record.keys())
    if missing:
        findings.error(f"{label}: missing required fields: {', '.join(missing)}")
        return False
    return True


def _read_jsonl(path: Path, label: str, findings: Findings) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        findings.error(f"{label}: cannot read: {exc}")
        return records
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.error(f"{label}:{number}: invalid JSON: {exc.msg}")
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            findings.error(f"{label}:{number}: record must be a JSON object")
    return records


def _read_run(root: Path, findings: Findings) -> dict[str, Any] | None:
    path = root / "run.json"
    try:
        raw = path.read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        findings.error(f"run.json: invalid JSON or unreadable: {exc}")
        return None
    if not _require_fields(value, RUN_FIELDS, "run.json", findings):
        return None
    if value.get("schema_version") != SCHEMA_VERSION:
        findings.error(f"run.json: unsupported schema_version {value.get('schema_version')!r}")
    if not isinstance(value.get("topic"), str) or not value["topic"].strip():
        findings.error("run.json: topic must be a non-empty string")
    if not _iso_date(value.get("as_of")):
        findings.error("run.json: as_of must be YYYY-MM-DD")
    if value.get("mode") not in {"snapshot", "update"}:
        findings.error("run.json: mode must be snapshot or update")
    if value.get("review_profile") not in {"full", "rapid"}:
        findings.error("run.json: review_profile must be full or rapid")
    if not _utc_timestamp(value.get("created_at")):
        findings.error("run.json: created_at must be YYYY-MM-DDTHH:MM:SSZ")
    if value.get("previous") is not None and not isinstance(value.get("previous"), str):
        findings.error("run.json: previous must be a path string or null")
    return value


def _validate_v17_bundle(root: Path, *, strict: bool = False) -> Findings:
    findings = Findings()
    now = datetime.now(timezone.utc)
    if not root.is_dir():
        findings.error(f"bundle root does not exist or is not a directory: {root}")
        return findings

    for filename in BASE_FILES:
        if not (root / filename).is_file():
            findings.error(f"missing required file: {filename}")
    run = _read_run(root, findings) if (root / "run.json").is_file() else None
    run_created_at = _parse_utc_timestamp(run.get("created_at")) if run else None
    if run:
        _validate_timestamp_window(run.get("created_at"), "run.json: created_at", findings, now, None)
    if run and run.get("mode") == "update" and not (root / "delta.md").is_file():
        findings.error("missing required file for update bundle: delta.md")
    if run and run.get("mode") == "update" and not run.get("previous"):
        findings.error("run.json: update mode requires previous")

    brief = root / "brief.md"
    if brief.is_file() and run:
        try:
            brief_text = brief.read_text(encoding="utf-8")
        except OSError as exc:
            findings.error(f"brief.md: cannot read: {exc}")
        else:
            if str(run.get("topic", "")).casefold() not in brief_text.casefold():
                findings.error("brief.md: does not contain the run topic")
            if str(run.get("as_of")) not in brief_text:
                findings.error("brief.md: does not contain the run as_of date")

    requirement_records = _read_jsonl(root / "requirements.jsonl", "requirements.jsonl", findings) if (root / "requirements.jsonl").is_file() else []
    sources = _read_jsonl(root / "sources.jsonl", "sources.jsonl", findings) if (root / "sources.jsonl").is_file() else []
    query_records = _read_jsonl(root / "queries.jsonl", "queries.jsonl", findings) if (root / "queries.jsonl").is_file() else []
    claims = _read_jsonl(root / "claims.jsonl", "claims.jsonl", findings) if (root / "claims.jsonl").is_file() else []
    evidence_records = _read_jsonl(root / "evidence.jsonl", "evidence.jsonl", findings) if (root / "evidence.jsonl").is_file() else []
    semantic_check_records = _read_jsonl(root / "semantic_checks.jsonl", "semantic_checks.jsonl", findings) if (root / "semantic_checks.jsonl").is_file() else []
    candidate_records = _read_jsonl(root / "candidates.jsonl", "candidates.jsonl", findings) if (root / "candidates.jsonl").is_file() else []
    execution_records = _read_jsonl(root / "executions.jsonl", "executions.jsonl", findings) if (root / "executions.jsonl").is_file() else []
    repository_records = _read_jsonl(root / "repositories.jsonl", "repositories.jsonl", findings) if (root / "repositories.jsonl").is_file() else []
    paper_records = _read_jsonl(root / "papers.jsonl", "papers.jsonl", findings) if (root / "papers.jsonl").is_file() else []
    coverage_records = _read_jsonl(root / "coverage.jsonl", "coverage.jsonl", findings) if (root / "coverage.jsonl").is_file() else []
    if not sources:
        findings.warning("sources.jsonl: no source records")
    if not sources and not query_records:
        findings.warning("queries.jsonl: no query records while the bundle has no sources")
    if not claims:
        findings.warning("claims.jsonl: no claim records")
    if not requirement_records:
        findings.warning("requirements.jsonl: no requirement records")

    source_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources, 1):
        label = f"sources.jsonl:{index}"
        if not _require_fields(source, SOURCE_FIELDS, label, findings):
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            findings.error(f"{label}: source_id must be a non-empty string")
        elif source_id in source_by_id:
            findings.error(f"{label}: duplicate source_id {source_id}")
        else:
            source_by_id[source_id] = source
        if not isinstance(source.get("title"), str) or not source["title"].strip():
            findings.error(f"{label}: title must be a non-empty string")
        if source.get("source_type") == "research-log":
            if source.get("url") not in {"bundle://queries.jsonl", "bundle://candidates.jsonl"}:
                findings.error(f"{label}: research-log url must be bundle://queries.jsonl or bundle://candidates.jsonl")
        elif not _http_url(source.get("url")):
            findings.error(f"{label}: url must be an http(s) URL")
        if source.get("tier") not in SOURCE_TIERS:
            findings.error(f"{label}: tier must be one of {', '.join(sorted(SOURCE_TIERS))}")
        if source.get("source_type") not in SOURCE_TYPES:
            findings.error(f"{label}: source_type is not allowed")
        if source.get("published_at") is not None and not _iso_date(source.get("published_at")):
            findings.error(f"{label}: published_at must be YYYY-MM-DD or null")
        if not _utc_timestamp(source.get("fetched_at")):
            findings.error(f"{label}: fetched_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(source.get("fetched_at"), f"{label}: fetched_at", findings, now, run_created_at)
        if source.get("access_status") not in ACCESS_STATUSES:
            findings.error(f"{label}: access_status is not allowed")
        if not isinstance(source.get("access_note"), str) or not source["access_note"].strip():
            findings.error(f"{label}: access_note must be a non-empty string")
        for list_field in ("queries",):
            if not isinstance(source.get(list_field), list) or not all(isinstance(v, str) for v in source[list_field]):
                findings.error(f"{label}: {list_field} must be a list of strings")
    query_by_id: dict[str, dict[str, Any]] = {}
    for index, query in enumerate(query_records, 1):
        label = f"queries.jsonl:{index}"
        if not _require_fields(query, QUERY_FIELDS, label, findings):
            continue
        query_id = query.get("query_id")
        if not isinstance(query_id, str) or not query_id:
            findings.error(f"{label}: query_id must be a non-empty string")
        elif query_id in query_by_id:
            findings.error(f"{label}: duplicate query_id {query_id}")
        else:
            query_by_id[query_id] = query
        if type(query.get("pass")) is not int or query["pass"] not in {1, 2, 3, 4}:
            findings.error(f"{label}: pass must be an integer from 1 through 4")
        for field_name in ("query", "channel", "followup_reason"):
            if not isinstance(query.get(field_name), str):
                findings.error(f"{label}: {field_name} must be a string")
        if not _utc_timestamp(query.get("executed_at")):
            findings.error(f"{label}: executed_at must be YYYY-MM-DDTHH:MM:SSZ")
        result_count = query.get("result_count")
        if result_count is not None and (type(result_count) is not int or result_count < 0):
            findings.error(f"{label}: result_count must be a non-negative integer or null")
        if not isinstance(query.get("result_count_note"), str):
            findings.error(f"{label}: result_count_note must be a string")
        elif result_count is None and not query["result_count_note"].strip():
            findings.error(f"{label}: result_count=null requires a non-empty result_count_note")
        _validate_timestamp_window(query.get("executed_at"), f"{label}: executed_at", findings, now, run_created_at)
        retained = query.get("retained_source_ids")
        if not isinstance(retained, list) or not all(isinstance(value, str) for value in retained):
            findings.error(f"{label}: retained_source_ids must be a list of strings")

    if sources and not query_records:
        findings.error("queries.jsonl: source records require at least one query record")
    for query_id, query in query_by_id.items():
        retained = query.get("retained_source_ids") if isinstance(query.get("retained_source_ids"), list) else []
        for source_id in retained:
            if source_id not in source_by_id:
                findings.error(f"query {query_id}: retained_source_ids references unknown source {source_id}")
            elif query_id not in source_by_id[source_id].get("queries", []):
                findings.error(f"query {query_id}: source {source_id} does not reciprocally list the query")
    for source_id, source in source_by_id.items():
        query_ids = source.get("queries") if isinstance(source.get("queries"), list) else []
        for query_id in query_ids:
            if query_id not in query_by_id:
                findings.error(f"source {source_id}: queries references unknown query {query_id}")
            elif source_id not in query_by_id[query_id].get("retained_source_ids", []):
                findings.error(f"source {source_id}: query {query_id} does not reciprocally retain the source")

    first_query_at = min(
        (timestamp for query in query_by_id.values() if (timestamp := _parse_utc_timestamp(query.get("executed_at"))) is not None),
        default=None,
    )
    requirement_by_id: dict[str, dict[str, Any]] = {}
    for index, requirement in enumerate(requirement_records, 1):
        label = f"requirements.jsonl:{index}"
        if not _require_fields(requirement, REQUIREMENT_FIELDS, label, findings):
            continue
        requirement_id = requirement.get("requirement_id")
        if not isinstance(requirement_id, str) or not requirement_id:
            findings.error(f"{label}: requirement_id must be a non-empty string")
        elif requirement_id in requirement_by_id:
            findings.error(f"{label}: duplicate requirement_id {requirement_id}")
        else:
            requirement_by_id[requirement_id] = requirement
        for field_name in ("text", "acceptance"):
            if not isinstance(requirement.get(field_name), str) or not requirement[field_name].strip():
                findings.error(f"{label}: {field_name} must be a non-empty string")
        if requirement.get("priority") not in REQUIREMENT_PRIORITIES:
            findings.error(f"{label}: priority must be must or should")
        lanes = requirement.get("required_lanes")
        if not isinstance(lanes, list) or not lanes or not all(isinstance(value, str) for value in lanes):
            findings.error(f"{label}: required_lanes must be a non-empty list of strings")
        elif any(value not in COVERAGE_LANES for value in lanes):
            findings.error(f"{label}: required_lanes contains an unsupported lane")
        if not _utc_timestamp(requirement.get("frozen_at")):
            findings.error(f"{label}: frozen_at must be YYYY-MM-DDTHH:MM:SSZ")
        else:
            frozen_at = _parse_utc_timestamp(requirement["frozen_at"])
            if run_created_at is not None and frozen_at is not None and frozen_at < run_created_at:
                findings.error(f"{label}: frozen_at must not be before run.json created_at")
            if first_query_at is not None and frozen_at is not None and frozen_at > first_query_at:
                findings.error(f"{label}: frozen_at must not be after the first query")

    candidate_by_id: dict[str, dict[str, Any]] = {}
    retained_candidate_counts: dict[tuple[str, str], int] = {}
    candidates_by_query: dict[str, list[dict[str, Any]]] = {}
    for index, candidate in enumerate(candidate_records, 1):
        label = f"candidates.jsonl:{index}"
        if not _require_fields(candidate, CANDIDATE_FIELDS, label, findings):
            continue
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            findings.error(f"{label}: candidate_id must be a non-empty string")
        elif candidate_id in candidate_by_id:
            findings.error(f"{label}: duplicate candidate_id {candidate_id}")
        else:
            candidate_by_id[candidate_id] = candidate
        query_id = candidate.get("query_id")
        if not isinstance(query_id, str) or query_id not in query_by_id:
            findings.error(f"{label}: query_id references an unknown query")
        else:
            candidates_by_query.setdefault(query_id, []).append(candidate)
        if not isinstance(candidate.get("title"), str):
            findings.error(f"{label}: title must be a string")
        if not _http_url(candidate.get("url")):
            findings.error(f"{label}: url must be an http(s) URL")
        if candidate.get("decision") not in CANDIDATE_DECISIONS:
            findings.error(f"{label}: decision is not allowed")
        if not _utc_timestamp(candidate.get("checked_at")):
            findings.error(f"{label}: checked_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(candidate.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
        source_id = candidate.get("source_id")
        if candidate.get("decision") == "retained":
            if not isinstance(source_id, str) or not source_id:
                findings.error(f"{label}: retained candidate requires a source_id")
            else:
                source = source_by_id.get(source_id)
                if source is None:
                    findings.error(f"{label}: retained candidate references unknown source {source_id}")
                else:
                    if _http_url(candidate.get("url")) and normalize_url(candidate["url"]) != normalize_url(source.get("url", "")):
                        findings.error(f"{label}: retained candidate URL does not match source {source_id}")
                    if isinstance(query_id, str) and query_id in query_by_id:
                        if source_id not in query_by_id[query_id].get("retained_source_ids", []):
                            findings.error(f"{label}: retained source {source_id} is absent from query retained_source_ids")
                        if query_id not in source.get("queries", []):
                            findings.error(f"{label}: source {source_id} does not reciprocally list the query")
                        retained_candidate_counts[(query_id, source_id)] = retained_candidate_counts.get((query_id, source_id), 0) + 1
        elif source_id is not None or not isinstance(candidate.get("reason"), str) or not candidate["reason"].strip():
            findings.error(f"{label}: excluded/deferred candidate requires source_id=null and a non-empty reason")
    for query_id, query in query_by_id.items():
        records = candidates_by_query.get(query_id, [])
        result_count = query.get("result_count")
        if result_count is None or result_count > 0:
            if not records:
                findings.error(f"query {query_id}: requires at least one candidate record")
        if result_count == 0 and any(record.get("decision") == "retained" for record in records):
            findings.error(f"query {query_id}: result_count=0 cannot have retained candidates")
        for source_id in query.get("retained_source_ids", []):
            count = retained_candidate_counts.get((query_id, source_id), 0)
            if count != 1:
                findings.error(f"query {query_id}: retained source {source_id} requires exactly one retained candidate")

    execution_by_id: dict[str, dict[str, Any]] = {}
    for index, execution in enumerate(execution_records, 1):
        label = f"executions.jsonl:{index}"
        if not _require_fields(execution, EXECUTION_FIELDS, label, findings):
            continue
        execution_id = execution.get("execution_id")
        if not isinstance(execution_id, str) or not execution_id:
            findings.error(f"{label}: execution_id must be a non-empty string")
        elif execution_id in execution_by_id:
            findings.error(f"{label}: duplicate execution_id {execution_id}")
        else:
            execution_by_id[execution_id] = execution
        source_id = execution.get("source_id")
        source = source_by_id.get(source_id) if isinstance(source_id, str) else None
        if source is None or source.get("source_type") != "repository":
            findings.error(f"{label}: source_id must reference a repository source")
        if execution.get("purpose") not in EXECUTION_PURPOSES:
            findings.error(f"{label}: purpose must be setup or tests")
        for field_name in ("command", "environment", "output_summary"):
            if not isinstance(execution.get(field_name), str) or not execution[field_name].strip():
                findings.error(f"{label}: {field_name} must be a non-empty string")
        for field_name in ("started_at", "ended_at"):
            if not _utc_timestamp(execution.get(field_name)):
                findings.error(f"{label}: {field_name} must be YYYY-MM-DDTHH:MM:SSZ")
            _validate_timestamp_window(execution.get(field_name), f"{label}: {field_name}", findings, now, run_created_at)
        started_at, ended_at = _parse_utc_timestamp(execution.get("started_at")), _parse_utc_timestamp(execution.get("ended_at"))
        if started_at is not None and ended_at is not None and ended_at < started_at:
            findings.error(f"{label}: ended_at must not be earlier than started_at")
        if execution.get("exit_code") != 0:
            findings.error(f"{label}: exit_code must be 0 for an executed record")

    repository_by_source_id: dict[str, dict[str, Any]] = {}
    for index, repository in enumerate(repository_records, 1):
        label = f"repositories.jsonl:{index}"
        if not _require_fields(repository, REPOSITORY_FIELDS, label, findings):
            continue
        source_id = repository.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            findings.error(f"{label}: source_id must be a non-empty string")
        elif source_id in repository_by_source_id:
            findings.error(f"{label}: duplicate repository card for source {source_id}")
        else:
            repository_by_source_id[source_id] = repository
        source = source_by_id.get(source_id) if isinstance(source_id, str) else None
        if source is None:
            findings.error(f"{label}: references unknown source {source_id}")
        elif source.get("source_type") != "repository":
            findings.error(f"{label}: source {source_id} is not a repository")
        if not isinstance(repository.get("owner_repo"), str) or not repository["owner_repo"].strip():
            findings.error(f"{label}: owner_repo must be a non-empty string")
        for field_name in ("latest_release", "license"):
            value = repository.get(field_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                findings.error(f"{label}: {field_name} must be a non-empty string or null")
        if not isinstance(repository.get("pinned_commit"), str) or not PINNED_COMMIT_PATTERN.fullmatch(repository["pinned_commit"]):
            findings.error(f"{label}: pinned_commit must be 7 to 40 hexadecimal characters")
        if not _iso_date(repository.get("pushed_at")):
            findings.error(f"{label}: pushed_at must be YYYY-MM-DD")
        if not _utc_timestamp(repository.get("checked_at")):
            findings.error(f"{label}: checked_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(repository.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
        if repository.get("setup") not in SETUP_STATUSES:
            findings.error(f"{label}: setup is not allowed")
        if repository.get("tests_ci") not in TESTS_CI_STATUSES:
            findings.error(f"{label}: tests_ci is not allowed")
        if repository.get("affiliation") not in AFFILIATION_STATUSES:
            findings.error(f"{label}: affiliation is not allowed")
        for status_field, execution_field, purpose in (("setup", "setup_execution_id", "setup"), ("tests_ci", "tests_execution_id", "tests")):
            status, execution_id = repository.get(status_field), repository.get(execution_field)
            if status == "executed":
                execution = execution_by_id.get(execution_id) if isinstance(execution_id, str) else None
                if execution is None:
                    findings.error(f"{label}: {status_field}=executed requires a valid {execution_field}")
                elif execution.get("source_id") != source_id or execution.get("purpose") != purpose:
                    findings.error(f"{label}: {execution_field} must reference this repository's {purpose} execution")
            elif execution_id is not None:
                findings.error(f"{label}: {execution_field} must be null unless {status_field}=executed")
        adoption = repository.get("adoption_evidence")
        if not isinstance(adoption, list) or not all(isinstance(value, str) for value in adoption):
            findings.error(f"{label}: adoption_evidence must be a list of source IDs")
        else:
            for adoption_source_id in adoption:
                if adoption_source_id not in source_by_id:
                    findings.error(f"{label}: adoption_evidence references unknown source {adoption_source_id}")
        if source is not None and source.get("license") != repository.get("license"):
            findings.error(f"{label}: license does not match source {source_id}")
        if repository.get("affiliation") == "unverified":
            findings.advisory(f"{label}: repository affiliation is unverified")
        if repository.get("license") is None:
            findings.advisory(f"{label}: repository license is unknown or undeclared")
        if repository.get("setup") in {"missing", "unknown"}:
            findings.advisory(f"{label}: repository setup is {repository.get('setup')}")
        if repository.get("tests_ci") in {"missing", "unknown"}:
            findings.advisory(f"{label}: repository tests_ci is {repository.get('tests_ci')}")
    for source_id, source in source_by_id.items():
        if source.get("source_type") == "repository" and source_id not in repository_by_source_id:
            findings.error(f"source {source_id}: repository source is missing a quality card")

    paper_by_source_id: dict[str, dict[str, Any]] = {}
    for index, paper in enumerate(paper_records, 1):
        label = f"papers.jsonl:{index}"
        if not _require_fields(paper, PAPER_FIELDS, label, findings):
            continue
        source_id = paper.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            findings.error(f"{label}: source_id must be a non-empty string")
        elif source_id in paper_by_source_id:
            findings.error(f"{label}: duplicate paper card for source {source_id}")
        else:
            paper_by_source_id[source_id] = paper
        source = source_by_id.get(source_id) if isinstance(source_id, str) else None
        if source is None:
            findings.error(f"{label}: references unknown source {source_id}")
        elif source.get("source_type") != "paper":
            findings.error(f"{label}: source {source_id} is not a paper")
        if not isinstance(paper.get("identifier"), str) or not paper["identifier"].strip():
            findings.error(f"{label}: identifier must be a non-empty string")
        if paper.get("publication_status") not in PAPER_STATUSES:
            findings.error(f"{label}: publication_status is not allowed")
        if paper.get("evidence_role") not in PAPER_EVIDENCE_ROLES:
            findings.error(f"{label}: evidence_role is not allowed")
        elif paper.get("evidence_role") == "survey" and source is not None and source.get("tier") != "T2":
            findings.error(f"{label}: survey paper source must have tier T2")
        if not isinstance(paper.get("code_search_note"), str) or not paper["code_search_note"].strip():
            findings.error(f"{label}: code_search_note must be a non-empty string")
        for field_name in ("venue", "revision"):
            value = paper.get(field_name)
            if value is not None and not isinstance(value, str):
                findings.error(f"{label}: {field_name} must be a string or null")
        if paper.get("publication_status") == "peer-reviewed" and paper.get("venue") is None:
            findings.error(f"{label}: peer-reviewed paper requires a venue")
        code_links = paper.get("code_links")
        if not isinstance(code_links, list):
            findings.error(f"{label}: code_links must be a list")
        else:
            for link_index, link in enumerate(code_links, 1):
                link_label = f"{label}:code_links:{link_index}"
                if not _require_fields(link, CODE_LINK_FIELDS, link_label, findings):
                    continue
                linked_source_id = link.get("source_id")
                linked_source = source_by_id.get(linked_source_id) if isinstance(linked_source_id, str) else None
                if linked_source is None:
                    findings.error(f"{link_label}: source_id references unknown source {linked_source_id}")
                elif linked_source.get("source_type") != "repository":
                    findings.error(f"{link_label}: source_id must reference a repository source")
                if link.get("relation") not in CODE_LINK_RELATIONS:
                    findings.error(f"{link_label}: relation is not allowed")
                for field_name in ("paper_locator", "repo_locator"):
                    if not isinstance(link.get(field_name), str) or not link[field_name].strip():
                        findings.error(f"{link_label}: {field_name} must be a non-empty precise locator")
                if link.get("relation") == "unverified":
                    findings.advisory(f"{link_label}: code link is unverified")
        for field_name, allowed_types in (("data_source_ids", {"dataset"}),):
            values = paper.get(field_name)
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                findings.error(f"{label}: {field_name} must be a list of source IDs")
                continue
            for linked_source_id in values:
                linked_source = source_by_id.get(linked_source_id)
                if linked_source is None:
                    findings.error(f"{label}: {field_name} references unknown source {linked_source_id}")
                elif linked_source.get("source_type") not in allowed_types:
                    findings.error(f"{label}: {field_name} source {linked_source_id} has the wrong source_type")
        if not isinstance(paper.get("status_locator"), str) or not paper["status_locator"].strip():
            findings.error(f"{label}: status_locator must be a non-empty string")
        if not _utc_timestamp(paper.get("checked_at")):
            findings.error(f"{label}: checked_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(paper.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
        if paper.get("publication_status") == "unknown":
            findings.advisory(f"{label}: publication_status is unknown")
    for source_id, source in source_by_id.items():
        if source.get("source_type") == "paper" and source_id not in paper_by_source_id:
            findings.error(f"source {source_id}: paper source is missing a paper card")
    linked_repository_ids = {
        link.get("source_id")
        for paper in paper_by_source_id.values()
        for link in paper.get("code_links", []) if isinstance(link, dict)
        if isinstance(link.get("source_id"), str)
    }
    for source_id, repository in repository_by_source_id.items():
        source = source_by_id.get(source_id)
        if source is not None and source.get("version") != repository.get("pinned_commit"):
            findings.error(f"source {source_id}: repository version must exactly match pinned_commit")
        if repository.get("affiliation") != "unverified" and source_id not in linked_repository_ids:
            findings.error(f"source {source_id}: non-unverified repository affiliation requires a paper code link")

    claim_by_id: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(claims, 1):
        label = f"claims.jsonl:{index}"
        if not _require_fields(claim, CLAIM_FIELDS, label, findings):
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            findings.error(f"{label}: claim_id must be a non-empty string")
        elif claim_id in claim_by_id:
            findings.error(f"{label}: duplicate claim_id {claim_id}")
        else:
            claim_by_id[claim_id] = claim
        if not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
            findings.error(f"{label}: statement must be a non-empty string")
        if claim.get("claim_type") not in CLAIM_TYPES:
            findings.error(f"{label}: claim_type is not allowed")
        if claim.get("risk") not in CLAIM_RISKS:
            findings.error(f"{label}: risk must be high or normal")
        elif claim.get("risk") == "normal" and (
            claim.get("claim_type") == "comparison"
            or (isinstance(claim.get("statement"), str) and (
                CURRENT_PATTERN.search(claim["statement"]) or HIGH_RISK_PATTERN.search(claim["statement"])
            ))
        ):
            findings.warning(f"{label}: likely high-risk claim is marked normal")
        if claim.get("confidence") not in CLAIM_CONFIDENCES:
            findings.error(f"{label}: confidence must be high, medium, or low")
        if claim.get("status") not in CLAIM_STATUSES:
            findings.error(f"{label}: status is not allowed")
        if not _iso_date(claim.get("as_of")):
            findings.error(f"{label}: as_of must be YYYY-MM-DD")
        elif run and claim.get("as_of") != run.get("as_of"):
            findings.error(f"{label}: as_of does not match run.json")

    coverage_by_id: dict[str, dict[str, Any]] = {}
    covered_claim_ids: set[str] = set()
    for index, coverage in enumerate(coverage_records, 1):
        label = f"coverage.jsonl:{index}"
        if not _require_fields(coverage, COVERAGE_FIELDS, label, findings):
            continue
        question_id = coverage.get("question_id")
        if not isinstance(question_id, str) or not question_id:
            findings.error(f"{label}: question_id must be a non-empty string")
        elif question_id in coverage_by_id:
            findings.error(f"{label}: duplicate question_id {question_id}")
        else:
            coverage_by_id[question_id] = coverage
        if not isinstance(coverage.get("question"), str):
            findings.error(f"{label}: question must be a string")
        lanes = coverage.get("required_lanes")
        if not isinstance(lanes, list) or not all(isinstance(value, str) for value in lanes):
            findings.error(f"{label}: required_lanes must be a list of strings")
        elif any(value not in COVERAGE_LANES for value in lanes):
            findings.error(f"{label}: required_lanes contains an unsupported lane")
        status = coverage.get("status")
        if status not in COVERAGE_STATUSES:
            findings.error(f"{label}: status is not allowed")
        claim_ids, source_ids = coverage.get("claim_ids"), coverage.get("source_ids")
        for field_name, values, known in (("claim_ids", claim_ids, claim_by_id), ("source_ids", source_ids, source_by_id)):
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                findings.error(f"{label}: {field_name} must be a list of IDs")
            else:
                for value in values:
                    if value not in known:
                        findings.error(f"{label}: {field_name} references unknown ID {value}")
                if field_name == "claim_ids":
                    covered_claim_ids.update(values)
        if not isinstance(coverage.get("gap"), str):
            findings.error(f"{label}: gap must be a string")
        if not _utc_timestamp(coverage.get("updated_at")):
            findings.error(f"{label}: updated_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(coverage.get("updated_at"), f"{label}: updated_at", findings, now, run_created_at)
        has_claims = isinstance(claim_ids, list) and bool(claim_ids)
        has_sources = isinstance(source_ids, list) and bool(source_ids)
        has_gap = isinstance(coverage.get("gap"), str) and bool(coverage["gap"].strip())
        if status == "covered" and (not has_claims or not has_sources or has_gap):
            findings.error(f"{label}: covered status requires non-empty claim_ids/source_ids and an empty gap")
        if status == "partial" and (not has_claims or not has_sources or not has_gap):
            findings.error(f"{label}: partial status requires claim_ids, source_ids, and a non-empty gap")
        if status in {"no-reliable-evidence", "out-of-scope"} and not has_gap:
            findings.error(f"{label}: {status} status requires a non-empty gap")
    if (sources or claims) and not coverage_records:
        findings.error("coverage.jsonl: sources or claims require at least one coverage record")
    if not sources and not claims and not coverage_records:
        findings.warning("coverage.jsonl: no coverage records while the bundle has no sources or claims")
    if requirement_by_id:
        for requirement_id, requirement in requirement_by_id.items():
            matching = [coverage for coverage in coverage_by_id.values() if coverage.get("question_id") == requirement_id]
            if len(matching) != 1:
                findings.error(f"requirement {requirement_id}: must map to exactly one coverage row")
                continue
            coverage = matching[0]
            if coverage.get("question") != requirement.get("text"):
                findings.error(f"requirement {requirement_id}: coverage question must exactly match requirement text")
            if coverage.get("required_lanes") != requirement.get("required_lanes"):
                findings.error(f"requirement {requirement_id}: coverage required_lanes must exactly match")
        for question_id in coverage_by_id:
            if question_id not in requirement_by_id:
                findings.error(f"coverage {question_id}: must map to a requirement record")
    for claim_id, claim in claim_by_id.items():
        if claim.get("status") in {"supported", "qualified", "conflicted"} and claim_id not in covered_claim_ids:
            findings.error(f"claim {claim_id}: is not referenced by any coverage row")

    evidence_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = {}
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(evidence_records, 1):
        label = f"evidence.jsonl:{index}"
        if not _require_fields(record, EVIDENCE_FIELDS, label, findings):
            continue
        evidence_id = record.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            findings.error(f"{label}: evidence_id must be a non-empty string")
        elif evidence_id in evidence_by_id:
            findings.error(f"{label}: duplicate evidence_id {evidence_id}")
        else:
            evidence_by_id[evidence_id] = record
        claim_id, source_id = record.get("claim_id"), record.get("source_id")
        if not isinstance(claim_id, str) or not claim_id:
            findings.error(f"{label}: claim_id must be a non-empty string")
        elif claim_id not in claim_by_id:
            findings.error(f"{label}: references unknown claim {claim_id}")
        if not isinstance(source_id, str) or not source_id:
            findings.error(f"{label}: source_id must be a non-empty string")
        elif source_id not in source_by_id:
            findings.error(f"{label}: references unknown source {source_id}")
        if record.get("relation") not in EVIDENCE_RELATIONS:
            findings.error(f"{label}: relation must be one of {', '.join(sorted(EVIDENCE_RELATIONS))}")
        for field_name in ("locator", "support_summary"):
            if not isinstance(record.get(field_name), str):
                findings.error(f"{label}: {field_name} must be a string")
        if not _utc_timestamp(record.get("checked_at")):
            findings.error(f"{label}: checked_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(record.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
        if isinstance(source_id, str) and source_id in source_by_id:
            checked_at = _parse_utc_timestamp(record.get("checked_at"))
            fetched_at = _parse_utc_timestamp(source_by_id[source_id].get("fetched_at"))
            if checked_at is not None and fetched_at is not None and checked_at < fetched_at - timedelta(minutes=5):
                findings.error(f"{label}: checked_at is earlier than source {source_id} fetched_at minus 5 minutes")
        if isinstance(claim_id, str) and isinstance(source_id, str):
            evidence_by_pair.setdefault((claim_id, source_id), []).append(record)

    joins_by_claim: dict[str, list[dict[str, Any]]] = {}
    referenced_sources: set[str] = set()
    for record in evidence_by_id.values():
        claim_id, source_id = record.get("claim_id"), record.get("source_id")
        if isinstance(claim_id, str) and claim_id in claim_by_id and isinstance(source_id, str) and source_id in source_by_id:
            joins_by_claim.setdefault(claim_id, []).append(record)
            referenced_sources.add(source_id)

    semantic_by_claim: dict[str, dict[str, Any]] = {}
    for index, check in enumerate(semantic_check_records, 1):
        label = f"semantic_checks.jsonl:{index}"
        if not _require_fields(check, SEMANTIC_CHECK_FIELDS, label, findings):
            continue
        claim_id = check.get("claim_id")
        if not isinstance(claim_id, str) or claim_id not in claim_by_id:
            findings.error(f"{label}: claim_id references an unknown claim")
        elif claim_id in semantic_by_claim:
            findings.error(f"{label}: duplicate semantic check for claim {claim_id}")
        else:
            semantic_by_claim[claim_id] = check
        if check.get("verdict") not in SEMANTIC_VERDICTS:
            findings.error(f"{label}: verdict must be pass, revise, or drop")
        for field_name in ("evidence_ids", "uncovered_terms"):
            values = check.get(field_name)
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                findings.error(f"{label}: {field_name} must be a list of strings")
        if not isinstance(check.get("rationale"), str) or not check["rationale"].strip():
            findings.error(f"{label}: rationale must be a non-empty string")
        if not _utc_timestamp(check.get("checked_at")):
            findings.error(f"{label}: checked_at must be YYYY-MM-DDTHH:MM:SSZ")
        _validate_timestamp_window(check.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
        if isinstance(claim_id, str) and isinstance(check.get("evidence_ids"), list):
            for evidence_id in check["evidence_ids"]:
                evidence_record = evidence_by_id.get(evidence_id)
                if evidence_record is None:
                    findings.error(f"{label}: evidence_ids references unknown evidence {evidence_id}")
                elif evidence_record.get("claim_id") != claim_id:
                    findings.error(f"{label}: evidence {evidence_id} belongs to a different claim")
    for claim_id in claim_by_id:
        if claim_id not in semantic_by_claim:
            findings.error(f"claim {claim_id}: requires exactly one semantic check")

    lane_source_types = {
        "paper": {"paper"}, "github": {"repository"}, "standards": {"standard"},
        "product": {"official-doc", "release", "repository"}, "benchmark": {"paper", "dataset", "repository"},
        "adoption": {"industry", "community", "repository"}, "negative": {"issue", "journalism", "community", "research-log"},
        "history": {"paper", "release", "official-doc"}, "mechanism": {"paper", "official-doc", "standard", "repository"},
    }
    for question_id, coverage in coverage_by_id.items():
        source_ids = coverage.get("source_ids") if isinstance(coverage.get("source_ids"), list) else []
        claim_ids = coverage.get("claim_ids") if isinstance(coverage.get("claim_ids"), list) else []
        for claim_id in claim_ids:
            for source_id in source_ids:
                if not evidence_by_pair.get((claim_id, source_id), []):
                    findings.error(f"coverage {question_id}: claim {claim_id} and source {source_id} need an evidence join")
        for lane in coverage.get("required_lanes", []):
            allowed = lane_source_types.get(lane, set())
            if allowed and not any(source_by_id.get(source_id, {}).get("source_type") in allowed for source_id in source_ids):
                findings.error(f"coverage {question_id}: lane {lane} lacks a compatible source type")
        if coverage.get("status") == "no-reliable-evidence":
            research_log_ids = [source_id for source_id in source_ids if source_by_id.get(source_id, {}).get("source_type") == "research-log"]
            bounded_claim_ids = [
                claim_id for claim_id in claim_ids
                if claim_by_id.get(claim_id, {}).get("claim_type") == "inference"
                and "bounded" in str(claim_by_id.get(claim_id, {}).get("scope", "")).casefold()
            ]
            if not research_log_ids or not bounded_claim_ids:
                findings.error(f"coverage {question_id}: no-reliable-evidence requires a research-log source and bounded-inference claim")
            elif not any(
                any(record.get("relation") in {"supports", "partial"} for record in evidence_by_pair.get((claim_id, source_id), []))
                for claim_id in bounded_claim_ids for source_id in research_log_ids
            ):
                findings.error(f"coverage {question_id}: no-reliable-evidence needs a closed research-log evidence join")

    for claim_id, claim in claim_by_id.items():
        joins = joins_by_claim.get(claim_id, [])
        supporting = [record for record in joins if record.get("relation") in {"supports", "partial"}]
        direct_supports = [record for record in joins if record.get("relation") == "supports"]
        contradicting = [record for record in joins if record.get("relation") == "contradicts"]
        status = claim.get("status")
        if status in {"supported", "qualified"} and not supporting:
            findings.error(f"claim {claim_id}: {status} claim requires a supports or partial evidence join")
        if status == "conflicted" and (not direct_supports or not contradicting):
            findings.error(f"claim {claim_id}: conflicted claim requires both supports and contradicts evidence joins")
        support_sources = [source_by_id[record["source_id"]] for record in supporting]
        if support_sources and all(source.get("source_type") == "research-log" for source in support_sources) and claim.get("claim_type") != "inference":
            findings.error(f"claim {claim_id}: non-inference claim cannot be supported only by research-log sources")
        if claim.get("risk") == "high" and status in {"supported", "qualified", "conflicted"}:
            if not any(
                isinstance(record.get("locator"), str) and record["locator"].strip()
                and isinstance(record.get("support_summary"), str) and record["support_summary"].strip()
                and source_by_id[record["source_id"]].get("access_status") == "opened"
                for record in direct_supports
            ):
                findings.error(
                    f"claim {claim_id}: high-risk claim requires an opened supports evidence join "
                    "with non-empty locator and support_summary"
                )
            if support_sources and not any(source.get("tier") == "T1" for source in support_sources):
                findings.error(f"claim {claim_id}: high-risk claim requires at least one T1 source")
            independence_groups = {
                source.get("independence_group") for source in support_sources
                if isinstance(source.get("independence_group"), str) and source.get("independence_group")
            }
            if len(independence_groups) < 2:
                findings.advisory(f"claim {claim_id}: high-risk claim has fewer than two independent source groups")
        statement = claim.get("statement", "")
        if isinstance(statement, str) and CURRENT_PATTERN.search(statement) and supporting:
            metadata_present = any(
                bool(PINNED_COMMIT_PATTERN.fullmatch(repository_by_source_id[record["source_id"]].get("pinned_commit", "")))
                if source_by_id[record["source_id"]].get("source_type") == "repository" and record["source_id"] in repository_by_source_id
                else source_by_id[record["source_id"]].get("version") not in (None, "")
                or source_by_id[record["source_id"]].get("published_at") not in (None, "")
                for record in supporting
            )
            if not metadata_present:
                findings.error(f"claim {claim_id}: current-status claim needs version or publication-date metadata")

    for source_id in source_by_id:
        if source_id not in referenced_sources:
            findings.warning(f"source {source_id}: unused by all evidence joins")

    report_text = ""
    landscape_has_table = False
    report = root / "report.md"
    if report.is_file():
        registered_urls = {normalize_url(source["url"]) for source in source_by_id.values() if _http_url(source.get("url"))}
        try:
            report_text = report.read_text(encoding="utf-8")
            report_urls = _markdown_urls(report_text)
        except OSError as exc:
            findings.error(f"report.md: cannot read: {exc}")
        else:
            if len(report_text.strip()) < 200:
                findings.warning("report.md: report is too short to be a completed landscape")
            if run and str(run.get("as_of")) not in report_text:
                findings.error("report.md: does not contain the run as_of date")
            if run and str(run.get("topic", "")).casefold() not in report_text.casefold():
                findings.error("report.md: does not contain the run topic")
            section_lines: list[tuple[int, str]] = []
            for line_number, line in enumerate(report_text.splitlines(), 1):
                if "<!-- section:" in line and not SECTION_MARKER_PATTERN.fullmatch(line.strip()):
                    findings.error(f"report.md:{line_number}: section marker must be on its own line")
                match = SECTION_MARKER_PATTERN.fullmatch(line.strip())
                if match:
                    section_lines.append((line_number, match.group(1)))
            if claims and run and run.get("review_profile") == "full":
                section_names = [name for _, name in section_lines]
                if section_names != list(SECTION_NAMES):
                    findings.error("report.md: section markers must appear exactly once in the required order")
                report_blocks = _report_blocks(report_text)
                for position, section_name in enumerate(CORE_SECTION_NAMES):
                    if section_names.count(section_name) != 1:
                        continue
                    start_line = next(line for line, name in section_lines if name == section_name)
                    next_line = min((line for line, _ in section_lines if line > start_line), default=float("inf"))
                    if not any(
                        start_line < line_number < next_line and CLAIM_MARKER_PATTERN.search(block)
                        for line_number, block, _ in report_blocks
                    ):
                        findings.error(f"report.md: section {section_name} requires at least one claim block")
                if section_names.count("landscape") == 1:
                    landscape_start = next(line for line, name in section_lines if name == "landscape")
                    landscape_end = min((line for line, _ in section_lines if line > landscape_start), default=float("inf"))
                    landscape_has_table = any(
                        landscape_start < line_number < landscape_end and is_table
                        for line_number, _, is_table in report_blocks
                    )
            marker_counts: dict[str, int] = {}
            for claim_id in CLAIM_MARKER_PATTERN.findall(report_text):
                marker_counts[claim_id] = marker_counts.get(claim_id, 0) + 1
            for claim_id, count in marker_counts.items():
                if claim_id not in claim_by_id:
                    findings.error(f"report.md: claim marker references unknown claim {claim_id}")
                elif count > 1:
                    findings.warning(f"report.md: claim marker {claim_id} appears {count} times")
                elif claim_by_id[claim_id].get("status") == "unsupported":
                    findings.error(f"report.md: unsupported claim {claim_id} must not appear in the report")
                elif (
                    (check := semantic_by_claim.get(claim_id)) is None
                    or check.get("verdict") != "pass"
                    or check.get("uncovered_terms") != []
                    or not isinstance(check.get("rationale"), str) or not check["rationale"].strip()
                    or not any(
                        evidence_by_id.get(evidence_id, {}).get("claim_id") == claim_id
                        and evidence_by_id[evidence_id].get("relation") == "supports"
                        for evidence_id in check.get("evidence_ids", []) if isinstance(evidence_id, str)
                    )
                ):
                    findings.error(f"report.md: claim {claim_id} requires a passing closed semantic check")
            for line_number, block, is_table in _report_blocks(report_text):
                claim_matches = list(CLAIM_MARKER_PATTERN.finditer(block))
                process_matches = list(PROCESS_MARKER_PATTERN.finditer(block))
                marker_count = len(claim_matches) + len(process_matches)
                if marker_count != 1:
                    findings.error(
                        f"report.md:{line_number}: substantive block requires exactly one claim or process marker"
                    )
                    continue
                if claim_matches and not is_table:
                    claim_id = claim_matches[0].group(1)
                    claim = claim_by_id.get(claim_id)
                    if claim is not None:
                        prefix = _strip_block_prefix(block[:claim_matches[0].start()])
                        if prefix != claim.get("statement"):
                            findings.error(
                                f"report.md:{line_number}: claim marker {claim_id} must follow the exact statement as the only prose before it"
                            )
            for claim_id, claim in claim_by_id.items():
                if claim.get("status") in {"supported", "qualified", "conflicted"} and claim_id not in marker_counts:
                    findings.error(f"report.md: reported claim {claim_id} is missing a claim marker")
                if claim.get("status") == "unsupported" and isinstance(claim.get("statement"), str) and claim["statement"] in report_text:
                    findings.error(f"report.md: unsupported claim {claim_id} statement must not appear in the report")
                if claim.get("status") in {"supported", "qualified", "conflicted"}:
                    statement = claim.get("statement")
                    if isinstance(statement, str):
                        statement_count = report_text.count(statement)
                        if statement_count > 1:
                            findings.warning(f"report.md: claim statement {claim_id} appears {statement_count} times")
                        scoped_marker = re.compile(re.escape(statement) + r"\s*<!--\s*claim:" + re.escape(claim_id) + r"\s*-->")
                        if not scoped_marker.search(report_text):
                            findings.error(f"report.md: reported claim {claim_id} needs its exact statement immediately before the claim marker")
            for url in sorted(report_urls):
                if normalize_url(url) not in registered_urls:
                    findings.error(f"report.md: URL is not registered in sources.jsonl: {url}")
    if strict and run and run.get("review_profile") == "full":
        full_counts = {
            "requirements": len(requirement_by_id), "queries": len(query_by_id), "sources": len(source_by_id),
            "claims": len(claim_by_id), "evidence": len(evidence_by_id),
        }
        for label, minimum in (("requirements", 6), ("queries", max(len(requirement_by_id), 8)), ("sources", 12), ("claims", 12), ("evidence", 12)):
            if full_counts[label] < minimum:
                findings.error(f"full profile: requires at least {minimum} {label}")
        for pass_number in (1, 2, 3):
            if sum(1 for query in query_by_id.values() if query.get("pass") == pass_number) < 2:
                findings.error(f"full profile: requires at least 2 pass {pass_number} queries")
        if len(report_text) < 6000:
            findings.error("full profile: report.md must contain at least 6000 characters")
        required_lanes = {lane for requirement in requirement_by_id.values() for lane in requirement.get("required_lanes", [])}
        if "github" in required_lanes and len(repository_by_source_id) < 2:
            findings.error("full profile: github lane requires at least 2 repository cards")
        if "paper" in required_lanes and len(paper_by_source_id) < 4:
            findings.error("full profile: paper lane requires at least 4 paper cards")
        if not any(record.get("decision") in {"excluded", "deferred"} for record in candidate_records):
            findings.error("full profile: requires at least one excluded or deferred candidate")
        nonretained = [record for record in candidate_records if record.get("decision") in {"excluded", "deferred"}]
        if len(nonretained) < max(5, -(-len(candidate_records) // 10)):
            findings.error("full profile: requires at least max(5, ceil(10% of candidates)) excluded/deferred candidates")
        for pass_number in (1, 2, 3):
            if not any(
                record.get("decision") in {"excluded", "deferred"}
                and query_by_id.get(record.get("query_id"), {}).get("pass") == pass_number
                for record in candidate_records
            ):
                findings.error(f"full profile: pass {pass_number} requires an excluded or deferred candidate")
        if not landscape_has_table:
            findings.error("full profile: landscape section requires a Markdown data table")
    return findings


def _markdown_urls(markdown: str) -> set[str]:
    urls = {match.group(1) for match in MARKDOWN_URL_PATTERN.finditer(markdown)}
    urls.update(match.group(1) for match in AUTOLINK_URL_PATTERN.finditer(markdown))
    urls.update(match.group(0).rstrip('.,;:!?]}"') for match in BARE_URL_PATTERN.finditer(markdown))
    return urls


def _report_blocks(markdown: str) -> list[tuple[int, str, bool]]:
    """Return substantive Markdown blocks outside fences as (line, text, table)."""
    blocks: list[tuple[int, str, bool]] = []
    prose: list[str] = []
    prose_line = 0
    in_fence = False
    lines = markdown.splitlines()

    def flush() -> None:
        nonlocal prose, prose_line
        if prose:
            blocks.append((prose_line, "\n".join(prose), False))
            prose, prose_line = [], 0

    separator = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
    horizontal = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
    for index, line in enumerate(lines, 1):
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if SECTION_MARKER_PATTERN.fullmatch(line.strip()):
            flush()
            continue
        if not line.strip() or re.match(r"^\s{0,3}#{1,6}\s", line) or horizontal.match(line) or separator.match(line):
            flush()
            continue
        is_table = "|" in line and not re.match(r"^\s*(?:[-*+]\s+|>\s*)", line)
        next_is_separator = index < len(lines) and bool(separator.match(lines[index]))
        if is_table:
            flush()
            if not next_is_separator:
                blocks.append((index, line, True))
            continue
        if re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s*)", line):
            flush()
            blocks.append((index, line, False))
            continue
        if not prose:
            prose_line = index
        prose.append(line)
    flush()
    return blocks


def _strip_block_prefix(value: str) -> str:
    return re.sub(r"^\s*(?:(?:[-*+]\s+|\d+[.)]\s+)|>\s*)", "", value).strip()


def _write_new(path: Path, content: str) -> None:
    """Write exactly once. Exclusive creation prevents accidental overwrites."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except FileExistsError as exc:
        raise BundleError(f"refusing to overwrite existing file: {path}") from exc


def _v2_records(root: Path, filename: str, findings: Findings) -> list[dict[str, Any]]:
    return _read_jsonl(root / filename, filename, findings) if (root / filename).is_file() else []


def _v2_id_map(records: list[dict[str, Any]], field_name: str, filename: str, findings: Findings) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records, 1):
        value = record.get(field_name)
        if not isinstance(value, str) or not value:
            findings.error(f"{filename}:{index}: {field_name} must be a non-empty string")
        elif value in result:
            findings.error(f"{filename}:{index}: duplicate {field_name} {value}")
        else:
            result[value] = record
    return result


def _validate_v2_bundle(root: Path, *, strict: bool = False) -> Findings:
    """Validate the 2.0 layered corpus, while retaining 1.7 as a separate path."""
    findings = Findings(); now = datetime.now(timezone.utc)
    if not root.is_dir():
        findings.error(f"bundle root does not exist or is not a directory: {root}"); return findings
    for filename in V2_BASE_FILES:
        if not (root / filename).is_file(): findings.error(f"missing required file: {filename}")
    try:
        run = json.loads((root / "run.json").read_text(encoding="utf-8"))
        plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.error(f"run.json/research_plan.json: invalid JSON or unreadable: {exc}"); return findings
    if run.get("schema_version") != V2_SCHEMA_VERSION: findings.error("run.json: unsupported schema_version")
    if not isinstance(run.get("topic"), str) or not run["topic"].strip() or not _iso_date(run.get("as_of")): findings.error("run.json: topic/as_of are invalid")
    if run.get("review_profile") not in {"full", "rapid", "comprehensive"}: findings.error("run.json: review_profile is invalid")
    comprehensive = run.get("review_profile") == "comprehensive"
    run_created_at = _parse_utc_timestamp(run.get("created_at"))
    if run_created_at is None: findings.error("run.json: created_at must be UTC")
    else: _validate_timestamp_window(run.get("created_at"), "run.json: created_at", findings, now, None)
    _require_fields(plan, V2_PLAN_FIELDS, "research_plan.json", findings)
    if any(plan.get(key) != run.get(key) for key in ("schema_version", "topic", "as_of")): findings.error("research_plan.json: schema_version/topic/as_of must match run.json")
    for name in ("lanes", "time_windows", "required_deliverable_kinds"):
        if not isinstance(plan.get(name), list) or not all(isinstance(value, str) and value for value in plan[name]): findings.error(f"research_plan.json: {name} must be a list of non-empty strings")
    if plan.get("important_cluster_policy") not in {"saturated", "all-covered"}: findings.error("research_plan.json: important_cluster_policy is invalid")
    targets = plan.get("targets")
    if not isinstance(targets, dict) or set(targets) - V2_TARGETS or any(value is not None and (type(value) is not int or value < 0) for value in targets.values()): findings.error("research_plan.json: targets must use declared target names and non-negative integers or null")
    declared_kinds = plan.get("required_deliverable_kinds", [])
    if any(kind not in V2_DELIVERABLE_KINDS for kind in declared_kinds):
        findings.error("research_plan.json: required_deliverable_kinds must use known deliverable kinds")
    if comprehensive:
        missing_lanes = {"paper", "github", "benchmark", "negative"} - set(plan.get("lanes", []))
        if missing_lanes:
            findings.error("research_plan.json: comprehensive profile requires paper/github/benchmark/negative lanes")
        missing_targets = V2_TARGETS - set(targets) if isinstance(targets, dict) else V2_TARGETS
        if missing_targets or any(type(targets.get(name)) is not int or targets[name] <= 0 for name in V2_TARGETS if name in targets):
            findings.error("research_plan.json: comprehensive profile requires every target to be an explicit positive integer")
        if not V2_COMPREHENSIVE_DELIVERABLE_KINDS <= set(declared_kinds):
            findings.error("research_plan.json: comprehensive profile is missing required deliverable kinds")
    records = {name: _v2_records(root, name, findings) for name in V2_BASE_FILES if name.endswith(".jsonl")}
    # Detailed cell-level coverage proofs are an optional audit surface. When a
    # run supplies them, validate them strictly; ordinary comprehensive runs
    # are judged on aggregate breadth, material gaps, and reader quality.
    records["coverage-proofs.jsonl"] = _v2_records(root, "coverage-proofs.jsonl", findings) if (root / "coverage-proofs.jsonl").is_file() else []
    def list_of(value: Any) -> bool: return isinstance(value, list) and all(isinstance(item, str) and item for item in value)
    def text(value: Any) -> bool: return isinstance(value, str) and bool(value.strip())
    for filename, fields in {"screening.jsonl": V2_SCREENING_FIELDS, "stage_events.jsonl": V2_STAGE_EVENT_FIELDS, "cluster_assignments.jsonl": V2_ASSIGNMENT_FIELDS, "time_windows.jsonl": V2_WINDOW_FIELDS, "repository_observations.jsonl": V2_REPOSITORY_OBSERVATION_FIELDS, "repository_engineering_profiles.jsonl": V2_REPOSITORY_ENGINEERING_PROFILE_FIELDS, "trend_metrics.jsonl": V2_TREND_FIELDS, "saturation_events.jsonl": V2_SATURATION_EVENT_FIELDS, "saturation.jsonl": V2_SATURATION_FIELDS, "research_questions.jsonl": V2_QUESTION_FIELDS, "gaps.jsonl": V2_GAP_FIELDS, "syntheses.jsonl": V2_SYNTHESIS_FIELDS, "relations.jsonl": V2_RELATION_FIELDS}.items():
        for index, row in enumerate(records[filename], 1): _require_fields(row, fields, f"{filename}:{index}", findings)

    queries = records["queries.jsonl"]; query_by_id = _v2_id_map(queries, "query_id", "queries.jsonl", findings)
    for index, row in enumerate(queries, 1):
        label = f"queries.jsonl:{index}"; _require_fields(row, V2_QUERY_FIELDS, label, findings)
        if row.get("stage") not in V2_QUERY_STAGES or type(row.get("iteration")) is not int or row["iteration"] < 1: findings.error(f"{label}: stage/iteration are invalid")
        if not all(list_of(row.get(name)) for name in ("target_lanes", "target_window_ids", "target_cluster_ids", "parent_query_ids", "gap_ids")) or not text(row.get("information_gain")): findings.error(f"{label}: target/parent/gap fields or information_gain are invalid")
        if not text(row.get("provider")) or not text(row.get("query_text")) or row.get("status") not in V2_QUERY_STATUSES: findings.error(f"{label}: provider/query_text/status are invalid")
        if row.get("request_url") is not None and not _http_url(row.get("request_url")): findings.error(f"{label}: request_url must be null or http(s)")
        if not isinstance(row.get("raw_snapshot_paths"), list) or not all(isinstance(value, str) and value for value in row.get("raw_snapshot_paths", [])): findings.error(f"{label}: raw_snapshot_paths must be a string list")
        result_count = row.get("result_count")
        if result_count is not None and (type(result_count) is not int or result_count < 0): findings.error(f"{label}: result_count must be a non-negative integer or null")
        if not isinstance(row.get("result_count_note"), str) or result_count is None and not text(row.get("result_count_note")): findings.error(f"{label}: result_count=null requires a non-empty result_count_note")
        if row.get("status") in {"failed", "blocked", "partial"} and not text(row.get("result_count_note")): findings.error(f"{label}: unsuccessful or partial queries require a result_count_note")
        if not _utc_timestamp(row.get("executed_at")): findings.error(f"{label}: executed_at must be UTC")
        _validate_timestamp_window(row.get("executed_at"), f"{label}: executed_at", findings, now, run_created_at)
    if comprehensive:
        stages = {row.get("stage") for row in queries}
        required_stages = {"discover", "gap-fill", "deep-focus", "verify", "adversarial"}
        if not required_stages <= stages:
            findings.error("queries.jsonl: comprehensive profile requires discover, gap-fill, deep-focus, verify, and adversarial stages")
        for lane in ("paper", "github"):
            if not any(row.get("stage") == "discover" and lane in row.get("target_lanes", []) for row in queries):
                findings.error(f"queries.jsonl: comprehensive profile requires a {lane} discover query")
    discoveries = records["discovery_results.jsonl"]; discovery_by_id = _v2_id_map(discoveries, "discovery_id", "discovery_results.jsonl", findings)
    for index, row in enumerate(discoveries, 1):
        label = f"discovery_results.jsonl:{index}"; _require_fields(row, V2_DISCOVERY_FIELDS, label, findings)
        if row.get("query_id") not in query_by_id or not text(row.get("provider")) or not text(row.get("title")) or not _http_url(row.get("url")) or not _utc_timestamp(row.get("observed_at")): findings.error(f"{label}: occurrence must contain query/provider/title/http URL/UTC metadata")
        _validate_timestamp_window(row.get("observed_at"), f"{label}: observed_at", findings, now, run_created_at)
    entities = records["entities.jsonl"]; entity_by_id = _v2_id_map(entities, "entity_id", "entities.jsonl", findings)
    for index, row in enumerate(entities, 1):
        label = f"entities.jsonl:{index}"; _require_fields(row, V2_ENTITY_FIELDS, label, findings)
        time_window_ids = row.get("time_window_ids")
        if not text(row.get("canonical_name")) or not _http_url(row.get("url")) or not list_of(row.get("discovery_ids")) or not isinstance(time_window_ids, list) or not all(isinstance(window_id, str) and window_id for window_id in time_window_ids) or not isinstance(row.get("aliases"), list): findings.error(f"{label}: canonical/discovery/window fields are invalid")
        if row.get("stage") not in V2_ENTITY_STAGES or row.get("entity_type") not in {"paper", "repository", "dataset", "product", "standard", "organization", "other"}: findings.error(f"{label}: stage/entity_type are invalid")
        if row.get("published_at") is not None and not _iso_date(row.get("published_at")): findings.error(f"{label}: published_at must be an ISO date or null")
        if not _utc_timestamp(row.get("created_at")) or not _utc_timestamp(row.get("updated_at")) or row.get("date_confidence") not in {"exact", "month", "year", "unknown"}: findings.error(f"{label}: date fields are invalid")
        for discovery_id in row.get("discovery_ids", []):
            if discovery_id not in discovery_by_id: findings.error(f"{label}: discovery_ids references an unknown occurrence")
        if not isinstance(row.get("source_ids"), list) or not all(isinstance(item, str) for item in row["source_ids"]): findings.error(f"{label}: source_ids must be a list of strings")
    discovery_use = {discovery_id: 0 for discovery_id in discovery_by_id}
    for row in entities:
        for discovery_id in row.get("discovery_ids", []):
            if discovery_id in discovery_use: discovery_use[discovery_id] += 1
    if any(count != 1 for count in discovery_use.values()): findings.error("entities.jsonl: every discovery occurrence must be assigned to exactly one entity")
    clusters = records["clusters.jsonl"]; cluster_by_id = _v2_id_map(clusters, "cluster_id", "clusters.jsonl", findings)
    for index, row in enumerate(clusters, 1):
        label = f"clusters.jsonl:{index}"; _require_fields(row, V2_CLUSTER_FIELDS, label, findings)
        if row.get("importance") not in {"important", "normal"} or row.get("confidence") not in CLAIM_CONFIDENCES or not list_of(row.get("parent_ids")) and row.get("parent_ids") != [] or not list_of(row.get("required_lanes")) or not all(text(row.get(name)) for name in ("label", "definition", "inclusion", "exclusion", "problem")): findings.error(f"{label}: cluster metadata is invalid")
        if not all(isinstance(value, str) for name in ("architecture_patterns", "implementation_patterns", "tradeoffs") for value in row.get(name, [])): findings.error(f"{label}: patterns/tradeoffs must be string lists")
        if any(lane not in plan.get("lanes", []) for lane in row.get("required_lanes", [])): findings.error(f"{label}: required_lanes must be declared by research_plan")
    parents = {cluster_id: row.get("parent_ids", []) for cluster_id, row in cluster_by_id.items()}
    def cyclic(node: str, stack: set[str], done: set[str]) -> bool:
        if node in stack: return True
        if node in done: return False
        stack.add(node); bad = any(parent not in parents or cyclic(parent, stack, done) for parent in parents[node]); stack.remove(node); done.add(node); return bad
    if any(cyclic(cluster_id, set(), set()) for cluster_id in parents): findings.error("clusters.jsonl: parent_ids must form an acyclic known DAG")
    assignments = records["cluster_assignments.jsonl"]; _v2_id_map(assignments, "assignment_id", "cluster_assignments.jsonl", findings); assigned: set[str] = set()
    for index, row in enumerate(assignments, 1):
        label = f"cluster_assignments.jsonl:{index}"
        if row.get("entity_id") not in entity_by_id or row.get("cluster_id") not in cluster_by_id or row.get("membership") not in {"primary", "secondary", "bridge"} or row.get("confidence") not in CLAIM_CONFIDENCES or not all(text(row.get(name)) for name in ("rationale", "method")) or not _utc_timestamp(row.get("time")): findings.error(f"{label}: assignment fields are invalid")
        else: assigned.add(row["entity_id"])
    for entity_id, row in entity_by_id.items():
        if row.get("stage") in {"mapped", "deep-verified"} and entity_id not in assigned: findings.error(f"entity {entity_id}: mapped/deep-verified entity requires an assignment")
        if row.get("stage") == "discovered" and row.get("source_ids"): findings.error(f"entity {entity_id}: discovered entity cannot have deep sources")
    windows = _v2_id_map(records["time_windows.jsonl"], "window_id", "time_windows.jsonl", findings)
    for index, row in enumerate(records["time_windows.jsonl"], 1):
        if not _iso_date(row.get("start")) or not _iso_date(row.get("end")) or row["start"] > row["end"] or row.get("kind") not in {"foundational", "established", "recent-12m", "recent-90d", "custom"}: findings.error(f"time_windows.jsonl:{index}: time window is invalid")
    if set(plan.get("time_windows", [])) != set(windows): findings.error("research_plan.json: time_windows must exactly declare time_windows.jsonl IDs")
    if comprehensive:
        window_kinds = {row.get("kind") for row in windows.values()}
        if not {"foundational", "recent-12m", "recent-90d"} <= window_kinds:
            findings.error("time_windows.jsonl: comprehensive profile requires foundational, recent-12m, and recent-90d windows")
    for entity in entities:
        if any(window_id not in windows for window_id in entity.get("time_window_ids", [])): findings.error(f"entity {entity.get('entity_id')}: time_window_ids must exist")
        if entity.get("date_confidence") == "exact" and _iso_date(entity.get("published_at")):
            expected_windows = {
                window_id for window_id, window in windows.items()
                if window.get("start") <= entity["published_at"] <= window.get("end")
            }
            if set(entity.get("time_window_ids", [])) != expected_windows:
                findings.error(f"entity {entity.get('entity_id')}: exact published_at must reconcile to every matching time window and no others")
    coverage_keys: set[tuple[str, str, str]] = set()
    coverage_row_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for index, row in enumerate(records["cluster_coverage.jsonl"], 1):
        _require_fields(row, V2_CLUSTER_COVERAGE_FIELDS, f"cluster_coverage.jsonl:{index}", findings); key = (row.get("cluster_id"), row.get("lane"), row.get("window_id"))
        if key in coverage_keys or key[0] not in cluster_by_id or key[1] not in plan.get("lanes", []) or key[2] not in windows or row.get("status") not in V2_CLUSTER_COVERAGE_STATUSES: findings.error(f"cluster_coverage.jsonl:{index}: cluster/lane/window coverage is invalid, duplicate, or has an unknown status")
        coverage_keys.add(key)
        coverage_row_by_key[key] = row
    coverage_proofs = records["coverage-proofs.jsonl"]
    _v2_id_map(coverage_proofs, "proof_id", "coverage-proofs.jsonl", findings)
    coverage_proof_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for index, proof in enumerate(coverage_proofs, 1):
        label = f"coverage-proofs.jsonl:{index}"
        _require_fields(proof, V2_COVERAGE_PROOF_FIELDS, label, findings)
        key = (proof.get("cluster_id"), proof.get("lane"), proof.get("window_id"))
        provenance = proof.get("provenance")
        if key in coverage_proof_by_key or key not in coverage_keys:
            findings.error(f"{label}: proof key must map one-to-one to a unique cluster_coverage row")
        else:
            coverage_proof_by_key[key] = proof
        if proof.get("applicability") not in V2_COVERAGE_APPLICABILITY or proof.get("status") not in V2_CLUSTER_COVERAGE_STATUSES or proof.get("coverage_basis") not in V2_COVERAGE_BASES:
            findings.error(f"{label}: applicability, status, or coverage_basis is invalid")
        if type(proof.get("positive_entity_count")) is not int or proof.get("positive_entity_count", -1) < 0 or not text(proof.get("scope_claim")) or not list_of(proof.get("missing_gates")) and proof.get("missing_gates") != [] or not text(proof.get("rationale")) or not _utc_timestamp(proof.get("checked_at")):
            findings.error(f"{label}: count, scope claim, missing gates, rationale, or checked_at is invalid")
        if not isinstance(provenance, dict):
            findings.error(f"{label}: provenance must be an object")
        else:
            _require_fields(provenance, V2_COVERAGE_PROVENANCE_FIELDS, f"{label}.provenance", findings)
            for field in V2_COVERAGE_PROVENANCE_FIELDS:
                if not isinstance(provenance.get(field), list) or any(not isinstance(value, str) or not value for value in provenance.get(field, [])):
                    findings.error(f"{label}.provenance: {field} must be a string list")
        if key in coverage_row_by_key and proof.get("status") != coverage_row_by_key[key].get("status"):
            findings.error(f"{label}: proof status must equal cluster_coverage status")
    if coverage_proofs and not set(coverage_proof_by_key) <= coverage_keys:
        findings.error("coverage-proofs.jsonl: every supplied proof must map to a cluster_coverage row")
    _v2_id_map(records["screening.jsonl"], "screening_id", "screening.jsonl", findings)
    for index, row in enumerate(records["screening.jsonl"], 1):
        if row.get("discovery_id") not in discovery_by_id or row.get("decision") not in {"exclude", "defer", "map", "deep-verify"} or not text(row.get("reason")) or not _utc_timestamp(row.get("checked_at")): findings.error(f"screening.jsonl:{index}: screening record is invalid")
    events_by_entity: dict[str, list[dict[str, Any]]] = {}
    _v2_id_map(records["stage_events.jsonl"], "event_id", "stage_events.jsonl", findings)
    for index, row in enumerate(records["stage_events.jsonl"], 1):
        if row.get("entity_id") not in entity_by_id or not _utc_timestamp(row.get("occurred_at")) or not text(row.get("rationale")): findings.error(f"stage_events.jsonl:{index}: entity/time/rationale are invalid"); continue
        events_by_entity.setdefault(row["entity_id"], []).append(row)
    for entity_id, events in events_by_entity.items():
        state = "discovered"
        for row in sorted(events, key=lambda item: item["occurred_at"]):
            if row.get("from_stage") != state or (state, row.get("to_stage")) not in {("discovered", "mapped"), ("mapped", "deep-verified")}:
                findings.error(f"stage_events.jsonl: {entity_id} must transition discovered → mapped → deep-verified without rollback or jump")
            else: state = row["to_stage"]
        if state != entity_by_id[entity_id].get("stage"): findings.error(f"entity {entity_id}: stage does not match its transition history")
    for entity_id, row in entity_by_id.items():
        if row.get("stage") != "discovered" and entity_id not in events_by_entity: findings.error(f"entity {entity_id}: non-discovered stage requires transition events")

    sources = records["sources.jsonl"]; source_by_id = _v2_id_map(sources, "source_id", "sources.jsonl", findings)
    for index, row in enumerate(sources, 1):
        label = f"sources.jsonl:{index}"; _require_fields(row, SOURCE_FIELDS | {"entity_id"}, label, findings)
        entity = entity_by_id.get(row.get("entity_id"))
        if entity is None or entity.get("stage") != "deep-verified": findings.error(f"{label}: source requires a deep-verified entity_id")
        elif row.get("source_id") not in entity.get("source_ids", []): findings.error(f"{label}: entity source_ids must reciprocally contain source_id")
        if row.get("source_type") == "research-log":
            if row.get("url") not in {"bundle://queries.jsonl", "bundle://candidates.jsonl"}: findings.error(f"{label}: research-log URL is invalid")
        elif not _http_url(row.get("url")): findings.error(f"{label}: URL must be http(s)")
        if row.get("tier") not in SOURCE_TIERS or row.get("source_type") not in SOURCE_TYPES or row.get("access_status") not in ACCESS_STATUSES or not text(row.get("access_note")): findings.error(f"{label}: tier/type/access fields are invalid")
        if not _utc_timestamp(row.get("fetched_at")): findings.error(f"{label}: fetched_at must be UTC")
        _validate_timestamp_window(row.get("fetched_at"), f"{label}: fetched_at", findings, now, run_created_at)
        if not list_of(row.get("queries")) or any(query_id not in query_by_id for query_id in row.get("queries", [])): findings.error(f"{label}: queries must reference executed v2 queries")
    for entity in entities:
        for source_id in entity.get("source_ids", []):
            if source_by_id.get(source_id, {}).get("entity_id") != entity.get("entity_id"): findings.error(f"entity {entity.get('entity_id')}: source_ids must reference reciprocal sources")
    sources_by_entity: dict[str, list[dict[str, Any]]] = {}
    for source in sources:
        sources_by_entity.setdefault(str(source.get("entity_id")), []).append(source)
    for entity_id, entity_sources in sources_by_entity.items():
        if entity_by_id.get(entity_id, {}).get("entity_type") == "repository":
            groups = {source.get("independence_group") for source in entity_sources if text(source.get("independence_group"))}
            if len(groups) > 1:
                findings.error(f"repository entity {entity_id}: API/README/tree/companion views must share one independence_group")
        entity = entity_by_id.get(entity_id, {})
        if "W_FUTURE_METADATA" in entity.get("time_window_ids", []) and any(
            source.get("access_status") == "opened"
            and source.get("tier") == "T1"
            and _iso_date(source.get("published_at"))
            and source["published_at"] <= plan.get("as_of", "")
            for source in entity_sources
        ):
            findings.error(f"entity {entity_id}: opened pre-cutoff T1 source contradicts future-metadata quarantine; reconcile the canonical date/windows")
    claims = records["claims.jsonl"]; claim_by_id = _v2_id_map(claims, "claim_id", "claims.jsonl", findings)
    for index, row in enumerate(claims, 1):
        label = f"claims.jsonl:{index}"; _require_fields(row, CLAIM_FIELDS | {"publication_status", "deliverable_ids"}, label, findings)
        if not text(row.get("statement")) or row.get("claim_type") not in CLAIM_TYPES or row.get("risk") not in CLAIM_RISKS or row.get("confidence") not in CLAIM_CONFIDENCES or row.get("status") not in CLAIM_STATUSES or row.get("publication_status") not in V2_PUBLICATION_STATUSES or not list_of(row.get("deliverable_ids")) and row.get("deliverable_ids") != []: findings.error(f"{label}: claim metadata is invalid")
    evidence = records["evidence.jsonl"]; evidence_by_id = _v2_id_map(evidence, "evidence_id", "evidence.jsonl", findings); evidence_for: dict[str, list[dict[str, Any]]] = {}
    for index, row in enumerate(evidence, 1):
        label = f"evidence.jsonl:{index}"; _require_fields(row, EVIDENCE_FIELDS, label, findings)
        if row.get("claim_id") not in claim_by_id or row.get("source_id") not in source_by_id or row.get("relation") not in EVIDENCE_RELATIONS or not _utc_timestamp(row.get("checked_at")): findings.error(f"{label}: evidence references or time are invalid")
        else:
            evidence_for.setdefault(row["claim_id"], []).append(row)
            _validate_timestamp_window(row.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
    for claim_id, claim in claim_by_id.items():
        joins = evidence_for.get(claim_id, []); supports = [row for row in joins if row.get("relation") in {"supports", "partial"}]
        if claim.get("status") in {"supported", "qualified"} and not supports: findings.error(f"claim {claim_id}: supported/qualified claim requires supports or partial evidence")
        if claim.get("status") == "conflicted" and (not any(row.get("relation") == "supports" for row in joins) or not any(row.get("relation") == "contradicts" for row in joins)): findings.error(f"claim {claim_id}: conflicted claim requires both supports and contradicts evidence")
        if claim.get("risk") == "high" and claim.get("status") in {"supported", "qualified", "conflicted"} and not any(row.get("relation") == "supports" and text(row.get("locator")) and text(row.get("support_summary")) and source_by_id.get(row.get("source_id"), {}).get("tier") == "T1" and source_by_id.get(row.get("source_id"), {}).get("access_status") == "opened" for row in joins): findings.error(f"claim {claim_id}: high-risk claim requires opened T1 direct supporting evidence")
        if claim.get("claim_type") != "inference" and joins and all(source_by_id.get(row.get("source_id"), {}).get("source_type") == "research-log" for row in joins): findings.error(f"claim {claim_id}: non-inference claim cannot rely only on research-log evidence")
    semantic_by_claim: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(records["semantic_checks.jsonl"], 1):
        label = f"semantic_checks.jsonl:{index}"; _require_fields(row, SEMANTIC_CHECK_FIELDS, label, findings); claim_id = row.get("claim_id")
        if claim_id not in claim_by_id or claim_id in semantic_by_claim or row.get("verdict") not in SEMANTIC_VERDICTS or not isinstance(row.get("evidence_ids"), list) or not isinstance(row.get("uncovered_terms"), list) or not text(row.get("rationale")) or not _utc_timestamp(row.get("checked_at")): findings.error(f"{label}: semantic audit record is invalid")
        else:
            semantic_by_claim[claim_id] = row
            if any(evidence_by_id.get(evidence_id, {}).get("claim_id") != claim_id for evidence_id in row["evidence_ids"]): findings.error(f"{label}: evidence_ids must belong to claim")
    for claim_id, claim in claim_by_id.items():
        check = semantic_by_claim.get(claim_id)
        if check is None: findings.error(f"claim {claim_id}: requires exactly one semantic check")
        elif claim.get("publication_status") == "published":
            checked_joins = [evidence_by_id.get(evidence_id, {}) for evidence_id in check.get("evidence_ids", [])]
            has_direct_support = any(join.get("relation") == "supports" for join in checked_joins)
            bounded_normal_inference = (
                claim.get("risk") != "high"
                and claim.get("claim_type") == "inference"
                and bool(checked_joins)
                and all(join.get("relation") in {"supports", "partial"} for join in checked_joins)
            )
            if check.get("verdict") != "pass" or check.get("uncovered_terms") != [] or not (has_direct_support or bounded_normal_inference):
                findings.error(f"claim {claim_id}: published claim requires closed passing semantic check plus direct support, except for a bounded normal-risk inference backed by cited partial evidence")

    repositories = records["repositories.jsonl"]; repo_by_source = _v2_id_map(repositories, "source_id", "repositories.jsonl", findings); executions = _v2_id_map(records["executions.jsonl"], "execution_id", "executions.jsonl", findings)
    for index, execution in enumerate(records["executions.jsonl"], 1):
        label = f"executions.jsonl:{index}"; _require_fields(execution, EXECUTION_FIELDS, label, findings)
        started, ended = _parse_utc_timestamp(execution.get("started_at")), _parse_utc_timestamp(execution.get("ended_at"))
        if source_by_id.get(execution.get("source_id"), {}).get("source_type") != "repository" or execution.get("purpose") not in EXECUTION_PURPOSES or not all(text(execution.get(name)) for name in ("command", "environment", "output_summary")) or started is None or ended is None or ended < started or execution.get("exit_code") != 0: findings.error(f"{label}: execution truth record is invalid")
    for index, card in enumerate(repositories, 1):
        label = f"repositories.jsonl:{index}"; _require_fields(card, REPOSITORY_FIELDS, label, findings); source = source_by_id.get(card.get("source_id"), {})
        if source.get("source_type") != "repository" or not PINNED_COMMIT_PATTERN.fullmatch(str(card.get("pinned_commit", ""))) or source.get("version") != card.get("pinned_commit") or card.get("setup") not in SETUP_STATUSES or card.get("tests_ci") not in TESTS_CI_STATUSES or card.get("affiliation") not in AFFILIATION_STATUSES or not _iso_date(card.get("pushed_at")) or not _utc_timestamp(card.get("checked_at")): findings.error(f"{label}: repository card is invalid")
        for status, field_name, purpose in ((card.get("setup"), "setup_execution_id", "setup"), (card.get("tests_ci"), "tests_execution_id", "tests")):
            execution_id = card.get(field_name)
            if status == "executed":
                if executions.get(execution_id, {}).get("source_id") != card.get("source_id") or executions.get(execution_id, {}).get("purpose") != purpose: findings.error(f"{label}: executed {purpose} requires matching execution record")
            elif execution_id is not None: findings.error(f"{label}: non-executed {purpose} must have null execution ID")
        if not isinstance(card.get("adoption_evidence"), list) or any(source_id not in source_by_id for source_id in card.get("adoption_evidence", [])): findings.error(f"{label}: adoption_evidence must reference sources")
    for source_id, source in source_by_id.items():
        if source.get("source_type") == "repository" and source_id not in repo_by_source: findings.error(f"source {source_id}: repository source requires one repository card")
    papers = records["papers.jsonl"]; paper_by_source = _v2_id_map(papers, "source_id", "papers.jsonl", findings)
    for index, card in enumerate(papers, 1):
        label = f"papers.jsonl:{index}"; _require_fields(card, PAPER_FIELDS, label, findings); source = source_by_id.get(card.get("source_id"), {})
        if source.get("source_type") != "paper" or not text(card.get("identifier")) or card.get("publication_status") not in PAPER_STATUSES or card.get("evidence_role") not in PAPER_EVIDENCE_ROLES or not text(card.get("code_search_note")) or not text(card.get("status_locator")) or not _utc_timestamp(card.get("checked_at")): findings.error(f"{label}: paper card is invalid")
        if card.get("publication_status") == "peer-reviewed" and not text(card.get("venue")): findings.error(f"{label}: peer-reviewed paper requires venue")
        if card.get("evidence_role") == "survey" and source.get("tier") != "T2": findings.error(f"{label}: survey paper source tier must be T2")
        if not list_of(card.get("data_source_ids")) and card.get("data_source_ids") != [] or any(source_by_id.get(source_id, {}).get("source_type") != "dataset" for source_id in card.get("data_source_ids", [])): findings.error(f"{label}: data_source_ids must be dataset sources")
        if not isinstance(card.get("code_links"), list): findings.error(f"{label}: code_links must be a list")
        for link in card.get("code_links", []):
            if not _require_fields(link, CODE_LINK_FIELDS, label + ":code_link", findings) or source_by_id.get(link.get("source_id"), {}).get("source_type") != "repository" or link.get("relation") not in CODE_LINK_RELATIONS or not text(link.get("paper_locator")) or not text(link.get("repo_locator")):
                findings.error(f"{label}: code link must identify a repository with exact locators")
            elif link.get("relation") == "reciprocal" and source.get("independence_group") != source_by_id[link["source_id"]].get("independence_group"):
                findings.error(f"{label}: reciprocal paper/repository artifacts must share one independence_group")
    for source_id, source in source_by_id.items():
        if source.get("source_type") == "paper" and source_id not in paper_by_source: findings.error(f"source {source_id}: paper source requires one paper card")

    observations = records["repository_observations.jsonl"]; observation_by_id = _v2_id_map(observations, "observation_id", "repository_observations.jsonl", findings)
    for index, row in enumerate(observations, 1):
        label = f"repository_observations.jsonl:{index}"; entity = entity_by_id.get(row.get("entity_id"), {})
        if entity.get("entity_type") != "repository" or not text(row.get("node_id")) or not text(row.get("owner_repo")) or not _http_url(row.get("api_url")) or not text(row.get("note")) or row.get("window_id") not in windows or not _utc_timestamp(row.get("observed_at")) or not _iso_date(row.get("created")) or not _iso_date(row.get("pushed")) or not isinstance(row.get("archived"), bool) or not isinstance(row.get("fork"), bool): findings.error(f"{label}: repository observation must bind repository entity and complete metadata")
        if any(type(row.get(name)) is not int or row[name] < 0 for name in ("stars", "forks", "open_issues", "commits_in_window", "contributors_in_window")): findings.error(f"{label}: numeric counts must be non-negative integers")
    engineering_profiles = records["repository_engineering_profiles.jsonl"]
    engineering_profile_by_id = _v2_id_map(engineering_profiles, "profile_id", "repository_engineering_profiles.jsonl", findings)
    for index, profile in enumerate(engineering_profiles, 1):
        label = f"repository_engineering_profiles.jsonl:{index}"
        entity_id = profile.get("entity_id")
        source_ids = profile.get("source_ids")
        pinned_commit = profile.get("pinned_commit")
        if entity_by_id.get(entity_id, {}).get("entity_type") != "repository" or not list_of(source_ids) or any(source_by_id.get(source_id, {}).get("entity_id") != entity_id or source_by_id.get(source_id, {}).get("access_status") != "opened" for source_id in source_ids or []) or not PINNED_COMMIT_PATTERN.fullmatch(str(pinned_commit or "")) or not text(profile.get("architecture_summary")) or not text(profile.get("adoption_boundary")) or not list_of(profile.get("unknowns")) or not _utc_timestamp(profile.get("checked_at")):
            findings.error(f"{label}: profile identity, opened pinned sources, summary, adoption boundary, unknowns, or timestamp is invalid")
        if not any(card.get("pinned_commit") == pinned_commit and source_by_id.get(card.get("source_id"), {}).get("entity_id") == entity_id for card in repositories):
            findings.error(f"{label}: pinned_commit must match the repository quality card for the same entity")

        def validate_located(items: Any, required: set[str], minimum: int, field_name: str) -> None:
            if not isinstance(items, list) or len(items) < minimum:
                findings.error(f"{label}: {field_name} requires at least {minimum} located records")
                return
            for item in items:
                if not isinstance(item, dict) or not required <= set(item) or not all(text(item.get(name)) for name in required - {"source_id", "step"}) or item.get("source_id") not in (source_ids or []):
                    findings.error(f"{label}: {field_name} records require text fields and a profile source_id")
                    break

        validate_located(profile.get("components"), {"name", "responsibility", "source_id", "locator"}, 3, "components")
        validate_located(profile.get("data_flow"), {"step", "operation", "from", "to", "source_id", "locator"}, 4, "data_flow")
        if isinstance(profile.get("data_flow"), list):
            steps = [item.get("step") for item in profile["data_flow"] if isinstance(item, dict)]
            if steps != list(range(1, len(steps) + 1)):
                findings.error(f"{label}: data_flow steps must be consecutive and ordered from 1")
        validate_located(profile.get("dependencies_services"), {"name", "role", "source_id", "locator"}, 1, "dependencies_services")
        validate_located(profile.get("integration_constraints"), {"constraint", "source_id", "locator"}, 2, "integration_constraints")
        validate_located(profile.get("maintenance_evidence"), {"finding", "source_id", "locator"}, 1, "maintenance_evidence")
        issue_pr = profile.get("issue_pr_findings")
        if not isinstance(issue_pr, list):
            findings.error(f"{label}: issue_pr_findings must be a list")
        elif issue_pr:
            validate_located(issue_pr, {"finding", "source_id", "locator"}, 1, "issue_pr_findings")
        elif not any(re.search(r"\b(issue|pull request|pr)\b", str(value), flags=re.I) for value in profile.get("unknowns", [])):
            findings.error(f"{label}: absent issue/PR findings must be explicit in unknowns")
        failures = profile.get("failure_modes")
        if not isinstance(failures, list) or len(failures) < 3:
            findings.error(f"{label}: failure_modes requires at least three project-specific records")
        else:
            for failure in failures:
                basis = failure.get("basis_source_ids") if isinstance(failure, dict) else None
                if not isinstance(failure, dict) or not {"mode", "trigger", "impact", "basis_source_ids", "inference"} <= set(failure) or not all(text(failure.get(name)) for name in ("mode", "trigger", "impact")) or not list_of(basis) or any(source_id not in (source_ids or []) for source_id in basis) or type(failure.get("inference")) is not bool:
                    findings.error(f"{label}: failure_modes require mode/trigger/impact, pinned source basis, and inference boundary")
                    break
    questions = records["research_questions.jsonl"]; question_by_id = _v2_id_map(questions, "question_id", "research_questions.jsonl", findings)
    for index, row in enumerate(questions, 1):
        if not text(row.get("text")) or not text(row.get("origin")) or not list_of(row.get("lanes")) or not list_of(row.get("window_ids")) or row.get("status") not in {"open", "answered", "deferred"} or not _utc_timestamp(row.get("created_at")) or any(cluster not in cluster_by_id for cluster in row.get("cluster_ids", [])) or any(lane not in plan.get("lanes", []) for lane in row.get("lanes", [])) or any(window not in windows for window in row.get("window_ids", [])): findings.error(f"research_questions.jsonl:{index}: question metadata is invalid")
    gaps = records["gaps.jsonl"]; gap_by_id = _v2_id_map(gaps, "gap_id", "gaps.jsonl", findings)
    for index, row in enumerate(gaps, 1):
        if row.get("question_id") not in question_by_id or not list_of(row.get("lanes")) or not list_of(row.get("window_ids")) or not list_of(row.get("perspectives")) or not text(row.get("rationale")) or not _utc_timestamp(row.get("created_at")): findings.error(f"gaps.jsonl:{index}: gap metadata is invalid")
    for index, row in enumerate(queries, 1):
        if any(lane not in plan.get("lanes", []) for lane in row.get("target_lanes", [])) or any(window not in windows for window in row.get("target_window_ids", [])) or any(cluster not in cluster_by_id for cluster in row.get("target_cluster_ids", [])) or any(parent not in query_by_id or parent == row.get("query_id") for parent in row.get("parent_query_ids", [])) or any(gap not in gap_by_id for gap in row.get("gap_ids", [])):
            findings.error(f"queries.jsonl:{index}: target lanes/windows/clusters/parents/gaps must exist")
    for index, row in enumerate(records["trend_metrics.jsonl"], 1):
        label = f"trend_metrics.jsonl:{index}"
        observation_ids = row.get("observation_ids", [])
        if (row.get("entity_id") is None) == (row.get("cluster_id") is None) or row.get("entity_id") not in {None, *entity_by_id} or row.get("cluster_id") not in {None, *cluster_by_id} or not isinstance(observation_ids, list) or any(observation not in observation_by_id for observation in observation_ids) or not text(row.get("method")) or row.get("status") not in V2_TREND_STATUSES or not isinstance(row.get("signal_only"), bool): findings.error(f"{label}: trend scope/metadata is invalid")
        if row.get("metric_type") in {"growth", "velocity", "acceleration"}:
            observations_for_metric = [observation_by_id[observation_id] for observation_id in observation_ids if observation_id in observation_by_id]
            observed_at = [observation.get("observed_at") for observation in observations_for_metric]
            if not row.get("signal_only") or len(observations_for_metric) < 2:
                findings.error(f"{label}: growth/velocity/acceleration requires two observations and signal_only=true")
            if row.get("entity_id") is not None and any(observation.get("entity_id") != row.get("entity_id") for observation in observations_for_metric):
                findings.error(f"{label}: growth/velocity/acceleration observations must belong to the target entity")
            if len(set(observed_at)) != len(observed_at) or observed_at != sorted(observed_at):
                findings.error(f"{label}: growth/velocity/acceleration observations must have distinct chronological observed_at values")
    for index, row in enumerate(records["relations.jsonl"], 1):
        evidence_ids = row.get("evidence_ids", [])
        if row.get("from_entity_id") not in entity_by_id or row.get("to_entity_id") not in entity_by_id or not text(row.get("relation_type")) or row.get("assertion_type") not in V2_RELATION_ASSERTION_TYPES or row.get("confidence") not in CLAIM_CONFIDENCES or not isinstance(evidence_ids, list) or any(evidence_by_id.get(evidence_id) is None for evidence_id in evidence_ids): findings.error(f"relations.jsonl:{index}: relation metadata is invalid")
        if row.get("assertion_type") == "fact" and not evidence_ids:
            findings.error(f"relations.jsonl:{index}: fact relation requires evidence")
        if row.get("assertion_type") == "forecast" and not evidence_ids and not text(row.get("conditions")):
            findings.error(f"relations.jsonl:{index}: forecast relation requires evidence, conditions, or an explicit rule")
    syntheses = records["syntheses.jsonl"]; synthesis_by_id = _v2_id_map(syntheses, "synthesis_id", "syntheses.jsonl", findings)
    for index, row in enumerate(syntheses, 1):
        if row.get("publication_status") not in V2_PUBLICATION_STATUSES or not text(row.get("action")) or not text(row.get("proposition")) or row.get("confidence") not in CLAIM_CONFIDENCES or any(claim not in claim_by_id for claim in row.get("claim_ids", [])) or any(evidence not in evidence_by_id for evidence in row.get("evidence_ids", [])) or any(cluster not in cluster_by_id for cluster in row.get("cluster_ids", [])): findings.error(f"syntheses.jsonl:{index}: synthesis metadata is invalid")
        if row.get("publication_status") == "published":
            required_text = ("weighting_method", "conditions", "limitations", "reversal_criteria", "minority_view", "unknowns")
            opposing_groups = row.get("opposing_group_ids")
            supporting_evidence_ids = row.get("supporting_evidence_ids")
            opposing_evidence_ids = row.get("opposing_evidence_ids")
            if not list_of(row.get("claim_ids")) or not list_of(row.get("evidence_ids")) or not list_of(supporting_evidence_ids) or not isinstance(opposing_evidence_ids, list) or not list_of(row.get("supporting_group_ids")) or not isinstance(opposing_groups, list) or not all(isinstance(group, str) and group for group in opposing_groups) or row.get("assessment") not in V2_SYNTHESIS_ASSESSMENTS or not all(text(row.get(name)) for name in required_text):
                findings.error(f"syntheses.jsonl:{index}: published synthesis requires claims, evidence, group lists, weighting, conditions, limitations, and reversal criteria")
            if set(supporting_evidence_ids or []) & set(opposing_evidence_ids or []):
                findings.error(f"syntheses.jsonl:{index}: synthesis-level supporting and opposing evidence must be disjoint")
            if set(row.get("evidence_ids", [])) != set(supporting_evidence_ids or []) | set(opposing_evidence_ids or []):
                findings.error(f"syntheses.jsonl:{index}: evidence_ids must equal the synthesis-level support/opposition partition")
            synthesis_claim_ids = set(row.get("claim_ids", []))
            if any(evidence_by_id.get(evidence_id, {}).get("claim_id") not in synthesis_claim_ids for evidence_id in row.get("evidence_ids", [])):
                findings.error(f"syntheses.jsonl:{index}: synthesis evidence must belong to its declared atomic claims")
            supporting_evidence = [evidence_by_id[evidence_id] for evidence_id in supporting_evidence_ids or [] if evidence_id in evidence_by_id]
            opposing_evidence = [evidence_by_id[evidence_id] for evidence_id in opposing_evidence_ids or [] if evidence_id in evidence_by_id]
            derived_supporting_groups = {
                source_by_id[evidence_row["source_id"]].get("independence_group")
                for evidence_row in supporting_evidence
                if evidence_row.get("source_id") in source_by_id
                and text(source_by_id[evidence_row["source_id"]].get("independence_group"))
            }
            derived_opposing_groups = {
                source_by_id[evidence_row["source_id"]].get("independence_group")
                for evidence_row in opposing_evidence
                if evidence_row.get("source_id") in source_by_id
                and text(source_by_id[evidence_row["source_id"]].get("independence_group"))
            }
            if set(row.get("supporting_group_ids", [])) != derived_supporting_groups:
                findings.error(f"syntheses.jsonl:{index}: supporting_group_ids must exactly match supporting evidence source independence groups")
            if set(row.get("opposing_group_ids", [])) != derived_opposing_groups:
                findings.error(f"syntheses.jsonl:{index}: opposing_group_ids must exactly match contradicting evidence source independence groups")
            if row.get("assessment") in {"mixed", "disputed"} and (not opposing_evidence_ids or not opposing_groups):
                findings.error(f"syntheses.jsonl:{index}: mixed/disputed synthesis requires explicit opposing evidence and canonical groups")
            proposition = str(row.get("proposition", "")).strip()
            if CLAIM_MARKER_PATTERN.search(proposition) or "<!--" in proposition:
                findings.error(f"syntheses.jsonl:{index}: proposition must not contain claim or process markers")
            if row.get("action") == "cross-source synthesis":
                if len(derived_supporting_groups) < 2:
                    findings.error(f"syntheses.jsonl:{index}: cross-source synthesis requires at least two canonical independence groups")
                for claim_id in row.get("claim_ids", []):
                    statement = str(claim_by_id.get(claim_id, {}).get("statement", "")).strip()
                    if statement and (proposition == statement or statement in proposition):
                        findings.error(f"syntheses.jsonl:{index}: cross-source proposition must be an analytical judgment, not an underlying atomic claim")
                        break
    deliverables = records["deliverables.jsonl"]; deliverable_by_id = _v2_id_map(deliverables, "deliverable_id", "deliverables.jsonl", findings); marker_claims: dict[str, set[str]] = {}; marker_syntheses: dict[str, set[str]] = {}
    import hashlib
    for index, row in enumerate(deliverables, 1):
        label = f"deliverables.jsonl:{index}"; _require_fields(row, V2_DELIVERABLE_FIELDS, label, findings); value = row.get("path"); path = Path(value) if isinstance(value, str) else Path()
        if not isinstance(value, str) or not value or path.is_absolute() or ".." in path.parts: findings.error(f"{label}: path must be safe and relative"); continue
        resolved = root / path
        if not resolved.is_file(): findings.error(f"{label}: path does not exist"); continue
        if row.get("sha256") != hashlib.sha256(resolved.read_bytes()).hexdigest(): findings.error(f"{label}: sha256 does not match file bytes (UTF-8 bytes)")
        if row.get("publication_status") not in V2_PUBLICATION_STATUSES or not isinstance(row.get("required"), bool) or not list_of(row.get("cluster_ids")) and row.get("cluster_ids") != [] or not list_of(row.get("entity_ids")) and row.get("entity_ids") != [] or not list_of(row.get("engineering_profile_ids")) and row.get("engineering_profile_ids") != [] or not list_of(row.get("claim_ids")) and row.get("claim_ids") != [] or not list_of(row.get("synthesis_ids")) and row.get("synthesis_ids") != [] or not _utc_timestamp(row.get("generated_at")): findings.error(f"{label}: manifest metadata is invalid")
        if any(cluster not in cluster_by_id for cluster in row.get("cluster_ids", [])) or any(entity not in entity_by_id for entity in row.get("entity_ids", [])) or any(profile_id not in engineering_profile_by_id for profile_id in row.get("engineering_profile_ids", [])) or any(claim not in claim_by_id for claim in row.get("claim_ids", [])) or any(synthesis not in synthesis_by_id for synthesis in row.get("synthesis_ids", [])): findings.error(f"{label}: manifest references unknown IDs")
        if row.get("kind") == "project-deep-dive":
            profile_ids = row.get("engineering_profile_ids", [])
            if len(profile_ids) != 1 or engineering_profile_by_id.get(profile_ids[0], {}).get("entity_id") not in row.get("entity_ids", []):
                findings.error(f"{label}: project deep dive requires exactly one reciprocal engineering profile for its entity")
        elif row.get("engineering_profile_ids"):
            findings.error(f"{label}: only project deep dives may reference engineering profiles")
        content = resolved.read_text(encoding="utf-8"); marker_claims[row.get("deliverable_id", "")] = set(CLAIM_MARKER_PATTERN.findall(content)); marker_syntheses[row.get("deliverable_id", "")] = set(V2_SYNTHESIS_MARKER_PATTERN.findall(content))
        if row.get("required") and row.get("kind") != "method" and len(re.findall(r"^#\s+", content, flags=re.M)) > 1:
            findings.error(f"{label}: required reader artifact must not concatenate multiple H1 documents")
        for marker in CLAIM_MARKER_PATTERN.finditer(content):
            claim_id = marker.group(1)
            claim_record = claim_by_id.get(claim_id)
            statement = claim_record.get("statement") if claim_record else None
            if isinstance(statement, str) and statement:
                exact_prefix = re.compile(re.escape(statement) + r"\s*$")
                if not exact_prefix.search(content[:marker.start()]):
                    findings.error(f"{label}: claim marker {claim_id} must immediately follow its exact ledger statement")
        if marker_claims[row.get("deliverable_id", "")] != set(row.get("claim_ids", [])) or marker_syntheses[row.get("deliverable_id", "")] != set(row.get("synthesis_ids", [])):
            findings.error(f"{label}: claim/synthesis markers and manifest must be bidirectional")
    for claim_id, claim in claim_by_id.items():
        ids = claim.get("deliverable_ids", [])
        if any(deliverable_id not in deliverable_by_id for deliverable_id in ids): findings.error(f"claim {claim_id}: unknown deliverable_id")
        if claim.get("publication_status") == "published":
            if not ids or any(claim_id not in marker_claims.get(deliverable_id, set()) or claim_id not in deliverable_by_id[deliverable_id].get("claim_ids", []) for deliverable_id in ids): findings.error(f"claim {claim_id}: published claim must be reciprocally marked in every listed deliverable")
        elif any(claim_id in claims for claims in marker_claims.values()):
            findings.error(f"claim {claim_id}: ledger-only claim must not appear in a published reader artifact")
    for synthesis_id, synthesis in synthesis_by_id.items():
        ids = synthesis.get("deliverable_ids", [])
        if any(deliverable_id not in deliverable_by_id for deliverable_id in ids): findings.error(f"synthesis {synthesis_id}: unknown deliverable_id")
        if synthesis.get("publication_status") == "published" and (not ids or any(synthesis_id not in marker_syntheses.get(deliverable_id, set()) or synthesis_id not in deliverable_by_id[deliverable_id].get("synthesis_ids", []) for deliverable_id in ids)): findings.error(f"synthesis {synthesis_id}: published synthesis must be reciprocally marked")
        elif synthesis.get("publication_status") != "published" and any(synthesis_id in ids for ids in marker_syntheses.values()):
            findings.error(f"synthesis {synthesis_id}: ledger-only synthesis must not appear in a published reader artifact")
    for profile_id, profile in engineering_profile_by_id.items():
        linked = [row for row in deliverables if profile_id in row.get("engineering_profile_ids", [])]
        if len(linked) != 1 or linked[0].get("kind") != "project-deep-dive" or profile.get("entity_id") not in linked[0].get("entity_ids", []):
            findings.error(f"engineering profile {profile_id}: requires exactly one reciprocal project deep dive")
    saturation_scopes = {"cluster": cluster_by_id, "lane": {lane: {} for lane in plan.get("lanes", [])}, "window": windows, "perspective": {"mechanism": {}, "implementation": {}, "benchmark": {}, "adoption": {}, "negative": {}}}
    saturation_events = records["saturation_events.jsonl"]
    saturation_event_by_id = _v2_id_map(saturation_events, "cycle_id", "saturation_events.jsonl", findings)
    for index, row in enumerate(saturation_events, 1):
        label = f"saturation_events.jsonl:{index}"
        key = (row.get("scope_type"), row.get("scope_id"))
        counts = (row.get("new_entities"), row.get("new_high_signal_items"), row.get("new_first_order_clusters"), row.get("new_stances"))
        identifier_lists = (row.get("new_entity_ids"), row.get("new_high_signal_ids"), row.get("new_first_order_cluster_ids"), row.get("new_stance_ids"))
        booleans = (row.get("boundary_changed"), row.get("proposition_changed"), row.get("material_change"))
        if key[0] not in saturation_scopes or key[1] not in saturation_scopes.get(key[0], {}) or type(row.get("iteration")) is not int or row.get("iteration", 0) < 1 or not list_of(row.get("query_ids")) or len(set(row.get("query_ids", []))) != len(row.get("query_ids", [])) or any(query_id not in query_by_id for query_id in row.get("query_ids", [])) or any(type(value) is not int or value < 0 for value in counts) or any(not isinstance(values, list) for values in identifier_lists) or any(type(value) is not bool for value in booleans) or not isinstance(row.get("remaining_gap_ids"), list) or any(gap not in gap_by_id for gap in row.get("remaining_gap_ids", [])) or not text(row.get("observed_gain")) or not _utc_timestamp(row.get("checked_at")):
            findings.error(f"{label}: cycle-level saturation evidence is invalid")
        else:
            _validate_timestamp_window(row.get("checked_at"), f"{label}: checked_at", findings, now, run_created_at)
            event_queries = [query_by_id[query_id] for query_id in row["query_ids"]]
            if any(query.get("iteration") != row.get("iteration") for query in event_queries):
                findings.error(f"{label}: every query must belong to the same recorded iteration as the saturation event")
            if any(query.get("status") != "succeeded" for query in event_queries):
                findings.error(f"{label}: a saturation event may reference only successfully completed queries; retry partial/failed/blocked scopes")
            target_field = {"cluster": "target_cluster_ids", "lane": "target_lanes", "window": "target_window_ids"}.get(key[0])
            if target_field and not any(key[1] in query.get(target_field, []) for query in event_queries):
                findings.error(f"{label}: at least one query must explicitly target the event scope")
            if row.get("new_entities") != len(row.get("new_entity_ids", [])) or any(entity_id not in entity_by_id for entity_id in row.get("new_entity_ids", [])):
                findings.error(f"{label}: new_entities must equal explicit canonical new_entity_ids")
            known_high_signal_ids = {*entity_by_id, *source_by_id, *claim_by_id, *synthesis_by_id}
            if row.get("new_high_signal_items") != len(row.get("new_high_signal_ids", [])) or any(item_id not in known_high_signal_ids for item_id in row.get("new_high_signal_ids", [])):
                findings.error(f"{label}: new_high_signal_items must equal explicit merged ledger IDs")
            if row.get("new_first_order_clusters") != len(row.get("new_first_order_cluster_ids", [])) or any(cluster_id not in cluster_by_id for cluster_id in row.get("new_first_order_cluster_ids", [])):
                findings.error(f"{label}: new_first_order_clusters must equal explicit cluster IDs")
            if row.get("new_stances") != len(row.get("new_stance_ids", [])) or any(synthesis_id not in synthesis_by_id for synthesis_id in row.get("new_stance_ids", [])):
                findings.error(f"{label}: new_stances must equal explicit synthesis IDs")
            structural_change = bool(row.get("boundary_changed") or row.get("proposition_changed") or row.get("new_first_order_clusters") or row.get("new_stances"))
            if not row.get("material_change") and structural_change:
                findings.error(f"{label}: material_change=false cannot report a boundary, proposition, first-order-cluster, or stance change")
            if row.get("material_change") and not structural_change and not row.get("new_high_signal_items"):
                findings.error(f"{label}: material_change=true requires a recorded high-signal or structural change")
    saturation = records["saturation.jsonl"]; saturation_by_scope: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(saturation, 1):
        key = (row.get("scope_type"), row.get("scope_id"))
        final_cycle_ids = row.get("final_cycle_ids")
        if key in saturation_by_scope or key[0] not in saturation_scopes or key[1] not in saturation_scopes[key[0]] or not text(row.get("stop_rule")) or not text(row.get("observed_gain")) or row.get("status") not in {"saturated", "incomplete"} or not isinstance(final_cycle_ids, list) or len(set(final_cycle_ids)) != len(final_cycle_ids) or any(cycle_id not in saturation_event_by_id for cycle_id in final_cycle_ids) or not isinstance(row.get("remaining_gap_ids"), list) or any(gap not in gap_by_id for gap in row.get("remaining_gap_ids", [])) or (row.get("status") == "incomplete" and not row.get("remaining_gap_ids")) or not _utc_timestamp(row.get("checked_at")): findings.error(f"saturation.jsonl:{index}: saturation metadata is invalid")
        else:
            saturation_by_scope[key] = row
            final_events = [saturation_event_by_id[cycle_id] for cycle_id in final_cycle_ids]
            if any((event.get("scope_type"), event.get("scope_id")) != key for event in final_events):
                findings.error(f"saturation.jsonl:{index}: final cycles must belong to the same saturation scope")
            if [event.get("iteration") for event in final_events] != sorted(event.get("iteration") for event in final_events):
                findings.error(f"saturation.jsonl:{index}: final_cycle_ids must be in increasing iteration order")
            if row.get("status") == "saturated":
                if len(final_events) < 2:
                    findings.error(f"saturation.jsonl:{index}: saturated scope requires at least two final cycle observations")
                else:
                    final_two = final_events[-2:]
                    iterations = [event.get("iteration") for event in final_two]
                    if iterations[1] != iterations[0] + 1:
                        findings.error(f"saturation.jsonl:{index}: final no-material cycles must be consecutive iterations")
                    if any(event.get("material_change") or event.get("boundary_changed") or event.get("proposition_changed") or event.get("new_first_order_clusters") or event.get("new_stances") for event in final_two):
                        findings.error(f"saturation.jsonl:{index}: saturated scope requires two consecutive no-material cycles")

    # Coverage is a separately auditable gate.  A status label is never proof:
    # every cell must reciprocally bind its real query/screening/entity or
    # bounded-scarcity trail, reader deliverable, and terminal saturation.
    screening_by_id = {row.get("screening_id"): row for row in records["screening.jsonl"]}
    screening_by_discovery = {row.get("discovery_id"): row for row in records["screening.jsonl"]}
    assignment_pairs = {(row.get("entity_id"), row.get("cluster_id")) for row in records["cluster_assignments.jsonl"]}
    saturation_by_id = {row.get("saturation_id"): row for row in saturation}
    for index, proof in enumerate(coverage_proofs, 1):
        label = f"coverage-proofs.jsonl:{index}"
        key = (proof.get("cluster_id"), proof.get("lane"), proof.get("window_id"))
        provenance = proof.get("provenance") if isinstance(proof.get("provenance"), dict) else {}
        query_ids = provenance.get("query_ids", [])
        successful_ids = provenance.get("successful_query_ids", [])
        discovery_ids = provenance.get("discovery_ids", [])
        screening_ids = provenance.get("screening_ids", [])
        excluded_ids = provenance.get("excluded_discovery_ids", [])
        entity_ids = provenance.get("entity_ids", [])
        source_ids = provenance.get("source_ids", [])
        claim_ids = provenance.get("claim_ids", [])
        deliverable_ids = provenance.get("deliverable_ids", [])
        saturation_ids = provenance.get("saturation_ids", [])
        saturation_event_ids = provenance.get("saturation_event_ids", [])
        gap_ids = provenance.get("gap_ids", [])

        reference_sets = (
            (query_ids, query_by_id, "query"), (discovery_ids, discovery_by_id, "discovery"),
            (screening_ids, screening_by_id, "screening"), (entity_ids, entity_by_id, "entity"),
            (source_ids, source_by_id, "source"), (claim_ids, claim_by_id, "claim"),
            (deliverable_ids, deliverable_by_id, "deliverable"), (saturation_ids, saturation_by_id, "saturation"),
            (saturation_event_ids, saturation_event_by_id, "saturation event"), (gap_ids, gap_by_id, "gap"),
        )
        for identifiers, lookup, kind in reference_sets:
            if any(identifier not in lookup for identifier in identifiers):
                findings.error(f"{label}: provenance references an unknown {kind} ID")
        if len(set(query_ids)) != len(query_ids) or len(set(discovery_ids)) != len(discovery_ids) or len(set(screening_ids)) != len(screening_ids):
            findings.error(f"{label}: query, discovery, and screening provenance IDs must be unique")

        computed_successful = sorted(query_id for query_id in query_ids if query_by_id.get(query_id, {}).get("status") == "succeeded")
        if sorted(successful_ids) != computed_successful:
            findings.error(f"{label}: successful_query_ids must exactly equal the succeeded query_ids")
        for query_id in successful_ids:
            query = query_by_id.get(query_id, {})
            if key[0] not in query.get("target_cluster_ids", []) or key[1] not in query.get("target_lanes", []) or key[2] not in query.get("target_window_ids", []):
                findings.error(f"{label}: every successful coverage query must explicitly target this cluster, lane, and window")

        proof_discoveries = [discovery_by_id[discovery_id] for discovery_id in discovery_ids if discovery_id in discovery_by_id]
        if any(row.get("query_id") not in query_ids for row in proof_discoveries):
            findings.error(f"{label}: discovery provenance must come from the proof's query_ids")
        if any(screening_by_id.get(screening_id, {}).get("discovery_id") not in discovery_ids for screening_id in screening_ids):
            findings.error(f"{label}: screening provenance must belong to the proof's discovery_ids")
        if any(discovery_id not in discovery_ids or screening_by_discovery.get(discovery_id, {}).get("decision") not in {"exclude", "defer"} for discovery_id in excluded_ids):
            findings.error(f"{label}: excluded_discovery_ids must be screened exclude/defer occurrences in this proof")

        valid_positive_entities = [
            entity_id for entity_id in entity_ids
            if entity_by_id.get(entity_id, {}).get("stage") in {"mapped", "deep-verified"}
            and (entity_id, key[0]) in assignment_pairs
            and key[2] in entity_by_id.get(entity_id, {}).get("time_window_ids", [])
        ]
        if len(valid_positive_entities) != len(entity_ids) or proof.get("positive_entity_count") != len(entity_ids):
            findings.error(f"{label}: positive entities must be mapped/deep, assigned to the cluster, in-window, and exactly counted")
        if any(source_by_id.get(source_id, {}).get("access_status") != "opened" for source_id in source_ids):
            findings.error(f"{label}: source provenance must reference opened sources")

        published_dives = [
            deliverable_id for deliverable_id in deliverable_ids
            if deliverable_by_id.get(deliverable_id, {}).get("kind") == "cluster-deep-dive"
            and deliverable_by_id.get(deliverable_id, {}).get("publication_status") == "published"
            and key[0] in deliverable_by_id.get(deliverable_id, {}).get("cluster_ids", [])
        ]
        saturated_scopes = {
            (saturation_by_id[saturation_id].get("scope_type"), saturation_by_id[saturation_id].get("scope_id"))
            for saturation_id in saturation_ids if saturation_id in saturation_by_id and saturation_by_id[saturation_id].get("status") == "saturated"
        }
        required_scopes = {("cluster", key[0]), ("lane", key[1]), ("window", key[2])}

        window = windows.get(key[2], {})
        future_window = bool(window and window.get("start") > plan.get("as_of"))
        required_cell = bool(key[0] in cluster_by_id and cluster_by_id[key[0]].get("importance") == "important" and key[1] in cluster_by_id[key[0]].get("required_lanes", []) and not future_window)
        if future_window:
            if proof.get("applicability") != "not-applicable" or proof.get("status") != "not-applicable" or proof.get("coverage_basis") != "not_applicable":
                findings.error(f"{label}: future-metadata cells must remain not-applicable quarantine")
        elif required_cell and proof.get("applicability") != "required":
            findings.error(f"{label}: an important declared lane/window cell must be applicability=required")

        if proof.get("coverage_basis") == "inherited":
            if cluster_by_id.get(key[0], {}).get("importance") == "important" or future_window:
                findings.error(f"{label}: inherited coverage is reserved for non-important aggregate/root cells")
        elif proof.get("status") == "covered":
            if proof.get("missing_gates") or not successful_ids or not published_dives or not required_scopes <= saturated_scopes:
                findings.error(f"{label}: covered requires no missing gates, a successful targeted query, a published cluster dive, and saturated cluster/lane/window scopes")
            if proof.get("coverage_basis") == "positive_evidence":
                if not entity_ids:
                    findings.error(f"{label}: positive_evidence coverage requires at least one assigned in-window entity")
            elif proof.get("coverage_basis") == "bounded_scarcity":
                if entity_ids or proof.get("positive_entity_count") != 0:
                    findings.error(f"{label}: bounded_scarcity must preserve zero positive entities")
                providers = {query_by_id[query_id].get("provider") for query_id in successful_ids if query_id in query_by_id}
                iterations = sorted({query_by_id[query_id].get("iteration") for query_id in successful_ids if query_id in query_by_id})
                proof_events = sorted(
                    (saturation_event_by_id[event_id] for event_id in saturation_event_ids if event_id in saturation_event_by_id),
                    key=lambda event: (event.get("iteration", 0), event.get("cycle_id", "")),
                )
                event_iterations = sorted({event.get("iteration") for event in proof_events})
                query_discovery_ids = {
                    discovery_id for discovery_id, discovery in discovery_by_id.items()
                    if discovery.get("query_id") in successful_ids
                }
                all_screened = query_discovery_ids <= set(discovery_ids) and query_discovery_ids <= set(screening_by_discovery)
                consecutive = len(iterations) >= 2 and iterations[-1] == iterations[-2] + 1 and len(event_iterations) >= 2 and event_iterations[-1] == event_iterations[-2] + 1
                no_material = bool(proof_events) and not any(event.get("material_change") or event.get("boundary_changed") or event.get("proposition_changed") or event.get("new_entities") or event.get("new_high_signal_items") or event.get("new_first_order_clusters") or event.get("new_stances") for event in proof_events[-2:])
                scoped_events = all(any(query_id in event.get("query_ids", []) for query_id in successful_ids if query_by_id.get(query_id, {}).get("iteration") == event.get("iteration")) for event in proof_events[-2:])
                audited_claims = bool(claim_ids) and all(claim_by_id.get(claim_id, {}).get("publication_status") == "published" and semantic_by_claim.get(claim_id, {}).get("verdict") == "pass" for claim_id in claim_ids)
                if len(providers) < 2 or not consecutive or not no_material or not scoped_events or not all_screened or set(excluded_ids) != query_discovery_ids or not audited_claims:
                    findings.error(f"{label}: bounded_scarcity requires multi-provider, two consecutive no-material targeted cycles, fully screened exclusions, and a published audited bounded-absence claim")
            else:
                findings.error(f"{label}: covered status requires positive_evidence or bounded_scarcity basis")
        elif proof.get("status") in {"partial", "gap"}:
            if not proof.get("missing_gates") or proof.get("coverage_basis") != "incomplete":
                findings.error(f"{label}: partial/gap coverage must preserve explicit missing gates and incomplete basis")
            if proof.get("status") == "gap" and not gap_ids:
                findings.error(f"{label}: gap coverage requires a scope-relevant gap ID")
    important = {cluster_id for cluster_id, cluster in cluster_by_id.items() if cluster.get("importance") == "important"}
    if comprehensive and len(important) < 2:
        findings.error("clusters.jsonl: comprehensive profile requires at least two important clusters")
    if not comprehensive:
        for cluster_id in important:
            row = saturation_by_scope.get(("cluster", cluster_id))
            deep_dive = [delivery for delivery in deliverables if delivery.get("kind") == "cluster-deep-dive" and delivery.get("publication_status") == "published" and cluster_id in delivery.get("cluster_ids", [])]
            if row is None or (row.get("status") == "saturated" and not deep_dive) or (row.get("status") == "incomplete" and not row.get("remaining_gap_ids")):
                findings.error(f"important cluster {cluster_id}: requires saturated published deep dive or explicit incomplete gaps")
    if comprehensive:
        def comprehensive_completion(message: str) -> None:
            if strict:
                findings.error(message)
            else:
                findings.warning(message)

        if not syntheses:
            comprehensive_completion("syntheses.jsonl: comprehensive profile requires non-empty syntheses")
        if not records["relations.jsonl"]:
            comprehensive_completion("relations.jsonl: comprehensive profile requires non-empty relations")
        if not saturation:
            comprehensive_completion("saturation.jsonl: comprehensive profile requires non-empty saturation records")
        if not coverage_proofs:
            findings.advisory("coverage-proofs.jsonl: optional detailed cell audit was not supplied")
        required_window_ids = {
            window_id for window_id, window in windows.items()
            if window.get("start") <= plan.get("as_of")
        }
        diagnostic_missing_cells: list[str] = []
        diagnostic_open_cells: list[str] = []
        for cluster_id in important:
            cluster = cluster_by_id[cluster_id]
            saturation_row = saturation_by_scope.get(("cluster", cluster_id))
            if saturation_row is None:
                comprehensive_completion(f"important cluster {cluster_id}: comprehensive profile requires a cluster completion record")
            elif saturation_row.get("status") == "incomplete" and not saturation_row.get("remaining_gap_ids"):
                comprehensive_completion(f"important cluster {cluster_id}: incomplete status requires explicit remaining gaps")
            elif saturation_row.get("status") != "saturated":
                findings.advisory(f"important cluster {cluster_id}: conclusion remains qualified by an incomplete saturation status")
            has_deep_dive = any(
                delivery.get("kind") == "cluster-deep-dive"
                and delivery.get("publication_status") == "published"
                and cluster_id in delivery.get("cluster_ids", [])
                for delivery in deliverables
            )
            if not has_deep_dive:
                comprehensive_completion(f"important cluster {cluster_id}: comprehensive profile requires a published cluster deep dive")
            for lane in cluster.get("required_lanes", []):
                for window_id in required_window_ids:
                    coverage_key = (cluster_id, lane, window_id)
                    if coverage_key not in coverage_keys:
                        diagnostic_missing_cells.append(f"{cluster_id}/{lane}/{window_id}")
                    elif coverage_row_by_key[coverage_key].get("status") != "covered":
                        diagnostic_open_cells.append(f"{cluster_id}/{lane}/{window_id}:{coverage_row_by_key[coverage_key].get('status')}")
        if diagnostic_missing_cells:
            findings.advisory(
                "cluster_coverage.jsonl: diagnostic grid has "
                f"{len(diagnostic_missing_cells)} missing important-scope cells; sample={diagnostic_missing_cells[:5]}"
            )
        if diagnostic_open_cells:
            findings.advisory(
                "cluster_coverage.jsonl: diagnostic grid has "
                f"{len(diagnostic_open_cells)} partial/gap important-scope cells; sample={diagnostic_open_cells[:5]}"
            )
        for lane in plan.get("lanes", []):
            saturation_row = saturation_by_scope.get(("lane", lane))
            if saturation_row is None:
                findings.advisory(f"saturation.jsonl: no optional lane-level completion record for {lane}")
            elif saturation_row.get("status") != "saturated":
                findings.advisory(f"saturation.jsonl: lane {lane} remains qualified as {saturation_row.get('status')}")
        for window_id in windows:
            saturation_row = saturation_by_scope.get(("window", window_id))
            if saturation_row is None:
                findings.advisory(f"saturation.jsonl: no optional window-level completion record for {window_id}")
            elif saturation_row.get("status") != "saturated":
                findings.advisory(f"saturation.jsonl: window {window_id} remains qualified as {saturation_row.get('status')}")
        for perspective in V2_SATURATION_PERSPECTIVES:
            saturation_row = saturation_by_scope.get(("perspective", perspective))
            if saturation_row is None:
                findings.advisory(f"saturation.jsonl: no optional perspective-level completion record for {perspective}")
            elif saturation_row.get("status") != "saturated":
                findings.advisory(f"saturation.jsonl: perspective {perspective} remains qualified as {saturation_row.get('status')}")
    mapped_stages = {"mapped", "deep-verified"}
    actual = {"discovered_entities": len(entities), "mapped_entities": sum(row.get("stage") in mapped_stages for row in entities), "deep_verified_entities": sum(row.get("stage") == "deep-verified" for row in entities), "queries": len(query_by_id), "sources": len(source_by_id), "claims": len(claim_by_id), "evidence": len(evidence_by_id), "clusters": len(cluster_by_id), "deliverables": len(deliverable_by_id)}
    for kind, stages, target in (("paper", V2_ENTITY_STAGES, "papers_discovered"), ("repository", V2_ENTITY_STAGES, "repositories_discovered"), ("paper", mapped_stages, "papers_mapped"), ("repository", mapped_stages, "repositories_mapped"), ("paper", {"deep-verified"}, "deep_papers"), ("repository", {"deep-verified"}, "deep_repositories")):
        actual[target] = sum(row.get("entity_type") == kind and row.get("stage") in stages for row in entities)
    recent = {window_id for window_id, row in windows.items() if str(row.get("kind", "")).startswith("recent-")}
    actual["recent_discovered"] = sum(bool(set(row.get("time_window_ids", [])) & recent) for row in entities); actual["recent_mapped"] = sum(row.get("stage") in mapped_stages and bool(set(row.get("time_window_ids", [])) & recent) for row in entities)
    for key, target in targets.items():
        if target is not None and actual[key] < target: findings.error(f"research_plan.json: declared target for {key} is not met")
    if any(kind not in {row.get("kind") for row in deliverables} for kind in plan.get("required_deliverable_kinds", [])): findings.error("research_plan.json: required deliverable kind is missing")
    return findings


def validate_bundle(root: Path, *, strict: bool = False) -> Findings:
    try:
        version = json.loads((root / "run.json").read_text(encoding="utf-8")).get("schema_version")
    except (OSError, json.JSONDecodeError):
        return _validate_v17_bundle(root, strict=strict)
    if version == V2_SCHEMA_VERSION:
        return _validate_v2_bundle(root, strict=strict)
    return _validate_v17_bundle(root, strict=strict)


def init_bundle(root: Path, topic: str, as_of: str, mode: str, previous: str | None, profile: str, schema_version: str = V2_SCHEMA_VERSION) -> None:
    if not _iso_date(as_of):
        raise BundleError("--as-of must be YYYY-MM-DD")
    if not topic.strip():
        raise BundleError("--topic must not be empty")
    if schema_version == V2_SCHEMA_VERSION:
        filenames = list(V2_BASE_FILES)
        if mode == "update":
            filenames.append("delta.md")
        existing = [str(root / filename) for filename in filenames if (root / filename).exists()]
        if existing:
            raise BundleError("refusing to overwrite existing file(s): " + ", ".join(existing))
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        run = {"schema_version": V2_SCHEMA_VERSION, "topic": topic, "as_of": as_of, "mode": mode, "review_profile": profile, "created_at": created_at, "previous": previous}
        plan = {"schema_version": V2_SCHEMA_VERSION, "topic": topic, "as_of": as_of, "lanes": [], "time_windows": [], "important_cluster_policy": "saturated", "required_deliverable_kinds": [], "targets": {target: None for target in sorted(V2_TARGETS)}}
        schema = {"schema_version": V2_SCHEMA_VERSION, "research_plan_required": sorted(V2_PLAN_FIELDS), "research_plan_targets": sorted(V2_TARGETS), "query_required": sorted(V2_QUERY_FIELDS), "query_stages": sorted(V2_QUERY_STAGES), "query_statuses": sorted(V2_QUERY_STATUSES), "entity_required": sorted(V2_ENTITY_FIELDS), "entity_stages": sorted(V2_ENTITY_STAGES), "discovery_required": sorted(V2_DISCOVERY_FIELDS), "screening_required": sorted(V2_SCREENING_FIELDS), "screening_decisions": ["exclude", "defer", "map", "deep-verify"], "stage_event_required": sorted(V2_STAGE_EVENT_FIELDS), "stage_transition": "discovered -> mapped -> deep-verified", "cluster_required": sorted(V2_CLUSTER_FIELDS), "cluster_assignment_required": sorted(V2_ASSIGNMENT_FIELDS), "cluster_memberships": ["primary", "secondary", "bridge"], "cluster_coverage_required": sorted(V2_CLUSTER_COVERAGE_FIELDS), "cluster_coverage_statuses": sorted(V2_CLUSTER_COVERAGE_STATUSES), "coverage_proof_required": sorted(V2_COVERAGE_PROOF_FIELDS), "coverage_provenance_required": sorted(V2_COVERAGE_PROVENANCE_FIELDS), "coverage_applicability": sorted(V2_COVERAGE_APPLICABILITY), "coverage_bases": sorted(V2_COVERAGE_BASES), "time_window_required": sorted(V2_WINDOW_FIELDS), "source_required": sorted(SOURCE_FIELDS | {"entity_id"}), "source_access_statuses": sorted(ACCESS_STATUSES), "evidence_required": sorted(EVIDENCE_FIELDS), "repository_required": sorted(REPOSITORY_FIELDS), "repository_observation_required": sorted(V2_REPOSITORY_OBSERVATION_FIELDS), "repository_engineering_profile_required": sorted(V2_REPOSITORY_ENGINEERING_PROFILE_FIELDS), "paper_required": sorted(PAPER_FIELDS), "execution_required": sorted(EXECUTION_FIELDS), "semantic_check_required": sorted(SEMANTIC_CHECK_FIELDS), "trend_metric_required": sorted(V2_TREND_FIELDS), "trend_statuses": sorted(V2_TREND_STATUSES), "saturation_event_required": sorted(V2_SATURATION_EVENT_FIELDS), "saturation_required": sorted(V2_SATURATION_FIELDS), "research_question_required": sorted(V2_QUESTION_FIELDS), "gap_required": sorted(V2_GAP_FIELDS), "synthesis_required": sorted(V2_SYNTHESIS_FIELDS), "synthesis_assessments": sorted(V2_SYNTHESIS_ASSESSMENTS), "relation_required": sorted(V2_RELATION_FIELDS), "relation_assertion_types": sorted(V2_RELATION_ASSERTION_TYPES), "deliverable_required": sorted(V2_DELIVERABLE_FIELDS), "deliverable_kinds": sorted(V2_DELIVERABLE_KINDS), "claim_publication_statuses": sorted(V2_PUBLICATION_STATUSES), "synthesis_marker": "<!-- synthesis:S001 claims:C001 clusters:CL001 -->", "sha256": "UTF-8 file bytes", "report_md": "Compatibility index only; deliverables.jsonl is the publication manifest."}
        content = {filename: "" for filename in V2_BASE_FILES if filename.endswith(".jsonl")}
        content.update({"brief.md": f"# Research brief\n\nTopic: {topic}\n\nAs of: {as_of}\n", "queries.md": "# Query log\n", "research_plan.json": json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", "report.md": f"# {topic} — As of {as_of}\n\nLayered deliverables are listed in deliverables.jsonl.\n", "run.json": json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n", "schema.json": json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"})
        if mode == "update":
            content["delta.md"] = f"# Delta since previous bundle\n\n_As of {as_of}_\n"
        for filename in filenames:
            _write_new(root / filename, content[filename])
        return
    if schema_version != SCHEMA_VERSION:
        raise BundleError("--schema-version must be 1.7 or 2.0")
    filenames = list(BASE_FILES)
    if mode == "update":
        filenames.append("delta.md")
    existing = [str(root / filename) for filename in filenames if (root / filename).exists()]
    if existing:
        raise BundleError("refusing to overwrite existing file(s): " + ", ".join(existing))
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run = {
        "schema_version": SCHEMA_VERSION,
        "topic": topic,
        "as_of": as_of,
        "mode": mode,
        "review_profile": profile,
        "created_at": created_at,
        "previous": previous,
    }
    content = {
        "brief.md": f"# Research brief\n\nTopic: {topic}\n\nAs of: {as_of}\n",
        "queries.md": "# Query log\n\nRecord each executed query, source, time, result count, retained IDs, and follow-up reason.\n",
        "requirements.jsonl": "",
        "queries.jsonl": "",
        "sources.jsonl": "",
        "claims.jsonl": "",
        "evidence.jsonl": "",
        "semantic_checks.jsonl": "",
        "candidates.jsonl": "",
        "executions.jsonl": "",
        "repositories.jsonl": "",
        "papers.jsonl": "",
        "coverage.jsonl": "",
        "report.md": f"# {topic} — As of {as_of}\n",
        "run.json": json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "schema.json": json.dumps({
            "schema_version": SCHEMA_VERSION,
            "source_required": sorted(SOURCE_FIELDS),
            "source_optional": ["license"],
            "source_tiers": sorted(SOURCE_TIERS),
            "source_types": sorted(SOURCE_TYPES),
            "source_access_statuses": sorted(ACCESS_STATUSES),
            "claim_required": sorted(CLAIM_FIELDS),
            "claim_types": sorted(CLAIM_TYPES),
            "claim_risks": sorted(CLAIM_RISKS),
            "claim_confidences": sorted(CLAIM_CONFIDENCES),
            "claim_statuses": sorted(CLAIM_STATUSES),
            "evidence_required": sorted(EVIDENCE_FIELDS),
            "evidence_relations": sorted(EVIDENCE_RELATIONS),
            "semantic_check_required": sorted(SEMANTIC_CHECK_FIELDS),
            "semantic_check_verdicts": sorted(SEMANTIC_VERDICTS),
            "semantic_audit": "Structured clause-level audit; not an automated entailment determination.",
            "query_required": sorted(QUERY_FIELDS),
            "query_passes": [1, 2, 3, 4],
            "candidate_required": sorted(CANDIDATE_FIELDS),
            "candidate_decisions": sorted(CANDIDATE_DECISIONS),
            "repository_required": sorted(REPOSITORY_FIELDS),
            "repository_setup_statuses": sorted(SETUP_STATUSES),
            "repository_tests_ci_statuses": sorted(TESTS_CI_STATUSES),
            "repository_affiliation_statuses": sorted(AFFILIATION_STATUSES),
            "execution_required": sorted(EXECUTION_FIELDS),
            "execution_purposes": sorted(EXECUTION_PURPOSES),
            "paper_required": sorted(PAPER_FIELDS),
            "paper_publication_statuses": sorted(PAPER_STATUSES),
            "paper_evidence_roles": sorted(PAPER_EVIDENCE_ROLES),
            "paper_code_link_required": sorted(CODE_LINK_FIELDS),
            "paper_code_link_relations": sorted(CODE_LINK_RELATIONS),
            "coverage_required": sorted(COVERAGE_FIELDS),
            "coverage_lanes": sorted(COVERAGE_LANES),
            "coverage_statuses": sorted(COVERAGE_STATUSES),
            "report_claim_marker": "<!-- claim:C001 -->",
            "report_claim_scope": "Exact claim statement followed by optional whitespace and its claim marker.",
            "report_process_markers": ["<!-- process:method -->", "<!-- process:limitation -->", "<!-- process:source-list -->"],
            "evidence_single_source_of_truth": True,
            "requirement_required": sorted(REQUIREMENT_FIELDS),
            "requirement_priorities": sorted(REQUIREMENT_PRIORITIES),
            "review_profiles": ["full", "rapid"],
            "report_section_markers": [f"<!-- section:{name} -->" for name in SECTION_NAMES],
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    if mode == "update":
        content["delta.md"] = f"# Delta since previous bundle\n\n_As of {as_of}_\n"
    for filename in filenames:
        _write_new(root / filename, content[filename])


def _load_for_diff(root: Path, filename: str) -> list[dict[str, Any]]:
    findings = Findings()
    path = root / filename
    if not path.is_file():
        raise BundleError(f"missing file for diff: {path}")
    records = _read_jsonl(path, filename, findings)
    if findings.errors:
        raise BundleError("; ".join(findings.errors))
    return records


def _bullets(items: Iterable[str]) -> list[str]:
    values = list(items)
    return [f"- {item}" for item in values] if values else ["- None."]


def diff_bundles(old_root: Path, new_root: Path) -> str:
    old_sources = {r.get("source_id"): r for r in _load_for_diff(old_root, "sources.jsonl") if isinstance(r.get("source_id"), str)}
    new_sources = {r.get("source_id"): r for r in _load_for_diff(new_root, "sources.jsonl") if isinstance(r.get("source_id"), str)}
    old_claims = {r.get("claim_id"): r for r in _load_for_diff(old_root, "claims.jsonl") if isinstance(r.get("claim_id"), str)}
    new_claims = {r.get("claim_id"): r for r in _load_for_diff(new_root, "claims.jsonl") if isinstance(r.get("claim_id"), str)}

    new_source_items = [f"`{key}` — {new_sources[key].get('url', '')}" for key in sorted(new_sources.keys() - old_sources.keys())]
    removed_source_items = [f"`{key}` — {old_sources[key].get('url', '')}" for key in sorted(old_sources.keys() - new_sources.keys())]
    changed_source_items = []
    for key in sorted(old_sources.keys() & new_sources.keys()):
        old_url, new_url = str(old_sources[key].get("url", "")), str(new_sources[key].get("url", ""))
        if normalize_url(old_url) != normalize_url(new_url):
            changed_source_items.append(f"`{key}` — {old_url} → {new_url}")

    new_claim_items = [f"`{key}` — {new_claims[key].get('statement', '')}" for key in sorted(new_claims.keys() - old_claims.keys())]
    removed_claim_items = [f"`{key}` — {old_claims[key].get('statement', '')}" for key in sorted(old_claims.keys() - new_claims.keys())]
    changed_claim_items = []
    for key in sorted(old_claims.keys() & new_claims.keys()):
        old_statement = _normalize_statement(str(old_claims[key].get("statement", "")))
        new_statement = _normalize_statement(str(new_claims[key].get("statement", "")))
        old_status, new_status = old_claims[key].get("status"), new_claims[key].get("status")
        if old_statement != new_statement or old_status != new_status:
            changed_claim_items.append(
                f"`{key}` — statement: {old_statement!r} → {new_statement!r}; status: {old_status!r} → {new_status!r}"
            )

    sections = [
        ("New sources", new_source_items), ("Removed sources", removed_source_items),
        ("Changed sources", changed_source_items), ("New claims", new_claim_items),
        ("Removed claims", removed_claim_items), ("Changed claims", changed_claim_items),
    ]
    lines = ["# Research bundle diff", ""]
    for title, items in sections:
        lines.extend((f"## {title}", "", *_bullets(items), ""))
    return "\n".join(lines)


def _normalize_statement(value: str) -> str:
    return " ".join(value.split()).casefold()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init", help="create a new research bundle")
    init.add_argument("--root", required=True, type=Path)
    init.add_argument("--topic", required=True)
    init.add_argument("--as-of", required=True)
    init.add_argument("--mode", choices=("snapshot", "update"), default="snapshot")
    init.add_argument("--previous")
    init.add_argument("--profile", choices=("comprehensive", "full", "rapid"), default="full")
    init.add_argument("--schema-version", choices=(SCHEMA_VERSION, V2_SCHEMA_VERSION), default=V2_SCHEMA_VERSION)
    validate = subparsers.add_parser("validate", help="validate a research bundle")
    validate.add_argument("--root", required=True, type=Path)
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--json", action="store_true", dest="as_json")
    diff = subparsers.add_parser("diff", help="compare bundle manifests")
    diff.add_argument("--old", required=True, type=Path)
    diff.add_argument("--new", required=True, type=Path)
    diff.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "init":
            init_bundle(args.root, args.topic, args.as_of, args.mode, args.previous, args.profile, args.schema_version)
            print(f"created research bundle: {args.root}")
            return 0
        if args.command == "validate":
            findings = validate_bundle(args.root, strict=args.strict)
            failed = bool(findings.errors or (args.strict and findings.warnings))
            if args.as_json:
                print(json.dumps({"valid": not failed, "errors": findings.errors, "warnings": findings.warnings, "advisories": findings.advisories}, ensure_ascii=False, sort_keys=True))
            else:
                for item in findings.errors:
                    print(f"ERROR: {item}")
                for item in findings.warnings:
                    print(f"WARNING: {item}")
                for item in findings.advisories:
                    print(f"ADVISORY: {item}")
                if not findings.errors and not findings.warnings:
                    print("OK: bundle is valid")
            return 1 if failed else 0
        if args.command == "diff":
            markdown = diff_bundles(args.old, args.new)
            if args.output:
                _write_new(args.output, markdown)
            else:
                print(markdown, end="")
            return 0
    except BundleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
