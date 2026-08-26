# 第 5 层：读取与上下文

这一层的总纲是：**每一种 Memory 怎样进入当前上下文；如果需要检索，实际采用什么检索方式。** 直接注入、索引导航、Agent 工具搜索和系统自动召回不是互斥架构，而是不同 Memory 对象各自的进入路径。每条路径都要能回答四件事：进入方式、检索方式、输出形态、上下文位置。

## 5.1 TencentDB：L3 直注、L2 导航→正文、L1/L0 工具检索与 Skill/Knowledge 路径

[TencentDB Agent Memory `0aff21a`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a)没有一个统一的跨资产 retriever。Session 初始化先按身份、绑定和资产状态得到可见目录；Memory、Skill、Wiki、CodeGraph 再分别装配。最终由同一个主 Agent 根据当前任务组合零种、一种或多种资产。

### L3：`persona.md` 直接进入稳定 System Context

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | 新 Session 初始化时由 Memory Injector 读取 |
| 检索方式 | 无；不做 query-time search |
| 输出形态 | `persona.md` 的跨场景准则全文，附 L2 导航 |
| 上下文位置 | System Prompt 的稳定部分；`session_init` 结果可缓存 |

L3 的设计是假定内容已经足够短、足够通用，所以每个新 Session 都先看到。例如“缺陷修复先建立失败证据；纯重构先建立行为基线”会直接约束默认判断。刚更新的 Persona 不一定改变已经运行中的 Session；验证新内容要开启新 Session。

### L2：Scene 索引先进入，正文按 path 展开

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | Session 初始化注入 Scene path/summary/heat/updated 导航 |
| 检索方式 | Agent 根据当前任务匹配摘要，再调用 scene read 工具按 path 读取 |
| 输出形态 | 先是轻量索引；命中后是单个 Scene Markdown 全文 |
| 上下文位置 | 索引在稳定 System Context；正文作为本轮动态工具结果 |

例如索引出现 `scene_blocks/缺陷修复与回归验证.md — 复现、最小修改与回归`。用户要求修复 bug 时，Agent 才读取该文件，得到适用条件、SOP、判断逻辑和反模式。所有 Scene 正文不会一次塞进 Prompt。

### L1：Atomic Memory 通过工具做 lexical/vector/hybrid 检索

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | Agent 遇到历史约定、偏好或原子事实时调用 `atomic/search` |
| 检索方式 | SQLite 路径并行 FTS5/BM25 与可选 embedding，再用 RRF 融合；另一后端可提供 dense+sparse hybrid |
| 输出形态 | 带 type、content、score、scope、时间/来源的原子片段 |
| 上下文位置 | 当前 turn 的动态工具结果，受 limit、threshold 与字符预算约束 |

未配置 embedding 时 BM25 仍可用；“工具检索”并不等于“后端没有向量”。当前 MemoryProxy 生产路径不再每轮自动塞入 L1，而是把只读 Memory 工具说明交给 Agent，自主决定 query。MemoryCore/OpenClaw 的另一适配路径可以在 `before_prompt_build` 自动执行 L1 search；它是可选适配，不是所有部署的默认行为。

### L0：Conversation 工具回到消息和时间线

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | 需要核对原话、时间顺序或某次 Session 时调用 conversation 工具 |
| 检索方式 | `conversation/search` 关键词检索；`conversation/query` 按 session/顺序读取 |
| 输出形态 | 原始 user/assistant 消息、时间与 Session 定位 |
| 上下文位置 | 当前 turn 的证据片段，不常驻 |

L1 是抽取后的原子结论，L0 是更接近原话的证据。用户问“我当时究竟怎么说的”时，命中 L1 后仍可继续查 L0，而不是把抽取文本当作逐字原话。

### Skill：目录先可见，`SKILL.md` 与 supporting files 按需加载

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | Session 初始化用 Agent/Task 描述和目标预筛 owned active Skill，注入 `available_skills` 目录 |
| 检索方式 | 先匹配 name/description；命中后 `skill_view`，需要资源再 `skill_files_read`；目录不足时 `skill_search` 团队库 |
| 输出形态 | 目录项 → 完整 `SKILL.md` → scripts/templates 等文件 |
| 上下文位置 | 目录在稳定 System Context；正文和资源作为动态读取结果 |

Skill search 的 score 只用于找候选；是否适用仍由 Agent 阅读 When to use、Required inputs、Decision rules 与 Validation 后判断。active head 更新后，已运行 Session 的缓存目录也可能仍旧。

### Wiki：资源入口 → BM25 search → 页面正文

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | Knowledge Injector 注入已绑定 Wiki 的名称、ID、摘要、服务地址与 `tools/list → tools/call` 说明 |
| 检索方式 | 默认 `search` 使用 FTS5/BM25；命中后 `read_page`；目录/关系需求再用 `list_pages`、`get_graph` |
| 输出形态 | title/snippet/related/links → 少量 Markdown 页面全文 |
| 上下文位置 | 资源目录与工具协议在稳定区；命中与页面正文进入动态工具结果 |

