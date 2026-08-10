# MM-C11｜共享、分布式与可移植记忆：深度报告

**状态：** final standalone cluster report；已纳入 v09 bundle。  
**研究截止：** 2026-08-10。  
**证据边界：** 本稿只把当前 bundle 中 `publication_status=published` 且 semantic check=`pass` 的 claim 用于技术正文；设计图、状态机、成本式和决策门均标为本报告综合，不伪装成某一来源的规范。第三方仓库没有在本次扩写中运行。

## 1. 决策摘要与簇边界

C11 不是“给多个 Agent 接一个向量库”。它研究的是：持久状态一旦跨 user、agent、team、tenant、host 或产品边界流动，如何同时保住主体身份、可见范围、写入权、来源、版本、冲突、撤销和可移植语义。只发生消息交换、却没有可复用持久状态的 multi-agent communication 不属于本簇；只优化单用户长期画像而不涉及跨主体授权的工作属于 C08；只讨论存储/索引而不处理共享语义的工作属于 C02–C04。当前账本对 MM-C11 有 297 个映射实体，其中 160 个 primary membership；类型为 151 papers、127 repositories、11 products、2 standards 和 6 other，滚动 12 个月/90 天覆盖分别为 243/130。后四组数字是 `cluster_assignments.jsonl × entities.jsonl` 的范围审计，不是质量分数。

**段落证据** — Claims: `EXP-C18`, `EXP-C19`. Evidence: `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`. Coverage inputs: `bundle/cluster_assignments.jsonl`, `bundle/entities.jsonl`.

需要把三个经常混写的目标拆开：**shared memory** 决定谁能看到和改变同一事实；**distributed memory** 决定同一逻辑状态如何跨副本、断连和并发写保持可解释；**portable memory** 决定状态离开原实现后，哪些字段、关系和生命周期不变量仍然成立。共享但不分布可以是一台机器上的 team store；分布但不共享可以是同一 owner 的多设备复制；可移植但不共享可以只是单用户 export/import。三者重叠处才需要完整的 identity/scope/authority/version/revocation contract。

**段落证据** — Claims: `EXP-C18`, `EXP-C19`, `STD-C018`, `SAT-STD-C023`. Evidence: `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `STD-J035`, `STD-J036`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`.

本稿的决策结论是：目前可采购或集成的是若干**项目级协议、格式、服务契约和本地纪律**，不是一个已经形成独立实现生态的通用 memory standard。工程团队应先冻结自己的主体/范围/冲突/删除不变量，再选择 transport、schema 和 adapter；不能反过来让某个 MCP server 或 JSON schema 暗中决定安全模型。

**段落证据** — Claims: `STD-C028`, `STD-C029`, `SAT-STD-C023`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `STD-J057`, `STD-J058`, `STD-J059`, `STD-J060`, `STD-J061`, `STD-J062`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`.

## 2. 演进脉络：从共享池到可治理交换

早期 shared-memory 路线首先解决“其他 Agent 能否取得我写过的信息”。INMS 式共享 conversational pool 证明共享可见性本身是一个独立机制；随后 Collaborative Memory 把 private/selective fragments 和动态访问控制放到模型中。由此产生的关键演进不是 store 从本地变远程，而是共享对象从“可检索文本”变成“带 principal、scope 和 policy 的状态”。如果 provenance 与撤销仍然缺席，一个共享池只能证明 availability，不能证明 organizational memory。

**段落证据** — Claims: `EXP-C18`, `EXP-C19`. Evidence: `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`.

第二条演进线来自 portability。工程仓库已经出现三种互不等价的“可移植”：memory object/API、单文件 agent 配置与可编辑记忆、以及 Markdown/Wiki 资产。它们分别优化机器校验、整体迁移和人类可检查性；因此 portable 不是布尔属性，而是要声明被搬运的对象层级、允许的变换和丢失预算。`add/remember`、`search/recall`、`forget/update` 等动词形成了表面接口趋同，但返回对象、更新语义、检索行为和 skill promotion 仍不一致。

**段落证据** — Claims: `GR-C-M008`, `GR-C-M016`, `GR-C-M017`. Evidence: `GR-V-M008-01`, `GR-V-M008-02`, `GR-V-M008-03`, `GR-V-M008-04`, `GR-V-M016-01`, `GR-V-M016-02`, `GR-V-M016-03`, `GR-V-M016-04`, `GR-V-M017-01`, `GR-V-M017-02`, `GR-V-M017-03`.

第三条演进线是规范化：MCP 先成为相邻的 context/tool exchange layer，memory-specific work 随后分化成 record interchange、service contract、local discipline、verifiable fact protocol 和 committed-working-context bundle。2026 年的新项目把 schema、OpenAPI、test vectors、runner 或 compliance suite 做得更可执行，但治理成熟度没有随资产数量自动提升。

**段落证据** — Claims: `STD-C007`, `STD-C018`, `STD-C029`, `SAT-STD-C014`, `SAT-STD-C016`, `SAT-STD-C018`, `SAT-STD-C019`, `SAT-STD-C023`. Evidence: `STD-J013`, `STD-J014`, `STD-J035`, `STD-J036`, `STD-J060`, `STD-J061`, `STD-J062`, `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J032`, `SAT-STD-J033`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J039`, `SAT-STD-J040`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`.

## 3. 状态模型：identity、scope、authority、consistency、version、revocation

下面是本报告建议的最小共享对象，不是现有任何单一规范的照抄：

| 不变量 | 最小状态 | 为什么不能省略 | 典型破坏方式 |
|---|---|---|---|
| identity | `subject_id`, `agent_id`, `tenant_id`, issuer | 将“谁的事实”和“谁在操作”分开 | recall/store 使用不同 identity，数据写入后不可达或串租 |
| scope | private/user/team/project/org + purpose | 同一内容对不同 principal 形成不同 view | 把 metadata 中的 namespace 当成 ACL |
| authority | owner、writer、reader、sharer、revoker、policy version | 写权限、分享权限与行动权限不是同一个权利 | 旧 token 或旧 policy 继续驱动读/行动 |
| consistency | revision、parents、conflict state、merge record | 并发与离线副本必须留下可解释结果 | silent last-write-wins 覆盖合法更新 |
| version | record schema、protocol、adapter、embedding/index fingerprint | wire compatibility 不等于 derived-state compatibility | 旧 adapter 输出可解析但丢失新字段 |
| revocation | revoked-at、reason、affected derivations、repair status | “以后不返回”不等于清除了传播副本 | 向量、摘要、profile、skill、backup 仍保留影响 |

**表格证据** — Claims: `EXP-C18`, `EXP-C19`, `FND-C17`, `FND-C21`, `REP-C22`, `PRJ-I004`, `PRJ-I005`, `PRJ-I011`, `SAT-STD-C007`, `SAT-STD-C016`. Evidence: `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `REP-V43`, `REP-V44`, `PRJ-IE004-01`, `PRJ-IE004-02`, `PRJ-IE005-01`, `PRJ-IE011-01`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J032`, `SAT-STD-J033`.

这六项必须在 state transition 中共同出现，而不能分别藏在数据库列、HTTP header、README 约定和向量 metadata 里。Scope Recall Hermes 明确区分 `general` scratch 与 `user/memory/project/ops` durable scopes，并把中央 PostgreSQL 场景留给已有 source of truth；Raven 则暴露了相反方向的失败条件：`memory.userId` 与 `memory.agentId` 是身份源，recall/store 不一致会造成不可召回。SMJAI OMP 的 `source.user_id` 与 namespace 是数据字段，固定代码面并没有因此自动获得组织级 tenant enforcement。

**段落证据** — Claims: `PRJ-A004`, `PRJ-I004`, `PRJ-A005`, `PRJ-I005`, `PRJ-I011`. Evidence: `PRJ-AE004-01`, `PRJ-AE004-02`, `PRJ-AE004-03`, `PRJ-IE004-01`, `PRJ-IE004-02`, `PRJ-AE005-01`, `PRJ-AE005-02`, `PRJ-AE005-03`, `PRJ-IE005-01`, `PRJ-IE011-01`.

## 4. 参考架构：权威账本与可重建投影分离

本报告把 C11 部署架构压缩为六层：`event/evidence ledger → typed/versioned state → materialized indexes → lifecycle/sync controller → scoped context compiler → action authorization`。前两层回答“发生了什么、当前有效状态是什么”；索引只回答“如何高效找到候选”；controller 负责 merge、supersede、revoke、repair；compiler 根据当前 principal、policy、time 与 budget 构造 view；行动层最后一次验证当前权限。任何一层丢掉 scope、version 或 provenance，后层都无法可靠补回。

**段落证据** — Claims: `FND-C17`, `FND-C21`, `FND-C23`, `REP-C22`, `EXP-C18`, `EXP-C19`. Evidence: `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `FND-EV44`, `FND-EV45`, `FND-EV46`, `REP-V43`, `REP-V44`, `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`.

