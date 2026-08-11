# MM-C04 — Retrieval, Ranking & Active Navigation：深度报告

> 状态：final cluster report；证据截止 `2026-08-10`。本稿讨论 cross-session memory 的 selection、ranking、query-adaptive retrieval、structured navigation 与 context compilation；没有 lifecycle/scope 的 generic RAG 检索不纳入本簇工程结论。

## 结论先行

可靠的 memory read path 不应等同于一次 `top_k` 调用，而应显式分为：`hard scope/time/authorization filter → multi-route candidate generation → freshness/authority/support/conflict/cost reranking → budgeted context compilation → action-use trace`。hybrid、graph、intent planning 或 re-retrieve 的价值只有在 matched protocol 中记录 candidate loss、预算、stale/conflicting evidence、rank trace 和最终 action-use 后才成立；“更多 route/更大 k/更复杂 memory”都不是独立质量证明。**判断：mixed/条件共识；信心 medium-high；成熟度为“hybrid pipeline 中等，trust-aware/active navigation 与统一协议偏早期”。**（支持 claims：REP-C04、REP-C07、REP-C12、REP-C16、REP-C18、REP-C22、FND-C14、FND-C15、BEN-C07、BEN-C25；支持 evidence：REP-V07、REP-V08、REP-V13、REP-V14、REP-V23、REP-V24、REP-V31、REP-V32、REP-V36、REP-V37、REP-V43、REP-V44、FND-EV26、FND-EV27、FND-EV28、FND-EV29、BEN-EV13、BEN-EV14、BEN-EV49、BEN-EV50；反对/限定 claims：REP-C05、REP-C06；反对/限定 evidence：REP-V09、REP-V10、REP-V11、REP-V12。）

边界上，本簇从 query intent 到 compiled evidence/action trace，依赖但不拥有 MM-C02 的 indexes，也不拥有 MM-C03 的 graph/time representation，更不负责 MM-C05 的 durable mutation。它必须消费 scope、version、time、provenance 与 budget，并把这些信息带到 prompt/tool decision；如果 retrieval 只返回相似文本而丢掉这些字段，后面的 LLM 无法可靠重建权限或历史。（支持 claims：REP-C07、REP-C18、REP-C22、OPS-C19、FND-C23；支持 evidence：REP-V13、REP-V14、REP-V36、REP-V37、REP-V43、REP-V44、OPS-J19、FND-EV44、FND-EV45、FND-EV46；反对/限定 claims：none；反对/限定 evidence：none。）

## 分层证据选择

| 证据层 | 代表性条目与时间 | 本稿使用方式 | 支持 claim / evidence | 反对或限定 claim / evidence |
|---|---|---|---|---|
| foundational architecture | MemGPT，2024-02-12 | tier movement/interrupt 表明 retrieval 是 context-control 决策而非独立搜索 | FND-C03、FND-C23 / FND-EV04、FND-EV44 | none / none |
| field baseline | Hindsight characterization，2025-12-14；A-MEM，2025-10-08 | top-k prompt injection 是常见基线；structured note/link 与 tunable k 是演化起点 | REP-C09、FND-C09、REP-C10 / REP-V17、REP-V18、FND-EV16、FND-EV17、REP-V19、REP-V20 | FND-C10 / FND-EV18、FND-EV19 |
| recent algorithm | SimpleMem，2026-01-29；HippoRAG repo，2026-08-10；MemCon，2026-07-15 | intent-aware planning、graph/PPR、retrieve/re-retrieve policy 三种 query-adaptive/active 路径 | REP-C04、REP-C16、FND-C14、FND-C15 / REP-V07、REP-V08、REP-V31、REP-V32、FND-EV26、FND-EV27、FND-EV28、FND-EV29 | FND-C16 / FND-EV30、FND-EV31 |
| fixed-commit GitHub | scope-recall-hermes@`867b…`，2026-08-08 | journal-first + lexical/vector/graph/freshness fusion 的工程模式，只证明静态实现 | PRJ-A004、PRJ-I004、PRJ-C004 / PRJ-AE004-01、PRJ-IE004-01、PRJ-E004 | PRJ-M004 / PRJ-ME004 |
| benchmark families | LoCoMo、LongMemEval、MemoryAgentBench、Mem2ActBench、MemoryArena | 从 QA 扩到 incremental、tool grounding、interdependent action；family 不可合并排名 | BEN-C01、BEN-C02、BEN-C03、BEN-C07、BEN-C12、BEN-C22 / BEN-EV01、BEN-EV03、BEN-EV05、BEN-EV13、BEN-EV23、BEN-EV43、BEN-EV44 | none / none |
| negative/security | LightMem reproduction，2026-07-31；trustworthy search，2026-06-04；query-only attacks | retriever/budget 可反转结果；相似但不适当的 memory 与 query injection 都会穿过 read path | REP-C05、REP-C06、REP-C07、OPS-C04、OPS-C10 / REP-V09、REP-V10、REP-V11、REP-V12、REP-V13、REP-V14、OPS-J04、OPS-J10 | none / none |

