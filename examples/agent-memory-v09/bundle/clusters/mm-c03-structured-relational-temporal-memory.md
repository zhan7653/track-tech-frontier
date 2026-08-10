# MM-C03 — Structured, Relational & Temporal Memory：深度报告

> 状态：final cluster report；证据截止 `2026-08-10`。本稿只讨论 graph、relational、temporal/bitemporal、versioned 与 conflict-aware representation；只有 flat similarity 的 generic retrieval 属 MM-C04 或普通 RAG，不因项目自称 memory graph 自动纳入本簇结论。

## 结论先行

关系、时间、版本和冲突密集的 Agent Memory 需要比“chunk + embedding + top-k”更明确的对象与访问语义：至少能区分 raw evidence、atomic fact/event/profile、stable identity 与 revision、valid time 与 transaction time、current/history/all-version view，以及 typed relation/causal edge。结构化表示的价值是保留可查询约束与演化路径，不是把 graph 当成真相来源；在局部事实 QA、宽松 raw-evidence budget 或构建过程丢失关键 span 时，flat/raw baseline 可以同样好甚至更好。**判断：mixed/条件共识；信心 medium；成熟度为“表示模式清晰，近期收益证据不稳定且以预印本/未执行仓库为主”。**（支持 claims：REP-C01、REP-C02、REP-C08、REP-C10、REP-C11、REP-C14、REP-C16、REP-C22、FND-C09；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、REP-V15、REP-V16、REP-V19、REP-V20、REP-V21、REP-V22、REP-V27、REP-V28、REP-V31、REP-V32、REP-V43、REP-V44、FND-EV16、FND-EV17；反对/限定 claims：REP-C03、REP-C06；反对/限定 evidence：REP-V05、REP-V06、REP-V11、REP-V12。）

本簇边界由“representation 能否回答 relation/time/version/conflict 问题”决定，而不是 backend 标签。graph 可表达 entity/relation/traversal，relational tables 可表达 typed current/profile，bitemporal schema 可表达 as-of/history，version chain 可表达 supersession；同一系统可以组合这些形式。相反，只有 vector similarity、没有 cross-session revision/time/scope 的检索器，即使返回关联内容，也不提供本簇所需保证。（支持 claims：REP-C02、REP-C11、REP-C14、REP-C16、REP-C22；支持 evidence：REP-V03、REP-V04、REP-V21、REP-V22、REP-V27、REP-V28、REP-V31、REP-V32、REP-V43、REP-V44；反对/限定 claims：REP-C09；反对/限定 evidence：REP-V17、REP-V18。）

## 分层证据选择

| 证据层 | 代表性条目与时间 | 本稿使用方式 | 支持 claim / evidence | 反对或限定 claim / evidence |
|---|---|---|---|---|
| foundational external memory | MemoryBank，2024-02-01 | conversation、summary、evolving profile 说明长期 memory 已隐含不同对象与更新 | FND-C05 / FND-EV08、FND-EV09 | none / none |
| structured-memory lineage | A-MEM，2025-10-08；Hindsight，2025-12-14 | structured note/link/update 与 world/experience/entity/belief networks 把 flat store 扩成可演化结构 | FND-C09、REP-C08、REP-C10 / FND-EV16、FND-EV17、REP-V15、REP-V16、REP-V19、REP-V20 | FND-C10 / FND-EV18、FND-EV19 |
| recent paper | AtomMem，2026-06-18；bitemporal store，2026-07-29 | atomic fact→event/profile/graph；identity/version 与 valid/transaction time | REP-C01、REP-C02 / REP-V01、REP-V02、REP-V03、REP-V04 | REP-C03 / REP-V05、REP-V06 |
| fixed-commit GitHub | causal-memory@`054a…`，2026-08-10 | raw log、atomic fact、decision→outcome edge、RRF 与 spreading activation 的实现样本；不外推运行效果 | PRJ-A003、PRJ-I003、PRJ-C003 / PRJ-AE003-01、PRJ-IE003-01、PRJ-E003 | PRJ-M003 / PRJ-ME003 |
| adjacent repository patterns | Cognee、MemMachine、HippoRAG，打开于 2026-08-10 | graph/vector/ontology、episodic graph/SQL profile、KG+PPR 三种工程形状 | REP-C11、REP-C14、REP-C16 / REP-V21、REP-V22、REP-V27、REP-V28、REP-V31、REP-V32 | REP-C19 / REP-V38、REP-V39 |
| benchmark/negative | LongMemEval；MemoryAgentBench；LightMem reproduction；bitemporal sample | 分离 long-range/update/selective-forget 与 candidate loss、post-filter dilution、raw/constructed reversal | BEN-C02、BEN-C03、REP-C03、REP-C05、REP-C06 / BEN-EV03、BEN-EV05、REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12 | BEN-C22 / BEN-EV43、BEN-EV44 |

