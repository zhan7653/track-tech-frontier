# 检索工程 walkthrough：六种实现怎样把查询变成上下文

下面不按项目写简介，而是沿同一条读取链比较固定版本实现：权威状态在哪里、有哪些候选 route、怎样融合、什么时候回填原文、怎样暴露失败。v09 的仓库检查读取了固定 commit 的 README、tree 和关键代码/manifest，但没有运行这些仓库；因此这里能重建公开代码的数据流，不能声称真实性能或生产采用。

## 1. Causal Memory：BM25、语义和因果边怎样汇合

固定版本 `054af36507537f7b616fa41db07be483cc6e55c3` 的 `causal-memory` 将原始 session log、atomic fact 和 decision→outcome causal edge 放在同一个 SQLite 骨架。读取不是一个 `vector.search()`：

```text
query
  ├─ search_facts: BM25 + optional embeddings
  ├─ search_causal: causal text / entity / trace candidates
  ├─ optional graph spreading activation
  └─ search_memory: RRF(k=60) → formatted memory lines
```

写路径在 distill 后维护 BM25 与可选 embedding；更新时 retire 旧 fact 再写新值。读取因此可以回到结构化 fact/revision，而非只取匿名 chunk。可选 `local-embed` 使用 384 维 BGE-small ONNX，需要首次下载模型与可动态加载的 ONNX Runtime；HTTP embedding 则依赖 endpoint/model 配置。

这套结构的特别之处是把 outcome relation 放入检索：一个失败决策可以沿因果 edge 激活相关 lesson。风险也来自同一处——跨任务 meta-edge 若建立在弱相似上，spreading activation 会扩大错误类比。distill 失败时 raw log 保留且不写 done marker，使其可重试，但 facts/causal recall 在修复前不完整。[v09 固定版本报告](../../../../agent-memory-v09/bundle/projects/jingxuanc-causal-memory.md)

## 2. OpenViking：目录层级本身参与导航

固定版本 `7f6085a2f95c8a79ec4eb82f973cae57628341a9` 将 resource、memory 和 skill 统一为 `viking://` 虚拟文件系统。完整内容与多媒体在 AGFS，向量索引只保留 URI、vector 和 metadata。查询先由 IntentAnalyzer 决定入口，再用优先队列做 hierarchical search，rerank 后按 L0/L1/L2 层级从 AGFS 加载内容：

```text
query → intent
      → vector / directory seeds
      → priority-queue tree traversal
      → rerank
      → URI hydration from AGFS
      → context + retrieval trajectory
```

层级表示让系统能先读短 overview，再按需要进入 summary 或完整内容，避免一次把大资源塞进上下文。但写入后的语义处理是异步的：Parser/TreeBuilder 先把内容落 AGFS，SemanticQueue 再自底向上生成 L0/L1 并更新向量索引。若调用方未等待 `wait_processed`，内容已存在却可能暂时无法语义召回。

另一个具体失败是 AGFS 与 vector index 分裂：索引 URI 可指向旧/缺失内容，或内容已经存在但未索引。恢复不能只重启服务，而要比较内容 revision、processing state 和 index watermark。[v10 项目工程报告](../../projects/volcengine--openviking.md)

## 3. Engraphis：在 hard token budget 下融合四类索引

固定版本 `128fe0515b842923df871a777eaacc3327f40513` 用一个 SQLite 文件保存 memory、FTS、bitemporal history、layered graph/code links 和 receipt；向量层默认 NumPy exact scan，可选 sqlite-vec。`MemoryEngine` 在 recall 中组合 lexical/vector/graph/code candidates，rerank 后打包到 hard token budget。

它的关键工程约束是 embedding fingerprint。模型或 revision 改变时，已有向量即使维数一样也可能不可比较；实现会禁止 persistent vector recall，直到一致重建。sqlite-vec 与 SQLCipher 的 native SQLite library 也不能安全共存：auto 模式回退 NumPy，显式 sqlite-vec 配置则启动失败。也就是说，后端选择同时改变性能、加密与失效模式，不只是配置字符串。

另一个容易误诊的情况是“数据存在但 recall 为空”：record 可能还没有 prompt eligibility，或调用使用了错误 workspace/repo/session scope。这是 review/scope gate，不是索引损坏。可观察系统需要把过滤 trace 与索引 trace 分开。[v10 项目工程报告](../../projects/coding-dev-tools--engraphis.md)

## 4. Mem0：多信号检索取决于后端实际能力

固定版本 `4debc58a83377b18be81ae1e5969a300736b2fac` 的 OSS Python facade 通过 factory 组合 LLM、embedder、vector store 和 optional reranker。读取时按 user/agent/run filters 隔离，再根据 provider 支持情况组合 semantic、BM25 keyword 和 entity signals。