这些层次回答不同问题：paper 说明机制，fixed-commit repo 说明真实 data flow 与依赖，benchmark 定义可比较单位，negative/security 证据寻找 reversal 和 failure。Stars、recent creation/push 与 commit count 只能触发深检，不能证明 growth、质量、成熟度或采用；本稿所有仓库成熟度都停留在静态检查边界。（支持 claims：PRJ-C004、PRJ-M004、REP-C19、EXP-C22、BEN-C23；支持 evidence：PRJ-E004、PRJ-ME004、REP-V38、REP-V39、EXP-V43、EXP-V44、BEN-EV45、BEN-EV46；反对/限定 claims：none；反对/限定 evidence：none。）

## foundational → recent 的演化脉络

第一代 read path 解决“有限 context 中取什么”：MemGPT 用 tier movement 与 interrupt 管理 context，常见 external-memory 系统则抽 salient snippet、写 vector/graph，再 top-k 注入 prompt。这个范式建立了 memory retrieval 的基本闭环，但往往把 scope、time、version、construction loss 与 token budget折叠进一个最终 QA 分数，因而无法说明到底哪一步有效。（支持 claims：FND-C03、FND-C23、REP-C09、REP-C17、REP-C18；支持 evidence：FND-EV04、FND-EV44、REP-V17、REP-V18、REP-V33、REP-V34、REP-V36、REP-V37；反对/限定 claims：none；反对/限定 evidence：none。）

第二代路线引入 multi-signal 与 query planning：Mem0 文档融合 semantic、BM25、entity 并另设 temporal ranking；A-MEM 让 retrieve_k 可调并利用 structured links；SimpleMem 把 semantic compression、online synthesis 与 intent-aware retrieval planning 串联；HippoRAG 用 knowledge graph + Personalized PageRank 扩展关联候选。这些机制共同表明“候选生成和排序应可组合”，但它们的 input construction、k、token budget、reader 和任务不同，不能从各自报告数字推导统一胜负。（支持 claims：REP-C04、REP-C10、REP-C12、REP-C16、REP-C17、REP-C18；支持 evidence：REP-V07、REP-V08、REP-V19、REP-V20、REP-V23、REP-V24、REP-V31、REP-V32、REP-V33、REP-V34、REP-V36、REP-V37；反对/限定 claims：none；反对/限定 evidence：none。）

第三代尝试 active navigation/control：MemCon 将 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 置于在线 policy；其作者描述的 contextual bandit/UCB 与 binary feedback 说明 navigation 可由任务反馈自适应，而不必固定一次 top-k。当前证据仍是作者机制/结果边界，缺跨 backend 的独立匹配复现；因此 active retrieval 是值得跟踪的近期趋势，尚不能列为生产默认。（支持 claims：FND-C14、FND-C15；支持 evidence：FND-EV26、FND-EV27、FND-EV28、FND-EV29；反对/限定 claims：FND-C16；反对/限定 evidence：FND-EV30、FND-EV31。）