证据组合刻意保留“结构能表达什么”和“结构是否提升任务结果”的差异。paper/README 可以支持对象、操作和算法形状；只有 matched protocol 才能支持收益。当前选中 paper stratum 很新但不成熟：十篇均为 2026 arXiv preprint、八篇落在 rolling-90d；selected repositories 未执行，canonical Graphiti entity 还缺失。因此趋势信号强，成熟度证据弱。（支持 claims：REP-C19、REP-C20、REP-C21；支持 evidence：REP-V38、REP-V39、REP-V40、REP-V41、REP-V42；反对/限定 claims：none；反对/限定 evidence：none。）

## foundational → recent 的演化脉络

最早的 external memory 已不只是单一记录：MemoryBank 同时保存 conversation、event summary 与 evolving user portrait，并区分 storage/retrieval/updater。A-MEM 随后让 note 带 structured attributes、与历史动态连边，并在新 memory 到来时更新旧 contextual representation；Hindsight 又把 world facts、agent experiences、entity summaries 与 evolving beliefs 分成四个 logical network。演化方向是从“可检索文本”转向“有类型、关系和演化规则的状态”，但这些架构描述本身不提供通用 graph 优势证明。（支持 claims：FND-C05、FND-C09、REP-C08、REP-C10；支持 evidence：FND-EV08、FND-EV09、FND-EV16、FND-EV17、REP-V15、REP-V16、REP-V19、REP-V20；反对/限定 claims：FND-C10；反对/限定 evidence：FND-EV18、FND-EV19。）

2026 的工作进一步拆开 granularity 与 time。AtomMem 从 selective atomic fact 生成 hierarchical event、temporal profile 和 associative graph；bitemporal store 将 identity 与 content version、valid time 与 transaction time分离，以避免 overwrite history；MemTxn 把 temporal version selection 放入 transaction boundary。这里形成的工程共识是“事实身份、内容版本和可见时间不能混成同一字段”，争议则是具体 graph-native/bitemporal 实现是否值得其构建、过滤和维护成本。（支持 claims：REP-C01、REP-C02、FND-C17、REP-C22；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、FND-EV32、FND-EV33、REP-V43、REP-V44；反对/限定 claims：REP-C03；反对/限定 evidence：REP-V05、REP-V06。）

## 机制与目标架构

建议先定义 memory object ontology，再决定物理图或表：`Evidence` 表示原始 utterance/tool outcome/source；`Fact/Claim` 表示可争议语义；`Event` 表示带参与者与有效时间的发生；`Profile/Belief` 表示会演化的聚合状态；`Entity` 提供稳定身份；`Relation/CausalEdge` 提供 typed link；`Revision` 连接 predecessor/superseder；`ControlMetadata` 保存 scope、authority、confidence 与 mutation receipt。同一 evidence 可导出多个 object，但每个 derived object 都必须反向引用 source span，graph edge 不能脱离其证据链。（支持 claims：REP-C01、REP-C02、REP-C08、REP-C14、FND-C17、OPS-C12、OPS-C13；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、REP-V15、REP-V16、REP-V27、REP-V28、FND-EV32、FND-EV33、OPS-J12、OPS-J13；反对/限定 claims：none；反对/限定 evidence：none。）

