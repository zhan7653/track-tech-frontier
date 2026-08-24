import json
from pathlib import Path

bundle = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
path = bundle / "cluster_assignments.jsonl"
rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

for row in rows:
    if row["entity_id"] == "E-d5bdee2e8ed548a7b3e0":  # MIRIX
        row["membership"] = "bridge"
        row["confidence"] = "high"
        row["method"] = "deep PDF reclassification"
        row["rationale"] = "MIRIX uses specialized agents as internal memory managers for one user's memory types; it is adjacent worker-pipeline evidence, not peer Subagent shared-state evidence."
    elif row["entity_id"] == "E-0d6c7a9829c068231d6f":  # MAPLE
        if row["cluster_id"] == "SM-C08":
            row["cluster_id"] = "SM-C05"
        row["membership"] = "bridge"
        row["confidence"] = "high"
        row["method"] = "deep PDF reclassification"
        row["rationale"] = "MAPLE delegates extraction, storage and personalization to internal workers; its synthetic user-personalization study does not establish named Subagent retention semantics."
    elif row["entity_id"] == "E-73f73c532ad06bcc6187":  # TreeMem
        row["membership"] = "bridge"
        row["confidence"] = "high"
        row["method"] = "deep PDF reclassification"
        row["rationale"] = "TreeMem optimizes builder, summarizer and retrieval agents inside a memory-construction pipeline; it informs credit assignment but is not direct task-Subagent memory sharing."

path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")
print(json.dumps({"rows": len(rows), "reclassified_entities": 3}))