## 机制与目标架构

建议把 read path 实现成可观察的 staged planner。Stage 0 解析 principal、tenant/user/agent/run scope、query intent、time view、action risk 和预算；Stage 1 在访问 index 前做 hard authorization/time/current-history filter；Stage 2 选择 lexical、semantic、entity、graph、temporal 或 raw-journal routes；Stage 3 对 route candidates 去重并保留每路 score/source；Stage 4 用 relevance、freshness、authority、source support、conflict、risk、cost rerank；Stage 5 编译 raw span、typed state、版本/冲突说明到 token/tool budget；Stage 6 保存 rank/compile/action trace。该拆分的目的不是增加组件，而是让 candidate loss 与越权发生在哪一层可被定位。（支持 claims：REP-C07、REP-C12、REP-C18、REP-C22、OPS-C19、BEN-C25；支持 evidence：REP-V13、REP-V14、REP-V23、REP-V24、REP-V36、REP-V37、REP-V43、REP-V44、OPS-J19、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

hard filter 必须早于语义召回和 prompt 注入：tenant/scope、revocation、valid/current view、source policy 与 action risk 不应由 LLM 在看到越权内容后再“自觉忽略”。trustworthy-search 将 retrieval 本身定义为 trust boundary，产品文档也把 scope/filter 作为明确接口；query-only injection 进一步说明攻击者不必拥有写 API，也能利用 observation/query 影响候选。因此 authorization、auditing 和 source policy 是 rank pipeline 的输入，不是后处理说明。（支持 claims：REP-C07、OPS-C04、OPS-C10、OPS-C19、OPS-C26；支持 evidence：REP-V13、REP-V14、OPS-J04、OPS-J10、OPS-J19、OPS-J26；反对/限定 claims：none；反对/限定 evidence：none。）

candidate fusion 不能只把不同 score 直接相加。实现需要先记录 route-specific ranks，再用 normalization、RRF 或 learned reranker 合并，同时保留 duplicates、conflicts 与 provenance；graph/PPR 或 spreading activation 适合多跳扩展，lexical 适合精确 token，vector 适合语义近邻，entity/time route 适合硬约束。v09 的工程证据支持这些 route 的存在，但没有一个 matched experiment 证明固定融合公式普适，因此 fusion policy 应可配置、可回放、可按 query class 对照。（支持 claims：REP-C12、REP-C16、PRJ-A003、PRJ-A004、REP-C17；支持 evidence：REP-V23、REP-V24、REP-V31、REP-V32、PRJ-AE003-01、PRJ-AE004-01、REP-V33、REP-V34；反对/限定 claims：REP-C05、REP-C06；反对/限定 evidence：REP-V09、REP-V10、REP-V11、REP-V12。）

context compiler 是 read path 的独立层：它决定 raw span 与 constructed memory 的比例、每条 evidence 的 token allocation、是否展示冲突和为何截断。严格预算下压缩/constructed memory 可能占优，matched depth/宽松预算下 raw-turn 可能保留更多 answer-relevant information；因此 compiler 应支持 raw fallback、source-span coverage 和 budget sweep，而不是把 representation loss 隐藏在“检索成功”后。（支持 claims：REP-C04、REP-C05、REP-C06、REP-C18、REP-C22；支持 evidence：REP-V07、REP-V08、REP-V09、REP-V10、REP-V11、REP-V12、REP-V36、REP-V37、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

## write–manage–read–action 数据流

**Write。** 虽然本簇聚焦 read，但 index key 必须在写入时携带 stable object/revision、scope、source、event/transaction time、lexical fields、embedding version 与 graph/entity links；否则 read path 无法早期过滤或解释 stale candidate。raw evidence 与 constructed object 应分别可检索并互相指回，给 oracle/source-loss 分析留下基准。（支持 claims：REP-C01、REP-C02、REP-C22、FND-C17；支持 evidence：REP-V01、REP-V02、REP-V03、REP-V04、REP-V43、REP-V44、FND-EV32、FND-EV33；反对/限定 claims：none；反对/限定 evidence：none。）

