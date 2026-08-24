from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


BUNDLE = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
PDF_ROOT = BUNDLE / "tmp" / "pdfs" / "round-04"
OUTPUT_ROOT = BUNDLE / "work" / "round-04" / "extracted"
MANIFEST = BUNDLE / "work" / "round-04" / "extraction.jsonl"


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for pdf_path in sorted(PDF_ROOT.glob("*.pdf")):
        data = pdf_path.read_bytes()
        record: dict[str, object] = {
            "arxiv_id": pdf_path.stem,
            "pdf_path": str(pdf_path),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }
        try:
            reader = PdfReader(pdf_path)
            page_texts: list[str] = []
            empty_pages: list[int] = []
            for page_number, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                if not text.strip():
                    empty_pages.append(page_number)
                page_texts.append(f"\n\n===== PAGE {page_number} =====\n\n{text}")
            combined = "".join(page_texts)
            output_path = OUTPUT_ROOT / f"{pdf_path.stem}.txt"
            output_path.write_text(combined, encoding="utf-8")
            record.update(
                {
                    "status": "extracted",
                    "pages": len(reader.pages),
                    "empty_pages": empty_pages,
                    "text_chars": len(combined),
                    "text_path": str(output_path),
                    "metadata": {str(k): str(v) for k, v in (reader.metadata or {}).items()},
                }
            )
        except Exception as exc:  # preserve per-paper extraction failures
            record.update({"status": "failed", "error": repr(exc)})
        records.append(record)
    MANIFEST.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    extracted = sum(record.get("status") == "extracted" for record in records)
    print(json.dumps({"pdfs": len(records), "extracted": extracted, "failed": len(records) - extracted}))


if __name__ == "__main__":
    main()
