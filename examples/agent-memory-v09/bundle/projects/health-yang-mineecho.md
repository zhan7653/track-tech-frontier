# Health-Yang/MineEcho：固定提交工程深潜

**Cluster:** MM-C08  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | bd04d2873700c9fb36b2b44641455567721a2a58 |
| Created / pushed | 2026-05-28 / 2026-06-05 |
| Freshness bucket | newly-created-90d |
| Release | none returned / — |
| License | NOASSERTION |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 28 / 2 |
| Single snapshot stars / forks / open issues | 245 / 27 / 0 |
| Engineering surface | moderate-surface (6/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

MineEcho 是本地 assistant 应用而非独立 memory library。BFF 同时维护 working memory、node:sqlite short-term interactions/preferences/tasks/summaries、file-based long-term profile，以及 L0-L3 memory tree；context-builder/semantic-recall 将近期 memory 与 knowledge-base 的 vector/BM25/graph/LightRAG 证据组合给 chat。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| BFF memory API/context builder | 提供 profile/short-term/task/skill/graph/project/learn/import/export routes并组装 prompt context | `GR-S056-T` — apps/bff/src/memory/README.md; blob 81eeedf4eb7682935967c081972ff19be8bd7924; sha256 1aec7537abd304c4cf2dc24ed8a394b5f08d5996ee4d1411a2cd5c01c06aa11c |
| ShortTermDb | node:sqlite 保存 interactions/preferences/tasks/daily summaries；不可用时退回 process-local Maps | `GR-S056-T` — apps/bff/src/memory/memory-db.ts; blob 9e80f8e9fc861a729dc62fb81cf763abb1463b91; sha256 27ad9341e88eb15e1e849134098fc5f773771e88ae6e5855d9e1afcc36195f97 |
| memory-tree/dream/storyline | 维护 L0-L3 content tree、summaries、embedding/semantic recall、dream schedule与 storyline | `GR-S056-T` — tree apps/bff/src/memory/{memory-tree/,memory-dream*,memory-storyline*,background-review.ts} |
| knowledge-base | raw/wiki/chunks、vector-store、graph-store、indexer与 LightRAG worker 提供四通道知识检索 | `GR-S056-R` — readmes/GRC056.md lines 79-97; tree apps/bff/src/knowledge-base |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | chat/task/meeting interaction 通过 BFF memory routes记录 | Console/OpenClaw gateway → working memory + ShortTermDb | `GR-S056-T` — memory README API endpoints; memory-db.ts addInteraction/addTask |
| 2 | SQLite 写 interactions/preferences/tasks/daily summaries并按 user/date索引 | BFF → short-term-memory.db | `GR-S056-T` — memory-db.ts initDb schema/indexes |
| 3 | dream/background review/summarizer 聚合短期内容到 long-term profile或 L0-L3 tree，embedding code维护本地向量 | short-term records → file memory/memory tree/vector state | `GR-S056-T` — tree memory-dream.ts, memory-tree/summarizer.ts, semantic-vector.ts |
| 4 | context builder融合近期、semantic、importance/recency与 knowledge channels并返回 evidence | memory tree + KB indexes → chat prompt | `GR-S056-R` — readmes/GRC056.md lines 79-97 |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| Express + zod + ws | BFF HTTP/websocket与输入 schema | `GR-S056-T` — apps/bff/package.json blob ddfa046238299f7f5f23a746faccce235f37f1b0; sha256 aa44b3b01f230cb83dfb0338e26170f55e7d03e075777c5e1be7b94d58cffec4 |
| node:sqlite + sqlite-vec | short-term relational store与可选本地 vector能力 | `GR-S056-T` — package.json dependencies; memory-db.ts dynamic import |
| provider APIs + LightRAG worker | embedding/LLM summary与 knowledge graph/vector processing，需本地配置 key | `GR-S056-R` — readmes/GRC056.md Quick Start/Memory and Knowledge |

**Integration constraints:**

- node:sqlite 不可用时 ShortTermDb 自动退回内存 Map；进程重启即丢 short-term state，集成方必须监控 fallback log。 (`GR-S056-T` — memory-db.ts lines 14-22,90-107,127-156)
- 仓库许可证是 PolyForm Noncommercial 1.0.0，商业使用需要另行书面许可；API 的 NOASSERTION 不能覆盖 README/LICENSE 明文。 (`GR-S056-R` — readmes/GRC056.md lines 360-362)
- 真实 provider keys 不随包提供，且 source startup 要同时安装 BFF/Console/vendored gateway dependencies。 (`GR-S056-R` — readmes/GRC056.md lines 157-217,294-296)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=28、unique contributors=2、open issues snapshot=0；无 release；CI/tests tree 存在。 (`GR-S056-O` — observations.jsonl/repositories.jsonl GRC056)
- open issues snapshot=0；PR latency、issue close-time、tracker 使用强度未知。 (`GR-S056-O` — observations.jsonl GRC056)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| ephemeral fallback data loss | node:sqlite import/open失败 | 短期 memory 转入内存 Map，重启丢失且多进程不共享 | GR-S056-T; inference=false |
| summary/tree compaction error | dream/summarizer模型遗漏或幻觉 | 高层 L1-L3 context 固化错误，后续召回反复放大 | GR-S056-T; inference=true |
| memory/KB index divergence | 文件、SQLite、tree vector、LightRAG多存储部分更新 | UI 可见内容与 chat evidence 不一致或漏召回 | GR-S056-R, GR-S056-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** profile/fact/preference 是否绑定 subject、consent、purpose、validity 和 source。

**首要失败风险：** 身份混淆、stale preference、越权推断和不可删除画像。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

定位为完整个人 assistant；未验证第三方生产采用、规模或 long-running durability。安装包/截图与 token-saving描述均为项目方材料。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- SQLite fallback发生率未知
- 独立 adoption 未验证
- 无 release migration contract

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 多用户/多 persona/撤回场景验证 scope、更新、解释、删除与 downstream action。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:17:28Z GitHub snapshot, Health-Yang/MineEcho was created 2026-05-28, last pushed 2026-06-05, pinned at bd04d2873700c9fb36b2b44641455567721a2a58, had 245 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C056-1 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, the inspected engineering surface for Health-Yang/MineEcho was setup=documented, CI=present, tests=present, license=NOASSERTION, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C056-2 -->

The repository's own GitHub metadata describes Health-Yang/MineEcho as: “Local-first Memory OS for personal AI assistants with L0-L3 memory, Wiki++ knowledge, skill routing, and TokenLess context compression.”
<!-- claim:GR-C056-3 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, fixed-source inspection of Health-Yang/MineEcho supports this project-specific architecture reading: MineEcho 是本地 assistant 应用而非独立 memory library。BFF 同时维护 working memory、node:sqlite short-term interactions/preferences/tasks/summaries、file-based long-term profile，以及 L0-L3 memory tree；context-builder/semantic-recall 将近期 memory 与 knowledge-base 的 vector/BM25/graph/LightRAG 证据组合给 chat。 The repository was not executed in v09.
<!-- claim:PRJ-A008 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, Health-Yang/MineEcho has these inspected dependencies or services: Express + zod + ws: BFF HTTP/websocket与输入 schema; node:sqlite + sqlite-vec: short-term relational store与可选本地 vector能力; provider APIs + LightRAG worker: embedding/LLM summary与 knowledge graph/vector processing，需本地配置 key. Its recorded integration constraints are: node:sqlite 不可用时 ShortTermDb 自动退回内存 Map；进程重启即丢 short-term state，集成方必须监控 fallback log。; 仓库许可证是 PolyForm Noncommercial 1.0.0，商业使用需要另行书面许可；API 的 NOASSERTION 不能覆盖 README/LICENSE 明文。; 真实 provider keys 不随包提供，且 source startup 要同时安装 BFF/Console/vendored gateway dependencies。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I008 -->

At pinned commit bd04d2873700c9fb36b2b44641455567721a2a58, the inspected repository tree for Health-Yang/MineEcho exposed these architecture or integration locations: apps, docs, marketing, scripts, vendor; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C008 -->

At the 2026-08-10T05:17:28Z GitHub/API snapshot for Health-Yang/MineEcho, the inspected rolling-90d window contained 28 commits and 2 unique contributors, while open issues were 0; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M008 -->

<!-- synthesis:PRJ-S08 claims:GR-C056-1,GR-C056-2,GR-C056-3,PRJ-A008,PRJ-I008,PRJ-C008,PRJ-M008 clusters:MM-C08 -->

<!-- process:limitation -->
