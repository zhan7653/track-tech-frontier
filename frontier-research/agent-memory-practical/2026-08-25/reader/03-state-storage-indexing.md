# 03 状态、存储与索引层：Memory 放在哪里，怎样被找到

## 结论

Memory 系统通常同时维护三类东西：原始证据、可调度的候选/版本状态，以及给 Agent 阅读的派生视图。把它们分开，系统才有机会回答“这条经验来自哪里”“它当前是否仍有效”“索引落后时能否重建”。

Codex 的答案很鲜明：原始 rollout 留在 JSONL；候选、job、lease、watermark 和使用统计放在 `memories_1.sqlite`；最终阅读材料是 `CODEX_HOME/memories` 下的 Markdown、rollout summaries 和 skills。读取优先使用约 2500 token 的 `memory_summary.md`，需要时用普通文本 substring search 搜索 `MEMORY.md` 等文件，再按行打开详情。公开固定代码中没有 embedding、ANN 或向量重排器。

```text
rollout JSONL ─────────────→ 原始证据
thread/state DB ───────────→ 候选发现与范围线索
memories_1.sqlite ─────────→ job、候选、watermark、usage
MEMORY.md / summaries / skills → Agent 可读的长期视图
```

这种设计把可读性、引用和低运维成本放在首位；检索质量更多取决于巩固 Agent 写出的标题、关键词和项目结构，而非向量相似度。

## Codex 的真实状态面