**Manage。** embedding/ranker/index schema、watermark 与 policy 都需 version；supersede/revoke/forget 要使旧候选在下一次 query 的 hard filter 中不可见，并触发 projection rebuild 或 tombstone propagation。controller 若允许 re-retrieve，应把第一次候选、反馈、第二次 query/预算和停止原因写入 trace；否则 active navigation 只增加模型/工具调用而无法归因。（支持 claims：FND-C14、FND-C15、FND-C17、FND-C21、REP-C18；支持 evidence：FND-EV26、FND-EV27、FND-EV28、FND-EV29、FND-EV32、FND-EV33、FND-EV40、FND-EV41、REP-V36、REP-V37；反对/限定 claims：FND-C16；反对/限定 evidence：FND-EV30、FND-EV31。）

**Read。** planner 分配 route/candidate/token/tool budget，hard filter 后产生候选并保存每阶段集合，reranker 输出 score breakdown，compiler 生成带 source/revision/time/conflict 的 evidence packet。指标必须同时含 candidate recall、source-span coverage、stale/unauthorized rate、selected tokens、rank stability 和 final use，而不是只看 answer accuracy。（支持 claims：REP-C07、REP-C18、REP-C22、BEN-C25；支持 evidence：REP-V13、REP-V14、REP-V36、REP-V37、REP-V43、REP-V44、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

**Action。** Mem2ActBench 与 MemoryArena 说明 memory 的终点可以是 tool constraint 应用或跨 session 决策，不只是回答 recall question；action stage 应记录哪些 memory item 被模型引用、是否满足当前约束、tool outcome 以及失败是否触发 re-retrieve。由此可以把“相关证据已召回但 agent 未使用”与“read path 根本没召回”分开，并检验 STALE 型行为不更新。（支持 claims：BEN-C07、BEN-C12、OPS-C16；支持 evidence：BEN-EV13、BEN-EV14、BEN-EV23、BEN-EV24、OPS-J16；反对/限定 claims：BEN-C22；反对/限定 evidence：BEN-EV43、BEN-EV44。）

## GitHub 实现模式与集成

scope-recall-hermes@`867b…` 提供本簇最完整的 fixed-commit read-path 样本：journal-first capture 隔开 raw turn 与 durable facts，SQLite 是 authoritative truth，digest/candidate/promotion 形成 user/memory/project/ops rows，LanceDB、SQLite brute-force 或 PGVector 是可重建 companion，`recall_pipeline` 融合 lexical/vector/graph/freshness。其价值在于把 source-of-truth、scope 与 candidate fusion 放进同一实现；限制是仓库未执行，companion recovery SLO、benchmark 与独立采用均未知。（支持 claims：PRJ-A004、PRJ-I004、PRJ-C004；支持 evidence：PRJ-AE004-01、PRJ-AE004-02、PRJ-AE004-03、PRJ-IE004-01、PRJ-IE004-02、PRJ-E004；反对/限定 claims：PRJ-M004；反对/限定 evidence：PRJ-ME004。）

它还给出一个重要 integration boundary：`general` 是本地 scratch，user/memory/project/ops 才是 durable scope；若已有 central PostgreSQL，多 agent 场景中该插件应是 local Hermes recall layer，而不是跨 agent source of truth。这意味着 read adapter 不能悄悄改变 authority：本地 recall 可以加速或个性化当前 agent，却不能覆盖共享权威状态；route fusion 时也必须标记 local/central source。（支持 claims：PRJ-I004、EXP-C18、EXP-C19；支持 evidence：PRJ-IE004-01、PRJ-IE004-02、EXP-V35、EXP-V36、EXP-V37、EXP-V38；反对/限定 claims：none；反对/限定 evidence：none。）

