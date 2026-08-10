# MM-C08 — Personalization, Identity & Conversational Continuity：深度报告

**研究截止：2026-08-10。** 本文不把“记住用户名字”当完整个性化。它研究跨 session 的 user facts、preferences、persona、identity/self-state 如何被观察、推断、确认、纠正、撤销和按目的使用，同时避免 stale、forged、越权或未经同意的 profile 影响后续行动。

当前 bundle join 得到本簇 membership 248、primary 99、rolling-12m 205、rolling-90d 120；类型为 220 papers、28 repositories。数量是 v09 coverage，不是用户采用、增长或成熟度；计数锚点为 `bundle/cluster_assignments.jsonl × bundle/entities.jsonl`。

## 1. 结论与边界

本簇的最小安全单位不是一段对话摘要，而是带 `subject + time + source/support + observed/inferred status + consent + visibility + current/conflict state` 的 profile assertion。纳入跨 session user fact、preference、persona、identity/self state 以及 correction/delete/continuity；单轮 style prompt、没有 durable state 的偏好提示不纳入。多 agent 共享 personal fact 时进入 C11 principal/policy boundary；profile 的更新、supersede、purge 与 C05 相交；privacy/extraction 与 C12 相交。

当前可辩护的产品决策不是“profile 越多越好”，而是 **minimal profile + episodic source + temporal identity resolution + purpose/scope + consent/correction/delete + action-time revalidation**。POLAR、MemMachine 等支持 state 分层；STALE、trustworthy search、MEXTRA 与 DP-MemView 则证明 retrieval relevance、state update 和 privacy 不能由一个 top-k profile API 包办。

证据锚点：claims `REP-C07,REP-C14,EXP-C12,EXP-C13,EXP-C19,OPS-C03,OPS-C14,OPS-C15,OPS-C16`；evidence `REP-V13,REP-V14,REP-V27,REP-V28,EXP-V23,EXP-V24,EXP-V25,EXP-V26,EXP-V37,EXP-V38,OPS-J03,OPS-J14,OPS-J15,OPS-J16`。

## 2. 演进脉络：从 conversation summary 到 governed identity state

### 2.1 User assessment 进入 updater

MemoryBank 的 store 不只保存 conversation records 与 event summaries，还包含 evolving user-personality assessments，并通过 updater 做强化/遗忘。这把个性化从 prompt convenience 变成长期 mutable state；但它没有因此提供 consent、tenant isolation、semantic correction 或 delete propagation 的完整合同。

证据锚点：claims `FND-C05,FND-C06`；evidence `FND-EV08,FND-EV09,FND-EV10,FND-EV11`。

### 2.2 Profile 与 episode/working memory 分层

MemMachine 文档把 graph-based episodic context、SQL profile facts/preferences 与 short-term working memory 分开；Supermemory 文档同时暴露 profile/episodic、fact extraction、temporal update/forgetting 与 hybrid search。这支持“profile 是 typed current-state projection，episode 是 evidence history”的架构区分，但这些是仓库实现陈述，不是独立性能或删除证明。

证据锚点：claims `REP-C13,REP-C14`；evidence `REP-V25,REP-V26,REP-V27,REP-V28`。

### 2.3 Personalization 扩展到 multimodal identity/world interaction

POLAR 将 personalized semantic context、visual concepts 与 episodic embodied trajectories 分离；这说明长期偏好可能依赖视觉/环境概念，但 world-state observation 不能被压成普通 user profile。跨 agent 使用时，personal state 还必须增加 principal-and-scope policy。

证据锚点：claims `EXP-C12,EXP-C19,EXP-C20`；evidence `EXP-V23,EXP-V24,EXP-V37,EXP-V38,EXP-V39,EXP-V40`。

### 2.4 Correction 的终点从 store 推到 behavior

STALE 在作者的 400 conflict scenarios/1,200 queries 设置中报告，即使最佳模型 overall accuracy 也只有 55.2%；其核心现象是 updated evidence 已存在而 response 仍按旧值规划。该作者结果不能外推所有系统，但它建立了“retrieval latest fact ≠ policy adaptation”的负向边界。

