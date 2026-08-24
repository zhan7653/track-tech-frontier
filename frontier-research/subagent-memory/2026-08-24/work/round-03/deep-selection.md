# Round 03 Deep Selection

Selection is based on mechanism coverage, current relevance, engineering distinctiveness, negative/counterexample value and the ability to change reader explanations. It is not a ranking and is not determined by Stars or a fixed quota.

## SM-C01 Context Inheritance and Delegation Boundaries

- **When Child Inherits** (`2605.08460`) — direct parent-to-child inheritance threat model.
- **AgentSys** (`2602.07398`) — explicit hierarchical memory management in an agent runtime.
- **MPAC** (`2604.09744`) — multi-principal coordination protocol and interface boundaries.
- **Dive into Claude Code** (`2604.14228`) — current coding-agent design-space analysis, used with official docs rather than alone.
- **Claude Code Subagents docs** — fresh context, delegation summary, inherited instructions/memory, permissions and worktree isolation.
- **OpenAI Agents SDK handoff/context code** — full history, filters, nested agent state and manager ownership.

## SM-C08 Subagent-Local Persistence and Identity

- **Claude Code persistent Subagent memory** — user/project/local scopes and named memory directories.
- **LangGraph subgraph persistence** — stateless, per-invocation and per-thread modes plus namespace collision boundary.
- **OpenAI Sandbox Memory** — Session separation, layout identity and read-without-generate internal Agent policy.
- **Deep Agents memory** — backend-routed persistent filesystem, agent/user/organization scope and writer policy.
- **MAPLE Sub-Agent Architecture** (`2602.13258`) — role-specific memory/learning mechanism.
- Coding-agent memory repositories (`pi-subagent-in-memory`, `subagent-memory`, `agent-memory-kit`, `dsh-memory`) remain map-stage counterpoints until fixed-version engineering quality is established.

## SM-C02 Ownership, Namespace and Visibility

- **Collaborative Memory** (`2505.18279`) — private/shared tiers and dynamic user-agent-resource policies.
- **Governed Shared Memory** (`2606.24535`) — fleet scopes, provenance and reported scope-enforcement failures.
- **GateMem** (`2606.18829`) — multi-principal utility, authorization and active forgetting benchmark.
- **MAP-Graph** (`2608.10509`) — permission eligibility separated from graded trust.
- **GroupMemBench** (`2605.14498`) — multi-party attribution and memory boundaries.
- **SAMEP** and **AgentLeak** — persistent context sharing protocol and internal-channel privacy leakage.

## SM-C03 Shared Coordination Substrates

- **PatchBoard** (`2605.29313`) — schema-grounded shared state and validated patch kernel.
- **tap** (`2606.14445`) — file-based heterogeneous Agent collaboration protocol.
- **LLM Multi-Agent Blackboard** (`2510.01285`) — explicit blackboard route.
- **MIRIX** (`2507.07957`) — multi-agent memory modules; determine whether “multi-agent” describes memory workers or a shared team substrate.
- Engineering cases: `microsoft/UFO`, `MehulG/memX`, `statewave-multi-agent-memory`, `shared-agent-memory` and `langgraph` Store/checkpoint split.

## SM-C04 Synchronization, Conflict and Belief Commit

- **StateFuse** (`2607.05844`) — conflict-preserving CRDT/OpSet semantics and correction handles.
- **MemTX** (`2607.23929`) — staged belief commit, action gate and cascading repair.
- **LatticeMind** (`2608.08236`) — explicit incompatible claims plus symbolic/LLM reconciliation.
- **PatchBoard** — transactional validated mutation.
- **Verified Concurrency Anomalies** (`2606.17182`) — race and invariant evidence.
- **Governed Shared Memory** — pipeline-ordering counterexample.
- **Reconcile Once, Write Anytime** (`2608.12984`) — trust-tiered librarian/writer separation.

## SM-C05 Return, Consolidation and Provenance

- **MAP-Graph** — lineage survives derivation and affects action risk.
- **CoMIC** (`2606.00756`) — critic-filtered trajectory circulation.
- **AutoRefine** (`2601.22758`) — trajectory to validated typed artifact.
- **TreeMem** (`2605.04811`) — builder/summarizer/retriever credit assignment.
- **State Contamination** (`2605.16746`) — sanitization before versus after summary.
- **MPBench** (`2606.04329`) and **Bad Memory** (`2607.14611`) — write-channel and persistent-file attack counterevidence.

## SM-C06 Population Experience and Skill Transfer

- **Multi-Agent Transactive Memory** (`2606.19911`) — population trajectory repository and consumer retrieval.
- **DecentMem** (`2605.22721`) — decentralized exploitation/exploration pools.
- **MemCollab** (`2603.23234`) — naive cross-model negative transfer and contrastive constraint distillation.
- **ConMem** (`2606.08702`) — relation-aware memory cards and conflict/dependency coordination.
- **CoMIC** — centralized reflection with decentralized execution.
- **LEGOMem** (`2510.04851`), **MAGE** (`2605.10064`), **Skill-MAS** (`2606.18837`) and **MemMA** (`2603.18718`) — procedural, evolving and coordinated memory variants.
- **Selectively Sharing Experiences** — older work retained only to explain why selective transfer predates current LLM-agent implementations.

## SM-C07 Discovery, Retrieval and Action Coupling

- **MAP-Graph** — eligibility, semantic retrieval, path trust and action gating.
- **Multi-agent In-context Coordination via Decentralized Memory Retrieval** (`2511.10030`) — decentralized retrieval topology.
- **RCR-Router** — role-aware structured-memory routing.
- **EquiMem** (`2605.09278`) — retrieval paths as trust-calibration evidence.
- **MATM** and **ConMem** — trajectory/card discovery for other agents.
- **G-Memory** (`2506.07398`) and hierarchical-memory studies — hierarchical navigation and bounded context.

## Cross-cutting benchmark and negative packets

- GateMem, GroupMemBench, AgentLeak, StateFuse conflict slice, PatchBoard ALFWorld protocol, MATM ALFWorld/WebArena, memory-poisoning benchmarks and runtime-specific security tests.
- Every quantitative comparison must receive a protocol fingerprint; incompatible results remain descriptive.
- Adoption remains a bounded gap because returned evidence is predominantly first-party.

## Project deep-dive candidates

1. `openai/openai-agents-python` — handoff, agents-as-tools, application context, Session and sandbox memory.
2. `openai/codex` — Subagent/Guardian execution boundaries versus local Memory extraction and use.
3. `langchain-ai/langgraph` plus `langchain-ai/deepagents` — subgraph persistence, Store, backend namespaces and subagent context propagation.
4. `microsoft/autogen` — agent/team state and Memory protocol.
5. `microsoft/UFO` — HostAgent/AppAgent blackboard data flow.
6. `caura-ai/caura` — governed fleet scopes, Postgres/pgvector/Redis and propagation pipeline.
7. Statewave multi-agent memory — episode log, compiler, conflict/provenance and context assembly.
8. `kimdanny/matm` — population trajectory storage/retrieval if canonical paper linkage is verified.
9. `MehulG/memX` — real-time typed shared state/pub-sub as a simpler engineering counterpoint.

Projects that cannot support a component/data-flow reconstruction will remain radar cards rather than being padded into deep reports.
