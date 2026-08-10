# letta-ai/letta：固定提交工程深潜

**Cluster:** MM-C01  
**Selection:** keep-lineage — Retained for historical/architectural lineage; current trend use is explicitly qualified.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | ff19ffeafeb54bd2a7dc5d4a552f10191732a235 |
| Created / pushed | 2023-10-11 / 2026-08-01 |
| Freshness bucket | foundational-lineage |
| Release | 0.16.8 / 2026-05-14T17:14:24Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 6 / 2 |
| Single snapshot stars / forks / open issues | 24170 / 2572 / 43 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

固定 SHA 是 README 明确标记的 legacy Letta V1 server。其memory分为可直接渲染/编辑的core blocks与archive/source passages：Memory schema把blocks/git-backed filesystem编进prompt，PassageManager切分文本、请求embeddings、写SQLAlchemy archival/source rows与tags，可选按archive dual-write到Turbopuffer；REST/server managers暴露agent、archive、passage与tool API。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| Memory/core blocks schema | 维护in-context blocks、git-backed memory filesystem/skills并编译进prompt | `GR-S001-T` — letta/schemas/memory.py; blob 4c04f3ad04456d09575506d0482933f6da52b825; sha256 febcd15fa5bad3e73a40d5229f75f747782f046c5e3f3c26b8f5c557403cc91c |
| PassageManager + ArchiveManager | 切分archival/source text、生成embeddings、创建tags与passages并处理delete/update | `GR-S001-T` — letta/services/passage_manager.py; blob 171dffead8948c59798aa0ed65e42059a5096c24; sha256 db8fb6ef28b69a9e516e61bfd14ece8c63ed032f0e8a04fc7c84bd153a534c20 |
| SQLAlchemy/SQLModel ORM + vector providers | 持久agent/archive/source/message state；Postgres pgvector、SQLite-vec、Pinecone/Turbopuffer等可选向量路径 | `GR-S001-T` — pyproject.toml database extras; tree letta/orm and services |
| legacy API server | V1 REST/server manager orchestration与SDK兼容表面 | `GR-S001-R` — readmes/GRC001.md legacy notice; tree letta/server/rest_api |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | agent tool/core-memory operation修改Block，或insert_passage接收archival text | agent/server API → Memory schema/PassageManager | `GR-S001-T` — memory.py core_memory_append/replace; passage_manager.py insert_passage |
| 2 | PassageManager chunk text并通过configured LLMClient请求embeddings，无config时允许None | text → passage objects + embeddings | `GR-S001-T` — passage_manager.py insert_passage lines 543-604 |
| 3 | SQL transaction写ArchivalPassage/SourcePassage与tags；Turbopuffer archive再做外部dual-write | passage objects → SQL + optional vector provider | `GR-S001-T` — passage_manager.py create_agent_passage/insert_passage |
| 4 | core blocks直接compile进prompt；archival retrieval经server/archive/vector路径取passages后加入context | Memory blocks/archive passages → LLM context | `GR-S001-T` — memory.py compile; tree archive/search managers |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| SQLAlchemy async + SQLModel + Alembic | V1 server state/passage persistence与migrations | `GR-S001-T` — pyproject.toml blob 30469e3014c050b0851201a74f7ff37017745760; sha256 ba86147a334a4900962b260d1912e263e011e8698377327b9f1a8fd943540c3e |
| OpenAI/Anthropic/LlamaIndex/Letta client | LLM、embeddings、document/index integration | `GR-S001-T` — pyproject.toml dependencies |
| optional Postgres/pgvector, SQLite-vec, Redis, Pinecone/Turbopuffer | database/vector/cache deployment variants | `GR-S001-T` — pyproject.toml optional database extras; passage_manager provider branches |

**Integration constraints:**