证据锚点：claims `EXP-C13,OPS-C16`；evidence `EXP-V25,EXP-V26,OPS-J16`。

### 2.5 Privacy 从静态存储扩到 repeated response transcript

MEXTRA 研究 black-box extraction；DP-MemView 把多轮 memory-conditioned responses 的 cumulative leakage 建模为 adaptive transcript privacy，并让 response model 只看到 selected public conditioning view。由此可见，加密 at rest 或 user_id filter 不能替代 response-time disclosure policy。

证据锚点：claims `OPS-C03,OPS-C14,OPS-C15`；evidence `OPS-J03,OPS-J14,OPS-J15`。

## 3. 问题分解与参考架构

建议把 personal memory 拆成五类状态：

1. **Episodic evidence**：用户原话、interaction event、tool result、source span；append-only、purpose/retention scoped。
2. **Semantic/profile assertion**：可纠正的 fact/preference，带 subject、predicate、value、valid/transaction time、support、stability、confidence、consent 与 status。
3. **Persona/identity constraint**：用户明确选择或系统身份规则；不能由单次 behavior 静默推断。
4. **Working personalization context**：本次任务编译出的最小 profile view，不等于全局 profile。
5. **Dependency/action trace**：哪些 plan、recommendation 或 tool parameter 使用了哪一 revision，供 correction 后失效和 repair。

部署上建议把 authoritative profile 放在 versioned relational/document store，episode 保存 raw source，semantic/temporal indexes 仅作 projection；响应模型只接收按 user/tenant/purpose/as-of 选择的 public view。这是设计综合，不是统一行业标准。

证据锚点：claims `REP-C14,REP-C22,EXP-C12,EXP-C19,OPS-C15,OPS-C16`；evidence `REP-V27,REP-V28,REP-V43,REP-V44,EXP-V23,EXP-V24,EXP-V37,EXP-V38,OPS-J15,OPS-J16`。

## 4. 算法与 write→manage→read→action 数据流

### 4.1 Write：observed 与 inferred 必须分开

write 先捕获 episodic evidence，再抽取 candidate assertion。建议状态机为：`observed → inferred-candidate → confirmed/current → contradicted/conflict → superseded/revoked/purged`。明确用户陈述、系统观测和模型推断使用不同 authority；敏感字段需要 purpose/consent gate。重复出现只能增加支持，不能自动把低信任推断变成身份事实。

证据锚点：claims `FND-C05,REP-C07,REP-C14`；evidence `FND-EV08,FND-EV09,REP-V13,REP-V14,REP-V27,REP-V28`。

### 4.2 Manage：correction 是 version 与 dependency repair

新值不 overwrite 旧文本，而是在同 subject/predicate 下建 revision，保留 valid time、transaction time、support 与 conflict。supersede 后重算 profile summary、retrieval index、cached recommendation 与 dependent plans；forget/revoke/purge 分开。STALE 表明只更新 store 不足，因此 propagation status 必须成为可观测字段。

证据锚点：claims `REP-C02,EXP-C13,OPS-C16,FND-C21`；evidence `REP-V03,REP-V04,EXP-V25,EXP-V26,OPS-J16,FND-EV40,FND-EV41`。

### 4.3 Read：scope、purpose、time 先于 similarity

query 必须携带 principal/user/tenant、requesting agent、purpose、as-of、allowed fields 与 token/privacy budget。先硬过滤 scope/purpose/consent/time，再解析 current/conflict，最后 semantic/lexical ranking。Trustworthy memory search 已指出 semantically related memories 可能 contextually inappropriate，并导致 cross-domain leakage、sycophancy、tool-call drift 或 jailbreak；不能交给 LLM 在 prompt 内“自行忽略”。

证据锚点：claims `REP-C07,OPS-C19,OPS-C26`；evidence `REP-V13,REP-V14,OPS-J19,OPS-J26`。

### 4.4 Compile：只给任务所需的 public conditioning view

context compiler 生成 purpose-limited profile view，附 source/currentness/conflict，但不暴露 raw private memory。DP-MemView 支持 selected public view 这一接口形状；其 formal privacy 结果不等于任何任意 compiler 都有同等保证。建议对多轮 disclosure 累计计量，而不是逐回答独立判断。

