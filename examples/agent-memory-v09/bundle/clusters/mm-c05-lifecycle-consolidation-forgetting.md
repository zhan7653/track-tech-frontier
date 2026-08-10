# MM-C05 — Lifecycle, Consolidation & Forgetting：深度报告

**研究截止：2026-08-10。** 本文是 final standalone cluster report，不是项目简介合集。它回答一个系统问题：长期状态怎样在持续写入、冲突、压缩、遗忘、撤权与故障之后，仍保持有限、可纠正、可恢复。

当前 bundle join 得到本簇 membership 479、primary 143、rolling-12m 406、rolling-90d 237；类型为 348 papers、130 repositories、1 other。这里的数量仅表示 v09 检索与映射覆盖，不表示技术成熟或增长；计数锚点为 `bundle/cluster_assignments.jsonl × bundle/entities.jsonl`。

## 1. 结论与边界

本簇的核心不是“有没有 add/delete API”，而是 **mutation plane 是否把状态变更当作有前置条件、版本、结果与补偿动作的操作**。纳入：admit、update、supersede、merge/consolidate、deduplicate、forget、revoke、purge、restore、rollback，以及这些动作的 policy、journal 和验证。只有存储与相似度检索、没有状态演化策略的系统留在 C01/C02/C04；单纯 prompt 截断或缓存压缩留在 C07；安全攻击属于 C12，但其 write→mutation→action 后果在本簇必须处理。

最稳妥的工程判断是：保留不可变 source/revision ledger，把 profile、summary、embedding、graph 和 current view 视作可重建 projection；让 learned controller 或 LLM hook **提出**动作，让独立事务/策略层验证并提交。该判断是跨来源综合，不是某一论文的原话。MemoryBank 已分 storage/retrieval/updating，近期 MemCon、MemTxn、budgeted consolidation 与 ForgetEval 又分别把 operation selection、事务恢复、预算约束和 forgetting placement 变成独立问题。

证据锚点：claims `FND-C05,FND-C14,FND-C17,FND-C19,FND-C21,FND-C23`；evidence `FND-EV08,FND-EV26,FND-EV27,FND-EV32,FND-EV33,FND-EV36,FND-EV37,FND-EV40,FND-EV41,FND-EV44,FND-EV45,FND-EV46`。

## 2. 演进脉络：为什么 retrieval 之后还需要 lifecycle

### 2.1 从“记住并强化”到显式 updater

MemoryBank 的 storage→retrieval→updating 分工，使遗忘第一次不只是 context window 的自然丢失：其 updater 借鉴 Ebbinghaus forgetting curve，以 elapsed time 与 relative importance 选择强化或遗忘。它建立了 lifecycle 问题，但没有由此证明 transaction、删除传播或 crash recovery 已解决。

证据锚点：claims `FND-C05,FND-C06`；evidence `FND-EV08,FND-EV09,FND-EV10,FND-EV11`。

### 2.2 从固定规则到 operation selection

随着 memory object 分成 raw episode、fact/profile、summary 和 procedure，单一 decay/importance rule 不再足够：不同任务可能需要 retrieve、再次检索、注入计划、consolidate、forget 或 no-op。MemCon 把这些动作放进在线 policy；作者还把实现描述为 tabular contextual bandit、UCB exploration、binary task feedback、无额外 LLM call。后者仍是作者设计陈述，不能外推为安全或跨 backend 泛化。

证据锚点：claims `FND-C14,FND-C15,FND-C16`；evidence `FND-EV26,FND-EV27,FND-EV28,FND-EV29,FND-EV30,FND-EV31`。

### 2.3 从“更新文本”到 transaction、version 与 recovery

当更新会改变后续行动，回答模型本身不能同时充当事实抽取器、authority checker、version resolver 和 crash-recovery engine。MemTxn 因而把 transaction boundary 放到 answer model 外，加入 source-supported admission、temporal version selection 与 durable snapshot journal。ForgetEval 又把 recall 与 supersede、release、purge 分开，说明“模型不再说出旧事实”不等于底层状态已经撤销或删除。