时间模型至少要区分 event/valid time 与 ingest/transaction time，并提供 `current`、`as-of(valid)`、`as-known-at(transaction)`、`history`、`all-conflicts` 等读取视图。更新创建新 revision 并关闭或限定旧 version 的可见区间，而不是物理覆盖；correction、late-arriving evidence 与 retrospective edit 因而可以被区分。bitemporal schema 只是实现这种语义的一种方式，relational version table 或 event sourcing 也可满足契约；关键是 time/version 能穿过 candidate generation 与 context compilation，而非仅存于后台字段。（支持 claims：REP-C02、FND-C17、REP-C22、OPS-C17；支持 evidence：REP-V03、REP-V04、FND-EV32、FND-EV33、REP-V43、REP-V44、OPS-J17；反对/限定 claims：REP-C03；反对/限定 evidence：REP-V05、REP-V06。）

关系层应把 edge type、direction、source、validity 和 revision 暴露给 traversal，而不是仅把共现转成无类型邻边。对 causal memory，decision→outcome edge 与普通 semantic similarity 不同；对 profile/entity，ownership、preference、membership 与 contradiction 也不应共用一个 score。Graph/PPR/spreading activation 可以扩大多跳候选，但最终证据仍需回到 source、scope、time 和 budget；graph 是 access path，不是 truth oracle。（支持 claims：REP-C11、REP-C16、PRJ-A003、OPS-C13、REP-C22；支持 evidence：REP-V21、REP-V22、REP-V31、REP-V32、PRJ-AE003-01、OPS-J13、REP-V43、REP-V44；反对/限定 claims：REP-C07；反对/限定 evidence：REP-V13、REP-V14。）

## write–manage–read–action 数据流与算法

**Write。** raw session/tool event 先落审计层；extractor 产生 candidate fact/event/entity/relation，entity resolver 选择 stable identity，temporal resolver 标记 valid/transaction time，conflict detector 对比 current/history，最后 admission gate 决定 commit、link 或保留未决。AtomMem 的 fact→event/profile/graph 与 causal-memory 的 raw log→fact→decision/outcome edge 提供两种具体形状；两者都支持“原文与召回结构分层”，但本轮没有执行 extraction accuracy 或 recovery。（支持 claims：REP-C01、PRJ-A003、PRJ-I003、FND-C17；支持 evidence：REP-V01、REP-V02、PRJ-AE003-01、PRJ-IE003-01、FND-EV32、FND-EV33；反对/限定 claims：REP-C19；反对/限定 evidence：REP-V38、REP-V39。）

**Manage。** 新 evidence 可以 append、merge、supersede、contradict 或 revoke 旧 object；consolidation 可生成 event/profile/belief，但必须保留 derivation 与 rollback link。A-MEM 的历史链接/上下文更新、Hindsight 的 retain/reflect、bitemporal revision 和 ForgetEval 的 supersede/release/purge 说明管理操作远超简单 upsert；同时也暴露 false merge、错误 entity resolution、错误 temporal closure 与删除派生图边的风险。（支持 claims：FND-C09、REP-C08、REP-C02、FND-C21；支持 evidence：FND-EV16、FND-EV17、REP-V15、REP-V16、REP-V03、REP-V04、FND-EV40、FND-EV41；反对/限定 claims：REP-C03；反对/限定 evidence：REP-V05、REP-V06。）

**Read。** query planner 先解析 scope、entity、relation、time、history/conflict intent，再选择 lexical/vector/SQL/graph/temporal route；候选融合后先验证 time/version/source，随后 rerank，最后在 token budget 内编译 evidence packet。若先 ANN top-k 再 post-filter，合法 temporal candidate 可能被稀释；若 graph expansion 无 budget，候选噪声和维护成本会不可控；若 constructed memory 覆盖 raw source，answer-relevant span 可能已经丢失。因此 protocol 要记录每个阶段的 candidate set 与 loss。（支持 claims：REP-C03、REP-C05、REP-C06、REP-C16、REP-C18、REP-C22；支持 evidence：REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V31、REP-V32、REP-V36、REP-V37、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

