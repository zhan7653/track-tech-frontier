# Sibyl-Labs/Sibyl-Memory：固定提交工程深潜

**Cluster:** MM-C01  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | e2241dbcff6840674d616c3ab3c1389ddf0c2f2d |
| Created / pushed | 2026-05-20 / 2026-08-07 |
| Freshness bucket | newly-created-90d |
| Release | v0.1.0 / 2026-05-21T00:02:26Z |
| License | MIT |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 41 / 2 |
| Single snapshot stars / forks / open issues | 98 / 10 / 1 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

固定 SHA 显示这是五个 Python 包共享一个 schema family 的本地优先系统：client 负责每租户 SQLite 权威存储与 FTS5，MCP/Hermes/LangGraph/CLI 是接入与运维表面。此结论来自 manifest、代码和 tree；README 的排名与隐私声明仍按项目方自述处理。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| sibyl-memory-client | SQLite schema bootstrap、事务、迁移、FTS5 rebuild 与租户隔离 | `GR-S003-T` — fixed-SHA sibyl-memory-client/src/sibyl_memory_client/storage.py; blob c167f712c5425fa214395dcce7f0d69c6eba0391; sha256 90035f7200ff05fefdd6595b9f400b514ce4ed1d3dabbe72269413154840d406 |
| sibyl-memory-mcp | 把 remember/recall/search/list/forget/state/event 暴露成 MCP tools，并为读结果加不可信内容边界 | `GR-S003-T` — fixed-SHA sibyl-memory-mcp/src/sibyl_memory_mcp/server.py; blob 7260d79b9060cca5b2ab666a38609f34bf0b17f6; sha256 250c167e1fdf50982f28a7d1d375c0d8224da4d8821805d6f0b5a5e955a727a8 |
| Hermes/LangGraph/CLI adapters | 把相同 client/schema 接到 Hermes provider、LangGraph BaseStore 与账户/迁移 CLI | `GR-S003-R` — readmes/GRC003.md lines 31-55; sha256 1b0f219244b6dc4aaa27b9712c8c60a62c2d104622db24d5c3a46a1fd477e69d |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | memory_remember 接收 category/name/body 并做类型与边界校验 | MCP client → MemoryClient | `GR-S003-T` — server.py build_server/memory_remember |
| 2 | client 在租户范围事务中写入 base table | MemoryClient → SQLite base tables | `GR-S003-T` — storage.py Storage.transaction/schema |
| 3 | 触发器或迁移 rebuild 维护 FTS5 shadow | SQLite base tables → FTS5 indexes | `GR-S003-T` — storage.py _migrate_if_needed/_rebuild_fts_indexes |
| 4 | memory_search 跨 tier 检索、截断并为返回 body 加 untrusted fence | FTS5/client search → MCP result | `GR-S003-T` — server.py memory_search/_bound_hits/_fence |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| Python stdlib sqlite3 + SQLite JSON1/FTS5 | 本地权威存储、JSON 约束与词法检索；client manifest 运行时 dependencies=[] | `GR-S003-T` — client pyproject.toml blob a6586ea20d996be142d91fa7f82979a4acf4e20e; storage.py |
| mcp FastMCP | MCP transport/tool surface，只有 mcp 包需要 | `GR-S003-T` — server.py imports mcp.server.fastmcp |

**Integration constraints:**