证据锚点：claims `FND-C17,FND-C18,FND-C21,FND-C22`；evidence `FND-EV32,FND-EV33,FND-EV34,FND-EV35,FND-EV40,FND-EV41,FND-EV42,FND-EV43`。

### 2.4 从状态正确到行为适应

STALE 给出关键反证：store 已更新，response 仍可能围绕旧值规划。这把 lifecycle 的终点从 database state 推到 action-time policy adaptation；StateAuditor 的限制也说明 provenance/chronology 验证不等于 semantic supersession。因而 correction 的完成条件必须包含 dependent projection、plan、cache 与 action premise 的失效或重算。

证据锚点：claims `OPS-C16,OPS-C17`；evidence `OPS-J16,OPS-J17`。

## 3. 问题分解与参考架构

本报告建议把 lifecycle 拆成五个责任域：

1. **Evidence ledger**：保存 raw receipt、source、principal、event/valid time、transaction time 与内容 hash；不因 summary 更新而覆盖。
2. **Mutation gateway**：验证 authority、schema、support、scope、conflict、budget 与 operation risk；产生 accept/reject/review decision。
3. **Revision graph**：每次 update/supersede/merge 建新 revision，保存 parent、operator、inputs、coverage/loss、current/conflict/status。
4. **Derived projections**：summary、profile、semantic/lexical index、graph、cache；允许异步生成，但必须带 revision watermark 和 rebuild path。
5. **Action/repair plane**：在 tool/action 前重新检查 currentness、scope 与 revocation；失败或纠正触发 dependency invalidation、rollback 或 replay。

这是设计推论。其依据是三平面综合、MemTxn 的外部 transaction boundary、budgeted-consolidation 的 operator/budget tension，以及 provenance 只能证明 transition history、不能证明内容真值的限制。

证据锚点：claims `FND-C17,FND-C19,FND-C20,FND-C23,OPS-C12,OPS-C13,OPS-C16,OPS-C17`；evidence `FND-EV32,FND-EV33,FND-EV36,FND-EV37,FND-EV38,FND-EV39,FND-EV44,FND-EV45,FND-EV46,OPS-J12,OPS-J13,OPS-J16,OPS-J17`。

## 4. 算法与 write→manage→read→action 数据流

### 4.1 Write：先记录，再晋升

建议把每次写入分为 `receipt` 与 `candidate mutation`。receipt 先追加到 ledger；candidate 再经过：身份/租户硬过滤 → source authority → schema/type → support span → conflict lookup → privacy/retention policy → destructive-risk tier。低支持的 inference 不应静默晋升为 current fact；高影响 delete/purge 应进入双重授权或延迟提交。

可实现的决策记录至少包含：`operation_id, object_id, parent_revision, principal, purpose, support_ids, valid_time, transaction_time, operator, budget, decision, reviewer, reason`。这是一项实现建议，不是现有统一标准。

证据锚点：claims `FND-C17,FND-C23,OPS-C24,OPS-C25`；evidence `FND-EV32,FND-EV33,FND-EV44,FND-EV45,FND-EV46,OPS-J24,OPS-J25`。

### 4.2 Manage：在预算下选择可逆操作

建议把 operator choice 写成受约束优化，而不是固定“总是摘要”：

`o* = argmax_o E[task utility | o] - λ·tokens - μ·latency - ν·information_loss - ρ·irreversibility`

其中 `o ∈ {retain, merge, abstract, rewrite, supersede, forget, no-op}`；`purge` 不应由同一低风险 policy 自动探索。每次 consolidation 保存 inputs、source-span coverage、loss audit 与可回滚 projection。该公式是本报告的决策框架；来源只支持 operator/budget 依赖和无普遍 operator ranking。

