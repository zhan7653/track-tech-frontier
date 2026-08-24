from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def link(title: str, url: str) -> str:
    return f"[{title.replace('|', '/')}]({url})"


sources = rows(ROOT / "sources.jsonl")
papers = sorted((row for row in sources if row["source_type"] == "paper"), key=lambda row: (row.get("published_at") or "", row["title"]), reverse=True)
repositories = sorted((row for row in sources if row["source_type"] == "repository"), key=lambda row: row["title"].lower())

out = [
    "# 深核验来源索引\n",
    "本页只列已经打开原始 PDF 或固定 commit 的 52 个 T1 source。广度候选仍保存在 Bundle ledgers，不在这里伪装成深证据。论文结果保持作者协议边界；仓库只证明固定代码、测试/CI存在与维护快照，不证明生产效果。\n",
    "## 论文（42）\n",
    "| 日期 | 来源 | 版本 | 主要用途 |\n",
    "|---|---|---|---|\n",
]
paper_clusters = {}
for assignment in rows(ROOT / "cluster_assignments.jsonl"):
    paper_clusters.setdefault(assignment["entity_id"], set()).add(assignment["cluster_id"])
for source in papers:
    clusters = ", ".join(sorted(paper_clusters.get(source["entity_id"], set()))) or "横切/bridge"
    out.append(f"| {source.get('published_at') or '未知'} | {link(source['title'], source['url'])} | {source['version']} | {clusters} |\n")

out.extend([
    "\n## 仓库（10）\n",
    "| 仓库 | 固定 commit | 对应工程报告 |\n",
    "|---|---|---|\n",
])
report_names = {
    "openai/openai-agents-python": "openai--openai-agents-python.md",
    "openai/codex": "openai--codex.md",
    "langchain-ai/langgraph": "langchain-ai--langgraph.md",
    "langchain-ai/deepagents": "langchain-ai--deepagents.md",
    "microsoft/autogen": "microsoft--autogen.md",
    "microsoft/UFO": "microsoft--UFO.md",
    "caura-ai/caura": "caura-ai--caura.md",
    "smaramwbc/statewave-multi-agent-memory": "smaramwbc--statewave-multi-agent-memory.md",
    "kimdanny/matm": "kimdanny--matm.md",
    "MehulG/memX": "MehulG--memX.md",
}
for source in repositories:
    repo = source["title"].removesuffix(" pinned source tree")
    out.append(f"| {link(repo, source['url'])} | `{source['version'][:8]}` | [报告](projects/{report_names[repo]}) |\n")

out.extend([
    "\n## 怎样使用这个索引\n",
    "- 想理解全领域：先读[总览](overview.md)和[架构](architecture.md)，不要从来源列表开始。\n",
    "- 想重建算法：从[机制分支](mechanisms/README.md)进入论文机制深页。\n",
    "- 想评估工程：从[GitHub 雷达](github-radar.md)进入固定版本项目报告。\n",
    "- 想检查数字/证据：使用根目录的 sources、papers、repositories、claims、evidence 和 semantic_checks JSONL。\n",
])

(ROOT / "reader" / "source-index.md").write_text("".join(out), encoding="utf-8")
print(json.dumps({"papers": len(papers), "repositories": len(repositories)}, ensure_ascii=False))