```text
Host / Agent / Operator
        │ identity + request scope + policy version
        ▼
Ingress & adapters ──► append-only evidence / operation journal
                              │ validate + assign revision/parents
                              ▼
                    authoritative typed state
                      │       │        │
                      ▼       ▼        ▼
                    FTS    vector    graph/profile/summary
                       \      |       /
                        scoped/time-aware retrieval
                                 │ budgeted compilation
                                 ▼
                         prompt / tool / action gate
                                 │ result + provenance
                                 └────────► new journal event
```

**图示证据** — Claims: `FND-C17`, `FND-C23`, `REP-C22`, `PRJ-A004`, `PRJ-A011`. Evidence: `FND-EV32`, `FND-EV33`, `FND-EV44`, `FND-EV45`, `FND-EV46`, `REP-V43`, `REP-V44`, `PRJ-AE004-01`, `PRJ-AE004-02`, `PRJ-AE004-03`, `PRJ-AE011-01`, `PRJ-AE011-02`, `PRJ-AE011-03`.

真实仓库已经展示了这个分层的局部形状。Scope Recall Hermes 把 SQLite 作为 truth，把 LanceDB、brute-force 或 PGVector 作为 companion；SMJAI OMP 的 SQLite/FTS5 triggers 同步文本索引，却只是 quoted-term FTS，schema 中可容纳 embedding 不等于实现了向量检索。这两例共同支持“权威状态与检索投影分离”，也提醒 adapter 不能把可选索引能力误报成协议能力。

**段落证据** — Claims: `PRJ-A004`, `PRJ-I004`, `PRJ-A011`, `PRJ-I011`. Evidence: `PRJ-AE004-01`, `PRJ-AE004-02`, `PRJ-AE004-03`, `PRJ-IE004-01`, `PRJ-IE004-02`, `PRJ-AE011-01`, `PRJ-AE011-02`, `PRJ-AE011-03`, `PRJ-IE011-01`.

## 5. Write → Manage → Read → Action 数据流

**Write。** 原始 turn、tool result 或外部事实先进入 evidence journal，而不是直接成为 team truth。入口绑定 actor、subject、tenant、source、scope proposal 与 policy version，执行 schema/size/source validation 后产生不可变 revision；“是否分享”是显式 transition。MemTxn 的 source-supported write validation 和 snapshot journal、Scope Recall Hermes 的 journal→digest/candidate→promotion 形状，都说明 capture 与 durable fact 应分层。

**段落证据** — Claims: `FND-C17`, `PRJ-A004`, `EXP-C18`. Evidence: `FND-EV32`, `FND-EV33`, `PRJ-AE004-01`, `PRJ-AE004-02`, `PRJ-AE004-03`, `EXP-V35`, `EXP-V36`.

