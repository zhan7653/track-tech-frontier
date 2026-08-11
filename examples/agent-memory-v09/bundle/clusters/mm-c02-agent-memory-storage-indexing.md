# MM-C02 — Agent-Memory Storage & Indexing：深度报告

> 状态：final cluster report；证据截止 `2026-08-10`。本稿讨论 agent-memory workload 的持久 substrate、索引与恢复边界，不把 generic vector database、普通 RAG 服务或 vendor feature list 本身算作完整 Agent Memory。

## 结论先行

MM-C02 的核心不是在 SQL、vector、graph 三者中选一个冠军，而是建立“权威状态与派生访问路径”的不对称关系：原始 evidence/receipt 与 revision ledger 承担可恢复事实，typed current/history state 承担应用语义，FTS、embedding、entity、graph、temporal index 承担可重建候选访问。这样 write correctness、delete propagation、index rebuild 和 query budget 才能分别测量；把 vector row 当成唯一事实源会混淆抽取、版本、索引与删除。**判断：条件共识；信心 medium-high；成熟度为“常规存储组件成熟，agent-memory 事务/跨索引一致性证据不足”。**（支持 claims：FND-C05、FND-C17、FND-C23、REP-C01、REP-C02、REP-C12、REP-C14、REP-C22、PRJ-A002、PRJ-A016；支持 evidence：FND-EV08、FND-EV32、FND-EV33、FND-EV44、FND-EV45、FND-EV46、REP-V01、REP-V03、REP-V23、REP-V27、REP-V43、REP-V44、PRJ-AE002-01、PRJ-AE016-01；反对/限定 claims：FND-C18、REP-C19；反对/限定 evidence：FND-EV34、FND-EV35、REP-V38、REP-V39。）

边界上，本簇纳入专为 agent memory 暴露 scope、revision、history、hybrid access、transaction/recovery 或 memory object schema 的 embedded store、service backend 与索引层；排除只有近邻搜索、没有跨 session/lifecycle 语义的 generic vector DB，也不把 `/memory` 路由名称当成证明。与 MM-C01 的区别是这里回答“状态如何落盘和访问”，与 MM-C03 的区别是这里不预设 graph/bitemporal 表示一定优于 flat substrate，与 MM-C04 的区别是 candidate 排名和 context compilation 不由本簇完成。（支持 claims：REP-C09、REP-C17、REP-C18、REP-C22、PRJ-A002；支持 evidence：REP-V17、REP-V18、REP-V33、REP-V34、REP-V36、REP-V37、REP-V43、REP-V44、PRJ-AE002-01；反对/限定 claims：none；反对/限定 evidence：none。）

## 分层证据选择

| 证据层 | 代表性条目与时间 | 本稿使用方式 | 支持 claim / evidence | 反对或限定 claim / evidence |
|---|---|---|---|---|
| foundational paper | MemoryBank，2024；MemGPT，2024-02-12 | 把 storage、retrieval、updating 与 tier placement 分离，确定 substrate 不是完整系统 | FND-C03、FND-C05 / FND-EV04、FND-EV08、FND-EV09 | FND-C18 / FND-EV34、FND-EV35 |
| recent paper | AtomMem，2026-06-18；bitemporal store，2026-07-29；MemTxn，2026-07-30 | typed objects、immutable identity/version、transaction journal 对 schema 与持久边界提出新要求 | REP-C01、REP-C02、FND-C17 / REP-V01、REP-V02、REP-V03、REP-V04、FND-EV32、FND-EV33 | REP-C03 / REP-V05、REP-V06 |
| fixed-commit repository | xerj@`c52c…`，2026-08-10；atomicmemory@`683b…`，2026-08-09 | 分别代表通用搜索引擎 substrate 与 typed memory backend；只用于实现/依赖/集成读取 | PRJ-A002、PRJ-I002、PRJ-A016、PRJ-I016 / PRJ-AE002-01、PRJ-IE002-01、PRJ-AE016-01、PRJ-IE016-01 | PRJ-C002、PRJ-C016 / PRJ-E002、PRJ-E016 |
| implementation corpus | Mem0、Cognee、MemMachine 的打开文档 | 验证 hybrid、graph/vector/ontology、episode/profile/working 分层是实际工程模式 | REP-C11、REP-C12、REP-C14 / REP-V21、REP-V22、REP-V23、REP-V24、REP-V27、REP-V28 | REP-C19 / REP-V38、REP-V39 |
| benchmark | LongMemEval，2024-10-14；MemoryAgentBench，2025-07-07 | 需要跨长程能力与 incremental operation 检验，而不是只测 ANN recall | BEN-C02、BEN-C03 / BEN-EV03、BEN-EV04、BEN-EV05、BEN-EV06 | BEN-C22 / BEN-EV43、BEN-EV44 |
| negative/comparability | LightMem reproduction，2026-07-31；bitemporal sample，2026-07-29 | 表示/索引收益会被 retriever、filter、depth、token budget 和小样本改变 | REP-C03、REP-C05、REP-C06、REP-C17 / REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V33、REP-V34 | none / none |

