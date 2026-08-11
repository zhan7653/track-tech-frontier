# 410979729/scope-recall-hermes：固定提交工程深潜

**Cluster:** MM-C04  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 867b9939e037299befd930647a5015ee6e4945c0 |
| Created / pushed | 2026-05-15 / 2026-08-08 |
| Freshness bucket | newly-created-90d |
| Release | v1.9.1 / 2026-08-08T15:28:49Z |
| License | MIT |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 126 / 4 |
| Single snapshot stars / forks / open issues | 220 / 20 / 3 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

Hermes provider 以 journal-first capture 隔离原始 turn 与 durable facts：SQLite 是权威 truth，digest/candidate/promotion 把证据变成 user/memory/project/ops rows，LanceDB、SQLite brute-force 或 PGVector 只作可重建 companion，recall_pipeline 以词法/向量/graph/freshness 信号融合当前 turn。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| journal/digest/candidate pipeline | 捕获合格 turn、生成 evidence packet/candidate，并经 review/promotion 写 durable memory | `GR-S057-T` — tree paths journal_store.py,event_digest.py,candidate_store.py,candidate_promotion.py; docs/memory.stack.contract.md |
| SQLite truth + lifecycle/relations | 保存 memories、FTS、scope、temporal/lifecycle、conflict/graph relations 与审计 receipt | `GR-S057-T` — memory_ops.py blob bc0d2720f530fcf5e8cbd765d218a76d7d8c5a66; sha256 4525daf2a72dedc2deac69b7a3406d7f89cd060a536420c4555232bb50f300ae |
| vector runtime + recall pipeline | 以 outbox 将 truth mutation 同步到 LanceDB/sqlite-vector/PGVector companion，再融合候选并解释 filter trace | `GR-S057-T` — tree paths vector_runtime.py,pgvector_store.py,sqlite_vector_store.py,recall_pipeline.py; memory_ops.py imports |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | Hermes hooks 捕获当前 turn 到 journal，并应用 secret/scope filters | Hermes conversation → journal staging | `GR-S057-R` — readmes/GRC057.md design promises |
| 2 | digest/candidate process 压缩证据，review/promotion 决定 durable 写入 | journal events → candidate ledger/durable memory intent | `GR-S057-T` — docs/memory.stack.contract.md promotion receipts |
| 3 | memory_ops 在 SQLite 事务写 truth、FTS、relations、freshness 并 enqueue vector intent | approved memory → SQLite + vector outbox | `GR-S057-T` — memory_ops.py store_memory_now/update_memory/merge_memories |
| 4 | outbox replay 更新 vector companion；recall 以 RRF/filters 取当前 turn evidence | SQLite/FTS/vector/graph → Hermes context | `GR-S057-T` — memory_ops.py replay_vector_outbox; recall_pipeline.py tree path |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| PyYAML + jsonschema | 核心配置/schema 验证 | `GR-S057-T` — pyproject.toml blob 805447e79b9a61263d6430cd57ec999edc39220b; sha256 0f99e4c2d8bfd87110e81c225b604d2d2a3339c7c495256bc48c1da9f380c505 |
| lancedb + pyarrow optional | 默认语义 vector companion extra | `GR-S057-T` — pyproject.toml optional-dependencies.lancedb |
| psycopg + pgvector optional | 中央 PostgreSQL/PGVector companion or bridge | `GR-S057-T` — pyproject.toml optional-dependencies.pgvector |

**Integration constraints:**

