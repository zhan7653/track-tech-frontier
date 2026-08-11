# MM-C01 — Memory Services & Control Planes：深度报告

> 状态：final cluster report；证据截止 `2026-08-10`。本文只综合 v09 已登记、已打开的 claim/evidence/synthesis、deep packet 与 fixed-commit repository profile；未执行仓库，也不把 stars、README 自报分数或目录存在解释成采用、性能或生产成熟度。

## 结论先行

当 memory 会跨 session 持久化、被后续行动消费、允许修订或删除时，工程问题不再是“把文本放进一个可搜索的库”，而是“谁可以让什么状态在何时生效、如何证明这次变化、怎样恢复到一致版本、读出的内容能否被当前行动授权”。因此本簇最稳健的目标形态是一个带证据账本、类型化状态、可重建索引、生命周期控制器、受限检索/编译器和 action-time authorization 的 memory service；`add/search/delete` 只能作为外部便捷 API，不能代替内部状态机。这个判断只适用于 external、persistent、mutable 或 action-bearing memory；一次性、只读、静态 QA 可以裁剪 mutation 与 action 层。**判断：条件共识；信心 high；成熟度为“职责分层较成熟、完整端到端实现未验证”。**（支持 claims：FND-C03、FND-C11、FND-C14、FND-C17、FND-C21、FND-C23、OPS-C07、OPS-C12、OPS-C24；支持 evidence：FND-EV04、FND-EV20、FND-EV26、FND-EV32、FND-EV40、FND-EV44、FND-EV45、FND-EV46、OPS-J07、OPS-J12、OPS-J24；反对/限定 claims：REP-C06；反对/限定 evidence：REP-V11、REP-V12。）

这一定义把 MM-C01 与相邻簇分开：MM-C01 管 service/API/runtime、执行状态控制、checkpoint/version、policy 与 recovery；MM-C02 管存储、索引、WAL/segment 等 substrate；MM-C05 管 admit、consolidate、forget 等策略本身；MM-C12 管威胁模型与纵深防御。一个项目同时落入多个簇并不矛盾，但本稿不会把 generic agent framework 的 feature list、纯数据库 primitive 或单纯向量检索当成“Memory OS”。（支持 claims：FND-C17、FND-C23、REP-C22、OPS-C24；支持 evidence：FND-EV32、FND-EV44、FND-EV45、FND-EV46、REP-V43、REP-V44、OPS-J24；反对/限定 claims：none；反对/限定 evidence：none。）

## 分层证据选择

| 证据层 | 代表性条目与时间 | 本稿从中提取的作用 | 支持 claim / evidence | 反对或限定 claim / evidence |
|---|---|---|---|---|
| foundational paper | MemGPT，2024-02-12 | tier movement、virtual context 与 interrupt 把 memory placement 提升为 runtime control 问题 | FND-C03、FND-C23 / FND-EV04、FND-EV44 | none / none |
| architecture paper | MemoryOS，2025-05-30 | 多级存储与模块化管理说明 service/control plane 可独立于单一检索器 | FND-C11 / FND-EV20 | none / none |
| recent mechanism paper | MemTxn，2026-07-30；MemCon，2026-07-15 | source-supported admission、temporal visibility、snapshot journal、可学习的 lifecycle action | FND-C14、FND-C17、FND-C23 / FND-EV26、FND-EV32、FND-EV33、FND-EV45、FND-EV46 | FND-C15、FND-C16 / FND-EV28、FND-EV29、FND-EV30、FND-EV31 |
| fixed-commit GitHub | Sibyl-Memory@`e224…`，2026-08-07；Letta V1@`ff19…`，2026-08-01；Mem0@`4deb…`，2026-08-07 | local-first、legacy server、provider facade 三种部署/集成形态；只证明静态实现表面 | PRJ-A001、PRJ-I001、PRJ-A014、PRJ-I014、PRJ-A015、PRJ-I015 / PRJ-AE001-01、PRJ-IE001-01、PRJ-AE014-01、PRJ-IE014-01、PRJ-AE015-01、PRJ-IE015-01 | PRJ-C001、PRJ-C014、PRJ-C015 / PRJ-E001、PRJ-E014、PRJ-E015 |
| benchmark | MemoryAgentBench，2025-07-07；MemSecBench，2026-07-29 | 从 recall 扩展到 incremental update 与 Write–Execute–Forget 检查点 | BEN-C03、BEN-C16 / BEN-EV05、BEN-EV06、BEN-EV31、BEN-EV32 | BEN-C22 / BEN-EV43、BEN-EV44 |
| negative/security | Hidden in Memory，2026-05-14；STALE，2026-08-03；OWASP Guard repo，2026-08-10 | 持久写入会驱动未来行动；更新成功不等于行为更新；需 detector/policy/snapshot rollback | OPS-C07、OPS-C16、OPS-C17、OPS-C24 / OPS-J07、OPS-J16、OPS-J17、OPS-J24 | OPS-C27 / OPS-J27、OPS-J45 |

