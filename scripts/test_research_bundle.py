from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import research_bundle


NOW_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def source(source_id: str = "S001", *, supports: list[str] | None = None, source_type: str = "paper", **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "source_id": source_id,
        "title": "Evidence source",
        "url": f"https://example.test/{source_id}",
        "source_type": source_type,
        "tier": "T1",
        "published_at": "2026-01-02",
        "fetched_at": NOW_UTC,
        "organization": "Example",
        "independence_group": "example",
        "version": "0123456789abcdef" if source_type == "repository" else "v1.2.3",
        "queries": ["Q001"],
        "limitations": "",
        "access_status": "opened",
        "access_note": "Opened the source body and reviewed its cited section.",
    }
    record.update(extra)
    return record


def claim(claim_id: str = "C001", *, evidence: list[str] | None = None, **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "claim_id": claim_id,
        "statement": "The implementation has a documented result.",
        "claim_type": "fact",
        "risk": "normal",
        "scope": "test",
        "as_of": "2026-08-10",
        "confidence": "high",
        "status": "supported",
    }
    record.update(extra)
    return record


def evidence(
    evidence_id: str = "E001", *, claim_id: str = "C001", source_id: str = "S001",
    relation: str = "supports", **extra: object,
) -> dict[str, object]:
    record: dict[str, object] = {
        "evidence_id": evidence_id,
        "claim_id": claim_id,
        "source_id": source_id,
        "locator": "Section 2",
        "support_summary": "The source directly supports the claim.",
        "relation": relation,
        "checked_at": NOW_UTC,
    }
    record.update(extra)
    return record


def query(query_id: str = "Q001", *, retained_source_ids: list[str] | None = None, **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "query_id": query_id,
        "pass": 1,
        "query": "test query",
        "channel": "test",
        "executed_at": NOW_UTC,
        "result_count": 1,
        "result_count_note": "",
        "retained_source_ids": retained_source_ids if retained_source_ids is not None else ["S001"],
        "followup_reason": "test",
    }
    record.update(extra)
    return record


def repository_card(source_id: str = "S001", **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "source_id": source_id,
        "owner_repo": "example/repository",
        "pinned_commit": "0123456789abcdef",
        "latest_release": "v1.2.3",
        "pushed_at": "2026-08-09",
        "license": "MIT",
        "setup": "documented",
        "tests_ci": "present",
        "setup_execution_id": None,
        "tests_execution_id": None,
        "affiliation": "official-owner",
        "adoption_evidence": [],
        "checked_at": NOW_UTC,
    }
    record.update(extra)
    return record


def paper_card(source_id: str = "S001", **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "source_id": source_id,
        "identifier": "arXiv:2608.00001",
        "publication_status": "preprint",
        "venue": None,
        "revision": "v1",
        "code_links": [],
        "data_source_ids": [],
        "status_locator": "Abstract status line",
        "evidence_role": "original-study",
        "code_search_note": "Repository search was performed against the paper metadata.",
        "checked_at": NOW_UTC,
    }
    record.update(extra)
    return record


def coverage(*, claim_ids: list[str] | None = None, source_ids: list[str] | None = None, **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "question_id": "RQ001",
        "question": "What does the evidence show?",
        "required_lanes": ["paper"],
        "status": "covered",
        "claim_ids": claim_ids if claim_ids is not None else ["C001"],
        "source_ids": source_ids if source_ids is not None else ["S001"],
        "gap": "",
        "updated_at": NOW_UTC,
    }
    record.update(extra)
    return record


def requirement(requirement_id: str = "RQ001", *, text: str = "What does the evidence show?", frozen_at: str = NOW_UTC, **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "requirement_id": requirement_id,
        "text": text,
        "priority": "must",
        "required_lanes": ["paper"],
        "acceptance": "Trace each covered claim and source through an evidence join.",
        "frozen_at": frozen_at,
    }
    record.update(extra)
    return record


def candidate(candidate_id: str = "K001", *, source_id: str | None = "S001", decision: str = "retained", **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "candidate_id": candidate_id,
        "query_id": "Q001",
        "title": "Evidence source",
        "url": f"https://example.test/{source_id}" if source_id else "https://example.test/candidate",
        "decision": decision,
        "source_id": source_id,
        "reason": "retained after review" if decision == "retained" else "not retained",
        "checked_at": NOW_UTC,
    }
    record.update(extra)
    return record


def semantic_check(claim_id: str = "C001", *, evidence_ids: list[str] | None = None, **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "claim_id": claim_id,
        "verdict": "pass",
        "evidence_ids": evidence_ids if evidence_ids is not None else ["E001"],
        "uncovered_terms": [],
        "rationale": "The cited evidence directly covers the bounded claim statement.",
        "checked_at": NOW_UTC,
    }
    record.update(extra)
    return record


def execution(execution_id: str = "X001", *, source_id: str = "S001", purpose: str = "setup", **extra: object) -> dict[str, object]:
    record: dict[str, object] = {
        "execution_id": execution_id,
        "source_id": source_id,
        "purpose": purpose,
        "command": "python -m pytest",
        "environment": "Python 3.11 on a test host",
        "started_at": NOW_UTC,
        "ended_at": NOW_UTC,
        "exit_code": 0,
        "output_summary": "Command completed successfully.",
    }
    record.update(extra)
    return record


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def write_valid_paper_bundle(
    root: Path, *, paper_records: list[dict[str, object]] | None = None,
    coverage_records: list[dict[str, object]] | None = None,
    extra_sources: list[dict[str, object]] | None = None,
) -> None:
    run = json.loads((root / "run.json").read_text(encoding="utf-8"))
    run["review_profile"] = "rapid"
    timestamp = run["created_at"]
    (root / "run.json").write_text(json.dumps(run), encoding="utf-8")
    sources = [source(fetched_at=timestamp), *(extra_sources or [])]
    claims = [claim()]
    evidence_records = [evidence(checked_at=timestamp)]
    write_jsonl(root / "sources.jsonl", sources)
    write_jsonl(root / "queries.jsonl", [query(executed_at=timestamp)])
    write_jsonl(root / "requirements.jsonl", [requirement(frozen_at=timestamp)])
    write_jsonl(root / "claims.jsonl", claims)
    write_jsonl(root / "evidence.jsonl", evidence_records)
    write_jsonl(root / "semantic_checks.jsonl", [semantic_check(checked_at=timestamp)])
    write_jsonl(root / "candidates.jsonl", [candidate(checked_at=timestamp)])
    write_jsonl(root / "papers.jsonl", [paper_card()] if paper_records is None else paper_records)
    write_jsonl(root / "coverage.jsonl", [coverage()] if coverage_records is None else coverage_records)
    (root / "report.md").write_text(
        "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->\n\n"
        "This process note documents the reproducible method, source handling, and evidence review workflow "
        "without adding a substantive research conclusion to the report.<!-- process:method -->",
        encoding="utf-8",
    )