**Action。** structured state 在驱动 tool/action 前需把“current fact”“historical fact”“conflicting claim”“inferred relation”明确区分，并由 action layer按当前 authority 选择；不能让 graph proximity 自动升级为授权事实。行动 outcome 应写回为独立 Evidence/Event，再经过同一 resolution pipeline，而非直接强化原 relation。这样可以测试结构是否真的改善 action success，也可定位错误是 edge construction、time view、retrieval 还是 policy use。（支持 claims：BEN-C07、BEN-C08、BEN-C12、BEN-C25、REP-C07、OPS-C07；支持 evidence：BEN-EV13、BEN-EV14、BEN-EV15、BEN-EV16、BEN-EV23、BEN-EV24、BEN-EV49、BEN-EV50、REP-V13、REP-V14、OPS-J07；反对/限定 claims：BEN-C22；反对/限定 evidence：BEN-EV43、BEN-EV44。）

## GitHub 实现模式与集成

causal-memory@`054af…` 是本簇最直接的 fixed-commit 实现样本：SQLite 同时承载 raw session logs、atomic facts 与 decision→outcome causal edges；write gatekeeping 分开审计原文和召回层，distill/consolidation 构造 facts/edges，read 以 BM25 与 optional embedding 做 RRF，并可运行 typed spreading activation。其模式支持“权威原文 + typed relational projection + multi-route retrieval”，但该 SHA 只有 MCP stdio，HTTP 未实现；local embedding 还需 ONNX runtime/model download，README benchmark/test 声明未执行，也无独立生产采用证据。（支持 claims：PRJ-A003、PRJ-I003、PRJ-C003；支持 evidence：PRJ-AE003-01、PRJ-AE003-02、PRJ-AE003-03、PRJ-IE003-01、PRJ-IE003-02、PRJ-E003；反对/限定 claims：PRJ-M003；反对/限定 evidence：PRJ-ME003。）

Cognee、MemMachine 与 HippoRAG 展示另外三种集成面：vector+graph+ontology 的 self-hosted pipeline、episodic graph/SQL profile/working memory 分层、以及 `index(docs) → graph/PPR → rag_qa`。这些实现证明工程社区正在把 structured memory 拆成不同 object 与 route，却不能互相替代 benchmark：ontology generation、profile SQL、PPR graph 的任务、写入成本与生命周期不同，且 v09 未运行其 tests/integration。应把它们当 design pattern 库，而不是按 stars 或 README 数字做排行榜。（支持 claims：REP-C11、REP-C14、REP-C16、REP-C19；支持 evidence：REP-V21、REP-V22、REP-V27、REP-V28、REP-V31、REP-V32、REP-V38、REP-V39；反对/限定 claims：none；反对/限定 evidence：none。）

集成层需要固定 canonical ID、edge/revision schema、time semantics 与 source pointer；MCP/SDK/HTTP 只是 transport。若现有系统以 SQL 为权威，可将 graph/PPR 作为 projection；若 graph-native 为权威，仍要给 derived summary/profile 留 provenance 和 version；若只需局部事实 QA，可用 relational/lexical/hybrid baseline，避免引入 graph maintenance。Graphiti 当前只在 mapped corpus 中出现引用/集成候选，缺 canonical getzep/graphiti entity，所以本稿不据其名声补写工程结论。（支持 claims：REP-C02、REP-C20、REP-C22、PRJ-I003；支持 evidence：REP-V03、REP-V04、REP-V40、REP-V43、REP-V44、PRJ-IE003-01、PRJ-IE003-02；反对/限定 claims：none；反对/限定 evidence：none。）

## 成本与复杂度

structured memory 的成本来自多阶段而非单一 graph query：write 侧有抽取、entity resolution、edge typing、conflict/time resolution 与 version fan-out；manage 侧有 merge/supersede、profile/event consolidation、orphan edge cleanup 与 reindex；read 侧有 query intent parsing、multi-route candidate、graph traversal/post-filter、rerank 和 source hydration；storage 侧有 raw evidence、object/history、edge 与多索引副本。现有证据确认这些机制存在，却没有 matched maintenance cost，因此不能以更高结构度推导更高性价比。（支持 claims：REP-C01、REP-C02、FND-C09、REP-C16、FND-C19、FND-C20；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、FND-EV16、FND-EV17、REP-V31、REP-V32、FND-EV36、FND-EV37、FND-EV38、FND-EV39；反对/限定 claims：REP-C17；反对/限定 evidence：REP-V33、REP-V34。）

