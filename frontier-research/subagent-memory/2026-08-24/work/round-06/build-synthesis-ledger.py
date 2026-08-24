from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
CHECKED = "2026-08-23T19:10:00Z"


CLAIMS = [
    ("R5-C001", "openai/openai-agents-python", "fact", "high", "Handoff filtering separates the model-visible input_items from new_items retained in Session history, while server-managed conversations do not support the same nested-history filter path.", "src/agents/handoffs/__init__.py", "The pinned handoff implementation and comments distinguish filtered input from retained session items and identify the server-managed limitation."),
    ("R5-C002", "openai/openai-agents-python", "fact", "high", "Sandbox memory generation is keyed by the memories_dir and sessions_dir layout inside a sandbox session; identical layouts share a manager and partial directory overlap is rejected.", "src/agents/sandbox/memory/manager.py", "The manager cache and overlap validation implement the layout identity rule."),
    ("R5-C003", "openai/codex", "fact", "high", "Codex multi-agent v2 spawn defaults to full-history fork and also supports no-history and a positive last-N-turn selection while recording canonical parent and agent-path identity.", "codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs", "The pinned handler parses fork_turns and constructs child ancestry/path metadata."),
    ("R5-C004", "openai/codex", "fact", "high", "Codex startup memory formation explicitly skips non-root agents, while the inspected memory prompt contributor does not contain the same non-root guard.", "codex-rs/memories/write/src/start.rs", "The startup function returns for non-root sources; the separate extension was also inspected to bound the read-side inference."),
    ("R5-C005", "langchain-ai/langgraph", "fact", "high", "LangGraph subgraphs distinguish no checkpointer, inherited per-invocation checkpointing, and persistent subgraph checkpointing, with thread id and checkpoint namespace determining retained state.", "libs/langgraph/langgraph/graph/state.py", "Compile flags and subgraph persistence tests define the three retention shapes."),
    ("R5-C006", "langchain-ai/langgraph", "fact", "normal", "LangGraph Store is a separate cross-thread hierarchical namespace abstraction whose semantic index and TTL behavior are optional and adapter-dependent.", "libs/checkpoint/langgraph/store/base/__init__.py", "The BaseStore contract defines tuple namespaces and optional indexing/TTL behavior."),
    ("R5-C007", "langchain-ai/deepagents", "fact", "high", "Deep Agents resets child messages for task execution but copies ordinary non-private parent state into the child and can return non-private child state fields to the parent.", "libs/deepagents/deepagents/middleware/subagents.py", "The middleware excludes messages/todos/structured/private fields and constructs a Command containing allowed child state updates."),
    ("R5-C008", "langchain-ai/deepagents", "fact", "normal", "Deep Agents inline subagents use the same configured backend object as the parent, so message-context isolation does not imply filesystem or persistent-memory isolation.", "libs/deepagents/deepagents/middleware/subagents.py", "The middleware passes the shared backend into inline child filesystem middleware."),
    ("R5-C009", "microsoft/autogen", "fact", "high", "AutoGen AssistantAgent save_state serializes model context but does not serialize the contents of independently configured external Memory components.", "python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py", "The save/load implementation handles llm_context; Memory components have a separate protocol/lifecycle."),
    ("R5-C010", "microsoft/autogen", "fact", "high", "AutoGen team snapshots are keyed by participant name and manager state, and the implementation warns that saving a running team can produce inconsistent state.", "python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py", "The team save/load implementation and warning define the portability and consistency boundary."),
    ("R5-C011", "microsoft/UFO", "fact", "normal", "UFO Host and App agents share one in-process Blackboard object whose questions, requests, trajectories and screenshots are serialized without bounded retrieval into later prompts.", "ufo/agents/memory/blackboard.py", "The fixed implementation owns four Memory lists and blackboard_to_prompt serializes their contents."),
    ("R5-C012", "microsoft/UFO", "inference", "normal", "In the pinned UFO source, automatic generic Blackboard persistence was not located beyond explicit serialization helpers and question preload, so cross-session durability remains a documentation claim rather than a verified code path.", "ufo/agents/memory/blackboard.py", "Repository-wide inspection found definitions for serialization and preload but no located automatic generic save/load invocation; this is a bounded absence finding."),
    ("R5-C013", "caura-ai/caura", "fact", "high", "Caura strong, fast and STM write paths intentionally apply different pre-persist governance, enrichment and duplicate-handling steps, so write mode changes the consistency and admission guarantee.", "core-api/src/core_api/pipeline/compositions/write.py", "The pinned pipeline composition orders different steps for each mode."),
    ("R5-C014", "caura-ai/caura", "fact", "high", "Caura persists tenant, fleet, agent, visibility, status and supersession metadata and enforces identity/scope across API, storage and background processing paths.", "core-api/src/core_api/pipeline/compositions/search.py", "The search pipeline and storage schema expose scoped identity, lifecycle and retrieval controls."),
    ("R5-C015", "smaramwbc/statewave-multi-agent-memory", "fact", "high", "The Statewave demo serializes post, compile and diff with a process-local asyncio lock because compile can consume all uncompiled episodes, while the actual compiler implementation remains outside the repository.", "agents/analyst.py", "The analyst code documents the race and uses the lock; SDK calls target the external service."),
    ("R5-C016", "kimdanny/matm", "fact", "high", "The MATM repository stores trajectory chunks in LanceDB, ranks candidates with consumer/source-specific runtime features, and can append successful runtime trajectories to the population index.", "matm/ltr/runtime_features.py", "The pinned index, feature/ranker and runner paths implement retrieval and optional online addition."),
    ("R5-C017", "MehulG/memX", "fact", "high", "memX uses Redis WATCH/MULTI with server timestamps to implement last-write-wins typed key state, which produces one current value rather than a preserved semantic conflict set.", "store.py", "The pinned set_value path compares timestamps and commits value plus timestamp transactionally."),
    ("R5-C018", "MehulG/memX", "fact", "high", "memX WebSocket notification uses an in-process Python subscription registry in the pinned code rather than a Redis pub/sub channel, so fan-out is not shared across workers or hosts.", "pubsub.py", "The fixed module maintains event/key-to-WebSocket lists and sends directly to connected sockets."),
]


