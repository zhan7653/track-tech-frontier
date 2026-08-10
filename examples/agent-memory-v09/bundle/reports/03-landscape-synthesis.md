# Agent Memory 架构与实现全景

## 结论先行

Agent Memory 的主问题已经不是“要不要向量库”，而是如何把不可信、会变化、带主体与时间的经验，编译成可追溯的持久状态，再在权限、预算和任务条件下将最小充分证据送入推理/行动，并让行动结果安全地回到状态系统。字段中的多数创新可以投影到四条路径：**write** 决定什么成为状态，**manage** 决定状态如何演化，**read** 决定当下看到什么，**action** 决定记忆如何改变行为且不继承过期权限。

最稳定的架构方向因此不是某个单一 store，而是六个可替换但契约明确的层：event/evidence ledger、typed/versioned state、materialized indexes、lifecycle controller、retrieval/context compiler、action authorization；service/runtime 与 observability 将它们连接，security、evaluation 和 cost 则横切每个状态转移。<!-- synthesis:ARCH-Y01 claims:FND-C17,FND-C23,REP-C02,REP-C22,EXP-C18,OPS-C07,OPS-C27 clusters:MM-C01,MM-C02,MM-C03,MM-C04,MM-C05,MM-C11,MM-C12 -->

## 1. 全领域正在构造的“状态编译器”

下表不是产品分层，而是从 broad map 与 deep packets 归纳出的运行责任。每一行都有不同的一致性、权限与成本语义。

| 运行责任 | 对应主簇 | 输入 → 输出 | 主流实现选择 | 不能被下一层补救的信息 |
|---|---|---|---|---|
| 接入与控制 | C01 | session/tool/event/import → authenticated operation | REST/MCP/SDK、memory OS、sidecar/service、checkpoint/admin | principal、tenant、purpose、source class、request id |
| 耐久与索引底座 | C02 | operation → journal/object/index records | SQLite/Postgres/Redis/object store、vector/lexical/graph connectors | durability、revision parent、commit order、delete/restore state |
| 状态表示 | C03 | raw evidence → fact/event/profile/belief/edge/version | typed records、event graph、bitemporal state、provenance links | valid time、transaction time、source span、conflict/supersession |
| 演化控制 | C05 | candidates/current state/outcome → admit/update/consolidate/forget | write gate、dedup、transaction、decay、budget policy、rollback | mutation intent、policy/version、loss、recovery point |
| 选择与编译 | C04 + C07 | query/task/authority/budget → evidence packet | scope/time hard filter、hybrid recall、graph/active navigation、rerank、token packing | rejected candidates、rank trace、budget、contradictions、why-now |
| 行为消费 | C06/C08/C09/C10/C11 | evidence packet → plan/tool/action/shared change | procedure/skill、profile resolution、project/world/shared state adapters | applicability、current authority、tool/environment version、outcome link |
| Assurance | C12 + C13 | every transition → audit/test/cost signal | provenance/taint、ACL/revocation、protocol fingerprint、failure gates | write→retrieve→act causal trace、repair/deletion proof、matched controls |

MemoryBank、MemGPT/Letta 和 MemoryOS 的历史脉络已经分别把 store/retrieve/update、virtual context tiering、Storage/Updating/Retrieval/Generation 显式拆开；MemTxn 又把 source-supported admission、version selection 和 recovery journal 放在回答模型外部。它们共同支持 plane separation，但没有任何一个来源证明了全栈标准已经成熟。（`FND-C03/FND-EV04–05`、`FND-C05/FND-EV08–09`、`FND-C11/FND-EV20–21`、`FND-C17/FND-EV32–33`。）

<!-- synthesis:LAND-AUTO-01 claims:FND-C03,FND-C05,FND-C11,FND-C17 clusters:MM-C01,MM-C03,MM-C05,MM-C12 -->

## 2. 写入：从“把文本存下”转向 typed admission

### 当前架构共识

write path 应先区分 durable object，再选择抽取、压缩和索引策略。至少需要 raw episode/tool outcome、semantic fact/profile、procedure/skill、world/project/shared state 与 control metadata；同一段输入可以产生多个 derived records，但 derived record 必须能回溯原 evidence。AtomMem 的 atomic fact→event/profile→associative graph、MemMachine 的 episodic graph/SQL profile/working memory 分离，以及 Voyager/MemP 的 executable skill/procedure，都表明不同对象不能被无差别 chunk 取代。（`REP-C01/REP-V01–02`、`REP-C14/REP-V27–28`、`EXP-C03/EXP-V05–06`、`EXP-C09/EXP-V17–18`。）<!-- synthesis:ARCH-Y02 claims:REP-C01,REP-C14,EXP-C03,EXP-C09 clusters:MM-C03,MM-C06,MM-C08 -->

