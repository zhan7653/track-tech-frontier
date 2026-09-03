from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import compile_figure_prompt as target


def valid_spec() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "figure_id": "example-loop",
        "target_page": "reader/overview.md",
        "reader_question": "How does the state loop close?",
        "takeaway": "Input is refined upward and feedback returns to input.",
        "aspect_ratio": "16:9",
        "alignment": {
            "status": "approved",
            "confirmed_by": "user",
            "approved_summary": "A quiet two-tier loop.",
            "geometry": "One triangle with two internal strata.",
            "information_density": "One idea per stratum.",
            "symbol_budget": "At most one symbol per stratum.",
            "connector_plan": "One upward edge and one outer return edge.",
            "visible_text_plan": "Only the two layer labels.",
        },
        "layout": {
            "grammar": "two-tier stack",
            "reading_order": ["L1", "L2"],
            "composition": "L1 below L2",
            "routing": "one upward edge and one outer return edge",
        },
        "style": {
            "surface": "formal schematic",
            "palette": ["navy structure", "orange feedback"],
            "notes": [],
        },
        "nodes": [
            {"id": "L1", "label": "01 输入", "role": "base", "visual": "wide base", "evidence": ["overview#flow"]},
            {"id": "L2", "label": "02 学习", "role": "apex", "visual": "small apex", "evidence": ["overview#flow"]},
        ],
        "edges": [
            {"id": "E1", "source": "L1", "target": "L2", "semantic_type": "refinement", "visual": "up arrow", "evidence": ["overview#flow"], "label": ""},
            {"id": "E2", "source": "L2", "target": "L1", "semantic_type": "feedback", "visual": "outer return arrow", "evidence": ["overview#flow"], "label": ""},
        ],
        "visible_text_whitelist": ["01 输入", "02 学习"],
        "caption_only": [],
        "forbidden_edges": [],
        "negative_constraints": ["no extra edges", "no extra text"],
    }


class FigurePromptCompilerTests(unittest.TestCase):
    def test_compiles_valid_spec(self) -> None:
        spec = target.validate_spec(valid_spec())
        prompt = target.compile_prompt(spec)

        self.assertIn("L2 -> L1", prompt)
        self.assertIn('"01 输入"', prompt)
        self.assertIn("INTERNAL IDS ARE CONTROL TOKENS", prompt)

    def test_rejects_forbidden_required_edge(self) -> None:
        spec = valid_spec()
        spec["forbidden_edges"] = [{"source": "L2", "target": "L1", "reason": "wrong endpoint"}]

        with self.assertRaisesRegex(target.FigureSpecError, "forbidden edge is also required"):
            target.validate_spec(spec)

    def test_rejects_unapproved_visual_alignment(self) -> None:
        spec = valid_spec()
        spec["alignment"]["status"] = "pending"

        with self.assertRaisesRegex(target.FigureSpecError, "must be 'approved'"):
            target.validate_spec(spec)

    def test_cli_writes_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            output = root / "prompt.md"
            spec_path.write_text(json.dumps(valid_spec(), ensure_ascii=False), encoding="utf-8")

            result = target.main(["--spec", str(spec_path), "--output", str(output)])

            self.assertEqual(result, 0)
            self.assertIn("Required directed relationships", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