- SQLite 必须支持 json_valid（代码错误信息指向 SQLite 3.38+）且启用 FTS5，否则 schema/search 无法工作。 (`GR-S003-T` — storage.py _ensure_schema/_rebuild_fts_indexes)
- 默认 DB 与凭据位于 ~/.sibyl-memory；这是单机文件边界，不提供跨主机协调或外部向量服务。 (`GR-S003-R` — readmes/GRC003.md lines 33-39,59-88)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=41、unique contributors=2、open issues single snapshot=1；release v0.1.0；CI/tests tree 存在。 (`GR-S003-O` — observations.jsonl/repositories.jsonl GRC003)
- open issues 仅单快照=1；PR latency 与 issue close-time 未测。 (`GR-S003-O` — observations.jsonl GRC003)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| FTS shadow 失配 | 迁移或崩溃留下形状正确但空的索引 | base rows 存在但搜索漏召回，需启动时 rebuild | GR-S003-T; inference=false |
| SQLite 写锁竞争 | 并发写超过 busy_timeout | 事务失败并向调用方传播 | GR-S003-T; inference=true |
| 存储内容提示注入 | 攻击性 memory body 被召回 | 若下游忽略 untrusted fence 仍可能影响 agent；代码只缓解不消除 | GR-S003-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** 服务/控制面是否把 durable records、mutation policy、retrieval 和 admin/observability 分开。

**首要失败风险：** tenant/ACL、迁移、删除、恢复与 centralized blast radius。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

未验证独立部署或第三方采用；README benchmark/排名与隐私陈述仅作项目方声明，stars 不参与质量判断。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 未运行仓库，真实吞吐/恢复正确性未知
- 独立生产 adoption 未验证

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 固定版本完成 CRUD→retrieve→supersede→delete→restore，并注入中断和跨 tenant 访问。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:07:57Z GitHub snapshot, Sibyl-Labs/Sibyl-Memory was created 2026-05-20, last pushed 2026-08-07, pinned at e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, had 98 cumulative stars, and had latest release v0.1.0 on 2026-05-21; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C003-1 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, the inspected engineering surface for Sibyl-Labs/Sibyl-Memory was setup=documented, CI=present, tests=present, license=MIT, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C003-2 -->

The repository's own GitHub metadata describes Sibyl-Labs/Sibyl-Memory as: “Durable, file-based long-term memory for AI agents. Five-package plugin family: SDK, CLI, MCP server, Hermes adapter, and a LangGraph BaseStore.…”
<!-- claim:GR-C003-3 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, fixed-source inspection of Sibyl-Labs/Sibyl-Memory supports this project-specific architecture reading: 固定 SHA 显示这是五个 Python 包共享一个 schema family 的本地优先系统：client 负责每租户 SQLite 权威存储与 FTS5，MCP/Hermes/LangGraph/CLI 是接入与运维表面。此结论来自 manifest、代码和 tree；README 的排名与隐私声明仍按项目方自述处理。 The repository was not executed in v09.
<!-- claim:PRJ-A001 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, Sibyl-Labs/Sibyl-Memory has these inspected dependencies or services: Python stdlib sqlite3 + SQLite JSON1/FTS5: 本地权威存储、JSON 约束与词法检索；client manifest 运行时 dependencies=[]; mcp FastMCP: MCP transport/tool surface，只有 mcp 包需要. Its recorded integration constraints are: SQLite 必须支持 json_valid（代码错误信息指向 SQLite 3.38+）且启用 FTS5，否则 schema/search 无法工作。; 默认 DB 与凭据位于 ~/.sibyl-memory；这是单机文件边界，不提供跨主机协调或外部向量服务。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I001 -->

At pinned commit e2241dbcff6840674d616c3ab3c1389ddf0c2f2d, the inspected repository tree for Sibyl-Labs/Sibyl-Memory exposed these architecture or integration locations: docs, sibyl-memory-cli, sibyl-memory-client, sibyl-memory-hermes, sibyl-memory-langgraph, sibyl-memory-mcp; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C001 -->

At the 2026-08-10T05:07:57Z GitHub/API snapshot for Sibyl-Labs/Sibyl-Memory, the inspected rolling-90d window contained 41 commits and 2 unique contributors, while open issues were 1; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M001 -->

<!-- synthesis:PRJ-S01 claims:GR-C003-1,GR-C003-2,GR-C003-3,PRJ-A001,PRJ-I001,PRJ-C001,PRJ-M001 clusters:MM-C01 -->

<!-- process:limitation -->