- general 是本地 scratch 且默认不进入 durable vector；user/memory/project/ops 才是 durable scopes，调用方必须保留身份/范围语义。 (`GR-S057-T` — docs/memory.stack.contract.md lines 155-164)
- 多 agent 已有中央 PostgreSQL 时，README 明确本插件应是本地 Hermes recall layer而非跨 agent source of truth。 (`GR-S057-R` — readmes/GRC057.md deployment boundaries)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=126、unique contributors=4、open issues snapshot=3；release v1.9.1；CI/tests 存在。 (`GR-S057-O` — observations.jsonl/repositories.jsonl GRC057)
- open issues snapshot=3；PR latency、issue close-time 与 release regression rate 未测。 (`GR-S057-O` — observations.jsonl GRC057)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| vector companion 债务 | truth commit 后 LanceDB/PGVector replay 失败 | SQLite truth 成功但 semantic index stale，代码标 needs_repair/pending | GR-S057-T; inference=false |
| scope leakage | adapter 传错 scope_mode/identity 或把 general 当 durable | 跨 chat/agent 错召回或 scratch 被永久化 | GR-S057-R, GR-S057-T; inference=true |
| SQLite contention/recovery | 并发 provider 写锁或异常中断 | store 失败、retry/rollback 路径被触发，可能留下待 replay intent | GR-S057-R, GR-S057-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** hard scope/time filter、candidate generation、rerank 与 context compiler 是否分层。

**首要失败风险：** 高 recall 但 stale/unauthorized、预算不公平和不可解释 fusion。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

未验证独立第三方生产采用；README 长版本说明与 benchmark 结果是维护者陈述。该仓只覆盖 Hermes 实现，不代表 OpenClaw sibling 或中央 shared-memory backend。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 未运行 Hermes integration
- 独立 adoption/规模未知
- companion recovery SLO 未测

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 固定 store/model/budget 对照 BM25、semantic、graph 与 hybrid，保存候选/拒绝/rank trace。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:17:37Z GitHub snapshot, 410979729/scope-recall-hermes was created 2026-05-15, last pushed 2026-08-08, pinned at 867b9939e037299befd930647a5015ee6e4945c0, had 220 cumulative stars, and had latest release v1.9.1 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C057-1 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, the inspected engineering surface for 410979729/scope-recall-hermes was setup=documented, CI=present, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C057-2 -->

The repository's own GitHub metadata describes 410979729/scope-recall-hermes as: “Hermes Agent memory plugin/provider for scope-aware recall, SQLite truth, LanceDB semantic search, and hybrid retrieval.”
<!-- claim:GR-C057-3 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, fixed-source inspection of 410979729/scope-recall-hermes supports this project-specific architecture reading: Hermes provider 以 journal-first capture 隔离原始 turn 与 durable facts：SQLite 是权威 truth，digest/candidate/promotion 把证据变成 user/memory/project/ops rows，LanceDB、SQLite brute-force 或 PGVector 只作可重建 companion，recall_pipeline 以词法/向量/graph/freshness 信号融合当前 turn。 The repository was not executed in v09.
<!-- claim:PRJ-A004 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, 410979729/scope-recall-hermes has these inspected dependencies or services: PyYAML + jsonschema: 核心配置/schema 验证; lancedb + pyarrow optional: 默认语义 vector companion extra; psycopg + pgvector optional: 中央 PostgreSQL/PGVector companion or bridge. Its recorded integration constraints are: general 是本地 scratch 且默认不进入 durable vector；user/memory/project/ops 才是 durable scopes，调用方必须保留身份/范围语义。; 多 agent 已有中央 PostgreSQL 时，README 明确本插件应是本地 Hermes recall layer而非跨 agent source of truth。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I004 -->

At pinned commit 867b9939e037299befd930647a5015ee6e4945c0, the inspected repository tree for 410979729/scope-recall-hermes exposed these architecture or integration locations: benchmarks, docs, examples, scripts, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C004 -->

At the 2026-08-10T05:17:37Z GitHub/API snapshot for 410979729/scope-recall-hermes, the inspected rolling-90d window contained 126 commits and 4 unique contributors, while open issues were 3; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M004 -->

<!-- synthesis:PRJ-S04 claims:GR-C057-1,GR-C057-2,GR-C057-3,PRJ-A004,PRJ-I004,PRJ-C004,PRJ-M004 clusters:MM-C04 -->

<!-- process:limitation -->