选择逻辑不是按“项目热度”抽样，而是让每一层分别覆盖历史起点、近期机制、可检查工程实现、可比协议和失败/攻击证据；同一作者的 paper 与 repo 不重复计成两个独立验证组。仓库证据用于回答组件、接口、依赖和部署边界，不能升级为运行正确性、性能、安全或采用结论。（支持 claims：FND-C04、FND-C10、FND-C12、REP-C19、EXP-C22、BEN-C23；支持 evidence：FND-EV06、FND-EV18、FND-EV22、REP-V38、REP-V39、EXP-V43、EXP-V44、BEN-EV45、BEN-EV46；反对/限定 claims：none；反对/限定 evidence：none。）

## 从 foundational 到 recent：问题怎样改变

第一阶段的突破是把有限 context 看成需要 runtime 管理的虚拟资源：MemGPT 的 tier movement 与 interrupt 说明“何时换入、换出和触发控制流”比单纯相似度检索更接近操作系统问题。第二阶段把这种思想扩成显式多级 memory 与服务模块，MemoryOS 将 storage level 和 management module 分开，使“长期状态服务”成为独立架构对象。两者奠定了 control-plane 语言，但还不能据此声称具备完整的更新验证、删除、回滚或多租户契约。（支持 claims：FND-C03、FND-C04、FND-C11、FND-C12；支持 evidence：FND-EV04、FND-EV05、FND-EV06、FND-EV20、FND-EV21、FND-EV22；反对/限定 claims：FND-C18；反对/限定 evidence：FND-EV34、FND-EV35。）

近期工作把控制从“context placement”推进到“状态转移”：MemCon 把 lifecycle operation 建模成控制动作，MemTxn 把 source support、temporal resolver 与 durable snapshot journal 放到更新边界，ForgetEval 则把 recall 与 supersede、release、purge 等 mutation operation 分开。方向上的共识是 memory service 必须能解释状态如何产生和变化；分歧在于 controller 是规则、显式状态机还是 learned policy，以及收益能否在相同 backend、任务和预算下稳定超过 passive/raw baseline。（支持 claims：FND-C14、FND-C15、FND-C17、FND-C21、FND-C23；支持 evidence：FND-EV26、FND-EV27、FND-EV28、FND-EV29、FND-EV32、FND-EV33、FND-EV40、FND-EV41、FND-EV44、FND-EV45、FND-EV46；反对/限定 claims：FND-C16、REP-C06；反对/限定 evidence：FND-EV30、FND-EV31、REP-V11、REP-V12。）

## 机制与目标架构

建议把外部 memory service 拆成六个可替换、契约明确的层，而不是绑定某个 vendor store：`evidence/event ledger → typed/versioned state → materialized indexes → lifecycle controller → retrieval/context compiler → action authorization`；service/runtime、identity、policy 和 observability 横向连接各层。ledger 保存可追溯输入和 tool outcome，typed state 表达当前/历史对象，indexes 只负责候选访问，controller 决定 admit/supersede/revoke/restore，compiler 在 scope、time 与 budget 内形成 evidence packet，最后一层在行动发生时重新校验权限和状态版本。该六层链是跨证据综合，不是任何单篇论文或单个仓库已经完整实现的产品。（支持 claims：FND-C17、FND-C23、REP-C22、EXP-C18、EXP-C19、OPS-C07、OPS-C12、OPS-C14、OPS-C16、OPS-C24、BEN-C25；支持 evidence：FND-EV32、FND-EV44、FND-EV45、FND-EV46、REP-V43、REP-V44、EXP-V35、EXP-V36、EXP-V37、EXP-V38、OPS-J07、OPS-J12、OPS-J14、OPS-J16、OPS-J24、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