Mem0、A-MEM 与 HippoRAG 则分别提供 hybrid signals、tunable k/links 和 graph/PPR route 的实现证据。集成时不应复刻其默认 budget：A-MEM 要求 k sweep，而 Mem0 文档 benchmark 使用 top_200；这两个数字不是同一协议。适配层应将 query class、routes、per-route depth、global candidate/token cap、reranker 和 fallback 全部显式配置，并记录 fixed version。（支持 claims：REP-C10、REP-C12、REP-C16、REP-C18；支持 evidence：REP-V19、REP-V20、REP-V23、REP-V24、REP-V31、REP-V32、REP-V36、REP-V37；反对/限定 claims：REP-C17；反对/限定 evidence：REP-V33、REP-V34。）

## 成本与运行负担

read cost 至少分解为 intent/query rewrite、每 route I/O/compute、candidate hydration、dedup/fusion、rerank、graph expansion、context tokens、re-retrieve/tool calls 与 trace storage；write/maintenance 侧还要分摊 embedding、index version、graph/link maintenance 和 rebuild。主动导航只有在额外步骤带来的 action/answer 增益超过延迟、tokens 与 failure surface 时才有净价值；当前 MemCon 只提供机制/作者结果，v09 没有跨 backend cost reproduction。（支持 claims：FND-C14、FND-C15、FND-C16、REP-C16、REP-C18；支持 evidence：FND-EV26、FND-EV27、FND-EV28、FND-EV29、FND-EV30、FND-EV31、REP-V31、REP-V32、REP-V36、REP-V37；反对/限定 claims：none；反对/限定 evidence：none。）

预算要成为 API contract：`max_routes`、`candidate_k_by_route`、`global_candidates`、`graph_hops/expansions`、`rerank_k`、`context_tokens`、`max_retrieval_rounds` 与 `tool_budget` 应进入 protocol fingerprint。LightMem reproduction 的 58.1→75.5 变化证明 retriever 本身可以支配最终结果；raw/constructed 排名又受 depth 和 answer-token cap 影响，所以没有预算记录的 accuracy 不能用于架构比较或容量规划。（支持 claims：REP-C05、REP-C06、REP-C18、BEN-C22；支持 evidence：REP-V09、REP-V10、REP-V11、REP-V12、REP-V36、REP-V37、BEN-EV43、BEN-EV44；反对/限定 claims：none；反对/限定 evidence：none。）

## Benchmark protocol 与可比性

至少保留五个 protocol family：LoCoMo/LongMemEval 的长程 QA，MemoryAgentBench 的 incremental retrieval/learning/understanding/forgetting，relation/time/conflict query，Mem2ActBench 的 memory-conditioned tool use，以及 MemoryArena 的 interdependent action-feedback。每个 family 单独报告，不平均成一个 memory score；固定 dataset/version、history construction、model、agent wrapper、store/index、retriever、route budget、token/tool budget、seed、judge，并附 route/candidate/compile trace。（支持 claims：BEN-C01、BEN-C02、BEN-C03、BEN-C07、BEN-C12、BEN-C22、BEN-C25；支持 evidence：BEN-EV01、BEN-EV02、BEN-EV03、BEN-EV04、BEN-EV05、BEN-EV06、BEN-EV13、BEN-EV14、BEN-EV23、BEN-EV24、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

每次 retrieval 评测应报告阶段性指标：授权后 gold 是否仍在 corpus；各 route candidate recall；fusion 后 recall/duplicate/conflict；rerank nDCG/recall 或任务匹配指标；compiler source-span coverage 与 token utilization；reader answer；action/tool constraint success；stale/unauthorized retrieval；latency/cost。oracle candidate 和 oracle raw-span 两个上界可区分 store/representation loss 与 rank/compiler loss。该分解直接回应 LightMem construction loss 与 bitemporal post-filter dilution，而不是用最终分数掩盖两者。（支持 claims：REP-C03、REP-C05、REP-C06、REP-C07、REP-C22；支持 evidence：REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V13、REP-V14、REP-V43、REP-V44；反对/限定 claims：none；反对/限定 evidence：none。）

