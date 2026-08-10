# Reader claim audit appendix

本文件集中保存主报告与深潜报告已经引用的原子 claim 原文和稳定 marker。它用于账本互认，不要求读者按顺序阅读，也不意味着低风险分析必须逐句原子化。

## 已引用的原子判断

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

LoCoMo evaluates very long-term conversational memory with QA, event summarization, and multimodal dialogue generation over conversations of about 300 turns, 9K tokens, and up to 35 sessions.
<!-- claim:BEN-C01 -->

LongMemEval uses 500 curated questions to assess five long-term assistant-memory abilities in scalable user-assistant histories.
<!-- claim:BEN-C02 -->

MemoryAgentBench organizes incremental multi-turn memory evaluation around accurate retrieval, test-time learning, long-range understanding, and selective forgetting.
<!-- claim:BEN-C03 -->

MemBench distinguishes factual from reflective memory and participation from observation, and evaluates effectiveness, efficiency, and capacity.
<!-- claim:BEN-C04 -->

Memora evaluates remembering, reasoning, and recommending on long personalized conversations and introduces FAMA to penalize obsolete or invalidated memory use.
<!-- claim:BEN-C05 -->

HaluMem separates memory extraction, memory updating, and memory question answering to diagnose hallucinations at different memory operations.
<!-- claim:BEN-C06 -->

Mem2ActBench evaluates whether an underspecified task request causes an agent to retrieve long-term constraints and apply them in tool use, not only answer a recall question.
<!-- claim:BEN-C07 -->

Mem2ActBench reports 2,029 sessions and 400 tool-use tasks, with a protocol that measures tool selection and parameter grounding.
<!-- claim:BEN-C08 -->

StoryBench uses branching narrative decisions and contrasts immediate-feedback with self-recovery settings.
<!-- claim:BEN-C09 -->

EMemBench derives questions from an agent's own text and visual game trajectory and computes ground truth from game signals.
<!-- claim:BEN-C10 -->

MEMTRACK models platform-interleaved Slack, Linear, and Git-style organizational histories and measures correctness, efficiency, and redundancy.
<!-- claim:BEN-C11 -->

MemoryArena evaluates memory in interdependent multi-session agentic tasks where agents distill earlier action and feedback into memory used for later decisions.
<!-- claim:BEN-C12 -->

GroupMemBench targets group dynamics, speaker-grounded belief tracking, and audience-adapted language with asker-bound queries across six categories.
<!-- claim:BEN-C13 -->

Mem-Gallery evaluates multimodal long-term conversational memory across extraction/test-time adaptation, reasoning, and knowledge management.
<!-- claim:BEN-C14 -->

ImplicitMemBench uses a Learning/Priming–Interfere–Test protocol with first-attempt scoring for procedural memory, priming, and classical conditioning.
<!-- claim:BEN-C15 -->

MemSecBench evaluates memory-poisoning lifecycle security through a controlled Write–Execute–Forget protocol over 310 cases in 48 contexts and a 24-configuration matrix.
<!-- claim:BEN-C16 -->

LongMemEval-V2 has 451 manually curated questions covering static recall, dynamic tracking, workflows, gotchas, and premise awareness for web-agent experience.
<!-- claim:BEN-C17 -->

The official LoCoMo repository contains data, task_eval, and scripts, making the authors' released dataset/evaluation artifact inspectable.
<!-- claim:BEN-C18 -->

The LongMemEval repository exposes small, medium, and oracle data forms and configurable retrievers plus turn/session memory granularity.
<!-- claim:BEN-C19 -->

The MemoryAgentBench repository contains method/configuration directories and a linked Hugging Face dataset, supporting inspection of its framework-specific setup.
<!-- claim:BEN-C20 -->

The LongMemEval-V2 repository documents data download, preparation, validation, and leaderboard packaging that uses a fixed latency–accuracy frontier.
<!-- claim:BEN-C21 -->

Scores from static conversational QA, environment task success, tool grounding, and operation/security lifecycle metrics are not a common leaderboard because their task units, access paths, agent settings, and metrics differ.
<!-- claim:BEN-C22 -->

OmniMemEval and MemoryData are current evaluation-harness candidates; their public descriptions do not make them independent benchmark-score authorities.
<!-- claim:BEN-C23 -->

Memory Gym is a partially observable endless-task benchmark for RL agents and is a useful trajectory-memory boundary case rather than an LLM persistent-memory result source.
<!-- claim:BEN-C24 -->

A defensible internal agent-memory evaluation should report a vector of matched protocol-family outcomes and cost/latency rather than average results across incompatible benchmark groups.
<!-- claim:BEN-C25 -->

The structural-index study held Claude Opus 4.7 fixed and compared index-on, the same harness with the index off, and an agentic-grep harness across SWE-PolyBench Verified and SWE-bench Pro with three seeds and a leak-audited per-task sandbox.
<!-- claim:C09-C01 -->

In the structural-index artifact's released table, index-on versus index-off was 50.4% versus 41.9% resolve and 84.5% versus 44.3% agent-targeted localization@5, while per-cell mean cost was $1.15 versus $1.19; these are author-released results for one fixed model and the stated filtered sample, not a universal coding-memory ranking.
<!-- claim:C09-C02 -->

The supercoder-eval artifact can recompute released metrics and inspect scoring logic, but it cannot rerun agent generation or independently reconstruct localization and resolve from unreleased traces, so it is not a full end-to-end reproduction package.
<!-- claim:C09-C03 -->

PROJECTMEM represents project history as append-only typed events for issues, attempts, fixes, decisions, and notes, deterministically projects them into compact summaries served over MCP, and adds a pre-action gate for previously failed approaches or fragile files.
<!-- claim:C09-C04 -->

PROJECTMEM's reported evaluation is a two-month author self-study over 10 projects and 207 logged events, so it supports feasibility and inspectability but does not establish a causal task-success benefit against a matched no-memory baseline.
<!-- claim:C09-C05 -->

The AGENTS.md study reports that repository context files did not generally improve task success and increased inference cost by more than 20% on average across its tested agents, models, generated files, and developer-committed files.
<!-- claim:C09-C06 -->

The AGENTS.md authors conclude that context files are useful for non-standard coding practices but that performance claims require evaluation and human-written files should avoid unnecessary requirements; this is a boundary on passive context injection, not a refutation of all structured project memory.
<!-- claim:C09-C07 -->

RL Developer Memory keeps a deterministic ranker deployed, logs retrieval and feedback decisions, and permits a contextual-bandit residual policy to influence canary behavior only through conservative off-policy-evaluation and review gates.
<!-- claim:C09-C08 -->

In RL Developer Memory's same-commit 200-case author benchmark, deterministic control and the full shadow/OPE configuration both report 80.0% expected-decision accuracy and 100.0% hard-negative suppression; the paper also reports unsupported active learned-policy deployment and official-client MCP interoperability, a live latency regression, and 40 residual non-RL failures.
<!-- claim:C09-C09 -->

At pinned commit 3d8e3f379913d49585ba126d090f5501de9c079d, projectmem exposes separate storage, search, summary, staleness, redaction, MCP-server, command, and test modules; v09 inspected this structure but did not execute the package or tests.
<!-- claim:C09-C10 -->

At pinned commit 89e4156ba11538a8be0e2343d215bdff778550ed, supercoder-eval separates released metrics, analysis, scoring, an exclusion ledger, and paper source; v09 found no CI or test directory in the inspected tree and did not execute the analysis.
<!-- claim:C09-C11 -->

C09 is not one storage problem: the retained evidence separates at least structural code indexes, event-sourced project judgments, passive repository instruction files, and feedback-conditioned developer policies, each with different write triggers, read paths, and evaluation units.
<!-- claim:C09-C12 -->

The positive structural-index ablation and negative repository-context-file study make the effect of coding memory conditional on representation, workload, and intervention point rather than on persistence or extra context alone.
<!-- claim:C09-C13 -->

Reflexion stores linguistic reflections on task feedback in an episodic memory buffer rather than updating model weights.
<!-- claim:EXP-C01 -->

Generative Agents stores a complete natural-language experience record, synthesizes higher-level reflections over time, and retrieves memories dynamically for planning.
<!-- claim:EXP-C02 -->

Voyager's persistent object is an ever-growing library of executable code skills, making its reusable unit a compositional behavior rather than a retrieved prose episode.
<!-- claim:EXP-C03 -->

MemGPT treats long-term memory primarily as virtual-context control: it moves information across memory tiers and uses interrupts to manage control flow.
<!-- claim:EXP-C04 -->

INMS proposes an asynchronous multi-agent shared conversational pool composed of real-time filtering, storage, retrieval, and a retrieval mediator refined from interaction history.
<!-- claim:EXP-C05 -->

Collaborative Memory distinguishes private fragments from selectively shared fragments and attaches provenance plus time-varying read and write policies to the sharing boundary.
<!-- claim:EXP-C06 -->

AriGraph constructs and updates a graph that integrates semantic and episodic memories while an agent explores an environment.
<!-- claim:EXP-C08 -->

MemP distills past trajectories into both step-by-step instructions and higher-level script-like abstractions, with explicit build, retrieval, and update strategies.
<!-- claim:EXP-C09 -->

MemSkill's self-evolving object is a set of memory-operation skills: a controller selects skills, an executor creates skill-guided memories, and a designer revises the skill set from hard cases.
<!-- claim:EXP-C10 -->

XSkill keeps action-level experiences and task-level skills as two visually grounded knowledge streams, accumulating them from rollouts and adapting retrieved knowledge to the current visual context.
<!-- claim:EXP-C11 -->

POLAR separates personalized semantic context and visual concepts from episodic embodied trajectories within a multimodal knowledge graph.
<!-- claim:EXP-C12 -->

On STALE's stated 400 conflict scenarios and 1,200 queries, the authors report that even the best evaluated model reached 55.2% overall accuracy, exposing a gap between retrieving updated evidence and acting on it.
<!-- claim:EXP-C13 -->

WorldLines reports persistent difficulties from partial observability, overwritten world state, and translating remembered state into embodied plans.
<!-- claim:EXP-C14 -->

In the authors' DunphyBench comparison, MeMento's preference-conditioned fixed-token compressor improved accuracy by 7.18% and reduced memory usage by 85.38% versus the stated strongest baseline.
<!-- claim:EXP-C15 -->

Experience/procedural memory is defined by a behavior-changing reusable artifact—reflection, instruction, script, or executable skill—not by persistence alone.
<!-- claim:EXP-C16 -->

Self-evolution is not one mechanism: MemP updates remembered procedures from task experience, whereas MemSkill evolves the policy that extracts, consolidates, and prunes memories.
<!-- claim:EXP-C17 -->

A shared store becomes organizational memory only when it defines sharing scope and authority; a conversational pool alone does not specify private-versus-shared visibility, provenance, or revocation semantics.
<!-- claim:EXP-C18 -->

Personalization and identity continuity are user-/agent-specific state problems, while multi-agent memory is a principal-and-scope problem; they intersect when personal facts must be shared selectively across agents.
<!-- claim:EXP-C19 -->

Multimodal/embodied memory adds observation grounding, visibility, spatial/world state, and action consequences; it is not simply a larger textual user profile or a generic skill bank.
<!-- claim:EXP-C20 -->

Benchmark results across procedural, personalized-conflict, and embodied-state settings should not be ranked together because their tasks, inputs, interventions, and success criteria differ.
<!-- claim:EXP-C21 -->

The inspected repositories provide implementation evidence for several distinct data flows—skill-file distillation, trace-to-playbook consolidation, layered team memory, and a scoped shared representation—but none is independent evidence of adoption, safety, or comparative performance.
<!-- claim:EXP-C22 -->

