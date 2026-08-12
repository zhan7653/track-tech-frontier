from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_FILES = (
    "README.md",
    "reader/README.md",
    "reader/overview.md",
    "reader/architecture.md",
    "reader/solution-landscape.md",
    "reader/scenarios.md",
    "reader/trends.md",
    "reader/github-radar.md",
    "reader/consensus-and-open-questions.md",
    "reader/method-and-scope.md",
    "reader/human-review.md",
    "reader/mechanisms/README.md",
    "reader/scenarios/README.md",
    "reader/cross-cutting/README.md",
    "reader/projects/README.md",
    "audit/README.md",
)

REQUIRED_SECTIONS = {
    "reader/overview.md": (
        "一图看懂",
        "领域现在主要在做什么",
        "当前形成的共识、分歧与空白",
    ),
    "reader/architecture.md": (
        "总体结构",
        "写入层",
        "读取层",
        "使用层",
        "横切面",
    ),
    "reader/solution-landscape.md": (
        "全领域的方案坐标",
        "工程实现的四种外形",
        "当前主流和新方向怎样区分",
    ),
    "reader/consensus-and-open-questions.md": (
        "相对稳固的共识",
        "主要争议",
        "尚未解决的问题长名单",
    ),
}

REQUIRED_DIRECTORY_CONTENT = {
    "reader/mechanisms": 1,
    "reader/scenarios": 1,
    "reader/cross-cutting": 1,
    "reader/projects": 1,
}

BRANCH_PACKAGE_MANIFEST = "audit/mechanism-packages.json"

