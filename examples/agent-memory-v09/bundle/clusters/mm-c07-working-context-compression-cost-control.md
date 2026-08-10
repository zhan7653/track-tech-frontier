# MM-C07 — Working Context, Compression & Cost Control：深度报告

**研究截止：2026-08-10。** 本文讨论的不是 GPU KV cache、HBM 或 serving quantization，而是 Agent 的 semantic working context：长期 evidence 怎样在 token、latency、storage 与 tool budget 下，被选择、压缩、路由并编译成当前行动真正需要的上下文。

当前 bundle join 得到本簇 membership 187、primary 55、rolling-12m 155、rolling-90d 76；类型为 148 papers、36 repositories、3 other。数量只是 v09 coverage，不是增长率或成熟度；计数锚点为 `bundle/cluster_assignments.jsonl × bundle/entities.jsonl`。

## 1. 结论与边界

Persistent store 不是 working context，retrieval result 也不是最终 prompt。本簇的核心组件是 **context compiler**：它从 raw evidence、derived summaries/profiles/procedures、retrieval candidates 与 tool state 中，在显式预算和权限约束下构造最小充分 evidence packet。纯数据库、纯向量检索属于 C02/C04；长期 state mutation 属于 C05；模型内部 KV/serving 优化属于 C15 boundary。

当前最强结论不是“压缩有效”，而是 **compression 的结论必须绑定 retriever、candidate depth、compiled-token budget、reader/judge 和 source-loss audit**。独立 LightMem reproduction 显示，仅改变 retriever 就能大幅改变 fixed constructed store 的答案结果；matched retrieval depth 下 raw-turn Naive RAG 通常更强，而 constructed memory 主要在 tight answer-token budget 下占优。因此 C07 的问题不是选择一种万能摘要，而是设计可观测、可回退的 budget allocation 与 compilation contract。

证据锚点：claims `REP-C05,REP-C06,REP-C18,REP-C22,FND-C23`；evidence `REP-V09,REP-V10,REP-V11,REP-V12,REP-V36,REP-V37,REP-V43,REP-V44,FND-EV44,FND-EV45,FND-EV46`。

## 2. 演进脉络：从 virtual context 到 budgeted compiler

### 2.1 Virtual context：承认模型上下文是有限资源

MemGPT 通过 memory tiers 与 interrupts 管理有限 LLM context，把“全部历史放进 prompt”改写为控制流与层级移动问题。这是 C07 的基础：working context 是运行时选择结果，不等于 durable store 的全部内容。

证据锚点：claims `FND-C03,EXP-C04`；evidence `FND-EV04,FND-EV05,EXP-V07,EXP-V08`。

### 2.2 Structured compression：把压缩、合成与检索规划分开

SimpleMem 定义 semantic structured compression → online semantic synthesis → intent-aware retrieval planning 三阶段路径。它把离线 memory construction 和在线 retrieval/compilation 分离，使错误可以定位到 source extraction、synthesis 或 read plan，而不是只看最终 QA。

证据锚点：claims `REP-C04`；evidence `REP-V07,REP-V08`。

### 2.3 Budget-dependent consolidation：operator 不再有固定排名

近期 budgeted-consolidation 研究认为 retention 保留 raw detail，consolidation 提高 per-token coverage 但可能丢失 query-critical detail；其 formal utility 只是特定假设下的 surrogate，不宣称 Merge、Abstract、Rewrite 有普遍排序。这把 consolidation 从“后台清理”变成 workload/budget-conditioned decision。

证据锚点：claims `FND-C19,FND-C20`；evidence `FND-EV36,FND-EV37,FND-EV38,FND-EV39`。

### 2.4 Context compilation 成为独立工程表面

GitHub 工程证据把长期事实记忆与 context compression 分开：Headroom 处理模型前的工具输出、日志、代码和历史压缩；Claude-Mem 从 coding sessions 提取 observations/summaries；LightMem 同时暴露 memory management、MCP 和 benchmark surfaces。该分工是 repository architecture synthesis，不是跨项目效果排名。

证据锚点：claims `GR-C-M004`；evidence `GR-V-M004-01,GR-V-M004-02,GR-V-M004-03`。

### 2.5 Multimodal fixed-token compression 扩大边界

