# 互操作与工程集成：可以连接，不等于已经标准化

Agent Memory 的互操作至少有四个不同问题：主机如何调用服务、一个记忆记录长什么样、版本/删除/来源等生命周期语义怎样保留、以及两个独立实现能否证明无损交换。把它们统称为“支持 MCP”或“符合某协议”会掩盖最关键的差异。

截至 2026-08-10，正式标准化仍早期；项目规格、适配器和同项目 conformance assets 正在增多；独立、当前版本、双向互操作的公开证据仍稀少。

## 互操作沿着生命周期发生

```text
Host / Agent ── transport & tool surface ──► Memory service
                                              │ write: record, provenance, scope
                                              ▼
  export/import ◄── schema & lifecycle ◄── versioned records / derived objects
       │                                      │ manage: update, deletion, migration
       ▼                                      ▼
Other host / store ◄── query & context view ◄── read: filter, explain, authorization
       │
       └──── action: tool call / shared state / audit receipt
```

传输接口解决“怎样发请求”；记录格式解决“字段能否被理解”；生命周期契约决定导入后是否仍能正确更新、撤销和追溯；conformance 才检验两个独立实现是否真能一起工作。任何一层缺失，都可能让“导入成功”只意味着文本被复制。

## 方案谱系与准确地位

| 层次 / 方案 | 解决的互操作问题 | 已能证明 | 不能宣称 | 状态判断 |
|---|---|---|---|---|
| W3C AI Agent Memory Interoperability CG | 社区讨论与规格形成 | 是 W3C Community Group | W3C Recommendation、实现或采用 | 标准形成早期 |
| SAIHM Internet-Draft | 记忆协议的提案 | 是 individual Internet-Draft | IETF 标准或 RFC | 早期提案 |
| MCP 与 Tasks | Host/client/server、工具资源和异步操作句柄 | 相邻 transport/operation lifecycle | Memory record、检索、遗忘的统一语义 | 成熟的邻接协议，不是 Memory 标准 |
| MGP、PAM、UMP、eMEM、AMP 等项目协议 | 记录、服务、治理或可验证事实的具体契约 | 项目内 schema、SDK、测试或 release | SDO 标准、跨生态采用 | 项目规格层，活跃但分散 |
| Engramory / OCF | 文件化规则或 committed working context | 可移植工作纪律/上下文 bundle | 通用 wire protocol 或 memory-unit 标准 | 有用但范围明确的项目格式 |
| 适配器与导入导出 | 具体系统之间的连接 | 一次实现、部分字段映射 | 当前版本的全字段双向 conformance | 需要逐版本审计 |

