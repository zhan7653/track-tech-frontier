# C14：基础理论、对象边界与可执行分类体系

截至 2026-08-10。C14 的任务不是给论文贴“情景记忆/语义记忆”标签，而是回答一个更严格的问题：一个分类体系能否把来源各异的论文与仓库压缩成可实现、可测试、可推翻的状态与操作契约。final mapped/deep-verified coverage all=93、primary=37（89 papers/4 repos；12m 69、90d 45）。

## 结论先行：分类必须同时回答对象、操作与控制面

当前较稳的综合不是某一套认知术语，而是三个彼此正交的坐标轴：

1. **持久对象是什么**：working/context、episodic evidence、semantic fact/profile、procedural artifact、world/project/shared state、control metadata；
2. **对象经历什么操作**：capture、admit、commit、retrieve、compile、supersede、consolidate、forget、purge、restore；
3. **哪一层负责什么**：data plane 保存记录与版本，retrieval plane 选择当下证据，mutation/control plane 决定写入与演化，action boundary 在执行前重新验证权限与适用条件。

这三个轴不能互相替代。“episodic”没有说明谁能删除；“graph”没有说明版本与权限；“长期”没有说明何时写入；“reflection”没有说明它是一次反馈、可执行程序还是事实。`FND-C07`、`FND-C08` 和 `EXP-C16` 共同给出 procedural boundary，`FND-C23` 给出 plane separation，`REP-C22` 则限定表示层必须把 provenance、time/version、scope 和 budget 带到 context compilation。

<!-- synthesis:C14-S01 claims:FND-C07,FND-C08,FND-C23,EXP-C16,REP-C22 clusters:MM-C14 -->

## 1. 第一轴：按行为语义区分 durable object

### 1.1 Working/context state

它是当前推理窗口中的临时选择结果，不等于持久 memory。MemGPT 的 virtual-context tiering 说明有限 context 需要外部状态调度，但 tier movement 本身不构成 update、delete 或 rollback 语义。`FND-C03` 因此 working state 的关键接口是 budget、source pointer、selection reason 与 expiry；它可以随请求重建，不应成为唯一事实副本。

### 1.2 Episodic evidence

Generative Agents 的 experience stream → reflection → planning 是“记忆改变后续行为”的重要谱系。`FND-C01` 但该工作并没有给出通用的更新、删除、回滚或 retention contract。`FND-C02` 因此 episodic evidence 更接近 append-only observation/interaction/tool receipt：它记录发生过什么、何时发生、来自哪里；后续摘要或反思是 derived artifact，而不是覆盖原事件。

### 1.3 Semantic fact、profile 与 belief

MemoryBank 同时保存对话记录、事件摘要和演化的用户人格评估，并把 storage、retrieval、updating 分开。`FND-C05` 这说明“事实/画像”与“事件证据”必须分层：profile/fact 需要 subject、valid time、source、confidence、supersession 与 consent；事件则应保留原始发生顺序。把二者压成一个向量 chunk，会同时丢掉可纠正性与身份边界。

### 1.4 Procedural artifact

Reflexion 的语言反馈与 Voyager 的 executable skill library 是两种不同的可复用行为对象。`FND-C07`、`FND-C08` 更近期的 experience/self-evolution 工作又区分“从任务经验更新 procedure”与“更新负责抽取、合并、修剪记忆的 policy”。`EXP-C17` 因此 procedure 至少要携带适用任务、环境/工具版本、前置条件、历史结果、失败与 deprecation；不能与 mutable user fact 共用相同 update 规则。

### 1.5 World、project 与 shared state

多模态/具身 memory 额外要求 observation grounding、visibility、空间/世界状态和 action consequence，不能被当作更大的文本画像。`EXP-C20` shared store 只有定义 sharing scope、authority、private/shared visibility、provenance 与 revocation 才能叫 organizational memory。`EXP-C18` 个性化是 subject-specific state，multi-agent memory 是 principal/scope 问题；二者只在选择性共享个人事实时相交。`EXP-C19`

### 1.6 Control metadata

source receipt、principal/tenant、valid/transaction time、revision parent、mutation intent、policy/model/index version、budget、rollback pointer 不属于“内容”，却决定内容能否安全演化。C14 把它们单独设为一等对象，是为了防止业务记录在经过 summary、embedding、graph edge 或 skill extraction 后失去治理语义。

## 2. 第二轴：生命周期不是 CRUD 的同义词

分类体系只有映射到状态机才有工程价值。一个最小、可回放的生命周期可以写成：

```text
capture evidence
  → authenticate / scope / type
  → propose candidate state
  → admit or quarantine
  → append receipt + revision
  → materialize indexes / summaries / graphs
  → retrieve + compile evidence packet
  → authorize action
  → observe outcome
  → supersede / consolidate / forget / purge / restore
```

A-MEM 把新 note 的结构属性、动态链接和历史上下文更新纳入 write path，说明写入会改变邻近表示，而不是只新增一行。`FND-C09` MemoryOS 把 Storage、Updating、Retrieval、Generation 分成模块并采用 short/mid/long tiers。`FND-C11` 这两条路线支持“组织与层级必须显式”，却没有自动给出事务或物理删除保证。