重要边界是：不是每个 vector backend 都实现 `keyword_search`。缺少该能力时，代码明确禁用 BM25，系统退化为 semantic route；因此 README 的“hybrid”不能自动外推到所有配置。Entity collection 也是独立伴随索引，更新失败时主 memory 仍可检索，但 entity boost 和 linked-memory 关系缺失。最终返回质量取决于主 store、history、entity index 和 reranker 的部分一致性。

身份必须从显式 filters/entity parameters 传入；metadata 中伪造的 user/agent/run id 会被剥离。旧调用若把身份只放 metadata，会出现“已写但无法按目标身份召回”，或在不严谨 adapter 中造成 scope 错配。[v10 项目工程报告](../../projects/mem0ai--mem0.md)

## 5. claude-mem：搜索之后还要按 ID 渐进披露

固定版本 `4702c337d85aa12e8ab7f845264a78885676261f` 由 Claude Code/OpenCode hooks 捕获 prompt、tool use 和 session end。SQLite 保存 sessions、observations、summaries 和 pending queue，ChromaDB 保存 observation vectors。MCP 读取不是直接回传所有观察，而是 `search → timeline → get_observations` 的渐进披露：先返回较小命中，再按 ID 展开上下文。

这一设计把 candidate budget 和 hydration budget 分开，适合编码 session 中大量工具记录。它也带来 dual-store 风险：SQLite commit 后 ChromaSync/MCP process 失败时，关键词数据存在但 semantic index stale；worker 则故意 fail-open，服务不可用时 host session 继续，代价是本轮 capture/recall 缺失。系统若只看 Agent 是否继续工作，会遗漏记忆层退化。

`contentSessionId` 与 `memorySessionId` 的语义不同，转换错误会破坏外键和 session continuity。这说明跨会话 memory 的“身份”不是一个字符串命名问题，而是读取能否回到正确时间线的约束。[v10 项目工程报告](../../projects/thedotmack--claude-mem.md)

## 6. Raven：host loop 负责何时读，backend 负责怎样读

固定版本 `14b7419245b816782b0435385d238f9f18ac090f` 把 Raven host loop 与 `MemoryBackend` protocol 分开。AgentLoop 在 turn 前按 user/agent track 调 `recall(query, top_k)`，context_engine 在预算内渲染 memory segment；turn 后再 `store` session slice 和 feedback。Bundled EverOS adapter 可以走 embedded 或 HTTP search，skill-forge 又把 memory hits 与本地/Hub skill candidates 融合。

这里的检索算法有一部分在精确 pin 的 `everos[multimodal]==1.2.1` 中，不在 Raven 仓库本身。它揭示了依赖边界：adapter 的固定 SHA 并不足以冻结真正的索引/抽取行为，还要冻结被适配包。版本升级可能需要重建 `~/.everos/.index`。若 plugin factory/import 失败，host 会退化为 no-backend，Agent 仍可运行但持久 memory 消失。

另一个关键约束是 `memory.userId` 和 `memory.agentId` 是 recall/store 的身份来源。两条 track 不一致会导致数据存在却取不回，或跨 track 暴露。它与“用哪种向量数据库”无关，却往往更决定系统是否正确。[v10 项目工程报告](../../projects/evermind-ai--raven.md)

## 7. 六个实现放在同一读路径上

| 系统 | 权威层 | 候选路线 | 融合/导航 | 编译/展开 | 主要可见故障 |
|---|---|---|---|---|---|
| Causal Memory | SQLite logs/facts/causal edges | BM25、optional embedding、entity/trace | RRF + typed activation | memory lines | distill 未完成、embedding 不可用、错误 meta-edge |
| OpenViking | AGFS | vector、directory hierarchy | priority queue + rerank | L0/L1/L2 hydration | async 未完成、AGFS/index 分裂 |
| Engraphis | SQLite record/history/graph | FTS、exact/vector、graph、code | engine fusion + rerank | hard-budget context pack | fingerprint mismatch、scope/review gate |
| Mem0 | vector store + history/entity companions | semantic、keyword、entity | provider-dependent fusion/rerank | result objects | backend 无 keyword、entity partial failure |
| claude-mem | SQLite observations/summaries | FTS + Chroma semantic | hybrid search | search→timeline→ID expand | worker fail-open、SQLite/Chroma stale |
| Raven | selected backend | backend-defined | host/context + skill fusion | budgeted segment | backend fallback、identity track mismatch |

这张表显示，所谓“检索方案”至少包含权威对象、索引、融合、上下文展开和失败可见性五个决策。系统名称或数据库标签不足以说明读取语义。

继续看[基准、成本与研究前沿](03-benchmarks-cost-and-frontier.md)。