Self-evolving skill systems create an evidence-promotion security boundary because an untrusted trajectory contributor can cause repeated experience to be normalized into persistent trusted procedural instructions; the paper formalizes success as Inclusion, Evolution Attribution, and Realization.
<!-- claim:FM-PE-C01 -->

In the authors' SkillClaw evaluation at 10% attacker support, PoisonedEvolution embedded target behaviors in 546 of 600 completed trials (91.0% SER) across six evolvers and four behavior families.
<!-- claim:FM-PE-C02 -->

On the structurally different Trace2Skill pipeline at the same 10% support ratio, the authors report 369 of 600 successful embeddings (61.5% SER), showing transfer across the two evaluated evolution architectures.
<!-- claim:FM-PE-C03 -->

The paper's pilot provenance-diversity gate blocked 25/25 single-cluster F1 candidates in one n=30,k=3 setting while accepting one five-session diverse control, but the paper itself calls the result preliminary.
<!-- claim:FM-PE-C04 -->

The evaluated SER measures durable artifact modification, not trigger activation, harmful action execution, credential theft, exfiltration, destructive effects, or a complete utility-security frontier.
<!-- claim:FM-PE-C05 -->

Generative Agents stores a natural-language record of experience, synthesizes higher-level reflections over time, and dynamically retrieves memories for planning.
<!-- claim:FND-C01 -->

Generative Agents documents a memory stream with retrieval, reflection and planning; this report uses it as historical lineage rather than as evidence for a general update, deletion, rollback or retention-control contract.
<!-- claim:FND-C02 -->

MemGPT introduces virtual-context management: it moves information across memory tiers and uses interrupts to manage control flow around an LLM with limited context.
<!-- claim:FND-C03 -->

The inspected letta-ai/letta README identifies the repository as formerly MemGPT but says it contains the legacy Letta V1 server and that active development moved to letta-code.
<!-- claim:FND-C04 -->

MemoryBank separates storage, retrieval, and updating; its store includes conversation records, event summaries, and evolving user-personality assessments.
<!-- claim:FND-C05 -->

MemoryBank's updater is inspired by an Ebbinghaus forgetting curve and selectively reinforces or forgets memory using elapsed time and relative importance.
<!-- claim:FND-C06 -->

Reflexion is a useful procedural-memory boundary: its official artifact provides code, demos, and task logs for verbal-reflection experiments, but does not thereby establish a general persistent-state lifecycle system.
<!-- claim:FND-C07 -->

Voyager supplies a complementary procedural form of memory—an executable skill library—so reusable skills should not be conflated with mutable user facts or episodic traces.
<!-- claim:FND-C08 -->

A-MEM proposes agentic note construction with structured attributes, dynamic links to relevant history, and updates to historical contextual representations as new memories are integrated.
<!-- claim:FND-C09 -->

The A-mem system repository explicitly distinguishes agent-construction code from a separate repository intended to reproduce the paper's evaluation results.
<!-- claim:FND-C10 -->

MemoryOS specifies short-, mid-, and long-term personal-memory tiers, with Storage, Updating, Retrieval, and Generation modules.
<!-- claim:FND-C11 -->

The inspected MemoryOS implementation exposes distinct ChromaDB, MCP, playground, PyPI, and evaluation directories, showing an integration-oriented decomposition rather than only a paper artifact.
<!-- claim:FND-C12 -->

MemoryAgentBench frames memory-agent assessment as four competencies: accurate retrieval, test-time learning, long-range understanding, and selective forgetting, in incremental multi-turn interactions.
<!-- claim:FND-C13 -->

MemCon models memory operations as an MDP and learns an online policy over retrieve, plan injection, re-retrieve, consolidate, forget, and no-op actions.
<!-- claim:FND-C14 -->

MemCon's authors describe the controller as backend-agnostic and based on task-by-task binary feedback, a tabular contextual bandit, UCB exploration, no pretraining, and no additional LLM calls.
<!-- claim:FND-C15 -->

In the MemCon preprint, authors report up to 15.2 percentage points higher task success and 5–20% lower token consumption across their stated six-benchmark, three-framework, three-backbone evaluation; this is not an independent reproduction.
<!-- claim:FND-C16 -->

MemTxn places a transaction boundary outside the answer model with source-supported write validation, temporal version selection, and a durable snapshot journal for application-visible recovery.
<!-- claim:FND-C17 -->

MemTxn's reported recovery and FactConsolidation results are author-reported preprint evidence under the paper's declared audits and answer-model configurations, not a general proof of reliable memory transactions.
<!-- claim:FND-C18 -->

The budgeted-consolidation preprint argues that retention preserves raw details while consolidation improves coverage per token but may lose query-critical detail; it treats the preferred operator as budget-dependent.
<!-- claim:FND-C19 -->

The same preprint explicitly limits its formal utility decomposition to a surrogate under stated assumptions and does not claim a universal ranking of Merge, Abstract, and Rewrite.
<!-- claim:FND-C20 -->

ForgetEval's authors distinguish recall from mutation-plane operations such as supersede, release, and purge, and compare thirteen configurations with partly complementary failure-mode coverage.
<!-- claim:FND-C21 -->

ForgetEval's reported LLM-hook gains and costs are model- and protocol-dependent author results; its paper itself records limited external-subset evidence, backend gaps, and LLM-quality sensitivity.
<!-- claim:FND-C22 -->

Across the inspected systems, a useful architecture split is a data plane (records/tiers), a retrieval plane (selection/injection), and a mutation/control plane (admission, consolidation, supersede, forget, recovery); this is a report synthesis rather than a claim made verbatim by any one source.
<!-- claim:FND-C23 -->

代表性工程已从“向量库加相似度搜索”扩展为复合记忆管线：Mem0 的当前自述把事实抽取、实体链接、BM25/语义融合与时间排序放在同一链路；Cognee 与 Neo4j Agent Memory 则把向量检索、知识图谱、关系抽取和审计/整合能力组合起来。
<!-- claim:GR-C-M001 -->

“写入什么”和“读出什么”已经成为两个独立控制面：A-Mem 在写入侧做动态组织与演化，MemChain 在读出侧显式决定 keep/drop/refine/merge 并生成可检查的 memory trace。
<!-- claim:GR-C-M002 -->

工程路线并未收敛到单一表示：OpenViking 用 viking:// 虚拟文件系统和 L0/L1/L2 分层加载，MemPalace 保留逐字文本并允许替换检索后端，OptMem 则选择 append-only 日志加正则召回。
<!-- claim:GR-C-M003 -->

上下文压缩与长期事实记忆是相邻但不同的工程层：Headroom 在模型前压缩工具输出、日志、代码和历史并保留可逆取回；Claude-Mem 从编码会话中提取观察与语义摘要；LightMem 同时提供记忆管理、MCP 和基准脚本。
<!-- claim:GR-C-M004 -->

程序性记忆的工程目标是把成功轨迹变成可复用策略或技能，而不只是保存对话：MemRL 把反馈效用引入两阶段检索，Hivemind 从团队轨迹提炼技能，TencentDB Agent Memory 把会话和工具轨迹转成可审核、可分享的 Skill 资产。
<!-- claim:GR-C-M005 -->

个性化记忆正在从单一 user profile 扩展为多层状态：MIRIX 分出 core/episodic/semantic/procedural/resource/knowledge-vault，OpenHuman 把个人数据压缩为本地图结构，MineEcho 同时保留交互记忆、周期摘要、Wiki/图与技能路由。
<!-- claim:GR-C-M006 -->

编码代理记忆形成了三种互补路径：Claude-Mem 保存会话观察与摘要，codebase-memory-mcp 把代码解析为可查询结构图，Brain0 把提交、符号、代理轨迹与风险/意图连成决策图。
<!-- claim:GR-C-M007 -->

“可移植”至少有三种互不等价的实现：OMP 规定 memory object/storage/HTTP API，Agent File 序列化 prompt、editable memory、tools 与模型设置，EverOS/memU 则把 Markdown/Wiki 作为跨代理可读写资产。
<!-- claim:GR-C-M008 -->

安全工程已经覆盖“攻击—运行时阻断—审计”三层：AgentPoison 提供 memory/knowledge-base poisoning 的红队代码，OWASP Agent Memory Guard 在存取路径上执行检测器与策略，Brain0 增加敏感读取和来源/意图审计。
<!-- claim:GR-C-M009 -->

评测仓库正在拆开以往混在一起的能力：MemoryAgentBench 关注增量多轮交互中的检索、测试时学习等能力；OmniMemEval 分为 memory-backend API 与带插件 agent runtime 两条轨；PrecisionMemBench 单独检查精度、噪声隔离和会话延迟。
<!-- claim:GR-C-M010 -->

具身记忆仍是工程证据薄弱的边界：MemoryVLA 仓库提供 paper-linked 机器人操控代码与多个分支，但 PHILIA 在本轮检查的论文页面和三条精确 GitHub repository 查询中没有出现可核实的 canonical repository。
<!-- claim:GR-C-M011 -->

仓库热度与当前实现位置可能分离：letta-ai/letta 的固定 README 明确称该仓库为 legacy server，并把活跃开发指向 letta-code/App Server，因此其累计 stars 不能直接代表当前代码面的活跃度。
<!-- claim:GR-C-M012 -->

microsoft/kernel-memory 当前应作为历史/集成谱系而非活跃候选：其固定 README 自称 archived research project、无支持、非 production software。
<!-- claim:GR-C-M013 -->

本轮 GitHub code-search 的有限抽样在目标仓库之外、且至少一个不同 owner 的公开仓库中核实了 mem0ai、letta-client、cognee、memvid、basic-memory、Microsoft.KernelMemory、hindsight-client 与 LightMem 的依赖或集成文本；这些只证明存在公开代码引用，不证明生产部署、用户规模或效果。
<!-- claim:GR-C-M014 -->

部署边界没有形成单一共识：Mem0 同时提供 library/self-hosted/cloud，Neo4j Agent Memory 保持 hosted NAMS 与 self-hosted Bolt 的同 API，OpenHuman 与 MineEcho 强调 local-first，而 Hindsight 推荐容器/服务加客户端。
<!-- claim:GR-C-M015 -->

README 中常见的 add/remember、search/recall、forget/update 等动词形成了事实上的最小接口共识，但底层语义差异很大：有的返回文本片段，有的返回图上下文，有的还执行 reflect/consolidate 或 skill promotion。
<!-- claim:GR-C-M016 -->

最小实现仍有明确位置：OptMem 的 append-only 文件加 regex、MemPalace 的逐字保存、Agent File 的单文件序列化分别优先可检查性、保真和迁移；它们提醒工程选择不应默认把图、LLM consolidation 和托管服务全部叠加。
<!-- claim:GR-C-M017 -->

Long-Term-Memory-API 实际解析为 MemVault/GraphRAG 托管 API 仓库，并在 README 中声明定时 consolidation、pgvector hybrid search 与图抽取；但其最近 push 不在本轮 90 天窗口，且没有独立部署证据，因此只进入观察名单。
<!-- claim:GR-C-M018 -->

本轮对 59 个候选仓库完成了完整 GitHub 状态观测；其中 19 个创建于滚动 90 天内，39 个创建于滚动 12 个月内，54 个在滚动 90 天内有 push。
<!-- claim:GR-C-RUN01 -->

在 59 个固定 SHA 工程卡中，46 个返回可识别 SPDX license，39 个有 latest release，40 个检查到 CI workflow，53 个检查到测试路径，40 个在 90 天提交窗口内有至少两名可归属贡献者；1 个 tree/README 深检为 partial。
<!-- claim:GR-C-RUN02 -->