本稿对 GitHub 的权重高于普通综述中的“代码是否存在”：固定 commit 可回答 WAL、segment、backend、adapter、scope enforcement 和 test surface，但本轮没有 install、recovery drill、load test 或独立 deployment，所以仓库只能证明实现形状，不能证明 substrate 的正确性、吞吐、可用性或采用。维护活动也是调查触发器，不参与技术优劣加权。（支持 claims：PRJ-C002、PRJ-M002、PRJ-C016、PRJ-M016、REP-C19、EXP-C22；支持 evidence：PRJ-E002、PRJ-ME002、PRJ-E016、PRJ-ME016、REP-V38、REP-V39、EXP-V43、EXP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

## 从 foundational 到 recent：substrate 的演化

早期 external-memory 架构通常把 conversation record、summary、profile 或 tier 当成被检索的持久对象；其主要进步是把 storage、retrieval、updating 从模型 context 中分出来。这个阶段足以证明“需要外部状态”，却没有给出统一的 identity、revision、valid/transaction time、完整删除或跨索引恢复协议，因此不能从“有长期存储”推出“有可靠 memory database”。（支持 claims：FND-C03、FND-C05、FND-C18；支持 evidence：FND-EV04、FND-EV08、FND-EV09、FND-EV34、FND-EV35；反对/限定 claims：none；反对/限定 evidence：none。）

近期路线把 store 从“文本+embedding”扩成两类对象：一类是 raw episode/tool outcome/source receipt，另一类是从它派生的 atomic fact、event、profile、claim、entity/link 或 temporal version。AtomMem 与 MemMachine 显示不同 memory object 需要不同 representation；bitemporal store 将 immutable identity、versioned content、valid time 与 transaction time分开；MemTxn 再把 source validation 与 durable snapshot journal 放在 answer model 之外。演化的共识不是“所有系统都应上 graph”，而是 derived state 必须回溯到 evidence，更新不应无痕覆盖历史。（支持 claims：REP-C01、REP-C02、REP-C14、FND-C17、REP-C22；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、REP-V27、REP-V28、FND-EV32、FND-EV33、REP-V43、REP-V44；反对/限定 claims：REP-C03；反对/限定 evidence：REP-V05、REP-V06。）

## 机制与目标架构

建议 substrate 至少划成四层：`append-oriented evidence/receipt ledger`、`typed current + history state`、`materialized access indexes`、`snapshot/rebuild metadata`。ledger 保存 raw input、source、scope、event time、transaction time 和 mutation receipt；typed store 保存 agent 可消费的 episode/fact/profile/procedure/world/control object 及 revision link；indexes 按需要生成 lexical、semantic、entity、graph、temporal access path；snapshot/rebuild 层记录 index schema、embedding/ranker version 和 watermark。只有 ledger/typed state 有权决定“记忆是否存在及当前版本”，index miss 不能等同于删除。（支持 claims：FND-C17、FND-C21、FND-C23、REP-C01、REP-C02、REP-C14、REP-C22；支持 evidence：FND-EV32、FND-EV33、FND-EV40、FND-EV41、FND-EV44、FND-EV45、FND-EV46、REP-V01、REP-V03、REP-V27、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