**Manage。** Controller 对 revision 做 supersede、merge、conflict quarantine、share、revoke、TTL/purge 和 derived-state repair。并发写不得只留下最终文本；至少保留 parent set、winner/merge rationale 和未决 conflict。删除也不能缩成一个 `deleted=true`：ForgetEval 区分 supersede、release、purge，说明逻辑隐藏、停止使用与物理移除是不同操作；portable export 必须声明它携带哪一种状态。

**段落证据** — Claims: `FND-C17`, `FND-C21`, `REP-C22`. Evidence: `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `REP-V43`, `REP-V44`.

**Read。** 查询先用当前 principal、tenant、purpose、time 与 policy 形成 eligible set，再做 lexical/vector/graph retrieval 与 budgeted compilation。先 global top-k、后过滤会泄漏存在性、分数或摘要衍生物；因此 scope 必须进入 candidate generation，而不只是最后一层 prompt redaction。Retain/consolidate 的收益依 budget 而变，说明共享系统还要把保真、覆盖和 token cost 放入 view construction。

**段落证据** — Claims: `FND-C19`, `REP-C22`, `EXP-C19`, `PRJ-I004`. Evidence: `FND-EV36`, `FND-EV37`, `REP-V43`, `REP-V44`, `EXP-V37`, `EXP-V38`, `PRJ-IE004-01`, `PRJ-IE004-02`.

**Action。** Memory 命中只产生带 provenance、revision 与 scope 的 candidate，不直接授予 tool 权限。行动前重新检查当前 principal、policy、revocation 与 artifact type；行动结果以新 event 回写，以便撤销依赖和审计。尤其是 shared skill：一旦轨迹被晋升为持久指令，污染就从“错误信息”升级为“行为改变”，所以 promotion 和 invocation 必须有不同的授权门。

**段落证据** — Claims: `EXP-C18`, `FND-C23`, `FM-PE-C01`, `FM-PE-C05`. Evidence: `EXP-V35`, `EXP-V36`, `FND-EV44`, `FND-EV45`, `FND-EV46`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J06`, `FM-PE-J07`.

## 6. 规范地位：MCP、W3C CG、SAIHM 与 UMP 不能混称

| Artifact | 截止状态 | 正确称谓 | 可依赖的边界 | 不应声称 |
|---|---|---|---|---|
| W3C AI Agent Memory Interoperability | 2026-06-03 创建、开放 | W3C Community Group | 标准讨论与未来 deliverable 场所 | W3C Recommendation、正式标准、采用证明 |
| SAIHM `draft-...-01` | stream None；无 RFC/std level | individual Internet-Draft | 可公开审阅的提案 | IETF 标准或 IETF endorsement |
| MCP 2026-07-28 | 官方相邻协议；扩展列 Authorization、Apps、Tasks | context/tool exchange protocol | host/client/server、prompts/resources/tools、扩展与 task lifecycle | durable memory record、检索、consolidation、forgetting 语义 |
| edihasaj UMP | 固定 v1.0 project release/schema | versioned project specification | portable record/operation 及 MCP/HTTP/file bindings | SDO 标准、生态共识、外部 v1.0 conformance |

**表格证据** — Claims: `SAT-STD-C001`, `SAT-STD-C003`, `SAT-STD-C004`, `SAT-STD-C005`, `STD-C007`, `STD-C018`, `STD-C029`. Evidence: `SAT-STD-J001`, `SAT-STD-J004`, `SAT-STD-J005`, `SAT-STD-J006`, `SAT-STD-J007`, `SAT-STD-J008`, `STD-J013`, `STD-J014`, `STD-J035`, `STD-J036`, `STD-J060`, `STD-J061`, `STD-J062`.

MCP Tasks 的 durable handle 很容易造成术语误判：它持久的是长操作的 handle、poll/reconnect/input-required lifecycle，不是 memory object 的 provenance、revision、scope 或删除。MCP 因而适合作为 adapter transport 或 maintenance-job surface，但 memory semantics 必须来自上层 contract。反过来，UMP 即使定义了 record 与 bindings，也明确把 retrieval、embedding、ranking、summarization 和 consolidation 留给实现；不能从 wire schema 推断检索质量或生命周期正确性。

**段落证据** — Claims: `SAT-STD-C005`, `STD-C007`, `STD-C018`. Evidence: `SAT-STD-J007`, `SAT-STD-J008`, `STD-J013`, `STD-J014`, `STD-J035`, `STD-J036`.

## 7. 项目规范层：同为“协议”，解决的问题并不相同

| 项目 | 固定状态 | 实际形状 | 正确成熟度边界 |
|---|---|---|---|
| Portable Agent Memory (PAM) | spec v1.0 Draft；SDK 0.1.0；无 tag/release | paper-backed protocol + SDK | 项目草案；版本面尚未对齐 |
| Engram | pinned spec + self-certification checklist | paper-backed governance/portability proposal | 项目草案；无 executable conformance runner |
| HKUDS MGP v0.1.1 | semantic spec、schemas、OpenAPI、gateway、adapters、compliance suite | governed memory service contract | 同项目规范与合规资产，不是 SDO standard |
| Engramory v0.7.0 | file/rules + host adapters | portable local discipline | experimental、single-project/single-writer；无 store migration version |
| eMEM v2.1.0 | protocol、code、SDK/package、conformance assets、project responder | versioned fact protocol/service surface | 项目运营证据；非独立采用 |
| OCF v0.2 Draft | schema、vectors、runner | committed-working-context/governance bundle | 明确不是 wire protocol，也不定义 memory unit |
| glatinone AMP v0.1.0 | draft、server、SDK、tests、同项目 CI | project protocol + reference implementation | 既不是 RFC，也没有独立采用 |
| SMJAI OMP fixed commit | JSON schema、Express server、browser/Claude-MCP/CLI adapters | record/API project spec + reference server | FTS5 reference shape；未验证第三方实现或 production adoption |