证据锚点：claims `OPS-C14,OPS-C15`；evidence `OPS-J14,OPS-J15`。

### 4.5 Action：偏好只影响授权范围内的参数

recommendation/tool action 前重新检查当前 revision、purpose 与 action authority；若用户纠正、撤权或 task context 改变，阻断旧 premise。action trace 记录使用的 profile revision、override、outcome 与 user correction，支持后续 safety/utility ablation。此为设计建议；STALE 与 Mem2ActBench 分别支持 behavior adaptation 与 tool-grounding 需要独立检查。

证据锚点：claims `EXP-C13,BEN-C07,OPS-C16`；evidence `EXP-V25,EXP-V26,BEN-EV13,BEN-EV14,OPS-J16`。

## 5. 实现与集成：profile API 背后的真实责任

### Mem0：facade、identity filter 与 backend capability

固定 SHA 的 Mem0 OSS `add` 先按 user/agent/run filters 隔离、检索 existing candidates、用 LLM 抽取 facts，再写 vector memories、SQLite history 与 entity collection；search 可组合 semantic、BM25、entity 与 rerank。identity 必须通过 filters/entity params 传递，metadata 中的 user/agent/run identifiers 会被剥离；backend 没有 keyword search 时 hybrid BM25 被禁用。故“同一 API”并不保证 scope 或 retrieval capability 等价，且 LLM/provider failure 会阻断 `infer=True` write。

证据锚点：claims `PRJ-A015,PRJ-I015,OPS-C26`；evidence `PRJ-AE015-01,PRJ-AE015-02,PRJ-AE015-03,PRJ-IE015-01,PRJ-IE015-02,OPS-J26`。

### MineEcho：多层 personal state 与 persistence fallback

MineEcho 固定 SHA 同时维护 working memory、node:sqlite short-term interactions/preferences/tasks/summaries、file-based long-term profile 与 L0-L3 tree，再把近期 memory 与 vector/BM25/graph/LightRAG evidence 组合给 chat。若 `node:sqlite` 不可用，ShortTermDb 会退回内存 Map，进程重启丢 state；这使 fallback logging 与 durability monitoring 成为 integration requirement。其 PolyForm Noncommercial license 也限制商业采用。

证据锚点：claims `PRJ-A008,PRJ-I008`；evidence `PRJ-AE008-01,PRJ-AE008-02,PRJ-AE008-03,PRJ-IE008-01,PRJ-IE008-02`。

### Letta V1：core blocks 与 archival passages 的 lineage boundary

固定 SHA 的 `letta-ai/letta` 被 README 明确标为 legacy V1；其 memory 分为可直接渲染/编辑的 core blocks 与 archive/source passages，PassageManager 写 SQL rows 并可 dual-write Turbopuffer。agent passage 与 source passage 的 archive/source ID 约束互斥，跨 backend embedding 维度语义也不同。该仓适合说明 core-profile/archive 的实现形状，不应被当作当前 Letta 主实现或生产成熟度证据。

证据锚点：claims `FND-C04,PRJ-A014,PRJ-I014`；evidence `FND-EV06,FND-EV07,PRJ-AE014-01,PRJ-AE014-02,PRJ-AE014-03,PRJ-IE014-01,PRJ-IE014-02`。

### Product controls 与 assurance boundary

Microsoft 文档暴露 CRUD、TTL、remember/forget 与 user scope；这些是必要 governance surfaces，但当前 evidence 不证明 tenant isolation、consent correctness 或 derived-data deletion。GitHub bounded code-search 只找到若干不同 owner 仓库中的公开依赖/集成文本；它不证明 production deployment、user scale 或 effect。

证据锚点：claims `OPS-C18,OPS-C19,GR-C-M014`；evidence `OPS-J18,OPS-J19,GR-V-M014-01,GR-V-M014-02,GR-V-M014-03,GR-V-M014-04,GR-V-M014-05,GR-V-M014-06,GR-V-M014-07,GR-V-M014-08,GR-V-M014-09,GR-V-M014-10,GR-V-M014-11,GR-V-M014-12,GR-V-M014-13,GR-V-M014-14,GR-V-M014-15,GR-V-M014-16,GR-V-M014-17,GR-V-M014-18,GR-V-M014-19,GR-V-M014-20,GR-V-M014-21,GR-V-M014-22`。