- README明确本仓是legacy V1 server，active development已移到letta-code/App Server；新项目不应把此SHA当当前主实现。 (`GR-S001-R` — readmes/GRC001.md lines 1-9)
- agent passage必须有archive_id且不能有source_id；source passage反之，调用方需保持存储域互斥。 (`GR-S001-T` — passage_manager.py create_agent/source passage guards)
- Postgres embedding会pad到MAX_EMBEDDING_DIM，而Turbopuffer/Pinecone不走同一padding语义，跨backend migration需验证维度。 (`GR-S001-T` — passage_manager.py embedding padding branches)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=6、unique contributors=2、open issues snapshot=43；release 0.16.8；CI/tests 存在。 (`GR-S001-O` — observations.jsonl/repositories.jsonl GRC001)
- open issues snapshot=43；PR latency、issue close-time以及legacy-only分类未测。 (`GR-S001-O` — observations.jsonl GRC001)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| Turbopuffer dual-write divergence | SQL passage成功后external insert失败 | 代码仅log error，SQL truth有row但外部vector缺项 | GR-S001-T; inference=false |
| embedding dimension/provider mismatch | 在不同vector provider间迁移或配置维度超过MAX | padding/shape差异造成写失败或检索空间不一致 | GR-S001-T; inference=true |
| legacy integration drift | 用V1 server对接当前Agent SDK/App Server文档 | API、schema、self-host路径不匹配，维护落在非主线代码 | GR-S001-R; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** 服务/控制面是否把 durable records、mutation policy、retrieval 和 admin/observability 分开。

**首要失败风险：** tenant/ACL、迁移、删除、恢复与 centralized blast radius。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

Letta作为项目有历史影响，但本次只核验legacy server SHA；不能将当前Letta Agent/Constellation采用归因于此代码。独立部署/production usage未验证。

公开代码引用只作为弱集成线索：

- `Arindam200/awesome-ai-apps/starter_ai_agents/letta_starter/pyproject.toml`（different owner=true；blob `2525061a5e151f2204ef92c34c488e67b6947a52`）
- `jagmarques/asqav-sdk/python/pyproject.toml`（different owner=true；blob `dd263dbc8617fe1c14985a29632be47a2ea23481`）
- `inni918/warashi/pyproject.toml`（different owner=true；blob `e2698eada25176dc6969f52b776875a859b8b596`）

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- legacy EOL/support policy未知
- 独立adoption未验证
- current App Server架构不在本profile

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 固定版本完成 CRUD→retrieve→supersede→delete→restore，并注入中断和跨 tenant 访问。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:07:13Z GitHub snapshot, letta-ai/letta was created 2023-10-11, last pushed 2026-08-01, pinned at ff19ffeafeb54bd2a7dc5d4a552f10191732a235, had 24170 cumulative stars, and had latest release 0.16.8 on 2026-05-14; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C001-1 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, the inspected engineering surface for letta-ai/letta was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C001-2 -->

The repository's own GitHub metadata describes letta-ai/letta as: “Platform for stateful agents: AI with advanced memory that can learn and self-improve over time.”
<!-- claim:GR-C001-3 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, fixed-source inspection of letta-ai/letta supports this project-specific architecture reading: 固定 SHA 是 README 明确标记的 legacy Letta V1 server。其memory分为可直接渲染/编辑的core blocks与archive/source passages：Memory schema把blocks/git-backed filesystem编进prompt，PassageManager切分文本、请求embeddings、写SQLAlchemy archival/source rows与tags，可选按archive dual-write到Turbopuffer；REST/server managers暴露agent、archive、passage与tool API。 The repository was not executed in v09.
<!-- claim:PRJ-A014 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, letta-ai/letta has these inspected dependencies or services: SQLAlchemy async + SQLModel + Alembic: V1 server state/passage persistence与migrations; OpenAI/Anthropic/LlamaIndex/Letta client: LLM、embeddings、document/index integration; optional Postgres/pgvector, SQLite-vec, Redis, Pinecone/Turbopuffer: database/vector/cache deployment variants. Its recorded integration constraints are: README明确本仓是legacy V1 server，active development已移到letta-code/App Server；新项目不应把此SHA当当前主实现。; agent passage必须有archive_id且不能有source_id；source passage反之，调用方需保持存储域互斥。; Postgres embedding会pad到MAX_EMBEDDING_DIM，而Turbopuffer/Pinecone不走同一padding语义，跨backend migration需验证维度。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I014 -->

At pinned commit ff19ffeafeb54bd2a7dc5d4a552f10191732a235, the inspected repository tree for letta-ai/letta exposed these architecture or integration locations: alembic, assets, certs, db, examples, fern, letta, otel, sandbox, scripts, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C014 -->

At the 2026-08-10T05:07:13Z GitHub/API snapshot for letta-ai/letta, the inspected rolling-90d window contained 6 commits and 2 unique contributors, while open issues were 43; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M014 -->

<!-- synthesis:PRJ-S14 claims:GR-C001-1,GR-C001-2,GR-C001-3,PRJ-A014,PRJ-I014,PRJ-C014,PRJ-M014 clusters:MM-C01 -->

<!-- process:limitation -->
