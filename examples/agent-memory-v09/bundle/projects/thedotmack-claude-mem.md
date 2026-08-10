# thedotmack/claude-mem：固定提交工程深潜

**Cluster:** MM-C07  
**Selection:** keep-deep — Frontier-window creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 4702c337d85aa12e8ab7f845264a78885676261f |
| Created / pushed | 2025-08-31 / 2026-08-10 |
| Freshness bucket | newly-created-12m |
| Release | v13.14.0 / 2026-08-08T02:21:38Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 484 / 36 |
| Single snapshot stars / forks / open issues | 90236 / 7857 / 389 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

这是 lifecycle-hook 驱动的 coding-session memory：Claude Code/OpenCode hooks 把 prompt、tool use 与 session end 发给每用户 Bun worker；worker 用 SQLite 保存 sessions/observations/summaries/pending queue，用 ChromaDB 保存 observation vectors；MCP 提供 search→timeline/get_observations 的渐进披露读取。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| Hook/CLI layer | 处理 SessionStart、UserPromptSubmit、PostToolUse、Stop、SessionEnd并调用 worker HTTP | `GR-S020-T` — docs/architecture-overview.md; blob 4ddbc058afdbe87fcb8a2e0695012254277c7a98; sha256 381596e7b7b48a7327a3dedb1ee1b567997c1894e02e1eff68c64315cb766cea |
| Worker daemon | SessionManager/SDKAgent/PendingMessageStore/SearchManager/ChromaSync与 SSE/UI orchestration | `GR-S020-T` — docs/architecture-overview.md system layers; tree src/services/worker |
| SQLite SessionStore | 持久 sessions、observations、summaries、prompts、pending messages 与 feedback | `GR-S020-T` — docs/architecture-overview.md Storage tables |
| ChromaDB + MCP search | 同步 observation embeddings并提供 hybrid semantic/FTS、timeline与渐进披露结果 | `GR-S020-T` — src/services/worker/SearchManager.ts; blob 98b194052009900c01a0ce63f442a355bd8feae8; sha256 f85c292b400bb864ec6c07a65a523985333368a8a3f98416e69b068bb28dac26 |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | UserPromptSubmit 初始化 session并请求 semantic context | host hook → worker /api/sessions/init + /api/context/semantic | `GR-S020-T` — architecture Data Flow |
| 2 | PostToolUse 将 tool observation 入 pending queue并交 SDKAgent | hook event → PendingMessageStore/SDKAgent | `GR-S020-T` — architecture lines 47-59 |
| 3 | 有效生成结果写 observations/session summary，content_hash 去重 | SDKAgent response → SQLite | `GR-S020-T` — architecture Pending Queue/Deduplication/Storage |
| 4 | ChromaSync 写 embeddings；MCP search融合 Chroma/SQLite并按 ID展开 timeline/observations | SQLite observations + Chroma → future session context | `GR-S020-T` — SearchManager.ts searchObservations/getTimeline/getRecentContext |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| Node >=20.12 + Bun >=1 | installer/CLI/worker runtime | `GR-S020-T` — package.json blob d85ccfd3281ad7ee1cc0b74def6a01e4c00a0489; sha256 e514ed97c3f8728b39f8bb9d13bc56d107376e7ec22215cbc001d9b38fb42920 |
| SQLite 3 | 结构化权威 session/observation store | `GR-S020-R` — readmes/GRC020.md system requirements/how it works |
| uv + ChromaDB/chroma-mcp | Python vector search process与 semantic index | `GR-S020-T` — architecture Storage/Process; README requirements |

**Integration constraints:**

