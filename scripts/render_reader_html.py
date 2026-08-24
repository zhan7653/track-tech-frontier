#!/usr/bin/env python3
"""Render a Track Tech Frontier reader suite as a static, offline HTML site.

The renderer intentionally supports the Markdown subset used by the repository's
reader suites. It escapes raw HTML, rewrites known relative links, generates a
small build-time search index, and renders the current Mermaid flowchart subset
to accessible SVG. Unsupported constructs remain visible as source text and are
reported in the build manifest rather than being silently discarded.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlsplit, urlunsplit


ASSET_DIRECTORY = Path(__file__).with_name("html_assets")
SAFE_SCHEMES = {"http", "https", "mailto"}
SAFE_ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".pdf", ".txt", ".csv", ".json", ".jsonl"}
GENERATOR_ID = "track-tech-frontier/render_reader_html.py"
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^(\s*)([-+*]|\d+[.)])\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`]*)?.*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CHINESE_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_+./:-]*")


class RenderError(Exception):
    """A deterministic, user-actionable rendering failure."""


@dataclass
class Heading:
    level: int
    text: str
    anchor: str


@dataclass
class SearchSection:
    title: str
    anchor: str
    text: str


@dataclass
class Page:
    source: Path
    relative_source: Path
    output: Path
    title: str
    description: str
    page_type: str
    page_type_label: str
    reading_minutes: int
    raw: str
    headings: list[Heading] = field(default_factory=list)
    sections: list[SearchSection] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    workspace_links: list[str] = field(default_factory=list)


@dataclass
class ListItem:
    content: str
    children: list["ListBlock"] = field(default_factory=list)


@dataclass
class ListBlock:
    ordered: bool
    items: list[ListItem]


@dataclass
class FlowNode:
    node_id: str
    label: str
    detail: str = ""
    group_id: str | None = None
    order: int = 0


@dataclass
class FlowEdge:
    source: str
    target: str
    label: str = ""
    dotted: bool = False


@dataclass
class FlowGroup:
    group_id: str
    label: str
    members: list[str] = field(default_factory=list)
    order: int = 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain_inline(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value)
    return html.unescape(value).strip()


def slugify(value: str) -> str:
    value = plain_inline(value).casefold()
    pieces: list[str] = []
    pending_dash = False
    for character in value:
        category = unicodedata.category(character)
        if character.isalnum() or category.startswith("L"):
            if pending_dash and pieces:
                pieces.append("-")
            pieces.append(character)
            pending_dash = False
        elif character in {"-", "_", " ", "/", ":"}:
            pending_dash = True
    slug = "".join(pieces).strip("-")
    return slug or "section"


def reading_minutes(text: str) -> int:
    text = COMMENT_RE.sub("", text)
    chinese = len(CHINESE_RE.findall(text))
    words = len(WORD_RE.findall(text))
    return max(1, math.ceil(chinese / 420 + words / 220))


def extract_title(raw: str, fallback: str) -> str:
    for line in raw.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return plain_inline(match.group(1))
    return fallback


def extract_description(raw: str) -> str:
    paragraph: list[str] = []
    in_fence = False
    for line in raw.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip() or line.startswith("#") or line.startswith("<!--"):
            if paragraph:
                break
            continue
        if LIST_RE.match(line) or line.lstrip().startswith((">", "|")):
            if paragraph:
                break
            continue
        paragraph.append(line.strip())
        if len(" ".join(paragraph)) >= 180:
            break
    description = plain_inline(" ".join(paragraph))
    return description[:220].rstrip("，,；;。 ") + ("。" if description else "")


def classify_page(relative: Path) -> tuple[str, str]:
    parts = relative.as_posix().split("/")
    name = relative.stem
    if relative.as_posix() == "reader/README.md":
        return "landing", "阅读入口"
    if relative.as_posix() == "README.md":
        return "about", "研究套件"
    if parts[0] == "audit":
        return "audit", "审计材料"
    if "mechanisms" in parts:
        return "mechanism", "技术机制"
    if "scenarios" in parts or name == "scenarios":
        return "scenario", "场景视图"
    if "projects" in parts:
        return "project", "工程案例"
    if "cross-cutting" in parts:
        return "cross-cutting", "横切问题"
    labels = {
        "overview": ("overview", "领域总览"),
        "architecture": ("architecture", "架构模型"),
        "solution-landscape": ("landscape", "方案全景"),
        "trends": ("trends", "近期变化"),
        "github-radar": ("radar", "GitHub 雷达"),
        "consensus-and-open-questions": ("consensus", "共识与问题"),
        "method-and-scope": ("method", "方法与范围"),
        "human-review": ("review", "人工评审"),
        "adjacent-boundaries": ("boundary", "相邻边界"),
    }
    return labels.get(name, ("report", "专题报告"))


def output_path(relative: Path) -> Path:
    posix = relative.as_posix()
    if posix == "reader/README.md":
        return Path("index.html")
    if posix == "README.md":
        return Path("about.html")
    if posix.startswith("reader/"):
        relative = Path(*relative.parts[1:])
    if relative.name == "README.md":
        return relative.parent / "index.html"
    return relative.with_suffix(".html")


def discover_pages(root: Path, output: Path) -> list[Page]:
    candidates: list[Path] = []
    if (root / "README.md").is_file():
        candidates.append(root / "README.md")
    for directory in (root / "reader", root / "audit"):
        if directory.is_dir():
            candidates.extend(sorted(directory.rglob("*.md")))
    pages: list[Page] = []
    for source in candidates:
        if output == source or output in source.parents:
            continue
        raw_bytes = source.read_bytes()
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            raise RenderError(f"UTF-8 BOM is not allowed: {source}")
        try:
            raw = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise RenderError(f"invalid UTF-8 in {source}: {error}") from error
        if "\ufffd" in raw:
            raise RenderError(f"replacement character found in {source}")
        relative = source.relative_to(root)
        kind, label = classify_page(relative)
        pages.append(
            Page(
                source=source,
                relative_source=relative,
                output=output_path(relative),
                title=extract_title(raw, source.stem),
                description=extract_description(raw),
                page_type=kind,
                page_type_label=label,
                reading_minutes=reading_minutes(raw),
                raw=raw,
            )
        )
    if not any(page.page_type == "landing" for page in pages):
        raise RenderError(f"reader/README.md is required under {root}")
    outputs = [page.output for page in pages]
    if len(outputs) != len(set(outputs)):
        raise RenderError("multiple Markdown pages map to the same HTML output path")
    return pages


def split_table_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in value:
        if character == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        escaped = character == "\\" and not escaped
        if character != "\\":
            escaped = False
    cells.append("".join(current).strip())
    return cells


def parse_list_records(lines: list[str]) -> ListBlock:
    records: list[tuple[int, bool, str]] = []
    for line in lines:
        match = LIST_RE.match(line)
        if not match:
            continue
        indent = len(match.group(1).expandtabs(4))
        ordered = match.group(2)[0].isdigit()
        records.append((indent, ordered, match.group(3)))

    def parse_from(index: int, indent: int, ordered: bool) -> tuple[ListBlock, int]:
        block = ListBlock(ordered=ordered, items=[])
        while index < len(records):
            item_indent, item_ordered, content = records[index]
            if item_indent < indent:
                break
            if item_indent > indent:
                if not block.items:
                    break
                child, index = parse_from(index, item_indent, item_ordered)
                block.items[-1].children.append(child)
                continue
            if item_ordered != ordered and block.items:
                break
            block.items.append(ListItem(content=content))
            index += 1
        return block, index

    if not records:
        return ListBlock(False, [])
    block, _ = parse_from(0, records[0][0], records[0][1])
    return block


def flow_endpoint_ids(value: str) -> list[str]:
    identifiers: list[str] = []
    for part in re.split(r"\s*&\s*", value.strip()):
        match = re.match(r"^([A-Za-z_][\w-]*)", part.strip())
        if match:
            identifiers.append(match.group(1))
    return identifiers


def flow_label(value: str, node_id: str) -> str:
    value = value.strip()
    patterns = (
        rf"^{re.escape(node_id)}\s*\[\s*\"(.*?)\"\s*\]$",
        rf"^{re.escape(node_id)}\s*\[(.*?)\]$",
        rf"^{re.escape(node_id)}\s*\(\[(.*?)\]\)$",
        rf"^{re.escape(node_id)}\s*\(\((.*?)\)\)$",
        rf"^{re.escape(node_id)}\s*\((.*?)\)$",
        rf"^{re.escape(node_id)}\s*\{{(.*?)\}}$",
    )
    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            return match.group(1).strip(' "').replace("\\n", " · ")
    return node_id


def parse_flowchart(source: str) -> tuple[str, dict[str, FlowNode], list[FlowEdge], dict[str, FlowGroup], list[str]]:
    direction = "LR"
    nodes: dict[str, FlowNode] = {}
    edges: list[FlowEdge] = []
    groups: dict[str, FlowGroup] = {}
    warnings: list[str] = []
    current_group: str | None = None
    order = 0

    def ensure_node(raw: str) -> str | None:
        nonlocal order
        ids = flow_endpoint_ids(raw)
        if not ids:
            return None
        node_id = ids[0]
        label = flow_label(raw.strip(), node_id)
        if node_id not in nodes:
            nodes[node_id] = FlowNode(node_id=node_id, label=label, group_id=current_group, order=order)
            order += 1
        elif label != node_id:
            nodes[node_id].label = label
        if current_group and node_id not in groups[current_group].members:
            groups[current_group].members.append(node_id)
            nodes[node_id].group_id = current_group
        return node_id

    operator_re = re.compile(r"\s*(-->|==>|---|-\.(.*?)\.->)\s*")
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        header = re.match(r"^(?:flowchart|graph)\s+(LR|RL|TB|TD|BT)\b", line, re.I)
        if header:
            direction = header.group(1).upper().replace("TD", "TB")
            continue
        group_match = re.match(r'^subgraph\s+([A-Za-z_][\w-]*)(?:\s*\[\"?(.*?)\"?\])?$', line)
        if group_match:
            group_id = group_match.group(1)
            label = (group_match.group(2) or group_id).strip(' "')
            groups[group_id] = FlowGroup(group_id=group_id, label=label, order=order)
            order += 1
            current_group = group_id
            continue
        if line == "end":
            current_group = None
            continue
        matches = list(operator_re.finditer(line))
        if matches:
            pieces: list[str] = []
            last = 0
            for match in matches:
                pieces.append(line[last : match.start()].strip())
                pieces.append(match.group(1))
                last = match.end()
            pieces.append(line[last:].strip())
            for index in range(0, len(pieces) - 2, 2):
                left, operator, right = pieces[index], pieces[index + 1], pieces[index + 2]
                left_ids = flow_endpoint_ids(left)
                right_ids = flow_endpoint_ids(right)
                for endpoint in re.split(r"\s*&\s*", left):
                    ensure_node(endpoint)
                for endpoint in re.split(r"\s*&\s*", right):
                    ensure_node(endpoint)
                label_match = re.match(r"-\.(.*?)\.->", operator)
                edge_label = label_match.group(1) if label_match else ""
                for source_id in left_ids:
                    for target_id in right_ids:
                        edges.append(FlowEdge(source_id, target_id, edge_label, operator.startswith("-.")))
            continue
        if re.match(r"^[A-Za-z_][\w-]*(?:\s*[\[({])", line):
            ensure_node(line)
        else:
            warnings.append(f"unsupported Mermaid statement: {line[:120]}")
    return direction, nodes, edges, groups, warnings


def wrap_label(value: str, limit: int = 18, max_lines: int = 4) -> list[str]:
    value = value.replace("<br/>", " ").replace("<br>", " ").strip()
    if not value:
        return [""]
    words = value.split()
    if len(words) == 1 and len(value) > limit:
        lines = [value[index : index + limit] for index in range(0, len(value), limit)]
    else:
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > limit:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max(1, limit - 1)] + "…"
    return lines


def render_flowchart(source: str, diagram_id: str) -> tuple[str, list[str]]:
    direction, nodes, edges, groups, warnings = parse_flowchart(source)
    if not nodes:
        escaped = html.escape(source)
        return f'<pre class="mermaid-fallback"><code>{escaped}</code></pre>', warnings + ["Mermaid diagram contained no parseable nodes"]

    display_nodes: dict[str, FlowNode] = {}
    membership = {member: group_id for group_id, group in groups.items() for member in group.members}
    if groups:
        for group_id, group in groups.items():
            detail = " · ".join(nodes[item].label for item in group.members if item in nodes)
            display_nodes[group_id] = FlowNode(group_id, group.label, detail, order=group.order)
        for node_id, node in nodes.items():
            if node_id not in membership and node_id not in groups:
                display_nodes[node_id] = node
    else:
        display_nodes = dict(nodes)

    display_edges: list[FlowEdge] = []
    seen_edges: set[tuple[str, str, str, bool]] = set()
    for edge in edges:
        source_id = membership.get(edge.source, edge.source)
        target_id = membership.get(edge.target, edge.target)
        if source_id == target_id or source_id not in display_nodes or target_id not in display_nodes:
            continue
        key = (source_id, target_id, edge.label, edge.dotted)
        if key not in seen_edges:
            display_edges.append(FlowEdge(*key))
            seen_edges.add(key)

    ordered = sorted(display_nodes.values(), key=lambda item: (item.order, item.node_id))
    order_index = {node.node_id: index for index, node in enumerate(ordered)}
    levels = {node.node_id: 0 for node in ordered}
    for node in ordered:
        incoming = [edge for edge in display_edges if edge.target == node.node_id and order_index.get(edge.source, 0) < order_index[node.node_id]]
        if incoming:
            levels[node.node_id] = max(levels.get(edge.source, 0) + 1 for edge in incoming)
    if direction in {"RL", "BT"}:
        maximum = max(levels.values(), default=0)
        levels = {key: maximum - value for key, value in levels.items()}

    columns: dict[int, list[FlowNode]] = {}
    for node in ordered:
        columns.setdefault(levels[node.node_id], []).append(node)
    horizontal = direction in {"LR", "RL"}
    node_width = 220
    base_height = 72
    level_gap = 86
    lane_gap = 34
    margin = 40
    positions: dict[str, tuple[float, float, float, float]] = {}
    max_items = max((len(items) for items in columns.values()), default=1)
    max_level = max(columns, default=0)
    if horizontal:
        width = margin * 2 + (max_level + 1) * node_width + max_level * level_gap
        height = margin * 2 + max_items * base_height + max(0, max_items - 1) * lane_gap
        for level, items in columns.items():
            column_height = len(items) * base_height + max(0, len(items) - 1) * lane_gap
            y0 = margin + (height - 2 * margin - column_height) / 2
            x = margin + level * (node_width + level_gap)
            for index, node in enumerate(items):
                positions[node.node_id] = (x, y0 + index * (base_height + lane_gap), node_width, base_height)
    else:
        row_width = max_items * node_width + max(0, max_items - 1) * lane_gap
        width = margin * 2 + row_width
        height = margin * 2 + (max_level + 1) * base_height + max_level * level_gap
        for level, items in columns.items():
            current_width = len(items) * node_width + max(0, len(items) - 1) * lane_gap
            x0 = margin + (width - 2 * margin - current_width) / 2
            y = margin + level * (base_height + level_gap)
            for index, node in enumerate(items):
                positions[node.node_id] = (x0 + index * (node_width + lane_gap), y, node_width, base_height)

    width = max(width, 420)
    height = max(height, 220)
    marker_id = f"arrow-{diagram_id}"
    svg: list[str] = [
        f'<svg class="flow-svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-labelledby="{diagram_id}-title {diagram_id}-desc">',
        f'<title id="{diagram_id}-title">技术流程图</title>',
        f'<desc id="{diagram_id}-desc">{len(display_nodes)} 个对象，{len(display_edges)} 条连接。图后提供文本列表。</desc>',
        '<defs>',
        f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" /></marker>',
        '</defs>',
    ]
    for edge in display_edges:
        sx, sy, sw, sh = positions[edge.source]
        tx, ty, tw, th = positions[edge.target]
        if horizontal:
            start_x, start_y = sx + sw, sy + sh / 2
            end_x, end_y = tx, ty + th / 2
            control = max(28, abs(end_x - start_x) * 0.44)
            path = f"M {start_x:.1f} {start_y:.1f} C {start_x + control:.1f} {start_y:.1f}, {end_x - control:.1f} {end_y:.1f}, {end_x:.1f} {end_y:.1f}"
        else:
            start_x, start_y = sx + sw / 2, sy + sh
            end_x, end_y = tx + tw / 2, ty
            control = max(28, abs(end_y - start_y) * 0.44)
            path = f"M {start_x:.1f} {start_y:.1f} C {start_x:.1f} {start_y + control:.1f}, {end_x:.1f} {end_y - control:.1f}, {end_x:.1f} {end_y:.1f}"
        dash = ' stroke-dasharray="7 6"' if edge.dotted else ""
        svg.append(f'<path class="flow-edge" d="{path}" marker-end="url(#{marker_id})"{dash} />')
        if edge.label:
            label_x = (start_x + end_x) / 2
            label_y = (start_y + end_y) / 2 - 6
            svg.append(f'<text class="flow-edge-label" x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="middle">{html.escape(edge.label)}</text>')
    for node in ordered:
        x, y, node_w, node_h = positions[node.node_id]
        lines = wrap_label(node.label, 18 if horizontal else 22, 3)
        text_y = y + node_h / 2 - (len(lines) - 1) * 9
        detail = node.detail or node.label
        svg.append(
            f'<g class="flow-node" tabindex="0" role="button" data-label="{html.escape(node.label, quote=True)}" data-detail="{html.escape(detail, quote=True)}" transform="translate({x:.1f} {y:.1f})">'
        )
        svg.append(f'<rect width="{node_w}" height="{node_h}" rx="16" />')
        svg.append(f'<circle class="flow-node-dot" cx="18" cy="18" r="4" />')
        svg.append(f'<text x="{node_w / 2:.1f}" y="{text_y - y:.1f}" text-anchor="middle">')
        for index, line in enumerate(lines):
            dy = "0" if index == 0 else "18"
            svg.append(f'<tspan x="{node_w / 2:.1f}" dy="{dy}">{html.escape(line)}</tspan>')
        svg.append("</text></g>")
    svg.append("</svg>")

    details: list[str] = ['<details class="diagram-details"><summary>用文字检查图中对象与连接</summary><div class="diagram-detail-grid">']
    details.append('<section><h4>对象</h4><dl>')
    for node in ordered:
        details.append(f'<dt>{html.escape(node.label)}</dt><dd>{html.escape(node.detail or "流程节点")}</dd>')
    details.append('</dl></section><section><h4>连接</h4><ol>')
    for edge in display_edges:
        source_label = display_nodes[edge.source].label
        target_label = display_nodes[edge.target].label
        relation = f"（{edge.label}）" if edge.label else ""
        details.append(f'<li>{html.escape(source_label)} → {html.escape(target_label)}{html.escape(relation)}</li>')
    details.append('</ol></section></div><details class="diagram-source"><summary>查看 Mermaid 源码</summary>')
    details.append(f'<pre><code>{html.escape(source)}</code></pre></details></details>')
    figure = (
        f'<figure class="flow-figure" id="{diagram_id}"><div class="diagram-canvas">{"".join(svg)}</div>'
        '<figcaption><span class="diagram-live" aria-live="polite">选择图中对象可查看它在流程中的含义。</span></figcaption>'
        f'{"".join(details)}</figure>'
    )
    return figure, warnings


class MarkdownRenderer:
    def __init__(self, page: Page, root: Path, destination_root: Path, source_map: dict[Path, Path]):
        self.page = page
        self.root = root
        self.destination_root = destination_root
        self.source_map = source_map
        self.used_anchors: dict[str, int] = {}
        self.assets: set[tuple[Path, Path]] = set()
        self.diagram_count = 0

    def anchor(self, title: str) -> str:
        base = slugify(title)
        count = self.used_anchors.get(base, 0)
        self.used_anchors[base] = count + 1
        return base if count == 0 else f"{base}-{count + 1}"

    def relative_href(self, target_output: Path, fragment: str = "") -> str:
        current = (self.destination_root / self.page.output).parent
        target = self.destination_root / target_output
        value = Path(os.path.relpath(target, current)).as_posix()
        return value + (f"#{fragment}" if fragment else "")

    def rewrite_target(self, target: str) -> tuple[str | None, str]:
        target = html.unescape(target.strip())
        if not target:
            return None, "broken"
        parsed = urlsplit(target)
        scheme = parsed.scheme.casefold()
        if scheme:
            if scheme not in SAFE_SCHEMES:
                self.page.warnings.append(f"blocked unsafe URL scheme: {target}")
                return None, "unsafe"
            return target, "external"
        if target.startswith("#"):
            return target, "anchor"
        decoded_path = unquote(parsed.path)
        resolved = (self.page.source.parent / decoded_path).resolve()
        candidate = resolved
        if resolved.is_dir() and (resolved / "README.md") in self.source_map:
            candidate = resolved / "README.md"
        if candidate.suffix.casefold() == ".md" and candidate in self.source_map:
            return self.relative_href(self.source_map[candidate], parsed.fragment), "internal"
        if candidate.exists():
            try:
                relative = candidate.relative_to(self.root)
            except ValueError:
                self.page.workspace_links.append(target)
                return None, "workspace"
            if candidate.is_dir():
                self.page.workspace_links.append(target)
                return None, "workspace"
            published_roots = (self.root / "reader", self.root / "audit")
            if not any(_inside(candidate, published_root) for published_root in published_roots):
                self.page.workspace_links.append(target)
                return None, "workspace"
            if candidate.suffix.casefold() not in SAFE_ASSET_SUFFIXES:
                raise RenderError(
                    f"unsupported local asset type in {self.page.relative_source}: {target}; "
                    f"allowed: {', '.join(sorted(SAFE_ASSET_SUFFIXES))}"
                )
            destination = Path("assets") / "source" / relative
            self.assets.add((candidate, self.destination_root / destination))
            return self.relative_href(destination, parsed.fragment), "asset"
        self.page.warnings.append(f"unresolved local link: {target}")
        return target, "broken"

    def inline(self, value: str) -> str:
        tokens: list[str] = []

        def stash(rendered: str) -> str:
            token = f"@@FRONTIERHTML{len(tokens)}@@"
            tokens.append(rendered)
            return token

        def code_replace(match: re.Match[str]) -> str:
            return stash(f'<code>{html.escape(match.group(1))}</code>')

        value = re.sub(r"`([^`]+)`", code_replace, value)

        def image_replace(match: re.Match[str]) -> str:
            alt, target = match.group(1), match.group(2)
            href, kind = self.rewrite_target(target)
            if href is None:
                if kind == "workspace":
                    return stash(f'<span class="workspace-link" title="仅在源工作区可用">{html.escape(alt or "工作区图片")}</span>')
                return stash(f'<span class="unsafe-link">{html.escape(alt or "图片")}</span>')
            return stash(f'<img src="{html.escape(href, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="lazy" data-link-kind="{kind}">')

        value = IMAGE_RE.sub(image_replace, value)

        def link_replace(match: re.Match[str]) -> str:
            label, target = match.group(1), match.group(2)
            href, kind = self.rewrite_target(target)
            safe_label = html.escape(plain_inline(label))
            if href is None:
                if kind == "workspace":
                    return stash(f'<span class="workspace-link" title="仅在源工作区可用：{html.escape(target, quote=True)}">{safe_label}<small>（源工作区）</small></span>')
                return stash(f'<span class="unsafe-link" title="已阻止不安全链接">{safe_label}</span>')
            attributes = [f'href="{html.escape(href, quote=True)}"', f'data-link-kind="{kind}"']
            if kind == "external":
                attributes.extend(('target="_blank"', 'rel="noopener noreferrer"'))
            return stash(f'<a {" ".join(attributes)}>{safe_label}</a>')

        value = MARKDOWN_LINK_RE.sub(link_replace, value)
        value = html.escape(value, quote=False)
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        value = re.sub(r"__(.+?)__", r"<strong>\1</strong>", value)
        value = re.sub(r"~~(.+?)~~", r"<del>\1</del>", value)
        value = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", value)
        for index, rendered in enumerate(tokens):
            value = value.replace(f"@@FRONTIERHTML{index}@@", rendered)
        return value

    def render_list(self, block: ListBlock) -> str:
        tag = "ol" if block.ordered else "ul"
        lines = [f"<{tag}>"]
        for item in block.items:
            lines.append(f"<li>{self.inline(item.content)}")
            for child in item.children:
                lines.append(self.render_list(child))
            lines.append("</li>")
        lines.append(f"</{tag}>")
        return "".join(lines)

    def starts_block(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        if not line.strip():
            return True
        if HEADING_RE.match(line) or FENCE_RE.match(line) or LIST_RE.match(line):
            return True
        if line.lstrip().startswith((">", "<!--")):
            return True
        if line.startswith("    ") or line.startswith("\t"):
            return True
        if re.match(r"^\s*(?:---+|\*\*\*+)\s*$", line):
            return True
        if index + 1 < len(lines) and "|" in line and TABLE_SEPARATOR_RE.match(lines[index + 1]):
            return True
        return False

    def render(self) -> str:
        lines = self.page.raw.splitlines()
        output: list[str] = []
        index = 0
        first_h1_skipped = False
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            if line.lstrip().startswith("<!--"):
                while index < len(lines) and "-->" not in lines[index]:
                    index += 1
                index += 1
                continue
            fence = FENCE_RE.match(line)
            if fence:
                marker, language = fence.group(1), (fence.group(2) or "text").casefold()
                index += 1
                contents: list[str] = []
                while index < len(lines) and not lines[index].lstrip().startswith(marker[0] * len(marker)):
                    contents.append(lines[index])
                    index += 1
                if index >= len(lines):
                    self.page.warnings.append(f"unclosed {language} code fence")
                else:
                    index += 1
                source = "\n".join(contents)
                if language == "mermaid":
                    self.diagram_count += 1
                    diagram, warnings = render_flowchart(source, f"diagram-{self.diagram_count}")
                    output.append(diagram)
                    self.page.warnings.extend(warnings)
                else:
                    label = language or "text"
                    output.append(
                        '<figure class="code-block">'
                        f'<figcaption><span>{html.escape(label)}</span><button type="button" class="copy-code">复制</button></figcaption>'
                        f'<pre><code class="language-{html.escape(label, quote=True)}">{html.escape(source)}</code></pre></figure>'
                    )
                continue
            heading = HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                title = plain_inline(heading.group(2))
                anchor = self.anchor(title)
                if level == 1 and not first_h1_skipped:
                    first_h1_skipped = True
                    index += 1
                    continue
                if level == 1:
                    level = 2
                    self.page.warnings.append("additional H1 demoted to H2")
                self.page.headings.append(Heading(level, title, anchor))
                output.append(f'<h{level} id="{html.escape(anchor, quote=True)}"><a class="heading-anchor" href="#{html.escape(anchor, quote=True)}" aria-label="链接到本节">#</a>{self.inline(heading.group(2))}</h{level}>')
                index += 1
                continue
            if re.match(r"^\s*(?:---+|\*\*\*+)\s*$", line):
                output.append("<hr>")
                index += 1
                continue
            if line.startswith("    ") or line.startswith("\t"):
                code_lines: list[str] = []
                while index < len(lines):
                    current = lines[index]
                    if current.startswith("    "):
                        code_lines.append(current[4:])
                    elif current.startswith("\t"):
                        code_lines.append(current[1:])
                    elif not current.strip() and index + 1 < len(lines) and (
                        lines[index + 1].startswith("    ") or lines[index + 1].startswith("\t")
                    ):
                        code_lines.append("")
                    else:
                        break
                    index += 1
                source = "\n".join(code_lines).rstrip()
                output.append(
                    '<figure class="code-block ascii-diagram">'
                    '<figcaption><span>结构示意 · text</span><button type="button" class="copy-code">复制</button></figcaption>'
                    f'<pre><code class="language-text">{html.escape(source)}</code></pre></figure>'
                )
                continue
            if index + 1 < len(lines) and "|" in line and TABLE_SEPARATOR_RE.match(lines[index + 1]):
                headers = split_table_row(line)
                index += 2
                rows: list[list[str]] = []
                while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                    rows.append(split_table_row(lines[index]))
                    index += 1
                table: list[str] = [
                    '<div class="table-frame">'
                    f'<div class="table-toolbar"><span>Comparison · {len(headers)} 列</span><small>横向滚动 · 点击一行聚焦</small></div>'
                    '<div class="table-wrap" tabindex="0" role="region" aria-label="可横向滚动的比较表"><table><thead><tr>'
                ]
                table.extend(f"<th scope=\"col\">{self.inline(cell)}</th>" for cell in headers)
                table.append("</tr></thead><tbody>")
                for row in rows:
                    padded = row + [""] * max(0, len(headers) - len(row))
                    table.append("<tr>")
                    table.extend(f"<td>{self.inline(cell)}</td>" for cell in padded[: len(headers)])
                    table.append("</tr>")
                table.append("</tbody></table></div></div>")
                output.append("".join(table))
                continue
            if LIST_RE.match(line):
                list_lines: list[str] = []
                while index < len(lines) and LIST_RE.match(lines[index]):
                    list_lines.append(lines[index])
                    index += 1
                output.append(self.render_list(parse_list_records(list_lines)))
                continue
            if line.lstrip().startswith(">"):
                quote: list[str] = []
                while index < len(lines) and lines[index].lstrip().startswith(">"):
                    quote.append(re.sub(r"^\s*>\s?", "", lines[index]))
                    index += 1
                output.append(f'<blockquote><p>{self.inline(" ".join(quote))}</p></blockquote>')
                continue
            paragraph: list[str] = []
            while index < len(lines) and not self.starts_block(lines, index):
                paragraph.append(lines[index].strip())
                index += 1
            if paragraph:
                output.append(f"<p>{self.inline(' '.join(paragraph))}</p>")
            else:
                self.page.warnings.append(f"unparsed line {index + 1}: {line[:100]}")
                output.append(f'<p class="render-warning">{html.escape(line)}</p>')
                index += 1
        self.page.sections = extract_search_sections(self.page.raw, self.page.headings)
        return "\n".join(output)


def extract_search_sections(raw: str, headings: list[Heading]) -> list[SearchSection]:
    lines = raw.splitlines()
    sections: list[SearchSection] = []
    current_title = ""
    current_anchor = ""
    current_level = 7
    buffer: list[str] = []
    heading_iter = iter(headings)
    next_rendered = next(heading_iter, None)
    in_fence = False

    def flush() -> None:
        if current_title and buffer:
            text = plain_search_text("\n".join(buffer))
            if text:
                sections.append(SearchSection(current_title, current_anchor, text[:1800]))

    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            buffer.append(line)
            continue
        match = HEADING_RE.match(line) if not in_fence else None
        if match:
            level = len(match.group(1))
            if level == 1:
                continue
            flush()
            title = plain_inline(match.group(2))
            if next_rendered is not None:
                current_title, current_anchor, current_level = next_rendered.text, next_rendered.anchor, next_rendered.level
                next_rendered = next(heading_iter, None)
            else:
                current_title, current_anchor, current_level = title, slugify(title), level
            buffer = []
        elif current_title:
            buffer.append(line)
    flush()
    return sections


def plain_search_text(raw: str) -> str:
    raw = COMMENT_RE.sub(" ", raw)
    raw = re.sub(r"```.*?```", " ", raw, flags=re.DOTALL)
    raw = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", raw)
    raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
    raw = re.sub(r"[#>*_`~|]", " ", raw)
    return " ".join(raw.split())


def navigation_group(page: Page) -> tuple[str, int]:
    if page.page_type == "landing":
        return "开始", 0
    if page.page_type in {"overview", "architecture", "landscape", "trends", "radar", "consensus", "boundary"}:
        return "领域地图", 1
    if page.page_type == "mechanism":
        return "技术机制", 2
    if page.page_type == "scenario":
        return "场景视图", 3
    if page.page_type == "cross-cutting":
        return "横切问题", 4
    if page.page_type == "project":
        return "工程案例", 5
    if page.page_type in {"method", "review", "audit"}:
        return "方法与证据", 6
    return "补充材料", 7


def page_sort_key(page: Page) -> tuple[int, int, str]:
    group, group_order = navigation_group(page)
    preferred = {
        "reader/README.md": 0,
        "reader/overview.md": 1,
        "reader/architecture.md": 2,
        "reader/solution-landscape.md": 3,
        "reader/trends.md": 4,
        "reader/scenarios.md": 5,
        "reader/github-radar.md": 6,
        "reader/consensus-and-open-questions.md": 7,
        "reader/adjacent-boundaries.md": 8,
        "reader/method-and-scope.md": 90,
        "reader/human-review.md": 91,
        "README.md": 99,
    }
    posix = page.relative_source.as_posix()
    return group_order, preferred.get(posix, 20), posix


def relative_link(from_output: Path, to_output: Path) -> str:
    return Path(os.path.relpath(to_output, from_output.parent)).as_posix()


def render_navigation(current: Page, pages: list[Page]) -> str:
    groups: dict[str, list[Page]] = {}
    for page in sorted(pages, key=page_sort_key):
        group, _ = navigation_group(page)
        groups.setdefault(group, []).append(page)
    parts: list[str] = ['<nav class="suite-nav-inner" aria-label="研究套件">']
    for label, group_pages in groups.items():
        parts.append(f'<section class="nav-group"><h2>{html.escape(label)}</h2><ul>')
        for page in group_pages:
            active = page.output == current.output
            aria = ' aria-current="page"' if active else ""
            class_name = ' class="active"' if active else ""
            parts.append(
                f'<li><a{class_name}{aria} href="{html.escape(relative_link(current.output, page.output), quote=True)}">'
                f'<span>{html.escape(page.title)}</span><small>{page.reading_minutes} 分钟</small></a></li>'
            )
        parts.append("</ul></section>")
    parts.append("</nav>")
    return "".join(parts)


def render_outline(page: Page) -> str:
    items = [heading for heading in page.headings if heading.level <= 3]
    if not items:
        return '<p class="outline-empty">本页没有二级标题。</p>'
    return "<ol>" + "".join(
        f'<li class="level-{heading.level}"><a href="#{html.escape(heading.anchor, quote=True)}">{html.escape(heading.text)}</a></li>'
        for heading in items
    ) + "</ol>"


def render_breadcrumb(page: Page) -> str:
    group, _ = navigation_group(page)
    return f'<nav class="breadcrumb" aria-label="面包屑"><a href="{html.escape(relative_link(page.output, Path("index.html")), quote=True)}">调研入口</a><span>/</span><span>{html.escape(group)}</span></nav>'


def render_pager(page: Page, pages: list[Page]) -> str:
    group, _ = navigation_group(page)
    peers = [candidate for candidate in sorted(pages, key=page_sort_key) if navigation_group(candidate)[0] == group]
    if len(peers) < 2 or page not in peers:
        return ""
    index = peers.index(page)
    previous = peers[index - 1] if index > 0 else None
    following = peers[index + 1] if index + 1 < len(peers) else None

    def card(candidate: Page | None, direction: str) -> str:
        if candidate is None:
            return '<span class="pager-empty" aria-hidden="true"></span>'
        label = "上一篇" if direction == "previous" else "下一篇"
        arrow = "←" if direction == "previous" else "→"
        return (
            f'<a class="pager-card {direction}" href="{html.escape(relative_link(page.output, candidate.output), quote=True)}">'
            f'<small>{arrow} {label} · {html.escape(candidate.page_type_label)}</small>'
            f'<strong>{html.escape(candidate.title)}</strong></a>'
        )
    return f'<nav class="page-pager" aria-label="同组页面导航">{card(previous, "previous")}{card(following, "next")}</nav>'


def render_landing_map(page: Page, pages: list[Page]) -> str:
    if page.page_type == "landing":
        targets = ["overview", "architecture", "mechanism", "project"]
        labels = {
            "overview": ("先建立全局地图", "问题、机制、近期变化与关键不确定性"),
            "architecture": ("再沿数据流走一遍", "从写入到状态、检索、行动与反馈"),
            "mechanism": ("进入一个技术分支", "重建方案家族的内部工作方式"),
            "project": ("检查真实工程", "固定版本的组件、依赖、边界与失败"),
        }
        cards: list[str] = []
        for target in targets:
            candidate = next((item for item in sorted(pages, key=page_sort_key) if item.page_type == target), None)
            if candidate is None:
                continue
            title, note = labels[target]
            cards.append(
                f'<a class="route-card" href="{html.escape(relative_link(page.output, candidate.output), quote=True)}">'
                f'<span class="route-card-kicker">{html.escape(candidate.page_type_label)}</span><strong>{html.escape(title)}</strong>'
                f'<p>{html.escape(note)}</p><small>{candidate.reading_minutes} 分钟 · {html.escape(candidate.title)}</small></a>'
            )
        return '<section class="reader-map" aria-labelledby="reader-map-title"><div class="reader-map-head"><span>Recommended paths</span><h2 id="reader-map-title">从问题到机制，再到工程证据</h2></div><div class="route-grid">' + "".join(cards) + "</div></section>"
    headings = [item for item in page.headings if item.level == 2][:8]
    if len(headings) < 3:
        return ""
    cards = "".join(
        f'<a href="#{html.escape(heading.anchor, quote=True)}"><span>{index + 1:02d}</span><strong>{html.escape(heading.text)}</strong></a>'
        for index, heading in enumerate(headings)
    )
    return f'<nav class="section-map" aria-label="本页理解地图"><span class="section-map-label">本页理解地图</span><div>{cards}</div></nav>'


def render_page(page: Page, pages: list[Page], body: str, destination_root: Path) -> str:
    asset_prefix = relative_link(page.output, Path("assets/site.css"))
    js_prefix = relative_link(page.output, Path("assets/site.js"))
    search_prefix = relative_link(page.output, Path("assets/search-index.js"))
    lead = page.description or "这是一份技术前沿调研套件中的读者页面。"
    navigation = render_navigation(page, pages)
    outline = render_outline(page)
    map_html = render_landing_map(page, pages)
    diagram_count = page.raw.count("```mermaid")
    table_count = sum(1 for index, line in enumerate(page.raw.splitlines()[:-1]) if "|" in line and TABLE_SEPARATOR_RE.match(page.raw.splitlines()[index + 1]))
    content_signals = [f"{len([heading for heading in page.headings if heading.level == 2])} 节"]
    if diagram_count:
        content_signals.append(f"{diagram_count} 图")
    if table_count:
        content_signals.append(f"{table_count} 表")
    content_summary = " · ".join(content_signals)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(lead, quote=True)}">
  <title>{html.escape(page.title)} · Frontier Atlas</title>
  <link rel="icon" href="{html.escape(relative_link(page.output, Path("assets/favicon.svg")), quote=True)}" type="image/svg+xml">
  <link rel="stylesheet" href="{html.escape(asset_prefix, quote=True)}">
  <script src="{html.escape(search_prefix, quote=True)}" defer></script>
  <script src="{html.escape(js_prefix, quote=True)}" defer></script>
</head>
<body data-page-type="{html.escape(page.page_type, quote=True)}">
  <a class="skip-link" href="#main-content">跳到正文</a>
  <div class="reading-progress" aria-hidden="true"><span></span></div>
  <header class="topbar">
    <button class="icon-button nav-toggle" type="button" aria-controls="suite-nav" aria-expanded="false"><span aria-hidden="true">☰</span><span class="sr-only">打开套件导航</span></button>
    <a class="brand" href="{html.escape(relative_link(page.output, Path("index.html")), quote=True)}"><span class="brand-mark">F</span><span><strong>Frontier Atlas</strong><small>技术调研 · 理解优先</small></span></a>
    <div class="top-actions">
      <button class="search-trigger" type="button" aria-haspopup="dialog"><span aria-hidden="true">⌕</span><span>搜索整套报告</span><kbd>Ctrl K</kbd></button>
      <button class="icon-button focus-toggle" type="button" aria-pressed="false" title="专注阅读"><span aria-hidden="true">◫</span><span class="sr-only">切换专注阅读</span></button>
      <button class="icon-button theme-toggle" type="button" title="切换主题"><span aria-hidden="true">◐</span><span class="sr-only">切换明暗主题</span></button>
    </div>
  </header>
  <noscript><div class="noscript-note">JavaScript 已关闭：正文、图表、链接和打印仍可使用；全文搜索、主题切换与当前章节高亮不可用。</div></noscript>
  <aside class="suite-nav" id="suite-nav">{navigation}</aside>
  <button class="nav-backdrop" type="button" tabindex="-1" aria-label="关闭导航"></button>
  <main class="reader-main" id="main-content">
    <article class="reader-article">
      {render_breadcrumb(page)}
      <header class="article-hero">
        <div class="article-meta"><span>{html.escape(page.page_type_label)}</span><span>{page.reading_minutes} 分钟</span><span>{html.escape(content_summary)}</span><span>{html.escape(page.relative_source.as_posix())}</span></div>
        <h1>{html.escape(page.title)}</h1>
        <p>{html.escape(lead)}</p>
      </header>
      {map_html}
      <div class="article-body">{body}</div>
      {render_pager(page, pages)}
      <footer class="article-footer"><span>Markdown 是权威内容源</span><a href="{html.escape(relative_link(page.output, Path("about.html")), quote=True)}">关于本套件</a><button type="button" onclick="window.print()">打印 / 导出 PDF</button></footer>
    </article>
  </main>
  <aside class="page-outline" aria-label="本页目录"><div><span class="outline-kicker">On this page</span><h2>本页目录</h2>{outline}</div></aside>
  <dialog class="search-dialog" id="search-dialog" aria-labelledby="search-title">
    <form method="dialog" class="search-shell">
      <header><div><span>Search the research suite</span><h2 id="search-title">搜索整套报告</h2></div><button value="close" aria-label="关闭搜索">×</button></header>
      <label class="search-field"><span class="sr-only">输入技术概念</span><input id="search-input" type="search" autocomplete="off" placeholder="输入机制、项目、风险或术语…"></label>
      <p class="search-hint">标题和章节优先；支持中文子串。↑ ↓ 选择，Enter 打开，Esc 关闭。</p>
      <div class="search-results" id="search-results" role="listbox" aria-label="搜索结果"></div>
    </form>
  </dialog>
</body>
</html>
'''


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag not in {"a", "link", "script", "img"}:
            return
        attribute = "href" if tag in {"a", "link"} else "src"
        value = values.get(attribute)
        if value:
            self.links.append((tag, value))


def collect_site_html(destination: Path) -> tuple[dict[Path, LinkCollector], list[str]]:
    documents: dict[Path, LinkCollector] = {}
    errors: list[str] = []
    html_files = sorted(destination.rglob("*.html"))
    if not html_files:
        return {}, ["site contains no HTML files"]
    for path in html_files:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            errors.append(f"{path.relative_to(destination)}: invalid UTF-8: {error}")
            continue
        if "\ufffd" in text:
            errors.append(f"{path.relative_to(destination)}: replacement character found")
        if len(re.findall(r"<h1\b", text, flags=re.I)) != 1:
            errors.append(f"{path.relative_to(destination)}: expected exactly one H1")
        parser = LinkCollector()
        parser.feed(text)
        documents[path.resolve()] = parser
    return documents, errors


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_site(destination: Path) -> list[str]:
    destination = destination.resolve()
    documents, errors = collect_site_html(destination)
    for path, parser in documents.items():
        for tag, link in parser.links:
            parsed = urlsplit(html.unescape(link))
            if parsed.scheme in SAFE_SCHEMES:
                continue
            if parsed.scheme:
                errors.append(f"{path.relative_to(destination)}: unsafe or unsupported scheme in {link}")
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not _inside(target, destination):
                errors.append(f"{path.relative_to(destination)}: local link escapes the standalone site: {link}")
                continue
            if parsed.path and not target.exists():
                errors.append(f"{path.relative_to(destination)}: broken local link {link}")
                continue
            if parsed.fragment and target.suffix.casefold() == ".html":
                target_document = documents.get(target)
                fragment = unquote(parsed.fragment)
                if target_document is None or fragment not in target_document.ids:
                    errors.append(f"{path.relative_to(destination)}: missing fragment target {link}")
    return errors


def read_search_index(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    prefix = "window.__FRONTIER_SEARCH_INDEX__="
    if not text.startswith(prefix) or not text.rstrip().endswith(";"):
        raise RenderError("assets/search-index.js has an invalid wrapper")
    payload = text[len(prefix) :].strip()
    return json.loads(payload[:-1])


def validate_manifest(destination: Path, source_root: Path) -> list[str]:
    destination = destination.resolve()
    source_root = source_root.resolve()
    errors = validate_site(destination)
    manifest_path = destination / "build-manifest.json"
    if not manifest_path.is_file():
        return errors + ["build-manifest.json is missing"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return errors + [f"build-manifest.json is invalid: {error}"]
    if manifest.get("generated_by") != GENERATOR_ID:
        errors.append("build-manifest.json: generated_by does not identify this renderer")
    if manifest.get("source_root") != ".":
        errors.append("build-manifest.json: source_root must be portable '.'")

    allowed: set[str] = {"build-manifest.json"}
    page_rows = manifest.get("pages")
    if not isinstance(page_rows, list):
        errors.append("build-manifest.json: pages must be an array")
        page_rows = []
    manifest_sources: set[str] = set()
    for row in page_rows:
        if not isinstance(row, dict):
            errors.append("build-manifest.json: page rows must be objects")
            continue
        source_value, output_value = row.get("source"), row.get("output")
        if not isinstance(source_value, str) or not isinstance(output_value, str):
            errors.append("build-manifest.json: page source/output must be strings")
            continue
        source = (source_root / source_value).resolve()
        output = (destination / output_value).resolve()
        if not _inside(source, source_root) or not _inside(output, destination):
            errors.append(f"build-manifest.json: unsafe page path {source_value} -> {output_value}")
            continue
        manifest_sources.add(Path(source_value).as_posix())
        allowed.add(Path(output_value).as_posix())
        if not source.is_file() or sha256(source) != row.get("source_sha256"):
            errors.append(f"build-manifest.json: source hash mismatch for {source_value}")
        if not output.is_file() or sha256(output) != row.get("output_sha256"):
            errors.append(f"build-manifest.json: output hash mismatch for {output_value}")

    assets = manifest.get("assets")
    if not isinstance(assets, dict):
        errors.append("build-manifest.json: assets must be an object")
        assets = {}
    for relative, expected_hash in assets.items():
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append("build-manifest.json: asset entries must be path/hash strings")
            continue
        path = (destination / relative).resolve()
        if not _inside(path, destination):
            errors.append(f"build-manifest.json: unsafe asset path {relative}")
            continue
        allowed.add(Path(relative).as_posix())
        if not path.is_file() or sha256(path) != expected_hash:
            errors.append(f"build-manifest.json: asset hash mismatch for {relative}")

    copied_rows = manifest.get("copied_assets", [])
    if not isinstance(copied_rows, list):
        errors.append("build-manifest.json: copied_assets must be an array")
        copied_rows = []
    for row in copied_rows:
        if not isinstance(row, dict):
            errors.append("build-manifest.json: copied asset rows must be objects")
            continue
        source_value, output_value = row.get("source"), row.get("output")
        if not isinstance(source_value, str) or not isinstance(output_value, str):
            errors.append("build-manifest.json: copied asset source/output must be strings")
            continue
        source = (source_root / source_value).resolve()
        output = (destination / output_value).resolve()
        if not _inside(source, source_root) or not _inside(output, destination):
            errors.append(f"build-manifest.json: unsafe copied asset path {source_value} -> {output_value}")
            continue
        allowed.add(Path(output_value).as_posix())
        if not source.is_file() or sha256(source) != row.get("source_sha256"):
            errors.append(f"build-manifest.json: copied source hash mismatch for {source_value}")
        if not output.is_file() or sha256(output) != row.get("output_sha256"):
            errors.append(f"build-manifest.json: copied output hash mismatch for {output_value}")

    try:
        expected_pages = discover_pages(source_root, destination)
    except RenderError as error:
        errors.append(f"source discovery failed during manifest check: {error}")
        expected_pages = []
    expected_sources = {page.relative_source.as_posix() for page in expected_pages}
    if expected_sources != manifest_sources:
        missing = sorted(expected_sources - manifest_sources)
        stale = sorted(manifest_sources - expected_sources)
        errors.append(f"build-manifest.json: source set drift; missing={missing[:5]} stale={stale[:5]}")
    if manifest.get("page_count") != len(page_rows):
        errors.append("build-manifest.json: page_count does not match pages")

    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual != allowed:
        errors.append(
            "build-manifest.json: output set drift; "
            f"missing={sorted(allowed - actual)[:5]} stale={sorted(actual - allowed)[:5]}"
        )

    search_path = destination / "assets" / "search-index.js"
    try:
        search_rows = read_search_index(search_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RenderError) as error:
        errors.append(f"search index is invalid: {error}")
        search_rows = []
    documents, _ = collect_site_html(destination)
    for row in search_rows:
        value = row.get("path") if isinstance(row, dict) else None
        if not isinstance(value, str):
            errors.append("search index row path must be a string")
            continue
        parsed = urlsplit(value)
        target = (destination / unquote(parsed.path)).resolve()
        if not _inside(target, destination) or not target.is_file():
            errors.append(f"search index target is missing or unsafe: {value}")
            continue
        if parsed.fragment and unquote(parsed.fragment) not in documents.get(target, LinkCollector()).ids:
            errors.append(f"search index fragment is missing: {value}")
    if manifest.get("search_record_count") != len(search_rows):
        errors.append("build-manifest.json: search_record_count does not match index")
    return errors


def build_search_index(pages: list[Page], destination: Path) -> Path:
    rows: list[dict[str, str]] = []
    for page in sorted(pages, key=page_sort_key):
        page_href = page.output.as_posix()
        rows.append({
            "path": page_href,
            "title": page.title,
            "section": page.page_type_label,
            "text": plain_search_text(page.raw)[:2400],
            "type": page.page_type,
        })
        for section in page.sections:
            rows.append({
                "path": f"{page_href}#{section.anchor}",
                "title": page.title,
                "section": section.title,
                "text": section.text,
                "type": page.page_type,
            })
    target = destination / "assets" / "search-index.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    target.write_text(f"window.__FRONTIER_SEARCH_INDEX__={payload};\n", encoding="utf-8", newline="\n")
    return target


def _build_site_into(root: Path, destination: Path) -> dict[str, object]:
    pages = discover_pages(root, destination)
    source_map = {page.source.resolve(): page.output for page in pages}
    destination.mkdir(parents=True, exist_ok=True)
    if not ASSET_DIRECTORY.is_dir():
        raise RenderError(f"missing renderer assets: {ASSET_DIRECTORY}")
    asset_target = destination / "assets"
    asset_target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSET_DIRECTORY / "site.css", asset_target / "site.css")
    shutil.copy2(ASSET_DIRECTORY / "site.js", asset_target / "site.js")
    shutil.copy2(ASSET_DIRECTORY / "favicon.svg", asset_target / "favicon.svg")

    copied_assets: set[tuple[Path, Path]] = set()
    output_entries: list[dict[str, object]] = []
    for page in pages:
        renderer = MarkdownRenderer(page, root, destination, source_map)
        body = renderer.render()
        copied_assets.update(renderer.assets)
        target = destination / page.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(page, pages, body, destination), encoding="utf-8", newline="\n")
        output_entries.append({
            "source": page.relative_source.as_posix(),
            "source_sha256": sha256(page.source),
            "output": page.output.as_posix(),
            "output_sha256": sha256(target),
            "page_type": page.page_type,
            "headings": len(page.headings),
            "warnings": page.warnings,
            "workspace_links": page.workspace_links,
        })
    copied_entries: list[dict[str, str]] = []
    for source, target in copied_assets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied_entries.append({
            "source": source.relative_to(root).as_posix(),
            "source_sha256": sha256(source),
            "output": target.relative_to(destination).as_posix(),
            "output_sha256": sha256(target),
        })
    search_target = build_search_index(pages, destination)
    errors = validate_site(destination)
    if errors:
        preview = "\n".join(f"- {item}" for item in errors[:20])
        raise RenderError(f"generated site validation failed ({len(errors)} error(s)):\n{preview}")
    manifest: dict[str, object] = {
        "schema_version": "1.1",
        "generated_by": GENERATOR_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_root": ".",
        "source_root_name": root.name,
        "entry": "index.html",
        "page_count": len(pages),
        "asset_count": len(copied_assets) + 4,
        "search_record_count": sum(1 + len(page.sections) for page in pages),
        "assets": {
            "assets/site.css": sha256(asset_target / "site.css"),
            "assets/site.js": sha256(asset_target / "site.js"),
            "assets/search-index.js": sha256(search_target),
            "assets/favicon.svg": sha256(asset_target / "favicon.svg"),
        },
        "copied_assets": sorted(copied_entries, key=lambda row: row["output"]),
        "workspace_only_link_count": sum(len(page.workspace_links) for page in pages),
        "pages": output_entries,
        "warnings": sum((page.warnings for page in pages), []),
    }
    manifest_path = destination / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return manifest


def _assert_replaceable(destination: Path) -> None:
    if not destination.exists():
        return
    if not destination.is_dir():
        raise RenderError(f"output path exists and is not a directory: {destination}")
    if not any(destination.iterdir()):
        return
    manifest_path = destination / "build-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RenderError(
            f"refusing to replace non-empty output without a valid renderer manifest: {destination} ({error})"
        ) from error
    if manifest.get("generated_by") == GENERATOR_ID and _manifest_output_owned(destination, manifest):
        return
    if manifest.get("schema_version") == "1.0" and _valid_legacy_output(destination, manifest):
        return
    raise RenderError(f"refusing to replace output not owned by {GENERATOR_ID}: {destination}")


def _manifest_output_owned(destination: Path, manifest: dict[str, object]) -> bool:
    allowed = {"build-manifest.json"}
    pages = manifest.get("pages")
    assets = manifest.get("assets")
    copied = manifest.get("copied_assets", [])
    if not isinstance(pages, list) or not isinstance(assets, dict) or not isinstance(copied, list):
        return False
    rows: list[tuple[str, str]] = []
    for row in pages:
        if not isinstance(row, dict) or not isinstance(row.get("output"), str) or not isinstance(row.get("output_sha256"), str):
            return False
        rows.append((row["output"], row["output_sha256"]))
    for relative, expected_hash in assets.items():
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            return False
        rows.append((relative, expected_hash))
    for row in copied:
        if not isinstance(row, dict) or not isinstance(row.get("output"), str) or not isinstance(row.get("output_sha256"), str):
            return False
        rows.append((row["output"], row["output_sha256"]))
    for relative, expected_hash in rows:
        normalized = Path(relative).as_posix()
        path = (destination / normalized).resolve()
        if not _inside(path, destination) or not path.is_file() or sha256(path) != expected_hash:
            return False
        allowed.add(normalized)
    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    return actual == allowed


def _valid_legacy_output(destination: Path, manifest: dict[str, object]) -> bool:
    """Recognize only byte-identical 1.0 output produced before generated_by existed."""
    if manifest.get("source_root") != "." or manifest.get("entry") != "index.html":
        return False
    pages = manifest.get("pages")
    assets = manifest.get("assets")
    if not isinstance(pages, list) or not pages or not isinstance(assets, dict):
        return False
    if set(assets) != {"site.css", "site.js", "search-index.js", "favicon.svg"}:
        return False
    allowed = {"build-manifest.json"}
    for row in pages:
        if not isinstance(row, dict) or not isinstance(row.get("output"), str) or not isinstance(row.get("output_sha256"), str):
            return False
        relative = Path(row["output"]).as_posix()
        path = (destination / relative).resolve()
        if not _inside(path, destination) or not path.is_file() or sha256(path) != row["output_sha256"]:
            return False
        allowed.add(relative)
    for name, expected_hash in assets.items():
        if not isinstance(expected_hash, str):
            return False
        relative = f"assets/{name}"
        path = destination / relative
        if not path.is_file() or sha256(path) != expected_hash:
            return False
        allowed.add(relative)
    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    extras = actual - allowed
    if not extras:
        return True
    if manifest.get("asset_count") != len(assets) + len(extras):
        return False
    if any(Path(relative).suffix.casefold() not in SAFE_ASSET_SUFFIXES for relative in extras):
        return False
    documents, document_errors = collect_site_html(destination)
    if document_errors:
        return False
    referenced: set[str] = set()
    for page_path, document in documents.items():
        for _, link in document.links:
            parsed = urlsplit(html.unescape(link))
            if parsed.scheme or not parsed.path:
                continue
            target = (page_path.parent / unquote(parsed.path)).resolve()
            if _inside(target, destination) and target.is_file():
                referenced.add(target.relative_to(destination).as_posix())
    return extras <= referenced


def build_site(root: Path, destination: Path) -> dict[str, object]:
    root = root.resolve()
    destination = destination.resolve()
    if not root.is_dir():
        raise RenderError(f"suite root does not exist: {root}")
    if destination == root:
        raise RenderError("output directory must not equal the suite root")
    for protected in (root / "reader", root / "audit"):
        if destination == protected or protected in destination.parents:
            raise RenderError(f"output directory must not be inside source content: {protected}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    _assert_replaceable(destination)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}-build-", dir=destination.parent))
    backup: Path | None = None
    try:
        manifest = _build_site_into(root, staging)
        errors = validate_manifest(staging, root)
        if errors:
            preview = "\n".join(f"- {item}" for item in errors[:20])
            raise RenderError(f"staged site validation failed ({len(errors)} error(s)):\n{preview}")
        if destination.exists():
            backup = destination.parent / f".{destination.name}-backup-{uuid.uuid4().hex}"
            os.replace(destination, backup)
            try:
                _assert_replaceable(backup)
            except (OSError, RenderError):
                os.replace(backup, destination)
                backup = None
                raise
        try:
            os.replace(staging, destination)
        except OSError:
            if backup is not None and backup.exists() and not destination.exists():
                os.replace(backup, destination)
                backup = None
            raise
        if backup is not None and backup.exists():
            try:
                _assert_replaceable(backup)
            except (OSError, RenderError) as error:
                rejected = destination.parent / f".{destination.name}-rejected-{uuid.uuid4().hex}"
                os.replace(destination, rejected)
                os.replace(backup, destination)
                backup = None
                raise RenderError(
                    f"old output changed during publish; original restored and replacement preserved at {rejected}"
                ) from error
            shutil.rmtree(backup)
            backup = None
        return manifest
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if backup is not None and backup.exists() and not destination.exists():
            os.replace(backup, destination)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Reader suite root containing reader/README.md")
    parser.add_argument("--output", type=Path, help="Output directory; defaults to <root>/site")
    parser.add_argument("--check", action="store_true", help="Validate an existing output directory without rebuilding")
    args = parser.parse_args(argv)
    destination = (args.output or (args.root / "site")).resolve()
    try:
        if args.check:
            errors = validate_manifest(destination, args.root)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
            print(f"OK: HTML site is valid ({len(list(destination.rglob('*.html')))} pages)")
            return 0
        manifest = build_site(args.root, destination)
        warning_count = len(manifest.get("warnings", []))
        print(f"generated HTML reader site: {destination}")
        print(
            f"pages={manifest['page_count']} search_records={manifest['search_record_count']} "
            f"warnings={warning_count} workspace_only_links={manifest['workspace_only_link_count']}"
        )
        return 0
    except (OSError, RenderError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