证据锚点：claims `FND-C14,FND-C19,FND-C20`；evidence `FND-EV26,FND-EV27,FND-EV36,FND-EV37,FND-EV38,FND-EV39`。

### 4.3 Read：解析 current、history 与 deletion lag

读取不应只返回 top-k text。resolver 先根据 principal/purpose/as-of/object type 选择 current、historical 或 all-versions intent，再输出 source、revision、conflict、revocation、projection watermark 与 delete status。若 authoritative ledger 已 supersede 而 index/cache 未追上，结果必须标明 lag 或阻断，而不是把 eventual consistency 隐藏给 LLM。

证据锚点：claims `FND-C17,REP-C02,REP-C22,OPS-C16`；evidence `FND-EV32,FND-EV33,REP-V03,REP-V04,REP-V43,REP-V44,OPS-J16`。

### 4.4 Action 与 repair：完成 correction 的最后一公里

action gateway 对 memory-derived premise 重新做 currentness、authority 与 scope 校验；outcome 写回新的 evidence。若后续证据否定旧 revision，系统沿 dependency graph 失效 summary、profile、index、plan 与 cached tool arguments。rollback 应恢复 application-visible state，并通过 journal replay 重建 projections；它不能只撤销回答文本。

证据锚点：claims `FND-C17,FND-C18,OPS-C16,OPS-C17`；evidence `FND-EV32,FND-EV33,FND-EV34,FND-EV35,OPS-J16,OPS-J17`。

## 5. 实现与集成：工程形状而非项目排名

### Journal-first 与可重建 companion

固定 SHA 静态检查显示两种可组合形状。`causal-memory` 把 raw session logs、atomic facts 与 decision→outcome edges 放在 SQLite 骨架中，并在写时隔开审计原文和召回层；`scope-recall-hermes` 以 SQLite 为 authoritative truth，把 LanceDB/PGVector 等作为可重建 companion，并通过 digest/candidate/promotion 晋升 durable rows。它们未在 v09 执行，因此只能支持 architecture/integration surface，不能证明 crash correctness 或性能。

证据锚点：claims `PRJ-A003,PRJ-I003,PRJ-A004,PRJ-I004`；evidence `PRJ-AE003-01,PRJ-AE003-02,PRJ-AE003-03,PRJ-IE003-01,PRJ-IE003-02,PRJ-AE004-01,PRJ-AE004-02,PRJ-AE004-03,PRJ-IE004-01,PRJ-IE004-02`。

### Multi-store lifecycle 与 backend capability drift

固定 SHA 的 Mem0 OSS 路径把 vector memories、SQLite history 与 entity collection 分开；add 会先按 user/agent/run filters 隔离、检索 existing candidates、抽取 facts，再写向量/history/entity。不同 vector backend 是否实现 keyword search 会改变 hybrid retrieval 能力，managed benchmark 又包含 OSS 没有的 proprietary optimizations。由此可推出：lifecycle contract 必须记录 backend capability 与 projection一致性，不能把 facade API 当作等价实现。

证据锚点：claims `PRJ-A015,PRJ-I015`；evidence `PRJ-AE015-01,PRJ-AE015-02,PRJ-AE015-03,PRJ-IE015-01,PRJ-IE015-02`。

### 产品 API 是控制表面，不是保证

Microsoft 文档提供 memory CRUD、TTL 与 remember/forget；AWS 文档提供 memoryId 和 session deletion；Google 文档提供 revision inspection 与 IAM Conditions。它们证明 lifecycle surface 存在，但当前 evidence 没有独立验证 embedding、summary、revision、backup、telemetry 与 cache 的端到端 purge，也没有完整生产控制链验证。

证据锚点：claims `OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C27`；evidence `OPS-J18,OPS-J19,OPS-J20,OPS-J21,OPS-J22,OPS-J27,OPS-J28,OPS-J29,OPS-J30,OPS-J31,OPS-J32,OPS-J33,OPS-J34,OPS-J35,OPS-J36,OPS-J37,OPS-J38,OPS-J39,OPS-J40,OPS-J41,OPS-J42,OPS-J43,OPS-J44,OPS-J45`。