所有 bundle 内 GitHub stars 数据都来自同一轮单快照；因此本报告不从这些 GitHub snapshots 计算或声称任何仓库的 star growth、velocity 或 acceleration。
<!-- claim:GR-C-RUN03 -->

本轮只对 10 个目标运行了有界 GitHub code-search adoption 查询，其中 9 个查询保留了目标仓库之外的可核实公开代码引用；不同 owner 不保证组织独立，其余仓库的独立部署证据保持未验证。
<!-- claim:GR-C-RUN04 -->

At the 2026-08-10T05:07:13Z GitHub snapshot, letta-ai/letta was created 2023-10-11, last pushed 2026-08-01, pinned at ff19ffeafeb54bd2a7dc5d4a552f10191732a235, had 24170 cumulative stars, and had latest release 0.16.8 on 2026-05-14; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C001-1 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, the inspected engineering surface for letta-ai/letta was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C001-2 -->

The repository's own GitHub metadata describes letta-ai/letta as: “Platform for stateful agents: AI with advanced memory that can learn and self-improve over time.”
<!-- claim:GR-C001-3 -->

At the 2026-08-10T05:07:45Z GitHub snapshot, mem0ai/mem0 was created 2023-06-20, last pushed 2026-08-07, pinned at 4debc58a83377b18be81ae1e5969a300736b2fac, had 62901 cumulative stars, and had latest release v2.0.17 on 2026-08-05; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C002-1 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, the inspected engineering surface for mem0ai/mem0 was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C002-2 -->

The repository's own GitHub metadata describes mem0ai/mem0 as: “Universal memory layer for AI Agents”
<!-- claim:GR-C002-3 -->

At the 2026-08-10T05:07:57Z GitHub snapshot, Sibyl-Labs/Sibyl-Memory was created 2026-05-20, last pushed 2026-08-07, pinned at e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, had 98 cumulative stars, and had latest release v0.1.0 on 2026-05-21; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C003-1 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, the inspected engineering surface for Sibyl-Labs/Sibyl-Memory was setup=documented, CI=present, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C003-2 -->

The repository's own GitHub metadata describes Sibyl-Labs/Sibyl-Memory as: “Durable, file-based long-term memory for AI agents. Five-package plugin family: SDK, CLI, MCP server, Hermes adapter, and a LangGraph BaseStore.…”
<!-- claim:GR-C003-3 -->

At the 2026-08-10T05:08:02Z GitHub snapshot, memvid/memvid was created 2025-05-27, last pushed 2026-07-14, pinned at e6bd9f7b9c38cd8d5370fa0fc936ac1dcd751813, had 16197 cumulative stars, and had latest release v2.0.140 on 2026-05-27; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C004-1 -->

At the 2026-08-10T05:08:15Z GitHub snapshot, redis/agent-memory-server was created 2025-03-14, last pushed 2026-08-09, pinned at 886437963dc02289e828872f0ae21fdaa734c337, had 304 cumulative stars, and had latest release server/v0.15.2 on 2026-04-10; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C005-1 -->

At the 2026-08-10T05:09:43Z GitHub snapshot, xerj-org/xerj was created 2026-06-30, last pushed 2026-08-10, pinned at c52c562ae5cedae3feed3f590409cf07e929197a, had 1321 cumulative stars, and had latest release v1.0.0-rc.13 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C006-1 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, the inspected engineering surface for xerj-org/xerj was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C006-2 -->

The repository's own GitHub metadata describes xerj-org/xerj as: “XERJ is the new way for AI to search data. Its autoindex capability activates agents to know your data without…”
<!-- claim:GR-C006-3 -->

At the 2026-08-10T05:11:36Z GitHub snapshot, topoteretes/cognee was created 2023-08-16, last pushed 2026-08-09, pinned at a148eab58eb2f9769585f10da5486543c9ece457, had 29898 cumulative stars, and had latest release v1.4.2 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C008-1 -->

At the 2026-08-10T05:11:44Z GitHub snapshot, OSU-NLP-Group/HippoRAG was created 2024-05-23, last pushed 2026-07-29, pinned at c617143f01477243992a63b2e2151cc003dd3b21, had 3929 cumulative stars, and had latest release v1.0.0 on 2025-02-27; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C009-1 -->

At the 2026-08-10T05:11:54Z GitHub snapshot, JingxuanC/causal-memory was created 2026-07-26, last pushed 2026-08-10, pinned at 054af36507537f7b616fa41db07be483cc6e55c3, had 30 cumulative stars, and had latest release v0.3.1 on 2026-07-26; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C010-1 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, the inspected engineering surface for JingxuanC/causal-memory was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C010-2 -->

The repository's own GitHub metadata describes JingxuanC/causal-memory as: “Causal memory layer for AI agents — MCP server that records decision→outcome relationships. Survives compaction.”
<!-- claim:GR-C010-3 -->

At the 2026-08-10T05:12:12Z GitHub snapshot, aiming-lab/SimpleMem was created 2026-01-01, last pushed 2026-07-24, pinned at db80b6a7c591e0ea730a058e9f5fc4eb06572299, had 3685 cumulative stars, and had latest release v0.3.0 on 2026-05-21; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C011-1 -->

At the 2026-08-10T05:12:14Z GitHub snapshot, noamschwartz/atlas-memory-demo was created 2026-05-26, last pushed 2026-07-28, pinned at 0bd36a7b177a09aad97dc78efeb5fb43b9322f6d, had 93 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C012-1 -->

At pinned commit 0bd36a7b177a09aad97dc78efeb5fb43b9322f6d, the inspected engineering surface for noamschwartz/atlas-memory-demo was setup=documented, CI=present, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C012-2 -->

At the 2026-08-10T05:12:35Z GitHub snapshot, WujiangXu/A-mem was created 2025-01-30, last pushed 2026-03-05, pinned at 0c8039f28fdcc08189a23c07a3437d9d2482f9c2, had 939 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C014-1 -->

At the 2026-08-10T05:12:50Z GitHub snapshot, mayiwen0212/MemChain was created 2026-06-29, last pushed 2026-06-30, pinned at 990ebea20518362606a558e60c6056d4a84621d2, had 97 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C015-1 -->

At pinned commit 990ebea20518362606a558e60c6056d4a84621d2, the inspected engineering surface for mayiwen0212/MemChain was setup=manifest-present, CI=not-found-in-inspected-tree, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C015-2 -->

At the 2026-08-10T05:13:51Z GitHub snapshot, volcengine/OpenViking was created 2026-01-05, last pushed 2026-08-10, pinned at 7f6085a2f95c8a79ec4eb82f973cae57628341a9, had 28136 cumulative stars, and had latest release python-sdk@0.1.7 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C016-1 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, the inspected engineering surface for volcengine/OpenViking was setup=documented, CI=present, tests=present, license=AGPL-3.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C016-2 -->

The repository's own GitHub metadata describes volcengine/OpenViking as: “Self-evolving Context Database for AI Agents. Unify Agent Memory, Knowledge RAG and Skills.”
<!-- claim:GR-C016-3 -->

At the 2026-08-10T05:14:07Z GitHub snapshot, VictorTaelin/OptMem was created 2026-07-25, last pushed 2026-07-31, pinned at 1fb164cf39028047781f72ac3bb1e5a691c1dcb0, had 1185 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C018-1 -->

At pinned commit 1fb164cf39028047781f72ac3bb1e5a691c1dcb0, the inspected engineering surface for VictorTaelin/OptMem was setup=documented, CI=not-found-in-inspected-tree, tests=not-found-in-inspected-tree, license=unknown, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C018-2 -->

At the 2026-08-10T05:14:19Z GitHub snapshot, zjunlp/LightMem was created 2025-06-11, last pushed 2026-08-06, pinned at 8fc9a9179f9170c4a40fc653fcb410375900f26e, had 1078 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C019-1 -->

At the 2026-08-10T05:14:45Z GitHub snapshot, thedotmack/claude-mem was created 2025-08-31, last pushed 2026-08-10, pinned at 4702c337d85aa12e8ab7f845264a78885676261f, had 90236 cumulative stars, and had latest release v13.14.0 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C020-1 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, the inspected engineering surface for thedotmack/claude-mem was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C020-2 -->

The repository's own GitHub metadata describes thedotmack/claude-mem as: “Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and…”
<!-- claim:GR-C020-3 -->

At the 2026-08-10T05:12:29Z GitHub snapshot, Mirix-AI/MIRIX was created 2025-04-11, last pushed 2026-07-25, pinned at 51f3342d5366b0e215439581f92e0323227146af, had 3547 cumulative stars, and had latest release v0.1.6 on 2025-12-25; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C021-1 -->

At the 2026-08-10T05:12:35Z GitHub snapshot, zjunlp/LightMem-Ego was created 2026-05-20, last pushed 2026-07-28, pinned at b6aa0f719d95acfc3d92ebe338bf31fcf97bfd10, had 65 cumulative stars, and had latest release v1.0.0 on 2026-07-14; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C022-1 -->

At pinned commit b6aa0f719d95acfc3d92ebe338bf31fcf97bfd10, the inspected engineering surface for zjunlp/LightMem-Ego was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C022-2 -->

At the 2026-08-10T05:12:45Z GitHub snapshot, basicmachines-co/basic-memory was created 2024-12-02, last pushed 2026-08-10, pinned at 940acff61a8eb5e2c3991c3bf4a8bb8009db45d1, had 3612 cumulative stars, and had latest release skills-latest on 2026-07-15; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C023-1 -->

At the 2026-08-10T05:12:50Z GitHub snapshot, campfirein/byterover-cli was created 2025-06-19, last pushed 2026-06-25, pinned at 1052ac1a5dd0fde4da8693d4712064f7876c269c, had 4937 cumulative stars, and had latest release v3.16.1 on 2026-05-27; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C024-1 -->

At the 2026-08-10T05:12:43Z GitHub snapshot, memorax-ai/memorax-code was created 2026-08-01, last pushed 2026-08-10, pinned at 13aefc8ba6cc1d2ae821e2619a7d4dd00d3c3276, had 169 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C025-1 -->

At pinned commit 13aefc8ba6cc1d2ae821e2619a7d4dd00d3c3276, the inspected engineering surface for memorax-ai/memorax-code was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C025-2 -->

At the 2026-08-10T05:13:25Z GitHub snapshot, Coding-Dev-Tools/engraphis was created 2026-06-30, last pushed 2026-08-10, pinned at 128fe0515b842923df871a777eaacc3327f40513, had 153 cumulative stars, and had latest release v1.5 on 2026-08-06; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C026-1 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, the inspected engineering surface for Coding-Dev-Tools/engraphis was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C026-2 -->

The repository's own GitHub metadata describes Coding-Dev-Tools/engraphis as: “Local-first, inspectable memory for coding agents: durable context across sessions and repositories, code-aware recall, bi-temporal history, MCP, and a self-hosted…”
<!-- claim:GR-C026-3 -->

At the 2026-08-10T05:12:54Z GitHub snapshot, CraftJarvis/JARVIS-1 was created 2023-10-21, last pushed 2024-04-08, pinned at aa9bd97debee045cb35b37564c71dee4c465b9ad, had 408 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C027-1 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, the inspected engineering surface for CraftJarvis/JARVIS-1 was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=unknown, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C027-2 -->

The repository's own GitHub metadata describes CraftJarvis/JARVIS-1 as: “JARVIS-1: Open-world Multi-task Agents with Memory-Augmented Multimodal Language Models”
<!-- claim:GR-C027-3 -->

At the 2026-08-10T05:12:58Z GitHub snapshot, shihao1895/MemoryVLA was created 2025-08-24, last pushed 2026-06-13, pinned at d732ea9072bc063399ccc817aed74ab172eb50be, had 316 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C028-1 -->

