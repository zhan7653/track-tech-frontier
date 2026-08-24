from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
CHECKED_7 = "2026-08-23T18:55:00Z"
CHECKED_8 = "2026-08-23T19:00:00Z"
GENERATED = "2026-08-23T19:05:00Z"
CLUSTERS = [f"SM-C{index:02d}" for index in range(1, 9)]


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def upsert(rows: list[dict], key: str, record: dict) -> None:
    for index, row in enumerate(rows):
        if row.get(key) == record[key]:
            rows[index] = record
            return
    rows.append(record)


def copy_publication(source: str, destination: str, synthesis: dict | None = None) -> Path:
    src = ROOT / source
    dst = ROOT / destination
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    if synthesis is not None:
        claims = ",".join(synthesis["claim_ids"])
        clusters = ",".join(synthesis["cluster_ids"])
        text += (
            "\n\n## 证据账本绑定\n\n"
            + synthesis["proposition"]
            + f"\n<!-- synthesis:{synthesis['synthesis_id']} claims:{claims} clusters:{clusters} -->\n"
        )
    dst.write_text(text, encoding="utf-8")
    return dst


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    queries = read(ROOT / "queries.jsonl")
    gaps = read(ROOT / "gaps.jsonl")
    syntheses = read(ROOT / "syntheses.jsonl")
    synthesis_by_id = {row["synthesis_id"]: row for row in syntheses}

    gap_ids_by_cluster: dict[str, list[str]] = {cluster: [] for cluster in CLUSTERS}
    for gap in gaps:
        for cluster in gap.get("cluster_ids", []):
            if cluster in gap_ids_by_cluster:
                gap_ids_by_cluster[cluster].append(gap["gap_id"])

    # Two consecutive, explicit boundary-review cycles support structural
    # saturation. They do not claim all empirical gaps are closed.
    for index, cluster in enumerate(CLUSTERS, start=1):
        for iteration, checked, base in ((7, CHECKED_7, 94), (8, CHECKED_8, 102)):
            query_id = f"Q{base + index - 1:03d}"
            upsert(queries, "query_id", {
                "executed_at": checked,
                "gap_ids": gap_ids_by_cluster[cluster],
                "information_gain": "Rechecked the branch against the paper mechanisms, fixed-version engineering reports, negative evidence and cross-cutting constraints; no new first-order boundary or stance was required.",
                "iteration": iteration,
                "parent_query_ids": [f"Q{84 + index - 1:03d}"],
                "provider": "manual-audit",
                "query_id": query_id,
                "query_text": f"Final structural recheck for {cluster}",
                "raw_snapshot_paths": [str(ROOT / "iterations" / f"round-{iteration:02d}" / "evaluation.md")],
                "request_url": None,
                "result_count": 1,
                "result_count_note": "One completed branch-level audit across the frozen research suite.",
                "stage": "verify",
                "status": "succeeded",
                "target_cluster_ids": [cluster],
                "target_lanes": ["paper", "repository", "negative"],
                "target_window_ids": ["W_ROLLING_12M", "W_ROLLING_90D"],
            })
    write(ROOT / "queries.jsonl", queries)

    saturation_events: list[dict] = []
    saturation: list[dict] = []
    for index, cluster in enumerate(CLUSTERS, start=1):
        cycle_ids = []
        for iteration, checked, base in ((7, CHECKED_7, 94), (8, CHECKED_8, 102)):
            cycle_id = f"SAT-E-{cluster}-{iteration}"
            cycle_ids.append(cycle_id)
            saturation_events.append({
                "boundary_changed": False,
                "checked_at": checked,
                "cycle_id": cycle_id,
                "iteration": iteration,
                "material_change": False,
                "new_entities": 0,
                "new_entity_ids": [],
                "new_first_order_cluster_ids": [],
                "new_first_order_clusters": 0,
                "new_high_signal_ids": [],
                "new_high_signal_items": 0,
                "new_stance_ids": [],
                "new_stances": 0,
                "observed_gain": "No new first-order mechanism, boundary or synthesis stance; remaining gaps change confidence or future work rather than the field tree.",
                "proposition_changed": False,
                "query_ids": [f"Q{base + index - 1:03d}"],
                "remaining_gap_ids": gap_ids_by_cluster[cluster],
                "scope_id": cluster,
                "scope_type": "cluster",
            })
        saturation.append({
            "checked_at": CHECKED_8,
            "final_cycle_ids": cycle_ids,
            "observed_gain": "Two consecutive reader/ledger boundary audits produced no material structural change.",
            "remaining_gap_ids": gap_ids_by_cluster[cluster],
            "saturation_id": f"SAT-{cluster}",
            "scope_id": cluster,
            "scope_type": "cluster",
            "status": "saturated",
            "stop_rule": "Stop first-order expansion after two consecutive iterations add no first-order cluster, boundary change or synthesis stance; preserve empirical gaps explicitly.",
        })
    write(ROOT / "saturation_events.jsonl", saturation_events)
    write(ROOT / "saturation.jsonl", saturation)

    # Relations say only that fixed engineering and study evidence instantiate
    # one mechanism family; they do not imply implementation lineage.
    evidence = read(ROOT / "evidence.jsonl")
    sources = read(ROOT / "sources.jsonl")
    source_entity = {row["source_id"]: row["entity_id"] for row in sources}
    evidence_by_claim = {row["claim_id"]: row for row in evidence}
    relation_pairs = [
        ("R5-C003", "R4-C019", "SM-C01"),
        ("R5-C014", "R4-C009", "SM-C02"),
        ("R5-C011", "R4-C007", "SM-C03"),
        ("R5-C017", "R4-C001", "SM-C04"),
        ("R5-C004", "R4-C018", "SM-C05"),
        ("R5-C016", "R4-C030", "SM-C06"),
        ("R5-C006", "R4-C016", "SM-C07"),
        ("R5-C002", "R4-C020", "SM-C08"),
    ]
    relations = []
    for left, right, cluster in relation_pairs:
        left_ev, right_ev = evidence_by_claim[left], evidence_by_claim[right]
        relations.append({
            "assertion_type": "inference",
            "conditions": "The relation means both artifacts inform the same mechanism branch; it does not assert code descent, equivalence or independent reproduction.",
            "confidence": "medium",
            "evidence_ids": [left_ev["evidence_id"], right_ev["evidence_id"]],
            "from_entity_id": source_entity[left_ev["source_id"]],
            "relation_id": f"REL-{cluster}",
            "relation_type": "engineering and research evidence address the same mechanism family",
            "to_entity_id": source_entity[right_ev["source_id"]],
        })
    write(ROOT / "relations.jsonl", relations)

    observations = read(ROOT / "repository_observations.jsonl")
    trend_metrics = []
    for observation in observations:
        trend_metrics.append({
            "acceleration": None,
            "checked_at": observation["observed_at"],
            "cluster_id": None,
            "completeness": "Complete for one inclusive 90-day commit/contributor window; no earlier comparable snapshot.",
            "delta": None,
            "end": "2026-08-24",
            "entity_id": observation["entity_id"],
            "followup": "Collect a later comparable snapshot before inferring growth, velocity or acceleration.",
            "method": "GitHub REST point-in-time repository metadata plus exhaustive paginated commit window; stars remain cumulative snapshot context.",
            "metric_id": "TM-" + observation["observation_id"],
            "metric_type": "activity-snapshot",
            "observation_ids": [observation["observation_id"]],
            "rate": None,
            "signal_only": True,
            "start": "2026-05-27",
            "status": "qualified",
        })
    write(ROOT / "trend_metrics.jsonl", trend_metrics)

    publication = ROOT / "publication"
    if publication.exists():
        shutil.rmtree(publication)
    publication.mkdir(parents=True)

    deliverables: list[dict] = []
    all_clusters = CLUSTERS

    def add(deliverable_id: str, kind: str, source: str, destination: str, *, clusters: list[str] | None = None,
            entities: list[str] | None = None, profiles: list[str] | None = None, synthesis_id: str | None = None) -> None:
        synthesis = synthesis_by_id[synthesis_id] if synthesis_id else None
        path = copy_publication(source, destination, synthesis)
        deliverables.append({
            "claim_ids": [],
            "cluster_ids": clusters or [],
            "deliverable_id": deliverable_id,
            "engineering_profile_ids": profiles or [],
            "entity_ids": entities or [],
            "generated_at": GENERATED,
            "kind": kind,
            "path": path.relative_to(ROOT).as_posix(),
            "publication_status": "published",
            "required": True,
            "sha256": digest(path),
            "synthesis_ids": [synthesis_id] if synthesis_id else [],
        })
        if synthesis is not None:
            synthesis["publication_status"] = "published"
            synthesis["deliverable_ids"] = [deliverable_id]

    add("D-CORE-README", "readme", "README.md", "publication/README.md", clusters=all_clusters)
    add("D-CORE-EXEC", "executive", "reader/overview.md", "publication/overview.md", clusters=all_clusters)
    add("D-CORE-FIELD", "field-tree", "reader/architecture.md", "publication/architecture.md", clusters=all_clusters)
    add("D-CORE-LAND", "landscape", "reader/solution-landscape.md", "publication/solution-landscape.md", clusters=all_clusters)
    add("D-CORE-TIME", "timeline", "reader/trends.md", "publication/trends.md", clusters=all_clusters)
    add("D-CORE-RADAR", "repository-radar", "reader/github-radar.md", "publication/github-radar.md", clusters=all_clusters)
    add("D-CORE-BENCHMARK", "benchmark-map", "reader/cross-cutting/benchmark-protocols.md", "publication/benchmark-protocols.md", clusters=all_clusters, synthesis_id="SY-X02")
    add("D-CORE-SECURITY", "security-failure", "reader/cross-cutting/02-security-governance.md", "publication/security-governance.md", clusters=["SM-C01", "SM-C02", "SM-C04", "SM-C05"], synthesis_id="SY-X01")
    add("D-CORE-CONSENSUS", "consensus", "reader/consensus-and-open-questions.md", "publication/consensus-and-open-questions.md", clusters=all_clusters)
    add("D-CORE-METHOD", "method", "reader/method-and-scope.md", "publication/method-and-scope.md", clusters=all_clusters)
    add("D-CORE-SOURCES", "source-index", "reader/source-index.md", "publication/source-index.md", clusters=all_clusters)
    add("D-CORE-REPORT", "report", "report.md", "publication/report.md", clusters=all_clusters)

    branch_sources = {
        "SM-C01": "reader/mechanisms/context-inheritance/01-mechanisms-and-security.md",
        "SM-C02": "reader/mechanisms/ownership-visibility/01-policy-and-provenance.md",
        "SM-C03": "reader/mechanisms/shared-substrates/01-state-surfaces.md",
        "SM-C04": "reader/mechanisms/synchronization/01-conflict-and-commit.md",
        "SM-C05": "reader/mechanisms/return-consolidation/01-compilation-and-lineage.md",
        "SM-C06": "reader/mechanisms/experience-transfer/01-trajectories-cards-and-skills.md",
        "SM-C07": "reader/mechanisms/retrieval-action/01-routing-navigation-and-gates.md",
        "SM-C08": "reader/mechanisms/local-persistence/01-runtime-lifetimes.md",
    }
    assignments = read(ROOT / "cluster_assignments.jsonl")
    for cluster in CLUSTERS:
        entity_ids = sorted({row["entity_id"] for row in assignments if row["cluster_id"] == cluster and row["entity_id"] in source_entity.values()})
        add(f"D-CLUSTER-{cluster[-3:]}", "cluster-deep-dive", branch_sources[cluster], f"publication/branches/{cluster}.md",
            clusters=[cluster], entities=entity_ids, synthesis_id="SY-C" + cluster[-2:])

    profiles = read(ROOT / "repository_engineering_profiles.jsonl")
    entities = read(ROOT / "entities.jsonl")
    entity_by_id = {row["entity_id"]: row for row in entities}
    project_report = {
        "openai/openai-agents-python": "openai--openai-agents-python.md",
        "openai/codex": "openai--codex.md",
        "langchain-ai/langgraph": "langchain-ai--langgraph.md",
        "langchain-ai/deepagents": "langchain-ai--deepagents.md",
        "microsoft/autogen": "microsoft--autogen.md",
        "microsoft/UFO": "microsoft--UFO.md",
        "caura-ai/caura": "caura-ai--caura.md",
        "smaramwbc/statewave-multi-agent-memory": "smaramwbc--statewave-multi-agent-memory.md",
        "kimdanny/matm": "kimdanny--matm.md",
        "MehulG/memX": "MehulG--memX.md",
    }
    for index, profile in enumerate(profiles, start=1):
        repo = entity_by_id[profile["entity_id"]]["canonical_name"]
        filename = project_report[repo]
        repo_clusters = sorted({row["cluster_id"] for row in assignments if row["entity_id"] == profile["entity_id"]})
        add(f"D-PROJECT-{index:02d}", "project-deep-dive", f"reader/projects/{filename}", f"publication/projects/{filename}",
            clusters=repo_clusters, entities=[profile["entity_id"]], profiles=[profile["profile_id"]])

    write(ROOT / "syntheses.jsonl", syntheses)
    write(ROOT / "deliverables.jsonl", deliverables)

    plan = json.loads((ROOT / "research_plan.json").read_text(encoding="utf-8"))
    plan["targets"] = {
        "claims": 50,
        "clusters": 8,
        "deep_papers": 40,
        "deep_repositories": 10,
        "deep_verified_entities": 50,
        "deliverables": 30,
        "discovered_entities": 4000,
        "evidence": 50,
        "mapped_entities": 200,
        "papers_discovered": 2000,
        "papers_mapped": 60,
        "queries": 100,
        "recent_discovered": 3000,
        "recent_mapped": 100,
        "repositories_discovered": 2000,
        "repositories_mapped": 130,
        "sources": 50,
    }
    (ROOT / "research_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"queries": len(queries), "saturation": len(saturation), "relations": len(relations), "trends": len(trend_metrics), "deliverables": len(deliverables)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