## 6. 成本模型

Personalization 的成本包含：episodic retention、LLM fact/preference extraction、confirmation/review、version/conflict storage、semantic/temporal index、purpose-limited compilation、privacy accounting、correction/delete propagation 与错误个性化的用户损失。Mem0 的 fixed-SHA integration 显示默认 write 依赖 LLM/embedding provider；MineEcho 的多层 state 又引入 local DB、file profile、knowledge worker 与 provider keys。当前没有 longitudinal matched no-profile cost/benefit ledger。

建议报告：每 session candidate/confirmed assertion 数、inference→confirmation ratio、raw/profile/index bytes、LLM calls、write/read p50/p95、human confirmation minutes、stale-use rate、cross-scope blocks、privacy disclosure budget、correction-to-action propagation time、delete completion 与 user override。任何只报 recall 或 tokens 的评估都不足以支持扩大 profile。

证据锚点：claims `PRJ-I008,PRJ-I015,OPS-C14,OPS-C16`；evidence `PRJ-IE008-01,PRJ-IE008-02,PRJ-IE015-01,PRJ-IE015-02,OPS-J14,OPS-J16`。

## 7. Benchmark protocol：必须有 no-profile、correction、action 与 privacy

建议构造同一 longitudinal user stream 的四臂：`no durable profile`、`episodic-only`、`minimal confirmed profile`、`automatic inferred profile`。固定 model、history、retriever/k、context budget、judge 与 tool set；按阶段注入 explicit preference、ambiguous behavior、conflicting update、consent change、cross-domain request、delete/export request 与 tool action。

Outcome vector 至少包括：

1. evidence localization 与 QA；
2. current/conflict resolution、FAMA/stale penalty；
3. preference-conditioned recommendation；
4. tool selection/parameter grounding；
5. cross-domain/tenant leakage 与 extraction；
6. correction/delete propagation；
7. sycophancy/override；
8. token/latency/storage/review cost。

LoCoMo/LongMemEval 提供 long-conversation QA；Memora 评估 remembering/reasoning/recommending 并惩罚 obsolete/invalidated use；HaluMem 拆 extraction/update/QA；Mem2ActBench 把长期 constraint 接到 tool selection/parameters。它们不是一个 leaderboard，必须保留 protocol label。

证据锚点：claims `BEN-C01,BEN-C02,BEN-C05,BEN-C06,BEN-C07,BEN-C22,BEN-C25`；evidence `BEN-EV01,BEN-EV02,BEN-EV03,BEN-EV04,BEN-EV09,BEN-EV10,BEN-EV11,BEN-EV12,BEN-EV13,BEN-EV14,BEN-EV43,BEN-EV44,BEN-EV49,BEN-EV50`。

## 8. 限制、失败与负面证据

| 失败面 | 当前证据 | 设计含义 |
|---|---|---|
| stale behavior | updated evidence 不保证 response 改用新 premise | action-time revalidation + dependency repair |
| contextually inappropriate recall | semantic relevance 可带来 leakage/sycophancy/tool drift/jailbreak | scope/purpose hard filter 在 LLM 前 |
| black-box extraction | private agent memory 可通过查询被抽取 | 需要 transcript-level disclosure control |
| cumulative leakage | repeated responses 的风险不是单轮相加可忽略 | 维护 adaptive privacy/accounting state |
| API surface overclaim | scope/TTL/delete 文档不等于 isolation/purge proof | 独立 penetration/delete audit |
| backend/fallback drift | identity/filter/search/durability 随 backend 或 fallback 改变 | capability fingerprint + telemetry |
| adoption gap | public code reference 不等于 deployment or effect | 不做 maturity winner |

