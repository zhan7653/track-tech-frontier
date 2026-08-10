# Agent Memory Benchmark 与评测地图

## Bottom line

There is no single “agent memory score.” The field measures at least eight distinct capabilities under materially different access and control assumptions: explicit recall, incremental update/forgetting, memory-to-action parameter grounding, on-trajectory episodic state, multi-party belief/speaker state, multimodal retention, implicit behavioral adaptation, and memory-security lifecycle. A system can score well where the answer is a post-hoc question over a fixed history yet fail when memory must guide later interdependent actions.

## Capability families—not a single benchmark list

**Recall and long-context retrieval.** LoCoMo created a multi-session conversational reference point: 300-turn, ~9K-token conversations over up to 35 sessions and QA, event-summary, and multimodal-generation tasks [BEN-C01]. LongMemEval narrows this to five assistant-memory abilities across 500 curated questions and scalable chat histories [BEN-C02]. Both are post-hoc: a history is provided (in raw, retrieved, or indexed form) and a response is judged. They therefore test evidence localization, temporal interpretation, and answer production, but do not establish that a memory system knows when to write, can safely revise itself, or can act on recalled state. 

MemoryAgentBench makes the ingestion side more explicit by sending chunked interactions and grouping tests into accurate retrieval, test-time learning, long-range understanding, and selective forgetting [BEN-C03]. MemBench adds factual versus reflective memory and participation versus observation, while treating effectiveness, efficiency, and capacity as separate measurement axes [BEN-C04]. Memora goes further on timeline mutation: its three tasks are remembering, reasoning, and recommending and FAMA penalizes obsolete/invalidated memory [BEN-C05]. HaluMem diagnoses pipeline operations—extraction, updating, and QA—rather than only final answers [BEN-C06]. These are complementary lifecycle diagnostics; their questions, histories, metrics, model wrappers, and judges differ, so their headline accuracy is not rankable across one another. 

**From recalling to doing.** Mem2ActBench’s unit is a tool-use task whose underspecified request requires an agent to draw constraints from prior memory and ground parameters into a tool call [BEN-C07]. Its released setup contains 2,029 sessions and 400 tool-use tasks, and evaluates tool-selection and parameter-grounding outcomes rather than only answer text [BEN-C08]. MemoryArena is even more strongly on-policy: human-crafted, explicitly interdependent subtasks are separated into sessions, and later decisions depend on experience distilled from earlier environment interaction [BEN-C12]. Success/progress in that loop measures a property absent from a retrieved-QA protocol. StoryBench uses branching interactive fiction and distinct immediate-feedback/self-recovery modes [BEN-C09]; EMemBench derives verifiable questions from the agent’s own text/visual-game trajectories [BEN-C10]; MEMTRACK puts noisy, conflicting Slack/Linear/Git-like evidence into organizational state tracking and adds correctness, efficiency, and redundancy [BEN-C11]. Together these are the action/state protocol family, but differ in environment, oracle, action space, and evaluation unit.

**The omitted contexts are now becoming first-class axes.** GroupMemBench uses graph-grounded multi-party conversations and asker-bound adversarial queries spanning six categories, rather than treating a group as a concatenated dyad [BEN-C13]. Mem-Gallery follows visual and text information across multi-session MLLM conversations and separates extraction/adaptation, reasoning, and knowledge management [BEN-C14]. ImplicitMemBench instead uses Learning/Priming–Interfere–Test and first-attempt scoring for procedural memory, priming, and classical conditioning [BEN-C15]. These protocols prove why a correct answer to an explicitly worded recall query is a poor proxy for speaker-grounded, visual, or automatically enacted memory.

**Reliability and security are a different measurement layer.** HaluMem asks whether extraction or updating fabricates, conflicts, or omits memory points before such error reaches QA [BEN-C06]. MemSecBench makes attack progression explicit: its controlled Write–Execute–Forget protocol evaluates 310 cases over 48 contexts and seven lifecycle checkpoints in an isolated configuration [BEN-C16]. Neither is an aggregate “safety score” for conversational recall; the former traces operation-level quality and the latter traces malicious persistence, downstream consequence, and selective repair.