def write_full_bundle(root: Path) -> None:
    run = json.loads((root / "run.json").read_text(encoding="utf-8"))
    timestamp = run["created_at"]
    names = ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima")
    claims = [claim(f"C{index:03d}", statement=f"The {name} record has documented evidence.") for index, name in enumerate(names, 1)]
    sources: list[dict[str, object]] = []
    candidates: list[dict[str, object]] = []
    queries: list[dict[str, object]] = []
    for query_index in range(1, 9):
        retained = [f"S{source_index:03d}" for source_index in range((query_index - 1) * 2 + 1, min(query_index * 2, 12) + 1)]
        queries.append(query(f"Q{query_index:03d}", retained_source_ids=retained, executed_at=timestamp, **{"pass": (query_index - 1) // 2 + 1}))
        for source_id in retained:
            sources.append(source(source_id, queries=[f"Q{query_index:03d}"], fetched_at=timestamp))
            candidates.append(candidate(f"K{source_id[1:]}", source_id=source_id, query_id=f"Q{query_index:03d}", checked_at=timestamp))
    candidates.extend((
        candidate("K013", source_id=None, decision="excluded", query_id="Q001", checked_at=timestamp),
        candidate("K014", source_id=None, decision="excluded", query_id="Q003", checked_at=timestamp),
        candidate("K015", source_id=None, decision="deferred", query_id="Q005", checked_at=timestamp),
        candidate("K017", source_id=None, decision="excluded", query_id="Q007", checked_at=timestamp),
        candidate("K016", source_id=None, decision="deferred", query_id="Q008", checked_at=timestamp),
    ))
    evidence_records: list[dict[str, object]] = []
    requirements: list[dict[str, object]] = []
    coverage_records: list[dict[str, object]] = []
    for requirement_index in range(1, 7):
        claim_ids = [f"C{2 * requirement_index - 1:03d}", f"C{2 * requirement_index:03d}"]
        source_ids = [f"S{2 * requirement_index - 1:03d}", f"S{2 * requirement_index:03d}"]
        text = f"Requirement {requirement_index} evidence closure"
        requirements.append(requirement(f"R{requirement_index:03d}", text=text, frozen_at=timestamp))
        coverage_records.append(coverage(question_id=f"R{requirement_index:03d}", question=text, claim_ids=claim_ids, source_ids=source_ids, updated_at=timestamp))
        for claim_id in claim_ids:
            for source_id in source_ids:
                evidence_records.append(evidence(f"E{len(evidence_records) + 1:03d}", claim_id=claim_id, source_id=source_id, checked_at=timestamp))
    write_jsonl(root / "requirements.jsonl", requirements)
    write_jsonl(root / "queries.jsonl", queries)
    write_jsonl(root / "sources.jsonl", sources)
    write_jsonl(root / "claims.jsonl", claims)
    write_jsonl(root / "evidence.jsonl", evidence_records)
    evidence_ids_by_claim = {claim_record["claim_id"]: [] for claim_record in claims}
    for record in evidence_records:
        evidence_ids_by_claim[record["claim_id"]].append(record["evidence_id"])
    write_jsonl(root / "semantic_checks.jsonl", [semantic_check(claim_id, evidence_ids=evidence_ids_by_claim[claim_id], checked_at=timestamp) for claim_id in evidence_ids_by_claim])
    write_jsonl(root / "candidates.jsonl", candidates)
    write_jsonl(root / "papers.jsonl", [paper_card(source_id, checked_at=timestamp) for source_id in [f"S{index:03d}" for index in range(1, 13)]])
    write_jsonl(root / "coverage.jsonl", coverage_records)
    claim_by_id = {record["claim_id"]: record for record in claims}
    core_claims = iter([f"C{index:03d}" for index in range(1, 11)])
    report_lines = ["# Test — As of 2026-08-10", ""]
    for section in research_bundle.SECTION_NAMES:
        report_lines.extend((f"<!-- section:{section} -->", ""))
        if section == "scope-method":
            report_lines.extend(("The method protocol is recorded for deterministic replay." + "x" * 6100 + "<!-- process:method -->", ""))
        elif section == "limitations-sources":
            report_lines.extend(("The source limitations are recorded separately.<!-- process:limitation -->", ""))
        else:
            claim_id = next(core_claims)
            report_lines.extend((claim_by_id[claim_id]["statement"] + f"<!-- claim:{claim_id} -->", ""))
            if section == "landscape":
                report_lines.extend(("| Claim | Status |", "| --- | --- |", f"| {claim_by_id['C011']['statement']}<!-- claim:C011 --> | supported |", ""))
    for claim_id in ("C012",):
        report_lines.extend((claim_by_id[claim_id]["statement"] + f"<!-- claim:{claim_id} -->", ""))
    (root / "report.md").write_text("\n".join(report_lines), encoding="utf-8")


def write_v2_bundle(root: Path) -> None:
    run = json.loads((root / "run.json").read_text(encoding="utf-8"))
    timestamp = run["created_at"]
    plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8"))
    plan.update({"lanes": ["paper"], "time_windows": ["W001"], "important_cluster_policy": "saturated", "required_deliverable_kinds": ["report"], "targets": {"deep_verified_entities": 1, "queries": 1, "sources": 1, "claims": 1, "evidence": 1, "clusters": 1, "deliverables": 1}})
    (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    write_jsonl(root / "queries.jsonl", [{"query_id": "Q001", "stage": "verify", "iteration": 1, "provider": "test-provider", "query_text": "primary study", "request_url": "https://example.test/search?q=primary", "status": "succeeded", "raw_snapshot_paths": ["raw/test.raw"], "target_lanes": ["paper"], "target_window_ids": ["W001"], "target_cluster_ids": ["CL001"], "parent_query_ids": [], "gap_ids": [], "information_gain": "Verify the primary study.", "executed_at": timestamp, "result_count": 1, "result_count_note": ""}])
    write_jsonl(root / "discovery_results.jsonl", [{"discovery_id": "DR001", "query_id": "Q001", "provider": "test-provider", "provider_result_id": "r1", "title": "Primary study", "url": "https://example.test/study", "identifier": "test:study", "observed_at": timestamp, "rank": 1, "page_cursor": None, "metadata": {}}])
    write_jsonl(root / "entities.jsonl", [{"entity_id": "EN001", "canonical_name": "Example entity", "url": "https://example.test/entity", "identifier": "test:entity", "aliases": [], "discovery_ids": ["DR001"], "stage": "deep-verified", "published_at": "2026-01-02", "created_at": timestamp, "updated_at": timestamp, "date_confidence": "exact", "time_window_ids": ["W001"], "source_ids": ["S001"], "entity_type": "paper"}])
    write_jsonl(root / "clusters.jsonl", [{"cluster_id": "CL001", "label": "Example cluster", "importance": "normal", "parent_ids": [], "definition": "Example field grouping.", "inclusion": "Relevant examples.", "exclusion": "Irrelevant examples.", "problem": "Illustrate validation.", "architecture_patterns": [], "implementation_patterns": [], "tradeoffs": [], "required_lanes": ["paper"], "confidence": "high"}])
    write_jsonl(root / "cluster_assignments.jsonl", [{"assignment_id": "A001", "entity_id": "EN001", "cluster_id": "CL001", "membership": "primary", "confidence": "high", "rationale": "Direct fit.", "method": "manual review", "time": timestamp}])
    write_jsonl(root / "time_windows.jsonl", [{"window_id": "W001", "label": "Current window", "start": "2026-01-01", "end": "2026-08-10", "kind": "recent-12m"}])
    write_jsonl(root / "cluster_coverage.jsonl", [{"cluster_id": "CL001", "lane": "paper", "window_id": "W001", "status": "covered"}])
    write_jsonl(root / "screening.jsonl", [{"screening_id": "SC001", "discovery_id": "DR001", "decision": "deep-verify", "reason": "Primary evidence.", "checked_at": timestamp}])
    write_jsonl(root / "stage_events.jsonl", [{"event_id": "SE001", "entity_id": "EN001", "from_stage": "discovered", "to_stage": "mapped", "occurred_at": timestamp, "rationale": "Classified."}, {"event_id": "SE002", "entity_id": "EN001", "from_stage": "mapped", "to_stage": "deep-verified", "occurred_at": timestamp, "rationale": "Checked source."}])
    write_jsonl(root / "sources.jsonl", [source("S001", source_type="paper", entity_id="EN001", fetched_at=timestamp)])
    write_jsonl(root / "claims.jsonl", [claim(publication_status="published", deliverable_ids=["D001"])])
    write_jsonl(root / "evidence.jsonl", [evidence(checked_at=timestamp)])
    write_jsonl(root / "semantic_checks.jsonl", [semantic_check(checked_at=timestamp)])
    write_jsonl(root / "papers.jsonl", [paper_card("S001", checked_at=timestamp)])
    write_jsonl(root / "research_questions.jsonl", [{"question_id": "RQ001", "text": "What does the study show?", "origin": "plan", "cluster_ids": ["CL001"], "lanes": ["paper"], "window_ids": ["W001"], "status": "answered", "created_at": timestamp}])
    write_jsonl(root / "gaps.jsonl", [])
    write_jsonl(root / "syntheses.jsonl", [])
    write_jsonl(root / "relations.jsonl", [])
    write_jsonl(root / "repository_observations.jsonl", [])
    write_jsonl(root / "trend_metrics.jsonl", [])
    write_jsonl(root / "saturation.jsonl", [])
    (root / "report.md").write_text("# Layered report\n\n" + claim()["statement"] + "<!-- claim:C001 -->\n", encoding="utf-8")
    import hashlib
    digest = hashlib.sha256((root / "report.md").read_bytes()).hexdigest()
    write_jsonl(root / "deliverables.jsonl", [{"deliverable_id": "D001", "kind": "report", "path": "report.md", "sha256": digest, "cluster_ids": ["CL001"], "entity_ids": ["EN001"], "engineering_profile_ids": [], "publication_status": "published", "required": True, "claim_ids": ["C001"], "synthesis_ids": [], "generated_at": timestamp}])


def write_comprehensive_v2_bundle(root: Path) -> None:
    """Build the smallest complete comprehensive fixture from declared targets."""
    write_v2_bundle(root)
    run = json.loads((root / "run.json").read_text(encoding="utf-8"))
    run["review_profile"] = "comprehensive"
    (root / "run.json").write_text(json.dumps(run), encoding="utf-8")
    timestamp = run["created_at"]
    earlier = (datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lanes = ["paper", "github", "benchmark", "negative"]
    windows = [
        {"window_id": "W001", "label": "Foundational", "start": "2018-01-01", "end": "2023-12-31", "kind": "foundational"},
        {"window_id": "W002", "label": "Recent year", "start": "2025-08-10", "end": "2026-08-10", "kind": "recent-12m"},
        {"window_id": "W003", "label": "Recent quarter", "start": "2026-05-10", "end": "2026-08-10", "kind": "recent-90d"},
    ]
    kinds = ["readme", "executive", "field-tree", "landscape", "timeline", "consensus", "repository-radar", "benchmark-map", "method", "source-index", "cluster-deep-dive", "project-deep-dive"]
    plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8"))
    plan.update({"lanes": lanes, "time_windows": [row["window_id"] for row in windows], "required_deliverable_kinds": kinds, "targets": {name: 1 for name in research_bundle.V2_TARGETS}})
    plan["targets"].update({"clusters": 2, "deliverables": 13})
    (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    query_stages = [("Q001", "discover", "paper"), ("Q002", "discover", "github"), ("Q003", "gap-fill", "benchmark"), ("Q004", "deep-focus", "paper"), ("Q005", "verify", "github"), ("Q006", "adversarial", "negative")]
    fixture_queries = [
        {"query_id": query_id, "stage": stage, "iteration": 1, "provider": "test-provider", "query_text": f"{stage} {lane}", "request_url": "https://example.test/search", "status": "succeeded", "raw_snapshot_paths": [f"raw/{query_id}.json"], "target_lanes": [lane], "target_window_ids": ["W002"], "target_cluster_ids": ["CL001"], "parent_query_ids": [], "gap_ids": [], "information_gain": "Test a declared coverage gap.", "executed_at": timestamp, "result_count": 1, "result_count_note": ""}
        for query_id, stage, lane in query_stages
    ]
    fixture_queries.extend([
        {"query_id": "QSAT001", "stage": "verify", "iteration": 1, "provider": "test-provider", "query_text": "first saturation audit", "request_url": "https://example.test/search", "status": "succeeded", "raw_snapshot_paths": ["raw/QSAT001.json"], "target_lanes": lanes, "target_window_ids": [row["window_id"] for row in windows], "target_cluster_ids": ["CL001", "CL002"], "parent_query_ids": [], "gap_ids": [], "information_gain": "No material field change.", "executed_at": timestamp, "result_count": 0, "result_count_note": "No retained signal."},
        {"query_id": "QSAT002", "stage": "verify", "iteration": 2, "provider": "test-provider", "query_text": "second saturation audit", "request_url": "https://example.test/search", "status": "succeeded", "raw_snapshot_paths": ["raw/QSAT002.json"], "target_lanes": lanes, "target_window_ids": [row["window_id"] for row in windows], "target_cluster_ids": ["CL001", "CL002"], "parent_query_ids": ["QSAT001"], "gap_ids": [], "information_gain": "Second consecutive no-material field change.", "executed_at": timestamp, "result_count": 0, "result_count_note": "No retained signal."},
    ])
    write_jsonl(root / "queries.jsonl", fixture_queries)
    write_jsonl(root / "discovery_results.jsonl", [
        {"discovery_id": "DR001", "query_id": "Q001", "provider": "test-provider", "provider_result_id": "paper", "title": "Example paper", "url": "https://example.test/paper", "identifier": "test:paper", "observed_at": timestamp, "rank": 1, "page_cursor": None, "metadata": {}},
        {"discovery_id": "DR002", "query_id": "Q002", "provider": "test-provider", "provider_result_id": "repo", "title": "Example repository", "url": "https://example.test/repo", "identifier": "test:repo", "observed_at": timestamp, "rank": 1, "page_cursor": None, "metadata": {}},
    ])
    entity_windows = ["W001", "W002", "W003"]
    write_jsonl(root / "entities.jsonl", [
        {"entity_id": "EN001", "canonical_name": "Example paper", "url": "https://example.test/paper", "identifier": "test:paper", "aliases": [], "discovery_ids": ["DR001"], "stage": "deep-verified", "published_at": None, "created_at": timestamp, "updated_at": timestamp, "date_confidence": "unknown", "time_window_ids": entity_windows, "source_ids": ["S001"], "entity_type": "paper"},
        {"entity_id": "EN002", "canonical_name": "Example repository", "url": "https://example.test/repo", "identifier": "test:repo", "aliases": [], "discovery_ids": ["DR002"], "stage": "deep-verified", "published_at": None, "created_at": timestamp, "updated_at": timestamp, "date_confidence": "unknown", "time_window_ids": entity_windows, "source_ids": ["S002"], "entity_type": "repository"},
    ])
    clusters = [
        {"cluster_id": cluster_id, "label": f"Cluster {index}", "importance": "important", "parent_ids": [], "definition": "A coherent research block.", "inclusion": "Direct memory systems.", "exclusion": "Unrelated systems.", "problem": "Manage agent memory.", "architecture_patterns": ["retrieval"], "implementation_patterns": ["index"], "tradeoffs": ["latency"], "required_lanes": lanes, "confidence": "high"}
        for index, cluster_id in enumerate(("CL001", "CL002"), 1)
    ]
    write_jsonl(root / "clusters.jsonl", clusters)
    write_jsonl(root / "cluster_assignments.jsonl", [
        {"assignment_id": "A001", "entity_id": "EN001", "cluster_id": "CL001", "membership": "primary", "confidence": "high", "rationale": "Direct fit.", "method": "manual review", "time": timestamp},
        {"assignment_id": "A002", "entity_id": "EN002", "cluster_id": "CL002", "membership": "primary", "confidence": "high", "rationale": "Direct fit.", "method": "manual review", "time": timestamp},
    ])
    write_jsonl(root / "time_windows.jsonl", windows)
    write_jsonl(root / "cluster_coverage.jsonl", [
        {"cluster_id": cluster_id, "lane": lane, "window_id": window["window_id"], "status": "covered"}
        for cluster_id in ("CL001", "CL002") for lane in lanes for window in windows
    ])
    write_jsonl(root / "screening.jsonl", [
        {"screening_id": "SC001", "discovery_id": "DR001", "decision": "deep-verify", "reason": "Primary evidence.", "checked_at": timestamp},
        {"screening_id": "SC002", "discovery_id": "DR002", "decision": "deep-verify", "reason": "Engineering evidence.", "checked_at": timestamp},
    ])
    write_jsonl(root / "stage_events.jsonl", [
        {"event_id": "SE001", "entity_id": "EN001", "from_stage": "discovered", "to_stage": "mapped", "occurred_at": timestamp, "rationale": "Classified."},
        {"event_id": "SE002", "entity_id": "EN001", "from_stage": "mapped", "to_stage": "deep-verified", "occurred_at": timestamp, "rationale": "Checked."},
        {"event_id": "SE003", "entity_id": "EN002", "from_stage": "discovered", "to_stage": "mapped", "occurred_at": timestamp, "rationale": "Classified."},
        {"event_id": "SE004", "entity_id": "EN002", "from_stage": "mapped", "to_stage": "deep-verified", "occurred_at": timestamp, "rationale": "Checked."},
    ])
    write_jsonl(root / "sources.jsonl", [source("S001", source_type="paper", entity_id="EN001", queries=["Q001"], fetched_at=timestamp), source("S002", source_type="repository", entity_id="EN002", queries=["Q002"], fetched_at=timestamp)])
    write_jsonl(root / "claims.jsonl", [claim(publication_status="published", deliverable_ids=["D001"])])
    write_jsonl(root / "evidence.jsonl", [evidence(checked_at=timestamp)])
    write_jsonl(root / "semantic_checks.jsonl", [semantic_check(checked_at=timestamp)])
    write_jsonl(root / "papers.jsonl", [paper_card("S001", checked_at=timestamp)])
    write_jsonl(root / "repositories.jsonl", [repository_card("S002", checked_at=timestamp)])
    write_jsonl(root / "repository_engineering_profiles.jsonl", [{
        "profile_id": "EP001", "entity_id": "EN002", "source_ids": ["S002"], "pinned_commit": "0123456789abcdef",
        "architecture_summary": "A fixed-commit test profile separates ingestion, durable state, retrieval, and response assembly.",
        "components": [
            {"name": "ingest", "responsibility": "Accept records.", "source_id": "S002", "locator": "README ingest"},
            {"name": "store", "responsibility": "Persist records.", "source_id": "S002", "locator": "README store"},
            {"name": "retrieve", "responsibility": "Select records.", "source_id": "S002", "locator": "README retrieve"},
        ],
        "data_flow": [
            {"step": 1, "operation": "write", "from": "client", "to": "ingest", "source_id": "S002", "locator": "README write"},
            {"step": 2, "operation": "persist", "from": "ingest", "to": "store", "source_id": "S002", "locator": "README store"},
            {"step": 3, "operation": "search", "from": "query", "to": "retrieve", "source_id": "S002", "locator": "README search"},
            {"step": 4, "operation": "compile", "from": "retrieve", "to": "response", "source_id": "S002", "locator": "README response"},
        ],
        "dependencies_services": [{"name": "example-db", "role": "Durable storage.", "source_id": "S002", "locator": "manifest dependency"}],
        "integration_constraints": [
            {"constraint": "Requires an explicit namespace.", "source_id": "S002", "locator": "README namespace"},
            {"constraint": "Deletion must invalidate the index.", "source_id": "S002", "locator": "README deletion"},
        ],
        "maintenance_evidence": [{"finding": "The fixed snapshot records a current push date.", "source_id": "S002", "locator": "repository metadata"}],
        "issue_pr_findings": [],
        "failure_modes": [
            {"mode": "stale index", "trigger": "Failed projection update.", "impact": "Old records are retrieved.", "basis_source_ids": ["S002"], "inference": True},
            {"mode": "scope leak", "trigger": "Missing namespace.", "impact": "Records cross principals.", "basis_source_ids": ["S002"], "inference": True},
            {"mode": "incomplete deletion", "trigger": "Index remains after record deletion.", "impact": "Deleted content stays searchable.", "basis_source_ids": ["S002"], "inference": True},
        ],
        "adoption_boundary": "No independent production deployment is established by this fixture.",
        "unknowns": ["Issue and PR latency were not measured.", "Runtime behavior was not executed."], "checked_at": timestamp,
    }])
    observation = {"entity_id": "EN002", "node_id": "N001", "owner_repo": "example/repository", "stars": 10, "forks": 1, "open_issues": 0, "created": "2026-02-02", "pushed": "2026-08-09", "latest_release": "v1.0", "default_commit": "0123456789abcdef", "archived": False, "fork": False, "license": "MIT", "commits_in_window": 1, "contributors_in_window": 1, "window_id": "W002", "api_url": "https://api.example.test/repo", "note": "Snapshot.", "observed_at": earlier}
    later_observation = dict(observation, observation_id="O002", stars=11, observed_at=timestamp)
    write_jsonl(root / "repository_observations.jsonl", [dict(observation, observation_id="O001"), later_observation])
    write_jsonl(root / "trend_metrics.jsonl", [{"metric_id": "TM001", "entity_id": "EN002", "cluster_id": None, "observation_ids": ["O001", "O002"], "metric_type": "growth", "start": 10, "end": 11, "delta": 1, "rate": 1, "acceleration": None, "method": "Compare two repository snapshots.", "completeness": "complete", "status": "signal", "followup": "Verify next period.", "signal_only": True, "checked_at": timestamp}])
    write_jsonl(root / "research_questions.jsonl", [{"question_id": "RQ001", "text": "What changed?", "origin": "plan", "cluster_ids": ["CL001"], "lanes": lanes, "window_ids": ["W002"], "status": "answered", "created_at": timestamp}])
    write_jsonl(root / "gaps.jsonl", [])
    write_jsonl(root / "relations.jsonl", [{"relation_id": "R001", "from_entity_id": "EN001", "to_entity_id": "EN002", "relation_type": "implements", "assertion_type": "fact", "evidence_ids": ["E001"], "conditions": "Within this test fixture.", "confidence": "medium"}])
    write_jsonl(root / "syntheses.jsonl", [{"synthesis_id": "SY001", "action": "compare", "proposition": "The two evidence lanes complement each other.", "claim_ids": ["C001"], "evidence_ids": ["E001"], "supporting_evidence_ids": ["E001"], "opposing_evidence_ids": [], "supporting_group_ids": ["example"], "opposing_group_ids": [], "assessment": "dominant", "minority_view": "No separately weighted minority position was retained in this fixture.", "unknowns": "The fixture does not test external validity.", "weighting_method": "Prioritize direct opened primary evidence.", "conditions": "Within the stated test scope.", "confidence": "medium", "limitations": "Small test corpus.", "reversal_criteria": "Direct contradictory evidence.", "cluster_ids": ["CL001", "CL002"], "publication_status": "published", "deliverable_ids": ["D001"]}])
    saturation_events = []
    saturation = []
    for scope_type, scope_ids in (("cluster", ["CL001", "CL002"]), ("lane", lanes), ("window", [row["window_id"] for row in windows]), ("perspective", sorted(research_bundle.V2_SATURATION_PERSPECTIVES))):
        for scope_id in scope_ids:
            cycle_ids = []
            for iteration in (1, 2):
                cycle_id = f"CYC{len(saturation_events) + 1:03d}"
                cycle_ids.append(cycle_id)
                saturation_events.append({"cycle_id": cycle_id, "scope_type": scope_type, "scope_id": scope_id, "iteration": iteration, "query_ids": [f"QSAT00{iteration}"], "new_entities": 0, "new_entity_ids": [], "new_high_signal_items": 0, "new_high_signal_ids": [], "new_first_order_clusters": 0, "new_first_order_cluster_ids": [], "new_stances": 0, "new_stance_ids": [], "boundary_changed": False, "proposition_changed": False, "material_change": False, "remaining_gap_ids": [], "observed_gain": "No material new signal.", "checked_at": timestamp})
            saturation.append({"saturation_id": f"SAT{len(saturation) + 1:03d}", "scope_type": scope_type, "scope_id": scope_id, "stop_rule": "No new first-order signal after follow-up.", "observed_gain": "Two consecutive targeted cycles changed neither boundary nor proposition.", "status": "saturated", "final_cycle_ids": cycle_ids, "remaining_gap_ids": [], "checked_at": timestamp})
    write_jsonl(root / "saturation_events.jsonl", saturation_events)
    write_jsonl(root / "saturation.jsonl", saturation)
    import hashlib
    deliverables = []
    deliverable_specs = [
        ("D001", "readme", ["CL001", "CL002"]),
        *[(f"D{index:03d}", kind, []) for index, kind in enumerate(kinds[1:10], 2)],
        ("D011", "cluster-deep-dive", ["CL001"]),
        ("D012", "cluster-deep-dive", ["CL002"]),
        ("D013", "project-deep-dive", []),
    ]
    for deliverable_id, kind, cluster_ids in deliverable_specs:
        path = Path("reports") / f"{deliverable_id}-{kind}.md"
        resolved = root / path
        resolved.parent.mkdir(exist_ok=True)
        content = "# Test deliverable\n"
        if deliverable_id == "D001":
            content += "\n" + claim()["statement"] + "<!-- claim:C001 -->\n<!-- synthesis:SY001 claims:C001 clusters:CL001 -->\n"
        resolved.write_text(content, encoding="utf-8")
        is_project = kind == "project-deep-dive"
        deliverables.append({"deliverable_id": deliverable_id, "kind": kind, "path": path.as_posix(), "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(), "cluster_ids": cluster_ids, "entity_ids": ["EN002"] if is_project else [], "engineering_profile_ids": ["EP001"] if is_project else [], "publication_status": "published", "required": True, "claim_ids": ["C001"] if deliverable_id == "D001" else [], "synthesis_ids": ["SY001"] if deliverable_id == "D001" else [], "generated_at": timestamp})
    write_jsonl(root / "deliverables.jsonl", deliverables)
    saturation_id_by_scope = {(row["scope_type"], row["scope_id"]): row["saturation_id"] for row in saturation}
    coverage_proofs = []
    for cluster_id in ("CL001", "CL002"):
        entity_id = "EN001" if cluster_id == "CL001" else "EN002"
        source_id = "S001" if cluster_id == "CL001" else "S002"
        deliverable_id = "D011" if cluster_id == "CL001" else "D012"
        for lane in lanes:
            for window in windows:
                window_id = window["window_id"]
                coverage_proofs.append({
                    "proof_id": f"CP-{cluster_id}-{lane}-{window_id}",
                    "cluster_id": cluster_id, "lane": lane, "window_id": window_id,
                    "applicability": "required", "status": "covered", "coverage_basis": "positive_evidence",
                    "positive_entity_count": 1, "scope_claim": "The synthetic fixture contains one mapped in-window entity for this declared cell.",
                    "missing_gates": [],
                    "provenance": {
                        "query_ids": ["QSAT001", "QSAT002"], "successful_query_ids": ["QSAT001", "QSAT002"],
                        "discovery_ids": [], "screening_ids": [], "excluded_discovery_ids": [],
                        "entity_ids": [entity_id], "source_ids": [source_id], "claim_ids": [],
                        "deliverable_ids": [deliverable_id],
                        "saturation_ids": [
                            saturation_id_by_scope[("cluster", cluster_id)],
                            saturation_id_by_scope[("lane", lane)],
                            saturation_id_by_scope[("window", window_id)],
                        ],
                        "saturation_event_ids": [], "gap_ids": [],
                    },
                    "rationale": "Synthetic positive-evidence coverage fixture.", "checked_at": timestamp,
                })
    write_jsonl(root / "coverage-proofs.jsonl", coverage_proofs)


class ResearchBundleTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        argv = list(args)
        if argv and argv[0] == "init" and "--schema-version" not in argv:
            argv.extend(("--schema-version", research_bundle.SCHEMA_VERSION))
        with redirect_stdout(out), redirect_stderr(err):
            code = research_bundle.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_init_creates_a_valid_snapshot_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            code, _, err = self.run_cli("init", "--root", str(root), "--topic", "Evidence graphs", "--as-of", "2026-08-10")
            self.assertEqual((code, err), (0, ""))
            self.assertEqual({path.name for path in root.iterdir()}, set(research_bundle.BASE_FILES))
            run = json.loads((root / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["topic"], "Evidence graphs")
            self.assertEqual(run["mode"], "snapshot")
            self.assertEqual(run["schema_version"], research_bundle.SCHEMA_VERSION)
            schema = json.loads((root / "schema.json").read_text(encoding="utf-8"))
            self.assertEqual(schema["schema_version"], "1.7")
            self.assertEqual(schema["source_access_statuses"], sorted(research_bundle.ACCESS_STATUSES))
            self.assertEqual(schema["evidence_required"], sorted(research_bundle.EVIDENCE_FIELDS))
            self.assertEqual(schema["evidence_relations"], sorted(research_bundle.EVIDENCE_RELATIONS))
            self.assertEqual(schema["query_required"], sorted(research_bundle.QUERY_FIELDS))
            self.assertEqual(schema["candidate_required"], sorted(research_bundle.CANDIDATE_FIELDS))
            self.assertEqual(schema["repository_required"], sorted(research_bundle.REPOSITORY_FIELDS))
            self.assertEqual(schema["paper_required"], sorted(research_bundle.PAPER_FIELDS))
            self.assertEqual(schema["coverage_required"], sorted(research_bundle.COVERAGE_FIELDS))
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0)
            self.assertIn("no source records", out)
            self.assertIn("no claim records", out)
            self.assertIn("report is too short", out)

    def test_init_never_overwrites_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.assertEqual(self.run_cli("init", "--root", str(root), "--topic", "First", "--as-of", "2026-08-10")[0], 0)
            original = (root / "brief.md").read_text(encoding="utf-8")
            code, _, err = self.run_cli("init", "--root", str(root), "--topic", "Second", "--as-of", "2026-08-11")
            self.assertEqual(code, 2)
            self.assertIn("refusing to overwrite", err)
            self.assertEqual((root / "brief.md").read_text(encoding="utf-8"), original)

    def test_broken_cross_reference_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_jsonl(root / "sources.jsonl", [source(supports=[])])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence(source_id="S404")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("references unknown source S404", out)

    def test_report_orphan_url_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            (root / "report.md").write_text("[orphan](https://unregistered.example/path).", encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("URL is not registered", out)

    def test_chinese_adjacent_markdown_links_are_parsed_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            first = source("S001", supports=["C001"], url="https://example.test/one")
            second = source("S002", supports=["C001"], url="https://example.test/two")
            write_jsonl(root / "sources.jsonl", [first, second])
            write_jsonl(root / "queries.jsonl", [query(retained_source_ids=["S001", "S002"])])
            write_jsonl(root / "claims.jsonl", [claim(evidence=["S001", "S002"])])
            write_jsonl(root / "evidence.jsonl", [evidence("E001"), evidence("E002", source_id="S002")])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check(evidence_ids=["E001", "E002"])])
            write_jsonl(root / "candidates.jsonl", [candidate("K001", url=first["url"]), candidate("K002", source_id="S002", url=second["url"])])
            write_jsonl(root / "papers.jsonl", [paper_card("S001"), paper_card("S002")])
            write_jsonl(root / "coverage.jsonl", [coverage(source_ids=["S001", "S002"])])
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->[一](https://example.test/one)；[二](https://example.test/two)支持该结论。",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_strict_promotes_repository_quality_card_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_jsonl(root / "sources.jsonl", [source(source_type="repository", version="0123456789abcdef", license="MIT")])
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            write_jsonl(root / "queries.jsonl", [query(executed_at=timestamp)])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check()])
            write_jsonl(root / "candidates.jsonl", [candidate()])
            write_jsonl(root / "repositories.jsonl", [repository_card(setup="unknown", tests_ci="missing", affiliation="unverified")])
            write_jsonl(root / "coverage.jsonl", [coverage(required_lanes=["github"])])
            write_jsonl(root / "requirements.jsonl", [requirement(required_lanes=["github"], frozen_at=timestamp)])
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->\n\n"
                "The method records repository quality-card observations, source identity, candidate selection, "
                "and validation boundaries as process metadata rather than an additional research conclusion."
                "<!-- process:method -->",
                encoding="utf-8",
            )
            self.assertEqual(self.run_cli("validate", "--root", str(root))[0], 0)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0)
            self.assertIn("setup is unknown", out)
            self.assertIn("tests_ci is missing", out)

    def test_diff_reports_deterministic_changes_and_safe_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old, new = Path(temp) / "old", Path(temp) / "new"
            for root in (old, new):
                self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(old / "sources.jsonl", [source("S001")])
            write_jsonl(new / "sources.jsonl", [source("S001", url="https://example.test/changed"), source("S002", supports=[])])
            write_jsonl(old / "claims.jsonl", [claim("C001")])
            write_jsonl(new / "claims.jsonl", [claim("C001", statement="A changed statement", status="qualified"), claim("C002", evidence=[], status="unsupported")])
            output = Path(temp) / "diff.md"
            code, _, err = self.run_cli("diff", "--old", str(old), "--new", str(new), "--output", str(output))
            self.assertEqual((code, err), (0, ""))
            rendered = output.read_text(encoding="utf-8")
            self.assertIn("`S002`", rendered)
            self.assertIn("`S001` — https://example.test/S001 → https://example.test/changed", rendered)
            self.assertIn("`C002`", rendered)
            self.assertIn("`C001`", rendered)
            self.assertEqual(self.run_cli("diff", "--old", str(old), "--new", str(new), "--output", str(output))[0], 2)

    def test_strict_rejects_an_empty_initialized_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("no source records", out)
            self.assertIn("no claim records", out)

    def test_claim_evidence_requires_a_join_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "claims.jsonl", [claim()])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("supported claim requires a supports or partial evidence join", out)

    def test_high_risk_support_needs_locator_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "claims.jsonl", [claim(risk="high")])
            write_jsonl(root / "evidence.jsonl", [evidence(locator="", support_summary="")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("non-empty locator and support_summary", out)

    def test_strict_rejects_likely_high_risk_claim_marked_normal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "claims.jsonl", [claim(statement="Version 2.4 was released in 2026.")])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("likely high-risk claim is marked normal", out)

    def test_run_topic_must_match_brief_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Correct Topic", "--as-of", "2026-08-10")
            run = json.loads((root / "run.json").read_text(encoding="utf-8"))
            run["topic"] = "Wrong Topic"
            (root / "run.json").write_text(json.dumps(run), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("brief.md: does not contain the run topic", out)
            self.assertIn("report.md: does not contain the run topic", out)

    def test_counter_evidence_requires_and_accepts_a_contradict_join(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_jsonl(root / "sources.jsonl", [source(), source("S002", supports=[])])
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            write_jsonl(root / "queries.jsonl", [query(retained_source_ids=["S001", "S002"], executed_at=timestamp)])
            write_jsonl(root / "claims.jsonl", [claim(status="conflicted")])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check()])
            write_jsonl(root / "candidates.jsonl", [candidate(), candidate("K002", source_id="S002")])
            write_jsonl(root / "papers.jsonl", [paper_card("S001"), paper_card("S002")])
            write_jsonl(root / "coverage.jsonl", [coverage(source_ids=["S001", "S002"])])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("conflicted claim requires both supports and contradicts evidence joins", out)
            write_jsonl(root / "evidence.jsonl", [evidence(), evidence("E002", source_id="S002", relation="contradicts")])
            (root / "report.md").write_text("# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->", encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_conflicted_claim_requires_both_sides(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "queries.jsonl", [query()])
            write_jsonl(root / "claims.jsonl", [claim(status="conflicted")])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            (root / "report.md").write_text(
                "# Test\n\n_As of 2026-08-10_\n\n<!-- claim:C001 -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("conflicted claim requires both supports and contradicts evidence joins", out)

    def test_complete_bundle_passes_strict_with_evidence_joins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            first = source("S001", supports=["C001"], source_type="repository", version="0123456789abcdef", license="MIT", independence_group="group-one")
            second = source("S002", supports=["C001"], independence_group="group-two")
            write_jsonl(root / "sources.jsonl", [first, second])
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            write_jsonl(root / "queries.jsonl", [query(retained_source_ids=["S001", "S002"], executed_at=timestamp)])
            write_jsonl(root / "claims.jsonl", [claim(risk="high", evidence=["S001", "S002"])])
            write_jsonl(root / "evidence.jsonl", [evidence("E001"), evidence("E002", source_id="S002")])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check(evidence_ids=["E001", "E002"])])
            write_jsonl(root / "candidates.jsonl", [candidate(), candidate("K002", source_id="S002")])
            write_jsonl(root / "repositories.jsonl", [repository_card(adoption_evidence=["S002"], affiliation="unverified")])
            write_jsonl(root / "papers.jsonl", [paper_card("S002")])
            write_jsonl(root / "coverage.jsonl", [coverage(source_ids=["S001", "S002"], required_lanes=["paper"])])
            write_jsonl(root / "requirements.jsonl", [requirement(frozen_at=timestamp)])
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->\n\n"
                "The reproducible method records [first](https://example.test/S001) and "
                "[second](https://example.test/S002) as reviewed artifacts, with enough procedural detail "
                "to document the deterministic evidence workflow and registered citation policy.<!-- process:method -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)

    def test_query_and_source_retention_must_be_reciprocal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "queries.jsonl", [query(retained_source_ids=[])])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check()])
            (root / "report.md").write_text("# Test\n\n_As of 2026-08-10_\n\n<!-- claim:C001 -->", encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("does not reciprocally retain the source", out)

    def test_repository_requires_card_and_pinned_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source(source_type="repository", version="main", license="MIT")])
            write_jsonl(root / "queries.jsonl", [query()])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check()])
            (root / "report.md").write_text("# Test\n\n_As of 2026-08-10_\n\n<!-- claim:C001 -->", encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("repository source is missing a quality card", out)
            write_jsonl(root / "repositories.jsonl", [repository_card(pinned_commit="main")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("pinned_commit must be 7 to 40 hexadecimal characters", out)

    def test_repository_allows_explicitly_missing_release_and_license(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_jsonl(root / "sources.jsonl", [source(source_type="repository", version="0123456789abcdef", license=None)])
            write_jsonl(root / "queries.jsonl", [query()])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            write_jsonl(root / "candidates.jsonl", [candidate()])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check()])
            write_jsonl(root / "repositories.jsonl", [repository_card(latest_release=None, license=None, affiliation="unverified")])
            write_jsonl(root / "coverage.jsonl", [coverage(required_lanes=["github"])])
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->\n\n"
                "The source-list records the repository artifact and its disclosed metadata.<!-- process:source-list -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("license is unknown or undeclared", out)

    def test_supported_claim_markers_reject_missing_and_unknown_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "queries.jsonl", [query()])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            (root / "report.md").write_text("# Test\n\n_As of 2026-08-10_", encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("missing a claim marker", out)
            (root / "report.md").write_text("# Test\n\n_As of 2026-08-10_\n\n<!-- claim:C404 -->", encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("claim marker references unknown claim C404", out)

    def test_coverage_is_required_for_nonempty_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root, coverage_records=[])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("sources or claims require at least one coverage record", out)

    def test_coverage_must_map_supported_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root, coverage_records=[coverage(status="partial", claim_ids=[], source_ids=["S001"], gap="claim mapping pending")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("is not referenced by any coverage row", out)

    def test_coverage_covered_status_requires_both_reference_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root, coverage_records=[coverage(claim_ids=[], source_ids=[])])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("covered status requires non-empty claim_ids/source_ids and an empty gap", out)

    def test_complete_coverage_passes_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)

    def test_paper_source_requires_a_card(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root, paper_records=[])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("paper source is missing a paper card", out)

    def test_peer_reviewed_paper_requires_venue(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root, paper_records=[paper_card(publication_status="peer-reviewed", venue=None)])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("peer-reviewed paper requires a venue", out)

    def test_paper_code_reference_must_be_a_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            wrong_type = source("S002", supports=[], queries=[])
            write_valid_paper_bundle(root, paper_records=[paper_card(code_links=[{"source_id": "S002", "relation": "reciprocal", "paper_locator": "Code availability", "repo_locator": "README"}])], extra_sources=[wrong_type])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("source_id must reference a repository source", out)

    def test_complete_paper_card_passes_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)

    def test_retained_candidate_requires_matching_url_and_exactly_one_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "candidates.jsonl", [candidate(url="https://example.test/not-S001")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("retained candidate URL does not match source S001", out)
            write_jsonl(root / "candidates.jsonl", [])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("retained source S001 requires exactly one retained candidate", out)

    def test_excluded_candidate_requires_null_source_and_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "candidates.jsonl", [candidate(decision="excluded", source_id="S001")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("excluded/deferred candidate requires source_id=null and a non-empty reason", out)
            write_jsonl(root / "candidates.jsonl", [candidate(decision="deferred", source_id=None, reason="")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("excluded/deferred candidate requires source_id=null and a non-empty reason", out)

    def test_null_query_result_count_requires_an_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "queries.jsonl", [query(result_count=None, result_count_note="")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("result_count=null requires a non-empty result_count_note", out)

    def test_complete_candidate_funnel_passes_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)

    def test_timestamp_window_rejects_future_query_source_and_evidence(self) -> None:
        future = (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "queries.jsonl", [query(executed_at=future)])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("queries.jsonl:1: executed_at: timestamp is later", out)
            write_jsonl(root / "queries.jsonl", [query()])
            write_jsonl(root / "sources.jsonl", [source(fetched_at=future)])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("sources.jsonl:1: fetched_at: timestamp is later", out)
            write_jsonl(root / "sources.jsonl", [source()])
            write_jsonl(root / "evidence.jsonl", [evidence(checked_at=future)])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("evidence.jsonl:1: checked_at: timestamp is later", out)

    def test_timestamp_window_rejects_records_before_run_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "sources.jsonl", [source(fetched_at="2000-01-01T00:00:00Z")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("sources.jsonl:1: fetched_at: timestamp is earlier than run.json created_at", out)

    def test_claim_marker_requires_exact_statement_not_a_paraphrase(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            (root / "report.md").write_text(
                "# Test\n\n_As of 2026-08-10_\n\nA paraphrase of the result.<!-- claim:C001 -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("needs its exact statement immediately before the claim marker", out)

    def test_repeated_claim_statement_is_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            statement = claim()["statement"]
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + statement + "<!-- claim:C001 -->\n\n" + statement + "<!-- process:method -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("claim statement C001 appears 2 times", out)

    def test_evidence_joins_are_the_only_claim_source_truth(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            stale_source = source(supports=[])
            stale_claim = claim(evidence=["S404"], counter_evidence=["S404"])
            write_jsonl(root / "sources.jsonl", [stale_source])
            write_jsonl(root / "claims.jsonl", [stale_claim])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_high_risk_requires_opened_direct_support(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "claims.jsonl", [claim(risk="high")])
            write_jsonl(root / "sources.jsonl", [source(access_status="metadata-only", access_note="Landing page only")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("requires an opened supports evidence join", out)

    def test_source_access_note_must_explain_the_access_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "sources.jsonl", [source(access_note="")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("access_note must be a non-empty string", out)

    def test_research_log_only_support_requires_an_inference_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            log = source(source_type="research-log", url="bundle://queries.jsonl", queries=[])
            write_jsonl(root / "sources.jsonl", [log])
            write_jsonl(root / "queries.jsonl", [query(result_count=0, retained_source_ids=[])])
            write_jsonl(root / "claims.jsonl", [claim()])
            write_jsonl(root / "evidence.jsonl", [evidence()])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check()])
            write_jsonl(root / "coverage.jsonl", [coverage(required_lanes=["negative"])])
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("non-inference claim cannot be supported only by research-log", out)
            write_jsonl(root / "claims.jsonl", [claim(claim_type="inference")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_block_coverage_rejects_unmarked_executive_bullet_and_table_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            for body in (
                "Executive summary without a marker.",
                "- A recommendation without a marker.",
                "| Claim | Status |\n| --- | --- |\n| Unmarked row | supported |",
            ):
                (root / "report.md").write_text(
                    "# Test — As of 2026-08-10\n\n" + claim()["statement"] + "<!-- claim:C001 -->\n\n" + body,
                    encoding="utf-8",
                )
                code, out, _ = self.run_cli("validate", "--root", str(root))
                self.assertEqual(code, 1)
                self.assertIn("substantive block requires exactly one claim or process marker", out)

    def test_process_block_and_table_header_are_permitted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            statement = claim()["statement"]
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n"
                "The method describes the reproducible workflow.<!-- process:method -->\n\n"
                "| Claim | Status |\n| --- | --- |\n"
                f"| {statement}<!-- claim:C001 --> | supported |",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_numeric_and_repository_language_warn_when_normal_risk(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            second = claim("C022", statement="The peer-reviewed repository release has verified CI.")
            first = claim("C014", statement="The benchmark reports 1,024.5 requests per second.")
            write_jsonl(root / "claims.jsonl", [first, second])
            write_jsonl(root / "evidence.jsonl", [evidence("E014", claim_id="C014"), evidence("E022", claim_id="C022")])
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check("C014", evidence_ids=["E014"]), semantic_check("C022", evidence_ids=["E022"])])
            write_jsonl(root / "coverage.jsonl", [coverage(claim_ids=["C014", "C022"])])
            (root / "report.md").write_text(
                "# Test — As of 2026-08-10\n\n" + first["statement"] + "<!-- claim:C014 -->\n\n"
                + second["statement"] + "<!-- claim:C022 -->",
                encoding="utf-8",
            )
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("claims.jsonl:1: likely high-risk claim is marked normal", out)
            self.assertIn("claims.jsonl:2: likely high-risk claim is marked normal", out)

    def test_strict_allows_advisories_without_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "sources.jsonl", [source(source_type="repository", license="MIT")])
            write_jsonl(root / "papers.jsonl", [])
            write_jsonl(root / "repositories.jsonl", [repository_card(setup="unknown", tests_ci="missing", affiliation="unverified")])
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            write_jsonl(root / "requirements.jsonl", [requirement(required_lanes=["github"], frozen_at=timestamp)])
            write_jsonl(root / "coverage.jsonl", [coverage(required_lanes=["github"])])
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)
            self.assertIn("ADVISORY: repositories.jsonl:1: repository setup is unknown", out)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict", "--json")
            self.assertEqual(code, 0, out)
            self.assertIn("advisories", json.loads(out))

    def test_unsupported_claim_statement_must_not_appear_in_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_valid_paper_bundle(root)
            write_jsonl(root / "claims.jsonl", [claim(status="unsupported")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("unsupported claim C001 statement must not appear", out)

    def test_requirement_mapping_requires_exact_question_and_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_valid_paper_bundle(root)
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            write_jsonl(root / "requirements.jsonl", [requirement(text="Frozen requirement", frozen_at=timestamp)])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("coverage question must exactly match requirement text", out)

    def test_full_profile_sections_allow_process_only_method_and_limitations(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_full_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)
            report = (root / "report.md").read_text(encoding="utf-8")
            (root / "report.md").write_text(report.replace("<!-- section:landscape -->\n\n", "", 1), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("section markers must appear exactly once in the required order", out)

    def test_paper_code_link_and_repository_affiliation_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_valid_paper_bundle(root)
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            repository_source = source("S001", source_type="repository", license="MIT", version="0123456789abcdef", fetched_at=timestamp)
            write_jsonl(root / "sources.jsonl", [repository_source])
            write_jsonl(root / "papers.jsonl", [])
            write_jsonl(root / "repositories.jsonl", [repository_card(affiliation="official-owner", checked_at=timestamp)])
            write_jsonl(root / "requirements.jsonl", [requirement(required_lanes=["github"], frozen_at=timestamp)])
            write_jsonl(root / "coverage.jsonl", [coverage(required_lanes=["github"], updated_at=timestamp)])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("non-unverified repository affiliation requires a paper code link", out)
            paper_source = source("S002", source_type="paper", queries=[], fetched_at=timestamp)
            write_jsonl(root / "sources.jsonl", [repository_source, paper_source])
            write_jsonl(root / "papers.jsonl", [paper_card("S002", checked_at=timestamp, code_links=[{
                "source_id": "S001", "relation": "reciprocal", "paper_locator": "Code availability", "repo_locator": "README code section",
            }])])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_executed_repository_status_requires_a_successful_linked_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_valid_paper_bundle(root)
            timestamp = json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]
            write_jsonl(root / "sources.jsonl", [source(source_type="repository", license="MIT", fetched_at=timestamp)])
            write_jsonl(root / "papers.jsonl", [])
            write_jsonl(root / "requirements.jsonl", [requirement(required_lanes=["github"], frozen_at=timestamp)])
            write_jsonl(root / "coverage.jsonl", [coverage(required_lanes=["github"], updated_at=timestamp)])
            write_jsonl(root / "repositories.jsonl", [repository_card(affiliation="unverified", setup="executed", setup_execution_id="X404")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("setup=executed requires a valid setup_execution_id", out)
            write_jsonl(root / "executions.jsonl", [execution(started_at=timestamp, ended_at=timestamp)])
            write_jsonl(root / "repositories.jsonl", [repository_card(affiliation="unverified", setup="executed", setup_execution_id="X001")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_paper_data_sources_must_be_datasets_and_surveys_t2(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_valid_paper_bundle(root, paper_records=[paper_card(data_source_ids=["S001"])])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("data_source_ids source S001 has the wrong source_type", out)
            write_jsonl(root / "papers.jsonl", [paper_card(evidence_role="survey")])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("survey paper source must have tier T2", out)

    def test_reported_claim_requires_a_passing_semantic_check(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10", "--profile", "rapid")
            write_valid_paper_bundle(root)
            write_jsonl(root / "semantic_checks.jsonl", [])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("requires exactly one semantic check", out)
            write_jsonl(root / "semantic_checks.jsonl", [semantic_check(verdict="revise", uncovered_terms=["scope"] )])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("requires a passing closed semantic check", out)

    def test_full_profile_candidate_quota_and_landscape_table_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Test", "--as-of", "2026-08-10")
            write_full_bundle(root)
            candidates = [record for record in (json.loads(line) for line in (root / "candidates.jsonl").read_text(encoding="utf-8").splitlines()) if record["decision"] == "retained"]
            write_jsonl(root / "candidates.jsonl", candidates)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("excluded/deferred candidates", out)
            write_full_bundle(root)
            report = (root / "report.md").read_text(encoding="utf-8")
            (root / "report.md").write_text(report.replace("| Claim | Status |\n| --- | --- |\n", "", 1).replace("| The kilo record has documented evidence.<!-- claim:C011 --> | supported |\n", "", 1), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("landscape section requires a Markdown data table", out)

    def test_schema_20_init_and_layered_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            code, _, err = self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            self.assertEqual((code, err), (0, ""))
            self.assertIn("research_plan.json", {path.name for path in root.iterdir()})
            self.assertIn("stage_events.jsonl", {path.name for path in root.iterdir()})
            write_v2_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_schema_20_claim_marker_requires_exact_ledger_statement(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            (root / "report.md").write_text(
                "# Layered report\n\nA paraphrase of the ledger claim.<!-- claim:C001 -->\n",
                encoding="utf-8",
            )
            import hashlib
            deliverable = json.loads((root / "deliverables.jsonl").read_text(encoding="utf-8"))
            deliverable["sha256"] = hashlib.sha256((root / "report.md").read_bytes()).hexdigest()
            write_jsonl(root / "deliverables.jsonl", [deliverable])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("must immediately follow its exact ledger statement", out)

    def test_schema_20_repository_views_cannot_split_independence_groups(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            sources = [json.loads(line) for line in (root / "sources.jsonl").read_text(encoding="utf-8").splitlines()]
            sources.append(source("S003", source_type="official-doc", entity_id="EN002", independence_group="split-repository-view"))
            write_jsonl(root / "sources.jsonl", sources)
            entities = [json.loads(line) for line in (root / "entities.jsonl").read_text(encoding="utf-8").splitlines()]
            next(entity for entity in entities if entity["entity_id"] == "EN002")["source_ids"].append("S003")
            write_jsonl(root / "entities.jsonl", entities)
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("must share one independence_group", out)

    def test_schema_20_accepts_comprehensive_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            code, _, err = self.run_cli(
                "init", "--root", str(root), "--topic", "Layered",
                "--as-of", "2026-08-10", "--profile", "comprehensive",
            )
            self.assertEqual((code, err), (0, ""))
            run = json.loads((root / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["review_profile"], "comprehensive")

    def test_schema_20_rejects_nondeep_source_and_bad_deliverable_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            entity = json.loads((root / "entities.jsonl").read_text(encoding="utf-8"))
            entity["stage"] = "mapped"
            write_jsonl(root / "entities.jsonl", [entity])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("requires a deep-verified entity_id", out)
            entity["stage"] = "deep-verified"
            write_jsonl(root / "entities.jsonl", [entity])
            deliverable = json.loads((root / "deliverables.jsonl").read_text(encoding="utf-8"))
            deliverable["sha256"] = "0" * 64
            write_jsonl(root / "deliverables.jsonl", [deliverable])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("sha256 does not match file bytes", out)

    def test_schema_20_query_stage_and_entity_transition_are_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            row = json.loads((root / "queries.jsonl").read_text(encoding="utf-8")); row["stage"] = "deep"
            write_jsonl(root / "queries.jsonl", [row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("stage/iteration are invalid", out)
            row["stage"] = "verify"; write_jsonl(root / "queries.jsonl", [row])
            events = [json.loads(line) for line in (root / "stage_events.jsonl").read_text(encoding="utf-8").splitlines()]
            events[0]["to_stage"] = "deep-verified"
            write_jsonl(root / "stage_events.jsonl", events)
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("without rollback or jump", out)

    def test_schema_20_query_log_preserves_replay_fields_and_failed_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            row = json.loads((root / "queries.jsonl").read_text(encoding="utf-8"))
            row.pop("query_text")
            write_jsonl(root / "queries.jsonl", [row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("missing required fields", out)
            write_v2_bundle(root)
            row = json.loads((root / "queries.jsonl").read_text(encoding="utf-8"))
            row.update({"status": "failed", "result_count": 0, "result_count_note": ""})
            write_jsonl(root / "queries.jsonl", [row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("require a result_count_note", out)

    def test_schema_20_screening_allows_an_explicit_defer_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            row = json.loads((root / "screening.jsonl").read_text(encoding="utf-8"))
            row["decision"] = "defer"
            row["reason"] = "Metadata is plausible, but identity is not yet resolvable."
            write_jsonl(root / "screening.jsonl", [row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_schema_20_rejects_cluster_cycle_and_unmet_declared_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            cluster = json.loads((root / "clusters.jsonl").read_text(encoding="utf-8")); cluster["parent_ids"] = ["CL001"]
            write_jsonl(root / "clusters.jsonl", [cluster])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("acyclic known DAG", out)
            cluster["parent_ids"] = []; write_jsonl(root / "clusters.jsonl", [cluster])
            plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8")); plan["targets"]["deep_papers"] = 2
            (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("declared target for deep_papers is not met", out)

    def test_schema_20_population_targets_are_cumulative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8"))
            plan["targets"].update({"discovered_entities": 1, "mapped_entities": 1, "papers_discovered": 1, "papers_mapped": 1})
            (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

    def test_schema_20_rejects_paper_data_type_and_open_semantic_check(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            card = json.loads((root / "papers.jsonl").read_text(encoding="utf-8")); card["data_source_ids"] = ["S001"]
            write_jsonl(root / "papers.jsonl", [card])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("data_source_ids must be dataset sources", out)
            card["data_source_ids"] = []; write_jsonl(root / "papers.jsonl", [card])
            check = json.loads((root / "semantic_checks.jsonl").read_text(encoding="utf-8")); check["verdict"] = "revise"
            write_jsonl(root / "semantic_checks.jsonl", [check])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("published claim requires closed passing semantic check", out)

    def test_schema_20_allows_bounded_normal_inference_with_partial_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            claim_row = json.loads((root / "claims.jsonl").read_text(encoding="utf-8"))
            claim_row["claim_type"] = "inference"
            claim_row["risk"] = "normal"
            write_jsonl(root / "claims.jsonl", [claim_row])
            evidence_row = json.loads((root / "evidence.jsonl").read_text(encoding="utf-8"))
            evidence_row["relation"] = "partial"
            evidence_row["support_summary"] = "The source supports the bounded analytical reading but not a universal external fact."
            write_jsonl(root / "evidence.jsonl", [evidence_row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)
            claim_row["risk"] = "high"
            write_jsonl(root / "claims.jsonl", [claim_row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("bounded normal-risk inference", out)

    def test_schema_20_requires_bidirectional_manifest_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            (root / "report.md").write_text("# Layered report\n", encoding="utf-8")
            import hashlib
            delivery = json.loads((root / "deliverables.jsonl").read_text(encoding="utf-8")); delivery["sha256"] = hashlib.sha256((root / "report.md").read_bytes()).hexdigest()
            write_jsonl(root / "deliverables.jsonl", [delivery])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("markers and manifest must be bidirectional", out)

    def test_schema_20_rejects_ledger_only_claim_in_reader(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            row = json.loads((root / "claims.jsonl").read_text(encoding="utf-8"))
            row["publication_status"] = "ledger-only"
            row["deliverable_ids"] = []
            write_jsonl(root / "claims.jsonl", [row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("ledger-only claim must not appear in a published reader artifact", out)

    def test_schema_20_rejects_exact_date_window_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            row = json.loads((root / "entities.jsonl").read_text(encoding="utf-8"))
            row["time_window_ids"] = []
            write_jsonl(root / "entities.jsonl", [row])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("exact published_at must reconcile", out)

    def test_schema_20_important_cluster_needs_completion_or_explicit_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            cluster = json.loads((root / "clusters.jsonl").read_text(encoding="utf-8")); cluster["importance"] = "important"
            write_jsonl(root / "clusters.jsonl", [cluster])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 1); self.assertIn("important cluster CL001", out)

    def test_schema_20_comprehensive_rejects_an_empty_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0", "--profile", "comprehensive")
            write_v2_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("comprehensive profile requires paper/github/benchmark/negative lanes", out)
            self.assertIn("explicit positive integer", out)

    def test_schema_20_complete_comprehensive_bundle_passes_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)

    def test_schema_20_comprehensive_reports_partial_cells_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            coverage_rows = [json.loads(line) for line in (root / "cluster_coverage.jsonl").read_text(encoding="utf-8").splitlines()]
            proof_rows = [json.loads(line) for line in (root / "coverage-proofs.jsonl").read_text(encoding="utf-8").splitlines()]
            coverage_rows[0]["status"] = "partial"
            proof_rows[0].update(status="partial", coverage_basis="incomplete", missing_gates=["replayable_successful_exact_query"])
            write_jsonl(root / "cluster_coverage.jsonl", coverage_rows)
            write_jsonl(root / "coverage-proofs.jsonl", proof_rows)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)
            self.assertIn("diagnostic grid has 1 partial/gap important-scope cells", out)

    def test_schema_20_covered_proof_requires_real_targeted_query(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            proofs = [json.loads(line) for line in (root / "coverage-proofs.jsonl").read_text(encoding="utf-8").splitlines()]
            proofs[0]["provenance"]["query_ids"] = []
            proofs[0]["provenance"]["successful_query_ids"] = []
            write_jsonl(root / "coverage-proofs.jsonl", proofs)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("covered requires no missing gates, a successful targeted query", out)

    def test_schema_20_allows_targeted_optional_coverage_proofs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            proofs = [json.loads(line) for line in (root / "coverage-proofs.jsonl").read_text(encoding="utf-8").splitlines()]
            write_jsonl(root / "coverage-proofs.jsonl", proofs[1:])
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)

    def test_schema_20_comprehensive_allows_no_coverage_proof_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            (root / "coverage-proofs.jsonl").unlink()
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)
            self.assertIn("optional detailed cell audit was not supplied", out)

    def test_schema_20_comprehensive_allows_incomplete_cluster_with_explicit_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            saturation = [json.loads(line) for line in (root / "saturation.jsonl").read_text(encoding="utf-8").splitlines()]
            gap = {"gap_id": "G001", "question_id": "RQ001", "cluster_ids": ["CL001"], "lanes": ["paper"], "window_ids": ["W002"], "perspectives": ["mechanism"], "status": "open", "rationale": "A bounded residual gap remains.", "created_at": json.loads((root / "run.json").read_text(encoding="utf-8"))["created_at"]}
            write_jsonl(root / "gaps.jsonl", [gap])
            (root / "coverage-proofs.jsonl").unlink()
            target = next(row for row in saturation if row["scope_type"] == "cluster" and row["scope_id"] == "CL001")
            target["status"] = "incomplete"
            target["remaining_gap_ids"] = ["G001"]
            write_jsonl(root / "saturation.jsonl", saturation)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 0, out)
            self.assertIn("important cluster CL001: conclusion remains qualified", out)

    def test_schema_20_saturation_requires_replayable_consecutive_scope_targeted_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            saturation = [json.loads(line) for line in (root / "saturation.jsonl").read_text(encoding="utf-8").splitlines()]
            saturation[0]["final_cycle_ids"] = saturation[0]["final_cycle_ids"][:1]
            write_jsonl(root / "saturation.jsonl", saturation)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("requires at least two final cycle observations", out)

            write_comprehensive_v2_bundle(root)
            events = [json.loads(line) for line in (root / "saturation_events.jsonl").read_text(encoding="utf-8").splitlines()]
            target = next(row for row in events if row["scope_type"] == "cluster" and row["scope_id"] == "CL002" and row["iteration"] == 2)
            target["query_ids"] = ["Q001"]
            write_jsonl(root / "saturation_events.jsonl", events)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("same recorded iteration", out)
            self.assertIn("explicitly target the event scope", out)

            write_comprehensive_v2_bundle(root)
            queries = [json.loads(line) for line in (root / "queries.jsonl").read_text(encoding="utf-8").splitlines()]
            next(row for row in queries if row["query_id"] == "QSAT002")["status"] = "partial"
            write_jsonl(root / "queries.jsonl", queries)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("only successfully completed queries", out)

    def test_schema_20_published_synthesis_groups_must_match_evidence_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            syntheses = [json.loads(line) for line in (root / "syntheses.jsonl").read_text(encoding="utf-8").splitlines()]
            syntheses[0]["supporting_group_ids"] = ["invented-group"]
            write_jsonl(root / "syntheses.jsonl", syntheses)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("supporting_group_ids must exactly match supporting evidence source independence groups", out)

    def test_schema_20_synthesis_stance_partition_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            syntheses = [json.loads(line) for line in (root / "syntheses.jsonl").read_text(encoding="utf-8").splitlines()]
            syntheses[0]["supporting_evidence_ids"] = []
            syntheses[0]["opposing_evidence_ids"] = []
            syntheses[0]["assessment"] = "mixed"
            write_jsonl(root / "syntheses.jsonl", syntheses)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("evidence_ids must equal the synthesis-level support/opposition partition", out)
            self.assertIn("mixed/disputed synthesis requires explicit opposing evidence", out)

    def test_schema_20_project_deep_dive_requires_complete_engineering_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            profiles = [json.loads(line) for line in (root / "repository_engineering_profiles.jsonl").read_text(encoding="utf-8").splitlines()]
            profiles[0]["components"] = profiles[0]["components"][:2]
            write_jsonl(root / "repository_engineering_profiles.jsonl", profiles)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("components requires at least 3 located records", out)

    def test_schema_20_cross_source_synthesis_cannot_be_an_atomic_claim_or_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            syntheses = [json.loads(line) for line in (root / "syntheses.jsonl").read_text(encoding="utf-8").splitlines()]
            atomic_statement = json.loads((root / "claims.jsonl").read_text(encoding="utf-8").splitlines()[0])["statement"]
            syntheses[0]["action"] = "cross-source synthesis"
            syntheses[0]["proposition"] = atomic_statement
            write_jsonl(root / "syntheses.jsonl", syntheses)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("cross-source synthesis requires at least two canonical independence groups", out)
            self.assertIn("must be an analytical judgment, not an underlying atomic claim", out)

            syntheses[0]["action"] = "compare"
            syntheses[0]["proposition"] = "A proposition <!-- claim:C001 --> with an embedded marker."
            write_jsonl(root / "syntheses.jsonl", syntheses)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("proposition must not contain claim or process markers", out)

    def test_schema_20_required_reader_cannot_concatenate_multiple_h1_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            deliverables = [json.loads(line) for line in (root / "deliverables.jsonl").read_text(encoding="utf-8").splitlines()]
            target = next(row for row in deliverables if row["deliverable_id"] == "D001")
            report = root / target["path"]
            report.write_text(report.read_text(encoding="utf-8") + "\n# Concatenated second report\n", encoding="utf-8")
            target["sha256"] = hashlib.sha256(report.read_bytes()).hexdigest()
            write_jsonl(root / "deliverables.jsonl", deliverables)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("must not concatenate multiple H1 documents", out)

    def test_schema_20_comprehensive_rejects_missing_lane_window_deliverable_saturation_and_synthesis(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8"))
            plan["lanes"].remove("negative")
            (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1); self.assertIn("paper/github/benchmark/negative lanes", out)

            write_comprehensive_v2_bundle(root)
            windows = [json.loads(line) for line in (root / "time_windows.jsonl").read_text(encoding="utf-8").splitlines()]
            windows = [row for row in windows if row["kind"] != "recent-90d"]
            write_jsonl(root / "time_windows.jsonl", windows)
            plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8")); plan["time_windows"] = [row["window_id"] for row in windows]
            (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1); self.assertIn("foundational, recent-12m, and recent-90d", out)

            write_comprehensive_v2_bundle(root)
            plan = json.loads((root / "research_plan.json").read_text(encoding="utf-8")); plan["required_deliverable_kinds"].remove("method")
            (root / "research_plan.json").write_text(json.dumps(plan), encoding="utf-8")
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1); self.assertIn("missing required deliverable kinds", out)

            write_comprehensive_v2_bundle(root)
            write_jsonl(root / "saturation.jsonl", [])
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1); self.assertIn("requires non-empty saturation records", out)

            write_comprehensive_v2_bundle(root)
            write_jsonl(root / "syntheses.jsonl", [])
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1); self.assertIn("requires non-empty syntheses", out)

    def test_schema_20_rejects_cross_entity_growth_observations(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_comprehensive_v2_bundle(root)
            observations = [json.loads(line) for line in (root / "repository_observations.jsonl").read_text(encoding="utf-8").splitlines()]
            observations[1]["entity_id"] = "EN001"
            write_jsonl(root / "repository_observations.jsonl", observations)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("observations must belong to the target entity", out)

    def test_schema_20_allows_unknown_time_windows_without_counting_them_as_recent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            self.run_cli("init", "--root", str(root), "--topic", "Layered", "--as-of", "2026-08-10", "--schema-version", "2.0")
            write_v2_bundle(root)
            entity = json.loads((root / "entities.jsonl").read_text(encoding="utf-8"))
            entity["time_window_ids"] = []
            entity["published_at"] = None
            entity["date_confidence"] = "unknown"
            write_jsonl(root / "entities.jsonl", [entity])
            code, out, _ = self.run_cli("validate", "--root", str(root))
            self.assertEqual(code, 0, out)

            write_comprehensive_v2_bundle(root)
            entities = [json.loads(line) for line in (root / "entities.jsonl").read_text(encoding="utf-8").splitlines()]
            for row in entities:
                row["time_window_ids"] = []
                row["published_at"] = None
                row["date_confidence"] = "unknown"
            write_jsonl(root / "entities.jsonl", entities)
            code, out, _ = self.run_cli("validate", "--root", str(root), "--strict")
            self.assertEqual(code, 1)
            self.assertIn("declared target for recent_discovered is not met", out)
            self.assertIn("declared target for recent_mapped is not met", out)


if __name__ == "__main__":
    unittest.main()