At pinned commit d732ea9072bc063399ccc817aed74ab172eb50be, the inspected engineering surface for shihao1895/MemoryVLA was setup=documented, CI=not-found-in-inspected-tree, tests=not-found-in-inspected-tree, license=unknown, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C028-2 -->

The repository's own GitHub metadata describes shihao1895/MemoryVLA as: “[ICLR 2026] Code of "MemoryVLA: Perceptual-Cognitive Memory in Vision-Language-Action Models for Robotic Manipulation"”
<!-- claim:GR-C028-3 -->

At the 2026-08-10T05:13:14Z GitHub snapshot, EverMind-AI/EverOS was created 2025-10-28, last pushed 2026-08-07, pinned at 48fc9084888bc17100053227284f939a5aca5e91, had 11939 cumulative stars, and had latest release v1.2.3 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C029-1 -->

At the 2026-08-10T05:13:10Z GitHub snapshot, SMJAI/open-memory-protocol was created 2026-06-29, last pushed 2026-07-02, pinned at 2f91247accde20feab9718790aa8a06c077e32bd, had 73 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C030-1 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, the inspected engineering surface for SMJAI/open-memory-protocol was setup=documented, CI=present, tests=present, license=NOASSERTION, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C030-2 -->

The repository's own GitHub metadata describes SMJAI/open-memory-protocol as: “An open standard for portable, interoperable AI memory across tools, sessions, and devices.”
<!-- claim:GR-C030-3 -->

At the 2026-08-10T05:13:18Z GitHub snapshot, TencentCloud/TencentDB-Agent-Memory was created 2026-04-07, last pushed 2026-08-06, pinned at fe3230f176f1bf5832fee79d12494bbc2d19a8aa, had 18945 cumulative stars, and had latest release v2.0.0 on 2026-08-03; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C031-1 -->

At the 2026-08-10T05:13:22Z GitHub snapshot, AI-secure/AgentPoison was created 2024-03-22, last pushed 2026-06-17, pinned at f859b503318b450d158662f78d761e2918a05259, had 233 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C032-1 -->

At pinned commit f859b503318b450d158662f78d761e2918a05259, the inspected engineering surface for AI-secure/AgentPoison was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C032-2 -->

The repository's own GitHub metadata describes AI-secure/AgentPoison as: “[NeurIPS 2024] Official implementation for "AgentPoison: Red-teaming LLM Agents via Memory or Knowledge Base Backdoor Poisoning"”
<!-- claim:GR-C032-3 -->

At the 2026-08-10T05:13:27Z GitHub snapshot, Brain0-ai/brain0 was created 2026-07-02, last pushed 2026-07-19, pinned at bf0998ca896e88deb32538b027ec06b59bbd42ed, had 368 cumulative stars, and had latest release v0.1.0 on 2026-07-02; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C034-1 -->

At pinned commit bf0998ca896e88deb32538b027ec06b59bbd42ed, the inspected engineering surface for Brain0-ai/brain0 was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C034-2 -->

At the 2026-08-10T05:13:28Z GitHub snapshot, HUST-AI-HYZ/MemoryAgentBench was created 2025-06-28, last pushed 2026-05-21, pinned at 455306dcabc3842526eb83cd4e225e5d486c5c5d, had 422 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C035-1 -->

At pinned commit 455306dcabc3842526eb83cd4e225e5d486c5c5d, the inspected engineering surface for HUST-AI-HYZ/MemoryAgentBench was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C035-2 -->

At the 2026-08-10T05:13:32Z GitHub snapshot, MemTensor/OmniMemEval was created 2026-06-24, last pushed 2026-08-06, pinned at 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, had 41 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C036-1 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, the inspected engineering surface for MemTensor/OmniMemEval was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C036-2 -->

The repository's own GitHub metadata describes MemTensor/OmniMemEval as: “Evaluation framework for benchmarking memory systems.”
<!-- claim:GR-C036-3 -->

At the 2026-08-10T05:13:38Z GitHub snapshot, tenurehq/precisionMemBench was created 2026-05-27, last pushed 2026-07-28, pinned at b95d6abb471c0d591c440172283dd74e7af000df, had 13 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C037-1 -->

At pinned commit b95d6abb471c0d591c440172283dd74e7af000df, the inspected engineering surface for tenurehq/precisionMemBench was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C037-2 -->

At the 2026-08-10T05:14:38Z GitHub snapshot, MemPalace/mempalace was created 2026-04-05, last pushed 2026-08-08, pinned at 8516db7fbc7f0840bf67132c5bf95c6e446d6acc, had 58263 cumulative stars, and had latest release v3.6.0 on 2026-07-17; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C038-1 -->

At the 2026-08-10T05:13:49Z GitHub snapshot, supermemoryai/supermemory was created 2024-02-27, last pushed 2026-08-10, pinned at 59b148e5b2d4f5b4e27c9a6351fb3a0224ed76f2, had 28834 cumulative stars, and had latest release server-v0.0.7-rc.2 on 2026-07-22; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C039-1 -->

At the 2026-08-10T05:16:59Z GitHub snapshot, headroomlabs-ai/headroom was created 2026-01-07, last pushed 2026-08-10, pinned at 2f2950a626cebf851aac29255e7188fbb1639f5a, had 65677 cumulative stars, and had latest release v0.34.0 on 2026-08-05; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C040-1 -->

At the 2026-08-10T05:15:28Z GitHub snapshot, DeusData/codebase-memory-mcp was created 2026-02-24, last pushed 2026-08-10, pinned at 4ed8d384f76b4945f1b50845d8b0e28c78ea304b, had 38323 cumulative stars, and had latest release v0.9.1-rc.1 on 2026-07-30; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C041-1 -->

At the 2026-08-10T05:16:53Z GitHub snapshot, tinyhumansai/openhuman was created 2026-02-18, last pushed 2026-08-09, pinned at 8774fe4a1221b695984921a0249263da4512aa81, had 36134 cumulative stars, and had latest release v0.63.12 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C042-1 -->

At the 2026-08-10T05:15:30Z GitHub snapshot, vectorize-io/hindsight was created 2025-10-30, last pushed 2026-08-10, pinned at 3a48b6e5bbbfd6c84ded1db23ee07b493d207b7d, had 19422 cumulative stars, and had latest release v0.9.0 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C043-1 -->

At the 2026-08-10T05:15:03Z GitHub snapshot, NevaMind-AI/memU was created 2025-07-29, last pushed 2026-08-09, pinned at 72150d9c2c491a659614cccd2d053ca542992117, had 14276 cumulative stars, and had latest release v2.0.0-beta.0 on 2026-07-23; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C044-1 -->

At the 2026-08-10T05:15:45Z GitHub snapshot, MemTensor/MemOS was created 2025-07-06, last pushed 2026-08-07, pinned at 8d310a7a4be6bbb9c04823a88f2ebaca6ae20baf, had 10662 cumulative stars, and had latest release memos-local-plugin-v2.0.14 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C045-1 -->

At the 2026-08-10T05:15:41Z GitHub snapshot, MaxFreedomPollard/Compartment was created 2026-07-20, last pushed 2026-08-09, pinned at 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, had 701 cumulative stars, and had latest release v4.5.0 on 2026-08-02; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C046-1 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, the inspected engineering surface for MaxFreedomPollard/Compartment was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C046-2 -->

The repository's own GitHub metadata describes MaxFreedomPollard/Compartment as: “Encrypted, fully offline agentic memory. One click install, GUI w/ memory map, all OS and agents. Superior memory creation, storage…”
<!-- claim:GR-C046-3 -->

At the 2026-08-10T05:15:40Z GitHub snapshot, AML-memory/agent-memory-leaderboard was created 2026-07-29, last pushed 2026-08-07, pinned at 5761ed58502d24153115cbdc010e44957cb18c3a, had 232 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C047-1 -->

At pinned commit 5761ed58502d24153115cbdc010e44957cb18c3a, the inspected engineering surface for AML-memory/agent-memory-leaderboard was setup=manifest-present, CI=not-found-in-inspected-tree, tests=not-found-in-inspected-tree, license=unknown, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C047-2 -->

At the 2026-08-10T05:15:51Z GitHub snapshot, letta-ai/agent-file was created 2025-03-23, last pushed 2026-03-24, pinned at 78212eb571e59e10b35b924375a997319b89c280, had 1193 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C048-1 -->

At the 2026-08-10T05:16:01Z GitHub snapshot, microsoft/kernel-memory was created 2023-07-13, last pushed 2026-06-08, pinned at 8fc4e16f31257faa34c5e368f8e99b45df7e4049, had 2174 cumulative stars, and had latest release packages-0.98.250508.3 on 2025-05-09; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C050-1 -->

At the 2026-08-10T05:16:03Z GitHub snapshot, mnemox-ai/tradememory-protocol was created 2026-02-23, last pushed 2026-07-30, pinned at df74662939e931baae7d7dab2be1ad8e716180ea, had 1408 cumulative stars, and had latest release v0.5.4 on 2026-07-28; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C051-1 -->

At the 2026-08-10T05:16:00Z GitHub snapshot, supermemoryai/memorybench was created 2025-09-17, last pushed 2026-08-06, pinned at 118209a746d97d0d85e5a7234267f0b6962857e9, had 304 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C052-1 -->

At pinned commit 118209a746d97d0d85e5a7234267f0b6962857e9, the inspected engineering surface for supermemoryai/memorybench was setup=documented, CI=not-found-in-inspected-tree, tests=not-found-in-inspected-tree, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C052-2 -->

At the 2026-08-10T05:16:18Z GitHub snapshot, CortexReach/memory-lancedb-pro was created 2026-02-24, last pushed 2026-08-09, pinned at ba9928f733f4a4d6b61f88763880db9cb7969feb, had 4460 cumulative stars, and had latest release v1.1.0-beta.10 on 2026-03-23; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C053-1 -->

At the 2026-08-10T05:16:08Z GitHub snapshot, jakops88-hub/Long-Term-Memory-API was created 2025-11-20, last pushed 2025-12-17, pinned at 00a71193475dc3bbbbbcbaceb32dae7ce6a7c621, had 72 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C054-1 -->

At the 2026-08-10T05:18:48Z GitHub snapshot, activeloopai/hivemind was created 2026-04-03, last pushed 2026-07-30, pinned at 7d17a412e983d00d86e8146a311eff017eb9f4f4, had 1541 cumulative stars, and had latest release v0.7.145 on 2026-07-30; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C055-1 -->

At the 2026-08-10T05:17:28Z GitHub snapshot, Health-Yang/MineEcho was created 2026-05-28, last pushed 2026-06-05, pinned at bd04d2873700c9fb36b2b44641455567721a2a58, had 245 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C056-1 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, the inspected engineering surface for Health-Yang/MineEcho was setup=documented, CI=present, tests=present, license=NOASSERTION, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C056-2 -->

The repository's own GitHub metadata describes Health-Yang/MineEcho as: “Local-first Memory OS for personal AI assistants with L0-L3 memory, Wiki++ knowledge, skill routing, and TokenLess context compression.”
<!-- claim:GR-C056-3 -->

At the 2026-08-10T05:17:37Z GitHub snapshot, 410979729/scope-recall-hermes was created 2026-05-15, last pushed 2026-08-08, pinned at 867b9939e037299befd930647a5015ee6e4945c0, had 220 cumulative stars, and had latest release v1.9.1 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C057-1 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, the inspected engineering surface for 410979729/scope-recall-hermes was setup=documented, CI=present, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C057-2 -->

The repository's own GitHub metadata describes 410979729/scope-recall-hermes as: “Hermes Agent memory plugin/provider for scope-aware recall, SQLite truth, LanceDB semantic search, and hybrid retrieval.”
<!-- claim:GR-C057-3 -->