建议的 write pipeline 是：

1. **capture**：保留原 turn、tool output、environment observation 或 import receipt，不立即把模型摘要当真相；
2. **authenticate and scope**：绑定 tenant/principal/agent/session、source class、purpose、visibility、retention policy；
3. **extract and type**：生成 fact/event/profile/procedure/world/project/shared candidates，并保留 source spans；
4. **admit**：执行 schema、authority、privacy、poisoning、duplicate/conflict 和 budget gate；高风险 candidate 可 quarantine；
5. **commit**：append immutable receipt/revision，再更新 SQL/vector/lexical/graph/temporal projections；
6. **observe**：记录 policy/model/index version、token/latency/bytes、decision 与 rollback pointer。

这个顺序直接回应安全包的攻击面：MINJA/eTAMP 表明攻击者不一定直接控制 store；MAFIA/Salami 又表明单条记录过滤和大 benign pool 都不是充分防线。write admission 必须保留来源、时间序列与后续行动可连接的身份，而不能只是一个输入 classifier。（`OPS-C05/OPS-J05`、`OPS-C10/OPS-J10`、`OPS-C11/OPS-J11`。）

### 主要分歧

何时压缩、合并或自动写入没有通用答案。budgeted-consolidation 证据认为 retention 保留细节，consolidation 在紧预算下提高单位 token 覆盖，却可能丢失 query-critical evidence；独立 LightMem 复现又显示 constructed store 的结果可被 retriever 与 token budget 反转。（`FND-C19/FND-EV36–37`、`REP-C05/REP-V09–10`、`REP-C06/REP-V11–12`。）因此 write-time summary 应是可重建 projection，而不是唯一记录；“永远摘要”与“永远保留”都不是共识。

## 3. 管理：lifecycle 与 consistency 是一等系统问题

### 从 CRUD 到状态机

C05 的成熟实现面不应只有 `add/search/delete`，而应显式区分 `propose/admit/commit/supersede/revoke/forget/purge/restore/reindex`。bitemporal representation 将 immutable identity 与 versioned content、valid time 与 transaction time分离；MemTxn 将更新验证和 snapshot journal 外置；ForgetEval 则把 recall 与 supersede/release/purge 等 mutation-plane operation 分开。这三类证据共同支持“更新不是覆盖、忘却不是搜不到、恢复不是重新问模型”。（`REP-C02/REP-V03–04`、`FND-C17/FND-EV32–33`、`FND-C21/FND-EV40–41`。）<!-- synthesis:ARCH-Y03 claims:REP-C02,FND-C17,FND-C21,OPS-C16,OPS-C17 clusters:MM-C03,MM-C05,MM-C12 -->

推荐一致性选择：

- 对 source receipt、authority、revision parent、revocation 和 action authorization 使用强一致或显式 compare-and-swap；
- 对 embeddings、graph edges、summaries、profiles 等 projection 允许 bounded eventual consistency，但查询结果必须暴露 projection/index version；
- shared state（C11）采用 principal-scoped branches、merge record 和 unresolved conflict，而不是 last-write-wins 全局 profile；
- semantic supersession 与 chronological validity 分开：StateAuditor 类 chronology/provenance 检查不能替代“新事实是否真的推翻旧事实”的语义裁决。（`OPS-C17/OPS-J17`。）

### learned controller 的正确位置

MemCon 将 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 作为 online policy actions，是 2026 control-plane 的强趋势信号；但它仍是作者预印本，且 learned policy 若直接拥有不可逆 purge 权限，会把探索错误变成持久损伤。（`FND-C14/FND-EV26–27`。）更稳妥的组合是：policy 在可审计 primitive 之上选择候选 operation；事务/权限层验证和提交高风险 mutation；恢复层保留可逆点。

## 4. 读取：从 top-k 相似度到 scope-aware context compilation

### 多路候选，不是“vector 或 graph”二选一

当前实践正向 hybrid access 收敛：semantic、lexical/BM25、entity、graph、temporal/version 和 scope filter 解决不同失配。Mem0 文档化 semantic+BM25+entity fusion 与 temporal ranking；Cognee/HippoRAG 展示 graph/ontology/PPR 路线；A-MEM 显式暴露 `retrieve_k`；这些支持“多路入口和预算可见”，不支持任何一个项目的通用优越性。（`REP-C11/REP-V21–22`、`REP-C12/REP-V23–24`、`REP-C16/REP-V31–32`、`REP-C18/REP-V36–37`。）

推荐 read path：