backend 是可替换实现而非语义本体。SQLite/FTS 适合 local-first 与单文件运维；PostgreSQL/pgvector 适合 typed relational state、scope enforcement 与 service deployment；WAL/segment + BM25/HNSW 适合高吞吐搜索 substrate；graph 或 object store 可作为关系/原始 artifact projection。选择时应以并发、恢复、数据规模、scope、history、删除传播和运维能力为条件，而不是因为论文或 README 使用某个存储就泛化其优越性。（支持 claims：PRJ-A001、PRJ-I001、PRJ-A002、PRJ-I002、PRJ-A016、PRJ-I016、REP-C11、REP-C12；支持 evidence：PRJ-AE001-01、PRJ-IE001-01、PRJ-AE002-01、PRJ-IE002-01、PRJ-AE016-01、PRJ-IE016-01、REP-V21、REP-V22、REP-V23、REP-V24；反对/限定 claims：REP-C17、REP-C19；反对/限定 evidence：REP-V33、REP-V34、REP-V38、REP-V39。）

## write–manage–read–action 数据流与算法边界

**Write。** ingest 先把 raw event 与 source receipt 持久化，再生成 typed candidate；commit 时分配 stable identity/revision，记录 scope 与时间，随后异步或事务性更新 FTS、embedding、entity、graph 等 projection。对于多索引系统，关键不是强迫所有 backend 同步提交，而是让失败可由 durable ledger 和 watermark 检测、重放、重建；若系统选择 dual write，则必须明确哪一个写入为 authoritative，以及部分成功时的补偿路径。（支持 claims：FND-C17、REP-C01、REP-C02、PRJ-A016、PRJ-I016；支持 evidence：FND-EV32、FND-EV33、REP-V01、REP-V02、REP-V03、REP-V04、PRJ-AE016-01、PRJ-IE016-01；反对/限定 claims：FND-C18；反对/限定 evidence：FND-EV34、FND-EV35。）

**Manage。** supersede/revoke/forget 应作用于 object/revision，而不是仅从一个 ANN index 删除；operation 需要更新 current-state pointer，保留或按策略清理 history，传播到 derived indexes、cache、raw artifact 与 snapshot，并留下可审核 receipt。ForgetEval 把 recall 与 supersede/release/purge 分开，AWS 文档展示删除 stored session 的产品级操作，但这些证据都没有证明任一实现已覆盖所有派生副本，因此“搜索不到”不能当成 deletion completeness。（支持 claims：FND-C21、OPS-C21、REP-C22；支持 evidence：FND-EV40、FND-EV41、OPS-J21、REP-V43、REP-V44；反对/限定 claims：OPS-C27；反对/限定 evidence：OPS-J27、OPS-J45。）

**Read。** storage/indexing 层只返回经 hard scope/time filter 的 candidates 与可解释元数据，不应在这里隐式决定最终 prompt；candidate 必须携带 object type、revision、source、validity、index route 和 score components，供 MM-C04 的 ranker/compiler 在匹配预算下选择。Mem0 的 semantic/BM25/entity/temporal signals 和 Cognee 的 vector/graph/ontology 展示 multi-route pattern，但多 route 也会增加重复、冲突和预算，不能由“支持更多索引”直接推导更高任务质量。（支持 claims：REP-C11、REP-C12、REP-C18、REP-C22、OPS-C26；支持 evidence：REP-V21、REP-V22、REP-V23、REP-V24、REP-V36、REP-V37、REP-V43、REP-V44、OPS-J26；反对/限定 claims：REP-C05、REP-C06；反对/限定 evidence：REP-V09、REP-V10、REP-V11、REP-V12。）

**Action。** substrate 不直接授权 tool use，但必须让上层验证“这条 candidate 是否仍是当前可见 revision、属于当前 scope、来自何种 source、是否被 revoke”。行动 outcome 随后作为新 raw event 回到 ledger，形成可追踪闭环。若只把最终 answer 写回 vector store，系统会丢失 tool outcome 与 derived claim 的区别，也无法定位后来错误来自 observation、extraction、retrieval 还是 action。（支持 claims：FND-C23、BEN-C07、BEN-C08、BEN-C25、OPS-C07；支持 evidence：FND-EV44、FND-EV45、FND-EV46、BEN-EV13、BEN-EV14、BEN-EV15、BEN-EV16、BEN-EV49、BEN-EV50、OPS-J07；反对/限定 claims：none；反对/限定 evidence：none。）