At the 2026-08-10T05:17:42Z GitHub snapshot, atomicstrata/atomicmemory was created 2026-05-18, last pushed 2026-08-09, pinned at 683bd92c9c77877962d7425e27b50cb83867fd9e, had 421 cumulative stars, and had latest release cli-v0.2.0 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C058-1 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, the inspected engineering surface for atomicstrata/atomicmemory was setup=documented, CI=present, tests=present, license=NOASSERTION, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C058-2 -->

The repository's own GitHub metadata describes atomicstrata/atomicmemory as: “Portable semantic memory for AI agents: core engine, TypeScript SDK, framework adapters, MCP server, CLI, and host plugins.”
<!-- claim:GR-C058-3 -->

At the 2026-08-10T05:17:49Z GitHub snapshot, EverMind-AI/Raven was created 2026-05-21, last pushed 2026-08-10, pinned at 14b7419245b816782b0435385d238f9f18ac090f, had 3532 cumulative stars, and had latest release v0.1.10 on 2026-07-31; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C059-1 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, the inspected engineering surface for EverMind-AI/Raven was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C059-2 -->

The repository's own GitHub metadata describes EverMind-AI/Raven as: “The memory-first, self-improving agent harness built on EverOS, with MiroThinker-powered deep research and reasoning.”
<!-- claim:GR-C059-3 -->

AgentPoison authors model a backdoor attack that poisons long-term memory or a RAG knowledge base.
<!-- claim:OPS-C01 -->

In AgentPoison's reported three-agent evaluation, average attack success exceeded 80% with poison rate below 0.1% and benign-performance impact below 1%.
<!-- claim:OPS-C02 -->

The ACL 2025 MEXTRA paper studies black-box extraction of private information from an agent memory module.
<!-- claim:OPS-C03 -->

MINJA is a query-and-observation-only memory-injection attack in its authors' threat model.
<!-- claim:OPS-C04 -->

eTAMP reports cross-session, cross-site compromise from an environmental observation without direct memory access.
<!-- claim:OPS-C05 -->

eTAMP's authors report that environmental stress increased attack success by up to eight times in their experiments.
<!-- claim:OPS-C06 -->

Sleeper-memory poisoning is evaluated as a write, later retrieval, and later action chain rather than a single prompt response.
<!-- claim:OPS-C07 -->

The sleeper-memory paper reports attacker-intended actions in 60–89% of its successful-retrieval evaluations.
<!-- claim:OPS-C08 -->

The MPBench study identifies four memory write channels and nine structural vulnerabilities in its taxonomy.
<!-- claim:OPS-C09 -->

MAFIA is explicitly designed for query-only attack settings with benign-memory pools and active input auditing.
<!-- claim:OPS-C10 -->

Salami Attack studies collusive memory fragments that are individually benign-looking but jointly harmful.
<!-- claim:OPS-C11 -->

MutMem binds nontrivial retrieval-weight changes to signed, predecessor-linked provenance transitions.
<!-- claim:OPS-C12 -->

MutMem's authors state that authorization and traceability do not establish content truth.
<!-- claim:OPS-C13 -->

DP-MemView formalizes cumulative leakage through repeated memory-conditioned responses as adaptive transcript privacy.
<!-- claim:OPS-C14 -->

DP-MemView exposes a selected public conditioning view rather than raw memory to the response model under its stated interface contract.
<!-- claim:OPS-C15 -->

STALE names the case where stored state is updated but a response still plans around the old value an implicit policy adaptation gap.
<!-- claim:OPS-C16 -->

StateAuditor verifies provenance and chronology of proposed transitions, not semantic supersession.
<!-- claim:OPS-C17 -->

Microsoft Foundry Memory preview documents memory-item CRUD, default retention/TTL, and a direct remember-or-forget command.
<!-- claim:OPS-C18 -->

Microsoft Foundry documents a scope parameter that segments memory across users.
<!-- claim:OPS-C19 -->

AWS Bedrock Agents Classic documents a caller-provided memoryId as the association key for a user's retained memory.
<!-- claim:OPS-C20 -->

AWS documents clearing Classic-agent memory by deleting stored sessions.
<!-- claim:OPS-C21 -->

Google documents Memory Bank operations for generated/uploaded memory retrieval, revision inspection, and IAM Conditions access control.
<!-- claim:OPS-C22 -->

Google documents that Memory Bank's generation processing occurs in the model endpoint's region or multi-region.
<!-- claim:OPS-C23 -->

OWASP Agent Memory Guard documents a write path through detectors and declarative policy, with snapshot-backed rollback/forensics.
<!-- claim:OPS-C24 -->

OWASP Agent Memory Guard documents source-class provenance carried into SecurityEvent records.
<!-- claim:OPS-C25 -->

mem0's README documents user, session, and agent memory scopes and a user_id search filter.
<!-- claim:OPS-C26 -->