SYNTHESES = [
    ("SY-C01", ["SM-C01"], ["R5-C001", "R5-C003", "R5-C007", "R4-C019"], "现实 runtime 已把历史、普通 state、application context、workspace 和能力暴露为不同继承面；因此“Child 拿到一段摘要”不能替代完整的委派边界，当前也没有跨框架统一的最小充分继承协议。", "dominant"),
    ("SY-C02", ["SM-C02"], ["R5-C006", "R5-C014", "R5-C017", "R4-C009"], "当前可用 primitive 多数允许应用构造 namespace 或 scope，但主体、权限、可见性和派生授权通常仍由上层约定；把共享键空间直接称为团队记忆会掩盖治理缺口。", "dominant"),
    ("SY-C03", ["SM-C03"], ["R5-C008", "R5-C011", "R5-C014", "R5-C017"], "共享底座已经覆盖对象引用、文件/Backend、checkpoint/store、Redis 当前值和多服务数据库，但这些实现对权威状态、历史、通知和恢复的语义不同，不能用“shared memory”一个标签互换。", "dominant"),
    ("SY-C04", ["SM-C04"], ["R5-C013", "R5-C015", "R5-C017", "R4-C001", "R4-C003", "R4-C007"], "工程常见路径仍以 write mode、reducer、LWW 或应用锁获得确定性；显式保留冲突、事务化 belief commit、验证 patch 与级联修复主要集中在较新的研究和少量治理服务。", "dominant"),
    ("SY-C05", ["SM-C05"], ["R5-C001", "R5-C004", "R5-C007", "R4-C018", "R4-C020"], "主流 Child→Parent 回流仍以最终文本、ToolMessage、普通 state update 或共享工件为主；带来源、验证、replay 和候选晋升的回流协议存在于特定系统，但尚未成为 runtime 默认。", "dominant"),
    ("SY-C06", ["SM-C06"], ["R5-C016", "R4-C027", "R4-C030", "R4-C035"], "跨 Agent 经验复用正在从相似度检索转向 consumer-specific utility、对比约束、分层图和失败卡片；现有证据同时表明跨模型负迁移与过量检索是真实边界，不能假设共享越多越好。", "dominant"),
    ("SY-C07", ["SM-C07"], ["R5-C006", "R5-C013", "R5-C016", "R4-C016", "R4-C035"], "前沿检索不再只做 top-k：scope、角色、时间、来源路径、consumer 和 action risk 开始进入候选生成与排序；但多数通用 store 仍只提供 namespace/search primitive。", "dominant"),
    ("SY-C08", ["SM-C08"], ["R5-C002", "R5-C004", "R5-C005", "R5-C009", "R5-C011"], "Subagent 的持久身份在真实实现中分别绑定 layout、thread/namespace、team participant、shared object 或 root/child role，而不是统一绑定“Agent 名称”；checkpoint 恢复、角色长期学习和团队共享必须分别配置。", "dominant"),
    ("SY-X01", ["SM-C01", "SM-C02", "SM-C04", "SM-C05"], ["R4-C018", "R4-C019", "R4-C022", "R4-C023", "R4-C025", "R4-C038"], "Subagent Memory 的主要安全链不是单点数据库攻击，而是输入经继承、局部处理、摘要/回流、共享检索和行动逐段改变形态；只审最终答案会漏掉内部消息、压缩状态和持久文件通道。", "dominant"),
    ("SY-X02", ["SM-C01", "SM-C04", "SM-C06", "SM-C07"], ["R4-C002", "R4-C008", "R4-C014", "R4-C017", "R4-C028", "R4-C037"], "现有 Benchmark 分别测 conflict visibility、validated patch、访问/遗忘、lineage action、trajectory transfer 或多人问答，尚不存在一个可把 Subagent Memory 整体排成单一榜单的共同协议。", "dominant"),
]


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def upsert(rows: list[dict], key: str, record: dict) -> None:
    for index, row in enumerate(rows):
        if row.get(key) == record[key]:
            rows[index] = record
            return
    rows.append(record)


