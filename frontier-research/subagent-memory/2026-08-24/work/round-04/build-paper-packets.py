from __future__ import annotations

import json
import re
from pathlib import Path


BUNDLE = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
EXTRACTED = BUNDLE / "work" / "round-04" / "extracted"
PACKETS = BUNDLE / "work" / "round-04" / "paper-packets"
INDEX = BUNDLE / "work" / "round-04" / "paper-packet-index.jsonl"

HEADING = re.compile(
    r"(?im)^(?:\d+(?:\.\d+)*\s+)?(?:"
    r"method(?:ology)?|approach|architecture|system(?: design)?|framework|"
    r"implementation|evaluation|experiment(?:s|al setup)?|results?|"
    r"limitations?|discussion|conclusion|threats to validity|security analysis|"
    r"ablation(?: study)?|benchmark"
    r")[^\n]{0,120}$"
)


def compact(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> None:
    PACKETS.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for path in sorted(EXTRACTED.glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = list(HEADING.finditer(text))
        selected: list[re.Match[str]] = []
        seen_families: set[str] = set()
        for match in matches:
            label = match.group(0).lower()
            family = next(
                (name for name in ("method", "approach", "architecture", "framework", "implementation", "evaluation", "experiment", "result", "limitation", "discussion", "conclusion", "threat", "security", "ablation", "benchmark") if name in label),
                label,
            )
            if family in seen_families:
                continue
            seen_families.add(family)
            selected.append(match)
            if len(selected) >= 8:
                break

        front = compact(text[:7000])
        chunks = [f"# {path.stem}\n\n## Front matter and abstract\n\n{front}"]
        headings: list[str] = []
        for match in selected:
            heading = compact(match.group(0))
            headings.append(heading)
            end = min(len(text), match.start() + 4500)
            chunks.append(f"\n\n## Extract around: {heading}\n\n{compact(text[match.start():end])}")

        packet = PACKETS / f"{path.stem}.md"
        packet.write_text("".join(chunks), encoding="utf-8")
        records.append(
            {
                "arxiv_id": path.stem,
                "source_text": str(path),
                "packet": str(packet),
                "headings": headings,
                "packet_chars": packet.stat().st_size,
            }
        )
    INDEX.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    print(json.dumps({"packets": len(records), "index": str(INDEX)}))


if __name__ == "__main__":
    main()