MeMento 在作者的 DunphyBench protocol 中报告 preference-conditioned fixed-token compression 的 accuracy 与 memory-usage 改善；该数字只能用于证明“视觉/偏好条件下也存在 budgeted compiler 问题”，不能与 textual QA 或其他系统直接排名。

证据锚点：claims `EXP-C15,EXP-C21`；evidence `EXP-V29,EXP-V30,EXP-V41,EXP-V42`。

## 3. 问题分解与参考架构

建议将 C07 分成六层：

1. **Raw evidence store**：保留可引用 source spans、tool result、image/frame 或 event；不被 summary 覆盖。
2. **Derived-state builders**：生成 summary、profile、procedure、event hierarchy；记录 compressor/model/prompt/version、inputs、coverage 与 loss。
3. **Candidate planner**：按 principal、purpose、time、type 与 task 先硬过滤，再给 lexical/semantic/entity/graph/temporal 路径分配 candidate budget。
4. **Budget allocator**：在 context、tool、latency 和 storage 约束下选择 raw/derived mix、depth、reranker 与 fallback。
5. **Context compiler**：输出带 why-now、as-of、source、confidence/conflict、token allocation 的 evidence packet，而不是无标记 top-k concatenation。
6. **Outcome telemetry**：记录实际使用的 spans、tokens、latency、tool/action outcome、abstention 与 reconstruction audit，反哺 projection retention。

这是跨 packet 的设计推论；目前没有统一 context-compiler API 或被执行的完整参考实现。

证据锚点：claims `FND-C19,FND-C23,REP-C04,REP-C18,REP-C22,BEN-C25`；evidence `FND-EV36,FND-EV37,FND-EV44,FND-EV45,FND-EV46,REP-V07,REP-V08,REP-V36,REP-V37,REP-V43,REP-V44,BEN-EV49,BEN-EV50`。

## 4. 算法与 write→manage→read→action 数据流

### 4.1 Write：raw first，projection second

write 先追加 raw receipt 与 source scope，再异步生成 derived object。每个 projection 保存 `input_ids, source_spans, compressor/model/prompt version, created_at, revision watermark, token length, coverage/loss audit`。若 raw source 不可保留，应明确不可逆边界，不能把 summary 当等价原文。

证据锚点：claims `FND-C19,REP-C04,REP-C22`；evidence `FND-EV36,FND-EV37,REP-V07,REP-V08,REP-V43,REP-V44`。

### 4.2 Manage：把 retention 与 compression 当可切换 operator

建议预算控制器解如下约束问题：

`maximize expected task utility - λ·prompt_tokens - μ·read_latency - ν·storage/rebuild - ρ·source_loss`

subject to principal/scope、minimum source coverage、context/tool caps 与 fallback policy。候选 operator 包括 keep raw、select spans、merge、abstract、rewrite、rebuild、drop projection；物理删除仍由 C05 policy 决定。公式是本报告的评估框架，来源只支持 budget-dependence 与 no universal ranking。

证据锚点：claims `FND-C19,FND-C20`；evidence `FND-EV36,FND-EV37,FND-EV38,FND-EV39`。

### 4.3 Read：先分 candidate budget，再分 compiled budget

应区分：`candidate_k`、各 retrieval lane 的配额、reranker depth、compiled memory tokens、answer tokens 与 tool-output tokens。A-Mem 要求用户调 `retrieve_k`，Mem0 的 documented benchmark configuration 使用 top_200；这证明 retrieval budget 是 implementation contract，不是中性细节。比较系统时必须把这几个预算分别记录。

证据锚点：claims `REP-C18`；evidence `REP-V36,REP-V37`。

### 4.4 Compile：最小充分、可追溯、可回退

compiler 对每个候选决定 raw span、derived summary 或两者并存，并输出 rejection reason。若 compression coverage 不足或 conflict 未解，触发 second retrieval、raw expansion 或 abstain；不能用更流畅的 summary 隐藏 evidence loss。LightMem reproduction 说明 retriever 和 answer-token cap 可反转结论，因此 fallback 必须属于 protocol。

证据锚点：claims `REP-C05,REP-C06,REP-C22`；evidence `REP-V09,REP-V10,REP-V11,REP-V12,REP-V43,REP-V44`。

### 4.5 Action 与反馈：优化目标不能停在 tokens saved

