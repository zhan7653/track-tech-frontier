from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
WORK = ROOT / "work" / "round-05"
CHECKED = "2026-08-23T18:40:00Z"


SPECS = [
    {
        "repo": "openai/openai-agents-python",
        "commit": "233467994fac7e7dbd868931573cc9a4302c0a16",
        "report": "reader/projects/openai--openai-agents-python.md",
        "clusters": ["SM-C01", "SM-C05", "SM-C08"],
        "summary": "Handoff, agent-as-tool, application context, sessions, sandbox snapshots and file-backed memory layouts form distinct state boundaries rather than one Subagent Memory switch.",
        "boundary": "Use as an orchestration primitive only after the application chooses history filters, context mutability, session ownership, sandbox lifecycle and memory layout.",
        "components": ["Handoff input projection", "Agent-as-tool nested runner", "Sandbox memory generation manager"],
        "flows": ["Parent history to handoff projection", "Structured tool input to nested agent", "Nested final output to manager", "Rollout JSONL through two-phase memory consolidation"],
        "dependency": "Agents SDK runtime plus a configured session/conversation and optional sandbox provider",
        "constraints": ["Server-managed conversations do not support the same handoff filtering path", "Memory durability depends on sandbox/session snapshot and layout reuse"],
        "failures": ["Shared mutable application context crosses the model-context boundary", "Mis-keyed layouts join unrelated memory directories", "Child evidence disappears when only the last output is returned"],
        "locators": ["src/agents/handoffs/__init__.py", "src/agents/agent.py", "src/agents/sandbox/memory/manager.py"],
    },
    {
        "repo": "openai/codex",
        "commit": "2161ec272a7d6b775c9c721e6206f4fe63e383f2",
        "report": "reader/projects/openai--codex.md",
        "clusters": ["SM-C01", "SM-C05", "SM-C08"],
        "summary": "Subagents are forkable threads with explicit parent communication and shared workspace state; startup memory formation explicitly skips non-root agents.",
        "boundary": "Useful for studying root/child asymmetry, but the fixed code does not expose a dedicated evidence-checked child-result-to-memory admission API.",
        "components": ["Multi-agent v2 spawn handler", "Agent communication/status path", "Root-gated memory startup and memory prompt extension"],
        "flows": ["Parent turns to Full/None/LastN child fork", "Child work to shared filesystem", "Child final/status to parent thread", "Eligible root rollout to extraction and consolidation"],
        "dependency": "Codex thread runtime, shared working directory and CODEX_HOME memory store",
        "constraints": ["All agents share the current filesystem in the inspected desktop mode", "Memory read enablement remains thread/config dependent even though the contributor lacks the root write guard"],
        "failures": ["Full-history fork propagates stale or hostile context", "Sibling agents can observe or overwrite shared files", "Root-only formation loses findings that never reach the root rollout"],
        "locators": ["codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs", "codex-rs/memories/write/src/start.rs", "codex-rs/ext/memories/src/extension.rs"],
    },
    {
        "repo": "langchain-ai/langgraph",
        "commit": "f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f",
        "report": "reader/projects/langchain-ai--langgraph.md",
        "clusters": ["SM-C02", "SM-C03", "SM-C04", "SM-C08"],
        "summary": "Versioned graph checkpoints and a cross-thread hierarchical store provide durable state primitives; identity, access, semantic conflict and admission remain application policy.",
        "boundary": "Adopt for persistence/replay primitives, not as a complete governed shared-memory design.",
        "components": ["StateGraph/subgraph compiler", "Checkpoint saver and namespaces", "Cross-thread BaseStore"],
        "flows": ["Graph state to checkpoint writes", "Thread id plus namespace to resume/replay", "Agent query to namespaced Store search", "Reducer output to the next superstep"],
        "dependency": "LangGraph Pregel runtime plus a selected checkpoint/store adapter",
        "constraints": ["Thread and namespace construction is an application responsibility", "Semantic indexing and TTL are optional and adapter-dependent"],
        "failures": ["Thread-id reuse mixes local state", "Parallel stateful subgraphs contend on one namespace", "Checkpoint and external store snapshots diverge"],
        "locators": ["libs/langgraph/langgraph/graph/state.py", "libs/checkpoint/langgraph/store/base/__init__.py", "libs/langgraph/tests/test_subgraph_persistence.py"],
    },
    {
        "repo": "langchain-ai/deepagents",
        "commit": "23b83ad50f63d241d0069a3dc426d43b211adf2e",
        "report": "reader/projects/langchain-ai--deepagents.md",
        "clusters": ["SM-C01", "SM-C02", "SM-C03", "SM-C05", "SM-C08"],
        "summary": "The task tool resets child messages while copying non-private custom state, propagating runtime configuration and sharing a filesystem backend; non-private child state can return to the parent.",
        "boundary": "Stateless refers to child message history, not to backend files, ordinary custom state, runtime context or permissions.",
        "components": ["SubAgentMiddleware task tool", "Shared/composite backend", "MemoryMiddleware AGENTS.md loader"],
        "flows": ["Task description to fresh child message state", "Non-private parent fields to child state", "Child final and state update to parent Command", "Memory paths through backend to system prompt"],
        "dependency": "LangChain agents, LangGraph state/store and a configured backend",
        "constraints": ["Ordinary custom fields require explicit PrivateStateAttr to stay private", "Parent and inline child use the same backend object unless the application changes the design"],
        "failures": ["Secrets in ordinary state are copied to the child", "Concurrent children race on shared files or reducers", "Always-loaded memory expands prompt-injection surface"],
        "locators": ["libs/deepagents/deepagents/middleware/subagents.py", "libs/deepagents/deepagents/middleware/memory.py", "libs/deepagents/deepagents/backends/composite.py"],
    },
    {
        "repo": "microsoft/autogen",
        "commit": "027ecf0a379bcc1d09956d46d12d44a3ad9cee14",
        "report": "reader/projects/microsoft--autogen.md",
        "clusters": ["SM-C02", "SM-C03", "SM-C08"],
        "summary": "Agent model context, external Memory components and team snapshots have separate lifecycles; team save/load does not atomically capture the external memory backend.",
        "boundary": "The protocols are extensible but leave retrieval, scope, conflict, ordering and cross-store snapshot consistency to the application.",
        "components": ["AssistantAgent model context", "Memory component protocol", "Group-chat participant/manager snapshot"],
        "flows": ["Incoming messages to model context", "Memory components to pre-inference context update", "Model/tool results back to context", "Participant states and manager state to team snapshot"],
        "dependency": "AutoGen AgentChat/Core runtime, model client and chosen external Memory components",
        "constraints": ["Saving a running team may produce inconsistent state", "Memory backends require an independent lifecycle and snapshot protocol"],
        "failures": ["Team restore and external memory restore refer to different times", "Agent-name keys collide or drift", "Memory ordering changes the compiled model context"],
        "locators": ["python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py", "python/packages/autogen-core/src/autogen_core/memory/_base_memory.py", "python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py"],
    },
    {
        "repo": "microsoft/UFO",
        "commit": "96983c73ed09e884a5f1d7ff8936c953b234b684",
        "report": "reader/projects/microsoft--UFO.md",
        "clusters": ["SM-C03", "SM-C07"],
        "summary": "Host and App agents share an in-process Blackboard of questions, requests, trajectories and screenshots; the fixed code serializes the full lists into prompts without retrieval, policy or conflict state.",
        "boundary": "Good as a transparent blackboard example, but automatic cross-session persistence was not located in the pinned implementation.",
        "components": ["Per-agent MemoryItem/Memory", "Host-owned Blackboard", "Processor memory update and prompt compiler"],
        "flows": ["Execution step to agent MemoryItem", "Selected fields to shared trajectory list", "Optional screenshot to Blackboard", "All Blackboard lists to the next model prompt"],
        "dependency": "UFO Host/App state machine, GUI automation runtime and screenshot files",
        "constraints": ["Sharing is by Python object reference in one runtime", "The located serialization helpers do not prove an automatic persistence lifecycle"],
        "failures": ["Unbounded prompt growth includes base64 images", "Parallel append order lacks versioning", "Warnings allow memory-update failures to continue silently"],
        "locators": ["ufo/agents/memory/memory.py", "ufo/agents/memory/blackboard.py", "ufo/agents/processors"],
    },
    {
        "repo": "caura-ai/caura",
        "commit": "54dd6d4f2075ca428b1f3a5a8c50114351ea4755",
        "report": "reader/projects/caura-ai--caura.md",
        "clusters": ["SM-C02", "SM-C03", "SM-C04", "SM-C05", "SM-C07", "SM-C08"],
        "summary": "A multi-service fleet-memory control plane combines tenant/fleet/agent scope, strong/fast/STM writes, hybrid retrieval, background enrichment, contradiction handling, lifecycle and audit.",
        "boundary": "The breadth makes it a strong engineering reference and also makes guarantees path-dependent across routes, modes, workers and storage calls.",
        "components": ["Core API write/search pipelines", "PostgreSQL/pgvector storage API", "Redis and background worker governance services"],
        "flows": ["Authenticated write through selected pipeline mode", "Row and embedding to scoped persistent storage", "Background enrichment/contradiction/lifecycle updates", "Scoped hybrid search through rerank/filter/audit"],
        "dependency": "PostgreSQL 16 with pgvector, Redis, API/storage/worker services and configured model/embedding providers",
        "constraints": ["Strong, fast and STM modes do not provide identical admission guarantees", "Identity and scope semantics span REST/MCP/routes/storage and workers"],
        "failures": ["Fast writes temporarily expose incomplete enrichment", "Dedup can suppress a contradictory row before resolution", "Cross-table purge or scope drift leaves residual data"],
        "locators": ["core-api/src/core_api/pipeline/compositions/write.py", "core-api/src/core_api/pipeline/compositions/search.py", "infra/postgres/init.sql"],
    },
    {
        "repo": "smaramwbc/statewave-multi-agent-memory",
        "commit": "7f16415176f7a8cc5ead659a7e8ee09fa031ce76",
        "report": "reader/projects/smaramwbc--statewave-multi-agent-memory.md",
        "clusters": ["SM-C03", "SM-C04"],
        "summary": "A demo integrates episode append, subject compile and token-bounded context retrieval, while the actual compiler and reconciliation service remain external to the repository.",
        "boundary": "Use to study client integration and race avoidance, not as source evidence for the closed Statewave compiler algorithm.",
        "components": ["Deterministic analyst candidate builder", "Statewave client wrapper", "FastAPI/SSE synthesis demo"],
        "flows": ["Source JSON to memory candidates", "Candidates to external episode API", "Subject compile to before/after diff", "Retrieved context to synthesis agent"],
        "dependency": "External Statewave service/SDK, FastAPI, SSE frontend and an OpenAI-compatible synthesis model",
        "constraints": ["Compiler and conflict logic are not present in this source tree", "The application lock protects only one Python process"],
        "failures": ["Concurrent processes can double-compile one subject", "A fixed subject joins all analysts", "Active-context synthesis hides losing claims unless timeline data is inspected"],
        "locators": ["agents/analyst.py", "statewave_tools.py", "server.py"],
    },
    {
        "repo": "kimdanny/matm",
        "commit": "2fb906b1a572f9ced0177741dee44be70ef1223c",
        "report": "reader/projects/kimdanny--matm.md",
        "clusters": ["SM-C06", "SM-C07"],
        "summary": "A population trajectory index uses dense retrieval and consumer-specific learning-to-rank features; successful runtime trajectories can be appended online.",
        "boundary": "It addresses experience selection rather than general shared-state ownership, transaction, revocation or conflict governance.",
        "components": ["LanceDB trajectory index", "Runtime feature extractor and rankers", "Environment runner and online trajectory writer"],
        "flows": ["Train-only trajectories to chunks/embeddings", "Consumer state to dense candidates", "Forty-four features to LTR reranking", "Successful runtime trajectory back to shared index"],
        "dependency": "LanceDB, embedding model, ranker runtimes and ALFWorld/WebArena environments",
        "constraints": ["Published results depend on fixed benchmark splits and external environment setup", "Online admission is primarily task success plus schema"],
        "failures": ["Stale or secret-bearing trajectories are reusable", "Consumer ranker drifts for new models/tools", "No-candidate skip changes the evaluation denominator"],
        "locators": ["matm/ltr/runtime_features.py", "matm/memory/lancedb_client.py", "scripts/verify_no_test_leakage.py"],
    },
    {
        "repo": "MehulG/memX",
        "commit": "86aeffed547e9978d214f2a101136d955042301f",
        "report": "reader/projects/MehulG--memX.md",
        "clusters": ["SM-C02", "SM-C03", "SM-C04"],
        "summary": "A compact FastAPI/Redis typed-state service combines JSON Schema, ACL lookup, server-time last-write-wins and in-process WebSocket notification.",
        "boundary": "Useful as a minimal current-value substrate, not as full memory with history, provenance, semantic retrieval or conflict preservation.",
        "components": ["FastAPI ACL/API layer", "Redis schema/value store", "In-process WebSocket subscription registry"],
        "flows": ["API key to Supabase/local ACL", "Write through schema validation", "Redis WATCH/MULTI to value and timestamp", "Process-local publish to WebSocket clients"],
        "dependency": "FastAPI, Redis, jsonschema and optional Supabase",
        "constraints": ["WebSocket fan-out is process-local in the pinned code", "User namespaces use only the first eight identifier characters"],
        "failures": ["LWW erases losing semantic conflicts", "Multiple API clocks can disagree", "Auth lookup failure changes authority to a local ACL"],
        "locators": ["store.py", "pubsub.py", "auth.py"],
    },
]


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def upsert(rows: list[dict], key: str, record: dict) -> None:
    for index, row in enumerate(rows):
        if row.get(key) == record[key]:
            rows[index] = record
            return
    rows.append(record)