## GitHub 实现模式与集成

xerj 的 fixed commit 显示一种“通用搜索 substrate 被 memory 表面调用”的模式：Rust engine 管理 WAL/segments、BM25、HNSW/exact vector，Elasticsearch-compatible HTTP 是接入桥，`/_memory` 只是上层表面。它对 MM-C02 的价值是展示成熟搜索原语怎样成为底座，同时也划清边界：ES 8.x 仅是支持子集，agent 仍需自行承担 object schema、revision、scope 与 lifecycle；本轮未执行 recovery/conformance/benchmark。（支持 claims：PRJ-A002、PRJ-I002、PRJ-C002；支持 evidence：PRJ-AE002-01、PRJ-AE002-02、PRJ-AE002-03、PRJ-IE002-01、PRJ-IE002-02、PRJ-E002；反对/限定 claims：PRJ-M002；反对/限定 evidence：PRJ-ME002。）

atomicmemory 的 fixed commit 显示相反的“typed memory backend”模式：Postgres/pgvector Core 注入 episode、memory、claim、entity/link、lesson、raw-content stores，ingest 与 search pipeline 显式区分 canonical objects、vector/keyword/entity/temporal/contradiction signals，SDK/MCP/CLI/adapters 共享 backend，可选 raw artifact storage 另由 registry/reconciler 管理。这更接近本稿目标架构，但 Core DB 测试需要 Postgres/pgvector，package matrix 包含未发布或 deprecated 表面，workspace/user scope 必须由 adapter 正确传入；多 store transaction/recovery 和独立采用仍未验证。（支持 claims：PRJ-A016、PRJ-I016、PRJ-C016；支持 evidence：PRJ-AE016-01、PRJ-AE016-02、PRJ-AE016-03、PRJ-IE016-01、PRJ-IE016-02、PRJ-E016；反对/限定 claims：PRJ-M016；反对/限定 evidence：PRJ-ME016。）

两种模式的决策不是“搜索引擎 vs memory 产品”二选一：已有搜索平台的团队可把通用 engine 作为 projection 层，在应用侧补 ledger/schema/control；需要统一 SDK/MCP 和 typed objects 的团队可采用 memory backend，但要验证数据库、scope、release 与恢复契约。无论哪条路径，都应在 adapter contract 中固定 identity、revision、scope、query budget、delete/rebuild semantics；否则替换 backend 会改变可见行为而无法审计。（支持 claims：PRJ-I002、PRJ-I016、REP-C18、REP-C22、FND-C17；支持 evidence：PRJ-IE002-01、PRJ-IE002-02、PRJ-IE016-01、PRJ-IE016-02、REP-V36、REP-V37、REP-V43、REP-V44、FND-EV32、FND-EV33；反对/限定 claims：none；反对/限定 evidence：none。）

## 成本与运维模型

storage cost 应按权威字节、revision/history、raw artifact、每类 materialized index 与 snapshot/audit retention 分开；write cost 按 WAL/transaction、extraction、embedding、index fan-out 和 reconciliation；read cost 按 candidate route、I/O、ANN/BM25/graph traversal、rerank 与 returned bytes；maintenance cost 按 compaction、vacuum、reindex、schema/embedding migration、backup/restore 和人工审计。现有 v09 证据能确认这些组件与多 backend 依赖存在，但没有提供同 workload 的全链 p50/p95、bytes/revisions、rebuild 或 recovery 数据，因此不能给出某 substrate 的成本排名。（支持 claims：PRJ-I002、PRJ-I016、FND-C19、FND-C20、REP-C18；支持 evidence：PRJ-IE002-01、PRJ-IE002-02、PRJ-IE016-01、PRJ-IE016-02、FND-EV36、FND-EV37、FND-EV38、FND-EV39、REP-V36、REP-V37；反对/限定 claims：REP-C17；反对/限定 evidence：REP-V33、REP-V34。）

