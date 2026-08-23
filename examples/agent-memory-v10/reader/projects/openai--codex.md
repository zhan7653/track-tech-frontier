# OpenAI Codex 本地 Memory 系统：固定版本代码级架构分析

**代码快照：2026-08-23｜`openai/codex` commit [`c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)｜最近稳定 release：[`rust-v0.149.0`](https://github.com/openai/codex/releases/tag/rust-v0.149.0)**

Codex 的本地 Memory 不是一个向量数据库，也不是简单把上一轮对话摘要塞回 prompt。固定版本源码显示，它是一条由两个 LLM 阶段、两个 SQLite 状态面、一组 Markdown 工件、一个 Git 基线和按需读取工具组成的后台流水线。其目标不是保存所有聊天，而是从近期已结束任务中提炼可能改变未来 Agent 行为的用户偏好、项目知识、失败经验和可复用流程。

本报告分析的是 Apache-2.0 开源仓库中的本地 CLI/App/IDE host 实现。模型权重、训练方法、完整托管云调度和服务端策略不在源码可见范围内。OpenAI Docs 描述的产品行为与固定提交代码可以互相校验，但不能用来推断未公开的模型内部机制。

## 一句话结论

Codex Memory 的核心形状是：

```text
近期、已空闲、允许生成 Memory 的根线程
        │
        ▼
Phase 1：逐线程 LLM 抽取
raw_memory + rollout_summary + rollout_slug
        │
        ▼
memories_1.sqlite：候选、任务、使用次数、租约与 watermarks
        │
        ▼
Phase 2：全局受限 Agent 巩固
MEMORY.md + memory_summary.md + rollout_summaries/ + skills/
        │
        ▼
新线程常驻注入 memory_summary.md
        │
        ├─ 词法搜索 MEMORY.md
        ├─ 按行读取详细块
        └─ 必要时打开 rollout summary / 原始 rollout
        │
        ▼
最终回答附带 Memory citation
        │
        └─ 回写 usage_count / last_usage，影响后续保留与巩固
```

它的工程辨识度在于：**写入高度生成式，读取却刻意保持文件化、词法化和渐进披露；项目 scope 主要由文档内容和 cwd 元数据表达，而不是由物理数据库或访问控制隔离。**

## 1. 边界：Codex 同时维护多种状态，但只有一部分叫 Memory

Codex 当前公开架构中至少存在六种容易混淆的状态：

| 状态面 | 主要载体 | 解决的问题 | 是否属于本地长期 Memory |
|---|---|---|---|
| 当前模型上下文 | response items、tool outputs、world state | 当前 turn 如何继续 | 否 |
| 压缩上下文 | compacted history | 超过 context window 后如何延续同一线程 | 否 |
| 线程与项目元数据 | `state_5.sqlite`、rollout JSONL | thread、cwd、branch、commit、source、权限和历史定位 | 是 Memory 的来源与作用域依据，但不是最终记忆 |
| Goal 状态 | 独立 goals DB / Goal extension | 当前长期任务的目标、进度与完成条件 | 否，属于控制面 |
| 权威项目规则 | `AGENTS.md`、checked-in docs、skills | 必须重复适用的确定性规则与流程 | 与 Memory 相邻，但不会由后台抽取替代 |
| 本地生成式 Memory | `memories_1.sqlite` + `~/.codex/memories/` | 跨线程召回偏好、项目经验与可复用知识 | 是 |

OpenAI Docs 明确把 `AGENTS.md` 与 Memory 分开：必须稳定生效的团队规则属于仓库文档，Memory 只是辅助 recall layer。[官方 Memories 文档](https://learn.chatgpt.com/docs/customization/memories)与代码中的过滤规则一致：Phase 1 会丢弃 developer message，并从 contextual user fragments 中排除完整 `AGENTS.md` 和 skill 注入块，避免把权威规则重新学习成一份可能漂移的生成式副本。[Phase 1 过滤代码](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase1.rs#L404-L486)

这意味着 Codex 不是一个统一状态池，而是用不同状态面承担不同一致性要求。它能降低“规则被摘要改写”的风险，却也要求读者区分：同一句内容来自仓库规则、当前上下文、历史 rollout，还是 Memory Writer 的推断。

## 2. 启动时机：不是在聊天结束时立即写，而是在后来某个根线程启动时回收旧线程

Memory pipeline 挂在 app-server 的 turn start 上：当一个主环境中的新 turn 真正启动，并且本轮有输入时，Codex 才异步调用 Memory startup task。[turn start 接入点](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/app-server/src/request_processors/turn_processor.rs#L575-L601)

启动任务会先排除：

- ephemeral session；
- 未启用 `MemoryTool` feature 的运行；
- subagent 等非根 Agent session；
- 没有可用 state DB 的运行。

随后它准备 `~/.codex/memories/`，清理陈旧的未使用候选，检查账户剩余额度，再依次执行 Phase 1 和 Phase 2。[startup pipeline](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/start.rs#L24-L73)

因此产品文档中的“后台生成、聊天结束后不会立刻更新”在代码里有更精确的含义：旧线程先进入 state DB；等它空闲足够久，并且后来有一个合格的根 turn 启动，后台 worker 才扫描和认领它。若用户长时间不再启动 Codex turn，Memory 形成也可能推迟。

### 2.1 默认候选窗口

固定提交中的默认配置是：

| 参数 | 默认值 | 实际含义 |
|---|---:|---|
| `max_rollout_age_days` | 10 天 | 只扫描最近更新的线程 |
| `min_rollout_idle_hours` | 6 小时 | 活跃线程暂不抽取 |
| `max_rollouts_per_startup` | 2 | 每次 startup 最多认领两个 rollout |
| Phase 1 concurrency | 8 | 配置调大候选数后最多八个并行采样 |
| `min_rate_limit_remaining_percent` | 25% | 低于阈值时跳过后台生成 |
| `max_raw_memories_for_consolidation` | 256 | Phase 2 的候选上限 |
| `max_unused_days` | 30 天 | 从未使用或长期未使用候选的保留窗口 |

这些是开源默认值，不证明托管客户端没有配置覆盖。`MemoryTool` 本身被标为 Stable，但 feature 默认关闭；启用该 feature 后，`generate_memories` 与 `use_memories` 的配置默认值为 true，`dedicated_tools` 和 `disable_on_external_context` 默认 false。[feature 状态](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/features/src/lib.rs#L986-L1003)、[Memory 配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/config/src/types.rs#L288-L354)

### 2.2 线程筛选不是纯文件扫描

候选从 `state_5.sqlite` 的 threads 表按 source、归档状态、`memory_mode`、更新时间与 idle cutoff 过滤；当前线程被排除。允许的交互来源包括 CLI、VS Code、Atlas 和 ChatGPT。通过过滤后，worker 再根据 `memories_1.sqlite` 中的 output/job watermark 判断是否需要重新抽取，并用 lease 防止同一线程被重复处理。[候选认领查询](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L133-L285)

这套结构把原始 rollout、线程目录和后台 job 分开：rollout 是证据，state DB 是发现索引，memories DB 是生成和调度状态。三者任一缺失都可能造成“历史还在磁盘，但没有进入 Memory”的情况。

## 3. Phase 1：逐线程抽取，把完整 rollout 变成两个不同粒度的派生物

Phase 1 对每个认领线程执行以下步骤：

```text
rollout JSONL
→ 解析 RolloutItem
→ 只保留可用于 Memory 的 response items 与 inter-agent communication
→ 排除 developer / AGENTS.md / skill 注入块
→ secrets redaction
→ 按模型有效 context window 截断
→ 低 reasoning effort 的抽取模型
→ strict JSON output
→ memories_1.sqlite.stage1_outputs
```

### 3.1 输入不是原样复制

Phase 1 会过滤 SessionMeta、TurnContext、WorldState、Compacted marker、security score 和普通 event stream，只保留适合送入模型的消息、工具调用/输出以及 inter-agent communication。其后再做一次 secret redaction。[过滤与序列化](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase1.rs#L404-L475)

超长 rollout 并不是无限输入。代码按 active model 的有效 context window 计算预算，再取其中 70% 给 rollout；元数据缺失时退回 150,000 token 限额，截断工具保留头尾而不是只取开头。[输入预算](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/prompts.rs#L98-L126)

这降低了直接溢出风险，但带来另一种信息损失：长任务中部的决定、失败和用户纠正可能不进入抽取请求。一个 0.144.1 用户 issue 报告了长 rollout 的大量 context-window failure；当前快照已经有明确截断，因此该 issue 不能证明 0.149+/main 仍以同样方式失败，但它仍提示覆盖率必须按版本和 rollout 长度观察。[issue #38860](https://github.com/openai/codex/issues/38860)

### 3.2 输出虽然是 strict JSON，核心内容仍是自由 Markdown

模型必须返回：

```json
{
  "rollout_summary": "...",
  "rollout_slug": "...",
  "raw_memory": "..."
}
```

`rollout_summary` 用于路由和稍后逐 rollout 查看；`raw_memory` 是更详细的模型派生记录。这里的名字容易误导：`raw_memories.md` 不是原始对话，而是多个 Phase 1 `raw_memory` 字段的合并；真正不可变证据仍是 `rollout_path` 指向的 JSONL。[输出 schema 与持久化](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase1.rs#L50-L63)、[文件物化](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/storage.rs#L44-L77)

Phase 1 prompt 明确允许 no-op，并要求优先保存能够减少未来用户重复说明、复用成功流程或避免已知失败的高信号材料。它也会给每个任务标 success、partial、uncertain 或 fail。代码只能验证 JSON 形状和非空字段，无法确定这些语义判断是否正确。

### 3.3 模型与成本分层

在默认 OpenAI provider 下，固定提交把 Memory extraction 的 preferred model 设为 `gpt-5.6-luna`，reasoning effort 为 low；consolidation preferred model 为 `gpt-5.6-terra`，reasoning effort 为 medium。两者都可由 Memory config 或 provider override 改写。[provider defaults](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/model-provider/src/provider.rs#L126-L169)

这反映了明确的成本分工：大量逐线程抽取使用较轻模型，低频全局重写使用更强模型。rate-limit 查询失败时 guard 会 fail-open，继续运行，而不是保守停止；这优先保证 Memory 有机会更新，也意味着额度保护不是强一致策略。[额度 guard](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/guard.rs#L1-L56)

## 4. 中间权威层：`memories_1.sqlite` 保存的是候选和调度，不是最终知识库

2026 年 5 月后，Memory job state 从通用 state DB 移到独立的 `memories_1.sqlite`，减少与线程状态的锁竞争。该数据库只有两类核心表：

- `stage1_outputs`：thread id、source watermark、raw/summary、slug、生成时间、使用次数、最近使用时间、是否属于最近一次 Phase 2 selection；
- `jobs`：Phase 1/2 的 status、worker、ownership token、lease、retry、错误、输入/成功 watermark。

[Memory DB schema](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/memory_migrations/0001_memories.sql)

它承担的是候选账本、并发协调、重试和选择快照。最终给模型读取的知识仍是文件。这个双层设计让 DB 可以判断哪些 rollout 已处理、哪些候选被使用，而 Markdown 则保持可检查、可 grep、可由 Agent 编辑。

## 5. Phase 2：一个被严格限权的内部 Agent 重写全局 Memory 工作区

Phase 2 不是普通 summarizer 函数，而是 Codex 自己启动的 `MemoryConsolidation` 内部 Agent。流程如下：

```text
领取全局 singleton job + lease
→ 确保 ~/.codex/memories 是带基线的 Git workspace
→ 从 memories DB 选 top-N Stage 1 outputs
→ 同步 raw_memories.md 与 rollout_summaries/*.md
→ 与上次成功基线做 bounded Git diff
→ 启动内部 consolidation Agent
→ Agent 阅读 diff、旧 MEMORY、旧 summary、新/删 rollout summaries
→ 增量更新 MEMORY.md / memory_summary.md / skills/
→ 验证工件
→ 重置 Git baseline
→ 原子更新 job watermark 与 selected snapshot flags
```

[Phase 2 主流程](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L47-L212)

### 5.1 选择策略形成了显式使用反馈环

Phase 2 先按以下优先级选择最多 256 个候选：

```text
usage_count DESC
→ last_usage 或 source_updated_at DESC
→ source_updated_at DESC
→ thread_id DESC
```

候选若曾被使用，以 `last_usage` 判断 30 天新鲜度；从未使用则看 source 时间。选中集合在 job 成功时作为 snapshot 一次性写回 `selected_for_phase2` flags。[选择查询](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L431-L525)、[selection snapshot 提交](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L1239-L1295)

Memory 被后续回答引用时，citation 中的 rollout IDs 会使对应 Stage 1 row 的 `usage_count` 加一并刷新 `last_usage`。使用过的 Memory 因而更可能继续进入全局巩固。[usage 回写](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L51-L86)

这是一个简单、可观察的 reinforcement loop，不是 learned retriever。它也可能形成曝光偏差：先进入 summary、较容易被找到和正确引用的内容获得更多保留信号；相关但未被 cite 的内容可能逐渐退出 top-N。当前代码记录了使用次数，却没有 counterfactual exposure 或“被搜到但未采用”的对照。

### 5.2 巩固 Agent 的权限边界比普通主 Agent 窄

巩固 Agent：

- cwd 被重定向到 Memory root；
-自身标记 ephemeral，禁用再次生成或读取 Memory，避免递归；
-没有 MCP servers、Apps、Plugins 或协作/子 Agent；
-approval policy 固定为 Never；
-在 managed sandbox 下只允许写 Memory root、禁止网络；
-完成期间用 heartbeat 维持全局 lease；丢失 ownership 后不允许提交新 baseline。

[受限 Agent 配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L308-L367)、[完成与 ownership 检查](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs#L378-L485)

Memory workspace 还拒绝根目录 symlink，递归清除其中的 symlink，并在完成时验证 `MEMORY.md` 是普通文件、`memory_summary.md` 首行恰好为 `v1`。Git baseline reset 前会删除临时 diff，避免删除内容残留在 prompt 工件或不可达 Git objects 中。[workspace 安全与验证](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/workspace.rs#L10-L114)

### 5.3 操作可靠性强于语义可靠性

lease、heartbeat、watermark、sandbox、symlink 拒绝、artifact check 和 Git baseline 都是确定性代码；但 Phase 2 的“合并哪些偏好、怎样处理冲突、是否删除旧结论”由自由文本 prompt 驱动。最终 validator 只证明两个文件存在、summary 版本头正确和没有 symlink，不验证：

-每条结论是否仍有当前 rollout 支持；
-项目 scope 是否正确；
-同一事实是否被重复合并；
-冲突是否被保留；
-删除 note 是否清掉所有派生描述；
-`MEMORY.md` 与 `memory_summary.md` 是否语义一致。

因此这套系统具备较成熟的后台 job 与文件安全控制，但 Memory 内容本身仍是一份由 Agent 维护的生成式文档。

## 6. 读取链：2500-token 常驻摘要 + 词法搜索 + 渐进披露

当 `MemoryTool` 和 `use_memories` 同时开启时，Memory extension 会读取全局 `memory_summary.md`，最多保留 2500 tokens，并作为 developer-policy fragment 注入线程。若 summary 不存在或为空，则不注入。[prompt contributor](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/extension.rs#L22-L76)、[summary 注入](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/prompts.rs#L23-L50)

形成如下三层访问：

```text
L0  memory_summary.md
    每个启用线程常驻，承担用户画像、全局偏好和检索路由

L1  MEMORY.md
    按 cwd / 项目 / 任务族组织的持久手册；按关键词查询

L2  rollout_summaries/、skills/ 与 rollout_path
    只在 L1 指向它们且需要精确步骤、错误文本或证据时打开
```

### 6.1 本地读取没有 embedding 或 ANN

当前 `LocalMemoriesBackend` 提供 list、read、search 和 add-ad-hoc-note 四个操作；search 是对子目录中普通文本文件做递归 substring scan，支持：

-任一 query 命中；
-所有 query 同行；
-所有 query 在指定行窗口内；
-大小写开关；
-去除非字母数字字符的 normalized 比较；
-上下文行和分页。

它按 path 与行号排序，不计算语义相似度、向量距离或学习得分。[backend contract](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/backend.rs#L6-L133)、[词法搜索实现](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local/search.rs#L17-L88)

这使检索便宜、可解释、易于引用，也把 recall 质量转移给 Phase 2 的标题、关键词、task group 和 summary 写法。若巩固 Agent 把用户原词改成过度抽象标签，后续 substring search 可能找不到，即使事实仍在文件中。

### 6.2 Dedicated tool 不是唯一读取路径

`dedicated_tools=false` 时，Memory extension 仍注入 read-path instructions，并把 Memory root 加为 primary Agent 的只读 helper root；Agent 可以按指令用 shell/grep 打开 Memory。`dedicated_tools=true` 时才注册 `memories.list/read/search/add_ad_hoc_note` 工具。普通 Agent 没有对 Memory root 的通用写权限；显式更新只能走受限 note surface 或后台 consolidation。[只读 root 配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/core/src/config/mod.rs#L3997-L4014)

路径实现拒绝 `..`、绝对路径、Windows prefix、隐藏组件和 symlink；递归搜索也跳过隐藏文件与 symlink。这防止 Memory 工具借相对路径逃出 `~/.codex/memories/`。[路径约束](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local.rs#L38-L88)

### 6.3 Citation 不只是展示，它参与生命周期

read-path prompt 要求：只要使用了 Memory，最终回答末尾就输出隐藏 citation block，包含实际文件行号和 rollout IDs。Codex 解析该块，把可见回答与 citation 分开，并用 IDs 更新 Stage 1 usage。[citation parser](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/read/src/citations.rs#L6-L50)

如果模型读了 Memory 却漏写 citation、引用了无效 thread ID，或者 shell 行为没有产生可解析 block，对应候选不会获得 usage reinforcement。生命周期正确性因此部分依赖模型遵守输出协议。

固定提交的 read-path prompt 还有一个值得注意的文字歧义：它在 `rollout_summaries/` 项下把“这些文件”描述成 append-only JSONL；实际 storage code 写的是 `.md` 摘要，真正的 JSONL 是摘要里 `rollout_path` 指向的原始会话。该措辞可能让 Agent 对应该打开摘要还是原 rollout 产生混淆。[read-path prompt](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/templates/memories/read_path.md)、[summary 文件写入](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/storage.rs#L110-L136)

## 7. 作用域：一个全局物理库，靠 cwd/branch 与文档结构做逻辑分区

本地 Memory root 固定为一个 `CODEX_HOME/memories`；Phase 2 也使用一个 global singleton consolidation job。不同项目并没有各自独立数据库或独立文件根。项目边界主要来自：

- thread metadata 的 `cwd`、`git_branch`、`git_sha`、origin 和 project id；
- rollout summary 头部的 cwd/branch；
- Phase 2 prompt 要求按 cwd / project scope 建立 `MEMORY.md` task groups；
- `memory_summary.md` 中按 scope 建立检索索引；
-主 Agent 在读取时根据当前任务自行选择相关块。

这是一种**全局存储、逻辑路由**架构，而不是硬 namespace。优点是跨仓库的稳定用户偏好和工具经验可以复用；边界是所有 memory-enabled 根线程都会先接收同一个全局 `memory_summary.md`，再由模型判断哪些 scope 相关。当前代码没有在文件读取层按 current cwd 做强过滤。

公开 issue #18343 正在请求 global/project/hybrid/thread-only 等显式 scope 与清理能力；它是用户需求证据，不是已证明的数据泄漏事件。[scope feature request](https://github.com/openai/codex/issues/18343)

Worktree 也不是单独 Memory namespace。不同 worktree 的 cwd、branch 和 commit 可以随 rollout 保存，但最终仍汇入全局文档；若 Phase 2 合并时丢掉 branch/commit 条件，旧分支经验可能被另一个 worktree 误用。

## 8. Subagent、Guardian、Goal 与 Compaction 的关系

### 8.1 Subagent 自己不触发 Memory Writer

startup code 对 `source.is_non_root_agent()` 直接返回，所以 subagent 自己的 rollout 不会作为独立 Phase 1 candidate。另一方面，Phase 1 会保留 root rollout 中的 `InterAgentCommunication` item；因此子 Agent 回传给主线程的消息仍可能通过主线程被记住。

这形成一种非对称边界：

```text
subagent private trace ──×──> 独立长期 Memory
subagent → main 的通信 ─────> 可能进入 main rollout 的 Memory
```

它减少了子线程日志直接污染全局 Memory，但也使“子 Agent 发现了什么”取决于主线程实际收到和保存了哪些通信。当前源码未提供多 Agent evidence independence 或冲突仲裁层。

### 8.2 Guardian 明确关闭 Memory

Guardian review session 会关闭 `use_memories` 和 dedicated memory tools，并使用只读权限交集。这使审批/复核判断不被个人历史 Memory 直接影响，是一种明确的 reviewer independence 边界。[Guardian 配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/core/src/guardian/review_session.rs#L1380-L1410)

### 8.3 Goal 与 Compaction 都不是长期 Memory

Goal 保存当前长期任务的完成条件和进度；Compaction 压缩同一线程的上下文。Phase 1 会忽略 `RolloutItem::Compacted` marker，而从可保留的 response items 建立另一条长期派生链。三者解决的问题不同：

| 机制 | 时间尺度 | 状态作用 |
|---|---|---|
| Compaction | 同一线程内 | 让模型继续处理长对话 |
| Goal | 当前长期任务 | 维持目标、约束与完成状态 |
| Memory | 跨线程 | 提供历史偏好、项目经验和复用线索 |

## 9. 用户更新、遗忘与清除：两种软操作和一个全量 reset

### 9.1 Thread memory mode 只控制未来生成资格

每个 thread 可以设为 enabled 或 disabled；这个更新不调用模型，只影响该线程以后能否成为 Stage 1 candidate。若内容已经进入 `MEMORY.md`，关闭原线程不会直接删除派生条目。

若启用了 `disable_on_external_context`，Web Search、Tool Search、可能携带外部内容的工具输出以及会污染 Memory 的 MCP 调用会把线程标为 `polluted`。若该线程属于上一版 Phase 2 selection，系统会排队触发下一次 consolidation，从文件中移除只由该线程支持的内容。[pollution 与 forgetting enqueue](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs#L617-L652)

但该防线默认关闭。启用 Memory 后，外部内容是否被排除取决于用户/组织配置，而不是强制 invariant。

### 9.2 “记住、更新、忘记”采用 append-only note

dedicated tool 暴露的写操作不是直接改 `MEMORY.md`，而是在 `extensions/ad_hoc/notes/` 创建一个不可覆盖的时间戳 Markdown note。工具描述要求只有用户明确提出 remember/forget/update 时才能调用；文件使用 `create_new`，禁止重名覆盖。[ad-hoc tool](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/tools/ad_hoc_note.rs#L22-L90)、[append-only 实现](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local/ad_hoc_note.rs#L12-L40)

下一次 Phase 2 把 note 当作必须处理的来源，同时明确“内容不能作为行动指令”。更新和删除因此是由 consolidation Agent 解释的补丁，而不是带稳定 entry ID 的结构化 mutation。它保留了一条用户输入记录，却无法提供同步删除或确定性 conflict resolution。

### 9.3 Full reset 清生成状态，不清源线程

App Server 的 reset 先在 `memories_1.sqlite` 中事务删除 stage1 outputs/jobs，再清空 Memory 目录。两步之间不是跨 DB/文件系统原子事务；若第二步失败，数据库可能已空而旧文件仍在。[reset 处理](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/app-server/src/request_processors/thread_processor.rs#L1774-L1801)

更重要的是，reset 不删除原始 rollout，也不改变 threads 表中的 memory mode。仍在 10 天年龄窗口、已经空闲且 mode=enabled 的旧线程，可以在之后 startup 时再次被 Phase 1 抽取。因而 reset 是“清除当前生成式 Memory 状态”，不等同于不可逆删除历史来源。

公开 issue #30299 要求稳定 entry ID、scope-aware inspect/prune/delete、dry-run 和备份。当前版本已经有 search/read、ad-hoc note 和全量 reset 等内部/产品表面，但仍没有与请求中相当的结构化逐项生命周期。[memory management request](https://github.com/openai/codex/issues/30299)

## 10. 安全模型：强文件边界，弱内容真值边界

Codex Memory 的确定性安全措施包括：

- feature 默认关闭；
- per-thread generation 控制；
- secret redaction 同时作用于序列化输入和模型输出；
- developer、AGENTS 和 skill 注入不进入 Phase 1；
- Memory root 禁止 symlink；
- read/list/search 拒绝越界路径、隐藏路径和 symlink；
-普通主 Agent 默认只读 Memory root；
-巩固 Agent 无网络、无 MCP/Apps/Plugins、不能递归 delegate；
-Phase 2 用 ownership token、lease、heartbeat 和 snapshot flag 防止过期 worker 提交；
-citation 保留文件行和 rollout provenance。

但内容层仍有四个弱点：

1. tool output 与用户历史可以包含提示注入，Phase 1 主要依赖 system prompt 把它们当数据；
2. secret redaction 是模式检测，不构成“所有敏感项目事实都不会进入 summary”的证明；
3.全局 summary 会跨项目注入，scope 主要靠文本路由；
4. Phase 2 的语义合并没有独立 verifier，artifact check 也不检查事实支持。

所以“路径逃逸”和“错误记忆”属于不同安全层：前者有较多代码级 invariant，后者仍主要依赖模型判断、来源提示和之后的用户纠正。

独立的 `Bad Memory` 预印本在合成 sandbox 中测试了 Claude Code 与 OpenAI Codex，作者报告：让不可信外部内容直接改写 Memory 并不容易，但一旦恶意 payload 已经存在于持久 Memory 文件中，它可以影响当前和后续 session；成功率随系统、模型和多 session 序列变化。它不能代表真实部署发生率，也没有对本固定提交的每一条防线做归因，但为“写入防护不等于读取安全”提供了独立反证。[Bad Memory](https://arxiv.org/abs/2607.14611)

## 11. 并发、恢复与当前问题报告

### 11.1 已有的并发控制

- Phase 1 每个 thread/job 使用 ownership token、lease、retry 和 source watermark；
- Phase 2 使用一个 global job、六小时成功 cooldown、心跳和 stale-lease takeover；
- Phase 2 成功时，在一个 memories DB transaction 中同时更新 global job 和 exact selection flags；
- Memory 文件以 Git baseline 表达上次成功状态，失败后的下一次 run 能看到未提交 diff；
-巩固 Agent 关闭前等待最多十秒，避免线程仍运行时释放 job。

### 11.2 仍存在的窗口

`get_phase2_input_selection` 使用多个 `LIMIT/OFFSET` 查询分页，再逐项回查 thread metadata，没有把完整选择过程包在单一 SQLite read transaction。公开 issue #26684 提出了并发 Stage 1 insert 使 OFFSET 漂移、导致候选遗漏或重复的可复现实验；当前固定提交仍保留该多查询形状，因此这个风险没有被代码结构本身排除。[issue #26684](https://github.com/openai/codex/issues/26684)

文件层也不是事务式写入：consolidation Agent 可以在失败前部分修改 `MEMORY.md` 或 skills；只有完成后才验证并重置 baseline。下一轮有机会通过 diff 修复，但读线程是否可能在中间窗口看到部分工件，当前报告没有找到明确的 reader/writer snapshot 协议。

### 11.3 Issue 是运行线索，不是已复现事实

当前官方仓库中还存在用户报告：

- 0.149.0 的 background Memory worker 可能重复提交后续 turn 并消耗额度；[issue #40110](https://github.com/openai/codex/issues/40110)
- Phase 2 global job 可能停在 pending，无法由新 root session 认领；[issue #37097](https://github.com/openai/codex/issues/37097)
- custom provider 仍可能继承 OpenAI 的 Luna/Terra model IDs；[issue #39272](https://github.com/openai/codex/issues/39272)

本次没有在本机执行 Memory pipeline，也没有独立复现这些 issue。它们只用于说明真实用户碰到的故障表面以及应检查的代码路径，不能当作发生率或当前所有平台均受影响的证明。

## 12. 与常见 Agent Memory 架构相比，Codex 的实质差异

| 维度 | Codex 当前形状 | 常见外部 Memory 服务 |
|---|---|---|
| 原始来源 | 本地 rollout JSONL + thread DB | 宿主主动提交消息/事件 |
| 写入触发 | 后续 root turn 启动时异步回收旧线程 | 每 turn、session end 或 API `add` |
| 形成 | 两阶段 LLM：逐 rollout 抽取 + 全局 Agent 巩固 | 单次事实抽取、摘要或 graph construction |
| 权威候选层 | `memories_1.sqlite` | SQL/vector/graph records |
| 最终可读层 | Markdown handbook、summary、skills | API records / embeddings / graph nodes |
| 读取 | prompt 常驻 index + agent-controlled substring search | ANN/BM25/hybrid/rerank |
| scope | 全局物理根 + cwd/project 文本组织 | user/agent/run/tenant namespace |
| 更新 | 新 rollout、usage/recency、ad-hoc notes、全局重写 | item CRUD、version/supersede/conflict |
| provenance | rollout path、thread ID、行级 citation | source IDs、record history、edges |
|执行边界 | Memory 只提供上下文；当前 sandbox/approval 仍控制行动 | 取决于宿主 Agent |

Codex 的设计更像“由 Agent 维护的本地个人操作手册”，而不是共享事实数据库。它适合保存用户工作方式、仓库导航、复用流程和失败屏障；对精确多写者冲突、强项目隔离、同步 CRUD 或结构化 temporal state 的支持较弱。

## 13. 最新演进说明了什么

从 2026-05-26 到本快照，固定仓库的 Memory 相关路径有 93 个提交；这只是活动计数，不证明质量。代码变化集中在：

- Memory state 独立 SQLite DB；
- dedicated tool 与 read extension；
- provider-aware model defaults；
- citation/usage feedback；
- paginated thread 兼容；
- external agent memory import；
- Phase 2 sandbox、workspace roots、artifact validation 与 shutdown；
- symlink/path hardening；
- detached Memory request 与 thread source 标识。

最近稳定 release `0.149.0` 发布于 2026-08-20；本报告的 `main` 快照晚三天。两者之间 Memory 相关差异很小，主要是 detached Memory request 的标记和 extension prompt fragment 的类型要求，而不是整条架构重写。

`ExternalAgentMemoryImport` 已在源码中出现，但仍标为 UnderDevelopment、默认关闭。它把来自其他 Agent 的项目记忆作为带 cwd scope 的来源材料导入，再由同一个 Phase 2 体系巩固；这说明 Codex 正在把 Memory 从单一客户端历史扩展到跨 Agent 迁移，同时仍避免把导入内容当作权威行动指令。

## 14. 成熟度判断

### 较成熟的部分

- 线程与 job 的持久化、watermark、lease、retry 和 selection snapshot；
- Memory root 的只读/受限写边界；
- progressive disclosure 与行级 citation；
- secret redaction、symlink/path hardening；
- Phase 2 内部 Agent 的网络和扩展隔离；
-细粒度配置、测试和 telemetry surface。

### 中等成熟的部分

- 两阶段形成和增量 consolidation；
- usage/recency 驱动的全局保留；
- cwd/project 文本化 scope；
- ad-hoc note 驱动的更新/忘记；
-跨 CLI/App/IDE 的本地 store 复用。

### 仍早期或证据不足的部分

- Memory 内容的事实正确性、去重、冲突和时态更新；
-逐项目硬隔离和跨 worktree revision 语义；
- item-level inspect/update/delete 与可验证派生删除；
-并发 selection 与文件读取的一致性；
- custom provider 的端到端可移植性；
- Memory 对 Coding Agent 成功率、工具调用数和用户纠正次数的独立测量；
- cloud/web 与本地 Memory 的完整同步边界。

## 15. 当前最重要的未解决问题

1. **Scope 是否应从文档约定升级为数据面约束。** 当前一个全局 summary 服务所有项目；还没有 project/worktree-specific physical view 与显式 precedence。
2. **生成式巩固怎样获得可验证语义。** Git diff 和 artifact check 能验证操作完成，却不能证明删对、合并对或没有把推断升级成事实。
3. **使用反馈怎样避免自强化。** citation 驱动的 usage ranking 保留常用内容，但缺少曝光偏差和遗漏反馈。
4. **一次 forget 如何穿过所有派生层。** thread disable、polluted、ad-hoc note、prune 和 full reset 是不同操作，尚未形成稳定 object ID 与 deletion receipt。
5. **并发生成和读取是否共享一致快照。** DB selection、Agent 文件写入与新线程读取跨越多个事务边界。
6. **怎样公平评价这种“LLM 写、词法读”的架构。** 需要同时测高信号形成率、跨项目误用、检索步骤、citation 完整性、更新/遗忘正确性、后台成本与最终工具行动，而不是只测 QA recall。

## 16. 证据与限制

本报告的工程结论来自 `openai/codex` 固定提交、当前 release metadata、OpenAI Docs 和少量官方 GitHub issue。没有运行第三方或 Codex Memory pipeline，没有访问用户实际 Memory 文件，也没有用 stars、issue 数或 README 描述替代正确性/采用证明。

源码可以证明组件、默认配置、控制流和静态失败窗口存在；它不能证明托管客户端一定使用相同配置、所有 feature flag 对所有账户开放、模型生成质量、真实故障率或完整云端实现。Issue 是问题报告，只有与固定代码结构直接吻合时才用于限定判断。

返回场景视图：[Coding Agent 与项目记忆](../scenarios/02-coding-agents.md)。返回机制入口：[写入与形成](../mechanisms/02-write-and-formation.md)、[生命周期与演化](../mechanisms/04-lifecycle-and-evolution.md)、[检索与上下文](../mechanisms/05-retrieval-and-context.md)。