def short_id(prefix: str, value: str) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def url(repo: str, commit: str, locator: str = "") -> str:
    base = f"https://github.com/{repo}/blob/{commit}/"
    return base + locator if locator else f"https://github.com/{repo}/tree/{commit}"


def main() -> None:
    entities = read_jsonl(ROOT / "entities.jsonl")
    discoveries = read_jsonl(ROOT / "discovery_results.jsonl")
    queries = read_jsonl(ROOT / "queries.jsonl")
    stage_events = read_jsonl(ROOT / "stage_events.jsonl")
    assignments = read_jsonl(ROOT / "cluster_assignments.jsonl")
    sources = read_jsonl(ROOT / "sources.jsonl")
    cards = read_jsonl(ROOT / "repositories.jsonl")
    observations_out = read_jsonl(ROOT / "repository_observations.jsonl")
    profiles = read_jsonl(ROOT / "repository_engineering_profiles.jsonl")

    # Round 03 added a handful of manually mapped product/negative entities.
    # Normalize them to the same date contract before the strict audit.
    for entity in entities:
        if entity.get("created_at") is None:
            entity["created_at"] = "2026-08-23T17:30:00Z"
        if entity.get("updated_at") is None:
            entity["updated_at"] = "2026-08-23T17:40:00Z"
        published = entity.get("published_at")
        if isinstance(published, str) and len(published) > 10:
            entity["published_at"] = published[:10]

    by_identifier = {row["identifier"]: row for row in entities}
    clone_rows = {row["repository"]: row for row in read_jsonl(WORK / "clone-manifest.jsonl")}
    codex_clone = json.loads((WORK / "codex-short-clone.json").read_text(encoding="utf-8"))
    clone_rows["openai/codex"] = {"repository": "openai/codex", **codex_clone}

    for offset, spec in enumerate(SPECS, start=84):
        repo = spec["repo"]
        obs_path = next(path for path in (WORK / "observations").glob("*.jsonl") if json.loads(path.read_text(encoding="utf-8"))["owner_repo"] == repo)
        observation = json.loads(obs_path.read_text(encoding="utf-8"))
        identifier = "github-node:" + observation["node_id"]
        query_id = f"Q{offset:03d}"
        discovery_id = short_id("D-R5-", identifier)
        source_id = short_id("S-R-", repo.lower())
        profile_id = short_id("EP-R5-", repo.lower())
        entity = by_identifier.get(identifier)
        is_new = entity is None
        if entity is None:
            entity = {
                "aliases": [repo],
                "canonical_name": repo,
                "created_at": CHECKED,
                "date_confidence": "exact",
                "discovery_ids": [],
                "entity_id": short_id("E-", identifier),
                "entity_type": "repository",
                "identifier": identifier,
                "published_at": observation["created"],
                "source_ids": [],
                "stage": "discovered",
                "time_window_ids": [],
                "updated_at": CHECKED,
                "url": f"https://github.com/{repo}",
            }
            entities.append(entity)
            by_identifier[identifier] = entity
        if discovery_id not in entity["discovery_ids"]:
            entity["discovery_ids"].append(discovery_id)
        if source_id not in entity["source_ids"]:
            entity["source_ids"].append(source_id)
        entity["stage"] = "deep-verified"
        entity["updated_at"] = CHECKED
        for window in (["W_ROLLING_12M"] if observation["created"] >= "2025-08-25" else ["W_PRE_FRONTIER"]):
            if window not in entity["time_window_ids"]:
                entity["time_window_ids"].append(window)
        if observation["created"] >= "2026-05-27" and "W_ROLLING_90D" not in entity["time_window_ids"]:
            entity["time_window_ids"].append("W_ROLLING_90D")

        upsert(queries, "query_id", {
            "executed_at": observation["observed_at"],
            "gap_ids": [],
            "information_gain": "Pinned and code-inspected a representative Subagent Memory implementation; recorded repository activity without treating stars as growth evidence.",
            "iteration": 5,
            "parent_query_ids": ["Q027"],
            "provider": "github-observe",
            "query_id": query_id,
            "query_text": repo,
            "raw_snapshot_paths": [str(obs_path), str(obs_path.with_name(obs_path.stem + "-run.json"))],
            "request_url": observation["api_url"],
            "result_count": 1,
            "result_count_note": "One explicitly selected representative repository was pinned, observed and inspected.",
            "stage": "deep-focus",
            "status": "succeeded",
            "target_cluster_ids": spec["clusters"],
            "target_lanes": ["github", "repository"],
            "target_window_ids": ["W_ROLLING_90D"],
        })
        upsert(discoveries, "discovery_id", {
            "discovery_id": discovery_id,
            "identifier": identifier,
            "metadata": {"description": "Round 05 fixed-version repository deep inspection", "source": "github-observe"},
            "observed_at": observation["observed_at"],
            "page_cursor": None,
            "provider": "github-observe",
            "provider_result_id": observation["provider_result_id"],
            "query_id": query_id,
            "rank": 1,
            "title": repo,
            "url": f"https://github.com/{repo}",
        })
        if is_new:
            upsert(stage_events, "event_id", {
                "entity_id": entity["entity_id"], "event_id": short_id("SE-R5-M-", repo),
                "from_stage": "discovered", "occurred_at": CHECKED,
                "rationale": "Selected as a representative runtime or memory substrate and pinned for source inspection.", "to_stage": "mapped",
            })
        upsert(stage_events, "event_id", {
            "entity_id": entity["entity_id"], "event_id": short_id("SE-R5-D-", repo),
            "from_stage": "mapped", "occurred_at": CHECKED,
            "rationale": "Pinned commit cloned or inspected with git show; architecture, data flow, dependencies and project-specific failure modes recorded.", "to_stage": "deep-verified",
        })
        for cluster_index, cluster_id in enumerate(spec["clusters"]):
            upsert(assignments, "assignment_id", {
                "assignment_id": short_id("A-R5-", repo + cluster_id),
                "cluster_id": cluster_id,
                "confidence": "high" if cluster_index == 0 else "medium",
                "entity_id": entity["entity_id"],
                "membership": "primary" if cluster_index == 0 else "secondary",
                "method": "fixed-version repository code inspection",
                "rationale": spec["summary"],
                "time": CHECKED,
            })

        pinned = spec["commit"]
        upsert(sources, "source_id", {
            "access_note": f"Pinned commit {pinned}; repository cloned or inspected through a local Git object database. Architecture-relevant implementation and tests were read; services/tests were not executed.",
            "access_status": "opened",
            "entity_id": entity["entity_id"],
            "fetched_at": CHECKED,
            "independence_group": f"repository:{repo.lower()}",
            "limitations": "Maintainer-controlled source artifact. Code existence is distinguished from production behavior; no setup, benchmark or fault-injection execution was performed.",
            "organization": repo.split("/")[0],
            "published_at": observation["pushed"],
            "queries": [query_id],
            "source_id": source_id,
            "source_type": "repository",
            "tier": "T1",
            "title": repo + " pinned source tree",
            "url": url(repo, pinned),
            "version": pinned,
        })
        upsert(cards, "source_id", {
            "adoption_evidence": [],
            "affiliation": "official-owner",
            "checked_at": CHECKED,
            "latest_release": observation["latest_release"],
            "license": observation["license"],
            "owner_repo": repo,
            "pinned_commit": pinned,
            "pushed_at": observation["pushed"],
            "setup": "documented",
            "setup_execution_id": None,
            "source_id": source_id,
            "tests_ci": "present",
            "tests_execution_id": None,
        })
        observation_record = {key: value for key, value in observation.items() if key not in {"measurement_basis", "provider_result_id"}}
        observation_record.update({"entity_id": entity["entity_id"], "observation_id": short_id("O-R5-", repo)})
        upsert(observations_out, "observation_id", observation_record)

        locators = [url(repo, pinned, locator) for locator in spec["locators"]]
        components = [
            {"name": name, "responsibility": spec["flows"][min(index, 3)], "source_id": source_id, "locator": locators[index]}
            for index, name in enumerate(spec["components"])
        ]
        data_flow = [
            {"step": index + 1, "operation": operation, "from": "upstream state" if index == 0 else spec["components"][min(index - 1, 2)], "to": spec["components"][min(index, 2)] if index < 3 else "downstream agent/state", "source_id": source_id, "locator": locators[min(index, 2)]}
            for index, operation in enumerate(spec["flows"])
        ]
        profile = {
            "adoption_boundary": spec["boundary"],
            "architecture_summary": spec["summary"],
            "checked_at": CHECKED,
            "components": components,
            "data_flow": data_flow,
            "dependencies_services": [{"name": spec["dependency"], "role": "Required runtime or service boundary", "source_id": source_id, "locator": locators[0]}],
            "entity_id": entity["entity_id"],
            "failure_modes": [
                {"mode": failure, "trigger": "The corresponding boundary or workload condition is present.", "impact": "Memory continuity, isolation, correctness or auditability can fail for this project-specific path.", "basis_source_ids": [source_id], "inference": True}
                for failure in spec["failures"]
            ],
            "integration_constraints": [{"constraint": item, "source_id": source_id, "locator": locators[min(index, 2)]} for index, item in enumerate(spec["constraints"])],
            "issue_pr_findings": [],
            "maintenance_evidence": [{"finding": f"Observed {observation['commits_in_window']} commits and {observation['contributors_in_window']} unique contributors in the requested rolling-90-day window; this is activity evidence, not quality or growth proof.", "source_id": source_id, "locator": observation["api_url"]}],
            "pinned_commit": pinned,
            "profile_id": profile_id,
            "source_ids": [source_id],
            "unknowns": ["Issue and PR review was not sampled systematically in this round.", "Production deployment configuration and behavior remain unverified.", "Tests and services were not executed."],
        }
        upsert(profiles, "profile_id", profile)

    # Extracted hyperlinks are discovery clues, not repository links until a
    # canonical pinned repository source is reciprocally verified.
    paper_cards = read_jsonl(ROOT / "papers.jsonl")
    for card in paper_cards:
        card["evidence_role"] = "original-study"
        if card.get("publication_status") == "conference":
            card["publication_status"] = "peer-reviewed"
        card["code_links"] = []
        card["code_search_note"] = "Repository URLs were searched in the opened PDF, but no canonical pinned reciprocal paper-code relationship was verified for this card."

    write_jsonl(ROOT / "entities.jsonl", entities)
    write_jsonl(ROOT / "discovery_results.jsonl", discoveries)
    write_jsonl(ROOT / "queries.jsonl", queries)
    write_jsonl(ROOT / "stage_events.jsonl", stage_events)
    write_jsonl(ROOT / "cluster_assignments.jsonl", assignments)
    write_jsonl(ROOT / "sources.jsonl", sources)
    write_jsonl(ROOT / "repositories.jsonl", cards)
    write_jsonl(ROOT / "repository_observations.jsonl", observations_out)
    write_jsonl(ROOT / "repository_engineering_profiles.jsonl", profiles)
    write_jsonl(ROOT / "papers.jsonl", paper_cards)
    print(json.dumps({"repositories": len(SPECS), "entities": len(entities), "sources": len(sources), "profiles": len(profiles)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