**表格证据** — Claims: `SAT-STD-C009`, `SAT-STD-C011`, `SAT-STD-C014`, `SAT-STD-C016`, `SAT-STD-C018`, `SAT-STD-C019`, `SAT-STD-C021`, `PRJ-A011`, `PRJ-I011`. Evidence: `SAT-STD-J017`, `SAT-STD-J018`, `SAT-STD-J021`, `SAT-STD-J022`, `SAT-STD-J023`, `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J032`, `SAT-STD-J033`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J039`, `SAT-STD-J040`, `SAT-STD-J043`, `SAT-STD-J044`, `SAT-STD-J045`, `PRJ-AE011-01`, `PRJ-AE011-02`, `PRJ-AE011-03`, `PRJ-IE011-01`.

这张表揭示的不是“谁最接近统一标准”，而是四种架构层级：record/API、service contract、local discipline、governance/context bundle。把它们放进同一个 protocol leaderboard 会误导：OCF 主动排除了 wire/memory-unit 定义，Engramory 主动接受 single-writer 边界，MGP 与 eMEM 则把更多运行时或验证资产纳入项目。工程采购应先选层级，再比较同层实现。

**段落证据** — Claims: `SAT-STD-C014`, `SAT-STD-C016`, `SAT-STD-C018`, `SAT-STD-C019`, `SAT-STD-C023`. Evidence: `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J032`, `SAT-STD-J033`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J039`, `SAT-STD-J040`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`.

## 8. Portability 与 conformance：adapter 存在不等于语义往返

本报告建议把 portability 分成五级：L0 能导出字节；L1 能通过目标 schema；L2 保留 identity/scope/provenance/version 等不变量；L3 对 update/share/revoke/delete 等 lifecycle operation 等价；L4 由两个独立实现做双向 round trip，并报告 preserved/transformed/lost fields。只有 L1 仍可能产生“语法成功、语义降级”；当前审计最强的公开外部 signal 尚未达到 L4。

**段落证据** — Claims: `STD-C028`, `SAT-STD-C006`, `SAT-STD-C007`, `SAT-STD-C008`, `SAT-STD-C024`. Evidence: `STD-J057`, `STD-J058`, `STD-J059`, `SAT-STD-J009`, `SAT-STD-J010`, `SAT-STD-J011`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J015`, `SAT-STD-J016`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`.

Agent Memory Hall 是最有说明力的反例：它确有双向 UMP/AMH converter、三个 adapter tests 和成功公共 CI；但输出是旧 UMP 0.1-shaped record，`body` 为 string，缺少 UMP 1.0 要求的 `ump` 与 `time` objects。所谓 round-trip 只保留同一 converter 内选定核心字段，并非 schema validation、完整 field-loss audit 或两个组织的往返。正确结论是“真实 partial adapter”，不是“UMP 1.0 compatible”。

**段落证据** — Claims: `SAT-STD-C006`, `SAT-STD-C007`, `SAT-STD-C008`. Evidence: `SAT-STD-J009`, `SAT-STD-J010`, `SAT-STD-J011`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J015`, `SAT-STD-J016`.

PAM/Amore 显示另一种边界：Amore 独立 clean-room 实现了 content-addressed envelope/`prev_hash` idea，这是设计转移；但它不是完整 `.pam` wire format 或 PAM conformance。可移植性报告因此应把**pattern adoption**、**partial adapter**、**full implementation** 和 **current-version conformance** 分列。

**段落证据** — Claims: `SAT-STD-C009`, `SAT-STD-C010`. Evidence: `SAT-STD-J017`, `SAT-STD-J018`, `SAT-STD-J019`, `SAT-STD-J020`.

## 9. 真实实现形状与集成约束

| 固定实现 | 权威状态与投影 | 接入面 | 关键集成约束 | 不能推出 |
|---|---|---|---|---|
| Sibyl Memory `e2241d…` | 每 tenant SQLite + FTS5；五包共享 schema family | client、CLI、MCP、Hermes、LangGraph | SQLite JSON1/FTS5；默认 `~/.sibyl-memory` 为单机文件边界 | 跨主机协调、生产 tenant isolation |
| Scope Recall Hermes `867b99…` | journal/SQLite truth；LanceDB、brute-force、PGVector companion | Hermes provider + scripts/tests/docs | durable scope 必须正确；已有中央 DB 时插件不是跨 Agent truth | “有 PGVector”即分布式 source of truth |
| Raven `14b741…` | host MemoryBackend Protocol；EverOS adapter | terminal agent、channels、MCP | exact-pinned `everos==1.2.1` internal APIs；userId/agentId identity 必须一致 | adapter 存在即 backend 可互换无迁移成本 |
| SMJAI OMP `2f9124…` | SQLite rows + FTS5 triggers；embedding 字段未进入 reference search | Express、browser、Claude-MCP、CLI | Node 22.5、strict schema limits；namespace/user_id 不是自动 ACL | schema 覆盖即 semantic search/tenant enforcement |

**表格证据** — Claims: `PRJ-A001`, `PRJ-I001`, `PRJ-A004`, `PRJ-I004`, `PRJ-A005`, `PRJ-I005`, `PRJ-A011`, `PRJ-I011`. Evidence: `PRJ-AE001-01`, `PRJ-AE001-02`, `PRJ-AE001-03`, `PRJ-IE001-01`, `PRJ-IE001-02`, `PRJ-AE004-01`, `PRJ-AE004-02`, `PRJ-AE004-03`, `PRJ-IE004-01`, `PRJ-IE004-02`, `PRJ-AE005-01`, `PRJ-AE005-02`, `PRJ-AE005-03`, `PRJ-IE005-01`, `PRJ-AE011-01`, `PRJ-AE011-02`, `PRJ-AE011-03`, `PRJ-IE011-01`.

这些实现共同说明 portability 的真正接口不止 `export()`：还包括 identity mapping、scope mapping、schema/version migration、index rebuild、failure recovery 与 authorization handoff。最危险的集成是把字段映射成功当成安全等价；例如 user/namespace 字段可以被序列化，却未必由目标实现强制执行。部署前应要求 adapter 输出 compatibility report：字段覆盖、默认值、降级、拒绝项、derived-index rebuild 和 security-envelope mapping。

