#!/usr/bin/env python3
"""Validate a source-grounded figure spec and compile an image-generation prompt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class FigureSpecError(ValueError):
    pass


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FigureSpecError(f"{field} must be a non-empty string")
    return value.strip()


def require_string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "an array" if allow_empty else "a non-empty array"
        raise FigureSpecError(f"{field} must be {qualifier} of strings")
    result = [require_string(item, f"{field}[]") for item in value]
    if len(result) != len(set(result)):
        raise FigureSpecError(f"{field} contains duplicates")
    return result


def validate_spec(spec: Any) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise FigureSpecError("figure spec must be a JSON object")
    if spec.get("schema_version") != "1.0":
        raise FigureSpecError("schema_version must be '1.0'")

    for field in ("figure_id", "target_page", "reader_question", "takeaway", "aspect_ratio"):
        require_string(spec.get(field), field)

    alignment = spec.get("alignment")
    if not isinstance(alignment, dict):
        raise FigureSpecError("alignment must be an object")
    if alignment.get("status") != "approved":
        raise FigureSpecError("alignment.status must be 'approved' before prompt compilation or image generation")
    if alignment.get("confirmed_by") != "user":
        raise FigureSpecError("alignment.confirmed_by must be 'user'")
    for field in ("approved_summary", "geometry", "information_density", "symbol_budget", "connector_plan", "visible_text_plan"):
        require_string(alignment.get(field), f"alignment.{field}")

    layout = spec.get("layout")
    if not isinstance(layout, dict):
        raise FigureSpecError("layout must be an object")
    for field in ("grammar", "composition", "routing"):
        require_string(layout.get(field), f"layout.{field}")

    style = spec.get("style")
    if not isinstance(style, dict):
        raise FigureSpecError("style must be an object")
    require_string(style.get("surface"), "style.surface")
    require_string_list(style.get("palette"), "style.palette")
    require_string_list(style.get("notes", []), "style.notes", allow_empty=True)

    nodes = spec.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise FigureSpecError("nodes must be a non-empty array")
    node_ids: set[str] = set()
    node_labels: list[str] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise FigureSpecError(f"nodes[{index}] must be an object")
        node_id = require_string(node.get("id"), f"nodes[{index}].id")
        if node_id in node_ids:
            raise FigureSpecError(f"duplicate node id: {node_id}")
        node_ids.add(node_id)
        node_labels.append(require_string(node.get("label"), f"nodes[{index}].label"))
        require_string(node.get("role"), f"nodes[{index}].role")
        require_string(node.get("visual"), f"nodes[{index}].visual")
        require_string_list(node.get("evidence"), f"nodes[{index}].evidence")

    reading_order = require_string_list(layout.get("reading_order"), "layout.reading_order")
    unknown_order = [item for item in reading_order if item not in node_ids]
    if unknown_order:
        raise FigureSpecError(f"layout.reading_order contains unknown nodes: {', '.join(unknown_order)}")

    edges = spec.get("edges")
    if not isinstance(edges, list) or not edges:
        raise FigureSpecError("edges must be a non-empty array")
    edge_ids: set[str] = set()
    edge_pairs: set[tuple[str, str, str]] = set()
    edge_labels: list[str] = []
    normalized_edges: list[dict[str, Any]] = []
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise FigureSpecError(f"edges[{index}] must be an object")
        edge_id = require_string(edge.get("id"), f"edges[{index}].id")
        if edge_id in edge_ids or edge_id in node_ids:
            raise FigureSpecError(f"duplicate or colliding edge id: {edge_id}")
        edge_ids.add(edge_id)
        source = require_string(edge.get("source"), f"edges[{index}].source")
        target = require_string(edge.get("target"), f"edges[{index}].target")
        if source not in node_ids or target not in node_ids:
            raise FigureSpecError(f"edge {edge_id} has unknown endpoint: {source} -> {target}")
        if source == target:
            raise FigureSpecError(f"edge {edge_id} cannot be a self-loop")
        semantic_type = require_string(edge.get("semantic_type"), f"edges[{index}].semantic_type")
        pair = (source, target, semantic_type)
        if pair in edge_pairs:
            raise FigureSpecError(f"duplicate semantic edge: {source} -> {target} ({semantic_type})")
        edge_pairs.add(pair)
        require_string(edge.get("visual"), f"edges[{index}].visual")
        require_string_list(edge.get("evidence"), f"edges[{index}].evidence")
        label = edge.get("label", "")
        if not isinstance(label, str):
            raise FigureSpecError(f"edges[{index}].label must be a string")
        if label.strip():
            edge_labels.append(label.strip())
        normalized_edges.append(edge)

    forbidden_edges = spec.get("forbidden_edges", [])
    if not isinstance(forbidden_edges, list):
        raise FigureSpecError("forbidden_edges must be an array")
    for index, edge in enumerate(forbidden_edges):
        if not isinstance(edge, dict):
            raise FigureSpecError(f"forbidden_edges[{index}] must be an object")
        source = require_string(edge.get("source"), f"forbidden_edges[{index}].source")
        target = require_string(edge.get("target"), f"forbidden_edges[{index}].target")
        require_string(edge.get("reason"), f"forbidden_edges[{index}].reason")
        if source not in node_ids or target not in node_ids:
            raise FigureSpecError(f"forbidden edge has unknown endpoint: {source} -> {target}")
        if any(item["source"] == source and item["target"] == target for item in normalized_edges):
            raise FigureSpecError(f"forbidden edge is also required: {source} -> {target}")

    whitelist = require_string_list(spec.get("visible_text_whitelist"), "visible_text_whitelist")
    missing_labels = [label for label in node_labels + edge_labels if label not in whitelist]
    if missing_labels:
        raise FigureSpecError(f"visible labels missing from whitelist: {', '.join(missing_labels)}")

    require_string_list(spec.get("caption_only", []), "caption_only", allow_empty=True)
    require_string_list(spec.get("negative_constraints"), "negative_constraints")
    return spec


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def compile_prompt(spec: dict[str, Any]) -> str:
    layout = spec["layout"]
    style = spec["style"]
    nodes = spec["nodes"]
    edges = spec["edges"]
    forbidden = spec.get("forbidden_edges", [])
    node_lines = [
        f'- {node["id"]}: visible label "{node["label"]}"; role={node["role"]}; visual={node["visual"]}; evidence={" | ".join(node["evidence"])}'
        for node in nodes
    ]
    edge_lines = [
        f'- {edge["id"]}: {edge["source"]} -> {edge["target"]}; meaning={edge["semantic_type"]}; visual={edge["visual"]}; '
        f'label={json.dumps(edge.get("label", ""), ensure_ascii=False)}; evidence={" | ".join(edge["evidence"])}'
        for edge in edges
    ]
    forbidden_lines = [
        f'- NEVER draw {edge["source"]} -> {edge["target"]}: {edge["reason"]}' for edge in forbidden
    ] or ["- No additional or inferred edges are allowed."]
    caption_only = spec.get("caption_only", [])
    style_notes = style.get("notes", [])
    return f"""Use case: scientific-educational