标准 Agent search 默认 `hop=0`，不会因为 Wiki 有 Wikilink graph 就自动多跳扩展。图边主要帮助解释页面关系或在显式请求时扩展。

### CodeGraph：资源入口 → 意图对应的代码/关系工具

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | Knowledge Injector 注入 CodeGraph 名称、ID、摘要、commit/status 与工具协议 |
| 检索方式 | 理解功能用 `explore`；找定义用 `search/node`；查上下游用 `callers/callees`；改动影响用 `impact` |
| 输出形态 | 文件/符号位置、必要源码、调用边或影响集合 |
| 上下文位置 | 资源目录在稳定区；查询结果进入本轮动态上下文 |

`search` 主要按名称/类型找节点，并非图遍历；`callers/callees/impact` 才沿预建边查询。索引明显落后或即将修改代码时，Agent 仍需读取当前 workspace source。

### 一个任务如何组合六条路径

用户说：“按上次约定修复 refresh token 撤销问题，解释设计原因，并确认改动影响。”同一轮可能这样装配：

```text
L3 Persona：直接提供“先建立验证证据”的长期准则
L1/L0：找回“共享 revocation store”的历史约定与原话
L2：读取缺陷修复与回归场景
Skill：读取 token-revocation workflow 与验证步骤
Wiki：搜索为何选择共享 Store 的设计页
CodeGraph：explore 实现，再用 impact 查影响范围
```

这些内容以稳定全文/目录、动态片段和工具结果分区进入上下文；仓库没有一个独立分类器保证四种资产只选其一。各资产的固定实现入口位于 [MemoryCore](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a/MemoryCore)与 [MemoryKnowledge](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a/MemoryKnowledge)。

## 5.2 Codex：`memory_summary` 直注、`MEMORY.md` 词法 search/read 与逐层读取

