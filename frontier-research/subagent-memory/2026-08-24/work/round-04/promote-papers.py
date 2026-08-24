from __future__ import annotations

import json
import re
from pathlib import Path


BUNDLE = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
CHECKED_AT = "2026-08-23T17:40:00Z"

VENUE_OVERRIDES = {
    "2605.16746": ("conference", "NeurIPS 2026", "PDF first page: '40th Conference on Neural Information Processing Systems (NeurIPS 2026)'"),
    "2606.04329": ("workshop", "AIWILD at ICML 2026", "PDF first page: 'Published at the Second Workshop on Agents in the Wild ... at ICML 2026'"),
}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    extractions = read_jsonl(BUNDLE / "work" / "round-04" / "extraction.jsonl")
    entities = read_jsonl(BUNDLE / "entities.jsonl")
    discoveries = read_jsonl(BUNDLE / "discovery_results.jsonl")
    assignments = read_jsonl(BUNDLE / "cluster_assignments.jsonl")
    sources = read_jsonl(BUNDLE / "sources.jsonl")
    papers = read_jsonl(BUNDLE / "papers.jsonl")
    stage_events = read_jsonl(BUNDLE / "stage_events.jsonl")

    entity_by_identifier = {row["identifier"]: row for row in entities}
    discovery_by_id = {row["discovery_id"]: row for row in discoveries}
    assignment_clusters: dict[str, list[str]] = {}
    for row in assignments:
        assignment_clusters.setdefault(row["entity_id"], []).append(row["cluster_id"])
    source_ids = {row["source_id"] for row in sources}
    paper_source_ids = {row["source_id"] for row in papers}
    event_ids = {row["event_id"] for row in stage_events}

    promoted = 0
    created_sources = 0
    created_cards = 0
    for extraction in extractions:
        arxiv_id = extraction["arxiv_id"]
        identifier = f"arxiv:{arxiv_id}"
        entity = entity_by_identifier.get(identifier)
        if entity is None:
            raise RuntimeError(f"No entity for {identifier}")
        source_id = f"S-P-{arxiv_id.replace('.', '')}"
        text_path = Path(extraction["text_path"])
        text = text_path.read_text(encoding="utf-8", errors="replace")
        revision_match = re.search(rf"arXiv:{re.escape(arxiv_id)}v(\d+)", text[:12000], re.I)
        revision = f"v{revision_match.group(1)}" if revision_match else "version-unresolved"
        code_links = sorted(set(re.findall(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text)))
        queries = sorted(
            {
                discovery_by_id[discovery_id]["query_id"]
                for discovery_id in entity.get("discovery_ids", [])
                if discovery_id in discovery_by_id
            }
        )

        old_stage = entity["stage"]
        if old_stage != "deep-verified":
            entity["stage"] = "deep-verified"
            promoted += 1
            event_id = f"SE-R4-{arxiv_id.replace('.', '')}"
            if event_id not in event_ids:
                stage_events.append(
                    {
                        "entity_id": entity["entity_id"],
                        "event_id": event_id,
                        "from_stage": old_stage,
                        "occurred_at": CHECKED_AT,
                        "rationale": "Original arXiv PDF downloaded, hashed, fully text-extracted, and inspected for mechanism/evaluation evidence.",
                        "to_stage": "deep-verified",
                    }
                )
                event_ids.add(event_id)
        if source_id not in entity["source_ids"]:
            entity["source_ids"].append(source_id)

        if source_id not in source_ids:
            sources.append(
                {
                    "access_note": f"Downloaded PDF SHA-256 {extraction['sha256']}; {extraction['pages']} pages; extracted text at {text_path}.",
                    "access_status": "opened",
                    "entity_id": entity["entity_id"],
                    "fetched_at": CHECKED_AT,
                    "independence_group": f"paper:{arxiv_id}",
                    "limitations": "Author paper; conclusions are bounded to the stated protocol. PDF extraction was checked for mechanism, experiments and limitations; no independent reproduction was performed in this research run.",
                    "organization": "paper authors",
                    "published_at": entity.get("published_at"),
                    "queries": queries,
                    "source_id": source_id,
                    "source_type": "paper",
                    "tier": "T1",
                    "title": entity["canonical_name"],
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "version": revision,
                }
            )
            source_ids.add(source_id)
            created_sources += 1

        if source_id not in paper_source_ids:
            publication_status, venue, status_locator = VENUE_OVERRIDES.get(
                arxiv_id,
                ("preprint", "arXiv", f"PDF first page arXiv identifier {arxiv_id} ({revision})"),
            )
            clusters = sorted(set(assignment_clusters.get(entity["entity_id"], [])))
            papers.append(
                {
                    "checked_at": CHECKED_AT,
                    "code_links": code_links,
                    "code_search_note": "GitHub links were extracted from the opened PDF; canonical paper-code linkage still requires repository-side verification.",
                    "data_source_ids": [],
                    "evidence_role": "Deep mechanism/evaluation evidence for " + (", ".join(clusters) if clusters else "cross-cutting analysis"),
                    "identifier": identifier,
                    "publication_status": publication_status,
                    "revision": revision,
                    "source_id": source_id,
                    "status_locator": status_locator,
                    "venue": venue,
                }
            )
            paper_source_ids.add(source_id)
            created_cards += 1

    write_jsonl(BUNDLE / "entities.jsonl", entities)
    write_jsonl(BUNDLE / "sources.jsonl", sources)
    write_jsonl(BUNDLE / "papers.jsonl", papers)
    write_jsonl(BUNDLE / "stage_events.jsonl", stage_events)
    print(json.dumps({"papers": len(extractions), "promoted": promoted, "sources_created": created_sources, "cards_created": created_cards}))


if __name__ == "__main__":
    main()
