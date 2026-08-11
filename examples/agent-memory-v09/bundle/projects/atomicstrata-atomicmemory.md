# atomicstrata/atomicmemory：固定提交工程深潜

**Cluster:** MM-C02  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 683bd92c9c77877962d7425e27b50cb83867fd9e |
| Created / pushed | 2026-05-18 / 2026-08-09 |
| Freshness bucket | newly-created-90d |
| Release | cli-v0.2.0 / 2026-08-07T09:12:33Z |
| License | NOASSERTION |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 40 / 2 |
| Single snapshot stars / forks / open issues | 421 / 37 / 21 |
| Engineering surface | strong-surface (7/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

TypeScript/Rust monorepo以Core作为Postgres/pgvector memory backend，MemoryService注入episode/memory/claim/entity/link/lesson/raw-content stores，ingest pipeline抽取canonical memory objects与representations，search pipeline做vector/keyword/entity/temporal/contradiction-aware retrieval。SDK、MCP、CLI与Vercel/OpenAI Agents/LangChain/LangGraph/Mastra adapters共享该backend；可选S3/Filecoin/IPFS-style raw storage由registry/reconciler维护。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| MemoryService | 统一ingest/quickIngest/verbatim/workspace、scoped search/CRUD、consolidation/decay/audit与event-chain API | `GR-S058-T` — packages/core/src/services/memory-service.ts; blob f4a23f767d9565fb43f1da436a6dce150b45d8c8; sha256 914914cc9586a65b7c5aa7bc2e650090132e9314c6e3bd0d047c1e4e239dacdf |
| Postgres repositories/stores | 保存episodes、canonical memory objects、representations、links/entities、audit与pgvector search | `GR-S058-T` — packages/core/src/db/memory-repository.ts; blob 3fb2f54bfafd9cdc6b99f03795027211b449dfc6; sha256 dcf0868818e0939207b62c70547f1e263708dab43c91425d0fb48190d7bd56e3 |
| ingest/extraction/embedding pipeline | conversation→episode→facts/claims/foresight/embeddings/lineage并执行post-write/reflection | `GR-S058-T` — tree packages/core/src/services/{memory-ingest,extraction,embedding,ingest-post-write}.ts |
| search/retrieval pipeline | semantic/hybrid/entity/namespace/temporal/iterative retrieval、rerank、receipt与format budget | `GR-S058-T` — tree packages/core/src/services/{memory-search,search-pipeline,hierarchical-retrieval,iterative-retrieval,retrieval-*}.ts |
| SDK/MCP/adapters | 在多个agent frameworks复用capture/retrieval语义和同一store | `GR-S058-R` — readmes/GRC058.md repository layout/package matrix; tree adapters,packages/sdk,packages/mcp-server |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | SDK/MCP/adapter提交conversation、scope、source与optional raw content | agent host → MemoryService.ingest/workspaceIngest | `GR-S058-T` — memory-service.ts ingest methods |
| 2 | ingest pipeline保存episode/raw artifact并调用LLM extraction/embedding形成canonical memories与lineage | conversation → episode/memory/claim representations | `GR-S058-T` — tree memory-ingest.ts/extraction.ts/embedding.ts |
| 3 | repositories在Postgres写memory、pgvector、facts/foresight/links/entities/audit；外部raw store由registry记录 | ingest outputs → Postgres/pgvector + optional raw storage | `GR-S058-T` — memory-repository.ts storeEpisode/storeMemory/storeAtomicFacts/createLinks |
| 4 | scopedSearch选择user/workspace path，融合vector/keyword/entity/temporal channels并返回receipt/packaged context | query + stores → SDK/MCP result | `GR-S058-T` — memory-service.ts scopedSearch/search; search-pipeline tree |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| PostgreSQL pg + pgvector | Core durable store与semantic/hybrid search | `GR-S058-T` — packages/core/package.json blob 8c64de8ab2883f26f01c3cbd24f8f214be5bb241; sha256 e7abcdc9317927a2ee2dbd1e61abdfaf09f120748197719db97efd08b47f9b02 |
| OpenAI/Anthropic/HuggingFace transformers | extraction、embedding、answer/rerank provider surfaces | `GR-S058-T` — packages/core/package.json dependencies |
| Express/Zod/Jose | Core HTTP/OpenAPI/auth schema surface | `GR-S058-T` — packages/core/package.json dependencies |
| S3/Synapse/Filecoin/Helia optional stack | raw document artifact persistence/reconciliation | `GR-S058-T` — packages/core/package.json dependencies/optionalDependencies |

**Integration constraints:**

- Core DB tests和运行需要Postgres/pgvector；README明确DB-backed tests在普通quick validation之外。 (`GR-S058-R` — readmes/GRC058.md Validation boundary/Local development)
- package matrix区分published/coming soon/deprecated；不能因源码存在就给Codex/Cursor plugin或deprecated npm CLI承诺可安装路径。 (`GR-S058-R` — readmes/GRC058.md package matrix lines 214-266)
- user与workspace scoped search走不同repository enforcement；adapter必须正确传workspaceId/agent scope，不能只依赖metadata。 (`GR-S058-T` — memory-service.ts scopedSearch/scopedGet/scopedDelete)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=40、unique contributors=2、open issues snapshot=21；latest observed release cli-v0.2.0；CI/tests 存在。 (`GR-S058-O` — observations.jsonl/repositories.jsonl GRC058)
- open issues snapshot=21；PR latency、issue close-time、package-specific backlog与release cadence未测。 (`GR-S058-O` — observations.jsonl GRC058)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| Postgres/pgvector不可用 | DB/migration/extension未就绪或embedding维度不一致 | Core ingest/search失败；不是纯本地SDK可自动兜底的路径 | GR-S058-R, GR-S058-T; inference=true |
| canonical/derived partial write | memory row成功但facts/foresight/links/post-write阶段失败 | 主memory可见但网络、contradiction或retrieval channels不完整 | GR-S058-T; inference=true |
| raw artifact divergence | S3/Filecoin写入、hash verify或reconciler失败 | DB metadata与外部原文状态不一致，需要recovery/reconciliation | GR-S058-T; inference=true |
| deprecated repository seam | 外部modules继续依赖标记deprecated的MemoryRepository而store interfaces演进 | 迁移期间API重复/行为漂移或遗漏runtime config | GR-S058-T; inference=false |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** authoritative ledger 与 vector/graph/lexical projections 是否可重建且有 watermark。

**首要失败风险：** crash consistency、schema/index drift、物理删除与 backup 残留。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

仓库提供发布package与hosted推荐路径，但未验证独立组织生产adoption；README性能姿态明确非已测保证。source-present但unpublished/coming-soon surfaces不计可采用实现。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 独立adoption未验证
- multi-store transaction/recovery guarantees未实测
- 各package release alignment未知

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 在固定数据集上测写入/更新/重建/恢复、索引滞后、存储增长和删除 manifest。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:17:42Z GitHub snapshot, atomicstrata/atomicmemory was created 2026-05-18, last pushed 2026-08-09, pinned at 683bd92c9c77877962d7425e27b50cb83867fd9e, had 421 cumulative stars, and had latest release cli-v0.2.0 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C058-1 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, the inspected engineering surface for atomicstrata/atomicmemory was setup=documented, CI=present, tests=present, license=NOASSERTION, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C058-2 -->

The repository's own GitHub metadata describes atomicstrata/atomicmemory as: “Portable semantic memory for AI agents: core engine, TypeScript SDK, framework adapters, MCP server, CLI, and host plugins.”
<!-- claim:GR-C058-3 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, fixed-source inspection of atomicstrata/atomicmemory supports this project-specific architecture reading: TypeScript/Rust monorepo以Core作为Postgres/pgvector memory backend，MemoryService注入episode/memory/claim/entity/link/lesson/raw-content stores，ingest pipeline抽取canonical memory objects与representations，search pipeline做vector/keyword/entity/temporal/contradiction-aware retrieval。SDK、MCP、CLI与Vercel/OpenAI Agents/LangChain/LangGraph/Mastra adapters共享该backend；可选S3/Filecoin/IPFS-style raw storage由registry/reconciler维护。 The repository was not executed in v09.
<!-- claim:PRJ-A016 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, atomicstrata/atomicmemory has these inspected dependencies or services: PostgreSQL pg + pgvector: Core durable store与semantic/hybrid search; OpenAI/Anthropic/HuggingFace transformers: extraction、embedding、answer/rerank provider surfaces; Express/Zod/Jose: Core HTTP/OpenAPI/auth schema surface; S3/Synapse/Filecoin/Helia optional stack: raw document artifact persistence/reconciliation. Its recorded integration constraints are: Core DB tests和运行需要Postgres/pgvector；README明确DB-backed tests在普通quick validation之外。; package matrix区分published/coming soon/deprecated；不能因源码存在就给Codex/Cursor plugin或deprecated npm CLI承诺可安装路径。; user与workspace scoped search走不同repository enforcement；adapter必须正确传workspaceId/agent scope，不能只依赖metadata。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I016 -->

At pinned commit 683bd92c9c77877962d7425e27b50cb83867fd9e, the inspected repository tree for atomicstrata/atomicmemory exposed these architecture or integration locations: adapters, crates, examples, packages, plugins, scripts, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C016 -->

At the 2026-08-10T05:17:42Z GitHub/API snapshot for atomicstrata/atomicmemory, the inspected rolling-90d window contained 40 commits and 2 unique contributors, while open issues were 21; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M016 -->

<!-- synthesis:PRJ-S16 claims:GR-C058-1,GR-C058-2,GR-C058-3,PRJ-A016,PRJ-I016,PRJ-C016,PRJ-M016 clusters:MM-C02 -->

<!-- process:limitation -->