def main() -> None:
    sources = read(ROOT / "sources.jsonl")
    source_by_repo = {}
    for source in sources:
        if source.get("source_type") == "repository" and source.get("title", "").endswith(" pinned source tree"):
            source_by_repo[source["title"].removesuffix(" pinned source tree")] = source
    claims = read(ROOT / "claims.jsonl")
    evidence = read(ROOT / "evidence.jsonl")
    checks = read(ROOT / "semantic_checks.jsonl")
    evidence_by_claim = {row["claim_id"]: row for row in evidence}

    for claim_id, repo, claim_type, risk, statement, locator, summary in CLAIMS:
        source = source_by_repo[repo]
        evidence_id = claim_id.replace("-C", "-EV")
        relation = "partial" if claim_type == "inference" else "supports"
        upsert(claims, "claim_id", {
            "as_of": "2026-08-24", "claim_id": claim_id, "claim_type": claim_type,
            "confidence": "medium" if claim_type == "inference" else "high", "deliverable_ids": [],
            "publication_status": "ledger-only", "risk": risk, "scope": "fixed-version repository mechanism",
            "statement": statement, "status": "qualified" if claim_type == "inference" else "supported",
        })
        full_locator = source["url"].replace("/tree/", "/blob/") + "/" + locator
        ev = {"checked_at": CHECKED, "claim_id": claim_id, "evidence_id": evidence_id, "locator": full_locator,
              "relation": relation, "source_id": source["source_id"], "support_summary": summary}
        upsert(evidence, "evidence_id", ev)
        evidence_by_claim[claim_id] = ev
        upsert(checks, "claim_id", {"checked_at": CHECKED, "claim_id": claim_id, "evidence_ids": [evidence_id],
            "rationale": "Checked against the pinned repository path and bounded to code structure; execution behavior is not claimed.",
            "uncovered_terms": [], "verdict": "pass"})

    source_by_id = {row["source_id"]: row for row in sources}
    syntheses = read(ROOT / "syntheses.jsonl")
    for synthesis_id, cluster_ids, claim_ids, proposition, assessment in SYNTHESES:
        joins = [evidence_by_claim[claim_id] for claim_id in claim_ids]
        supporting_groups = sorted({source_by_id[row["source_id"]]["independence_group"] for row in joins})
        upsert(syntheses, "synthesis_id", {
            "action": "bounded synthesis", "assessment": assessment, "claim_ids": claim_ids,
            "cluster_ids": cluster_ids, "conditions": "Applies to the fixed papers, repositories and protocols inspected through 2026-08-24.",
            "confidence": "medium", "deliverable_ids": [], "evidence_ids": [row["evidence_id"] for row in joins],
            "limitations": "Evidence mixes author studies and maintainer-controlled source artifacts; no common end-to-end reproduction was run.",
            "minority_view": "A tightly governed application may supply stronger semantics above a generic runtime or store than the underlying project exposes by default.",
            "opposing_evidence_ids": [], "opposing_group_ids": [], "proposition": proposition,
            "publication_status": "ledger-only", "reversal_criteria": "Reverse or narrow this judgment if replicated cross-runtime experiments or fixed code show the missing semantics as default, interoperable and effective.",
            "supporting_evidence_ids": [row["evidence_id"] for row in joins], "supporting_group_ids": supporting_groups,
            "synthesis_id": synthesis_id, "unknowns": "Production configurations, closed services and future runtime versions may implement additional controls.",
            "weighting_method": "Mechanism agreement across independent paper/repository groups; newer claims are down-weighted when supported only by author studies or a single codebase.",
        })

    write(ROOT / "claims.jsonl", claims)
    write(ROOT / "evidence.jsonl", evidence)
    write(ROOT / "semantic_checks.jsonl", checks)
    write(ROOT / "syntheses.jsonl", syntheses)
    print(json.dumps({"claims": len(claims), "evidence": len(evidence), "syntheses": len(syntheses)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
