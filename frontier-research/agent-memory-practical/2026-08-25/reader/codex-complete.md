# Codex Memory 完整说明：从 rollout 到可复用状态

**固定代码快照：2026-08-23｜commit `c9b19deb09c1841ce7acc33ddb96276030936a29`**
**最近稳定版本：[`rust-v0.149.0`](https://github.com/openai/codex/releases/tag/rust-v0.149.0)**
**当前仓库文档复核：2026-08-25**

正文以固定 commit 作为代码分析锚点；release tag 用来标记当时的版本背景，不能替代逐文件定位。当前 `main` 的 Memory README 用于复核 pipeline 是否仍保留同一组阶段和工件。

本章只分析公开的本地 CLI/App/IDE host 路径。模型权重、隐藏服务端调度、云端完整实现和真实用户 Memory 文件不在源码可见范围内。固定快照的代码级材料见 [v10 Codex 工程报告](../../../../examples/agent-memory-v10/reader/projects/openai--codex.md)。当前仓库对 pipeline 的结构说明见 [codex-rs/memories/README.md](https://github.com/openai/codex/blob/main/codex-rs/memories/README.md)。

## 一句话看懂 Codex 的形状

Codex Memory 是一条“后台生成、文件化读取”的流水线：

```text
符合条件的 root rollout
  ↓
Phase 1：逐线程模型抽取
  ↓
memories_1.sqlite：候选、job、租约、watermark、usage
  ↓
Phase 2：全局受限 Agent 巩固
  ↓
~/.codex/memories/
  ├─ memory_summary.md
  ├─ MEMORY.md
  ├─ rollout_summaries/
  └─ skills/
  ↓
新线程常驻 summary + 按需词法读取
  ↓
回答 citation → usage 回写 → 下一轮 Phase 2 选择
```

它把模型判断集中在写入和巩固阶段，把读取做成可检查的本地文件访问。SQLite 负责候选和调度；Markdown 与 skills 承担 Agent 实际使用的内容。

## 1. Codex 同时维护哪些状态

把以下状态分开，才能看懂 Memory 的边界：

| 状态面 | 主要载体 | 解决的问题 | 在长期 Memory 中的地位 |
|---|---|---|---|
| 当前上下文 | response items、tool outputs、world state | 当前 turn 如何继续 | 输入来源，最终 Memory 仍需后续形成 |
| Compaction | 压缩后的线程历史 | 同一线程如何继续处理长对话 | 运行时状态 |
| 线程与项目元数据 | `state_5.sqlite`、rollout JSONL | thread、cwd、branch、commit、来源和权限 | 来源与作用域依据 |
| Goal | Goal DB / Goal extension | 当前长期任务的目标和进度 | 控制面 |
| 确定性规则 | `AGENTS.md`、仓库文档、skills | 必须稳定执行的规则和流程 | 与 Memory 相邻的权威状态 |
| 生成式 Memory | `memories_1.sqlite` + `~/.codex/memories/` | 跨线程复用偏好、项目经验和流程 | 本章的主体 |

OpenAI 的仓库实现会过滤 developer、`AGENTS.md` 和 Skill 注入，避免把本来有明确权威载体的规则再次交给生成式 Memory 学习。规则文件和 Memory 分担不同一致性要求：前者要求每次稳定生效，后者提供历史线索和复用经验。

## 2. 什么时候启动后台 Memory

Memory pipeline 挂在 root session 的启动路径上。当前官方文档列出的前置条件是：session 不能是 ephemeral，Memory feature 必须启用，session 不能是 Subagent，state DB 必须可用。满足条件后，pipeline 异步执行 Phase 1，再执行 Phase 2。[官方触发与阶段说明](https://github.com/openai/codex/blob/main/codex-rs/memories/README.md)

固定快照的默认候选窗口和调度参数包括：

| 参数 | 固定快照中的默认含义 |
|---|---|
| `max_rollout_age_days` | 只扫描最近约 10 天的线程 |
| `min_rollout_idle_hours` | 至少空闲约 6 小时才进入候选 |
| `max_rollouts_per_startup` | 每次启动最多认领 2 个 rollout |
| Phase 1 concurrency | 最多 8 个抽取任务并行 |
| rate-limit guard | 剩余额度过低时跳过后台生成 |
| `max_raw_memories_for_consolidation` | Phase 2 最多选择 256 个候选 |

这些是开源默认配置，不能推断所有托管客户端都使用相同值。后台延迟带来两个直接结果：任务结束时不会立即出现最终 Memory；用户长时间不再启动 root turn 时，旧线程可能暂时没有进入形成流程。

## 3. Phase 1：把一个 rollout 变成候选

### 3.1 选择与认领

候选从 `state_5.sqlite` 的 threads 表和 Memory 状态库共同筛选。代码会检查 source、归档状态、`memory_mode`、更新时间、idle cutoff、已有 watermark 和正在运行的 lease。任务先写入 job claim，再交给 worker，避免多个启动任务重复处理同一线程。

对应代码路径：

- [startup pipeline](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/start.rs#L24-L73)
- [候选筛选与认领](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L133-L285)

### 3.2 取哪些 rollout 内容

Phase 1 会解析 rollout JSONL，再筛出适合 Memory 形成的 response items、工具调用/结果和 root rollout 中的 inter-agent communication。SessionMeta、TurnContext、WorldState、Compacted marker、security score 以及 developer/规则/skill 注入不会作为普通记忆文本发送。

长 rollout 会按当前模型的有效 context window 计算预算。固定快照的 prompt 逻辑把约 70% 的有效窗口留给 rollout，缺少模型元数据时使用回退上限，并采用头尾保留的截断方式。[输入过滤](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase1.rs#L404-L486)｜[输入预算](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/prompts.rs#L98-L126)

### 3.3 输出和候选落库

抽取模型必须返回严格 JSON：

```json
{
  "rollout_summary": "任务摘要和后续定位线索",
  "rollout_slug": "可选的短标识",
  "raw_memory": "从该 rollout 提炼的候选记忆"
}
```

`raw_memory` 是模型派生文本；原始证据仍由 `rollout_path` 指向的 JSONL 保存。代码验证 JSON 结构、字段和任务状态，却不能证明内容中的事实、scope 或冲突判断正确。

Phase 1 成功后，把输出写入 `memories_1.sqlite` 的 `stage1_outputs`，同时保存 source watermark、生成时间、usage 计数、最近使用时间和 Phase 2 selection 标记。失败任务保留 retry、lease 和错误信息。[Phase 1 输出结构](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase1.rs#L50-L63)

## 4. `memories_1.sqlite`：候选账本和调度控制面

这个数据库承担两种职责：

1. 保存逐 rollout 的候选内容和使用状态；
2. 协调 Phase 1/Phase 2 的 job、lease、retry、watermark 和 ownership。

核心表可以概括为：

| 表/字段族 | 记录什么 |
|---|---|
| `stage1_outputs` | thread、source watermark、raw/summary/slug、生成时间、usage、last usage、selection 标记 |
| `jobs` | 阶段、状态、worker、ownership token、lease、retry、错误和 watermark |

SQLite 在这里更像候选和调度账本。新线程读取的主要内容来自 Memory root 中的 Markdown 和 skills 文件，不能把这两个状态面混写成一个“知识库”。

## 5. Phase 2：一个受限 Agent 巩固全局文件

Phase 2 先领取 global singleton job，再从 stage-1 候选中选出一个有界集合。选择排序主要使用：

```text
usage_count DESC
→ last_usage / generated_at DESC
→ source_updated_at DESC
→ thread_id DESC
```

使用过的候选按最近使用时间判断新鲜度；从未使用的候选使用生成或来源时间。系统把选中的候选同步为：

- `raw_memories.md`：本轮合并的 Phase 1 原始候选；
- `rollout_summaries/<slug>.md`：逐 rollout 摘要；
- `phase2_workspace_diff.md`：相对于上次成功基线的变化。

如果工作区有变化，Codex 启动一个专用 `MemoryConsolidation` Agent。这个 Agent 使用 Memory root 作为 cwd，关闭 Memory tools、MCP、Apps、协作委派和递归 Memory 生成。父权限 profile 为 Managed 时，固定代码把网络关闭并把可写根目录收窄到 Memory root；External profile 会保留父 profile 明确给出的网络与工作区设置。它读取旧的 `MEMORY.md`、`memory_summary.md`、`skills/`、新候选和 Git diff，再进行增量巩固。[Phase 2 流程](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L47-L212)｜[巩固 Agent 权限](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L308-L367)

成功后，系统验证工件、重置 Git baseline，并在状态库中提交 job 和 selection watermark。验证器能检查文件存在、summary 版本头和 symlink 等确定性条件；它不会证明模型合并了正确事实、保留了所有冲突或完成了派生删除。

## 6. 一条完整任务 walkthrough：退款测试经验怎样走完一圈

下面用一个固定格式的示例把整条链路串起来。文字和 ID 是示意数据；组件、文件和控制流对应固定快照中的真实形状。

### 第一天：任务运行

```text
thread_id: T-1842
cwd: /work/payments
branch: fix/refund
git_sha: 91f3...
memory_mode: enabled

用户：退款集成测试又失败了，先检查 fixture schema。
工具：cargo test -p payments --test refunds
结果：fixture 仍使用旧字段 refund_status
Agent：更新 fixture，再重跑 integration suite
```

这些内容先留在 thread rollout JSONL。Codex 不在这一刻直接改 `MEMORY.md`。

### 第二天：后续 root turn 触发 Phase 1

一个新的 root turn 启动后，后台 worker 检查 T-1842 的 source、更新时间、idle cutoff、memory mode 和 lease。若它符合固定快照的默认窗口，Phase 1 读取 rollout，过滤规则注入和运行控制项，做 secret redaction 与上下文截断。

模型返回：

```json
{
  "rollout_summary": "refund integration test failed because fixture used refund_status",
  "rollout_slug": "refund-fixture",
  "raw_memory": "payments 项目中，退款集成测试先检查 fixture schema；旧 refund_status 字段会导致失败，更新 fixture 后再运行 suite。"
}
```

这条结果写进 `memories_1.sqlite.stage1_outputs`：

```text
thread_id = T-1842
source_updated_at = 2026-08-20
usage_count = 0
last_usage = NULL
selected_for_phase2 = 0
rollout_path = .../T-1842.jsonl
```

此时系统已经有了“候选”和“来源”，但全局手册还没有这条内容。

### 第三天：Phase 2 巩固

后续启动触发 Phase 2。它把选中的候选写成临时输入：

```text
raw_memories.md
rollout_summaries/refund-fixture.md
phase2_workspace_diff.md
```

受限的 `MemoryConsolidation` Agent 读取旧的 `MEMORY.md`、新的 diff 和这份 rollout summary，可能写出：

```markdown
## Payments / refund integration tests

- 先检查 fixture schema 是否仍使用 `refund_status`。
- 若字段已迁移，更新 fixture 后再运行 integration suite。
- 来源：rollout T-1842
```

随后 Phase 2 验证工件、重置 Git baseline，并提交本轮 selection snapshot。新线程之后才有机会通过 `memory_summary.md` 的项目索引找到这段内容。

### 第四天：新线程读取并行动

用户输入：“帮我修一下退款测试。”

读取链路可能是：

```text
memory_summary.md
  → 找到 payments / refund 任务组
MEMORY.md search("refund", "fixture")
  → 命中 MEMORY.md:84-89
read(84..105)
  → 得到 T-1842 和旧字段线索
读取当前仓库 fixture 与测试输出
  → 判断旧经验是否仍适用
```

Memory 给出的是一个检查方向。Agent 仍要查看当前 branch、文件和测试结果，再决定是否修改。工具权限由当前 sandbox 和 approval 规则决定。

如果回答采用了这条 Memory，read-path prompt 要求附带类似下面的隐藏 citation：

```text
MEMORY.md:84-89; rollout_id=T-1842
```

解析器据此把 `T-1842.usage_count` 从 0 改为 1，并刷新 `last_usage`。下一次 Phase 2 选择候选时，T-1842 会得到一个使用信号。

### 第五天：新证据改变结论

如果当前测试显示项目已经从 `refund_status` 迁移到 `refund_state`，用户又明确说“以后不要再按旧字段处理”，系统会先把这条请求记入 append-only note。下一次 Phase 2 需要把 note、当前 rollout 和旧的 T-1842 候选放在一起处理。固定 Codex 实现没有给每条 Markdown 结论分配统一的可事务更新 ID，因此最终删改仍依赖巩固 Agent 的语义判断。

这条 walkthrough 展示了 Codex 的强项和边界：后台调度、来源回查、文件化阅读和 usage 回写都有清楚的代码路径；事实修订、跨项目硬隔离、派生删除和“引用后是否真的成功”仍需要更强的状态与反馈机制。

## 7. 读取路径：摘要常驻，细节按需打开

开启 `use_memories` 后，Codex 会把 `memory_summary.md` 注入新线程。固定快照限制常驻摘要约 2500 tokens，随后由 read-path prompt 指示 Agent 按需使用本地 Memory 工具或只读 helper root。

读取层形成三层：

```text
L0  memory_summary.md
    全局导航、偏好和 scope 线索

L1  MEMORY.md
    按 cwd、项目和任务族组织的手册

L2  rollout_summaries / skills / 原始 rollout
    需要具体步骤、错误文本或证据时再打开
```

`LocalMemoriesBackend` 的 search 是递归 substring scan，支持任意/全部 query、行窗口、大小写与 normalized 比较、上下文和分页，按路径与行号排序。它不计算 embedding 距离，也不运行 ANN 或 learned reranker。[读取扩展](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/extension.rs#L22-L76)｜[backend contract](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/backend.rs#L6-L133)｜[词法搜索](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local/search.rs#L17-L88)

这套读取路径把召回质量的一部分责任放到巩固 Agent：标题、关键词、task group 和 summary 组织方式会直接影响后续 substring search。它换来了简单、便宜、可解释和容易给出行号引用的访问面。

## 8. 作用域与几个相邻状态

Codex 的 Memory root 通常是一个全局物理目录。project、cwd、branch、commit、origin 和 task group 主要写入 rollout 元数据、summary 头部和 Markdown 结构，再由主 Agent 在读取时选择相关块。当前代码没有在文件读取层按 current cwd 强制过滤整个全局 summary。

这形成了“全局存储、逻辑路由”的作用域形状：稳定的用户偏好和工具经验可以跨仓库复用，项目经验也可能被错误地带入另一个 worktree。公开的 [scope 请求 #18343](https://github.com/openai/codex/issues/18343) 说明用户正在要求更明确的 global/project/hybrid/thread-only 语义；issue 是需求和问题线索，不代表已经发生普遍泄露。

几个容易混淆的状态有不同时间尺度：

| 机制 | 时间尺度 | 主要作用 |
|---|---|---|
| Compaction | 当前 thread | 压缩上下文，让同一线程继续工作 |
| Goal | 当前长期任务 | 保存目标、进度和完成条件 |
| Memory | 跨 thread | 复用偏好、项目经验和流程 |
| `AGENTS.md`/skills | 项目或组织规则 | 提供确定性规则与可复用工具流程 |

Subagent 不独立触发长期 Memory Writer。root rollout 中的 inter-agent communication 仍可能进入 Phase 1，因此子 Agent 的长期影响取决于主线程实际收到和保留的通信。Guardian review session 会关闭 `use_memories` 和 dedicated memory tools，让复核过程减少个人历史影响。

## 9. 更新、遗忘和重置

Codex 提供几种不同力度的操作：

### 8.1 Thread memory mode

`enabled/disabled` 主要影响线程未来能否生成新候选。关闭一个线程不会自动从已经生成的 `MEMORY.md` 删除派生条目。

### 8.2 外部内容污染

开启 `disable_on_external_context` 后，Web Search、Tool Search、部分 MCP 输出等外部内容可以把线程标记为 polluted，并触发后续巩固清理只由该线程支持的内容。这个开关在固定版本中默认关闭。

### 8.3 Ad-hoc note

`memories.add_ad_hoc_note` 只在用户明确提出 remember、forget 或 update 时写入 append-only note。note 使用 create-new，不能覆盖同名文件；下一次 Phase 2 再解释它应该怎样修改长期工件。[ad-hoc note 工具](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/tools/ad_hoc_note.rs#L22-L90)

### 8.4 Full reset

App Server 的 reset 会清空 Memory 数据库中的 stage-1/job 行并清空 Memory 目录，但不会删除原始 rollout，也不会改变线程的 memory mode。符合年龄和空闲条件的旧线程之后仍可能再次被抽取。因此 reset 表示清除当前生成状态，不能当作原始来源和所有派生影响的不可逆删除。

## 10. 安全边界

Codex 的确定性安全措施集中在路径、权限和后台 worker：

- Memory feature 可关闭；
- secret redaction 作用于序列化输入和模型输出；
- Memory root 拒绝 symlink、越界路径、隐藏组件和绝对路径；
- 普通主 Agent 对 Memory root 主要是只读访问；
- Phase 2 Agent 在 Managed profile 下无网络并收窄到 Memory root；Memory tools、MCP/Apps、协作和递归 Memory 生成被关闭；External profile 可能继承父级网络与工作区设置；
- ownership token、lease、heartbeat 和 snapshot flag 限制过期 worker 提交；
- citation 保留文件行和 rollout provenance。

内容层仍依赖模型判断。工具输出和用户历史可能包含提示注入；secret redaction 也不等于所有敏感事实都不会进入摘要；Phase 2 validator 无法证明事实支持、scope 正确或删除传播完整。

## 11. 并发、恢复和可观察故障

Phase 1 使用每线程 job、source watermark、lease 和 retry。Phase 2 使用全局 singleton job、heartbeat、stale takeover 和成功 cooldown。Memory root 以 Git baseline 表达上次成功状态，失败后下一轮可以看到未提交 diff。

跨数据库和文件系统的边界仍然存在：候选选择、SQLite 状态、Markdown 写入和新线程读取没有一个覆盖全部步骤的原子快照。官方 [issue #26684](https://github.com/openai/codex/issues/26684) 讨论并发 Stage 1 写入与 Phase 2 `LIMIT/OFFSET` 分页可能造成候选遗漏或重复；[issue #38860](https://github.com/openai/codex/issues/38860) 报告长 rollout 的 context-window failure。两者都是公开问题报告，本文不把它们转换成总体发生率。

## 12. 与七层通用架构的对应关系

| 通用层 | Codex 对应实现 | 当前证据强度 |
|---|---|---|
| 输入 | startup eligibility、rollout filter、redaction、budget | 代码和官方文档可见 |
| 写入 | Phase 1 JSON 抽取、Phase 2 consolidation | 代码、prompt、工件可见 |
| 状态 | SQLite candidates/jobs + Markdown/Git artifacts | schema 和文件路径可见 |
| 管理 | usage/recency selection、notes、pollution、reset | 代码可见，语义正确性较弱 |
| 读取 | summary injection、lexical search、progressive disclosure | 代码和 prompt 可见 |
| 使用 | read instructions、citation、只读 root、工具权限 | 代码和 prompt 可见 |
| 反馈 | citation → usage → selection → consolidation | 控制流可见，长期收益未独立测量 |

这个对应表提供了前七章的成熟锚点。每个功能章会把 Codex 这一格展开，再放入近期工作对该格的扩展。

## 13. Codex 目前最成熟、最薄弱的部分

### 较成熟

- 线程和 job 的持久化、租约、重试和 watermark；
- 两阶段形成和全局巩固的调度边界；
- 文件化 Memory workspace、Git baseline 和渐进读取；
- 路径、symlink、网络和后台 Agent 权限控制；
- citation、usage 和 selection snapshot 的可观察连接。

### 中等成熟

- 两阶段模型形成；
- usage/recency 驱动的候选保留；
- cwd/project 文本化 scope；
- append-only note 驱动的用户纠正；
- CLI/App/IDE 共用本地状态面。

### 证据不足或仍早期

- 事实正确性、去重、冲突和时态更新；
- project/worktree 硬隔离；
- item-level inspect/update/delete 和派生删除回执；
- 并发选择和文件读取的一致快照；
- Memory 对工具调用数、纠正次数和 Coding Agent 成功率的独立长期测量。

## 14. 外部前沿为什么会补这些位置

近半年的论文把注意力从“如何多存一点”移到“如何让状态变化可解释、可恢复、可治理”：

- 系统表征工作把 ingestion、construction、retrieval 和 generation 的成本分开；
- GEM/MemState 把 ingestion、revision、forgetting、retrieval 视为状态级操作；
- MemTxn 把 source-supported update、时间版本和 snapshot recovery 放到回答模型外；
- AgeMem v3（2026-07-23）把 store/retrieve/update/summarize/discard 暴露为 Agent policy 动作；
- MemTX 进一步讨论 belief commit、权限、来源和派生动作修复。[MemTX](https://arxiv.org/abs/2607.23929)

这些工作补的是 Codex 当前较薄的语义控制面。它们大多仍是预印本或原型，尚未提供跨 runtime 的统一接口和长期生产证据。

## 15. 证据边界

本章的 Codex 组件、路径、默认控制流和静态失败窗口来自固定 commit 与当前官方仓库。它们可以证明代码中存在某种结构，不能证明所有托管客户端都采用同一配置，也不能证明模型生成质量、真实故障率或生产采用规模。

论文结果只适用于论文给出的模型、数据、预算和评测协议。官方 issue 只能说明有人报告了某种问题。本文没有运行 Codex Memory pipeline，也没有读取真实用户 Memory 文件。