<!-- synthesis:BEN-AUTO-01 claims:BEN-C01,BEN-C02,BEN-C03,BEN-C04,BEN-C05,BEN-C06,BEN-C07,BEN-C08,BEN-C09,BEN-C10,BEN-C11,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16 clusters:MM-C13 -->

## Protocol fingerprints and valid comparison groups

| Group | Benchmarks | Unit / access / setting | Measurement | What is comparable |
|---|---|---|---|---|
| BEN-G1 static conversational QA | LoCoMo, LongMemEval | fixed multi-session histories; post-hoc query; raw-context/RAG/memory-agent variants | QA/task-specific scores; some LLM judging | only matched dataset/version, history size, backbone, retrieval budget and judge |
| BEN-G2 incremental lifecycle | MemoryAgentBench, MemBench, Memora, HaluMem | chunked or sequential ingestion with later query/update | accuracy/recall/F1 plus efficiency/capacity or FAMA/operation metrics | only within identical task and supplied interaction wrapper |
| BEN-G3 action/state | Mem2ActBench, StoryBench, EMemBench, MEMTRACK, MemoryArena | tool or environment interaction; memory affects later decisions | tool success/grounding, trajectory/game correctness, task success/progress | no pooling: action space, oracle, feedback and execution policy must match |
| BEN-G4 context-specialized | GroupMemBench, Mem-Gallery, ImplicitMemBench | multi-party, multimodal, or cue-free learning/interference | accuracy or first-attempt behavioral effect | only within same modality/identity and constructed controls |
| BEN-G5 reliability/security | HaluMem, MemSecBench | operation pipeline or adversarial lifecycle | extraction/update/QA diagnostics; attack/repair checkpoints | only matched harness, backend, LLM and threat model |

LongMemEval-V2 bridges recall and experienced web-agent knowledge rather than merging groups: 451 manually curated questions cover static state, dynamic tracking, workflow, gotchas, and premise awareness over multimodal web-agent histories [BEN-C17]. It should be reported separately as BEN-G3-adjacent because it asks about accumulated environment experience but still uses curated questions rather than fully open-ended task success.

<!-- synthesis:BEN-AUTO-02 claims:BEN-C17 clusters:MM-C13 -->

## Artifact and engineering reading

The official LoCoMo repository exposes data and task-evaluation code [BEN-C18]. LongMemEval releases `s`, `m`, and oracle data forms and supports explicit BM25/dense retrievers and turn/session granularity [BEN-C19]. MemoryAgentBench exposes its code plus framework-specific directories and dataset distribution [BEN-C20]. LongMemEval-V2 supplies data validation/prepare scripts and explicitly packages a latency–accuracy frontier submission path [BEN-C21]. This supports re-running particular protocols; it does not make score claims across these projects automatically reproducible or comparable.

The current open ecosystem also contains **harness candidates**, not new scoring authorities: OmniMemEval describes itself as a memory-system evaluation framework, and MemoryData claims a unified launcher across four benchmark families [BEN-C23]. Their role should be to standardize the *execution envelope* (pinned dataset, agent wrapper, model, retrieval/token/tool budget, seed, and judge) while preserving original benchmark metrics and protocol labels. A wrapper that erases those labels creates false precision.

<!-- synthesis:BEN-AUTO-03 claims:BEN-C18,BEN-C19,BEN-C20,BEN-C21,BEN-C23 clusters:MM-C13 -->

## Internal evaluation matrix

Use a gated matrix, not an average leaderboard:

