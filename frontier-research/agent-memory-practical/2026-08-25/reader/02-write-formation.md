# 02 写入与形成层：候选怎样成为可用的长期经验

## 结论

写入与形成层把一段任务经历转为后续 Agent 可以使用的长期材料。它需要判断候选是否值得保留、如何与旧经验并存、什么时候对读者可见，以及错误时能否回到来源。

Codex 使用两阶段形成。Phase 1 对每个合格 rollout 写出 `raw_memory`、摘要和 slug；Phase 2 则启动一个权限被压缩的内部 Agent，在全局 Memory 工作区中读取新旧差异，更新 `MEMORY.md`、`memory_summary.md`、rollout summaries 和可能的 skills。最终产物是一套可读 Markdown 手册，候选和调度状态仍保存在 SQLite。这很适合沉淀用户偏好、项目导航、重复成功流程和失败屏障；冲突判定、逐项更新和事实真值仍主要由模型完成，数据库层没有替它提供事务语义。

```text
rollout
  → Phase 1：逐线程抽取候选
  → 候选账本与使用统计
  → Phase 2：选择候选、查看工作区 diff
  → consolidation Agent 增量编辑 Memory 工件
  → 校验工件、重置 Git baseline、提交 selection snapshot
```

## Codex 的真实形成链