W3C 的活动是 Community Group，不是 W3C Recommendation；SAIHM 在快照时是 stream None、无 RFC 和 standards level 的 individual Internet-Draft。两者都应被描述为标准形成/提案，而不是“已有行业标准”。[W3C Community Group](https://www.w3.org/groups/cg/ai-agent-memory-interop/) [SAIHM Datatracker record](https://datatracker.ietf.org/doc/draft-saihm-memory-protocol/)

MCP 是重要邻接层：它提供宿主、客户端和服务端的协作表面；Tasks 为长操作提供持久 `taskId`、轮询与重连。它不规定 Memory 的记录形状、provenance、更新、冲突或删除语义，因此“通过 MCP 接入”不能被读成“Memory 已可移植”。[MCP specification](https://modelcontextprotocol.io/specification/2025-06-18)

## 把集成放回 write → manage → read → act

**写入。** 集成方需要决定谁能创建记录，以及至少传递来源、主体、scope、时间和幂等标识。单纯的 `add(text)` 适合快速接入，却难以在导入时保住租户边界和原始证据。

**管理。** 真正难互通的是 update、supersede、删除、派生摘要、embedding 迁移和冲突。一个文件或 JSON 能被读入，不表示另一端知道其 predecessor、保留期限、派生依赖或删除请求应如何传播。MGP 的 Core、Lifecycle、Interop、ExternalService profiles 和同项目 compliance suite 是这类契约走向可执行化的例子；它们仍是 HKUDS/MGP 的项目协议，不是正式标准，也没有独立当前版本 conformance 证据。[MGP specification index](https://github.com/HKUDS/MGP/blob/54ce6c00e3d0aa731ecbe17e74407cbbb5a96f10/spec/README.md) [MGP compliance suite](https://github.com/HKUDS/MGP/blob/54ce6c00e3d0aa731ecbe17e74407cbbb5a96f10/docs/compliance-suite.md)

**读取。** 统一 search API 往往只对齐输入文本和返回片段，尚未对齐过滤、时间语义、冲突呈现、权限判定与“为什么此刻返回”。这也是为什么评测 harness 可降低接口摩擦，却不能保证语义相同。`OmniMemEval` 的 backend/plugin 归一化适合做实验连接，但本身不定义一套跨服务 Memory 标准。[OmniMemEval](https://github.com/MemTensor/OmniMemEval)

**行动。** 服务端返回的记忆不应携带跨宿主自动生效的工具授权。跨系统交换时，目标宿主仍需按自己的主体、权限和动作策略重新解释；否则一个“可移植记录”会意外变成“可移植能力”。

## 工程实例说明的不是同一件事

| 项目 / 工件 | 核心形状 | 其互操作价值 | 边界 |
|---|---|---|---|
| Open Memory Protocol v2.0 | draft、`.omp.zip`、备份/恢复/导入导出与治理范围 | 把归档和恢复作为协议对象 | Draft；没有被证明为正式或广泛采纳标准 |
| SMJAI Open Memory Protocol | REST、MCP adapter、CLI、浏览器扩展 | 展示服务与 host 接入形状 | 与同名 OMP 项目不是同一实体 |
| UMP v1.0 / Agent Memory Hall adapter | 严格记录 schema 与一个转换器 | 说明 record mapping 可实现 | 已检查适配器是 0.1-shaped，不符合 UMP 1.0 的完整 schema |
| Engramory | 规则文件、host adapters、单项目/单写者范围 | 人类可审计的本地工作纪律 | 明示实验性、无 store migration version，不是 wire 标准 |
| OCF | committed working context、schemas、fixtures | 表达当前生效状态及其治理线索 | 明示不是新 wire protocol，也不定义 memory units |
| eMEM | 签名、内容寻址事实及项目服务 | 完整性和可验证记录实验 | 项目资产和项目自营 responder 不是独立采用 |

名称也不能当身份。`UMP`、`AMP/RFC-AMP-001`、`Open Memory Protocol` 都存在不同团队的同名工件；互操作报告需要 owner、规范 URL 和固定版本，不能只写缩写。

## 采用与 conformance：目前证据到哪里为止

可以确认一些外部活动：Agent Memory Hall 有双向 UMP/AMH 转换器与测试，但检查显示它输出的形状更接近 UMP 0.1，而不是要求 `ump:"1.0"`、对象化 body/time 且禁止额外字段的 UMP 1.0；因此它是“有适配器的部分可移植性”，不是当前版本合规。Engramory 有一个外部 bootstrap 会 clone 并安装其规则，但未固定上游版本，也没有 conformance、CI 或生产部署报告。

相反，MGP、eMEM、OCF、glatinone AMP 等项目内的 schema、fixtures、SDK、CI 和 reference implementation 是可贵的可执行资产，却主要属于同一组织。它们提高了规范可测试性，不能替代两家独立实现对同一版本的互操作报告。包发布、star、registry listing、项目自营 endpoint 或 README 中的客户表述同样不能单独证明独立生产采用。

## 当前状态、近期变化与未解问题

当前主流集成方式仍是 host API、MCP 适配器、REST/SDK 与导入导出；这些降低连接成本，但大多只保证 API 层可达。近 12 个月的变化是项目规格从纯文档向 schemas、OpenAPI、fixtures 和 compliance suite 演进；近 90 天的弱信号是多个治理/可移植格式并存，反映需求明确但语义尚未收敛。

相对稳固的判断是：正式标准化早期、项目规格繁荣、独立 conformance 稀缺。未知的关键处包括跨后端删除与派生物撤销、时间/冲突语义、权限传递、加密与密钥边界、双向 round-trip 的字段损失，以及不同模型/embedding 版本下的语义迁移。要改变“尚未充分互通”的判断，需要公开的、版本固定的双组织实现、测试向量和字段/不变量损失报告，而不是更多名称相似的草案。

## 证据与阅读边界

- 标准形成状态：[W3C AI Agent Memory Interoperability CG](https://www.w3.org/groups/cg/ai-agent-memory-interop/)、[SAIHM individual Internet-Draft](https://datatracker.ietf.org/doc/draft-saihm-memory-protocol/)。
- 邻接 transport/lifecycle：[MCP specification](https://modelcontextprotocol.io/specification/2025-06-18)。
- 项目契约实例：[MGP](https://github.com/HKUDS/MGP)、[Engramory](https://github.com/tinqiao-oss/engramory)、[eMEM](https://github.com/evermind-ai/emem)、[OCF](https://github.com/aquifer-labs/ocf)。
- 归档/导入导出草案：[Open Memory Protocol](https://openmemoryprotocol.com/spec/)。

本文区分标准、草案、项目规格、适配器和采用证据；不把任一项目工件称为行业标准，也不提供集成选型建议。