**段落证据** — Claims: `EXP-C18`, `EXP-C19`, `REP-C22`, `PRJ-I004`, `PRJ-I005`, `PRJ-I011`, `SAT-STD-C007`, `SAT-STD-C016`. Evidence: `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `REP-V43`, `REP-V44`, `PRJ-IE004-01`, `PRJ-IE004-02`, `PRJ-IE005-01`, `PRJ-IE011-01`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J032`, `SAT-STD-J033`.

## 10. 成本模型：不要只算向量查询

本报告建议把一次共享记忆操作的总成本写成：

```text
C_total = C_capture + C_validate + C_store + C_index
        + C_sync + C_conflict + C_retrieve + C_compile
        + C_authorize + C_audit + C_revoke_repair + C_human
```

其中 `C_sync` 取决于副本与断连模式，`C_conflict` 取决于并发率和 merge 策略，`C_revoke_repair` 覆盖 summary/profile/vector/skill/backup 等衍生物，`C_human` 覆盖冲突裁决和高风险分享审批。保留 raw detail 与 consolidation 的优先级本来就随 token budget 变化；跨实现迁移还增加 schema validation、embedding/index rebuild 与 dual-write 验证。该式是工程综合，不是已验证的行业成本模型。

**公式依据** — Claims: `FND-C19`, `FND-C21`, `REP-C22`, `PRJ-I001`, `PRJ-I004`, `PRJ-I005`, `PRJ-I011`. Evidence: `FND-EV36`, `FND-EV37`, `FND-EV40`, `FND-EV41`, `REP-V43`, `REP-V44`, `PRJ-IE001-01`, `PRJ-IE001-02`, `PRJ-IE004-01`, `PRJ-IE004-02`, `PRJ-IE005-01`, `PRJ-IE011-01`.

当前证据不足以比较“UMP vs MGP vs eMEM”的 TCO：协议层级不同，且没有统一 workload、部署拓扑、模型调用、同步冲突和删除修复测量。相邻的 AGENTS.md 研究在自己的 coding protocol 中发现 passive context 增加平均推理成本超过 20%，但这不是 C11 benchmark，只能提醒“多携带上下文”不是免费收益。工程 PoC 应至少记录 model calls/tokens、p50/p95 write/read/sync、bytes/revisions、index rebuild、conflict rate、audit retention 与 human-review minutes。

**段落证据** — Claims: `BEN-C22`, `C09-C06`, `SAT-STD-C024`. Evidence: `BEN-EV43`, `BEN-EV44`, `C09-E10`, `C09-E11`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`. Named gap: `GAP-CNS-12`.

## 11. Benchmark：必须把共享正确性、可移植性与行动结果拆开

一个可判定的 C11 benchmark 至少要冻结九类条件：主体/tenant 数、拓扑与网络分区、record/schema/protocol version、write/concurrency mix、scope/policy change schedule、merge rule、retrieval/token/tool budget、model/judge、以及 cleanup/backup/restore。任务族应分为：单写共享、并发冲突、离线合并、跨实现 export/import、撤销传播、删除修复、tenant 隔离、poisoned shared skill 与 action-use。静态 QA、环境任务成功、tool grounding 和 operation/security lifecycle 不是同一个 leaderboard。

**段落证据** — Claims: `BEN-C22`, `FND-C17`, `FND-C21`, `FM-PE-C01`, `FM-PE-C05`. Evidence: `BEN-EV43`, `BEN-EV44`, `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J06`, `FM-PE-J07`.

建议把指标拆成四组：性能为 p50/p95/p99 与 bytes/tokens；一致性为 lost update、unresolved conflict、stale read 和 convergence time；安全/治理为 cross-tenant exposure、unauthorized share/action、revocation propagation 与 derived-copy residue；portability 为 schema pass、field loss、invariant loss、round-trip asymmetry。AMH 的三字段 same-converter round-trip 之所以不足，正因为它没有覆盖 schema、全字段、双实现和 lifecycle invariants。

**段落证据** — Claims: `SAT-STD-C006`, `SAT-STD-C007`, `SAT-STD-C008`, `SAT-STD-C024`, `BEN-C22`. Evidence: `SAT-STD-J009`, `SAT-STD-J010`, `SAT-STD-J011`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J015`, `SAT-STD-J016`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `BEN-EV43`, `BEN-EV44`.

## 12. 失败、污染、tenant 与 deletion

| Failure | 形成机制 | 最低检测 | 修复动作 |
|---|---|---|---|
| schema drift | adapter 仍可运行但版本字段/shape 已变 | normative validation + field diff | 拒绝或显式 downgrade；重做 migration |
| scope confusion | identity/scope 仅作为 metadata | 跨 tenant negative reads/actions | 强制 principal-aware candidate generation |
| concurrent overwrite | single-writer 假设被部署拓扑打破 | partition + concurrent write test | 保留 parents/conflict；人工或规则 merge |
| shared-skill poisoning | 不可信轨迹被晋升为持久指令 | promotion lineage + diverse provenance | quarantine、rollback、撤销已传播 artifact |
| stale derived state | truth 已 supersede/purge，index/summary/profile 仍旧 | dependency walk + residue scan | rebuild/invalidate 所有 derived copies |
| revoke-after-use | 旧事实已进入计划、tool call 或下游 skill | action provenance + policy-version audit | 停止行动、补偿、重新规划并记录 incident |

**表格证据** — Claims: `SAT-STD-C007`, `SAT-STD-C008`, `SAT-STD-C016`, `EXP-C18`, `EXP-C19`, `PRJ-I011`, `FM-PE-C01`, `FM-PE-C04`, `FM-PE-C05`, `FND-C21`, `REP-C22`. Evidence: `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J015`, `SAT-STD-J016`, `SAT-STD-J032`, `SAT-STD-J033`, `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `PRJ-IE011-01`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J05`, `FM-PE-J06`, `FM-PE-J07`, `FND-EV40`, `FND-EV41`, `REP-V43`, `REP-V44`.