部署形态可以是 in-process library、sidecar、独立 service 或 MCP/server adapter，但接口都应暴露稳定的 identity/scope、revision、receipt、query budget、trace、checkpoint 和 recovery 语义。in-process/local-first 形态减少网络边界，却把并发、跨主机协调和文件备份留给宿主；独立 service 统一 tenancy 与策略，却增加网络、鉴权、迁移和故障域；MCP/adapter 适合连接 agent runtime，但不能自动成为权威数据源。这里的选择是 topology 决策，不改变控制契约本身。（支持 claims：PRJ-A001、PRJ-I001、PRJ-C001、PRJ-A014、PRJ-I014、PRJ-C014、PRJ-A015、PRJ-I015、PRJ-C015；支持 evidence：PRJ-AE001-01、PRJ-AE001-02、PRJ-IE001-01、PRJ-E001、PRJ-AE014-01、PRJ-AE014-02、PRJ-IE014-01、PRJ-E014、PRJ-AE015-01、PRJ-AE015-02、PRJ-IE015-01、PRJ-E015；反对/限定 claims：none；反对/限定 evidence：none。）

## 算法与 write–manage–read–action 数据流

**Write。** 请求首先带上 tenant/user/agent/run、source、event time 和 caller authority，经认证 gateway 生成不可混淆的 receipt；原始 evidence 先进入 append-oriented ledger，再由 extractor 产生 typed candidate，而不是直接覆盖“当前记忆”。candidate 需通过 source support、duplicate/conflict、scope 与 policy 检查后才能 commit 成 revision；embedding、FTS、graph 等 projection 随后由同一 revision 派生。该顺序使索引失败可重建、抽取错误可撤回，也给 write-time poisoning detector 一个可插入边界。（支持 claims：FND-C17、FND-C23、OPS-C01、OPS-C03、OPS-C05、OPS-C12、OPS-C24、PRJ-A015、PRJ-I015；支持 evidence：FND-EV32、FND-EV33、FND-EV44、FND-EV45、OPS-J01、OPS-J03、OPS-J05、OPS-J12、OPS-J24、PRJ-AE015-01、PRJ-IE015-01；反对/限定 claims：OPS-C13；反对/限定 evidence：OPS-J13。）

**Manage。** controller 针对已提交 revision 执行 consolidate、supersede、revoke、forget、purge、restore、reindex 或 checkpoint；每个 operation 都应产生 predecessor、actor、reason 与 effect，物理删除还要枚举 derived indexes、cache、backup 和 audit-retention 之间的边界。learned controller 可以提出动作，但 durable commit、rollback 与权限检查仍需显式契约，因为 policy 适配失败可能出现“数据库已经更新、回答行为没有变化”，而 provenance/chronology 本身也不能证明 semantic supersession 正确。（支持 claims：FND-C14、FND-C17、FND-C21、OPS-C12、OPS-C16、OPS-C17；支持 evidence：FND-EV26、FND-EV32、FND-EV40、FND-EV41、OPS-J12、OPS-J16、OPS-J17；反对/限定 claims：FND-C15、FND-C16；反对/限定 evidence：FND-EV28、FND-EV29、FND-EV30、FND-EV31。）

**Read。** query 先做 hard scope/time/authorization filter，再从多个 materialized access path 生成 candidates；ranker 可用 relevance、freshness、authority、source support、conflict 和 cost 信号，但输出应是带 source span、revision、validity 与 rank trace 的 evidence packet，而不是无来源拼接文本。compiler 在 token/tool budget 下决定向模型暴露多少 raw evidence、typed state 和 conflict，且记录未选候选与预算，以便区分“store 没有”“retriever 丢失”“compiler 截断”和“model 未使用”。（支持 claims：REP-C07、REP-C18、REP-C22、FND-C23、OPS-C19；支持 evidence：REP-V13、REP-V14、REP-V36、REP-V37、REP-V43、REP-V44、FND-EV44、FND-EV45、FND-EV46、OPS-J19；反对/限定 claims：REP-C06；反对/限定 evidence：REP-V11、REP-V12。）

