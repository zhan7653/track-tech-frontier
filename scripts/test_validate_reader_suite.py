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
            if directory == "reader/mechanisms":
                body = (
                    "# Example\n\n"
                    "## 方案与数据流\n\n"
                    + "### 方案一\n\n实现、成本、失败与最新研究。\n\n"
                    + "### 方案二\n\n具体机制。\n\n"
                    + "### 方案三\n\n具体机制。\n\n"
                    + "### 方案四\n\n具体机制。\n\n"
                )
                path.write_text(body, encoding="utf-8")
            else:
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

    def test_arxiv_link_can_be_registered_in_version_audit_sources(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        suite = root / "agent-memory-v10"
        suite.mkdir()
        for child in list(root.iterdir()):
            if child != suite:
                child.rename(suite / child.name)
        audit = suite / "audit"
        (audit / "sources.jsonl").write_text(
            '{"source_id":"D1","url":"https://arxiv.org/abs/2606.06448"}\n',
            encoding="utf-8",
        )
        overview = suite / "reader" / "overview.md"
        overview.write_text(
            overview.read_text(encoding="utf-8")
            + "\n[New evidence](https://arxiv.org/abs/2606.06448)\n",
            encoding="utf-8",
        )

        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(suite)}

        self.assertNotIn("unknown-arxiv", codes)

    def test_rejects_shallow_mechanism_outline(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        mechanism = root / "reader" / "mechanisms" / "example.md"
        mechanism.write_text("# Thin\n\n## 方案\n\n只有一张表和几句话。\n", encoding="utf-8")

        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(root)}

        self.assertIn("shallow-mechanism", codes)

    def test_requires_all_mechanism_deep_pages(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        manifest = root / validate_reader_suite.BRANCH_PACKAGE_MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            '{"packages":[{"branch":"example","entry":"reader/mechanisms/example.md",'
            '"deep_pages":["reader/mechanisms/example/missing.md"]}]}',
            encoding="utf-8",
        )

        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(root)}

        self.assertIn("missing-deep-page", codes)

    def test_requires_branch_entry_to_link_declared_deep_page(self) -> None:
        temporary, root = self._suite()
        self.addCleanup(temporary.cleanup)
        deep_page = root / "reader" / "mechanisms" / "example" / "mechanism.md"
        deep_page.parent.mkdir(parents=True, exist_ok=True)
        deep_page.write_text("# Mechanism\n\n完整分析。\n", encoding="utf-8")
        manifest = root / validate_reader_suite.BRANCH_PACKAGE_MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            '{"packages":[{"branch":"example","entry":"reader/mechanisms/example.md",'
            '"deep_pages":["reader/mechanisms/example/mechanism.md"]}]}',
            encoding="utf-8",
        )

        codes = {finding.code for finding in validate_reader_suite.validate_reader_suite(root)}

        self.assertIn("unlinked-deep-page", codes)


if __name__ == "__main__":
    unittest.main()
