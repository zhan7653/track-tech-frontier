# 第 5 章　读取、检索与上下文：Agent 怎样找到并使用过去的经验

## 结论

读取层的任务是把当前问题与足够可靠的历史材料接起来，并在上下文预算内交给 Agent。它至少包含候选定位、原文展开、范围过滤、上下文编译和使用回执。检索分数高并不自动代表 Agent 得到正确上下文，更不能保证它会据此执行正确行动。

Codex 的成熟实现选择了一条很克制的路线：每个启用线程常驻一个短摘要；需要细节时，由 Agent 在 Markdown 工件中进行词法搜索、按行读取并继续打开来源摘要或原始 rollout。固定版本的本地读取没有 embedding、向量数据库或 ANN。它依靠目录、标题、关键词、行号和 Agent 的逐步搜索完成导航。

## 5.1 Codex 的真实读取链

固定快照 [`openai/codex@c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)将读取分成三层。启用 `MemoryTool` 且 `use_memories=true` 时，扩展读取全局 `memory_summary.md`，最多取 2,500 tokens，作为 developer-policy fragment 注入每个新线程；没有摘要时不注入。[summary 注入实现](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/extension.rs#L22-L76)

```text
新线程
  → L0：memory_summary.md（最多 2,500 tokens，常驻）
  → L1：按关键词搜索 MEMORY.md 或其他可读文件
  → L2：按行读取命中块，必要时打开 rollout_summaries/、skills/ 或原始 rollout
  → 使用内容时留下 citation
  → citation 回写来源 usage
```

| 层 | 内容 | 读取目的 | 失败时的影响 |
|---|---|---|---|
| L0 | `memory_summary.md` | 用户偏好、项目路由和高层索引 | Agent 起点缺少“去哪里找” |
| L1 | `MEMORY.md` 等 Markdown 手册 | 找到任务族、项目块和关键词 | 有事实但关键词不匹配时可能找不到 |
| L2 | rollout summaries、skills、原始 rollout | 核对步骤、失败信息和来源 | 信息多，读取成本也更高 |

这种分层让每次新线程只承担短摘要的 token 成本。细节按需读取，避免把所有历史塞入 prompt；代价是摘要的标题和路由文字必须写得好，Agent 也要实际执行搜索。

## 5.2 词法渐进读取怎样工作

`LocalMemoriesBackend` 暴露 `list`、`read`、`search` 和 `add-ad-hoc-note`。当 `dedicated_tools=false`（固定配置默认值）时，扩展提供读取指令并把 Memory root 作为主 Agent 的只读 helper root；Agent 可以用 shell/grep 按指令打开文件。只有设为 `dedicated_tools=true` 时，才注册 `memories.list/read/search/add_ad_hoc_note` 这组专用工具。[backend contract](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/backend.rs#L6-L133)、[工具与配置](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/config/src/types.rs#L288-L354)

本地 `search` 对 Memory root 下的文本文件递归做 substring scan。它支持任一词命中、所有词同一行命中、所有词在指定行窗口内命中、大小写选项、去掉非字母数字符号后的规范化比较、上下文行与分页。结果按路径和行号给出；代码没有计算 embedding 相似度、向量距离或学习到的排序分数。[词法搜索实现](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local/search.rs#L17-L88)

```text
当前任务：“退款集成测试为何仍然失败？”
  → L0 提示 payments / refund / integration-tests 这个任务族
  → search("refund", "fixture", line_window=8)
  → 命中 MEMORY.md:84-91
  → read 84-105，得到“旧 fixture 字段”的线索和 R-17
  → 若需要原始错误，打开 rollout_summaries/R-17.md
  → 若仍有歧义，再由摘要中的 rollout_path 打开原始 JSONL
```

这里没有“一个向量命中即为答案”的跳跃。Agent 会先看到短线索，再读局部正文，再决定是否回到更原始的证据。对于编码任务，这比把长日志一次拼进 prompt 更容易控制 token，也更容易向用户说明依据来自哪里。

## 5.3 路径和范围：读得到与该不该读是两件事

Memory root 在本地是一个全局目录。读取工具拒绝 `..`、绝对路径、Windows prefix、隐藏组件和 symlink；递归搜索也跳过隐藏文件与 symlink。普通 Agent 没有该目录的通用写权限。[路径约束](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories/src/local.rs#L38-L88)

这解决了路径逃逸和意外写入。项目范围使用另一种机制：rollout summary 记录 cwd、branch、commit 和项目线索，Phase 2 将这些线索组织进 `MEMORY.md` 与摘要索引；主 Agent 根据当前任务选择相关块。当前代码没有在读取 API 层按 cwd 进行硬过滤，因此不同项目共用同一个物理根和同一份常驻摘要。

| 问题 | 当前 Codex 控制 | 仍需 Agent 判断 |
|---|---|---|
| 能否越出 Memory 目录 | 路径校验、拒绝 symlink | 无 |
| 能否直接改写 Memory | helper root 只读，写操作受限 | 是否应提出更新请求 |
| 当前项目是否相关 | cwd/branch 作为文本和元数据线索 | 当前命中的项目块是否适用 |
| 旧分支经验是否仍有效 | rollout 有 branch/commit 可追溯 | 该经验能否迁移到当前分支 |

所以“全局摘要”提供跨项目的连续性，也会带来误用风险。一个与当前仓库无关的偏好或历史项目线索可能先进入模型输入，之后再依赖模型做文本范围判断。

## 5.4 citation：检索与后续保留连接在一起

当 Agent 在回答中采用了 Memory，读取提示要求它带隐藏 citation block，包含使用到的文件行和 rollout IDs。系统解析 citation，并将有效 ID 回写到候选账本的 `usage_count` 和 `last_usage`。这使读取结果不仅影响当前回答，也影响第 4 章中下一次 Phase 2 的 selection。[citation parser](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/read/src/citations.rs#L6-L50)

```text
search 命中 R-17
  → Agent 读到来源并把建议用于回答
  → citation 写入 R-17
  → usage 计数更新
  → R-17 在未来巩固中获得更高优先级
```

这条链的价值在于可追溯：系统能知道“哪次历史 rollout 被当作依据”。它的边界同样清楚：citation 缺失、ID 写错、Agent 虽读到却没有使用，都会让 usage 信号不完整；usage 也不能证明答案正确或用户满意。

## 5.5 为什么 Codex 当前不依赖 embedding

向量检索擅长用语义相近的表达召回材料，却增加 embedding 模型、索引构建、模型迁移、范围过滤和重建的一整套维护面。Codex 当前选择将“找什么”交给 Agent 的搜索动作，把稳定的文件系统、行号和词法匹配作为读取底座。这个选择带来三项可见性质：

- 成本和故障面较小：没有 embedding API、向量维度、ANN 索引或重建队列；
- 可解释性较强：命中路径、行号和文件内容可以直接展示；
- 召回很依赖写入质量：Phase 2 若没有保留用户原词、项目别名或具体错误文本，后来 substring search 可能找不到仍在文件里的信息。

这体现了 Codex 当前文件化、人工可读的 Memory 工作区形状。需要跨表达、跨语言和大规模对象检索的系统常会增加 dense、BM25、图或 rerank route；加入这些能力之后，还要负责索引与权威文本的版本一致性。

## 5.6 近半年补充：检索正在补足“当前版本、覆盖率和成本”

### MemTxn：先确定当前可见版本，再把它交给回答模型

2026 年 7 月的 [MemTxn](https://arxiv.org/abs/2607.27834)将 Temporal Resolver 放在回答模型外。当同一事实有相互冲突的版本时，Resolver 先选择应用可见版本；Ordered PatchTest 检查更新与来源的支持关系，snapshot journal 用于故障恢复。论文报告了其作者设置下的审计和恢复结果；成熟度仍是预印本原型。

它补的是检索前的一个常被忽略的问题：系统在开始排序前，哪一版事实有资格参与读取。Codex 的 Markdown 手册可以记录新旧经验，但本地词法搜索并没有可执行的 temporal resolver。若旧规则和新规则都含有相同关键词，最终依赖文件写法和 Agent 解释来选用。MemTxn 的代价是维护版本、来源收据和快照，回报是让“当前值”成为可检查的状态而非提示词习惯。

一个查询例子：

```text
查询：退款字段现在叫什么？

候选 A：refund_status
  valid_time: 2026-07-01 → 2026-08-23
  recorded_at: 2026-07-01

候选 B：refund_state
  valid_time: 2026-08-24 → open
  recorded_at: 2026-08-24

MemTxn 风格的读取：
  先用时间与来源规则选 B
  再把 B、来源 receipt 和冲突说明编译进上下文
```

Codex 当前词法读取可能同时命中 A 和 B，最终由 Markdown 顺序、标题和 Agent 判断处理。它能把两条记录的来源展开给模型，却没有一个独立的版本解析器先决定“当前值”。

### Omri 等：用分阶段测量检查读取真的省了多少

2026 年 6 月的 [Agent Memory: Characterization and System Implications](https://arxiv.org/abs/2606.06448)构建了按 construction、retrieval、generation 分摊成本的 profiling harness，并比较十类代表性系统。对读取层最直接的启发是：短摘要减少常驻上下文，并不等于端到端更便宜；它可能增加多轮 search、rerank、hydration 或模型推理。

Codex 的 lexical progressive read 属于可测的工程假设：L0 的 token 很小，具体问题可能要多次搜索和按行读取。应比较同一任务上的常驻 token、工具调用数、展开行数、回答延迟和最终行动，不能只比较“是否使用向量数据库”。论文提供测量框架，不能单独证明 Codex 的具体成本优势。

### LightMem 的独立复现：构造和 retriever 必须分开比较

2026 年 7 月的 [LightMem reproduction](https://arxiv.org/abs/2607.29104)在固定的 constructed store 上更换 retriever，作者报告回答准确率可由 58.1% 变为 75.5%；在其 matched retrieval-depth 对照中，raw-turn Naive RAG 常常更强，constructed memory 的优势主要出现在回答 token 预算很紧的情况。结果受作者数据、模型和实验协议限制，不构成所有系统的排序。

这项工作与 Codex 的关系很直接：优秀的写入摘要并不能免除检索设计，优秀的向量 route 也不能补回写入时丢掉的证据。报告一个检索方案时，至少应分开看原始证据是否仍在、候选是否召回、文本是否被编译进上下文、Agent 是否据此正确回答或行动。

## 5.7 当前边界

- `memory_summary.md` 是全局常驻索引，当前读取层没有按 cwd 的硬 namespace filter；
- 词法检索受关键词、拼写、语言和摘要措辞影响，跨表达召回能力有限；
- 一次 search 命中只说明文件中出现了词，不能证明该段对当前任务仍有效；
- 原始 rollout 可追溯，但自动 hydration 到何种深度仍由 Agent 自行决定；
- citation 提供使用线索，不能证明材料真实、完整、适用或被用户认可；
- Markdown 与原始 rollout 都存在时，系统没有通用的版本解析器来保证旧规则不会和新规则同时进入上下文。

对读者来说，最重要的观察点是完整读取链：当前问题如何触发搜索，命中如何展开，范围和版本如何判断，最后哪条历史真正进入回答。Codex 已将这条链做成可见的文件、行号和 citation；更复杂的检索系统需要在同样位置给出对象 ID、版本、过滤理由和展开收据，才能说明“找到了什么、为何使用它”。