成本应与“保留了什么语义”一起报告：bytes/revision、facts/event、edges/entity、source-span coverage、valid/history query latency、candidate depth、graph expansions、token budget、rebuild 和 human correction。严格 token budget 下 structured/compressed memory 可能减少 context，宽松 budget 下 raw evidence 可能保留更多细节；因此 storage saving 与 answer quality 是联合曲线，不是一个脱离 protocol 的单点。（支持 claims：REP-C05、REP-C06、REP-C18、FND-C19；支持 evidence：REP-V09、REP-V10、REP-V11、REP-V12、REP-V36、REP-V37、FND-EV36、FND-EV37；反对/限定 claims：none；反对/限定 evidence：none。）

## Benchmark protocol 与可比性

本簇最小 benchmark matrix 应分别含：局部事实、entity relation、多跳 relation、knowledge update、as-of/current/history、late-arriving evidence、contradiction/supersession、causal decision→outcome、selective forgetting 与 action-use；每题保存 gold source span、gold object/revision/time view。系统比较时固定 raw inputs、extractor/LLM、backend、retriever、candidate depth、token budget、reader/judge，并分别报告 object/edge extraction、source coverage、candidate recall、time/conflict correctness、final answer/action、latency 与 maintenance cost。（支持 claims：BEN-C02、BEN-C03、BEN-C22、BEN-C25、REP-C22；支持 evidence：BEN-EV03、BEN-EV04、BEN-EV05、BEN-EV06、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

对照组至少包括 raw-turn lexical/vector、flat hybrid、typed relational、graph traversal、bitemporal 和结构+raw fallback；不允许各系统使用不同 k/token/reader。bitemporal paper 的 60-question sample 同时出现 knowledge-update gain 与 temporal-reasoning drop，LightMem reproduction 又显示 retriever 选择与 matched depth 可反转 raw/constructed 排名，这两组负证据要求报告 oracle recall、source-span loss 和 filter placement，而不是只报最终平均分。（支持 claims：REP-C03、REP-C05、REP-C06、REP-C17、REP-C18；支持 evidence：REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V33、REP-V34、REP-V36、REP-V37；反对/限定 claims：none；反对/限定 evidence：none。）

## 限制、失败与替代方案

主要失败包括：LLM 抽取遗漏 source detail、entity resolution 把不同人合并、edge 类型或方向错误、valid/transaction time 混淆、late evidence 意外覆盖当前状态、graph expansion 放大污染、post-filter 稀释合法候选、profile consolidation 固化错误，以及删除 object 后遗留 derived edge。trustworthy-search 还指出语义相关内容可能在当前 domain/context 不适用，因此结构更丰富并不自动更安全。（支持 claims：REP-C03、REP-C06、REP-C07、OPS-C01、OPS-C07、OPS-C13；支持 evidence：REP-V05、REP-V06、REP-V11、REP-V12、REP-V13、REP-V14、OPS-J01、OPS-J07、OPS-J13；反对/限定 claims：none；反对/限定 evidence：none。）

替代路线按需求裁剪：局部事实与低更新频率可用 raw/flat hybrid；需要当前/历史但关系简单可用 relational version table；需要 as-of/late arrival 采用 bitemporal contract；需要多跳 entity/causal navigation 才引入 typed graph；严格 token budget 可使用 structured summary，但保留 raw fallback 与 source span。没有证据支持“graph everywhere”，也没有证据支持“flat everywhere”；正确比较单位是任务语义 + matched protocol + maintenance cost。（支持 claims：REP-C02、REP-C03、REP-C05、REP-C06、REP-C16、REP-C22；支持 evidence：REP-V03、REP-V04、REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V31、REP-V32、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