PoisonedEvolution 的结果不能直接当生产攻击率，但它把 shared skill 的特殊风险说清楚：持久 artifact modification 与实际 trigger/action 是不同阶段；作者的 provenance-diversity gate 只是一个 preliminary pilot。设计上应把 promotion、distribution、invocation 和 revocation 分开审计，而不是用一个 trust score 代替全过程。

**段落证据** — Claims: `FM-PE-C01`, `FM-PE-C04`, `FM-PE-C05`. Evidence: `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J05`, `FM-PE-J06`, `FM-PE-J07`.

Deletion 是 C11 最容易被接口动词掩盖的失败面。`forget` 可能只是不再检索，也可能是 supersede、release、purge；跨副本、向量、摘要、profile、audit 和 backup 的 physical removal 没有共同 end-to-end contract。决策者应要求 deletion manifest：每个 authoritative/derived location 的状态、最后修复时间、不可删除审计例外及恢复测试。

**段落证据** — Claims: `FND-C21`, `FND-C23`, `REP-C22`. Evidence: `FND-EV40`, `FND-EV41`, `FND-EV44`, `FND-EV45`, `FND-EV46`, `REP-V43`, `REP-V44`. Named gap: `GAP-CNS-02`.

## 13. Adoption 证据边界：两条弱信号，不是零，也不是成熟采用

采用证据应分六级：项目自述/registry listing < 外部 mention < 外部 unversioned integration < version-pinned dependency < independent conformance < independently attributable production deployment。W3C participant、GitHub star、README customer logo、项目 operated endpoint 和同组织 reference implementation 都不能跨级。当前审计发现的是两条弱外部 integration 加一条 partial design uptake，而不是 current-version ecosystem conformance。

**段落证据** — Claims: `SAT-STD-C002`, `SAT-STD-C010`, `SAT-STD-C017`, `SAT-STD-C018`, `SAT-STD-C020`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `SAT-STD-J002`, `SAT-STD-J003`, `SAT-STD-J019`, `SAT-STD-J020`, `SAT-STD-J034`, `SAT-STD-J035`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J041`, `SAT-STD-J042`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`.

| Signal | 独立性 | 版本/一致性 | 可发布结论 |
|---|---|---|---|
| Agent Memory Hall ↔ UMP | 不同 repo/owner | adapter 固定，但语义是旧 0.1 shape | 真实 partial adapter；非 UMP 1.0 conformance |
| Amore ↔ PAM idea | 不同 repo/owner | pinned clean-room pattern | provenance-chain pattern adoption；非完整 PAM |
| Agent Team Kit ↔ Engramory | 外部 non-fork repo | upstream clone 未 pin | 真实弱集成；无 conformance/CI/production report |
| Artesian ↔ OCF | 同一 organization | 有 reader/writer/fixtures | reference implementation；非独立 adoption |
| eMEM responder/registry | project-owned | 有项目版本与资产 | distribution/operation evidence；非独立 deployment |
| Engram writer claims | project claim 未被 exact search corroborate | n/a | 不发布为 adoption fact |

**表格证据** — Claims: `SAT-STD-C006`, `SAT-STD-C007`, `SAT-STD-C010`, `SAT-STD-C012`, `SAT-STD-C017`, `SAT-STD-C018`, `SAT-STD-C020`, `SAT-STD-C025`. Evidence: `SAT-STD-J009`, `SAT-STD-J010`, `SAT-STD-J011`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J019`, `SAT-STD-J020`, `SAT-STD-J024`, `SAT-STD-J025`, `SAT-STD-J034`, `SAT-STD-J035`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J041`, `SAT-STD-J042`, `SAT-STD-J056`, `SAT-STD-J057`.

因此准确的 bounded abstention 是：在已记录并打开的公共来源与搜索范围内，没有验证到 promoted memory-specific specs 的 current-version external conformant implementation、independent versioned conformance report 或 two-party round-trip loss report；生产采用侧仍只有前述弱集成，eMEM/OCF 的相关资产分别受 project-owned 与 same-organization 边界约束。它不覆盖私有部署、未索引代码、vendored/renamed 实现或截止日之后的发布。

**段落证据** — Claims: `STD-C026`, `SAT-STD-C017`, `SAT-STD-C018`, `SAT-STD-C020`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `STD-J051`, `STD-J052`, `STD-J053`, `STD-J054`, `SAT-STD-J034`, `SAT-STD-J035`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J041`, `SAT-STD-J042`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`.

## 14. 共识、分歧与决策门

**较强共识。** 共享 store 本身不构成可治理组织记忆；principal/scope/authority 必须显式化。Transport、record、retrieval 和 lifecycle 也是不同层：MCP 不定义 memory semantics，UMP 不定义 retrieval/consolidation。工程接口的动词虽趋同，语义仍未统一。

**段落证据** — Claims: `EXP-C18`, `EXP-C19`, `STD-C007`, `STD-C018`, `GR-C-M016`. Evidence: `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `STD-J013`, `STD-J014`, `STD-J035`, `STD-J036`, `GR-V-M016-01`, `GR-V-M016-02`, `GR-V-M016-03`, `GR-V-M016-04`.

**证据薄弱的共识。** 项目层正在收敛到 schema/API、MCP/HTTP/file bindings 与 executable conformance assets，但没有收敛到 canonical record、security envelope、version/merge/revocation、retrieval/consolidation 或共同 test suite。这里的 `evidence-thin` 不是“没有工作”，而是独立组织、同版本、同协议的验证不足。

**段落证据** — Claims: `STD-C028`, `SAT-STD-C014`, `SAT-STD-C018`, `SAT-STD-C021`, `SAT-STD-C023`, `SAT-STD-C024`. Evidence: `STD-J057`, `STD-J058`, `STD-J059`, `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J043`, `SAT-STD-J044`, `SAT-STD-J045`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`.