active navigation 对照要固定初始 query/store/model，比较 one-shot、rule-based re-retrieve、graph/PPR navigation 与 learned controller；统一最大 rounds、candidate/token/tool budget，并报告 stop reason、loop rate、marginal gain 和 failure。若 learned policy使用额外反馈或调用，必须在成本向量中显式计入，不能只把最终任务分数与一次 top-k 比较。（支持 claims：FND-C14、FND-C15、BEN-C25；支持 evidence：FND-EV26、FND-EV27、FND-EV28、FND-EV29、BEN-EV49、BEN-EV50；反对/限定 claims：FND-C16；反对/限定 evidence：FND-EV30、FND-EV31。）

## 限制、失败与负证据

第一类失败是 candidate loss：extract/constructed memory 丢掉 source span，ANN 未召回，hard filter 位置错误，graph expansion 没覆盖目标，post-filter 稀释合法时间候选。第二类是 ranking/compilation：stale 或低 authority item 排在前，conflict 被压扁，budget 截断关键 raw evidence。第三类是 trust/action：语义相关但 contextually inappropriate 的内容越域，query/observation injection 操纵候选，召回成功却未改变行为。每类需要不同 trace 和修复，不能统一归因于“memory 不好”。（支持 claims：REP-C03、REP-C05、REP-C06、REP-C07、OPS-C04、OPS-C10、OPS-C16；支持 evidence：REP-V05、REP-V06、REP-V09、REP-V10、REP-V11、REP-V12、REP-V13、REP-V14、OPS-J04、OPS-J10、OPS-J16；反对/限定 claims：none；反对/限定 evidence：none。）

目前最强的反例来自独立 LightMem reproduction：固定 constructed store，仅改变 retriever 就把 accuracy 从 58.1% 推到 75.5%；matched depth 下 raw-turn Naive RAG 通常更强，而 constructed memory 主要在严格 answer-token budget 下受益，oracle 还发现 construction 删除了 answer-relevant information。这不证明所有 structured/active retrieval 无效，却足以否决不匹配 retriever/depth/token 的排行榜和“constructed 必然更优”。（支持 claims：REP-C05、REP-C06；支持 evidence：REP-V09、REP-V10、REP-V11、REP-V12；反对/限定 claims：REP-C04、REP-C16；反对/限定 evidence：REP-V07、REP-V08、REP-V31、REP-V32。）

## 替代方案、共识与决策含义

按条件选择最小 read path：短静态 QA 用 lexical/vector hybrid + raw evidence；需要 entity/time/conflict 时增加 hard filters 与 structured routes；严格 context budget 加 compiler/summary 但保留 raw fallback；需要多跳关系才开 graph/PPR；反馈丰富且任务长程时再试 re-retrieve/active controller；高风险 tool use 强制 trustworthy filter 与 action-time authorization。所有复杂化都要有 matched ablation，否则默认回到可解释的简单 baseline。（支持 claims：REP-C05、REP-C06、REP-C07、REP-C12、REP-C16、FND-C14、BEN-C07；支持 evidence：REP-V09、REP-V10、REP-V11、REP-V12、REP-V13、REP-V14、REP-V23、REP-V24、REP-V31、REP-V32、FND-EV26、BEN-EV13、BEN-EV14；反对/限定 claims：none；反对/限定 evidence：none。）

