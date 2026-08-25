# 第 4 章　管理与演化：Memory 怎样被保留、修订、隔离和清除

## 结论

管理层决定一段候选经历之后的命运：进入全局手册、继续保留、等待下一次重写、因外部内容而隔离，或被清除。它处理的是跨任务、跨时间的状态变化，因此要同时看四件事：选择规则、使用反馈、污染边界和重置范围。

Codex 已经把这四件事做成了可观察的工程流程。它有候选账本、使用次数、后台单例任务、外部内容污染标记和全量 reset；最终的修订判断仍由 Phase 2 内部 Agent 写 Markdown 完成。调度与文件边界由确定性代码控制，哪条经验应合并、保留多久、怎样改写，仍有生成式判断参与。

## 4.1 这一层管理什么

前面几层产生 rollout、候选记忆和存储工件；管理层持续回答下面的问题。

| 管理问题 | 对用户的可见结果 | Codex 的主要载体 |
|---|---|---|
| 哪些候选值得进入下一次巩固 | 常用或近期经历更可能留在手册中 | `stage1_outputs` 的使用与时间字段 |
| 一次巩固应处理哪些候选 | `MEMORY.md`、摘要和 skills 被增量改写 | Phase 2 selection + Git baseline |
| 外部内容进入过线程后怎么办 | 该线程可以退出未来 Memory 来源 | thread `memory_mode` / `polluted` 状态 |
| 用户说“记住、更新、忘记”后怎么办 | 先留下不可覆盖的请求记录，随后由巩固处理 | `extensions/ad_hoc/notes/` |
| 全部清除到底清什么 | 当前生成式 Memory 消失，原始会话仍可能保留 | `memories_1.sqlite` + Memory 目录 reset |

这里的“管理”不等于数据库管理界面。它直接影响下一次 Agent 会看到哪段历史，也影响旧结论会不会继续影响行为。

## 4.2 Codex 的选择链：从候选账本到一次全局巩固