MemTxn 把 source-supported admission、temporal version selection 和 durable snapshot journal 放在 answer model 外部。`FND-C17` ForgetEval 则区分 recall 与 supersede、release、purge 等 mutation-plane 操作。`FND-C21` 因而 update 不能只写成 `upsert`，forget 不能只写成“top-k 搜不到”，restore 也不能只靠再次提示模型。分类体系至少要区分逻辑失效、版本替代、索引移除、物理清除、派生物传播和恢复点。

<!-- synthesis:C14-S02 claims:FND-C09,FND-C11,FND-C17,FND-C21 clusters:MM-C14 -->

## 3. 第三轴：plane separation 与参考接口

### Data plane

保存 immutable receipts、typed state、version/validity、policy labels 与 materialized projection pointers。它的核心不变量是：derived state 可回溯，revision 有父关系，删除/恢复状态可查询，tenant/principal 不在下游临时补写。

### Retrieval plane

将 query/task/as-of/authority/budget 转成候选与 evidence packet。它可以组合 lexical、semantic、graph、temporal 和 scope filter，但输出必须继续携带 source、revision、conflict、rejected reason 与 index watermark。`REP-C22` 的重要含义是，vector 与 graph 只是候选结构；真正的 durable boundary 是治理语义能否穿过表示与 context compiler。

### Mutation/control plane

决定 admit、merge、supersede、forget、purge、restore 的策略与授权。MemCon 将 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 建模为 online policy actions。`FND-C14` 这提供了可学习 controller 的方向，但 learned policy 不应绕开可审计 primitive：探索策略可以提议 operation，高风险 mutation 仍应由事务、权限与恢复层提交。

### Action boundary

“被取回”不等于“可以执行”。procedure、profile、project/world/shared state 分别需要工具版本、当前用户、repo/branch/commit、visibility、role/revocation 等前置条件。action 前重验这些条件，才能把 memory quality 与 task/action success、unsafe action、stale-dependency failure 连接起来。

## 4. 理论分歧：稳定性、可塑性与预算没有通吃解

Budgeted consolidation 的结果把一个常被隐藏的取舍显式化：retention 保留细节，consolidation 在紧 token 预算下提高覆盖，却可能损失 query-critical evidence；优选操作依赖预算。`FND-C19` 这反对“总是摘要”与“永远保留”两个极端，也说明 memory theory 不能脱离 workload distribution、query horizon、loss tolerance 与 recovery cost。

因此，C14 更适合用条件化目标而不是统一效用函数：

- 对需要审计、纠正和删除的状态，优先保留 evidence/receipt，再让 summary/graph/profile 成为可重建 projection；
- 对紧上下文预算，测 coverage-per-token 与 critical-detail loss，而不是只报 token saving；
- 对高变动状态，测 supersession、stale hit 与 dependency propagation；
- 对 learned controller，测 policy drift、不可逆 mutation、off-policy safety 与 rollback；
- 对共享或行动型状态，把 authority 与 harmful transfer 纳入效用，而不是只看 recall。

这仍不是统一形式化理论。当前材料支持的是约束集合与可证伪协议，而不是一个已经被多实现验证的最优 memory objective。

## 5. 从 taxonomy 到 schema、API 与观测

一个可执行 taxonomy 至少应产生下列实现字段：

| 分类问题 | Schema / API 落点 | 可检查不变量 | 失败观测 |
|---|---|---|---|
| 这是什么对象 | `type`, `subject`, `source`, `payload_ref` | 类型决定更新与共享规则 | type confusion、事实/程序混写 |
| 何时成立 | `valid_from/to`, `recorded_at`, `revision` | current/history 可分离 | stale hit、未来信息泄漏 |
| 谁能看/改/分享 | `principal`, `tenant`, `purpose`, `visibility`, `policy` | filter 在候选生成前执行 | cross-scope retrieval/action |
| 如何演化 | `operation`, `parent_revision`, `supersedes`, `tombstone` | mutation 可回放、可恢复 | silent overwrite、ghost delete |
| 如何被选择 | `query`, `candidate_set`, `rank`, `budget`, `index_version` | 选择过程可复现 | candidate loss、budget unfairness |
| 如何影响行为 | `compiled_evidence`, `authorization`, `action`, `outcome` | action 可追到 memory revision | stale/poisoned action、无效 recall |

这张表把认知类比降为命名辅助，把真正的工程共识放在 interface 和 invariant。新论文若不能映射到对象、操作或控制面之一，应先作为 boundary/defer 处理，而不是为了容纳它继续增加同义分类。

## 6. 评测含义：不同对象不能拼成一个总榜

静态对话 QA、环境 task success、tool grounding、mutation/security lifecycle 的任务单位、访问路径、agent setting 和指标不同，不能构成共同 leaderboard。`BEN-C22` C14 因此给 benchmark 的不是一条总指标，而是一组 protocol fingerprint：object type、write/update/forget policy、history construction、retriever/index、k/token/tool budget、model/judge、action requirement、security/repair step。