固定快照 [`c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29) 中，Phase 1 位于 `codex-rs/memories/write/src/phase1.rs`，Phase 2 位于 `phase2.rs`。两者中间的权威调度面是 `memories_1.sqlite`，文件工件位于 `CODEX_HOME/memories`。

### Phase 1：每个线程只生成候选，不直接改长期手册

Phase 1 prompt 要求模型优先记录能够减少未来重复说明、复用成功流程或避免已知失败的高信号内容，也允许 `no-op`。模型会给任务标记 success、partial、uncertain 或 fail。代码能校验 JSON 结构与非空字段，不能证明“这个结论真的正确”或“它应当覆盖旧结论”。

以第一章的退款修复为例，Phase 1 交给下一阶段的内容可写成：

| 字段 | 示例 | 作用 |
|---|---|---|
| `thread_id` | `T-1842` | 找回来源和使用反馈 |
| `source_updated_at` | `2026-08-20` | 判断新鲜度与增量 |
| `rollout_summary` | “退款 fixture 字段导致集成测试失败” | 低成本定位候选 |
| `raw_memory` | “旧 `refund_status` 字段失效；更新 fixture 后重跑 suite” | 给巩固 Agent 的详细候选 |
| `rollout_path` | 原始 JSONL 路径 | 可回到任务证据 |

这里仍没有确定的 `ADD`、`UPDATE` 或 `DELETE` 数据库操作。Codex 先把候选和来源关系留在数据库，等待低频的全局巩固。这避免每条 tool result 直接修改稳定 Memory，也引入 write-to-visible 延迟。

### Phase 2：一个受限 Agent 进行增量巩固

`phase2.rs` 领取一个 global singleton job 和 lease，准备 `CODEX_HOME/memories` 作为带 Git baseline 的工作区，从候选中选出最多 256 条，然后物化以下输入：

```text
memories_1.sqlite.stage1_outputs
  → raw_memories.md
  → rollout_summaries/<thread>.md
  + 旧 MEMORY.md / memory_summary.md / skills/
  + 上次成功 baseline 之后的 Git diff
  → MemoryConsolidation 内部 Agent
```

内部 Agent 的 cwd 被固定在 Memory root。它不能再次启动 Memory pipeline、调用 Memory tools、使用 MCP servers、Apps、协作或子 Agent。父权限 profile 为 Managed 时，固定代码把 writable roots 收窄到 Memory root，并把 network access 设为关闭；父 profile 为 External 时，代码会保留父 profile 明确给出的网络与工作区设置。它可以在当前 profile 允许的范围内读写 Memory root 工件。结束时系统检查 ownership token、验证工件、重置 Git baseline，并在一个数据库事务中提交 global job watermark 和这轮 selection flags。对读者来说，长期 Memory 更新是一项异步后台任务，不能把它当作同步、逐条的 CRUD API。[Phase 2 权限配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L308-L367)

下表把同一条候选放进这条链路：

| 阶段 | 退款示例的状态 | 用户何时能看到 |
|---|---|---|
| 原始 rollout | 工具错误、用户要求、修复过程 | 线程历史中 |
| Phase 1 candidate | “更新旧 fixture 后重跑 integration suite” | 通常不可作为稳定长期结论使用 |
| Phase 2 工作区 | 新候选与旧项目经验并排比较 | consolidation 运行中 |
| `MEMORY.md` | “refund tests：若字段失败，先检查 fixture schema” | 之后的读取路径可搜索 |
| `memory_summary.md` | 项目条目和检索路由 | 新线程可常驻得到 |

### 选择候选：使用反馈会影响形成

Phase 2 的 `get_phase2_input_selection` 会按 `usage_count`、最近使用时间、source 更新时间和 thread ID 选择候选。被引用过的候选更容易在之后的巩固中保留；从未使用的候选主要按新鲜度参与。回答实际使用 Memory citation 时，相关 rollout ID 会回写 `usage_count` 和 `last_usage`。

这是一条可观察的反馈环：

```text
候选被选入手册
  → Agent 更容易搜索到并引用
  → usage_count 增加
  → 更可能再次进入 Phase 2
```

它不等同于 learned retriever，也没有记录“候选被展示但没有帮助”这一反事实信号。因此常被找到的内容会得到更多保留机会；相关但尚未被成功引用的内容可能逐渐退出候选窗口。

### 工件校验解决了什么，没有解决什么

Phase 2 对 Memory root 做了较强的操作性约束：拒绝或清理 symlink，确认 `MEMORY.md` 是普通文件，确认 `memory_summary.md` 有 `v1` 首行，并清理临时 diff 后重置 baseline。lease、heartbeat、watermark 和 selection snapshot 也防止过期 worker 随意提交。

| 已由代码检查的事情 | 尚由模型判断的事情 |
|---|---|
| job 是否属于当前 worker | 两条候选是否表达同一件事 |
| 工件路径和类型是否安全 | 新经验是否真的推翻旧经验 |
| 必要文件是否存在、summary 格式是否合格 | 项目范围、用户偏好和事实是否被正确归纳 |
| 任务和 selection 是否完成提交 | 删除是否清除了所有语义派生物 |

因此 Codex 的形成层在后台任务和文件安全上较成熟，在“语义更新是否正确”上仍是生成式流程。

## 通用形成架构：先把候选与提交分开

从 Codex 可抽出的通用链路如下：

```text
证据事件
  → 候选抽取（事实、偏好、事件、流程或无操作）
  → 与现有状态比较
  → 保留 / 合并 / 更新 / 标记冲突 / 忽略
  → 提交稳定视图
  → 建立摘要、关键词、向量或图等派生物
```

不同系统的实质差异在“比较与提交”处。纯摘要系统将旧摘要和新内容交给模型重写；类型化系统先拆成原子事实或事件；受治理系统会把抽取结果当 proposal，再检查来源、范围、政策、重复和冲突。后两种增加了延迟和结构成本，但能让“为什么写进来”比一段无来源摘要更可检查。

## 近期机制：从生成摘要走向受约束状态转移

### MemTxn：来源支持的更新与可恢复快照

[MemTxn](https://arxiv.org/abs/2607.27834)（2026-07，预印本）把 memory update 放到回答模型之外：候选更新要由来源支持，Temporal Resolver 选择相应时间版本，durable snapshot journal 记录可恢复状态，并通过 Ordered PatchTest 检查更新。它解决的具体问题是“模型生成了一个看似合理的新结论，却没有证据、也可能在崩溃后留下半更新状态”。

简化数据流是：

```text
source receipt + proposed patch
  → 支持性检查 / 时间解析
  → 通过后写入 snapshot journal
  → 形成当前可见状态
```

与 Codex 相比，Codex 保留 rollout path 和 Git baseline，但将更新语义留给 Phase 2 Agent；MemTxn 尝试把来源检查和提交边界变成系统机制。它目前是论文与原型证据，不能视为行业通用实现或跨后端可靠性证明。

### Budget-dependent consolidation：合并的时机取决于任务量与预算

[Retain or Consolidate?](https://arxiv.org/abs/2607.17545)（2026-07，预印本）研究原始细节保留与巩固后 token 覆盖之间的权衡。它把写入、未来查询数量和存储预算一起纳入“何时保留、何时合并”的决定。对 Codex 的启发很直接：Phase 2 采用固定候选上限和后台周期，系统还没有公开显示它会按未来查询密度动态选择 retain 或 consolidate。

这类工作提出了合理的操作选择问题，但其结论依赖作者设定的任务、检索器和预算。它还没有给出可直接替换 Codex Phase 2 的成熟控制器。

### 受治理的写入管线：Caura 的工程对照

固定提交的 [Caura](https://github.com/caura-ai/caura/tree/54dd6d4f2075ca428b1f3a5a8c50114351ea4755) 展示了另一种更结构化的工程写法：`write.py` 将 scope、策略、去重、持久化、异步 enrichment 和 contradiction/lifecycle 分成显式 pipeline；其 `memories` 行包含 tenant、fleet、agent、type、content、embedding、FTS、status、visibility、`supersedes` 与时间字段。strong mode 会在持久化前做更多治理检查，fast mode 把部分处理放到后台，因此二者的延迟和一致性保证不同。

它补上了 Codex Markdown 工作流中较弱的 item-level scope、status 和 supersedes；同时也说明更强的控制面会把正确性分散到 route、worker、storage API 和后台任务中。固定代码和测试能证明实现形状，不能证明生产采用或端到端语义正确。

### Microsoft Agent Framework Azure Cosmos Memory：把抽取、去重和摘要做成可配置流水线（官方工程，README 复核 2026-08-25）

[Microsoft Agent Framework 的 Azure Cosmos Memory 包](https://github.com/microsoft/agent-framework/blob/main/python/packages/azure-cosmos-memory/README.md)给出了一个当前可运行的服务化写入路径。它先保存 conversation turns，再由 LLM 抽取 fact、procedural、episodic 和 unclassified 四类 Memory，随后生成 thread/user summary，并执行 deduplication 和 contradiction reconciliation。官方示例还提供 `FACT_EXTRACTION_EVERY_N`、`DEDUP_EVERY_N`、`USER_SUMMARY_EVERY_N` 和 `THREAD_SUMMARY_EVERY_N` 等 cadence 配置，以及 `min_confidence` 和 `top_k`。

它的具体数据流可以写成：

```text
每轮对话
  → Cosmos DB 保存 turn
  → 按 cadence 触发 LLM 抽取
  → fact / procedural / episodic / unclassified
  → 去重与矛盾协调
  → thread summary / user profile
  → 下次运行检索并注入上下文
```

Episodic Memory 默认 TTL 为 90 天；处理可以在进程内运行，也可以通过 Cosmos DB change feed 放到 Azure Functions。`user_id` 和 `thread_id` 作为逻辑 scope 传入 provider。这个实现与 Codex 的后台空闲线程回收形成清晰对照：Cosmos Memory 更接近按 turn/cadence 处理，Codex 更接近延迟的 rollout 批处理；前者更快看到新信息，后者更容易控制后台批量成本。

该包属于 Microsoft Agent Framework 的官方代码路径，依赖 Azure Cosmos DB 和 AI Foundry。仓库和 README 能证明组件、配置和数据流，不能证明在不同租户、不同模型和生产负载下的抽取正确率。

## 当前边界

- Codex 更新对用户可见有后台延迟；新候选不等于已经写入 `MEMORY.md`。
- 候选选择以使用和新鲜度驱动，会产生先被发现内容的自强化。
- Git baseline 能帮助下次运行看到未完成 diff，不能使文件写入与数据库提交成为跨介质原子事务。
- `remember`、`forget`、`update` 的显式请求会先写 append-only note，再由未来 Phase 2 解释；当前没有稳定 entry ID 的同步定向修改。
- 语义冲突、旧结论失效和派生内容删除仍缺少独立 verifier。

下一章说明这些候选、工件和来源信息分别被放在哪里，以及 Codex 选择文件化、词法化读取的原因；embedding 检索的适用位置也会一并说明。