恢复验收至少需要模拟：ledger committed/index missing、部分 dual write、stale embedding version、corrupt segment、scope metadata 丢失、delete 后旧 snapshot 回灌，以及 schema migration 中断；验收目标是应用可见 current/history、derived index 和 audit receipt 重新一致，而不是进程仅能启动。MemTxn 为 durable snapshot journal 提供近期机制证据，xerj/atomicmemory 提供静态存储面，但本包没有执行这些故障注入，因此此处是基于现有边界提出的决策协议，不是已证实 SLO。（支持 claims：FND-C17、FND-C18、PRJ-A002、PRJ-A016；支持 evidence：FND-EV32、FND-EV33、FND-EV34、FND-EV35、PRJ-AE002-01、PRJ-AE016-01；反对/限定 claims：REP-C19；反对/限定 evidence：REP-V38、REP-V39。）

## Benchmark protocol 与可比性

substrate 比较必须共享 object schema、ingest sequence、update/delete workload、scope cardinality、raw/derived bytes、embedding/ranker version、candidate budget、reader model 和 hardware，并分别报告 write amplification、index freshness、candidate recall、current/history correctness、delete propagation、rebuild time、recovery point、p50/p95 和任务结果。只比较 ANN recall 或最终 QA 都不足：前者忽略 lifecycle 与 action，后者把 retriever、budget 和 reader 差异混进 store 结论。（支持 claims：BEN-C02、BEN-C03、BEN-C22、BEN-C25、REP-C17、REP-C18；支持 evidence：BEN-EV03、BEN-EV04、BEN-EV05、BEN-EV06、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50、REP-V33、REP-V34、REP-V36、REP-V37；反对/限定 claims：none；反对/限定 evidence：none。）

representation/index benchmark 还必须报告 candidate loss 的位置。bitemporal 论文在小样本上同时出现 update 增益与 temporal reasoning 下降，作者将下降归因于 post-filter dilution；LightMem reproduction 则显示固定 store 时 retriever 替换即可改变结果，constructed memory 还可能丢失 answer-relevant information。因而 graph、temporal、vector 或 hybrid 的收益都必须在 matched candidate depth/token budget 下与 flat/raw baseline 比，并计入 maintenance 与 rebuild。（支持 claims：REP-C03、REP-C05、REP-C06、REP-C17、REP-C22；支持 evidence：REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V33、REP-V34、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

## 限制、失败与替代方案

主要失败面包括：authoritative/index 身份颠倒、部分 dual write、scope 仅存在于 metadata、revision 覆盖历史、embedding/schema migration 造成新旧混读、delete 未传播到 derived copy、重建从错误 snapshot 开始、以及 backend feature subset 被误当成兼容。Graph/temporal projection 还会增加维护和过滤路径；更多索引若没有 trace 只会扩大不可解释候选面。当前所有 selected repositories 均未执行，故这些风险不能被 README 的测试数、性能数字、stars 或 recent activity 抵消。（支持 claims：PRJ-I002、PRJ-I016、REP-C03、REP-C19、OPS-C21、OPS-C26；支持 evidence：PRJ-IE002-01、PRJ-IE002-02、PRJ-IE016-01、PRJ-IE016-02、REP-V05、REP-V06、REP-V38、REP-V39、OPS-J21、OPS-J26；反对/限定 claims：none；反对/限定 evidence：none。）

替代方案应按约束分层：极小单机部署可用 SQLite + FTS + append history；已有 Postgres 的服务可用 relational current/history + pgvector projection；高搜索吞吐团队可用 WAL/segment engine 作为候选层；关系/时间密集任务才增加 graph/bitemporal；对象/媒体原文可放 object store，但 metadata/receipt 仍进入 ledger。简化路径必须保留 scope、stable identity、revision 与 rebuild contract；若连这些也不需要，问题更接近普通 RAG，不应归入本簇的 Agent Memory substrate。（支持 claims：PRJ-A001、PRJ-I001、PRJ-A002、PRJ-I002、PRJ-A016、PRJ-I016、REP-C02、REP-C22；支持 evidence：PRJ-AE001-01、PRJ-IE001-01、PRJ-AE002-01、PRJ-IE002-01、PRJ-AE016-01、PRJ-IE016-01、REP-V03、REP-V04、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