Across the 19-source security/product packet inspected in v09, no single independent source validated a complete production chain from poisoned-write prevention through tenant-scoped action authorization; the retained sources cover individual links, so this is a bounded corpus conclusion rather than a universal absence claim.
<!-- claim:OPS-C27 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, fixed-source inspection of Sibyl-Labs/Sibyl-Memory supports this project-specific architecture reading: 固定 SHA 显示这是五个 Python 包共享一个 schema family 的本地优先系统：client 负责每租户 SQLite 权威存储与 FTS5，MCP/Hermes/LangGraph/CLI 是接入与运维表面。此结论来自 manifest、代码和 tree；README 的排名与隐私声明仍按项目方自述处理。 The repository was not executed in v09.
<!-- claim:PRJ-A001 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, fixed-source inspection of xerj-org/xerj supports this project-specific architecture reading: 固定 SHA 是一个 Rust 搜索/向量/日志引擎而非专用 agent-memory SDK；Elasticsearch-compatible HTTP 是采用桥，xerj-query 解析 DSL，xerj-engine 协调 WAL/segments、BM25 与 HNSW/exact vector，/_memory 只是其上的应用表面。 The repository was not executed in v09.
<!-- claim:PRJ-A002 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, fixed-source inspection of JingxuanC/causal-memory supports this project-specific architecture reading: Rust/MCP 系统把 raw session logs、atomic facts 和 decision→outcome causal edges 放在同一 SQLite 骨架上：写时 gatekeeping 隔开审计原文与召回层，distill/consolidation 形成 facts/edges，读时 BM25 与可选 embedding 用 RRF 融合并可做 typed spreading activation。 The repository was not executed in v09.
<!-- claim:PRJ-A003 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, fixed-source inspection of 410979729/scope-recall-hermes supports this project-specific architecture reading: Hermes provider 以 journal-first capture 隔离原始 turn 与 durable facts：SQLite 是权威 truth，digest/candidate/promotion 把证据变成 user/memory/project/ops rows，LanceDB、SQLite brute-force 或 PGVector 只作可重建 companion，recall_pipeline 以词法/向量/graph/freshness 信号融合当前 turn。 The repository was not executed in v09.
<!-- claim:PRJ-A004 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, fixed-source inspection of EverMind-AI/Raven supports this project-specific architecture reading: Raven 是完整 terminal agent harness；memory 由 host 侧 MemoryBackend Protocol 与 manifest-only plugin discovery 解耦，context_engine 在 turn 前组装 recalled memory，AgentLoop 在 turn 后 store/feedback。固定 SHA 将 EverOS 作为 bundled adapter，但重逻辑仍在 exact-pinned everos 包，另有 skill-forge 把 memory hits 与 skill sources 汇合。 The repository was not executed in v09.
<!-- claim:PRJ-A005 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, fixed-source inspection of volcengine/OpenViking supports this project-specific architecture reading: OpenViking 把 memory/resource/skill 统一为 viking:// 虚拟文件系统。Service 层复用在 embedded、CLI 与 HTTP；Parser/TreeBuilder 先把内容写 AGFS，SemanticQueue 异步生成 L0/L1/L2 并写只含 URI/vector/metadata 的索引；Retrieve 做 intent→hierarchical search→rerank；Session commit 归档消息后按 schema 抽取 self/peer/experience memory。 The repository was not executed in v09.
<!-- claim:PRJ-A006 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, fixed-source inspection of thedotmack/claude-mem supports this project-specific architecture reading: 这是 lifecycle-hook 驱动的 coding-session memory：Claude Code/OpenCode hooks 把 prompt、tool use 与 session end 发给每用户 Bun worker；worker 用 SQLite 保存 sessions/observations/summaries/pending queue，用 ChromaDB 保存 observation vectors；MCP 提供 search→timeline/get_observations 的渐进披露读取。 The repository was not executed in v09.
<!-- claim:PRJ-A007 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, fixed-source inspection of Health-Yang/MineEcho supports this project-specific architecture reading: MineEcho 是本地 assistant 应用而非独立 memory library。BFF 同时维护 working memory、node:sqlite short-term interactions/preferences/tasks/summaries、file-based long-term profile，以及 L0-L3 memory tree；context-builder/semantic-recall 将近期 memory 与 knowledge-base 的 vector/BM25/graph/LightRAG 证据组合给 chat。 The repository was not executed in v09.
<!-- claim:PRJ-A008 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, fixed-source inspection of Coding-Dev-Tools/engraphis supports this project-specific architecture reading: Engraphis 以 MemoryService 统一 CLI/MCP/REST/dashboard ingress，MemoryEngine 组合 Store、embedder、vector index、reranker、conflict/retention/graph policies。一个 SQLite 文件保存 memories、FTS、bi-temporal history、layered graph/code links与 hashed receipts；vector backend 默认为 NumPy exact scan，可选 sqlite-vec，query 再做 lexical/vector/graph/code fusion与 hard-budget context packing。 The repository was not executed in v09.
<!-- claim:PRJ-A009 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, fixed-source inspection of CraftJarvis/JARVIS-1 supports this project-specific architecture reading: 这是 2023/2024 Minecraft embodied-agent 研究代码的离线评估快照：multimodal language planner 将视觉/文本指令映射成计划，goal-conditioned STEVE-1/Malmo controller执行；assets/memory.json 是不完整的 fixed memory。README明确 multimodal descriptor/retrieval 与 online growing-memory learning 尚未发布，因此不能把 EpisodeStorage 误称为完整 agent-memory write/index/read系统。 The repository was not executed in v09.
<!-- claim:PRJ-A010 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, fixed-source inspection of SMJAI/open-memory-protocol supports this project-specific architecture reading: 该仓同时定义 vendor-neutral memory JSON schema、reference Express server 与 browser/Claude-MCP/CLI adapters。Reference server 用 node:sqlite保存 conversations与memory rows，FTS5 triggers同步 content/tags；embedding字段可被schema/storage保存，但固定 SHA 的 search实现只做quoted-term FTS，不构成semantic vector engine。 The repository was not executed in v09.
<!-- claim:PRJ-A011 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, fixed-source inspection of MaxFreedomPollard/Compartment supports this project-specific architecture reading: Compartment 是本地加密 vault：MCP/hooks/CLI 捕获memory，bundled BGE-small ONNX在CPU生成384-d vectors，Store只在RAM中打开SQLite（records/vec windows/FTS5/relations/audit/meta），每record text/vector加密后整个数据库image被序列化进AEAD journal；查询在解锁后用exact或可选HNSW vector+FTS5 BM25做RRF。 The repository was not executed in v09.
<!-- claim:PRJ-A012 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, fixed-source inspection of MemTensor/OmniMemEval supports this project-specific architecture reading: 这是评测编排仓而非memory implementation。User-memory track用client_factory把不同backend归一为add/search并跑LoCoMo/LongMemEval/BEAM/Persona/HaluMem；agent-memory track把Agent Runtime+Memory Plugin+Task Domain+Verifier组合，runner严格编排cleanup→train→settle→backup/restore→test，最后judge/aggregate/report。 The repository was not executed in v09.
<!-- claim:PRJ-A013 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, fixed-source inspection of letta-ai/letta supports this project-specific architecture reading: 固定 SHA 是 README 明确标记的 legacy Letta V1 server。其memory分为可直接渲染/编辑的core blocks与archive/source passages：Memory schema把blocks/git-backed filesystem编进prompt，PassageManager切分文本、请求embeddings、写SQLAlchemy archival/source rows与tags，可选按archive dual-write到Turbopuffer；REST/server managers暴露agent、archive、passage与tool API。 The repository was not executed in v09.
<!-- claim:PRJ-A014 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, fixed-source inspection of mem0ai/mem0 supports this project-specific architecture reading: OSS Python Memory facade用factory组合LLM、embedder、vector_store、optional reranker和SQLite history。add先按user/agent/run filters隔离、检索existing candidates、LLM抽facts，再batch embed/insert memory vectors、写history并异步式容错地维护独立entity collection；search按provider能力融合semantic、BM25 keyword、entity signals并可rerank。server/TS/CLI是其外部表面，managed platform另有未开源优化边界。 The repository was not executed in v09.
<!-- claim:PRJ-A015 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, fixed-source inspection of atomicstrata/atomicmemory supports this project-specific architecture reading: TypeScript/Rust monorepo以Core作为Postgres/pgvector memory backend，MemoryService注入episode/memory/claim/entity/link/lesson/raw-content stores，ingest pipeline抽取canonical memory objects与representations，search pipeline做vector/keyword/entity/temporal/contradiction-aware retrieval。SDK、MCP、CLI与Vercel/OpenAI Agents/LangChain/LangGraph/Mastra adapters共享该backend；可选S3/Filecoin/IPFS-style raw storage由registry/reconciler维护。 The repository was not executed in v09.
<!-- claim:PRJ-A016 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, the inspected repository tree for Sibyl-Labs/Sibyl-Memory exposed these architecture or integration locations: docs, sibyl-memory-cli, sibyl-memory-client, sibyl-memory-hermes, sibyl-memory-langgraph, sibyl-memory-mcp; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C001 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, the inspected repository tree for xerj-org/xerj exposed these architecture or integration locations: demo, deploy, docs, engine, functions, landing, metrics, recipes, scripts, user-feedback, xerj-ux; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C002 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, the inspected repository tree for JingxuanC/causal-memory exposed these architecture or integration locations: benches, crates, docs, scripts; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C003 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, the inspected repository tree for 410979729/scope-recall-hermes exposed these architecture or integration locations: benchmarks, docs, examples, scripts, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C004 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, the inspected repository tree for EverMind-AI/Raven exposed these architecture or integration locations: LICENSES, benchmarks, bridge, demos, docs, raven, scripts, tests, ui-tui; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C005 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, the inspected repository tree for volcengine/OpenViking exposed these architecture or integration locations: benchmark, bot, build_support, crates, deploy, docker, docs, examples, integrations, npm, openviking, openviking_cli; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C006 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, the inspected repository tree for thedotmack/claude-mem exposed these architecture or integration locations: cursor-hooks, docker, docs, fixtures, install, openclaw, plans, plugin, ragtime, scripts, src, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C007 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, the inspected repository tree for Health-Yang/MineEcho exposed these architecture or integration locations: apps, docs, marketing, scripts, vendor; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C008 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, the inspected repository tree for Coding-Dev-Tools/engraphis exposed these architecture or integration locations: demo, deploy, docs, engraphis, eval, integrations, scripts, skills, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C009 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, the inspected repository tree for CraftJarvis/JARVIS-1 exposed these architecture or integration locations: assets, jarvis, scripts; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C010 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, the inspected repository tree for SMJAI/open-memory-protocol exposed these architecture or integration locations: adapters, packages, spec; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C011 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, the inspected repository tree for MaxFreedomPollard/Compartment exposed these architecture or integration locations: docs, install, integrations, packaging, skills, src, tests, tools; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C012 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, the inspected repository tree for MemTensor/OmniMemEval exposed these architecture or integration locations: configs, data, docs, env_examples, scripts; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C013 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, the inspected repository tree for letta-ai/letta exposed these architecture or integration locations: alembic, assets, certs, db, examples, fern, letta, otel, sandbox, scripts, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C014 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, the inspected repository tree for mem0ai/mem0 exposed these architecture or integration locations: cli, docs, examples, integrations, mem0, mem0-ts, scripts, server, skills, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C015 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, the inspected repository tree for atomicstrata/atomicmemory exposed these architecture or integration locations: adapters, crates, examples, packages, plugins, scripts, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C016 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, Sibyl-Labs/Sibyl-Memory has these inspected dependencies or services: Python stdlib sqlite3 + SQLite JSON1/FTS5: 本地权威存储、JSON 约束与词法检索；client manifest 运行时 dependencies=[]; mcp FastMCP: MCP transport/tool surface，只有 mcp 包需要. Its recorded integration constraints are: SQLite 必须支持 json_valid（代码错误信息指向 SQLite 3.38+）且启用 FTS5，否则 schema/search 无法工作。; 默认 DB 与凭据位于 ~/.sibyl-memory；这是单机文件边界，不提供跨主机协调或外部向量服务。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I001 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, xerj-org/xerj has these inspected dependencies or services: tokio + axum + tower-http: 异步 runtime 与 HTTP transport; memmap2, roaring, fst, lz4_flex, zstd: segment/index 数据结构与压缩; aws-sdk-s3/aws-config: S3-compatible object integration；不是本地核心路径的必需外部服务. Its recorded integration constraints are: 兼容的是 Elasticsearch 8.x API 子集，不等同完整 Elasticsearch；调用方必须按支持矩阵验证 query/aggregation。; 索引与恢复依赖 data_dir/WAL/segment 一致性；需要运行独立 server，嵌入 agent 时承担进程、端口和持久卷运维。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I002 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, JingxuanC/causal-memory has these inspected dependencies or services: rusqlite: 单文件 SQLite 权威存储; reqwest + tokio: HTTP embedding/LLM 调用与异步等待; fastembed optional local-embed: BAAI/bge-small-en-v1.5 ONNX 384-d embedding；首次需下载模型且动态加载 ONNX runtime. Its recorded integration constraints are: 固定 SHA 状态只提供 MCP stdio；README 明确 HTTP transport 尚未实现，网络服务接入需另加 wrapper。; 启用 local-embed 时需要可动态加载的 ONNX Runtime 与首次模型下载；HTTP embedding 则需要 endpoint/model 配置。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I003 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, 410979729/scope-recall-hermes has these inspected dependencies or services: PyYAML + jsonschema: 核心配置/schema 验证; lancedb + pyarrow optional: 默认语义 vector companion extra; psycopg + pgvector optional: 中央 PostgreSQL/PGVector companion or bridge. Its recorded integration constraints are: general 是本地 scratch 且默认不进入 durable vector；user/memory/project/ops 才是 durable scopes，调用方必须保留身份/范围语义。; 多 agent 已有中央 PostgreSQL 时，README 明确本插件应是本地 Hermes recall layer而非跨 agent source of truth。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I004 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, EverMind-AI/Raven has these inspected dependencies or services: everos[multimodal]==1.2.1: bundled backend 的实际 extraction/search/persistence substrate，精确 pin 因 adapter 使用 internal APIs; litellm + httpx + pydantic: LLM/provider调用、HTTP backend 与配置/schema; mcp + channel extras: tool/server interface 与 Telegram/Slack/Discord/Matrix 等 gateway integrations. Its recorded integration constraints are: EverOS adapter 直接依赖 everos internal APIs，文档要求升级时重新核对并可能重建 ~/.everos/.index；不能把版本 range 随意放宽。; memory.userId 与 memory.agentId 是唯一身份源；recall/store identity 不一致会让已写 memory 无法召回。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I005 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, volcengine/OpenViking has these inspected dependencies or services: openviking-sdk + FastAPI/Uvicorn/httpx: SDK、独立 HTTP server 与 client transport; OpenAI/LiteLLM/Volcengine SDK: 可配置 LLM、embedding、reranker/semantic generation providers; pdfplumber/trafilatura/scrapy/python-docx/openpyxl/tree-sitter family: 文档与代码资源解析. Its recorded integration constraints are: 写入语义处理异步；调用方在 add_resource 后需 wait_processed 或接受短时间不可语义召回。; self/peer memory 路由受 memory_policy、schema stage、peer_enabled 与 safe peer_id 控制；错误 policy 会漏写或越界。; AGPL-3.0 对服务分发/修改有许可边界，生产集成需法律审查。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I006 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, thedotmack/claude-mem has these inspected dependencies or services: Node >=20.12 + Bun >=1: installer/CLI/worker runtime; SQLite 3: 结构化权威 session/observation store; uv + ChromaDB/chroma-mcp: Python vector search process与 semantic index. Its recorded integration constraints are: npm global install 仅装 SDK，不注册 hooks/worker；必须用 npx installer 或 host plugin install。; contentSessionId 与 memorySessionId 语义不同；转换错误会破坏 FK/session continuity。; hooks 故意 fail-open，worker 不可用不会阻塞 host，这意味着可用性优先于 capture completeness。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I007 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, Health-Yang/MineEcho has these inspected dependencies or services: Express + zod + ws: BFF HTTP/websocket与输入 schema; node:sqlite + sqlite-vec: short-term relational store与可选本地 vector能力; provider APIs + LightRAG worker: embedding/LLM summary与 knowledge graph/vector processing，需本地配置 key. Its recorded integration constraints are: node:sqlite 不可用时 ShortTermDb 自动退回内存 Map；进程重启即丢 short-term state，集成方必须监控 fallback log。; 仓库许可证是 PolyForm Noncommercial 1.0.0，商业使用需要另行书面许可；API 的 NOASSERTION 不能覆盖 README/LICENSE 明文。; 真实 provider keys 不随包提供，且 source startup 要同时安装 BFF/Console/vendored gateway dependencies。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I008 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, Coding-Dev-Tools/engraphis has these inspected dependencies or services: numpy >=1.24: 唯一 core dependency；默认 exact vector scan/offline engine; FastAPI/Uvicorn/SentenceTransformers/MCP optional extras: server、real embeddings与 agent transport; sqlite-vec/tree-sitter/psycopg/SQLCipher optional extras: native exact KNN、code graph、Postgres introspection、at-rest encryption. Its recorded integration constraints are: persistent vector space 需要可验证且稳定的 embedding fingerprint；身份不明或变化时 vector recall fail-closed直到 rebuild。; sqlite-vec 与 SQLCipher native SQLite libraries 不能同进程安全组合；auto回退NumPy，显式 sqlite-vec 请求会报错。; open repo不含 hosted team identity/automation等服务实现，不能从本地代码推断 hosted feature。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I009 -->