| Internal gate | Representative seed | Required controls | Release criterion |
|---|---|---|---|
| Recall & temporal evidence | LongMemEval + LoCoMo | dataset revision; session/turn granularity; context/retrieval budget; judge | evidence retrieval and answer quality reported separately |
| Update, conflict, forgetting | MemoryAgentBench + Memora + HaluMem | ingest cadence; mutation schedule; operation API; stale-memory metric | pass update/forget tests before optimization claims |
| Tool/action reuse | Mem2ActBench + MemoryArena | same tool set/environment image; agent policy; retries; action budget | task success plus parameter/evidence trace, not QA alone |
| Organizational/multi-party | GroupMemBench + MEMTRACK | speaker identities, audience, permissions and cross-platform state | speaker attribution and conflict resolution tracked |
| Multimodal/embodied | Mem-Gallery + EMemBench | image/trajectory assets and VLM version; visual retrieval budget | report text-only and visual-dependent slices |
| Implicit/procedural | ImplicitMemBench | paired control, interference, first attempt only | report behavioral effect and constraint violations |
| Security/revocation | MemSecBench + HaluMem | threat model, write gate, memory backend, repair test | no production readiness claim without write→execute→forget evidence |

Each matrix cell should log a protocol fingerprint: task/unit, corpus construction, memory access, oracle/agent setting, model/judge, metrics, baselines, versions, limitations, and comparability group. A release-facing scorecard may present a vector of gated outcomes and an explicit cost/latency column; it must never collapse BEN-G1 through BEN-G5 into one total.

## Consensus, disputes, and decisions

**Scoped consensus (high confidence):** fixed-history conversational QA is necessary but insufficient for evaluating long-horizon agent memory; the independently designed action-focused MemoryArena and tool-grounding Mem2ActBench make this boundary explicit [BEN-C07,BEN-C12]. **Mixed/evidence-thin:** whether one shared harness can yield fair cross-family comparisons—current wrappers can harmonize execution, but only a controlled rerun can establish metric alignment [BEN-C23]. **Dispute to preserve:** a high static-recall result could reflect model context capacity, retriever, extraction policy, or judge behavior; it cannot by itself demonstrate safe memory lifecycle management or downstream agency [BEN-C22].

Decision implication: select a benchmark family from the memory failure mode first, then run a matched baseline and report the complete fingerprint. Treat non-comparable benchmark wins as coverage signals only. Reversal criteria: a conclusion about action utility requires controlled, same-agent reruns where memory access is ablated; a conclusion about safety requires matched threat/repair tests; and a cross-family claim requires a pre-registered harmonized protocol rather than a normalized average.

<!-- synthesis:BEN-AUTO-04 claims:BEN-C07,BEN-C12,BEN-C22,BEN-C23 clusters:MM-C13 -->


## Procedural-memory poisoning protocol

PoisonedEvolution 的 SER 统计的是持久技能工件被嵌入目标行为，不是 recall、触发成功或真实危害执行。跨 SkillClaw 与 Trace2Skill 的数值说明该攻击可跨两个已测 promotion architecture 转移，但不能拼入通用 Memory leaderboard。后续对比必须同时固定 attacker-support ratio、evolver、artifact inspection、trigger/action test 与 defense assumptions。

## Procedural-security benchmark 原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

In the authors' SkillClaw evaluation at 10% attacker support, PoisonedEvolution embedded target behaviors in 546 of 600 completed trials (91.0% SER) across six evolvers and four behavior families.
<!-- claim:FM-PE-C02 -->

On the structurally different Trace2Skill pipeline at the same 10% support ratio, the authors report 369 of 600 successful embeddings (61.5% SER), showing transfer across the two evaluated evolution architectures.
<!-- claim:FM-PE-C03 -->

The evaluated SER measures durable artifact modification, not trigger activation, harmful action execution, credential theft, exfiltration, destructive effects, or a complete utility-security frontier.
<!-- claim:FM-PE-C05 -->

<!-- synthesis:FM-BEN-S01 claims:FM-PE-C02,FM-PE-C03,FM-PE-C05 clusters:MM-C13 -->