## 共识、分歧、成熟度与决策含义

**共识**是 scope、provenance、time/version 与 retrieval budget 必须穿过 representation-to-context path；**条件共识**是 relation/temporal/conflict-heavy task 通常需要超越 flat top-k；**争议**是 graph-native、bitemporal、constructed memory 的通用收益与最佳算法；**证据不足**是近期 preprint 的跨 backend 复现、canonical Graphiti 工程结论、selected repo 的执行/采用与端到端成本。typed object 和多 route 是中等成熟的工程模式，bitemporal/transaction 跨 backend 标准、active graph navigation 与可靠自动 consolidation 仍偏早期。（支持 claims：REP-C01、REP-C02、REP-C20、REP-C21、REP-C22、FND-C17；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、REP-V40、REP-V41、REP-V42、REP-V43、REP-V44、FND-EV32、FND-EV33；反对/限定 claims：REP-C03、REP-C06、REP-C19；反对/限定 evidence：REP-V05、REP-V06、REP-V11、REP-V12、REP-V38、REP-V39。）

采用决策应先列目标 query semantics，再选最小 representation：若没有 as-of/history/conflict/multi-hop 需求，不为 graph 付费；若有，则用 gold source/time/revision 和 fault cases 做 matched evaluation，并保留 raw evidence fallback。反转“结构化通常有必要”的条件是：多个公开 backend、相同 input/extractor/retriever/reader/budget 的独立结果持续显示 flat retrieval 在 relation/temporal/conflict tasks 上等同或更好且维护成本更低；升级为强共识则需结构化方案跨 backend 稳定领先并经 recovery/delete 验证。（支持 claims：REP-C03、REP-C05、REP-C06、REP-C17、REP-C22；支持 evidence：REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V33、REP-V34、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

## 已命名缺口

- `GAP-CNS-03`：缺 flat、hybrid、graph、bitemporal、active navigation 在 relation/temporal/conflict-heavy tasks 上的 matched candidate/token/reader/maintenance-cost 对照。
- `GAP-CNS-04`：LightMem 揭示 raw/constructed reversal，但缺跨多系统 source-span coverage、oracle recall 与 matched-budget reproduction。
- `GAP-CNS-10`：selected repositories 未做 pinned execution、maintenance/license 与 independent deployment 验证。
- `GAP-CNS-12`：缺 write/retrieve/consolidate/delete/repair/action 的全链成本、latency、bytes/revisions、rebuild 与人工负担。
- `GAP-CNS-13`：canonical getzep/graphiti entity 尚未重建 identity、rename/transfer、commit、release 与 paper relation。

下一轮不是再增加 graph 项目列表，而是修复 canonical entity、执行 causal/graph/bitemporal representative，并在同一 raw evidence 与 protocol 下测 source loss、temporal filter、maintenance 和 action outcome。（支持 claims：REP-C03、REP-C19、REP-C20、BEN-C22；支持 evidence：REP-V05、REP-V06、REP-V38、REP-V39、REP-V40、BEN-EV43、BEN-EV44；反对/限定 claims：none；反对/限定 evidence：none。）

## 实际饱和轮次

`SAT-CL-MM-C03` 在 `2026-08-10T10:54:07Z` 记录为 `saturated`：已消费 13 个 targeted queries、25 个 deep-verified memberships；最终可回放轮次为 `FM-EV-CLUSTER-MM-C03-11` 与 `FM-EV-CLUSTER-MM-C03-12`。停止规则是连续两个 breadth wave 不再增加 first-order leaf，且 targeted deep/negative/implementation follow-up 不再改变边界或决策命题；五个 residual gaps 继续保留。饱和仅代表本次证据地图的 first-order leaf 与命题边界稳定，不代表结构化路线的效果、成本或成熟度已经定论。（过程记录：SAT-CL-MM-C03；支持 claims：none；支持 evidence：none；反对/限定 claims：none；反对/限定 evidence：none。）


<!-- synthesis:CLY-C03 claims:REP-C01,REP-C02,REP-C03,REP-C07,REP-C22 clusters:MM-C03 -->