1. 解析 intent、principal、purpose、as-of 语义、task/environment/tool version 和预算；
2. 在 candidate generation 前执行 tenant/scope/permission/retention hard filter；
3. 分路召回 semantic/lexical/entity/graph/temporal candidates，分别记预算和 index version；
4. 合并并基于 relevance、freshness、authority、provenance、conflict、risk、cost 做 rerank；
5. 产生包含支持与冲突项的 evidence packet，而非裸文本列表；
6. context compiler 按 token/action budget 选择、格式化、引用，证据不足则 abstain 或二次检索；
7. 保存 retrieved/rejected IDs、reason、rank、tokens 和 prompt injection point。

“先取回再让 LLM 忽略越权内容”不是可靠权限模型。trustworthy-search 证据把检索本身定义为 trust boundary；STALE 又显示 stored state 已更新并不保证 response 改变行为。（`REP-C07/REP-V13–14`、`EXP-C13/EXP-V25–26`。）<!-- synthesis:ARCH-Y04 claims:REP-C07,REP-C18,EXP-C13,OPS-C19 clusters:MM-C04,MM-C07,MM-C08,MM-C12 -->

### context compiler 是缺失的工程层

编译器应输出 `why-now + as-of + source + revision + scope + conflict + budget`，并根据任务选择 current fact、historical episode、two-version conflict、procedure preconditions 或 world-state evidence。它把 C03 的语义、C04 的选择和 C07 的预算合成一个可测试接口。没有该层时，store/index 的正确性会在 prompt 拼接中丢失。

## 5. 行动：memory 的价值与风险都在“后续行为”发生

五类 durable object 需要不同 action adapter：

| 对象簇 | 行为作用 | 必须随记忆一起传递的条件 | 主要失败 |
|---|---|---|---|
| C06 procedure/skill | 影响 plan、tool sequence 或 executable action | source outcome、适用任务/工具版本、confidence、deprecation、side-effect class | contamination、过拟合、旧工具假设、越权执行 |
| C08 profile/identity | 解析当前用户偏好、persona/self constraint | user/tenant、valid time、consent、correction、visibility | stale premise、sycophancy、跨用户泄露 |
| C09 project/environment | 约束代码修改、handoff、build/test 环境 | repo/branch/commit、decision status、secret class、supersession | stale code、错误分支、秘密持久化、冲突决策 |
| C10 world state | 让 perception/planning 连续 | observation/visibility、space/time、action consequence、uncertainty | partial observability、overwritten state、记得但不会行动 |
| C11 shared state | 协作、复用组织知识、同步任务状态 | principal/role、read/write/share/revoke policy、provenance、merge status | authority collapse、tenant leak、stale propagated rule |

Voyager/MemP/MemSkill 说明 procedure 可以是 code、instruction/script 或 memory-operation policy，不能统称为“reflection”；Collaborative Memory 说明共享状态需要动态 read/write policy 与 provenance；POLAR/WorldLines 又分别划出 personal multimodal state 与 partially observable world state。（`EXP-C03/EXP-V05–06`、`EXP-C09/EXP-V17–18`、`EXP-C10/EXP-V19–20`、`EXP-C06/EXP-V11–12`、`EXP-C12/EXP-V23–24`、`EXP-C14/EXP-V27–28`。）

无论对象类型，敏感 action 都应按当前 identity、policy、tool/environment state 重新授权；不能因为一条 memory 曾被写入，就继承写入者或历史会话的权限。sleeper-memory 的 write→retrieve→later action 证据直接说明这一点。（`OPS-C07/OPS-J07`。）

<!-- synthesis:LAND-AUTO-02 claims:EXP-C03,EXP-C06,EXP-C09,EXP-C10,EXP-C12,EXP-C14,OPS-C07 clusters:MM-C01,MM-C03,MM-C05,MM-C12 -->

## 6. Security、evaluation 与 economics 不是三个附录

### Security/governance

C12 要求在每个状态转移保留控制点：write source/authority/quarantine；store revision/signature/rollback；read scope/purpose/freshness/privacy；action reauthorization；delete/repair propagation。MutMem 类型的 signed transition 可证明谁改了什么，但其作者也明确不证明内容真实；DP-MemView 处理 repeated-response disclosure，也不覆盖 raw export、logs 与 tool traces。（`OPS-C12/OPS-J12`、`OPS-C14/OPS-J14`。）所以 provenance、truth、authorization 和 privacy 是不同列，不能用一个“可信分数”折叠。

### Evaluation

C13 已经分化出至少五个不可混排的 protocol groups：static conversational QA；incremental lifecycle；action/state；multi-party/multimodal/implicit context；reliability/security。MemoryAgentBench/HaluMem 诊断 operation，Mem2ActBench/MemoryArena 测 memory-to-action，MemSecBench 测 Write–Execute–Forget。平均成一个 leaderboard 会抹掉 access path、agent loop、judge 和 metric 差异。（`BEN-C03/BEN-EV05–06`、`BEN-C06/BEN-EV11–12`、`BEN-C07/BEN-EV13–14`、`BEN-C12/BEN-EV23–24`、`BEN-C16/BEN-EV31–32`、`BEN-C22/BEN-EV43–44`。）