Asset type: source-grounded architecture or mechanism figure for a technical research website
Figure ID: {spec['figure_id']}
Target page: {spec['target_page']}
Aspect ratio: {spec['aspect_ratio']}

Primary reader question: {spec['reader_question']}
Required first-glance takeaway: {spec['takeaway']}

USER-APPROVED VISUAL ALIGNMENT — DO NOT DEVIATE
Approved summary: {spec['alignment']['approved_summary']}
Geometry: {spec['alignment']['geometry']}
Information density: {spec['alignment']['information_density']}
Symbol budget: {spec['alignment']['symbol_budget']}
Connector plan: {spec['alignment']['connector_plan']}
Visible text plan: {spec['alignment']['visible_text_plan']}

SEMANTIC GRAPH CONTRACT — INTERNAL IDS ARE CONTROL TOKENS, NEVER VISIBLE TEXT
Nodes:
{chr(10).join(node_lines)}

Required directed relationships:
{chr(10).join(edge_lines)}

Forbidden relationships:
{chr(10).join(forbidden_lines)}

VISIBLE TEXT CONTRACT
Render only these strings, exactly once unless the visual contract explicitly requires repetition:
{bullet(spec['visible_text_whitelist'])}
Do not render node IDs, edge IDs, file paths, evidence anchors, schema keys, or audit language.

VISUAL RENDER CONTRACT
Layout grammar: {layout['grammar']}
Reading order: {' -> '.join(layout['reading_order'])}
Composition: {layout['composition']}
Connector routing: {layout['routing']}
Surface: {style['surface']}
Palette:
{bullet(style['palette'])}
Additional style rules:
{bullet(style_notes) if style_notes else '- No additional style rules.'}

CAPTION-ONLY INFORMATION — DO NOT DRAW AS TEXT OR PEER MODULES
{bullet(caption_only) if caption_only else '- None.'}

HARD NEGATIVE CONSTRAINTS
{bullet(spec['negative_constraints'])}

Final audit before rendering: exactly match the required nodes, directions, visible-text whitelist, layout grammar, and feedback endpoints. A visually attractive but semantically different figure is invalid.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="JSON figure specification")
    parser.add_argument("--output", type=Path, help="Compiled prompt path")
    parser.add_argument("--check", action="store_true", help="Validate without writing a prompt")
    args = parser.parse_args(argv)
    try:
        spec = validate_spec(json.loads(args.spec.read_text(encoding="utf-8")))
        if not args.check:
            if args.output is None:
                raise FigureSpecError("--output is required unless --check is used")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(compile_prompt(spec), encoding="utf-8", newline="\n")
        print(f"OK: {spec['figure_id']} nodes={len(spec['nodes'])} edges={len(spec['edges'])}")
        return 0
    except (OSError, json.JSONDecodeError, FigureSpecError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