证据锚点：claims `EXP-C13,REP-C07,OPS-C03,OPS-C14,OPS-C15,OPS-C18,OPS-C19,OPS-C26,GR-C-M014`；evidence `EXP-V25,EXP-V26,REP-V13,REP-V14,OPS-J03,OPS-J14,OPS-J15,OPS-J18,OPS-J19,OPS-J26,GR-V-M014-01,GR-V-M014-02,GR-V-M014-03,GR-V-M014-04,GR-V-M014-05,GR-V-M014-06,GR-V-M014-07,GR-V-M014-08,GR-V-M014-09,GR-V-M014-10,GR-V-M014-11,GR-V-M014-12,GR-V-M014-13,GR-V-M014-14,GR-V-M014-15,GR-V-M014-16,GR-V-M014-17,GR-V-M014-18,GR-V-M014-19,GR-V-M014-20,GR-V-M014-21,GR-V-M014-22`。

## 9. 替代方案与适用条件

1. **Session-only state**：高敏感、长期收益未证实时默认；session end 后删除或用户导出。
2. **Minimal confirmed profile**：只保存用户明确确认的少量稳定字段，其他行为证据留 episode。
3. **User-owned local file/profile**：强调可见、可编辑、可携带；牺牲自动推断与 managed convenience。
4. **Ask-on-demand**：在高影响 recommendation/action 前重新询问，而不依赖陈旧偏好。
5. **Purpose-specific views**：不同 agent/domain 只获得必要字段，不建立 global all-agent profile pool。
6. **No persistence for sensitive domains**：当 extraction/consent/delete guarantee 不足时，拒绝跨 session 保存。

扩大 automatic personalization 的条件：longitudinal matched no-profile study 显示稳定净效用，同时 stale、leakage、sycophancy、tenant 与 delete 指标过门槛。任何 cross-tenant exposure、不可纠正 identity drift 或高影响 stale action 都应触发收缩。

证据锚点：claims `REP-C07,EXP-C13,EXP-C19,OPS-C03,OPS-C14,OPS-C15,OPS-C16`；evidence `REP-V13,REP-V14,EXP-V25,EXP-V26,EXP-V37,EXP-V38,OPS-J03,OPS-J14,OPS-J15,OPS-J16`。

## 10. 共识、分歧与决策

**条件共识：** profile/episode/working context 应分开；每个 assertion 要有 subject、scope、time、source 与 correction path；purpose/tenant filter 应在 retrieval 前；最新记录被检索不等于 behavior 已适应；API/documentation 不是 isolation 或 deletion proof。

**仍有分歧：** 自动推断多少 profile；是否允许 persona 从 behavior 演化；local-first 与 managed service 的合适边界；consent 是 field-level 还是 purpose/session-level；多 agent 是否共享 personal state；privacy mechanism 与 utility/cost 如何共同优化。

**决策建议：** `restricted pilot`。从 minimal confirmed profile + episodic source 开始，要求 principal scope、purpose、valid time、consent、correction/delete、dependency repair 与 no-profile ablation。自动 inferred profile 限于低风险字段并需可见/可撤销；高影响 action 默认重新确认。

证据锚点：claims `REP-C13,REP-C14,EXP-C12,EXP-C13,EXP-C19,OPS-C03,OPS-C14,OPS-C15,OPS-C16,OPS-C19`；evidence `REP-V25,REP-V26,REP-V27,REP-V28,EXP-V23,EXP-V24,EXP-V25,EXP-V26,EXP-V37,EXP-V38,OPS-J03,OPS-J14,OPS-J15,OPS-J16,OPS-J19`。

## 11. 分层代表证据