**主要分歧。** 一条路线追求严格、小型、可传输 record；一条路线把 lifecycle/interop profiles 做成 service contract；一条路线优先 local-first、人类可读 discipline；另一条路线搬运“当前承诺与治理证据”而非 memory units。没有证据证明其中一种能无损覆盖其他层级，选择应由部署边界决定，而不是由名称中的 `open`、`universal`、`protocol` 或 `RFC` 决定。

**段落证据** — Claims: `GR-C-M008`, `GR-C-M017`, `SAT-STD-C014`, `SAT-STD-C016`, `SAT-STD-C019`, `SAT-STD-C021`, `SAT-STD-C023`. Evidence: `GR-V-M008-01`, `GR-V-M008-02`, `GR-V-M008-03`, `GR-V-M008-04`, `GR-V-M017-01`, `GR-V-M017-02`, `GR-V-M017-03`, `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J032`, `SAT-STD-J033`, `SAT-STD-J039`, `SAT-STD-J040`, `SAT-STD-J043`, `SAT-STD-J044`, `SAT-STD-J045`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`.

**决策门。** 进入 PoC 前必须回答：谁是 authoritative owner；是否跨 tenant；断连和并发写怎么合并；revoke/delete 要修复哪些衍生物；adapter 固定到哪个规范/commit；失败时能否导出原始 journal；是否有两方 round trip；谁独立验证过；成本如何按 write/manage/read/action 计量。任一答案为 unknown 时，应缩小共享范围或保留 dual-write/rollback，而不是直接承诺组织级 memory。

**段落证据** — Claims: `FND-C17`, `FND-C21`, `EXP-C18`, `EXP-C19`, `SAT-STD-C007`, `SAT-STD-C008`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `SAT-STD-J012`, `SAT-STD-J013`, `SAT-STD-J014`, `SAT-STD-J015`, `SAT-STD-J016`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`.

## 15. 分层代表证据与命名风险

| 深选层 | 代表项 | 在本簇中的角色 | 证据限制 |
|---|---|---|---|
| foundational mechanism | MemTxn、ForgetEval、controlled-process synthesis | transaction/version/recovery、supersede/release/purge、data/retrieval/control-plane 分离 | 不是 shared-memory 标准 |
| shared/recent research | INMS、Collaborative Memory | shared pool 与 principal/scope/authority 的边界 | 尚无统一生产 benchmark |
| normative/standards | W3C CG、SAIHM、MCP、UMP | 治理状态、相邻 transport、project record spec | 成熟度和规范权威不可互换 |
| project engineering | MGP、Engramory、eMEM、OCF、glatinone AMP、SMJAI OMP | service/local/fact/context/record 各层实现形状 | 多数同项目验证；本次未执行 |
| external integration | AMH、Amore、Agent Team Kit | partial adapter、pattern adoption、unversioned install | 无 current-version independent conformance |
| benchmark/negative | benchmark protocol synthesis、PoisonedEvolution | 揭示 protocol 不可比与 shared-skill promotion 风险 | 不能推出生产发生率或总体排名 |

**表格证据** — Claims: `FND-C17`, `FND-C21`, `FND-C23`, `EXP-C18`, `EXP-C19`, `BEN-C22`, `STD-C029`, `SAT-STD-C006`, `SAT-STD-C010`, `SAT-STD-C014`, `SAT-STD-C016`, `SAT-STD-C017`, `SAT-STD-C018`, `SAT-STD-C019`, `SAT-STD-C021`, `FM-PE-C01`, `FM-PE-C05`, `PRJ-A011`. Evidence: `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `FND-EV44`, `FND-EV45`, `FND-EV46`, `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `BEN-EV43`, `BEN-EV44`, `STD-J060`, `STD-J061`, `STD-J062`, `SAT-STD-J009`, `SAT-STD-J010`, `SAT-STD-J011`, `SAT-STD-J019`, `SAT-STD-J020`, `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J032`, `SAT-STD-J033`, `SAT-STD-J034`, `SAT-STD-J035`, `SAT-STD-J036`, `SAT-STD-J037`, `SAT-STD-J038`, `SAT-STD-J039`, `SAT-STD-J040`, `SAT-STD-J043`, `SAT-STD-J044`, `SAT-STD-J045`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J06`, `FM-PE-J07`, `PRJ-AE011-01`, `PRJ-AE011-02`, `PRJ-AE011-03`.

命名本身已经成为 identity gap。`Universal Memory Protocol` 同时指 edihasaj 的 portable-record interchange 与 Devansh Verma 的 probabilistic identity/context research；`RFC-AMP-001` 同时出现在 glatinone AMP 与 Red Hat AI Americas MemoryHub 的不同 proposal 中。Entity key 必须至少包含 owner、canonical URL、normative document、version/commit 和 artifact type；搜索与 adoption join 不能只用 acronym/title。

**段落证据** — Claims: `SAT-STD-C013`, `SAT-STD-C021`, `SAT-STD-C022`. Evidence: `SAT-STD-J026`, `SAT-STD-J027`, `SAT-STD-J043`, `SAT-STD-J044`, `SAT-STD-J045`, `SAT-STD-J046`, `SAT-STD-J047`.

## 16. 残余缺口、反转条件与真实 saturation

MM-C11 保留六个不能被“saturated”掩盖的 gap：`GAP-CNS-02`（端到端 deletion/derived-copy repair）、`GAP-CNS-05`（dynamic permission、revocation、conflict、poisoning、cross-tenant 与 propagated-skill repair）、`GAP-CNS-07`（完整 attack→repair→action 链）、`GAP-CNS-08`（固定 protocol fingerprint 的可复跑 harness）、`GAP-CNS-10`（pinned execution、release/issue/dependency/license 与独立下游部署）、`GAP-CNS-12`（全链成本）。这些 gap 是下一轮决策性测试，不是附录愿望清单。

**段落证据** — Claims: `FND-C21`, `BEN-C22`, `FM-PE-C01`, `FM-PE-C05`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `FND-EV40`, `FND-EV41`, `BEN-EV43`, `BEN-EV44`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J06`, `FM-PE-J07`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`. Gap ledger IDs: `GAP-CNS-02`, `GAP-CNS-05`, `GAP-CNS-07`, `GAP-CNS-08`, `GAP-CNS-10`, `GAP-CNS-12`.

Cluster saturation 的真实终点是 `SAT-CL-MM-C11`：field-matrix 的 `FM-EV-CLUSTER-MM-C11-11` 与 `FM-EV-CLUSTER-MM-C11-12` 连续两轮分别审计 20/19 个 unique candidates，没有新增 first-order cluster、entity、高信号项或 stance，也没有改变 boundary/proposition；其查询为 `SAT11-C11-OA`, `SAT11-FOUNDATION-OA`, `SAT11-GH-C10C11` 与 `SAT12-C11-ARXIV`, `SAT12-FOUNDATION-ARXIV`, `SAT12-GH-C10C11`。这关闭的是当前 field map 的一阶边界，不关闭上述六个深证据 gap。

**段落证据** — Claims: `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`. Saturation ledger IDs: `SAT-CL-MM-C11`, `FM-EV-CLUSTER-MM-C11-11`, `FM-EV-CLUSTER-MM-C11-12`.

Standards/adoption/product boundary 另有一条独立 saturation 链：`STD-EV-CLUSTER-MM-C11-05` 首次改变 project-spec topology，`-06` 增加弱外部 Engramory integration；之后必须继续到 lane-complete 的 `STD-EV-CLUSTER-MM-C11-09` 与 `-10`，两轮都实际覆盖 adoption、standards、product-boundary 且 `material_change=false`。Cycle 07/08 虽无 material change，却没有共同覆盖所需 lane，因此没有被拿来冒充终止条件。

**段落证据** — Claims: `SAT-STD-C014`, `SAT-STD-C017`, `SAT-STD-C023`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `SAT-STD-J028`, `SAT-STD-J029`, `SAT-STD-J030`, `SAT-STD-J034`, `SAT-STD-J035`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`. Saturation ledger IDs: `STD-EV-CLUSTER-MM-C11-05`, `STD-EV-CLUSTER-MM-C11-06`, `STD-EV-CLUSTER-MM-C11-09`, `STD-EV-CLUSTER-MM-C11-10`, `SAT-LA-STANDARDS`, `SAT-LA-ADOPTION`.

