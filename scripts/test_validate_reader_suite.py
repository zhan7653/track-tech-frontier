from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_reader_suite


class ReaderSuiteValidationTests(unittest.TestCase):
    def _suite(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for relative in validate_reader_suite.REQUIRED_FILES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            body = f"# {path.stem}\n\n"
            for section in validate_reader_suite.REQUIRED_SECTIONS.get(relative, ()):
                body += f"## {section}\n\n完整内容。\n\n"
            path.write_text(body, encoding="utf-8")
        for directory in validate_reader_suite.REQUIRED_DIRECTORY_CONTENT:
            path = root / directory / "example.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Example\n\n完整内容。\n", encoding="utf-8")
        return temporary, root

    def test_valid_minimal_suite(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate_reader_suite.validate_reader_suite(root), [])

    def test_reports_broken_link_and_placeholder(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        overview = root / "reader" / "overview.md"
        overview.write_text(overview.read_text(encoding="utf-8") + "\nTODO [missing](absent.md)\n", encoding="utf-8")
        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(root)}
        self.assertIn("placeholder", codes)
        self.assertIn("broken-link", codes)

    def test_reports_internal_marker_and_bad_h1(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        project = root / "reader" / "projects" / "example.md"
        project.write_text("# One\n\n# Two\n\n<!-- claim:C001 -->\n", encoding="utf-8")
        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(root)}
        self.assertIn("h1-count", codes)
        self.assertIn("internal-marker", codes)

    def test_arxiv_link_must_exist_in_frozen_v09_sources(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        suite = root / "agent-memory-v10"
        suite.mkdir()
        for child in list(root.iterdir()):
            if child != suite:
                child.rename(suite / child.name)
        source_dir = root / "agent-memory-v09" / "bundle"
        source_dir.mkdir(parents=True)
        (source_dir / "sources.jsonl").write_text(
            '{"source_id":"S1","url":"https://arxiv.org/abs/2501.00001"}\n',
            encoding="utf-8",
        )
        overview = suite / "reader" / "overview.md"
        overview.write_text(
            overview.read_text(encoding="utf-8")
            + "\n[Wrong paper](https://arxiv.org/abs/2601.99999)\n",
            encoding="utf-8",
        )

        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(suite)}

        self.assertIn("unknown-arxiv", codes)


if __name__ == "__main__":
    unittest.main()
