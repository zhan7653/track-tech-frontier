# 第 4 层：管理与演化

首次形成以后，新证据可能补充、限制或推翻旧结论。管理层要把这种变化表达为 `update / merge / supersede / conflict / version`，并让当前状态与必要历史仍可解释。TencentDB 与 Codex 已经实现了不同形状的更新管理；MemTxn、GEM/MemState 与 ForgetEval 则把来源校验、状态轨迹和语义遗忘进一步变成显式机制。

## 4.1 TencentDB：L1/L2/L3/Skill 的 update、merge、version 与 conflict

[TencentDB Agent Memory `0aff21a`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a)没有一个统一 Evolution Engine。Chat 由 L1→L2→L3 的触发器和 Prompt 串联；Skill 走独立的不可变版本链。

### L1：先找相似旧对象，再决定当前表示

每个新 L1 候选先通过向量或 FTS 找 Top-K 相关旧项，冲突/去重 Prompt 再返回：

| 动作 | 语义 | 当前状态变化 |
|---|---|---|
| `store` | 没有相关旧项 | 创建新 ID，version=1 |
| `update` | 新证据修正或补强一个旧对象 | 保留对象身份，写新内容并递增 version |
| `merge` | 多条内容属于同一对象或方法 | 合并正文、类型、优先级、时间和来源，旧 current 退出 |
| `skip` | 重复、低价值或不应保存 | 不改变状态 |

更新后的版本继续追加到 JSONL，DB current row 与 FTS/vector 投影则切换到新内容。`source_message_ids` 与 team/user/agent/session/task scope 一起保留，使后续能回到触发这次变化的消息。这里的删除只是 update/merge 中旧 current 表示退出，不是跨层语义遗忘。

### L2：Scene Agent 用文件操作完成 UPDATE / MERGE

Scene Agent 读取新 L1、当前 Scene 索引和必要正文，判断 `UPDATE / MERGE / CREATE / NO-OP`。默认优先更新已有场景；高度重叠或容量压力下才合并。运行前工程侧备份 `scene_blocks/`，成功后扫描 Markdown 并重建 `scene_index.json`；失败或留下部分文件时可恢复备份。

合并时，Agent 先写新的综合 Scene，再把旧文件写为 `[DELETED]`；cleanup 随后 unlink 文件、清理 L2 当前视图并重建索引。这是“Agent 提议文件变化 + 工程代码落实”的局部管理动作。它不会自动沿来源关系去修改所有下游对象。

### L3：旧 Persona 与变化 Scene 共同驱动增量重写

L3 不在每条 L1 变化后立即更新。触发仍是首次生成、累计 50 条新 L1、`PERSONA_UPDATE_REQUEST` 或 Persona 丢失恢复。增量 Prompt 输入：

```text
old persona.md
+ 上次成功时间之后变化的 Scene 完整正文
+ trigger reason / counters / scene stats
```

Prompt 可以收窄、合并或移除旧规则；大改用 `write`，局部替换用 `edit`。成功后计数归零，工程侧清理模型误写的导航并重新追加最新 L2 导航。已有 Session 常使用 `session_init` 缓存，所以新 Persona 主要在新 Session 生效。

用“失败测试规则”可以看到冲突如何跨层传播：

```text
旧 L1/L2/L3：所有代码修改前先写失败测试

新 Session：纯重构没有待修复失败，但必须先建立行为基线
  → L1 update/merge：把绝对规则改成条件规则
  → L2 UPDATE：区分缺陷修复与纯重构
  → L3 触发后重写：
     缺陷修复先建立失败证据；纯重构先锁定行为基线
```

这不是数据库依赖图自动传播。若 L2/L3 尚未触发或生成失败，高层状态可以暂时落后于 L1。

### Skill：immutable versions 与 active head

Skill Review 在新轨迹到来后先通过最近提示、`skill_list`、`skill_view` 读取当前能力，再选择 no-op、create、update、patch 或 `files_write`。对已有 Skill 的写操作必须带刚读到的 `expected_version`；stale version 会被拒绝并要求重读。

```text
auth-token-revocation@v1
  基本撤销流程
      ↓ 新轨迹：多实例状态不一致
auth-token-revocation@v2
  Decision rules 加入共享 Store
      ↓ 新轨迹：旧 token / 并发刷新回归缺失
auth-token-revocation@v3
  Validation 补上两类测试
```