At pinned commit aa9bd97debee045cb35b37564c71dee4c465b9ad, CraftJarvis/JARVIS-1 has these inspected dependencies or services: torch 2.2.1 + torchvision 0.17.1: multimodal/planner/controller model runtime; gym 0.23.1 + gymnasium 0.29.1 + Malmo/JDK8: Minecraft environment/control stack; openai 1.16.0: language-model planner API，需 OPENAI_API_KEY. Its recorded integration constraints are: README明确只发布 offline evaluation；multimodal descriptor、retrieval、learning.py与online growing memory不可用。; 项目固定 gym==0.23.1，而 mineclip/minedojo依赖不同版本；README直接提示冲突可能出现。; 需要 JDK8、构建Minecraft/Malmo、下载weights并设置OPENAI_API_KEY，部署成本远高于普通memory library。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I010 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, SMJAI/open-memory-protocol has these inspected dependencies or services: Node >=22.5 node:sqlite: reference server runtime与内置SQLite; Express 4.18 + Zod 3.22: HTTP server与runtime input validation; SQLite FTS5: reference implementation唯一实际检索索引. Its recorded integration constraints are: 协议对象允许embedding，但reference search不读取它；需要semantic search的实现者必须另加vector index并定义一致性。; canonical schema content上限10000、tags格式/数量、id pattern与additionalProperties=false会拒绝不兼容host payload。; SQLiteStorage接口未展示组织级tenant enforcement；source.user_id与namespace是数据字段，不能自动当安全边界。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I011 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, MaxFreedomPollard/Compartment has these inspected dependencies or services: PyNaCl + argon2-cffi: XChaCha20-Poly1305与key derivation; onnxruntime + tokenizers + numpy: bundled local embedding与exact vector math; mcp >=1,<2 + optional usearch: stdio MCP surface；>20k HNSW extra. Its recorded integration constraints are: mcp 2.0移除了项目导入的FastMCP路径，manifest硬限制<2；升级需先port server。; vault记录embedding model SHA256并拒绝用不匹配模型打开；模型升级要显式reindex --re-embed。; 所有search在RAM中进行，vault必须先unlock且容量直接影响RSS/启动重载；多process写由advisory lock串行。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I012 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, MemTensor/OmniMemEval has these inspected dependencies or services: OpenAI/httpx/datasets/pandas: runner、LLM answer/judge、dataset与metrics; FAISS/Transformers/Torch/Pyserini/Tevatron: BrowseComp-Plus dense/sparse retrieval baseline与indexing; Docker/SWE-bench/document toolchain: software engineering/knowledge work domains; backend APIs + answer/eval LLM credentials: 被测系统与judge外部服务. Its recorded integration constraints are: 不同memory plugin必须显式实现cleanup/train/settle/backup/restore lifecycle；缺一项会破坏跨trial隔离或公平比较。; requirements包含Tevatron git main且多数依赖不pin，重复实验需另做lockfile/container固定。; LLM-as-Judge与backend credentials/model versions是外部变量，报告必须记录实际配置而不能只报仓库SHA。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I013 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, letta-ai/letta has these inspected dependencies or services: SQLAlchemy async + SQLModel + Alembic: V1 server state/passage persistence与migrations; OpenAI/Anthropic/LlamaIndex/Letta client: LLM、embeddings、document/index integration; optional Postgres/pgvector, SQLite-vec, Redis, Pinecone/Turbopuffer: database/vector/cache deployment variants. Its recorded integration constraints are: README明确本仓是legacy V1 server，active development已移到letta-code/App Server；新项目不应把此SHA当当前主实现。; agent passage必须有archive_id且不能有source_id；source passage反之，调用方需保持存储域互斥。; Postgres embedding会pad到MAX_EMBEDDING_DIM，而Turbopuffer/Pinecone不走同一padding语义，跨backend migration需验证维度。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I014 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, mem0ai/mem0 has these inspected dependencies or services: Qdrant client >=1.12: 默认/核心vector store client; OpenAI >=1.90 + httpx: 默认LLM与embedding provider/API transport; SQLAlchemy + sqlite3 history: history/session bookkeeping；self-host server DB surface; many optional vector stores/LLMs/spaCy: backend portability、hybrid entity extraction与NLP. Its recorded integration constraints are: Mem0需要LLM执行fact extraction且默认OpenAI模型/embedding；无key或provider failure会阻断infer=True add。; identity必须通过filters/entity params传递；metadata中的user_id/agent_id/run_id会被剥离，旧调用签名需迁移。; vector backend若未实现keyword_search，代码明确禁用hybrid BM25，只保留semantic；不同backend能力并不等价。; README明确managed benchmark含OSS没有的proprietary optimizations，不能用platform分数代表此SHA。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I015 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, atomicstrata/atomicmemory has these inspected dependencies or services: PostgreSQL pg + pgvector: Core durable store与semantic/hybrid search; OpenAI/Anthropic/HuggingFace transformers: extraction、embedding、answer/rerank provider surfaces; Express/Zod/Jose: Core HTTP/OpenAPI/auth schema surface; S3/Synapse/Filecoin/Helia optional stack: raw document artifact persistence/reconciliation. Its recorded integration constraints are: Core DB tests和运行需要Postgres/pgvector；README明确DB-backed tests在普通quick validation之外。; package matrix区分published/coming soon/deprecated；不能因源码存在就给Codex/Cursor plugin或deprecated npm CLI承诺可安装路径。; user与workspace scoped search走不同repository enforcement；adapter必须正确传workspaceId/agent scope，不能只依赖metadata。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I016 -->

At the 2026-08-10T05:07:57Z GitHub/API snapshot for Sibyl-Labs/Sibyl-Memory, the inspected rolling-90d window contained 41 commits and 2 unique contributors, while open issues were 1; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M001 -->

At the 2026-08-10T05:09:43Z GitHub/API snapshot for xerj-org/xerj, the inspected rolling-90d window contained 907 commits and 10 unique contributors, while open issues were 33; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M002 -->

At the 2026-08-10T05:11:54Z GitHub/API snapshot for JingxuanC/causal-memory, the inspected rolling-90d window contained 163 commits and 2 unique contributors, while open issues were 9; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M003 -->

At the 2026-08-10T05:17:37Z GitHub/API snapshot for 410979729/scope-recall-hermes, the inspected rolling-90d window contained 126 commits and 4 unique contributors, while open issues were 3; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M004 -->

At the 2026-08-10T05:17:49Z GitHub/API snapshot for EverMind-AI/Raven, the inspected rolling-90d window contained 149 commits and 20 unique contributors, while open issues were 70; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M005 -->

At the 2026-08-10T05:13:51Z GitHub/API snapshot for volcengine/OpenViking, the inspected rolling-90d window contained 862 commits and 102 unique contributors, while open issues were 455; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M006 -->

At the 2026-08-10T05:14:45Z GitHub/API snapshot for thedotmack/claude-mem, the inspected rolling-90d window contained 484 commits and 36 unique contributors, while open issues were 389; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M007 -->

At the 2026-08-10T05:17:28Z GitHub/API snapshot for Health-Yang/MineEcho, the inspected rolling-90d window contained 28 commits and 2 unique contributors, while open issues were 0; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M008 -->

At the 2026-08-10T05:13:25Z GitHub/API snapshot for Coding-Dev-Tools/engraphis, the inspected rolling-90d window contained 348 commits and 4 unique contributors, while open issues were 0; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M009 -->

At the 2026-08-10T05:12:54Z GitHub/API snapshot for CraftJarvis/JARVIS-1, the inspected rolling-90d window contained 0 commits and 0 unique contributors, while open issues were 7; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M010 -->

At the 2026-08-10T05:13:10Z GitHub/API snapshot for SMJAI/open-memory-protocol, the inspected rolling-90d window contained 31 commits and 1 unique contributors, while open issues were 1; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M011 -->

At the 2026-08-10T05:15:41Z GitHub/API snapshot for MaxFreedomPollard/Compartment, the inspected rolling-90d window contained 147 commits and 2 unique contributors, while open issues were 3; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M012 -->

At the 2026-08-10T05:13:32Z GitHub/API snapshot for MemTensor/OmniMemEval, the inspected rolling-90d window contained 18 commits and 3 unique contributors, while open issues were 1; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M013 -->

At the 2026-08-10T05:07:13Z GitHub/API snapshot for letta-ai/letta, the inspected rolling-90d window contained 6 commits and 2 unique contributors, while open issues were 43; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M014 -->

At the 2026-08-10T05:07:45Z GitHub/API snapshot for mem0ai/mem0, the inspected rolling-90d window contained 394 commits and 97 unique contributors, while open issues were 708; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M015 -->

At the 2026-08-10T05:17:42Z GitHub/API snapshot for atomicstrata/atomicmemory, the inspected rolling-90d window contained 40 commits and 2 unique contributors, while open issues were 21; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M016 -->

AtomMem reports a representation that extracts selective atomic facts, then groups them into hierarchical events and temporal profiles before associative-graph retrieval.
<!-- claim:REP-C01 -->

The bitemporal-store paper represents a memory as immutable identity plus versioned content, with valid time and transaction time kept separately rather than overwriting history.
<!-- claim:REP-C02 -->

In the bitemporal paper's 60-question sample, its time-travel path improved knowledge-update recall but reduced temporal-reasoning recall, so temporal filtering is not a universally beneficial reranker.
<!-- claim:REP-C03 -->

SimpleMem's paper defines a three-stage path: semantic structured compression, online semantic synthesis, and intent-aware retrieval planning.
<!-- claim:REP-C04 -->

An independent LightMem reproduction reports that changing only the retriever over a fixed constructed store shifted answer accuracy from 58.1% to 75.5%.
<!-- claim:REP-C05 -->

That reproduction finds raw-turn Naive RAG generally stronger at matched retrieval depths, while constructed LightMem is favored chiefly under tight answer-token budgets.
<!-- claim:REP-C06 -->

The trustworthy-search paper frames memory retrieval as a trust boundary because semantically related memories can be contextually inappropriate and induce cross-domain leakage, sycophancy, tool-call drift, or jailbreak behavior.
<!-- claim:REP-C07 -->

The Hindsight paper describes four logical networks separating world facts, agent experiences, entity summaries, and evolving beliefs, governed by retain, recall, and reflect operations.
<!-- claim:REP-C08 -->

Hindsight's authors characterize the common external-memory pattern as salient-snippet extraction followed by vector/graph storage and top-k prompt injection into an otherwise stateless model.
<!-- claim:REP-C09 -->

A-Mem's README documents note generation with structured attributes, historical-link analysis, and updates to contextual representations; its evaluation command exposes retrieve_k as a tunable parameter.
<!-- claim:REP-C10 -->

Cognee documents a self-hosted persistent-memory design that combines vector embeddings, graph reasoning, and an ontology-generation layer.
<!-- claim:REP-C11 -->

Mem0 documents multi-signal retrieval that fuses semantic, BM25 keyword, and entity matching, with a separate temporal-reasoning ranking feature.
<!-- claim:REP-C12 -->

Supermemory documents a combined profile/episodic service with fact extraction, temporal updates and forgetting, plus hybrid search over knowledge and personalized context.
<!-- claim:REP-C13 -->

MemMachine documents three distinct memories: graph-based episodic conversational context, SQL-stored profile facts/preferences, and short-term working memory.
<!-- claim:REP-C14 -->

The inspected letta-ai/letta repository is explicitly described as the legacy V1 server; its README says active development moved to Letta Agent and self-hosted API deployment to App Server.
<!-- claim:REP-C15 -->

HippoRAG's paper combines LLMs, a knowledge graph, and Personalized PageRank; the repository documents an index(docs) then rag_qa(queries) integration path.
<!-- claim:REP-C16 -->

Across the inspected literature, reported accuracy is not directly rankable: the bitemporal paper uses a 60-question sample, the LightMem reproduction compares retrievers at matched depths, and vendor READMEs describe different stacks and budgets.
<!-- claim:REP-C17 -->

Retrieval budget is an implementation contract, not a neutral detail: A-Mem instructs users to tune retrieve_k and sweep k, while Mem0's documented benchmark configuration uses a top_200 retrieval budget.
<!-- claim:REP-C18 -->

No selected repository was executed in this packet; setup is documented and visible test/CI artifacts are marked present only where inspected.
<!-- claim:REP-C19 -->