本章仍以 [`c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29) 为锚点。Codex 中容易混淆的状态并不都属于跨线程 Memory：当前 response items 和 compaction 服务于本线程；Goal 保存当前长期任务；`AGENTS.md` 和 checked-in docs 承担确定性规则；本地 Memory 才负责跨线程回忆偏好、项目经验和可复用流程。

| 状态面 | 主要载体 | 保存什么 | 在 Memory 中的角色 |
|---|---|---|---|
| 原始运行记录 | rollout JSONL | 消息、工具输入输出、执行过程 | 可回放证据 |
| 线程元数据 | `state_5.sqlite` | source、cwd、branch、commit、更新时间、mode | 候选发现和逻辑 scope 线索 |
| Memory 候选与调度 | `memories_1.sqlite` | Phase 1 输出、jobs、lease、watermark、usage | 形成层的权威账本 |
| 可读长期视图 | `CODEX_HOME/memories/` | `MEMORY.md`、`memory_summary.md`、summaries、skills | Agent 实际读取的内容 |
| 团队规则 | `AGENTS.md`、项目文档 | 必须稳定生效的约束 | 独立于生成式 Memory 的权威来源 |

`memories_1.sqlite` 的迁移文件是 `codex-rs/state/memory_migrations/0001_memories.sql`。其中 `stage1_outputs` 保存 thread ID、source watermark、raw/summary、slug、生成时间、usage_count、last_usage 和 selected 标记；`jobs` 保存 Phase 1/2 的状态、worker、ownership token、lease、retry、错误和输入/成功 watermark。这个数据库承担候选及其生命周期记录，供后台工作者协调；最终可读状态位于 Memory 文件工作区。

### 文件工件怎样组织

Phase 2 由 `storage.rs` 将选中的候选物化到 Memory root。典型目录形状如下：

```text
CODEX_HOME/memories/
  MEMORY.md                 # 详细长期手册
  memory_summary.md         # 短索引，首行版本为 v1
  raw_memories.md           # 多个 Phase 1 raw_memory 的工作材料
  rollout_summaries/        # 逐线程摘要，带 rollout_path
  skills/                   # 可复用的过程性材料
  extensions/ad_hoc/notes/  # 显式 remember/forget/update 请求
```

`raw_memories.md` 保存多个 `raw_memory` 字段的合并结果。真正原始的 JSONL 由逐线程摘要中的 `rollout_path` 指向。这条来源链让 Agent 可以从短摘要逐步打开详细手册、rollout summary，最后回到完整任务记录。

### 默认读取路径：先短摘要，再按需打开文件

当 `MemoryTool` 和 `use_memories` 都启用时，`codex-rs/ext/memories/src/extension.rs` 读取 `memory_summary.md`，最多注入约 2500 token 作为 developer-policy fragment。这个常驻摘要承担用户偏好、全局索引和项目路由；它不应承载每个细节。

后续读取有三层：

```text
L0  memory_summary.md
    每个启用线程的短索引

L1  MEMORY.md
    详细手册，按项目 / cwd / 任务组组织

L2  rollout_summaries/、skills/、rollout JSONL
    只有需要精确步骤、错误文本或来源时才继续打开
```

`LocalMemoriesBackend` 提供 list、read、search 和 add-ad-hoc-note。`local/search.rs` 的 search 是对普通文本做递归 substring scan：可做任一词命中、同一行 all-terms、行窗口 all-terms、大小写和规范化比较，并按 path 与行号返回上下文。它不计算 embedding、向量距离、ANN 邻居或 learned score。

以下是一次搜索的伪返回，展示它更像代码搜索而非语义召回：

```text
query: ["refund", "fixture"]

MEMORY.md:84
  Payments / refund integration tests
  - If the fixture schema changed, update the fixture before rerunning.
  Source: rollout T-1842

rollout_summaries/T-1842.md:12
  Failure: stale refund_status field in fixture.
```

用户可见结果是：当用户用“退款 fixture”这类项目原词提问时，Agent 容易命中；如果 Phase 2 把原词抽象成陌生的标签，substring search 可能找不到，即使相关事实仍在文件中。Codex 把这部分责任交给文档组织、关键词与 Agent 的分步搜索。

### Citation 也改变存储生命周期

read-path prompt 要求 Agent 使用 Memory 后在最终回答中附带隐藏 citation block，包含实际文件行号和 rollout IDs。`memories/read/src/citations.rs` 解析它，随后 state 层更新相应 Stage 1 候选的 usage。Citation 因而不只是展示出处：它把“被使用过”的信号回流到候选选择。

如果模型读了文件却漏掉 citation，或引用无效 thread ID，usage 信号就不会更新。这是一个清晰的接口边界：代码能解析格式，不能保证模型总能正确声明它使用了哪些 Memory。

## 从 Codex 抽出的通用存储架构

一个可审视的 Memory 存储层至少可以按下面四类对象描述：

| 对象 | 最少应有的信息 | 用途 |
|---|---|---|
| evidence event | 内容或位置、来源、时间、主体、hash/receipt | 回放与审计 |
| memory candidate / revision | 类型、scope、支持来源、状态、版本 | 控制何时成为当前知识 |
| derived index | 由哪个版本生成、索引类型、构建时间 | 检索与重建 |
| usage / decision record | 哪次检索、是否被引用、动作和结果 | 保留、评估与纠错 |

Codex 对这四类的取舍是：evidence 留在 rollout，candidate 和 usage 放 SQLite，详细可读 view 放文件，derived index 基本由文本标题、行号和目录结构承担。它没有为每个 Memory item 分配稳定的结构化 ID，也没有把 scope 做成物理数据库 namespace；项目边界主要来自 cwd/branch 元数据以及 Markdown 中的组织方式。

## 近期机制：从单一检索库转向多视图、可追溯状态

### LangGraph：namespace/key Store，向量索引是可选能力

固定提交的 [LangGraph Store](https://github.com/langchain-ai/langgraph/tree/f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f) 提供 `(namespace tuple, key)` 的 JSON object 存储，可 `get/search/put/delete/list namespaces`。其语义 index 默认关闭，只有显式配置 embedding 才启用；TTL 也默认关闭并要求 adapter 支持。它说明成熟框架并不把向量检索当作 Memory 的必需前提：先有明确 key、namespace 和对象操作，再选择是否为某些字段建语义索引。

对 Codex 的对照很直观。Codex 的逻辑 scope 是 cwd 和文档结构，方便本地阅读但缺少硬 namespace；LangGraph 的 namespace/key 更适合应用主动管理对象身份和隔离，但它不会自动从 Agent 轨迹抽取有用经验。二者处理的是同一层的不同问题。

### Caura：一份权威 row，多种派生检索面

固定提交的 [Caura](https://github.com/caura-ai/caura/tree/54dd6d4f2075ca428b1f3a5a8c50114351ea4755) 使用 Postgres、pgvector、FTS、Redis 和 worker。其 `memories` 主表把 tenant、fleet、agent、type、content、embedding、FTS、status、visibility、`supersedes` 和 timestamps 放在同一权威 row，后台再处理 enrichment、dedup 和 contradiction。它解决的是多租户、结构化 scope、状态筛选与 hybrid retrieval 的工程需求。

这是一种“数据库是权威，向量/全文/关系是可更新投影”的路线。它比 Codex 的文件化层次更强于过滤和服务端查询，也带来部署、schema 演化、异步索引滞后与多路径保证不一致的成本。仓库代码和测试表明它实现了这些组件，不代表独立生产效果。

### MAP-Graph：让 lineage 进入查询与行动边界

[MAP-Graph](https://arxiv.org/abs/2608.10509)（2026-08，预印本）提出 provenance-aware shared memory，将 provenance/lineage 纳入共享 Memory 的查询、权限和行动风险处理。它要解决的实际问题是：传统向量库可以找回相似文本，却难以判断这段知识是谁产生的、能否被当前主体使用、下游行动能否依赖它。

其新意不在“又加一个图数据库”，而在让来源边与对象关系成为决定可见性和风险的状态。Codex 目前有 rollout ID、路径和行级 citation，能支持回查；但读取时仍由 Agent 根据全局 summary 和文本 scope 自行判断相关性，尚没有 lineage 驱动的硬访问投影。MAP-Graph 是近期研究信号，尚非通用基础设施。

### Neo4j Labs Agent Memory：短期、长期和推理状态放进同一图服务（官方仓库，README 复核 2026-08-25）

[Neo4j Labs Agent Memory](https://github.com/neo4j-labs/agent-memory)提供了一个图原生工程对照。README 把状态分成 per-session conversation、长期实体/偏好/事实图和 reasoning traces/tool usage；访问面同时提供 vector + text search、entity resolution、deduplication、关系抽取和相似任务检索。它还提供 buffered writes、dedupe/consolidation primitives、multi-tenant `user_identifier`、MCP tools 和 `:TOUCHED` 审计边。

其主要数据流是：

```text
消息 / reasoning trace / tool usage
  → 多阶段实体与关系抽取
  → Neo4j 节点、边和审计关系
  → text + vector + graph 查询
  → context / similar task / reasoning reuse
  → buffered write、dedup、eval harness
```

它补充了 Codex 文件化状态中较弱的结构化实体、关系和跨语言 SDK。代价也很具体：需要 Neo4j 后端、embedding/LLM provider、实体解析和图维护；图中的边、摘要和向量如何同步删除仍需额外治理。仓库声明这是 Neo4j Labs 的 community-supported project，代码和 README足以说明工程形状，不能单独证明生产采用或通用性能。

## 为什么 Codex 没有默认 embedding 检索

Embedding 对同义表达、模糊问题和大规模候选召回有价值；它也需要 embedding 模型、重建策略、过滤条件、距离阈值、索引一致性和额外存储。Codex 当前选择把长期材料写成可 grep 的本地文件，并让 Agent 先从 2500-token 摘要定位，再做词法搜索和逐层打开。这样可以直接看到命中行、给出 citation，并避免维护一条始终同步的语义索引。

可以把两种路径并排理解：

| 问题 | Codex 当前路径 | 向量/混合路径常见回答 |
|---|---|---|
| 已知项目术语怎么找 | substring search + 目录/标题 | embedding 或 BM25 召回后过滤 |
| 如何解释命中 | 文件、行号、rollout ID | 需要额外保留 source span 与 rerank 解释 |
| 索引如何更新 | 编辑文本即可；无 ANN rebuild | 写新向量、删除旧向量、可能异步重建 |
| 跨措辞召回 | 依赖摘要和 Agent 改写 query | 通常更强，但可能召回语义近却 scope 错的内容 |
| 多租户/权限过滤 | 文本组织与 Agent 判断 | 需要在检索前/后把 scope 写入过滤器 |

近期方向把 embedding 放回 Memory 状态的派生视图中。无论用 substring、BM25、向量还是图，系统仍需说明该索引对应哪个版本、失效后如何重建、删除和权限变化怎样传播。

## 当前边界

- `memory_summary.md` 是全局物理摘要，所有启用线程先看到同一个短索引；文件读取层没有按 cwd/project 做强制过滤。
- SQLite 与文件系统之间没有跨介质原子提交；数据库已更新而文件更新失败，或相反，仍可能留下恢复工作。
- 词法检索便宜、透明，但对同义改写和不良标题敏感。
- rollout ID 与 citation 支持来源追溯，但候选/Memory 条目没有统一的稳定对象 ID、版本图和级联删除回执。
- 更结构化的 namespace、hybrid index 和 provenance graph 已有活跃仓库或近期论文，但它们增加的复杂度、延迟和治理成本尚不能被“检索更聪明”一句话抵消。

下一章将处理状态随时间怎样更新、冲突、失效、撤销和遗忘。