记录 agent 实际引用了哪些 memory、是否调用 tool、action 是否成功、旧 projection 是否造成错误。只有当压缩在相同任务与授权边界下改善 action success 或保持质量并降低总成本，才能称为有用。单纯 token reduction 可能伴随 source loss，不能独立作为上线指标。

证据锚点：claims `BEN-C07,BEN-C12,BEN-C22,BEN-C25`；evidence `BEN-EV13,BEN-EV14,BEN-EV23,BEN-EV24,BEN-EV43,BEN-EV44,BEN-EV49,BEN-EV50`。

## 5. 实现与集成：四种可检查形状

### Hierarchical virtual filesystem

OpenViking 固定 SHA 将 memory/resource/skill 统一到 `viking://`，内容先写 AGFS，SemanticQueue 异步生成 L0/L1/L2 与 URI/vector/metadata index，retrieve 执行 intent→hierarchical search→rerank。`add_resource` 后必须 `wait_processed` 或接受短时不可语义召回；这使 projection lag 成为 API contract。仓库未执行，不能证明 latency 或 quality。

证据锚点：claims `PRJ-A006,PRJ-I006`；evidence `PRJ-AE006-01,PRJ-AE006-02,PRJ-AE006-03,PRJ-IE006-01,PRJ-IE006-02`。

### Hook-driven observation/summarization

Claude-Mem 固定 SHA 通过 host hooks 把 prompt/tool/session-end 事件交给 per-user Bun worker；SQLite 保存 sessions/observations/summaries/pending queue，ChromaDB 保存 observation vectors，MCP 以 search→timeline/get_observations 做渐进披露。hooks 故意 fail-open，worker 不可用不会阻塞 host，因此 availability 优先于 capture completeness；评测必须测 missing-capture 与 session-ID continuity。

证据锚点：claims `PRJ-A007,PRJ-I007`；evidence `PRJ-AE007-01,PRJ-AE007-02,PRJ-AE007-03,PRJ-IE007-01,PRJ-IE007-02`。

### Local encrypted compiler substrate

Compartment 固定 SHA 在解锁后把 encrypted vault 打开到 RAM-only SQLite，结合 FTS5、exact/optional HNSW vector 与 RRF；vault 记录 embedding model hash，模型变更需显式 reindex/re-embed。所有 search 在 RAM 中意味着容量影响 RSS 与启动重载，多进程写由 advisory lock 串行。这是具体 cost/integration shape，不是性能保证。

证据锚点：claims `PRJ-A012,PRJ-I012`；evidence `PRJ-AE012-01,PRJ-AE012-02,PRJ-AE012-03,PRJ-IE012-01,PRJ-IE012-02`。

### Harness/plugin boundary

OmniMemEval 固定 SHA 不是 store，而是 evaluator：user-memory track 把 backend 归一为 add/search；agent-memory track 组合 runtime、memory plugin、task domain 与 verifier，并编排 cleanup→train→settle→backup/restore→test。不同 plugin 若缺 lifecycle method 会破坏 trial isolation；LLM judge、backend credentials 和 model version 都必须记录。

证据锚点：claims `PRJ-A013,PRJ-I013`；evidence `PRJ-AE013-01,PRJ-AE013-02,PRJ-AE013-03,PRJ-IE013-01,PRJ-IE013-02`。

## 6. 成本模型

C07 至少有五类预算，不能压成 token count：

- **construction**：抽取、summary、embedding、graph/profile build；
- **online retrieval**：candidate generation、rerank、remote service；
- **compiled context**：memory、tool output、answer reserve；
- **durability**：raw + derived + indexes + revision storage、rebuild；
- **failure/operations**：capture gap、stale cache、model migration、fallback、human audit。

建议报告 `source bytes → derived bytes → index bytes → compiled tokens` 的完整漏斗，以及 p50/p95 write/read/compile、cold start、rebuild、LLM calls、action success 和 reconstruction loss。MeMento 的 memory-usage 数字和 MemCon 的 token 数字均为各自作者协议；LightMem reproduction 进一步说明 answer-token cap 会改变胜负。当前没有跨系统同口径 cost ledger。

证据锚点：claims `EXP-C15,FND-C16,REP-C05,REP-C06,PRJ-I012`；evidence `EXP-V29,EXP-V30,FND-EV30,FND-EV31,REP-V09,REP-V10,REP-V11,REP-V12,PRJ-IE012-01,PRJ-IE012-02`。

## 7. Benchmark protocol：固定预算后再谈效果