对象分类决定最小充分指标：episodic/semantic 看 answer 与 evidence/time correctness；procedure 看 action success 与 harmful transfer；profile 看 personalization benefit、staleness、consent 和 leakage；world/project 看 current-state consistency 与 environment/repo version；shared state看协作收益、authority、conflict 和 revocation；control metadata 看 rollback、delete propagation 与 audit completeness。

## 7. 成熟度、近期信号与剩余空白

C14 的 final coverage 以论文为主、仓库很少，说明 taxonomy/theory 供给远多于 conformance artifact。2026 信号主要集中在 learned operation control、transaction/version、budgeted consolidation 和 explicit forgetting；它们在问题定义上趋同于“控制状态转移”，但仍来自不同协议和作者组，不能写成一个标准已经形成。

当前可以称为中等共识的是：对象类型不可混写；storage/retrieval/update 需要分工；provenance/time/scope/version 应穿过 representation→context；mutation 与 action 需要独立验收。争议仍包括 consolidation 的最优时机、learned controller 的跨域稳定性、parametric/latent 与 external memory 的边界，以及 shared/world/personal state 是否存在可移植 ontology。

仍需补的不是更多术语，而是四类 artifact：taxonomy→schema 映射、跨实现 operation semantics、conformance/test pack、external 与 model-native memory 在 persistence/update/delete/provenance/cost 上的匹配对照。任何新 taxonomy 若不能生成这些测试或改变决策边界，应视为解释性框架，而不是成熟工程标准。

<!-- synthesis:C14-S03 claims:FND-C03,FND-C05,FND-C14,FND-C19,FND-C23,EXP-C17,EXP-C18,EXP-C19,EXP-C20,REP-C22,BEN-C22 clusters:MM-C14 -->



## C14 原子证据附录

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

Scores from static conversational QA, environment task success, tool grounding, and operation/security lifecycle metrics are not a common leaderboard because their task units, access paths, agent settings, and metrics differ.
<!-- claim:BEN-C22 -->

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

Generative Agents stores a natural-language record of experience, synthesizes higher-level reflections over time, and dynamically retrieves memories for planning.
<!-- claim:FND-C01 -->

MemGPT introduces virtual-context management: it moves information across memory tiers and uses interrupts to manage control flow around an LLM with limited context.
<!-- claim:FND-C03 -->

MemoryBank separates storage, retrieval, and updating; its store includes conversation records, event summaries, and evolving user-personality assessments.
<!-- claim:FND-C05 -->

Reflexion is a useful procedural-memory boundary: its official artifact provides code, demos, and task logs for verbal-reflection experiments, but does not thereby establish a general persistent-state lifecycle system.
<!-- claim:FND-C07 -->

Voyager supplies a complementary procedural form of memory—an executable skill library—so reusable skills should not be conflated with mutable user facts or episodic traces.
<!-- claim:FND-C08 -->

A-MEM proposes agentic note construction with structured attributes, dynamic links to relevant history, and updates to historical contextual representations as new memories are integrated.
<!-- claim:FND-C09 -->

MemoryOS specifies short-, mid-, and long-term personal-memory tiers, with Storage, Updating, Retrieval, and Generation modules.
<!-- claim:FND-C11 -->

MemCon models memory operations as an MDP and learns an online policy over retrieve, plan injection, re-retrieve, consolidate, forget, and no-op actions.
<!-- claim:FND-C14 -->

MemTxn places a transaction boundary outside the answer model with source-supported write validation, temporal version selection, and a durable snapshot journal for application-visible recovery.
<!-- claim:FND-C17 -->

The budgeted-consolidation preprint argues that retention preserves raw details while consolidation improves coverage per token but may lose query-critical detail; it treats the preferred operator as budget-dependent.
<!-- claim:FND-C19 -->

ForgetEval's authors distinguish recall from mutation-plane operations such as supersede, release, and purge, and compare thirteen configurations with partly complementary failure-mode coverage.
<!-- claim:FND-C21 -->

Across the inspected systems, a useful architecture split is a data plane (records/tiers), a retrieval plane (selection/injection), and a mutation/control plane (admission, consolidation, supersede, forget, recovery); this is a report synthesis rather than a claim made verbatim by any one source.
<!-- claim:FND-C23 -->

## 补充可审计工程判断

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

Inference: the durable architecture boundary is not 'vector versus graph' alone; it is whether provenance, time/version, scope, and retrieval budget survive the representation-to-context compilation path.
<!-- claim:REP-C22 -->

<!-- synthesis:CLY-C14 claims:FND-C01,FND-C03,FND-C05,FND-C07,FND-C08,FND-C14,FND-C17,FND-C19,FND-C21,FND-C23,EXP-C16,EXP-C17,EXP-C18,EXP-C19,EXP-C20,REP-C22,BEN-C22 clusters:MM-C14 -->
