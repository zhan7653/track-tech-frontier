# xerj-org/xerj：固定提交工程深潜

**Cluster:** MM-C02  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | c52c562ae5cedae3feed3f590409cf07e929197a |
| Created / pushed | 2026-06-30 / 2026-08-10 |
| Freshness bucket | newly-created-90d |
| Release | v1.0.0-rc.13 / 2026-08-08T18:51:00Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 907 / 10 |
| Single snapshot stars / forks / open issues | 1321 / 292 / 33 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

固定 SHA 是一个 Rust 搜索/向量/日志引擎而非专用 agent-memory SDK；Elasticsearch-compatible HTTP 是采用桥，xerj-query 解析 DSL，xerj-engine 协调 WAL/segments、BM25 与 HNSW/exact vector，/_memory 只是其上的应用表面。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| xerj-api + xerj-query | Axum HTTP/ES-compatible handlers把 JSON 请求解析成 QueryNode 并规划执行 | `GR-S006-T` — docs/ARCHITECTURE.md; blob f75f4362a10b887958475e8c0314e0ed0ec7bee7; sha256 000d561331017544a311fb3a79032e49df6f625870e4c0539e5235474e1e7d5e |
| xerj-engine | Engine/Index 组合 storage、FTS、vector、aggregation 并合并 memtable/segment 命中 | `GR-S006-T` — engine/crates/xerj-engine/Cargo.toml; blob 028484792cf7675bbd694376962009449244c75e; sha256 bed17d99e797582584c3fdefbabb6b6e6d48362e34ab8f70eccea740f5e041b7 |
| xerj-storage + xerj-fts + xerj-vector | 分别提供 WAL/分片 memtable/immutable segments、BM25 postings、持久 HNSW 与 filtered exact scan | `GR-S006-T` — docs/ARCHITECTURE.md lines 46-60,64-121 |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | PUT doc 或 bulk 请求进入 Axum handler | ES/native HTTP client → xerj-api | `GR-S006-T` — docs/ARCHITECTURE.md lines 92-101 |
| 2 | IndexStore 批量追加 WAL 并写分片 memtable | xerj-engine → xerj-storage WAL/memtable | `GR-S006-T` — docs/ARCHITECTURE.md ingest path |
| 3 | 后台 flush 排序 WAL seq_no、压缩为 immutable segment并 merge | memtable → on-disk segments | `GR-S006-T` — docs/ARCHITECTURE.md lines 95-108 |
| 4 | search 解析 DSL，扫描 memtable/segments并调用 HNSW或exact vector，再返回 JSON | xerj-query/xerj-engine → HTTP response | `GR-S006-T` — docs/ARCHITECTURE.md lines 64-89 |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| tokio + axum + tower-http | 异步 runtime 与 HTTP transport | `GR-S006-T` — engine/Cargo.toml blob ffe748be77f124e82705769fdd68fad1fc212dc4; sha256 c6d63be634c122bbd192952fdfbb4b5bccadefa7f62051088a2ac8763db2e288 |
| memmap2, roaring, fst, lz4_flex, zstd | segment/index 数据结构与压缩 | `GR-S006-T` — engine/Cargo.toml workspace dependencies |
| aws-sdk-s3/aws-config | S3-compatible object integration；不是本地核心路径的必需外部服务 | `GR-S006-T` — engine/Cargo.toml workspace dependencies |

**Integration constraints:**

