from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import render_reader_html as target


class ReaderHtmlRendererTests(unittest.TestCase):
    def _suite(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "suite"
        output = Path(temporary.name) / "site"
        (root / "reader").mkdir(parents=True)
        (root / "README.md").write_text("# Suite\n\nAbout.\n", encoding="utf-8")
        (root / "reader" / "README.md").write_text(
            "# Reader entry\n\nStart here.\n\n[Overview](overview.md)\n",
            encoding="utf-8",
        )
        (root / "reader" / "overview.md").write_text(
            """# Technical overview

The report explains a mechanism.

## Flow

```mermaid
flowchart LR
  A[Input] --> B[State] --> C[Action]
```

## Comparison

| Route | Cost |
|---|---|
| Static | Low |

## Safety

<script>alert('no')</script>

[blocked](javascript:alert(1))

## Text diagram

    input --> state
             |
             v
           action
""",
            encoding="utf-8",
        )
        return temporary, root, output

    def test_builds_offline_site_and_search_index(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)

        manifest = target.build_site(root, output)

        self.assertEqual(manifest["page_count"], 3)
        self.assertTrue((output / "index.html").is_file())
        self.assertTrue((output / "overview.html").is_file())
        self.assertTrue((output / "assets" / "search-index.js").is_file())
        self.assertEqual(manifest["source_root"], ".")
        self.assertNotIn(str(root), json.dumps(manifest))

    def test_renders_mermaid_table_and_safe_markup(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)

        target.build_site(root, output)
        text = (output / "overview.html").read_text(encoding="utf-8")

        self.assertIn('class="flow-svg"', text)
        self.assertIn('class="diagram-details"', text)
        self.assertIn('class="table-toolbar"', text)
        self.assertIn('class="code-block ascii-diagram"', text)
        self.assertIn("input --&gt; state", text)
        self.assertIn("&lt;script&gt;alert", text)
        self.assertNotIn("<script>alert('no')</script>", text)
        self.assertIn('class="unsafe-link"', text)
        self.assertNotIn('href="javascript:', text)

    def test_rewrites_markdown_link_to_html(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)

        target.build_site(root, output)
        entry = (output / "index.html").read_text(encoding="utf-8")

        self.assertIn('href="overview.html"', entry)

    def test_duplicate_headings_receive_stable_suffixes(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        overview = root / "reader" / "overview.md"
        overview.write_text("# Page\n\n## Same\n\nA.\n\n## Same\n\nB.\n", encoding="utf-8")

        target.build_site(root, output)
        text = (output / "overview.html").read_text(encoding="utf-8")

        self.assertIn('id="same"', text)
        self.assertIn('id="same-2"', text)

    def test_broken_local_link_fails_the_build(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        overview = root / "reader" / "overview.md"
        overview.write_text(overview.read_text(encoding="utf-8") + "\n[Missing](missing.md)\n", encoding="utf-8")

        with self.assertRaisesRegex(target.RenderError, "broken local link"):
            target.build_site(root, output)

    def test_site_validator_rejects_dangerous_generated_scheme(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name)
        (output / "index.html").write_text(
            '<!doctype html><html><body><h1>One</h1><a href="data:text/html,bad">bad</a></body></html>',
            encoding="utf-8",
        )

        errors = target.validate_site(output)

        self.assertTrue(any("unsafe or unsupported scheme" in error for error in errors))

    def test_source_asset_cannot_override_renderer_javascript(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        asset = root / "reader" / "assets" / "site.js"
        asset.parent.mkdir(parents=True)
        asset.write_text("alert('override')", encoding="utf-8")
        overview = root / "reader" / "overview.md"
        overview.write_text(overview.read_text(encoding="utf-8") + "\n[asset](assets/site.js)\n", encoding="utf-8")

        with self.assertRaisesRegex(target.RenderError, "unsupported local asset type"):
            target.build_site(root, output)

    def test_passive_source_asset_is_copied_to_isolated_directory(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        asset = root / "reader" / "diagram.png"
        asset.write_bytes(b"not-a-real-png")
        overview = root / "reader" / "overview.md"
        overview.write_text(overview.read_text(encoding="utf-8") + "\n![diagram](diagram.png)\n", encoding="utf-8")

        manifest = target.build_site(root, output)

        copied = output / "assets" / "source" / "reader" / "diagram.png"
        self.assertEqual(copied.read_bytes(), b"not-a-real-png")
        self.assertEqual(manifest["copied_assets"][0]["output"], "assets/source/reader/diagram.png")

    def test_outside_workspace_link_becomes_non_clickable_and_manifested(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        external = root.parent / "external.md"
        external.write_text("# External\n", encoding="utf-8")
        overview = root / "reader" / "overview.md"
        overview.write_text(overview.read_text(encoding="utf-8") + "\n[external](../../external.md)\n", encoding="utf-8")

        manifest = target.build_site(root, output)
        rendered = (output / "overview.html").read_text(encoding="utf-8")

        self.assertIn('class="workspace-link"', rendered)
        self.assertNotIn('href="../../external.md"', rendered)
        self.assertEqual(manifest["workspace_only_link_count"], 1)
        self.assertFalse(any("escapes the standalone site" in error for error in target.validate_site(output)))

    def test_rebuild_removes_stale_page(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        obsolete = root / "reader" / "obsolete.md"
        obsolete.write_text("# Obsolete\n\nOld.\n", encoding="utf-8")
        target.build_site(root, output)
        self.assertTrue((output / "obsolete.html").is_file())

        obsolete.unlink()
        target.build_site(root, output)

        self.assertFalse((output / "obsolete.html").exists())
        self.assertEqual(target.validate_manifest(output, root), [])

    def test_manifest_check_detects_tampered_output_and_extra_file(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        target.build_site(root, output)
        (output / "overview.html").write_text("<h1>tampered</h1>", encoding="utf-8")
        (output / "stale.html").write_text("<h1>stale</h1>", encoding="utf-8")

        errors = target.validate_manifest(output, root)

        self.assertTrue(any("output hash mismatch" in error for error in errors))
        self.assertTrue(any("output set drift" in error for error in errors))

    def test_fragment_validation_rejects_missing_anchor(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        target.build_site(root, output)
        entry = output / "index.html"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace('href="overview.html"', 'href="overview.html#missing-anchor"', 1),
            encoding="utf-8",
        )

        errors = target.validate_site(output)

        self.assertTrue(any("missing fragment target" in error for error in errors))

    def test_refuses_to_replace_unowned_nonempty_output(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        output.mkdir()
        (output / "keep.txt").write_text("user data", encoding="utf-8")

        with self.assertRaisesRegex(target.RenderError, "refusing to replace"):
            target.build_site(root, output)

    def test_refuses_to_replace_owned_output_with_unmanifested_file(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        target.build_site(root, output)
        (output / "user-note.txt").write_text("do not delete", encoding="utf-8")

        with self.assertRaisesRegex(target.RenderError, "refusing to replace"):
            target.build_site(root, output)

    def test_rechecks_moved_backup_and_restores_concurrent_change(self) -> None:
        temporary, root, output = self._suite()
        self.addCleanup(temporary.cleanup)
        target.build_site(root, output)
        original = target._assert_replaceable
        calls = 0

        def inject_after_first_check(path: Path) -> None:
            nonlocal calls
            calls += 1
            original(path)
            if calls == 1:
                (output / "late-user-file.txt").write_text("preserve me", encoding="utf-8")

        with patch.object(target, "_assert_replaceable", side_effect=inject_after_first_check):
            with self.assertRaisesRegex(target.RenderError, "refusing to replace"):
                target.build_site(root, output)

        self.assertEqual((output / "late-user-file.txt").read_text(encoding="utf-8"), "preserve me")
        self.assertTrue((output / "index.html").is_file())
        self.assertFalse(any(output.parent.glob(f".{output.name}-backup-*")))


if __name__ == "__main__":
    unittest.main()
