# SMJAI/open-memory-protocol：固定提交工程深潜

**Cluster:** MM-C11  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 2f91247accde20feab9718790aa8a06c077e32bd |
| Created / pushed | 2026-06-29 / 2026-07-02 |
| Freshness bucket | newly-created-90d |
| Release | none returned / — |
| License | NOASSERTION |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 31 / 1 |
| Single snapshot stars / forks / open issues | 73 / 2 / 1 |
| Engineering surface | moderate-surface (5/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

该仓同时定义 vendor-neutral memory JSON schema、reference Express server 与 browser/Claude-MCP/CLI adapters。Reference server 用 node:sqlite保存 conversations与memory rows，FTS5 triggers同步 content/tags；embedding字段可被schema/storage保存，但固定 SHA 的 search实现只做quoted-term FTS，不构成semantic vector engine。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| OMP v1 schema | 约束 id/content/type/source/tags/namespace/time/optional embedding/metadata 的交换对象 | `GR-S030-T` — spec/v1/memory.schema.json; blob c33cb75ad18568bdc6c3a8e4eb6fbf505981754a; sha256 cc42a70a2be474ba7d554ae1c0cf827a0b57de795db88e4a470f670e8b167acb |
| Express reference routes | 提供 memories、conversations、extract、compress、handoff HTTP endpoints | `GR-S030-T` — tree packages/server/src/routes/{memories,conversations,extract,compress,handoff}.ts |
| SQLiteStorage | 建表、FTS triggers、CRUD/list/search/export/import与conversation persistence | `GR-S030-T` — packages/server/src/storage/sqlite.ts; blob 238c6140464a699e88c5430ca78708ab0d9763c8; sha256 abcac58acd0f1f8fc31bc036fd6b4eb1dbf674c5d2c97c1c4e10e596a44df5ba |
| tool adapters | browser extension、Claude MCP与CLI把各宿主数据映射到同一server/schema | `GR-S030-T` — tree adapters/{browser-extension,claude-mcp,cli} |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | adapter或HTTP caller提交符合memory schema的content/type/source/namespace | host adapter → Express route | `GR-S030-T` — spec schema + routes/memories.ts tree |
| 2 | route用类型/schema逻辑构造ID和timestamps并调用SQLiteStorage.create | Express → SQLiteStorage | `GR-S030-T` — sqlite.ts create |
| 3 | insert写memories，FTS5 trigger索引content/tags；embedding作为JSON字段持久化 | SQLiteStorage → memories + memories_fts | `GR-S030-T` — sqlite.ts migrate/create |
| 4 | search把query tokens转成quoted OR FTS expression，按type/namespace过滤并join返回memory objects | memories_fts → HTTP/MCP result | `GR-S030-T` — sqlite.ts search lines 198-219 |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| Node >=22.5 node:sqlite | reference server runtime与内置SQLite | `GR-S030-T` — packages/server/package.json blob b02635df8599321a95973280f616fef6cf451575; sha256 f50a302f11774d3b45ae8146c036872ce3fa716be3048cfbbb168a3d6e27a991 |
| Express 4.18 + Zod 3.22 | HTTP server与runtime input validation | `GR-S030-T` — packages/server/package.json dependencies |
| SQLite FTS5 | reference implementation唯一实际检索索引 | `GR-S030-T` — sqlite.ts migrate/search |

**Integration constraints:**

- 协议对象允许embedding，但reference search不读取它；需要semantic search的实现者必须另加vector index并定义一致性。 (`GR-S030-T` — memory.schema.json embedding + sqlite.ts search)
- canonical schema content上限10000、tags格式/数量、id pattern与additionalProperties=false会拒绝不兼容host payload。 (`GR-S030-T` — spec/v1/memory.schema.json)
- SQLiteStorage接口未展示组织级tenant enforcement；source.user_id与namespace是数据字段，不能自动当安全边界。 (`GR-S030-T` — sqlite.ts list/search filters)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=31、unique contributors=1、open issues snapshot=1；无release；CI/tests 存在。 (`GR-S030-O` — observations.jsonl/repositories.jsonl GRC030)
- open issues snapshot=1；PR latency、issue close-time、外部implementer compatibility未测。 (`GR-S030-O` — observations.jsonl GRC030)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| semantic expectation mismatch | caller写embedding并以为server会vector search | 实际仅FTS OR，语义同义召回缺失 | GR-S030-T; inference=false |
| tenant boundary误用 | 把user_id/namespace字段当授权而未加auth/row-level enforcement | 多租户部署可能跨用户list/search | GR-S030-T; inference=true |
| expiration不自动生效 | 写入expires_at但search/list路径未过滤或后台清理未配置 | 过期memory仍可能被返回 | GR-S030-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** shared/private branch、owner、merge、revoke 和 portable schema 是否明确。

**首要失败风险：** 跨 agent/tenant 泄漏、冲突静默覆盖、污染传播和 round-trip 语义丢失。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

这是协议草案+reference server，不应把其schema覆盖面当生态共识或实现成熟度；未验证第三方独立implementations/adoption。package声明Apache-2.0，但API license detection为NOASSERTION，需以仓库LICENSE复核。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 独立 protocol implementations/adoption 未验证
- auth/deployment hardening未全面审计
- expiration cleanup未知

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 两实现 export/import/sync/merge/revoke，加入离线分叉、恶意共享 skill 与动态权限。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:13:10Z GitHub snapshot, SMJAI/open-memory-protocol was created 2026-06-29, last pushed 2026-07-02, pinned at 2f91247accde20feab9718790aa8a06c077e32bd, had 73 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C030-1 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, the inspected engineering surface for SMJAI/open-memory-protocol was setup=documented, CI=present, tests=present, license=NOASSERTION, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C030-2 -->

The repository's own GitHub metadata describes SMJAI/open-memory-protocol as: “An open standard for portable, interoperable AI memory across tools, sessions, and devices.”
<!-- claim:GR-C030-3 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, fixed-source inspection of SMJAI/open-memory-protocol supports this project-specific architecture reading: 该仓同时定义 vendor-neutral memory JSON schema、reference Express server 与 browser/Claude-MCP/CLI adapters。Reference server 用 node:sqlite保存 conversations与memory rows，FTS5 triggers同步 content/tags；embedding字段可被schema/storage保存，但固定 SHA 的 search实现只做quoted-term FTS，不构成semantic vector engine。 The repository was not executed in v09.
<!-- claim:PRJ-A011 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, SMJAI/open-memory-protocol has these inspected dependencies or services: Node >=22.5 node:sqlite: reference server runtime与内置SQLite; Express 4.18 + Zod 3.22: HTTP server与runtime input validation; SQLite FTS5: reference implementation唯一实际检索索引. Its recorded integration constraints are: 协议对象允许embedding，但reference search不读取它；需要semantic search的实现者必须另加vector index并定义一致性。; canonical schema content上限10000、tags格式/数量、id pattern与additionalProperties=false会拒绝不兼容host payload。; SQLiteStorage接口未展示组织级tenant enforcement；source.user_id与namespace是数据字段，不能自动当安全边界。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I011 -->

At pinned commit 2f91247accde20feab9718790aa8a06c077e32bd, the inspected repository tree for SMJAI/open-memory-protocol exposed these architecture or integration locations: adapters, packages, spec; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C011 -->

At the 2026-08-10T05:13:10Z GitHub/API snapshot for SMJAI/open-memory-protocol, the inspected rolling-90d window contained 31 commits and 1 unique contributors, while open issues were 1; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M011 -->

<!-- synthesis:PRJ-S11 claims:GR-C030-1,GR-C030-2,GR-C030-3,PRJ-A011,PRJ-I011,PRJ-C011,PRJ-M011 clusters:MM-C11 -->

<!-- process:limitation -->