## 6. 成本模型

Lifecycle 成本至少分六账：写入抽取/校验、revision/ledger storage、projection build/rebuild、在线 read/rerank、人工 review、delete/recovery propagation。MemCon 作者报告 token 降低，但没有独立复现；budgeted consolidation 只支持“operator 取决于预算”，不支持普遍最优；ForgetEval 也明确记录 model/backend/protocol 与 LLM-quality sensitivity。因此不能把单一 token saving 当总成本。

建议每次实验同时记录：raw bytes、revision growth、projection bytes、write p50/p95、read p50/p95、consolidation compute、review minutes、delete-to-all-projections latency、recovery time、action success 与 false-forget cost。当前来源没有跨系统同口径数据，这一表是评估设计而非既有事实。

证据锚点：claims `FND-C16,FND-C19,FND-C20,FND-C22`；evidence `FND-EV30,FND-EV31,FND-EV36,FND-EV37,FND-EV38,FND-EV39,FND-EV42,FND-EV43`。

## 7. Benchmark protocol：必须测状态与行动

建议用同一事件流构造六阶段协议：`initial write → repeated use → conflict/update → consolidation pressure → revoke/forget/purge → crash/restore`。每阶段分别检查：

- authoritative state correctness 与 source support；
- current/history/conflict resolution；
- stale premise 是否进入回答或 tool action；
- delete/rollback 是否传播到所有 projection；
- task success、abstention、false forget；
- token、latency、storage、repair 与 review cost。

MemoryAgentBench 可提供 incremental retrieval/learning/understanding/forgetting framing；Memora 对 obsolete/invalidated memory 引入 penalty；HaluMem 拆 extraction/update/QA；MemSecBench 提供 Write–Execute–Forget security lifecycle。它们的 task unit 和指标不同，不能直接平均；内部 harness 应保留 protocol family 与完整 fingerprint。

证据锚点：claims `BEN-C03,BEN-C05,BEN-C06,BEN-C16,BEN-C22,BEN-C25,FND-C13,FND-C21`；evidence `BEN-EV05,BEN-EV06,BEN-EV09,BEN-EV10,BEN-EV11,BEN-EV12,BEN-EV31,BEN-EV32,BEN-EV43,BEN-EV44,BEN-EV49,BEN-EV50,FND-EV24,FND-EV25,FND-EV40,FND-EV41`。

## 8. 限制、失败与负面证据

| 失败面 | 已有证据允许的结论 | 不能推出什么 |
|---|---|---|
| consolidation 丢失 query-critical detail | retain 与 consolidate 的收益随 budget 变化；没有普遍 Merge/Abstract/Rewrite 排名 | “结构化/摘要总是更好” |
| controller 错误动作 | MemCon 是近期作者预印本，controller 可选 forget 等动作 | backend-agnostic 等于安全泛化 |
| transaction 证据边界 | MemTxn 有 source validation/version/journal 机制，但结果仍是作者协议 | 已证明生产 crash consistency |
| stale behavior | store 更新后行为仍可能使用旧 premise | correction API 调用成功等于 agent 已适应 |
| provenance 边界 | predecessor-linked provenance 可审计 transition；不证明内容真值 | signed history 等于 correct memory |
| deletion 边界 | API 可见 delete/TTL/revision surface | embeddings、backup、cache、telemetry 已完全 purge |

证据锚点：claims `FND-C18,FND-C19,FND-C20,FND-C22,OPS-C13,OPS-C16,OPS-C17,OPS-C27`；evidence `FND-EV34,FND-EV35,FND-EV36,FND-EV37,FND-EV38,FND-EV39,FND-EV42,FND-EV43,OPS-J13,OPS-J16,OPS-J17,OPS-J27,OPS-J28,OPS-J29,OPS-J30,OPS-J31,OPS-J32,OPS-J33,OPS-J34,OPS-J35,OPS-J36,OPS-J37,OPS-J38,OPS-J39,OPS-J40,OPS-J41,OPS-J42,OPS-J43,OPS-J44,OPS-J45`。