[Codex `c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)的长期读取是“短索引常驻 + 普通文件词法搜索 + 来源指针下钻”。固定实现没有 embedding、ANN 或 learned reranker。

### `memory_summary.md`：新 Thread 的直接入口

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | `use_memories` 启用时，扩展在新 Thread 读取一个固定快照 |
| 检索方式 | 无；最多约 2500 tokens 的 summary 直接加载 |
| 输出形态 | 首行 `v1` 的密集短索引：用户偏好、项目/任务族与搜索路由 |
| 上下文位置 | developer-policy fragment；每个启用 Thread 的稳定入口 |

它应该告诉 Agent“去哪里找”，而不是塞满全部细节。若 summary 没保留项目名、别名或错误关键词，后面的文件 search 会更难定位相关块。

### `MEMORY.md`：Agent 自主做文件/词法搜索

| 必答项 | 实际路径 |
|---|---|
| 进入方式 | summary 指向相关 task group 后，Agent 主动 search/grep 再 read 行范围 |
| 检索方式 | 对 Memory root 普通文本做递归 substring scan；支持 any/all terms、行窗口、大小写/规范化和分页 |
| 输出形态 | 文件路径、行号、命中行与上下文窗口 |
| 上下文位置 | 当前 turn 的动态文件片段 |

启用 dedicated tools 时使用 `memories.list/read/search`；否则主 Agent 按只读指令使用普通文件工具。两条接入都读取同一套 Markdown，不是两种检索语义。

```text
query: ["auth-service", "token", "revocation"]
→ MEMORY.md:18-27
  生产/多实例使用共享 revocation store
  本地 Map 仅限单实例测试
  Sources: th-42, th-51
```

这是代码搜索式命中：没有语义距离。Agent 可以改写关键词、多次搜索和扩大行窗口，但搜索质量仍取决于 Phase 2 的标题与用词。

### Skills、rollout summaries 与 raw rollout：按来源逐层展开

| Memory 类型 | 进入方式 | 检索方式 | 输出形态 | 上下文位置 |
|---|---|---|---|---|
| `skills/` | `MEMORY.md` 或目录提示相关 Skill | list/read，沿 Skill 路径读 `SKILL.md` 与配套文件 | 流程、模板、示例 | 动态按需片段 |
| `rollout_summaries/*.md` | Memory block 的 source/slug 指向任务摘要 | 按文件名/关键词 search/read | 单任务结果、cwd/branch、`rollout_path` | 更深一层证据 |
| rollout JSONL | 需要精确命令、错误或原话时沿 `rollout_path` | 普通文件搜索与范围读取 | 原始消息和工具事件 | 最深层、临时证据 |

例如新 Thread 在 `/repo/auth-service` 收到“按以前验证过的方式改 refresh token”：

```text
memory_summary：定位 auth-service / token revocation
→ search MEMORY.md：找到共享 Store 与测试命令
→ read 对应行：取得当前手册和 th-42/th-51
→ 必要时读 rollout summary：确认历史验证结果
→ 仍有歧义才沿 rollout_path 查看原始 JSONL
```

最终进入推理的是被选中的文件片段，与当前 Thread 的 user message 和新 tool results 一起组成上下文；整本手册和原始历史不会一次性注入。回答采用 Memory 时附带文件行与 rollout IDs，citation 将在第 6 层形成 usage 反馈。固定读取接口见 [extension.rs](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/extension.rs)、[backend.rs](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/backend.rs)与 [local search](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local/search.rs)。

## 5.3 MemFlow：意图路由、检索层级与动态预算

[MemFlow](https://arxiv.org/abs/2605.03312)针对小模型难以自行选择工具、检索深度和预算的问题，把 memory planning 从 Answer Agent 外置。它不是新增一种索引，而是明确选择哪条读取路径。

```text
query + session/task
→ Router Agent 判断 intent
→ Memory Agent 执行对应 tier
   1. Profile Lookup
   2. Targeted Retrieval
   3. Deep Reasoning
→ 按 tier 动态分配 token budget，编译证据
→ Answer Agent 只看紧凑 context
→ Validator 检查答案是否受证据支持
   └─ 不足时升级到更重 tier 重试
```

Profile Lookup 适合直接用户属性；Targeted Retrieval 处理可定位事实；Deep Reasoning 才承担跨片段、多跳或更大预算的查询。比如“我常用哪个编辑器”可以直接 lookup；“上次项目延期由哪两次变更共同造成”会进入 deep route。输出不只是 top-k，而是一份带路由层级和预算的证据上下文；Validator 决定停止还是升级。

论文在冻结的 Qwen3-1.7B 上评测该 route-then-compile 结构。其关键机制是把“查什么、查多深、给多少上下文”变成显式、可复查的计划，而不是依赖小模型在开放工具循环中临场组织。

## 5.4 OpenViking：目录/URI 递归检索、L0/L1/L2 hydration 与检索轨迹

[OpenViking](https://github.com/volcengine/OpenViking)把 Resource、Memory 与 Skill 放入 `viking://` 虚拟文件系统。目录层级参与检索；URI 既是命名空间，也是从摘要回到原文的稳定指针。

```text
viking://resources/docs/auth/
├─ .abstract.md   L0：短摘要，用于快速召回
├─ .overview.md   L1：目录概览与导航
├─ oauth.md       L2：完整原文
└─ jwt.md         L2：完整原文
```

[官方检索文档](https://docs.openviking.ai/en/api/06-retrieval)区分 `find` 与 `search`：`find` 做直接查询；`search` 加入 session context、intent analysis 与 query expansion。核心路径是：

```text
query
→ intent analysis（search）
→ L0 vector/directory seeds
→ 在高相关目录递归检查子项
→ 用 L1 内容 rerank
→ 返回 URI、type、level、score、match_reason
→ overview/read 按 URI hydration 到 L1/L2
→ retrieval trajectory 记录展开路径
```

L0/L1 是目录级语义 sidecar，不是每个普通文件都有三份副本。Agent 可以先看 Abstract，相关时读 Overview，再只打开少量 L2 原文。比如查询“OAuth 授权码流程”，先命中 `viking://resources/docs/auth/`，L1 导航指出 `oauth.md`，最后才加载文件全文。

输出可以分为 memories/resources/skills 三类 MatchedContext，并保留 query plan 与详细 results。新版本的 context mode 还可以在 server 端按 token budget 做 tier filling：先给每类默认层级，再把剩余预算用于高分项的更深 hydration。这样“目录递归、内容层级、预算和轨迹”成为同一协议，而不是分散的 Prompt 习惯。

## 5.5 CICL：证据/行动感知的上下文选择与编排

[Decision-Aware Memory Cards / CICL](https://arxiv.org/abs/2606.08151)不再只问“哪段文字与 query 相似”，而问“哪段证据最可能改变 Agent 的下一步行动”。

```text
BM25 等基础 route 召回 files/tests/traces/rules/memories
→ 构建 instance context graph
→ 估计每个 candidate 的 decision-oriented utility
→ 选择会影响下一动作、能补足必要证据且负迁移较低的单元
→ 压缩成 typed Memory Cards
→ 将卡片交给 tool-using Agent
```

在一个代码缺陷任务中，两个文件都可能与错误信息高度相似：README 描述症状，测试文件却包含能决定修改位置的断言。传统相似度可能把 README 排前；CICL 会尝试评估“移除该单元后，下一动作是否会改变”，把测试与相关实现组成更高 utility 的卡片。卡片保留证据类型和压缩后的行动相关内容，不只是无来源摘要。

论文用 SWE-bench Verified 的文件检索与受控消融展示该协议，ranker 可以是 hosted LLM、local surrogate 或轻量模型。它提供的是可审计的 context-selection layer：基础检索仍负责候选覆盖，CICL 再决定哪些候选值得占用行动前的有限上下文。

第 5 层的输出到此为止：直接注入内容、索引、文件片段和工具结果已经进入当前推理。下一层观察这些 Memory/Skill 被怎样使用、任务结果如何回流，并由具体系统把反馈变成新的经验、技能或 Memory 策略。