The v09 mapped corpus contains repository candidates that reference Graphiti integrations but does not contain getzep/graphiti as a canonical repository entity, so Graphiti-specific engineering conclusions are outside this packet's verified selection.
<!-- claim:REP-C20 -->

The selected paper stratum is current but immature: all ten selected mapped papers are 2026 arXiv preprints, and eight are in the rolling-90-day window.
<!-- claim:REP-C21 -->

Inference: the durable architecture boundary is not 'vector versus graph' alone; it is whether provenance, time/version, scope, and retrieval budget survive the representation-to-context compilation path.
<!-- claim:REP-C22 -->

The W3C AI Agent Memory Interoperability activity is a Community Group created on 2026-06-03, not a W3C Recommendation or other formal W3C standard.
<!-- claim:SAT-STD-C001 -->

The W3C API listed 17 group participants at the cutoff; that count is participation/attention evidence and cannot establish implementation or production adoption.
<!-- claim:SAT-STD-C002 -->

draft-saihm-memory-protocol-01 remained an individual Internet-Draft record with stream None, no RFC and no standards level; it must not be called an IETF standard.
<!-- claim:SAT-STD-C003 -->

At the captured cutoff, the official MCP extensions overview listed Authorization Extensions, MCP Apps and MCP Tasks and contained no memory extension listing.
<!-- claim:SAT-STD-C004 -->

MCP Tasks defines durable asynchronous operation handles, polling, reconnect and input-required lifecycle; this does not standardize persistent memory records, retrieval, consolidation or forgetting.
<!-- claim:SAT-STD-C005 -->

Agent Memory Hall contains a real bidirectional UMP/AMH converter with file import/export, three adapter tests and successful public CI at the pinned commit.
<!-- claim:SAT-STD-C006 -->

The Agent Memory Hall converter targets an older UMP 0.1-shaped record: it emits body as a string and omits the required ump and time objects, so it is not conformant to the pinned UMP 1.0 schema.
<!-- claim:SAT-STD-C007 -->

The AMH test called round-trip preserves only selected core fields within its own converter; it is not a schema-validation report, full-field loss analysis or two-party UMP round trip.
<!-- claim:SAT-STD-C008 -->

Portable Agent Memory is a paper-backed project protocol with a substantial draft spec and SDK, but the repository had no tag/release and exposed spec v1.0 Draft versus SDK 0.1.0; it is not an SDO standard.
<!-- claim:SAT-STD-C009 -->

Amore is independent evidence that a PAM provenance-chain idea was implemented: its NOTICE describes a clean-room content-addressed envelope/prev_hash implementation, but this is not full .pam wire-format or PAM conformance.
<!-- claim:SAT-STD-C010 -->

Engram is a paper-backed project draft whose pinned specification repository supplies a self-certification checklist but no executable conformance runner; self-certification cannot establish an independent conformant implementation.
<!-- claim:SAT-STD-C011 -->

Engram project claims about OpenClaw/Hermes writers were not corroborated by the recorded exact identifier searches, so this packet does not publish them as adoption facts.
<!-- claim:SAT-STD-C012 -->

The title Universal Memory Protocol also names a probabilistic identity/context research framework on Zenodo that is distinct from the edihasaj portable-record interchange specification.
<!-- claim:SAT-STD-C013 -->

HKUDS MGP v0.1.1 is a substantial project protocol with semantic specification, schemas, OpenAPI, reference gateway, adapters and an executable compliance suite; those same-project assets do not turn it into an SDO standard.
<!-- claim:SAT-STD-C014 -->

Engramory v0.7.0 is an explicitly experimental portable file-based memory discipline with several host adapters, not a cross-vendor wire standard; its own documentation limits it to single-project/single-writer use and lacks a store migration version.
<!-- claim:SAT-STD-C016 -->

An externally owned non-fork repository, syh5285126-ops/agent-team, really integrates tinqiao Engramory by cloning it and installing its rules/store, but the clone is unversioned and the repository supplies no conformance, CI or production-deployment report.
<!-- claim:SAT-STD-C017 -->

eMEM is a versioned project protocol with code, SDK/package and conformance assets plus a project-operated responder; project-owned deployment/registry claims are not independent adoption, and the README says its guard had not yet been pointed at a live organisation.
<!-- claim:SAT-STD-C018 -->

OCF v0.2 is a draft portable committed-working-context and governance bundle with schemas, vectors and a runner; its own scope explicitly says it is not a new wire protocol and does not define memory units.
<!-- claim:SAT-STD-C019 -->

Artesian is an inspectable OCF implementation, but it is maintained under aquifer-labs, the same organization as the OCF spec, so it is reference-implementation evidence rather than independent adoption.
<!-- claim:SAT-STD-C020 -->

glatinone's RFC-AMP-001 is a real v0.1.0 project draft with reference server, SDK, tests and successful same-project CI, but it is neither an RFC nor an independently adopted standard.
<!-- claim:SAT-STD-C021 -->

The label RFC-AMP-001 is itself ambiguous: the Red Hat AI Americas MemoryHub repository contains a distinct project proposal with the same label, not an implementation of glatinone AMP.
<!-- claim:SAT-STD-C022 -->

The 2026 project-spec layer is broader than a record/API list: it includes governed service contracts, portable local disciplines, verifiable content-addressed fact protocols and committed-working-context governance bundles.
<!-- claim:SAT-STD-C023 -->

Executable conformance assets are appearing inside project repositories, but this audit still found no current-version external conformant implementation, independent conformance report or two-party round-trip report for the promoted memory-specific project specs.
<!-- claim:SAT-STD-C024 -->

This audit did find two weaker external implementation signals—an AMH UMP 0.1-shaped adapter and an unversioned Engramory installer—so the correct conclusion is qualified partial integration, not zero external activity.
<!-- claim:SAT-STD-C025 -->

The W3C AI Agent Memory Interoperability activity is a Community Group, and its adopted charter explicitly says its reports are not W3C Recommendations or other W3C standards.
<!-- claim:STD-C001 -->

The W3C group's use-case catalogue, baseline profile, conformance criteria, test vectors and test suite are chartered first-year targets; this bounded audit did not identify a published conformance report or test pack at the cutoff.
<!-- claim:STD-C002 -->

draft-saihm-memory-protocol-01 is an individual Active Internet-Draft with stream None and intended status Informational; the datatracker disclaimer gives it no formal IETF standing or endorsement.
<!-- claim:STD-C003 -->

SAIHM's own status page says no standards-development organization has adopted it and labels it a candidate specification rather than an Internet, ISO, OASIS, IEEE or W3C standard.
<!-- claim:STD-C004 -->

The W3C group currently normatively references SAIHM while its chair discloses that he also maintains SAIHM; participation is explicitly not endorsement, so group formation is not independent adoption evidence.
<!-- claim:STD-C005 -->

The W3C charter says AAIF hosts the reference implementation, while SAIHM's status page says its AAIF proposal has not yet been submitted; until reconciled by an AAIF primary source, this packet treats AAIF hosting as unverified.
<!-- claim:STD-C006 -->

MCP 2026-07-28 is stateless at the protocol layer; persistent application state can be represented by explicit handles, but MCP does not thereby define a durable memory record or lifecycle.
<!-- claim:STD-C007 -->

MCP's standard server primitives are prompts, resources and tools; memory is not a fourth core primitive in the 2026-07-28 server specification.
<!-- claim:STD-C008 -->

At the captured cutoff, the official MCP extensions overview listed Authorization Extensions, MCP Apps and MCP Tasks and contained no memory extension listing; Tasks adds durable asynchronous operation handles and does not define a memory record or lifecycle contract.
<!-- claim:STD-C009 -->

The official MCP Knowledge Graph Memory Server defines its own entity/relation/observation tool vocabulary and memory://knowledge-graph resource; it demonstrates transport of one memory model, not standardization of memory semantics.
<!-- claim:STD-C010 -->

The YouTale Agent Memory Protocol is a v0.1 Markdown-first draft whose CLI, MCP and Python reference implementations were described as planned or under development, not released artifacts, at the pinned commit.
<!-- claim:STD-C011 -->

The Smriti AMP repository contains a filename/version-heading mismatch, has no GitHub tag or release in the audited snapshot, and bundles the claimed reference implementations with the specification; therefore its 'stable' or 'production' wording is not independent adoption evidence.
<!-- claim:STD-C012 -->

Independent technical discussion of Smriti AMP identifies under-specified consolidation behavior and metadata escape hatches as threats to semantic interoperability; the project author's response moved the design toward a standalone REST/gRPC boundary.
<!-- claim:STD-C013 -->

A separate peer-reviewed 2026 work also uses the name Agent-Memory Protocol for privacy operations—redact, pack and hydrate—so AMP cannot be treated as one uniquely identified specification without a canonical source and version.
<!-- claim:STD-C014 -->

SMJAI's Open Memory Protocol is a v0.1 project draft with REST, server, MCP adapter, CLI and browser-extension surfaces; the audited repository had one listed contributor and no GitHub release, and no independent adopter was verified.
<!-- claim:STD-C016 -->

Universal Memory Protocol has a genuine project v1.0.0 release and pinned artifacts, while a different-owner repository contains a tested UMP 0.1-shaped adapter; the adapter does not satisfy the pinned UMP 1.0 record schema and is not evidence of UMP 1.0 conformance, production adoption, or a two-party round trip.
<!-- claim:STD-C017 -->

UMP standardizes portable records and operations with MCP/HTTP/file bindings while deliberately leaving retrieval, embeddings, ranking, summarization and consolidation outside its scope.
<!-- claim:STD-C018 -->

Web Agent Memory Protocol is an experimental browser-facing prior attempt whose own README says it is work in progress and not production-ready.
<!-- claim:STD-C019 -->

MemTools is an interoperability research framework for composing lifecycle components and evaluation protocols; it is not a wire protocol, storage standard or SDO specification.
<!-- claim:STD-C020 -->

MemTools validates structural field contracts (requires_keys/provides_keys), while its limitations explicitly say this does not guarantee behavioral compatibility between components.
<!-- claim:STD-C021 -->

In author-reported ALFWorld batch results, combining AWM formation with A-Mem backend/retrieval scored 43.28 versus 40.30 for native AWM; this is evidence of research composability under one framework, not production interoperability.
<!-- claim:STD-C022 -->

MemTools reports protocol sensitivity: the AWM pipeline scored 33.58 under stream execution versus 40.30 under batch execution, so execution protocol is an experimental variable rather than a neutral wrapper.
<!-- claim:STD-C023 -->

No independent reproduction of MemTools was found by the exact recorded search as of 2026-08-10; because the paper was submitted only 18 days earlier, this is a bounded no-evidence result with substantial indexing-lag risk.
<!-- claim:STD-C024 -->

Protocol naming is fragmented: the exact GitHub repository queries returned 103 'agent memory protocol' hits and 18 'open memory protocol' hits, including incompatible specifications and unrelated homonyms; those counts measure discovery noise, not adoption.
<!-- claim:STD-C025 -->

Across the selected SAIHM, YouTale AMP, Smriti AMP, EB-DevTech OMP, SMJAI OMP and UMP candidates, the recorded exact web/code/package searches found no independently auditable production deployment, external conformant implementation, versioned conformance report or two-party round-trip evidence.
<!-- claim:STD-C026 -->

The candidates show partial architectural convergence on exposing memory through MCP tools or HTTP/file bindings, but no demonstrated consensus on canonical record shape, identity/security envelope, lifecycle semantics, retrieval/consolidation behavior or conformance tests.
<!-- claim:STD-C028 -->

The present standards landscape is therefore not a contest among mature memory standards: MCP is the mature adjacent context-exchange layer, while memory-specific artifacts remain a Community Group work program, an individual draft, project specs or a research framework.
<!-- claim:STD-C029 -->