## 9. 替代方案与适用条件

1. **Append-only raw + manual current pointer**：低写频、高审计要求、人工可承受时优先；牺牲自动 consolidation，换取可恢复性。
2. **Session TTL / no durable profile**：高敏感、收益未证实时，直接缩小 persistence boundary。
3. **Static lifecycle rules**：操作集合稳定、反馈稀疏时，先用 deterministic thresholds；learned policy 只做 shadow recommendation。
4. **Human-reviewed semantic revisions**：高影响 user facts、政策或 tool constraints，要求 evidence span 与 review 后晋升。
5. **Long context + scoped retrieval**：如果 matched-budget baseline 已足够，不应为了“拥有 lifecycle”而新增有损 projection。

这些是基于已见风险的决策建议，不是来源报告的比较结果。反转条件是：跨 backend、同 workload 的独立复现证明自动 controller/consolidation 在 action success、detail retention、privacy deletion、rollback completeness 和总成本上稳定优于简单基线。

证据锚点：claims `FND-C19,FND-C20,REP-C05,REP-C06,OPS-C16`；evidence `FND-EV36,FND-EV37,FND-EV38,FND-EV39,REP-V09,REP-V10,REP-V11,REP-V12,OPS-J16`。

## 10. 共识、分歧与决策

**条件共识：** mutation 与 retrieval 应分责；raw evidence 与 derived state 应分开；supersede/release/purge 不应混成一个 delete；高影响 mutation 需要 source、scope、version 与 recovery；评测必须追到 later action。

**仍有分歧：** consolidation 何时发生、使用何种 operator；LLM hook 放在 store、retriever、compiler 还是 action loop；learned controller 能否跨 backend 泛化；logical hide 与 physical purge 的最低保证；eventual projection 是否能满足高风险应用。

**决策建议：** 默认采用 guarded pilot：append-only ledger + typed revision + deterministic admission + rollback + delete status；learned selection 先 shadow，destructive operations 永不由未约束 policy 独立提交。扩大条件是 matched lifecycle/security/cost 复现；缩小条件是 stale-action、cross-scope、不可恢复 mutation 或无法证明 delete propagation。

证据锚点：claims `FND-C17,FND-C18,FND-C19,FND-C20,FND-C21,FND-C22,FND-C23,BEN-C22,OPS-C16,OPS-C27`；evidence `FND-EV32,FND-EV33,FND-EV34,FND-EV35,FND-EV36,FND-EV37,FND-EV38,FND-EV39,FND-EV40,FND-EV41,FND-EV42,FND-EV43,FND-EV44,FND-EV45,FND-EV46,BEN-EV43,BEN-EV44,OPS-J16,OPS-J27,OPS-J28,OPS-J29,OPS-J30,OPS-J31,OPS-J32,OPS-J33,OPS-J34,OPS-J35,OPS-J36,OPS-J37,OPS-J38,OPS-J39,OPS-J40,OPS-J41,OPS-J42,OPS-J43,OPS-J44,OPS-J45`。

## 11. 分层代表证据