最小可比实验应有四臂：`raw-turn`、`selected raw spans`、`constructed/summary memory`、`structured/graph/versioned memory`。固定 dataset/version、memory access、model/prompt、retriever family、candidate_k、rerank depth、compiled tokens、answer tokens、judge、seed 与 hardware/service。输出 outcome vector：

1. source-span/oracle recall；
2. answer/action correctness；
3. contradiction/stale/unauthorized inclusion；
4. tokens 与 raw/derived/index storage；
5. write/read/compile p50/p95；
6. reconstruction/abstention；
7. tool/action success；
8. rebuild/fallback behavior。

LongMemEval artifact 暴露 small/medium/oracle forms、retriever 与 turn/session granularity，可用于 access-path ablation；OmniMemEval 可作为 harness candidate，但不是独立 score authority。跨 static QA、tool grounding、environment action 的分数不能合并。

证据锚点：claims `BEN-C02,BEN-C19,BEN-C22,BEN-C23,BEN-C25,REP-C17`；evidence `BEN-EV03,BEN-EV04,BEN-EV37,BEN-EV38,BEN-EV43,BEN-EV44,BEN-EV45,BEN-EV46,BEN-EV49,BEN-EV50,REP-V33,REP-V34,REP-V35`。

## 8. 限制、失败与负面证据

| 失败面 | 当前证据 | 对设计的约束 |
|---|---|---|
| retriever confound | fixed constructed store 随 retriever 改变出现大幅结果差异 | 系统比较必须固定/报告 retriever |
| raw vs constructed reversal | matched depth 下 raw-turn 常更强，tight answer budget 才偏向 constructed | 不默认“先摘要” |
| query-critical loss | consolidation 可提高 coverage/token 但丢关键细节 | 保存 source spans 与 raw fallback |
| no universal operator | Merge/Abstract/Rewrite 无普遍排序 | operator 与 workload/budget 绑定 |
| async projection lag | OpenViking 需等待 processing；Claude-Mem fail-open 可漏 capture | watermark、completeness 与 fallback 是接口 |
| single-protocol multimodal gain | MeMento 数字来自作者指定 protocol | 不跨 textual/multimodal benchmark 排名 |

证据锚点：claims `REP-C05,REP-C06,FND-C19,FND-C20,EXP-C15,PRJ-I006,PRJ-I007`；evidence `REP-V09,REP-V10,REP-V11,REP-V12,FND-EV36,FND-EV37,FND-EV38,FND-EV39,EXP-V29,EXP-V30,PRJ-IE006-01,PRJ-IE006-02,PRJ-IE007-01,PRJ-IE007-02`。

## 9. 替代方案与适用条件

1. **Raw history + scoped retrieval**：history 可控、tight budget 不严重时作为默认基线。
2. **User-curated context file**：低频、可人工维护的稳定约束；必须记录 freshness，不把文件长度当价值。
3. **Hierarchical selection without lossy rewrite**：用目录/event/source spans 降候选量，暂不生成抽象 summary。
4. **Long-context model**：减少 retrieval/summary 复杂度，但仍需 scope、stale、cost 与 evidence tracing；不能自动解决 lifecycle。
5. **Ephemeral semantic cache**：只优化当前 session，避免把低价值 projection 晋升为长期事实。

升级到复杂 compiler 的条件：在同模型/同预算下，action/answer 与 evidence coverage 不降，且 total cost 或 latency 有稳定收益。若 raw baseline 更强或 reconstruction loss 不可接受，应裁剪 consolidation/summary 层。

证据锚点：claims `REP-C05,REP-C06,FND-C19,FND-C20,REP-C22`；evidence `REP-V09,REP-V10,REP-V11,REP-V12,FND-EV36,FND-EV37,FND-EV38,FND-EV39,REP-V43,REP-V44`。

## 10. 共识、分歧与决策

**条件共识：** budget 必须显式；raw 与 derived 应分开；candidate_k 与 compiled tokens 是不同变量；context 必须保留 scope/time/source/conflict；最终指标应连接 action，不只 tokens saved。

**仍有分歧：** offline compression、online synthesis 或 dynamic retrieval 的最优比例；graph/profile/summary 的统一接口；long-context 是否会降低 compiler 价值；什么情况下允许不可逆 source discard；latency、storage 与 answer quality 如何统一定价。