MECHANISM_REQUIRED_SIGNALS = (
    "方案",
    "数据流",
    "实现",
    "成本",
    "失败",
    "最新研究",
)
MECHANISM_MIN_H3 = 4

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
INTERNAL_MARKER_RE = re.compile(r"<!--\s*(?:claim|synthesis|process):", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"(?:\bTODO\b|\bTBD\b|\bFIXME\b|即将补充|待补充|重编中|placeholder)",
    re.IGNORECASE,
)
H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)
ARXIV_RE = re.compile(
    r"https?://arxiv\.org/(?:abs|html)/(\d{4}\.\d{4,5})(?:v\d+)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    detail: str


def _reader_markdown_files(root: Path) -> list[Path]:
    files = [root / "README.md"]
    files.extend(sorted((root / "reader").rglob("*.md")))
    files.extend(sorted((root / "audit").rglob("*.md")))
    return [path for path in files if path.is_file()]


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def validate_reader_suite(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            findings.append(Finding("missing-file", relative, "required reader artifact is absent"))

    for relative, minimum in REQUIRED_DIRECTORY_CONTENT.items():
        directory = root / relative
        count = len([path for path in directory.glob("*.md") if path.name != "README.md"]) if directory.is_dir() else 0
        if count < minimum:
            findings.append(
                Finding("empty-section", relative, f"expected at least {minimum} substantive Markdown file(s), found {count}")
            )

    package_manifest = root / BRANCH_PACKAGE_MANIFEST
    if package_manifest.is_file():
        try:
            package_data = json.loads(package_manifest.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            findings.append(Finding("branch-package-manifest", BRANCH_PACKAGE_MANIFEST, str(error)))
        else:
            packages = package_data.get("packages")
            if not isinstance(packages, list):
                findings.append(
                    Finding("branch-package-manifest", BRANCH_PACKAGE_MANIFEST, "packages must be an array")
                )
            else:
                seen_branches: set[str] = set()
                for index, package in enumerate(packages):
                    if not isinstance(package, dict):
                        findings.append(
                            Finding(
                                "branch-package-manifest",
                                BRANCH_PACKAGE_MANIFEST,
                                f"packages[{index}] must be an object",
                            )
                        )
                        continue
                    branch = package.get("branch")
                    entry = package.get("entry")
                    deep_pages = package.get("deep_pages")
                    if not isinstance(branch, str) or not branch.strip():
                        findings.append(
                            Finding(
                                "branch-package-manifest",
                                BRANCH_PACKAGE_MANIFEST,
                                f"packages[{index}].branch must be a non-empty string",
                            )
                        )
                        continue
                    if branch in seen_branches:
                        findings.append(
                            Finding("branch-package-manifest", BRANCH_PACKAGE_MANIFEST, f"duplicate branch: {branch}")
                        )
                    seen_branches.add(branch)
                    if not isinstance(entry, str) or not entry.strip():
                        findings.append(
                            Finding(
                                "branch-package-manifest",
                                BRANCH_PACKAGE_MANIFEST,
                                f"{branch}.entry must be a non-empty path",
                            )
                        )
                        continue
                    if not isinstance(deep_pages, list) or not deep_pages or not all(
                        isinstance(path, str) and path.strip() for path in deep_pages
                    ):
                        findings.append(
                            Finding(
                                "branch-package-manifest",
                                BRANCH_PACKAGE_MANIFEST,
                                f"{branch}.deep_pages must be a non-empty path array",
                            )
                        )
                        continue

                    entry_path = root / entry
                    if not entry_path.is_file():
                        findings.append(Finding("missing-branch-entry", entry, f"declared branch entry for {branch}"))
                        continue
                    try:
                        entry_text = entry_path.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        entry_text = ""
                    linked_paths: set[Path] = set()
                    for match in MARKDOWN_LINK_RE.finditer(entry_text):
                        target = match.group(1).strip()
                        parsed = urlsplit(target)
                        if parsed.scheme or target.startswith("#") or not parsed.path:
                            continue
                        linked_paths.add((entry_path.parent / unquote(parsed.path)).resolve())

                    for deep_page in deep_pages:
                        deep_path = (root / deep_page).resolve()
                        if not deep_path.is_file():
                            findings.append(
                                Finding("missing-deep-page", deep_page, f"declared deep-dive for {branch} is absent")
                            )
                        elif deep_path not in linked_paths:
                            findings.append(
                                Finding(
                                    "unlinked-deep-page",
                                    entry,
                                    f"branch entry for {branch} does not link to {deep_page}",
                                )
                            )
    for path in _reader_markdown_files(root):
        relative = _relative(path, root)
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            findings.append(Finding("utf8-bom", relative, "UTF-8 BOM is not allowed"))
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            findings.append(Finding("utf8", relative, str(error)))
            continue

        if "\ufffd" in text:
            findings.append(Finding("replacement-char", relative, "contains U+FFFD replacement character"))
        if len(H1_RE.findall(text)) != 1:
            findings.append(Finding("h1-count", relative, "reader Markdown must contain exactly one H1"))
        if PLACEHOLDER_RE.search(text):
            findings.append(Finding("placeholder", relative, "contains unfinished placeholder language"))

        # The old-to-new map intentionally names legacy C01-C16 identifiers, but
        # no reader page may expose claim/synthesis/process markers.
        if INTERNAL_MARKER_RE.search(text):
            findings.append(Finding("internal-marker", relative, "contains an internal audit marker"))

        for match in MARKDOWN_LINK_RE.finditer(text):
            target = match.group(1).strip()
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            local = unquote(parsed.path)
            if not local:
                continue
            resolved = (path.parent / local).resolve()
            if not resolved.exists():
                findings.append(Finding("broken-link", relative, target))

    for relative, sections in REQUIRED_SECTIONS.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for section in sections:
            if section not in text:
                findings.append(Finding("missing-section", relative, section))

    mechanism_dir = root / "reader" / "mechanisms"
    if mechanism_dir.is_dir():
        for path in sorted(mechanism_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            raw = path.read_bytes()
            relative = _relative(path, root)
            try:
                text = raw.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                continue
            h3_count = len(re.findall(r"^###\s+\S", text, re.MULTILINE))
            if h3_count < MECHANISM_MIN_H3:
                findings.append(
                    Finding(
                        "shallow-mechanism",
                        relative,
                        f"found {h3_count} family-level H3 sections; expected at least {MECHANISM_MIN_H3}",
                    )
                )
            for signal in MECHANISM_REQUIRED_SIGNALS:
                if signal not in text:
                    findings.append(Finding("missing-mechanism-depth", relative, signal))

    # A reader recompile may rename a paper for clarity, but it must not silently
    # invent or transpose an arXiv ID when a frozen predecessor ledger exists.
    source_ledgers = (
        root.parent / "agent-memory-v09" / "bundle" / "sources.jsonl",
        root / "audit" / "sources.jsonl",
    )
    existing_ledgers = [path for path in source_ledgers if path.is_file()]
    if existing_ledgers:
        known_arxiv: set[str] = set()
        ledgers_valid = True
        for source_ledger in existing_ledgers:
            try:
                for raw_line in source_ledger.read_text(encoding="utf-8").splitlines():
                    if not raw_line.strip():
                        continue
                    source = json.loads(raw_line)
                    match = ARXIV_RE.search(str(source.get("url", "")))
                    if match:
                        known_arxiv.add(match.group(1))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                ledgers_valid = False
                findings.append(Finding("source-ledger", _relative(source_ledger, root.parent), str(error)))
        if ledgers_valid:
            for path in _reader_markdown_files(root):
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                for match in ARXIV_RE.finditer(text):
                    if match.group(1) not in known_arxiv:
                        line_number = text.count("\n", 0, match.start()) + 1
                        findings.append(
                            Finding(
                                "unknown-arxiv",
                                _relative(path, root),
                                f"line {line_number}: {match.group(1)} is absent from frozen v09 sources",
                            )
                        )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a reader-first frontier research suite.")
    parser.add_argument("--root", required=True, type=Path, help="Topic/version suite root containing reader/ and audit/")
    args = parser.parse_args(argv)

    findings = validate_reader_suite(args.root)
    if findings:
        for finding in findings:
            print(f"ERROR [{finding.code}] {finding.path}: {finding.detail}")
        print(f"FAILED: {len(findings)} reader-suite error(s)")
        return 1

    markdown_count = len(_reader_markdown_files(args.root.resolve()))
    print(f"OK: reader suite is structurally complete ({markdown_count} Markdown files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