| Stratum | 代表项 | 用途 | 边界 | Claim / evidence |
|---|---|---|---|---|
| foundational | MemoryBank（2024 bundle date） | storage/retrieval/updating 与 selective forgetting 起点 | 不含通用 transaction/delete/recovery proof | `FND-C05,FND-C06` / `FND-EV08,FND-EV09,FND-EV10,FND-EV11` |
| recent paper | MemCon、MemTxn、budgeted consolidation、ForgetEval（2026） | operation policy、transaction、budget、forget placement | 均以作者预印本为主 | `FND-C14,FND-C17,FND-C19,FND-C21` / `FND-EV26,FND-EV27,FND-EV32,FND-EV33,FND-EV36,FND-EV37,FND-EV40,FND-EV41` |
| repository | causal-memory、scope-recall-hermes、Mem0 fixed-SHA | journal/source truth、projection、multi-store integration | 静态检查，未执行 | `PRJ-A003,PRJ-A004,PRJ-A015` / `PRJ-AE003-01,PRJ-AE003-02,PRJ-AE003-03,PRJ-AE004-01,PRJ-AE004-02,PRJ-AE004-03,PRJ-AE015-01,PRJ-AE015-02,PRJ-AE015-03` |
| benchmark | MemoryAgentBench、Memora、HaluMem、MemSecBench | incremental/update/forget/operation/security family | 分数不可合并 | `BEN-C03,BEN-C05,BEN-C06,BEN-C16,BEN-C22` / `BEN-EV05,BEN-EV06,BEN-EV09,BEN-EV10,BEN-EV11,BEN-EV12,BEN-EV31,BEN-EV32,BEN-EV43,BEN-EV44` |
| negative | no universal consolidation ranking；STALE；provenance≠truth | 约束自动化与完成条件 | 协议/模型依赖 | `FND-C20,FND-C22,OPS-C13,OPS-C16` / `FND-EV38,FND-EV39,FND-EV42,FND-EV43,OPS-J13,OPS-J16` |

## 12. 命名缺口与真实 saturation

- **GAP-C05-01 — independent lifecycle reproduction：** MemCon、MemTxn、budgeted consolidation、ForgetEval 在统一 backend adapter、model、budget、workload 下的独立复现。
- **GAP-C05-02 — delete propagation contract：** raw、summary、embedding/index、revision、cache、backup、telemetry 与 downstream plan 的 hide/supersede/revoke/purge 语义。
- **GAP-C05-03 — safe controller exploration：** irreversible mutation 的 action mask、off-policy evaluation、rollback 与 human review。
- **GAP-C05-04 — crash/concurrency truth：** journal replay、partial commit、multi-writer conflict、projection watermark 与 recovery point objective。
- **GAP-C05-05 — operational cost：** write/read/consolidate/delete/recover 的同口径 p50/p95、storage 与人工成本。

Field-matrix 的 C05 scope 已按真实执行记录闭合：cycle 11 的 `SAT11-C05-OA`（1 result）、`SAT11-FOUNDATION-OA`（10）、`SAT11-GH-C05C06`（2）无 material change；cycle 12 的 `SAT12-C05-ARXIV`（10）、`SAT12-FOUNDATION-ARXIV`（10）、`SAT12-GH-C05C06`（10）再次无 material change。两轮 HTTP 均成功，详见 `work/saturation-followup/field-matrix/scope-saturation.jsonl`。这只说明第一阶 lifecycle taxonomy 已饱和，不关闭上述 deeper-evidence gaps。

重新打开本簇的触发条件：出现新的 lifecycle primitive；独立复现反转 operator/controller 结论；完整 delete/recovery contract；或真实运行数据改变成本与安全决策。

证据锚点：claims `FND-C18,FND-C20,FND-C22,OPS-C16,OPS-C17,OPS-C27`；evidence `FND-EV34,FND-EV35,FND-EV38,FND-EV39,FND-EV42,FND-EV43,OPS-J16,OPS-J17,OPS-J27,OPS-J28,OPS-J29,OPS-J30,OPS-J31,OPS-J32,OPS-J33,OPS-J34,OPS-J35,OPS-J36,OPS-J37,OPS-J38,OPS-J39,OPS-J40,OPS-J41,OPS-J42,OPS-J43,OPS-J44,OPS-J45`。


<!-- synthesis:CLY-C05 claims:FND-C14,FND-C17,FND-C19,FND-C21,FND-C23 clusters:MM-C05 -->