- 兼容的是 Elasticsearch 8.x API 子集，不等同完整 Elasticsearch；调用方必须按支持矩阵验证 query/aggregation。 (`GR-S006-R` — readmes/GRC006.md lines 134-155)
- 索引与恢复依赖 data_dir/WAL/segment 一致性；需要运行独立 server，嵌入 agent 时承担进程、端口和持久卷运维。 (`GR-S006-T` — docs/ARCHITECTURE.md recovery/deployment flow)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=907、unique contributors=10、open issues single snapshot=33；release v1.0.0-rc.13；CI/tests 存在。 (`GR-S006-O` — observations.jsonl/repositories.jsonl GRC006)
- open issues snapshot=33；PR latency、issue close-time、RC 到 stable 的时间均未测。 (`GR-S006-O` — observations.jsonl GRC006)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| 高写入下读尾延迟 | 持续高率 writer 与 read 并发 | 项目自述 benchmark 的四个 loss 均为 read p99 gap | GR-S006-R; inference=false |
| WAL/segment 恢复失败 | 持久卷损坏或不完整 snapshot/restore | 重放不能重建完整 memtable/FTS 状态，索引不可用或缺文档 | GR-S006-T; inference=true |
| ES compatibility drift | 客户端使用未覆盖或语义不同的 ES API | 迁移看似成功但查询/聚合结果或错误契约不一致 | GR-S006-R, GR-S006-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** authoritative ledger 与 vector/graph/lexical projections 是否可重建且有 watermark。

**首要失败风险：** crash consistency、schema/index drift、物理删除与 backup 残留。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

ES protocol 是潜在采用桥，但本次未验证独立生产部署；README benchmark/兼容数字为项目方证据，未复跑；stars 不用于质量判断。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 独立 adoption 未验证
- 未运行 recovery/conformance/benchmark

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 在固定数据集上测写入/更新/重建/恢复、索引滞后、存储增长和删除 manifest。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:09:43Z GitHub snapshot, xerj-org/xerj was created 2026-06-30, last pushed 2026-08-10, pinned at c52c562ae5cedae3feed3f590409cf07e929197a, had 1321 cumulative stars, and had latest release v1.0.0-rc.13 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C006-1 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, the inspected engineering surface for xerj-org/xerj was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C006-2 -->

The repository's own GitHub metadata describes xerj-org/xerj as: “XERJ is the new way for AI to search data. Its autoindex capability activates agents to know your data without…”
<!-- claim:GR-C006-3 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, fixed-source inspection of xerj-org/xerj supports this project-specific architecture reading: 固定 SHA 是一个 Rust 搜索/向量/日志引擎而非专用 agent-memory SDK；Elasticsearch-compatible HTTP 是采用桥，xerj-query 解析 DSL，xerj-engine 协调 WAL/segments、BM25 与 HNSW/exact vector，/_memory 只是其上的应用表面。 The repository was not executed in v09.
<!-- claim:PRJ-A002 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, xerj-org/xerj has these inspected dependencies or services: tokio + axum + tower-http: 异步 runtime 与 HTTP transport; memmap2, roaring, fst, lz4_flex, zstd: segment/index 数据结构与压缩; aws-sdk-s3/aws-config: S3-compatible object integration；不是本地核心路径的必需外部服务. Its recorded integration constraints are: 兼容的是 Elasticsearch 8.x API 子集，不等同完整 Elasticsearch；调用方必须按支持矩阵验证 query/aggregation。; 索引与恢复依赖 data_dir/WAL/segment 一致性；需要运行独立 server，嵌入 agent 时承担进程、端口和持久卷运维。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I002 -->

At pinned commit c52c562ae5cedae3feed3f590409cf07e929197a, the inspected repository tree for xerj-org/xerj exposed these architecture or integration locations: demo, deploy, docs, engine, functions, landing, metrics, recipes, scripts, user-feedback, xerj-ux; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C002 -->

At the 2026-08-10T05:09:43Z GitHub/API snapshot for xerj-org/xerj, the inspected rolling-90d window contained 907 commits and 10 unique contributors, while open issues were 33; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M002 -->

<!-- synthesis:PRJ-S02 claims:GR-C006-1,GR-C006-2,GR-C006-3,PRJ-A002,PRJ-I002,PRJ-C002,PRJ-M002 clusters:MM-C02 -->

<!-- process:limitation -->