**决策建议：** `adopt simple baseline first`。先部署 scoped raw retrieval、明确 budget、trace 与 raw fallback；constructed/structured memory 只在 matched protocol 中稳定改善 source coverage/action 或显著降低总成本时加入。任何生产 compiler 都应 pin compressor/model/prompt/index version，并暴露 projection lag 与 reconstruction audit。

证据锚点：claims `REP-C05,REP-C06,REP-C18,REP-C22,BEN-C22,BEN-C25`；evidence `REP-V09,REP-V10,REP-V11,REP-V12,REP-V36,REP-V37,REP-V43,REP-V44,BEN-EV43,BEN-EV44,BEN-EV49,BEN-EV50`。

## 11. 分层代表证据

| Stratum | 代表项 | 用途 | 边界 | Claim / evidence |
|---|---|---|---|---|
| foundational | MemGPT virtual context | tiering 与 control-flow 起点 | 非完整 cost/quality contract | `FND-C03` / `FND-EV04,FND-EV05` |
| recent paper | SimpleMem；budgeted consolidation；MeMento | structured compiler、operator/budget、multimodal fixed-token | 作者机制/结果，协议不同 | `REP-C04,FND-C19,EXP-C15` / `REP-V07,REP-V08,FND-EV36,FND-EV37,EXP-V29,EXP-V30` |
| repository | OpenViking、Claude-Mem、Compartment | hierarchy/async、hook summary、local encrypted hybrid | fixed-SHA static，未执行 | `PRJ-A006,PRJ-A007,PRJ-A012` / `PRJ-AE006-01,PRJ-AE006-02,PRJ-AE006-03,PRJ-AE007-01,PRJ-AE007-02,PRJ-AE007-03,PRJ-AE012-01,PRJ-AE012-02,PRJ-AE012-03` |
| benchmark | LongMemEval forms；OmniMemEval harness | retrieval granularity 与 plugin lifecycle | harness 不等于 score authority | `BEN-C19,BEN-C23` / `BEN-EV37,BEN-EV38,BEN-EV45,BEN-EV46` |
| negative | independent LightMem reproduction；no universal operator ranking | retriever/token confound 与 source loss | reproduction 仍受其 protocol 限制 | `REP-C05,REP-C06,FND-C20` / `REP-V09,REP-V10,REP-V11,REP-V12,FND-EV38,FND-EV39` |

## 12. 命名缺口与真实 saturation

- **GAP-C07-01 — matched cost-quality ledger：** raw/selected/constructed/structured 四臂的 tokens、latency、storage、LLM calls、action 与 source coverage。
- **GAP-C07-02 — loss recovery：** source-span coverage、reconstruction、raw expansion 与 irreversible discard contract。
- **GAP-C07-03 — real p95 and scale：** async projection lag、cold start、rebuild、RAM/storage growth、remote service variance。
- **GAP-C07-04 — action-level benefit：** compression 对 tool/action 的净收益，而非仅 QA 或 token saving。
- **GAP-C07-05 — compiler interface：** budget、why-now、as-of、conflict、scope、fallback 的跨 backend contract。

Field-matrix 的 C07 scope 有两轮真实 no-material closure。Cycle 11：`SAT11-C07-OA`（10）、`SAT11-FOUNDATION-OA`（10）、`SAT11-GH-C07C08`（5）；cycle 12：`SAT12-C07-ARXIV`（6）、`SAT12-FOUNDATION-ARXIV`（10）、`SAT12-GH-C07C08`（10）。所有请求成功，均未要求新 entity、stance、proposition 或 first-order boundary；详见 `work/saturation-followup/field-matrix/scope-saturation.jsonl`。

这证明本轮对 virtualization、compression、budget、latency、raw-evidence-loss 的第一阶机制已饱和，不证明 operational cost 或某 compressor 已胜出。出现 matched action/cost reproduction、新 compiler primitive 或 source-loss reversal 时应重开。

证据锚点：claims `REP-C05,REP-C06,REP-C17,REP-C19,FND-C20`；evidence `REP-V09,REP-V10,REP-V11,REP-V12,REP-V33,REP-V34,REP-V35,REP-V38,REP-V39,FND-EV38,FND-EV39`。


<!-- synthesis:CLY-C07 claims:FND-C03,FND-C19,REP-C05,REP-C06,REP-C18 clusters:MM-C07 -->