| Stratum | 代表项 | 用途 | 边界 | Claim / evidence |
|---|---|---|---|---|
| foundational | MemoryBank | conversation/event/personality assessment 与 updater | 缺 consent/isolation/delete proof | `FND-C05,FND-C06` / `FND-EV08,FND-EV09,FND-EV10,FND-EV11` |
| recent paper | POLAR、STALE、DP-MemView（2026） | multimodal personalized state、behavior adaptation negative、transcript privacy | 作者 protocols，需独立复现 | `EXP-C12,EXP-C13,OPS-C14,OPS-C15` / `EXP-V23,EXP-V24,EXP-V25,EXP-V26,OPS-J14,OPS-J15` |
| repository/product | Mem0、MineEcho、Letta V1、Microsoft scope/TTL | identity filters、layered profile、core/archive、API controls | fixed-SHA/static/docs；Letta 为 legacy；不证明 assurance | `PRJ-A015,PRJ-A008,PRJ-A014,OPS-C18,OPS-C19` / `PRJ-AE015-01,PRJ-AE015-02,PRJ-AE015-03,PRJ-AE008-01,PRJ-AE008-02,PRJ-AE008-03,PRJ-AE014-01,PRJ-AE014-02,PRJ-AE014-03,OPS-J18,OPS-J19` |
| benchmark | LoCoMo、LongMemEval、Memora、HaluMem、Mem2ActBench | QA、update/forget、operation failure、tool grounding | protocol families 不可合并 | `BEN-C01,BEN-C02,BEN-C05,BEN-C06,BEN-C07,BEN-C22` / `BEN-EV01,BEN-EV02,BEN-EV03,BEN-EV04,BEN-EV09,BEN-EV10,BEN-EV11,BEN-EV12,BEN-EV13,BEN-EV14,BEN-EV43,BEN-EV44` |
| negative/security | trustworthy search、MEXTRA、STALE、DP-MemView | inappropriate recall、extraction、stale action、cumulative leakage | 不等于 production prevalence 或通用 defense | `REP-C07,OPS-C03,EXP-C13,OPS-C14` / `REP-V13,REP-V14,OPS-J03,EXP-V25,EXP-V26,OPS-J14` |

## 12. 命名缺口与真实 saturation

- **GAP-C08-01 — longitudinal utility-safety：** 真实长期用户、matched no-profile/episodic/minimal/automatic profile 的净效用。
- **GAP-C08-02 — consent lifecycle：** purpose change、withdrawal、derived profile、shared agent 与 backup 的 consent/delete propagation。
- **GAP-C08-03 — dependent preference repair：** correction 后 recommendation、plan、cache 与 tool parameters 的失效和重算。
- **GAP-C08-04 — tenant and cross-agent isolation：** user/agent/team/purpose filter 的独立 penetration test。
- **GAP-C08-05 — adaptive privacy：** extraction 与 repeated-response leakage 的共同 utility/cost protocol。
- **GAP-C08-06 — adoption/operations：** 独立 deployment、release migration、p95、support burden 与 user override data。

Field-matrix 的 C08 scope 有两轮真实 no-material closure。Cycle 11：`SAT11-C08-OA`（10）、`SAT11-FOUNDATION-OA`（10）、`SAT11-GH-C07C08`（5）；cycle 12：`SAT12-C08-ARXIV`（3）、`SAT12-FOUNDATION-ARXIV`（10）、`SAT12-GH-C07C08`（10）。所有请求成功，均未要求新 entity、stance、proposition 或 first-order boundary；follow-up 看见 conflicting-memory QA、Mi-Memory 与 provenance implementations，但它们强化既有 profile/conflict/evaluation 路线。详见 `work/saturation-followup/field-matrix/scope-saturation.jsonl`。

这只关闭第一阶 personalization/profile taxonomy，不关闭 longitudinal consent、independent adoption、tenant isolation、delete propagation 或 privacy/utility evidence。出现新的 identity-state primitive、independent longitudinal reversal、cross-tenant result 或完整 consent/delete contract 时应重开。

证据锚点：claims `EXP-C13,EXP-C19,REP-C07,OPS-C03,OPS-C14,OPS-C15,OPS-C16,OPS-C27`；evidence `EXP-V25,EXP-V26,EXP-V37,EXP-V38,REP-V13,REP-V14,OPS-J03,OPS-J14,OPS-J15,OPS-J16,OPS-J27,OPS-J28,OPS-J29,OPS-J30,OPS-J31,OPS-J32,OPS-J33,OPS-J34,OPS-J35,OPS-J36,OPS-J37,OPS-J38,OPS-J39,OPS-J40,OPS-J41,OPS-J42,OPS-J43,OPS-J44,OPS-J45`。


<!-- synthesis:CLY-C08 claims:FND-C05,EXP-C12,EXP-C13,EXP-C19,OPS-C03,OPS-C14,OPS-C15,OPS-C16 clusters:MM-C08 -->
