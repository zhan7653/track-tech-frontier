# Coding-Dev-Tools/engraphis：固定提交工程深潜

**Cluster:** MM-C09  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 128fe0515b842923df871a777eaacc3327f40513 |
| Created / pushed | 2026-06-30 / 2026-08-10 |
| Freshness bucket | newly-created-90d |
| Release | v1.5 / 2026-08-06T00:11:49Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 348 / 4 |
| Single snapshot stars / forks / open issues | 153 / 30 / 0 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

Engraphis 以 MemoryService 统一 CLI/MCP/REST/dashboard ingress，MemoryEngine 组合 Store、embedder、vector index、reranker、conflict/retention/graph policies。一个 SQLite 文件保存 memories、FTS、bi-temporal history、layered graph/code links与 hashed receipts；vector backend 默认为 NumPy exact scan，可选 sqlite-vec，query 再做 lexical/vector/graph/code fusion与 hard-budget context packing。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| MemoryService surfaces | 让 Smart/Classic MCP、REST、dashboard、CLI 共用一套 scope/write/recall semantics | `GR-S026-T` — docs/ARCHITECTURE_V3.md; blob 912f84f44a941f1da881b0e68a5a0f83b0dcf0d4; sha256 2bbd16242ea7788bee6e8e984c5a3178707047f7fb96ebc966a61e3dd21d85f9 |
| MemoryEngine | 编排 remember、conflict、evolution、retention、recall、context pack与 privacy/audit | `GR-S026-T` — engraphis/core/engine.py; blob 5523472119643aa6d4b01e4729149e4badd212c8; sha256 b4403588995cf514e3c60b9f502bb7a1d66d60e9d7d2036dec904cea9c2a9b0a |
| SQLite store + vector backends | 持久 records/FTS/graph/history，NumPy或sqlite-vec维护 embedding index | `GR-S026-T` — tree engraphis/core/store.py, backends/{vector_numpy,vector_sqlitevec,encrypted_db}.py |
| layered/code graph + receipts | temporal/entity/causal/semantic overlays、incremental code AST/regex index与 content-free receipt chain | `GR-S026-T` — docs/ARCHITECTURE_V3.md lines 21-60 |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | remember/import 经 Service 校验 scope、secret、provenance并产生 record | MCP/REST/CLI/resource adapter → MemoryEngine | `GR-S026-T` — engine.py facade and ARCHITECTURE service contract |
| 2 | Engine 做 embedding、dedup/conflict/evolution并写 SQLite memory/history/FTS/graph/receipt | MemoryEngine → single SQLite store | `GR-S026-T` — engine.py remember path; architecture one database |
| 3 | vector backend upsert embedding；code index以content hash增量更新 symbols/code_edges | stored records/files → NumPy/sqlite-vec + code graph | `GR-S026-T` — architecture incremental indexing/vector compatibility |
| 4 | recall融合 lexical/vector/graph/code、rerank并打包到 hard token budget | indexes → prompt-ready context/evidence | `GR-S026-R` — readmes/GRC026.md What Engraphis gives an agent/Quickstart library |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| numpy >=1.24 | 唯一 core dependency；默认 exact vector scan/offline engine | `GR-S026-T` — pyproject.toml blob 053924ec3be4ce04a131da02b597c967e42ac18b; sha256 012143b941a57bcd37ef95430d50324eb5ea24489d473dc2405d1a44bb146d89 |
| FastAPI/Uvicorn/SentenceTransformers/MCP optional extras | server、real embeddings与 agent transport | `GR-S026-T` — pyproject.toml server/mcp extras |
| sqlite-vec/tree-sitter/psycopg/SQLCipher optional extras | native exact KNN、code graph、Postgres introspection、at-rest encryption | `GR-S026-T` — pyproject.toml vector/code/postgres/encryption extras |

**Integration constraints:**