- npm global install 仅装 SDK，不注册 hooks/worker；必须用 npx installer 或 host plugin install。 (`GR-S020-R` — readmes/GRC020.md lines 131-161)
- contentSessionId 与 memorySessionId 语义不同；转换错误会破坏 FK/session continuity。 (`GR-S020-T` — architecture Two Types of Session ID)
- hooks 故意 fail-open，worker 不可用不会阻塞 host，这意味着可用性优先于 capture completeness。 (`GR-S020-T` — architecture Graceful Degradation)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=484、unique contributors=36、open issues snapshot=389；release v13.14.0；CI/tests 存在。 (`GR-S020-O` — observations.jsonl/repositories.jsonl GRC020)
- open issues snapshot=389；PR latency、issue close-time、installer/platform defect proportion 未测。 (`GR-S020-O` — observations.jsonl GRC020)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| worker fail-open | worker未启动、端口冲突或 HTTP timeout | host session继续但当前事件/recall缺失 | GR-S020-T; inference=false |
| pending parser rejection | SDKAgent 输出不可解析 | queue 保留、iterator继续；积压会延迟或阻塞 observation materialization | GR-S020-T; inference=false |
| SQLite/Chroma divergence | SQLite commit 后 ChromaSync/MCP process失败 | keyword data存在但 semantic index stale或缺项 | GR-S020-T; inference=true |
| session ID mismatch | content/memory ID映射错误或 worker restart | FK关联失败、summary/observation落到错误 session | GR-S020-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** working context 与 durable memory 的切分、压缩损失和可逆取回是否显式。

**首要失败风险：** token 节省掩盖证据丢失、工具输出截断和 context contamination。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

README 有 host/plugin 安装入口，但本次未验证独立组织采用或生产 SLO；版本/下载/star不作质量或增长结论。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- worker/Chroma recovery SLO 未测
- 独立 adoption 未验证
- 未运行跨平台 install

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. matched task 下测 raw/compressed/retrieved context 的答案、证据、动作、token 与 latency。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:14:45Z GitHub snapshot, thedotmack/claude-mem was created 2025-08-31, last pushed 2026-08-10, pinned at 4702c337d85aa12e8ab7f845264a78885676261f, had 90236 cumulative stars, and had latest release v13.14.0 on 2026-08-08; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C020-1 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, the inspected engineering surface for thedotmack/claude-mem was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C020-2 -->

The repository's own GitHub metadata describes thedotmack/claude-mem as: “Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and…”
<!-- claim:GR-C020-3 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, fixed-source inspection of thedotmack/claude-mem supports this project-specific architecture reading: 这是 lifecycle-hook 驱动的 coding-session memory：Claude Code/OpenCode hooks 把 prompt、tool use 与 session end 发给每用户 Bun worker；worker 用 SQLite 保存 sessions/observations/summaries/pending queue，用 ChromaDB 保存 observation vectors；MCP 提供 search→timeline/get_observations 的渐进披露读取。 The repository was not executed in v09.
<!-- claim:PRJ-A007 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, thedotmack/claude-mem has these inspected dependencies or services: Node >=20.12 + Bun >=1: installer/CLI/worker runtime; SQLite 3: 结构化权威 session/observation store; uv + ChromaDB/chroma-mcp: Python vector search process与 semantic index. Its recorded integration constraints are: npm global install 仅装 SDK，不注册 hooks/worker；必须用 npx installer 或 host plugin install。; contentSessionId 与 memorySessionId 语义不同；转换错误会破坏 FK/session continuity。; hooks 故意 fail-open，worker 不可用不会阻塞 host，这意味着可用性优先于 capture completeness。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I007 -->

At pinned commit 4702c337d85aa12e8ab7f845264a78885676261f, the inspected repository tree for thedotmack/claude-mem exposed these architecture or integration locations: cursor-hooks, docker, docs, fixtures, install, openclaw, plans, plugin, ragtime, scripts, src, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C007 -->

At the 2026-08-10T05:14:45Z GitHub/API snapshot for thedotmack/claude-mem, the inspected rolling-90d window contained 484 commits and 36 unique contributors, while open issues were 389; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M007 -->

<!-- synthesis:PRJ-S07 claims:GR-C020-1,GR-C020-2,GR-C020-3,PRJ-A007,PRJ-I007,PRJ-C007,PRJ-M007 clusters:MM-C07 -->

<!-- process:limitation -->