固定快照为 [`openai/codex@c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)。Phase 1 已把每个 rollout 的 `raw_memory`、`rollout_summary`、来源 thread、水位和使用字段写入 `memories_1.sqlite`。Phase 2 启动时，先领取一个全局 singleton job，再从这个数据库取候选；成功后才提交选择快照和新的 baseline。[Phase 2 主流程](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L47-L212)

```text
stage1_outputs
  → 按使用与新鲜度选取最多 256 条
  → 物化 raw_memories.md / rollout_summaries/*.md
  → Phase 2 Agent 对比 Git baseline 与新增材料
  → 更新 MEMORY.md、memory_summary.md、可复用 skills
  → 检查工件、reset baseline
  → 在同一数据库事务提交 selection flags 与 job watermark
```

选择顺序是：`usage_count` 降序，再按 `last_usage` 或 `source_updated_at` 的新鲜度、`source_updated_at` 和 thread ID 排序。使用过的候选按最后使用时间判断 30 天窗口；从未使用的候选按来源时间判断。默认最多选择 256 条。代码将成功的准确集合写回 `selected_for_phase2`，避免“这次到底处理了谁”只存在于模型输出中。[选择查询与提交](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L431-L525)

| 固定版本默认值 | 作用 | 读者能看到的后果 |
|---|---|---|
| 每次 startup 最多处理 2 个 rollout | 限制后台写入负担 | 新完成任务可能需等待多次启动 |
| 最近 10 天、至少空闲 6 小时 | 避免仍在变化的线程过早被提炼 | 太旧或持续活跃的线程不会成为候选 |
| Phase 2 最多 256 条 raw memories | 控制巩固上下文 | 很多候选时，低使用、较旧内容更容易被排到后面 |
| 未使用窗口 30 天 | 清理长期没有进入巩固视野的候选 | “未被用到”逐渐成为弱淘汰信号 |

这些默认值来自开源客户端，配置或托管环境可以覆盖它们；它们描述当前代码的工作方式，不能直接推广为所有 Agent 的通用最佳参数。

### 一个选择例子

假设候选账本中有四条记录：

| rollout | 内容摘要 | usage_count / last_usage | 来源更新时间 | 下一次优先级 |
|---|---|---|---|---|
| R-17 | 支付项目的集成测试顺序 | 6 / 昨天 | 20 天前 | 高 |
| R-31 | 同一项目一次未完成的排错 | 0 / — | 昨天 | 高 |
| R-08 | 已迁移分支上的构建命令 | 2 / 40 天前 | 50 天前 | 低 |
| R-42 | 刚发现的外部网页方案 | 0 / — | 今天 | 取决于污染状态 |

R-17 由于多次在后续回答中被引用，优先留在巩固输入中；R-31 足够新，也有机会被纳入；R-08 的时间和使用信号都弱；R-42 若被标为 `polluted`，会转入排除路径。这个例子展示的是排序机制，并不意味着某条“更常被引用”的经验一定更正确。

## 4.3 usage：引用回写形成一条简单的保留反馈

Codex 的读取提示要求 Agent 使用 Memory 后，在最终回答中附隐藏 citation block，带上实际文件行号和 rollout ID。读取模块解析该 citation；有效的 rollout ID 会让对应 `stage1_outputs` 行的 `usage_count` 加一，并刷新 `last_usage`。[citation 解析](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/read/src/citations.rs#L6-L50)、[usage 回写](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L51-L86)

```text
Agent 搜到 MEMORY.md 第 84 行
  → 回答末尾引用该行关联的 R-17
  → citation parser 验证 ID
  → R-17.usage_count + 1，last_usage = 当前时间
  → 下次 Phase 2 selection 更容易再看到 R-17
```

它给系统提供了“这一来源被实际用过”的信号，成本很低，也保留了来源线索。当前代码没有把它实现成点击率模型：系统没有记录“候选曾被展示却未采用”、用户是否认可这次引用、引用是否真的帮助任务成功。因此会出现曝光偏差：已在摘要中、关键词容易被搜到的材料更容易继续被引用；同样有价值但没有被找到的材料得不到强化。

## 4.4 pollution：外部上下文如何退出候选池

Codex 可以配置 `disable_on_external_context`。启用后，Web Search、Tool Search、可能带外部内容的工具输出，以及被标为会污染 Memory 的 MCP 调用，会将当前 thread 标成 `polluted`；它不再作为未来 Phase 1 的正常候选。若该 thread 在上一轮 Phase 2 selection 中，代码会安排后续 consolidation，尝试移除仅由这条 thread 支持的内容。[污染标记与 forgetting enqueue](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L617-L652)

这一机制针对的是来源隔离，避免网页、搜索结果或不可信工具材料直接沉淀成长期经验。固定配置中的 `disable_on_external_context` 默认值为 `false`；使用者必须开启它，防线才会生效。[Memory 配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/config/src/types.rs#L288-L354)

| 场景 | 线程状态 | 之后会发生什么 | 还没有得到的保证 |
|---|---|---|---|
| 本地代码与测试工具 | 正常 | 可按 idle/age 进入 Phase 1 | 提取内容一定正确 |
| 启用防护后的网页搜索 | `polluted` | 后续不再作为普通来源；可能触发巩固清理 | 已进入所有摘要、skill、缓存的内容立即消失 |
| 用户关闭 thread Memory | `disabled` | 阻止未来生成资格 | 已经写入手册的派生内容同步删除 |
| 未启用防护的外部工具 | 正常 | 仍可能进入候选流程 | 来源已被安全隔离 |

因此 `polluted` 只提供一次面向来源的软隔离。系统还要能够追到由它支持的摘要、技能、索引和已执行行动，才能证明旧内容不再造成影响。

## 4.5 更新、忘记与 reset：三种不同力度的操作

用户明确要求“记住、更新、忘记”时，专用工具不会直接改 `MEMORY.md`。它会在 `extensions/ad_hoc/notes/` 下创建带时间戳、不可覆盖的 Markdown note；下一次 Phase 2 必须把该 note 当作输入，同时把其中内容当数据而非执行指令。[ad-hoc note 实现](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/tools/ad_hoc_note.rs#L22-L90)

全量 reset 的行为更强，但边界也更窄：App Server 先在事务中删除 `memories_1.sqlite` 的 stage1 outputs 和 jobs，再清空 Memory 目录。它不会删除原始 rollout，也不会把历史 thread 的 `memory_mode` 改为 disabled。10 天窗口内、已空闲且仍 enabled 的旧 thread 之后可以再次被 Phase 1 抽取。[reset 路径](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/app-server/src/request_processors/thread_processor.rs#L1774-L1801)

```text
“忘记退款项目的旧构建规则”
  → append-only note：请求撤销
  → 下一轮 Phase 2 判断应删/改哪些手册内容
  → 未来 read path 不应继续推荐旧规则

“reset all memories”
  → 清候选账本与 Memory 工作区
  → 原始 rollout 仍在
  → 条件仍满足时，旧 rollout 以后可重新生成候选
```

这组区别解释了为什么管理 UI 中同样写着“忘记”，实际效果可能差很多：关闭 thread、写一条忘记 note、污染隔离和 reset 分别作用在生成资格、未来巩固、来源筛选和当前派生状态上。

## 4.6 近半年补充：从“重写文档”走向可治理状态

### GEM / MemState：把演化定义成状态操作

2026 年 5 月的 [GEM / MemState 论文](https://arxiv.org/abs/2605.26252)把长期 Memory 提炼为 ingestion、revision、forgetting、retrieval 四种状态级操作，并以 property-graph 原型验证可行性。它要解决的痛点是：一条 record、一个 embedding 或一条 edge 各自看起来正确，整体状态却会无控制增长、无法表达语义修订，或者遗忘后仍留下派生物。

若把这一思路放回 Codex，`raw_memory → MEMORY.md` 之间缺少稳定的对象 ID、修订关系和派生边；Phase 2 可以改对文本，却很难机械地列出“这条被撤销的 rollout 曾影响哪些摘要或 skills”。GEM 给出的方向是让 revision 和 forgetting 成为显式操作，并在状态中保留依赖。它目前是论文和 MemState 原型，尚未成为 Codex 或通用 Agent runtime 的共同接口。

### MemTxn：把来源验证、版本选择和故障恢复放在回答模型之外

2026 年 7 月的 [MemTxn](https://arxiv.org/abs/2607.27834)提出三件配套机制：Ordered PatchTest 检查更新是否有来源支持，Temporal Resolver 在冲突版本中选可见版本，durable snapshot journal 在故障后恢复声明的完整活跃状态。论文报告了作者设置下的审计、恢复和 FactConsolidation 结果；它仍是预印本和原型，不能外推为工业部署效果。

它补的是 Codex 管理链中的确定性空档。Codex 的 lease、watermark 和 Git baseline 已经能协调后台 job；Phase 2 仍由模型决定某句新材料是否足以覆盖旧结论。MemTxn 会把“可否更新”“当前版本是谁”“崩溃后如何恢复”拆到一个独立事务边界中。这样做增加了 receipt、版本和 journal 的维护成本，换来更可检查的更新语义。

可以把一次更新写成前后状态：

```text
旧状态：
  preference = "refund_status"
  valid_until = null
  source = T-1842

新输入：
  patch = "refund_state"
  source = T-1910
  valid_from = 2026-08-24

提交前：
  PatchTest 检查新值是否能回到 T-1910
  Temporal Resolver 选择当前可见版本

提交后：
  current = refund_state
  history 保留 T-1842 → T-1910
  snapshot journal 记录可恢复点
```

如果写入在“更新 current、尚未更新索引”时崩溃，恢复流程应从 journal 回到完整的旧状态或完整的新状态。Codex 的 Git baseline 能让下一轮看到未提交 diff，但它没有把每个 Markdown 结论和 SQLite row 绑定成这样的统一事务对象。

### Omri 等：把选择策略当作可计量的系统决策

2026 年 6 月的 [Agent Memory: Characterization and System Implications](https://arxiv.org/abs/2606.06448)对十类系统按 construction、retrieval、generation 分段测量，讨论 construction scheduling、query 量摊销和 freshness–latency 取舍。它提醒工程实现：一个“延后巩固”的策略没有消灭成本，只是把成本移到后台并引入新鲜度延迟。

Codex 的 6 小时 idle、每次最多两个 rollout、使用/新鲜度选择正好能放进这张账：写入负担较平缓，刚得到的纠正可能不会立刻可用。论文提供系统分析框架，不提供一个替代 Codex 默认值的万能参数。

## 4.7 当前边界

- selection 使用过往引用作为强化信号，缺少“被看见但未采用”和用户纠正的反向证据；
- `polluted` 与 `disabled` 防止未来采集，无法单独证明历史派生物、缓存或行动前提已全部修复；
- ad-hoc note 是 append-only 请求，没有逐项稳定 ID、同步删除或确定性冲突裁决；
- reset 跨越数据库和文件系统，两个步骤之间没有一个统一事务；它也不会抹去原始 rollout；
- 物理存储根仍是全局的，scope 主要通过 cwd、rollout summary 和文本组织表达；
- Phase 2 artifact validation 验证文件形状和路径安全，不验证每条文本结论是否仍受现有来源支持。

对不太懂技术的读者，最实用的判断标准是：先问系统能否说明“这条 Memory 从哪来、何时被用过、谁把它改掉、清除后哪些副本仍可能存在”。Codex 已能回答其中一部分；把这些回答连成可验证的修订链，仍是当前研究和工程的重点。