**Action。** 编译出的 memory 只能作为行动提案的依据，不能继承写入时或检索时的永久授权；在 tool call/外部副作用发生前，应按当前 principal、scope、revision freshness 和 policy 再授权，并把 outcome 回写成新 evidence。这样才能把“记住了错误内容”与“错误内容触发了危险行动”分成两个可观察检查点，也能在修订后验证 behavior 是否真正改变。（支持 claims：BEN-C07、BEN-C08、BEN-C16、BEN-C25、OPS-C07、OPS-C16；支持 evidence：BEN-EV13、BEN-EV14、BEN-EV15、BEN-EV16、BEN-EV31、BEN-EV32、BEN-EV49、BEN-EV50、OPS-J07、OPS-J16；反对/限定 claims：BEN-C22；反对/限定 evidence：BEN-EV43、BEN-EV44。）

## GitHub 实现模式与集成决策

固定提交揭示的不是“最佳项目排名”，而是三种可组合模式。Sibyl-Memory 代表 local-first schema family：client 以 per-tenant SQLite/FTS5 为权威，MCP、Hermes、LangGraph、CLI 是表面，适合单机/边缘，但没有跨主机协调证据；legacy Letta V1 把直接进入 prompt 的 core blocks 与 archive/source passages 分开，经 server manager、SQLAlchemy 和可选外部 archive 承载，说明 service API 与 prompt state 可分层，但当前 Letta 架构不在该固定 profile；Mem0 代表 provider facade，通过 LLM/embedder/vector/reranker factory 和 SQLite history 组合多个 backend，集成面广，却存在 backend capability 差异和 OSS/managed 归因边界。三者共同支持“接口与权威状态必须分开”，不支持“某一仓库已经验证完整 control plane”。（支持 claims：PRJ-A001、PRJ-I001、PRJ-C001、PRJ-M001、PRJ-A014、PRJ-I014、PRJ-C014、PRJ-M014、PRJ-A015、PRJ-I015、PRJ-C015、PRJ-M015；支持 evidence：PRJ-AE001-01、PRJ-IE001-01、PRJ-E001、PRJ-ME001、PRJ-AE014-01、PRJ-IE014-01、PRJ-E014、PRJ-ME014、PRJ-AE015-01、PRJ-IE015-01、PRJ-E015、PRJ-ME015；反对/限定 claims：none；反对/限定 evidence：none。）

集成时应先回答“谁是 source of truth、失败后从哪里重建、scope 在哪一层强制、版本怎样传播”，再选 SDK、MCP 或 server。若 SQLite/ledger 是权威，vector/graph 只能是可重建 projection；若 managed backend 是权威，则本地 history/cache 需定义一致性和删除传播；若 legacy server 正在迁移，必须把 migration/compatibility 作为独立验收项，不能以 lineage 或 stars 代替。这个顺序减少了将 adapter、index 或 prompt block 误认成完整 memory system 的风险。（支持 claims：PRJ-C001、PRJ-C014、PRJ-C015、FND-C17、OPS-C21；支持 evidence：PRJ-E001、PRJ-E014、PRJ-E015、FND-EV32、FND-EV33、OPS-J21；反对/限定 claims：none；反对/限定 evidence：none。）

## 成本、可观测性与运行负担

成本不能只报 retrieval latency。write 侧至少分离抽取/验证模型调用、embedding、transaction/ledger 写放大和多索引更新；manage 侧记录 consolidation、dedup、reindex、checkpoint、rollback 与 human review；read 侧记录候选数、各路召回、rerank、context tokens 与 stale/conflict rate；action 侧记录重新授权和失败恢复。已有证据只说明 retention 与 consolidation 存在预算权衡、不同策略没有普适排名，尚没有覆盖全链的可比测量，因此这些字段是测量契约，不是已验证的成本优势。（支持 claims：FND-C19、FND-C20、REP-C18、BEN-C25；支持 evidence：FND-EV36、FND-EV37、FND-EV38、FND-EV39、REP-V36、REP-V37、BEN-EV49、BEN-EV50；反对/限定 claims：none；反对/限定 evidence：none。）

可观测性的最小单位应是一次 state transition 与一次 evidence-to-action trace：receipt、source、revision、scope、controller decision、index watermark、query fingerprint、selected/unselected candidate、compiled tokens、action authorization 和 outcome。没有这些字段，即使最终 QA 分数变化，也无法归因是控制策略、retriever、预算还是 reader model；而只记录 provenance 又不能证明内容为真或旧规则已被语义取代。（支持 claims：FND-C17、REP-C18、OPS-C13、OPS-C17、BEN-C22；支持 evidence：FND-EV32、FND-EV33、REP-V36、REP-V37、OPS-J13、OPS-J17、BEN-EV43、BEN-EV44；反对/限定 claims：none；反对/限定 evidence：none。）