每个 `(skill_id, version)` 是不可变快照；成功写入后旧版 `is_head=0`，新版 `is_head=1`，FTS/vector 只更新 active head。Review Agent 没有 delete 工具，因此自动链的主要动作是版本化修订和 no-op，而不是自主淘汰整个 Skill。管理动作可回查 [L1 writer](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/0aff21a/MemoryCore/src/core/record/l1-writer.ts)、[Scene Prompt](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/0aff21a/MemoryCore/src/core/prompts/scene-extraction.ts)、[Persona 模块](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a/MemoryCore/src/core/persona)与 [Skill 模块](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a/MemoryCore/src/core/skill)。

## 4.2 Codex：Phase 2 文件级合并、改写、supersede 与冲突处理

[Codex `c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)没有稳定 Memory item ID 上的 per-fact update。新/变化 rollout 先刷新对应 Phase 1 candidate；Phase 2 再把选中候选、旧文件、ad-hoc notes 与 workspace diff 交给 Consolidation Agent，重写同一套全局 Markdown。

```text
new/changed Stage 1 candidates
+ old MEMORY.md / memory_summary.md / skills
+ raw_memories / rollout_summaries 的增删改 diff
→ Phase 2 incremental consolidation
→ current MEMORY.md / summary / skills
```

Prompt 对文件级更新规定了几条关键语义：

- 新候选合入适当 task group，而不是机械追加；
- diff 中的输入修改与删除必须传播到正式文件；
- 一个 Memory block 若同时有失效与仍有效来源，只移除失效 reference 或局部结论，不能整块删除；
- `MEMORY.md` 收窄后同步修正 `memory_summary.md`；
- 无 meaningful signal 时保持最小变更；
- 不打开原始 rollout transcript，冲突依据来自候选与 rollout summary。

例如旧 `MEMORY.md` 写“所有修改前先写失败测试”，新 candidate 明确限定纯重构只需行为基线。Phase 2 不是建立一条 `SUPERSEDES` edge，而是直接把段落改成两条条件规则，并更新 summary 导航。旧表述仍能在原始 rollout、candidate source 和 Git 差异中回查，但当前 Agent 只读最新文件。

Git baseline 让下一次 Phase 2 看见上次成功基线与当前工作区的差异；job ownership、watermark 和 selection snapshot 管理后台提交。它们能说明哪次生成成功处理了哪些候选，却不能证明每个 clause 都已正确解冲突。文件间的语义一致性仍由 Phase 2 Prompt 与后续运行检查维持。

Codex 的管理单元因此是“受来源指针约束的文件级 current state”，而 TencentDB 同时有 L1 item version、Scene 文件和 Skill version head。两者都能修正当前内容，但都没有统一的跨对象 revision graph。文件改写与 selection 状态分别见 [Phase 2](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs)和 [Memory state runtime](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs)。

## 4.3 MemTxn：来源校验、Temporal Resolver、提交与恢复

[MemTxn](https://arxiv.org/abs/2607.27834)把更新拆成四个职责，形成位于 answer model 之外的 transaction boundary：

```text
source receipt + proposed patch + current state
→ Ordered PatchTest：新断言是否由来源支持
→ Temporal Resolver：冲突版本中谁当前可见
→ commit new revision / reject
→ durable snapshot journal：保存可恢复的 active map
```

### Ordered PatchTest 先验证“能不能写”

更新 proposal 不能只因语言流畅而被接受。PatchTest 对新 assertion 与 source span/tool receipt 做有序检查；不支持的 clause 被拒绝。论文报告的 item-disjoint audit 用 supported originals 与 hard negatives 检查这道准入，但结果只适用于其作者协议。

### Temporal Resolver 再决定“哪一版可见”

当旧值与新值冲突时，Resolver 使用时间和版本信息选择 application-visible state，同时保留必要历史。例如：

```text
v1  所有修改前先写失败测试
source: Session A

proposal v2
  缺陷修复：先失败测试
  纯重构：先行为基线
source: Session B 的明确纠正

结果
  current = v2
  history = v1 → v2
```

这与“把两句话都放进 top-k，让回答模型自己猜”不同；可见版本在进入回答模型前已经被解析。

### Snapshot journal 恢复的是完整 active state

多 key 更新可能只写成功一部分。MemTxn 的 durable snapshot journal 记录声明的 active map；故障后恢复完整旧状态或完整新状态，而不是假设它知道底层实际写成功了哪些 key。论文在 LongMemEval-S、LoCoMo 状态与 MemoryAgentBench FactConsolidation 上报告作者实验结果；它是原型机制证据，不等于任意文件、向量和图后端已经共享一个 ACID 事务。

MemTxn 将“模型提出修改”“来源允许修改”“当前版本切换”“故障恢复”分开。这个分工正是 TencentDB/Codex 生成式改写中尚未独立建模的部分。

## 4.4 GEM/MemState：状态级 revision 与派生关系管理

[GEM / MemState](https://arxiv.org/abs/2605.26252)认为长期 Memory 的正确性不是某一 row、embedding 或 edge 单独正确，而是整个 state trajectory 在多次变化后仍满足约束。它把 ingestion、revision、forgetting、retrieval 定义为四种 state-level operators，并在 property-graph 原型中把 content、typed structure 与 policy 放在同一状态模型。

对 revision 最重要的变化是：系统必须区分“相关”与“派生”。`SIMILAR_TO` 或普通 association 只帮助查找，不应因上游变化自动删除邻居；extension/dependency/derived-from 关系才表示下游对象依赖某个 revision，需要失效或重算。

```text
L1 fact f1：所有修改前先写失败测试
  ├─ derives → Scene s1
  ├─ derives → Persona rule p1
  └─ derives → Skill validation k1

f1 revision → f2：纯重构改为行为基线
  → s1 / p1 标记受影响并重算
  → k1 只有真正依赖绝对规则时才进入 revalidation
```

输出不是一次无差别全库重写，而是新的 governed state：哪些 revision 成为 current、哪些派生物已重建、哪些仍 unresolved。TencentDB 当前用 L1 scheduler、L2/L3 Prompt 串联，Codex 用全局 Phase 2 重写；GEM/MemState 把这种传播关系提升为显式数据管理语义。

## 4.5 Control-Plane Placement / ForgetEval：语义遗忘怎样落地

[Control-Plane Placement / ForgetEval](https://arxiv.org/abs/2606.15903)研究的不是“有没有 delete API”，而是 mutation hook 放在哪里，会覆盖哪类遗忘失败。论文把 recall plane 与会改变状态的 control plane 分开，并使用三种操作语义：

| 操作 | 状态含义 |
|---|---|
| `supersede` | 新 revision 成为 current，旧版保留为历史 |
| `release` | 对象退出 active working/context 层，但 durable state 可保留 |
| `purge` | 在受管范围内清除 payload 与派生投影 |

它比较的三种 placement 各自看到不同信息：

1. **deterministic primitive** 直接按标识与时间改 store，擅长精确 lexical/temporal 目标，但难以处理同一对象的别名、跨语言表述或被拆开的 compound fact；
2. **inscribe-time LLM** 在写入时做 canonicalization，能把别名归到稳定对象，却还不知道用户未来一次遗忘请求具体要撤销哪个语义部分；
3. **mutation-time hook** 在收到 supersede/release/purge 意图时解析目标与范围，再调用确定性 primitive，因而能处理 prefix collision、compound fact 等 intent-aware mutation。

例如 Memory 中同时存在“本地 Map 适合单实例测试”和“本地 Map 可用于生产”。用户要求撤销第二条时，简单字符串删除可能误删两条；写入时 canonicalization 只能知道它们都谈 Map；mutation-time hook 需要把“生产适用性”解析为目标，再让底层只更新对应 revision 和派生状态。

ForgetEval 用模板与 adversarial cases 分别测 canonicalization 和 intent-aware deletion，并让异构 store 通过 Adapter Protocol 暴露真实支持的操作。它说明语义遗忘至少需要：稳定对象/版本、明确操作、正确 placement、派生修复与可核验结果。TencentDB 的 L1 current 替换、L2 文件清理或 L3 重写，以及 Codex 的文件级删改，都只是局部更新结果；两套固定实现没有把“未来不再相信、召回、派生或据此行动”建模成统一的语义遗忘机制。

第 5 层从这里接过已经形成的当前状态，继续回答每一种 Memory 究竟怎样进入上下文。