- persistent vector space 需要可验证且稳定的 embedding fingerprint；身份不明或变化时 vector recall fail-closed直到 rebuild。 (`GR-S026-R` — readmes/GRC026.md vector identity/recovery sections)
- sqlite-vec 与 SQLCipher native SQLite libraries 不能同进程安全组合；auto回退NumPy，显式 sqlite-vec 请求会报错。 (`GR-S026-T` — docs/ARCHITECTURE_V3.md lines 78-92)
- open repo不含 hosted team identity/automation等服务实现，不能从本地代码推断 hosted feature。 (`GR-S026-R` — readmes/GRC026.md open-core boundary)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=348、unique contributors=4、open issues snapshot=0；latest observed release v1.5；CI/tests 存在。 (`GR-S026-O` — observations.jsonl/repositories.jsonl GRC026)
- open issues snapshot=0；PR latency、issue close-time、main-to-release lag未测。 (`GR-S026-O` — observations.jsonl GRC026)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| embedding fingerprint mismatch | 模型/revision改变或远端模型身份不可固定 | persistent vector recall被禁用，直到全量一致 rebuild | GR-S026-R, GR-S026-T; inference=false |
| native backend conflict | sqlite-vec 与 SQLCipher同进程加载 | auto退回NumPy或显式配置启动失败，性能/加密取舍变化 | GR-S026-T; inference=false |
| scope/review gate zero result | records未获prompt eligibility或调用错 workspace/repo/session | 数据存在但召回为空，需要 review/approval而非索引修复 | GR-S026-R; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** 代码结构、项目判断、会话观察与反馈策略是否分别绑定 repo/branch/worktree/commit。

**首要失败风险：** index drift、错误 decision 复用、secret capture、multi-worktree 冲突和 stale action。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

README含 hosted/open-core边界和自测数据，但本次未验证第三方生产 adoption或性能；open repo只支持对本地 engine/MCP/dashboard的判断。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 独立 adoption 未验证
- 未运行 migration/vector backend matrix
- hosted实现不在仓库

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 同 harness 做 index/log/context on-off，跨 commit/branch 重放，注入 secret、failed fix 和 concurrent worktree。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:13:25Z GitHub snapshot, Coding-Dev-Tools/engraphis was created 2026-06-30, last pushed 2026-08-10, pinned at 128fe0515b842923df871a777eaacc3327f40513, had 153 cumulative stars, and had latest release v1.5 on 2026-08-06; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C026-1 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, the inspected engineering surface for Coding-Dev-Tools/engraphis was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C026-2 -->

The repository's own GitHub metadata describes Coding-Dev-Tools/engraphis as: “Local-first, inspectable memory for coding agents: durable context across sessions and repositories, code-aware recall, bi-temporal history, MCP, and a self-hosted…”
<!-- claim:GR-C026-3 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, fixed-source inspection of Coding-Dev-Tools/engraphis supports this project-specific architecture reading: Engraphis 以 MemoryService 统一 CLI/MCP/REST/dashboard ingress，MemoryEngine 组合 Store、embedder、vector index、reranker、conflict/retention/graph policies。一个 SQLite 文件保存 memories、FTS、bi-temporal history、layered graph/code links与 hashed receipts；vector backend 默认为 NumPy exact scan，可选 sqlite-vec，query 再做 lexical/vector/graph/code fusion与 hard-budget context packing。 The repository was not executed in v09.
<!-- claim:PRJ-A009 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, Coding-Dev-Tools/engraphis has these inspected dependencies or services: numpy >=1.24: 唯一 core dependency；默认 exact vector scan/offline engine; FastAPI/Uvicorn/SentenceTransformers/MCP optional extras: server、real embeddings与 agent transport; sqlite-vec/tree-sitter/psycopg/SQLCipher optional extras: native exact KNN、code graph、Postgres introspection、at-rest encryption. Its recorded integration constraints are: persistent vector space 需要可验证且稳定的 embedding fingerprint；身份不明或变化时 vector recall fail-closed直到 rebuild。; sqlite-vec 与 SQLCipher native SQLite libraries 不能同进程安全组合；auto回退NumPy，显式 sqlite-vec 请求会报错。; open repo不含 hosted team identity/automation等服务实现，不能从本地代码推断 hosted feature。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I009 -->

At pinned commit 128fe0515b842923df871a777eaacc3327f40513, the inspected repository tree for Coding-Dev-Tools/engraphis exposed these architecture or integration locations: demo, deploy, docs, engraphis, eval, integrations, scripts, skills, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C009 -->

At the 2026-08-10T05:13:25Z GitHub/API snapshot for Coding-Dev-Tools/engraphis, the inspected rolling-90d window contained 348 commits and 4 unique contributors, while open issues were 0; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M009 -->

<!-- synthesis:PRJ-S09 claims:GR-C026-1,GR-C026-2,GR-C026-3,PRJ-A009,PRJ-I009,PRJ-C009,PRJ-M009 clusters:MM-C09 -->

<!-- process:limitation -->