会反转当前判断的证据很明确：W3C/IETF 正式状态变化；两个组织固定到同一 normative version 的实现；带 fixture/tool/commit/hash 的独立 conformance report；双方 import/export 的字段与 lifecycle-loss 报告；动态权限、tenant、revocation、delete/repair 的公开部署测试；以及可归属 operator 的生产 case。出现其中任何一项，都应重开 status、adoption 或 architecture proposition，而不是只把链接追加到清单。

**段落证据** — Claims: `SAT-STD-C001`, `SAT-STD-C003`, `SAT-STD-C024`, `SAT-STD-C025`, `STD-C028`, `STD-C029`. Evidence: `SAT-STD-J001`, `SAT-STD-J004`, `SAT-STD-J005`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`, `STD-J057`, `STD-J058`, `STD-J059`, `STD-J060`, `STD-J061`, `STD-J062`.

---

**最终工程判断：** 默认选择最小共享范围、明确 authoritative truth、保留 append-only provenance、把 index 视为可重建投影、固定 schema/adapter 版本，并把 revoke/delete/action repair 纳入同一状态机。只有在独立 conformance、tenant/failure benchmark 与 operator-attributable adoption 出现后，才把某个项目 spec 从“可试验的互操作资产”升级为“可依赖的组织级 memory contract”。

**结论证据** — Claims: `FND-C17`, `FND-C21`, `FND-C23`, `EXP-C18`, `EXP-C19`, `REP-C22`, `STD-C028`, `STD-C029`, `SAT-STD-C023`, `SAT-STD-C024`, `SAT-STD-C025`. Evidence: `FND-EV32`, `FND-EV33`, `FND-EV40`, `FND-EV41`, `FND-EV44`, `FND-EV45`, `FND-EV46`, `EXP-V35`, `EXP-V36`, `EXP-V37`, `EXP-V38`, `REP-V43`, `REP-V44`, `STD-J057`, `STD-J058`, `STD-J059`, `STD-J060`, `STD-J061`, `STD-J062`, `SAT-STD-J048`, `SAT-STD-J049`, `SAT-STD-J050`, `SAT-STD-J051`, `SAT-STD-J052`, `SAT-STD-J053`, `SAT-STD-J054`, `SAT-STD-J055`, `SAT-STD-J058`, `SAT-STD-J059`, `SAT-STD-J056`, `SAT-STD-J057`.


## 补充可审计工程判断

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

INMS proposes an asynchronous multi-agent shared conversational pool composed of real-time filtering, storage, retrieval, and a retrieval mediator refined from interaction history.
<!-- claim:EXP-C05 -->

Collaborative Memory distinguishes private fragments from selectively shared fragments and attaches provenance plus time-varying read and write policies to the sharing boundary.
<!-- claim:EXP-C06 -->

<!-- synthesis:CLY-C11 claims:EXP-C05,EXP-C06,EXP-C18,EXP-C19,STD-C007,STD-C018,STD-C026,STD-C028,STD-C029,SAT-STD-C001,SAT-STD-C003,SAT-STD-C004,SAT-STD-C005,SAT-STD-C006,SAT-STD-C007,SAT-STD-C014,SAT-STD-C016,SAT-STD-C018,SAT-STD-C019,SAT-STD-C021,SAT-STD-C023,SAT-STD-C024,SAT-STD-C025 clusters:MM-C11 -->