### Cost

成本需按 operation 计量：capture/extract/admit/commit、embedding/graph projection、retrieval/rerank/context tokens、consolidation/reindex/delete/restore、security scan/audit/human review、action retries。至少记录 p50/p95 latency、model calls/tokens、bytes/revisions per logical fact、index rebuild/repair time 与 false-block load。任何“更省 token”结论必须同时报告 fidelity、raw baseline、retrieval depth 和 action success；不能只报 summary ratio。

<!-- synthesis:LAND-AUTO-03 claims:BEN-C03,BEN-C06,BEN-C07,BEN-C12,BEN-C16,BEN-C22,OPS-C12,OPS-C14 clusters:MM-C01,MM-C03,MM-C05,MM-C12 -->

## 7. 共识、矛盾与成熟度

| 命题 | 判断 | 依据与条件 | 会改变判断的证据 |
|---|---|---|---|
| 持久 memory 需要 storage、selection 与 mutation/control 分工 | dominant / moderate | 跨历史系统、OS-style、transaction 与 forgetting evidence；适用于 external state | 跨 backend 复现显示无独立 mutation/recovery 层仍能稳定处理 conflict/delete/crash |
| typed state + scope/time/provenance 比无类型 chunk 更稳健 | dominant / conditional | 多个独立表示与共享/安全机制；不等于 graph 必胜 | 可复现实验表明 flat store 在同预算下对 update/conflict/authority/action 同样可靠 |
| constructed/compressed memory 普遍优于 raw history | mixed | 效果依赖 retriever、k、token cap、任务；存在独立反例 | 多系统、同模型/预算/reader 的可复现对照显示稳定优势 |
| learned lifecycle controller 应替代 static policy | evidence-thin | MemCon 是高价值近期信号，缺独立长期复现与安全约束 | 跨 framework/domain 的独立、长期、同预算复现，含 irreversible-action safety |
| graph/active navigation 普遍优于 hybrid retrieval | disputed/evidence-thin | 图保留 relation，active search 可扩展，但 protocol 不可比且 audit/cost 增加 | matched index/data/budget 的多任务消融与 failure analysis |
| 一套 benchmark 总分可比较所有 memory systems | rejected | protocol families 的 task/access/agent/metric 不兼容 | 预注册统一 harness 同时保留原 protocol fingerprints，且跨组校准获验证 |
| 现有 API/开源仓库已证明 production-safe/adopted | evidence-thin | 文档和 code surface 仅证明接口/工件存在，未执行、无独立采用/隔离/删除证明 | 可复现部署、incident/deletion/tenant tests 与独立 adoption evidence |

当前更成熟的是**职责分层和可观测契约**；中等成熟的是 typed external state、hybrid retrieval、profile/episode/skill 分离与 benchmark family；较早期的是 learned control、active navigation、bitemporal/transactional memory 的跨 backend 标准化、safe shared skill、端到端 deletion 和 model-native/external bridge。<!-- synthesis:ARCH-Y05 claims:FND-C14,FND-C17,FND-C19,REP-C05,REP-C06,REP-C22,BEN-C22,OPS-C27 clusters:MM-C01,MM-C03,MM-C04,MM-C05,MM-C07,MM-C12,MM-C13 -->

## 8. 工程决策顺序

1. 先定义 durable object、主体、时间、来源、版本与 action boundary，再选数据库。
2. 先让 raw evidence、revision 和 delete/recovery 可追溯，再加自动 consolidation 或 learned controller。
3. 先做 hard scope/time filter，再做语义/图检索；把 context compiler 作为正式组件。
4. 先用 raw/no-memory/matched-budget baselines 证明 memory 改变行为，再讨论项目排行榜。
5. 对 C06/C08/C09/C10/C11 分别建 action adapter，不能让一个 global top-k profile 覆盖所有主体和任务。
6. 敏感 action 重新授权，删除测试覆盖 raw、summary、embedding、graph、revision、cache、backup 和 traces。
7. C15/C16 只作为替代/集成视图：只有当它们满足相同 state、authority、observability、evaluation contract，才进入主架构比较。

C09 专属 deep packet 已闭合结构索引、事件溯源、上下文反证和反馈策略四条路线。仍未闭合的决策缺口是：Graphiti canonical identity；仓库实际安装/测试；shared-memory revocation/poisoning；跨产品 deletion propagation 与 tenant isolation；统一但不抹平 protocol 的 harness；learned controller 的 safe exploration；真实 p95/存储/人工审核成本。它们都可能改变实现选择，应在最终报告中保留为 abstention/gap，而不是用更多项目简介填满。