**共识**是 retrieval budget 与 protocol fingerprint 会显著改变排名，scope/time 应在 prompt 前过滤；**条件共识**是 hard filter→candidate→rerank→compile 的 staged pipeline 更可审计；**争议**是 constructed/graph/active navigation 的普适收益与最佳 fusion/controller；**证据不足**是跨系统 source-span/oracle 对照、统一 action/security harness、selected repo 的执行/采用、Graphiti canonical 工程证据及全链成本。hybrid retrieval 为中等成熟，trustworthy search、active navigation 与跨 backend rank trace 尚早期。（支持 claims：REP-C05、REP-C06、REP-C07、REP-C17、REP-C18、REP-C20、REP-C22、BEN-C22；支持 evidence：REP-V09、REP-V10、REP-V11、REP-V12、REP-V13、REP-V14、REP-V33、REP-V34、REP-V36、REP-V37、REP-V40、REP-V43、REP-V44、BEN-EV43、BEN-EV44；反对/限定 claims：none；反对/限定 evidence：none。）

上线 gate 应要求：scope/time hard-filter unit tests；每 route 可重放 trace；raw/constructed fallback；budget sweep；stale/conflict/security cases；action-use ablation；p50/p95 与 cost vector；pinned repo execution。反转 staged pipeline 判断所需证据是：多个任务 family、相同 store/model/budget 的独立结果持续显示无 scope/time/rank/compiler 分层的简化 top-k 在 correctness、isolation、action success 和成本上同等可靠；升级 active navigation 为默认则需跨 backend 稳定净收益且无不可控 loop/cost。（支持 claims：REP-C07、REP-C18、BEN-C07、BEN-C22、BEN-C25、OPS-C04、OPS-C10；支持 evidence：REP-V13、REP-V14、REP-V36、REP-V37、BEN-EV13、BEN-EV14、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50、OPS-J04、OPS-J10；反对/限定 claims：none；反对/限定 evidence：none。）

## 已命名缺口

- `GAP-CNS-03`：缺 flat、hybrid、graph、bitemporal、active navigation 在 relation/temporal/conflict-heavy tasks 上的 matched candidate/token/reader/maintenance-cost 对照。
- `GAP-CNS-04`：缺跨系统 source-span coverage、oracle recall 与 matched-budget raw/constructed reproduction。
- `GAP-CNS-08`：现有 harness candidates 尚未证明可固定 dataset/model/wrapper/retrieval-token-tool budget/seed/judge 并重跑 action/security families。
- `GAP-CNS-10`：selected repositories 未执行，缺 pinned install/test、maintenance/license 与 independent deployment evidence。
- `GAP-CNS-12`：缺全链 model calls、tokens、latency、bytes/revisions、rebuild、audit retention 与 human review 成本。
- `GAP-CNS-13`：canonical getzep/graphiti entity 尚未完成 identity、commit、release 与 paper relation 重建。

下一轮应优先建立可重放 retrieval trace harness，固定 raw/constructed、route、candidate/token/tool budget，再执行 representative repositories；继续添加“支持 hybrid/graph”项目不会关闭上述任何决策缺口。（支持 claims：REP-C17、REP-C18、REP-C19、REP-C20、BEN-C22、BEN-C25；支持 evidence：REP-V33、REP-V34、REP-V36、REP-V37、REP-V38、REP-V39、REP-V40、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

## 实际饱和轮次

`SAT-CL-MM-C04` 在 `2026-08-10T10:54:07Z` 记录为 `saturated`：已消费 8 个 targeted queries、13 个 deep-verified memberships；最终可回放轮次为 `FM-EV-CLUSTER-MM-C04-11` 与 `FM-EV-CLUSTER-MM-C04-12`。停止规则是连续两个 breadth wave 不再增加 first-order leaf，且 targeted deep/negative/implementation follow-up 不再改变边界或决策命题；六个 residual gaps 继续保留。饱和只说明当前 first-order map 与 decision proposition 已稳定，不表示 retrieval protocol、active navigation 或成熟度已经被最终验证。（过程记录：SAT-CL-MM-C04；支持 claims：none；支持 evidence：none；反对/限定 claims：none；反对/限定 evidence：none。）


<!-- synthesis:CLY-C04 claims:REP-C05,REP-C06,REP-C07,REP-C16,REP-C18,REP-C22 clusters:MM-C04 -->