## Benchmark protocol 与可比性

MM-C01 不应只用 post-hoc recall QA 验收。最低协议应覆盖：长程信息获取、跨 session 保留、显式修订/冲突、forget/purge、checkpoint/restore、scope isolation、poison write、修复后行为、以及 memory 驱动的 tool/action outcome；每次运行固定 dataset/version、history construction、模型、agent wrapper、backend、write policy、retriever、k/token/tool budget、seed 与 judge，并保存 protocol fingerprint。MemoryAgentBench 的 incremental competencies 与 MemSecBench 的 Write–Execute–Forget 可提供不同切面，但二者不能合并成一个总分。（支持 claims：BEN-C03、BEN-C16、BEN-C22、BEN-C25、FND-C13；支持 evidence：BEN-EV05、BEN-EV06、BEN-EV31、BEN-EV32、BEN-EV43、BEN-EV44、BEN-EV49、BEN-EV50、FND-EV24、FND-EV25；反对/限定 claims：none；反对/限定 evidence：none。）

比较 passive store 与 control-plane 方案时，必须匹配 raw/constructed input、reader、candidate depth、answer/context token cap 和 backend，并分别报告 correctness、state integrity、recovery、action success 与成本；否则 controller 可能只是借到更多模型调用或 tokens。独立 LightMem 复现表明，固定 store 时仅 retriever 变化即可把报告准确率从 58.1% 推到 75.5%，且 matched depth 下 raw-turn 往往更强，这构成对“架构越复杂越好”的直接限定，而不是对可变持久系统控制需求的否定。（支持 claims：REP-C05、REP-C06、REP-C17、BEN-C22；支持 evidence：REP-V09、REP-V10、REP-V11、REP-V12、REP-V33、REP-V34、BEN-EV43、BEN-EV44；反对/限定 claims：FND-C14、FND-C15；反对/限定 evidence：FND-EV26、FND-EV28、FND-EV29。）

## 限制、失败模式、负证据与替代方案

控制面会引入自身风险：错误 admission 使污染持久化，错误 consolidation 隐去原证据，错误 forget 造成 false deletion 或 hidden dependency，controller policy 可能随任务漂移，snapshot 可恢复字节但未必恢复正确语义，signed provenance 证明谁改了什么却不证明内容真实。更严峻的是 sleeper memory 可在后来被检索并驱动行动，而当前证据没有一套经端到端验证的 full-chain defense；因此 detector、policy、snapshot 和 action authorization 应被看作相互补充，而非单点证明安全。（支持 claims：OPS-C01、OPS-C07、OPS-C12、OPS-C13、OPS-C16、OPS-C17、OPS-C24、OPS-C27；支持 evidence：OPS-J01、OPS-J07、OPS-J12、OPS-J13、OPS-J16、OPS-J17、OPS-J24、OPS-J27、OPS-J45；反对/限定 claims：none；反对/限定 evidence：none。）

替代方案按条件而不是排名选择：短期静态 QA 可保留 raw history + simple retrieval，避免抽取丢失；单机个人 agent 可选 local-first SQLite/FTS + append ledger + 定期 snapshot；多租户或共享状态需要独立 service、强 scope 与 revision；强关系/时间任务再引入 graph/bitemporal projection；高风险行动必须加 action-time gate。若系统无法承担完整链，应明确裁剪层及其不可提供的保证，而不是把简化实现命名为完整 Memory OS。（支持 claims：REP-C06、REP-C22、EXP-C18、OPS-C19、BEN-C25、PRJ-A001、PRJ-C001；支持 evidence：REP-V11、REP-V12、REP-V43、REP-V44、EXP-V35、EXP-V36、OPS-J19、BEN-EV49、BEN-EV50、PRJ-AE001-01、PRJ-E001；反对/限定 claims：none；反对/限定 evidence：none。）

## 共识、分歧、成熟度与决策含义