## 共识、分歧与决策含义

**共识**是多种 memory object 与 multi-index 已成为常见工程形态，且 retrieval budget/版本/scope 会改变行为；**条件共识**是 authoritative ledger + typed state + rebuildable index 最适合可修改、需恢复的 external memory；**争议**是 graph、bitemporal、hybrid 或专用 engine 在何种 workload 下值得其维护成本；**证据不足**是跨 backend 事务一致性、完整删除、灾难恢复、独立采用与成本排名。通用 SQL/WAL/FTS/ANN primitive 本身成熟，但“agent-memory database contract”仍缺标准化、执行对照和失败证据。（支持 claims：REP-C11、REP-C12、REP-C14、REP-C17、REP-C18、REP-C22、FND-C17；支持 evidence：REP-V21、REP-V22、REP-V23、REP-V24、REP-V27、REP-V28、REP-V33、REP-V34、REP-V36、REP-V37、REP-V43、REP-V44、FND-EV32、FND-EV33；反对/限定 claims：REP-C03、REP-C19；反对/限定 evidence：REP-V05、REP-V06、REP-V38、REP-V39。）

工程决策应先写出 object/revision/scope/delete/rebuild contract，再选 backend；PoC 必须用 pinned schema 和 matched workload 做 fault injection 与 budgeted retrieval，不能只跑 vendor demo。若公开、独立、同硬件同模型同数据的比较表明单一 flat store 在 relation/temporal/conflict、correction、delete、recovery 与成本上持续等同或优于 typed multi-index 方案，则可反转本稿的分层建议；在此之前，只能按工作负载裁剪 projection，不能移除权威状态边界。（支持 claims：REP-C02、REP-C03、REP-C05、REP-C06、FND-C17、BEN-C25；支持 evidence：REP-V03、REP-V04、REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、FND-EV32、FND-EV33、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

## 已命名缺口

- `GAP-CNS-03`：缺 relation/temporal/conflict-heavy tasks 上 flat、hybrid、graph、bitemporal、active navigation 的 matched candidate/token/reader/maintenance-cost 对照。
- `GAP-CNS-10`：selected repositories 未执行，缺 pinned install/test、release/issue health、dependency/lock-in、license 与 independent deployment evidence。
- `GAP-CNS-12`：缺同时覆盖 write/retrieve/consolidate/delete/repair/action 的 model call、token、latency、bytes/revision、rebuild、audit retention 与 human review 测量。

这三个缺口共同阻止“最佳 backend”排名：下一轮应以可重放 workload + failure injection + cost ledger 为主，而不是继续堆积相似 vector/graph 项目简介。（支持 claims：REP-C17、REP-C19、BEN-C22、BEN-C25；支持 evidence：REP-V33、REP-V34、REP-V38、REP-V39、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

## 实际饱和轮次

`SAT-CL-MM-C02` 在 `2026-08-10T10:54:07Z` 记录为 `saturated`：已消费 10 个 targeted queries、14 个 deep-verified memberships；最终可回放轮次为 `FM-EV-CLUSTER-MM-C02-11` 与 `FM-EV-CLUSTER-MM-C02-12`。停止规则是连续两个 breadth wave 不再增加 first-order leaf，且 targeted deep/negative/implementation follow-up 不再改变边界或决策命题；三个 residual gaps 仍保留。饱和指本轮 map boundary 稳定，不等于 backend 对照、运行验证或生产成熟度已经完成。（过程记录：SAT-CL-MM-C02；支持 claims：none；支持 evidence：none；反对/限定 claims：none；反对/限定 evidence：none。）


## 补充可审计工程判断

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

A-Mem's README documents note generation with structured attributes, historical-link analysis, and updates to contextual representations; its evaluation command exposes retrieve_k as a tunable parameter.
<!-- claim:REP-C10 -->

Supermemory documents a combined profile/episodic service with fact extraction, temporal updates and forgetting, plus hybrid search over knowledge and personalized context.
<!-- claim:REP-C13 -->

<!-- synthesis:CLY-C02 claims:REP-C10,REP-C11,REP-C12,REP-C13,REP-C14,REP-C19,REP-C22 clusters:MM-C02 -->