**共识**是持久可变 memory 需要把 data、retrieval、mutation/control 与 action-use 分开观察；**条件共识**是六层外部链适合跨 session、可修改、会驱动行动的部署；**争议**是 learned controller、transaction/bitemporal 契约与复杂 constructed memory 是否在相同预算下稳定创造净收益；**证据不足**是某个仓库已经实现并运行验证全部链、跨 backend 的 recovery 与 delete 完整性、以及独立生产采用。职责分层和固定提交架构读取可评为较成熟，typed external state/hybrid retrieval 为中等，learned control、跨 backend transaction、端到端 deletion 与 model-native bridge 仍早期。（支持 claims：FND-C14、FND-C17、FND-C23、REP-C05、REP-C06、REP-C22、OPS-C27；支持 evidence：FND-EV26、FND-EV32、FND-EV33、FND-EV44、FND-EV45、FND-EV46、REP-V09、REP-V10、REP-V11、REP-V12、REP-V43、REP-V44、OPS-J27、OPS-J45；反对/限定 claims：none；反对/限定 evidence：none。）

采购或自研决策应以四个 gate 收敛：一，明确 source of truth 与 topology；二，用状态机列出 write/manage/read/action 及可恢复点；三，在目标 protocol family 下做 pinned、matched-budget 运行；四，将 scope leakage、poisoning、stale behavior、delete propagation 和 rollback 纳入上线阻断项。反转本稿主判断所需的证据是：多个 backend、同模型同任务同预算的独立实验持续表明 passive/raw-history 方案在 update、conflict、forget、recovery、action success 与成本上等同或更好；在此之前，简化可作为条件性方案，不能泛化成成熟共识。（支持 claims：FND-C17、BEN-C16、BEN-C22、OPS-C07、OPS-C16、REP-C05、REP-C06；支持 evidence：FND-EV32、FND-EV33、BEN-EV31、BEN-EV32、BEN-EV43、BEN-EV44、OPS-J07、OPS-J16、REP-V09、REP-V10、REP-V11、REP-V12；反对/限定 claims：none；反对/限定 evidence：none。）

## 已命名缺口

- `GAP-CNS-01`：MemCon、MemTxn、budgeted consolidation、ForgetEval 缺跨 backend、同任务流、同预算独立复现。
- `GAP-CNS-09`：缺 model-native/latent 与 external memory 在 persistence、update、delete、provenance、auditability、cost、recovery 上的匹配对照。
- `GAP-CNS-10`：selected repositories 未做 pinned install/test、维护健康、license 与 independent downstream deployment 验证。
- `GAP-CNS-12`：缺覆盖 write/retrieve/consolidate/delete/repair/action 的全链成本与 SLO 测量。
- `GAP-CNS-13`：canonical Graphiti entity 尚未完成 identity、commit、release、paper relation 重建。
- `GAP-CNS-14`：legacy Letta V1 之外的当前 Letta architecture、release、migration、compatibility 尚未专属深检。

这些缺口限定的是部署置信度，而不是继续增加相似项目简介的理由；下一轮优先级应是 matched execution、migration/recovery drill 和 canonical entity repair。（支持 claims：FND-C17、REP-C19、EXP-C22、BEN-C23；支持 evidence：FND-EV32、FND-EV33、REP-V38、REP-V39、EXP-V43、EXP-V44、BEN-EV45、BEN-EV46；反对/限定 claims：none；反对/限定 evidence：none。）

## 实际饱和轮次

`SAT-CL-MM-C01` 在 `2026-08-10T10:54:07Z` 记录为 `saturated`：已消费 14 个 targeted queries、23 个 deep-verified memberships；最终可回放轮次是 `FM-EV-CLUSTER-MM-C01-11` 与 `FM-EV-CLUSTER-MM-C01-12`。停止规则是连续两个 breadth wave 不再增加 first-order leaf，且 targeted deep/negative/implementation follow-up 不再改变本簇边界或决策命题；六个 residual gaps 仍按上述 ID 保留。这里的“饱和”只表示本轮映射/命题边界稳定，不表示技术已经成熟或缺口已关闭。（过程记录：SAT-CL-MM-C01；支持 claims：none；支持 evidence：none；反对/限定 claims：none；反对/限定 evidence：none。）


## 补充可审计工程判断

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

MemoryBank separates storage, retrieval, and updating; its store includes conversation records, event summaries, and evolving user-personality assessments.
<!-- claim:FND-C05 -->

<!-- synthesis:CLY-C01 claims:FND-C03,FND-C05,FND-C11,FND-C17,FND-C23 clusters:MM-C01 -->
