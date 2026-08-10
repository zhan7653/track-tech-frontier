# EverMind-AI/Raven：固定提交工程深潜

**Cluster:** MM-C05  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 14b7419245b816782b0435385d238f9f18ac090f |
| Created / pushed | 2026-05-21 / 2026-08-10 |
| Freshness bucket | newly-created-90d |
| Release | v0.1.10 / 2026-07-31T17:48:25Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 149 / 20 |
| Single snapshot stars / forks / open issues | 3532 / 59 / 70 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

Raven 是完整 terminal agent harness；memory 由 host 侧 MemoryBackend Protocol 与 manifest-only plugin discovery 解耦，context_engine 在 turn 前组装 recalled memory，AgentLoop 在 turn 后 store/feedback。固定 SHA 将 EverOS 作为 bundled adapter，但重逻辑仍在 exact-pinned everos 包，另有 skill-forge 把 memory hits 与 skill sources 汇合。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| MemoryBackend protocol + plugin discovery | 定义 recall/store/feedback/start/stop、user/agent 双轨身份，并只在被选中时 import backend factory | `GR-S059-T` — raven/memory_engine/backend.py; blob 622781e33c10ba6299e38a9ed13fad8442869c0c; sha256 88d553980dd8117e712df56e13d9445832c07942001618ff82afb5a02665b6da |
| EverOS bundled plugin | 把 Raven contract 适配到 everos embedded/http search/memorize 与 multimodal extraction | `GR-S059-T` — docs/memory-plugin-architecture.md; blob 2deb85473c6885943b57d426e15ff485a0c1eb14; sha256 5b276d83af84259d71c8c5ec68b9cace53fbb442fb49458275c5146d542a41e2 |
| context_engine + AgentLoop | 按预算渲染 memory segment、在每 turn 调用 recall，并在完成后 store session slice/feedback | `GR-S059-T` — tree paths raven/context_engine/segments/memory.py, raven/agent/, backend.py lifecycle comments |
| skill_forge | 将 memory/backend、本地/Hub skill candidates 统一为 ScoredSkill 并做 cross-source fusion/gating | `GR-S059-T` — tree paths raven/memory_engine/skill_forge/{router,fusion,gate,everos_source}.py |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | 配置选择 memory.backend 并由 plugin factory start backend | Raven config/plugin manifests → MemoryBackend instance | `GR-S059-T` — docs/memory-plugin-architecture.md sections 2-7 |
| 2 | AgentLoop 分 user/agent track 调 recall，传 query/user_id/agent_id/top_k | current turn → selected backend | `GR-S059-T` — backend.py MemoryBackend.recall contract |
| 3 | context_engine 对 hits 组装、裁剪后注入 prompt/skill routing | Memory hits → agent context | `GR-S059-T` — tree context_engine/segments/memory.py and skill_forge |
| 4 | turn 完成后 backend.store 保存 session messages，feedback 处理信号 | AgentLoop session slice → EverOS or third-party store | `GR-S059-T` — backend.py store/feedback contract |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| everos[multimodal]==1.2.1 | bundled backend 的实际 extraction/search/persistence substrate，精确 pin 因 adapter 使用 internal APIs | `GR-S059-T` — pyproject.toml blob c73b4803f1291e8643a5d0dfe33c42bd0fceb8c5; sha256 a4155458efa204ca35333ea1a0417510f15d1125739a1af2d34139d452b763ad |
| litellm + httpx + pydantic | LLM/provider调用、HTTP backend 与配置/schema | `GR-S059-T` — pyproject.toml dependencies |
| mcp + channel extras | tool/server interface 与 Telegram/Slack/Discord/Matrix 等 gateway integrations | `GR-S059-T` — pyproject.toml dependencies/optional-dependencies |

**Integration constraints:**

- EverOS adapter 直接依赖 everos internal APIs，文档要求升级时重新核对并可能重建 ~/.everos/.index；不能把版本 range 随意放宽。 (`GR-S059-T` — docs/memory-plugin-architecture.md lines 298-339,379-382)
- memory.userId 与 memory.agentId 是唯一身份源；recall/store identity 不一致会让已写 memory 无法召回。 (`GR-S059-T` — docs/memory-plugin-architecture.md lines 64-73; backend.py contract)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=149、unique contributors=20、open issues snapshot=70；release v0.1.10；CI/tests 存在。 (`GR-S059-O` — observations.jsonl/repositories.jsonl GRC059)
- open issues snapshot=70；PR latency、issue close-time、按子系统缺陷分布未测。 (`GR-S059-O` — observations.jsonl GRC059)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| backend factory fallback | plugin factory/import/dependency 初始化失败 | 文档称 host fallback 为 no backend，agent 可运行但持久 memory 缺失 | GR-S059-T; inference=false |
| EverOS internal API drift | everos 版本或 ~/.everos index schema 改变 | adapter import/search/memorize 失败或需要 index rebuild/migration | GR-S059-T; inference=false |
| identity track mismatch | store 与 recall 的 user_id/agent_id 路由不一致 | 数据存在但目标 track 检索不到，或跨 track 暴露 | GR-S059-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** admit、consolidate、supersede、forget、purge、rollback 是否是可回放操作。

**首要失败风险：** 压缩丢证、删除不完全、learned controller 漂移和 mutation 冲突。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

仓库是 agent harness 而非可独立替换的单一 memory engine；本次未验证 Raven/EverOS 的独立生产 adoption。README ecosystem 与测试数字均视为项目方陈述。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 第三方 memory plugins 的兼容矩阵未知
- 独立 adoption 未验证
- 未运行 EverOS migration/e2e

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 重放 add/update/conflict/delete/recover 序列，逐层检查 raw、summary、embedding、edge、cache、backup。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:17:49Z GitHub snapshot, EverMind-AI/Raven was created 2026-05-21, last pushed 2026-08-10, pinned at 14b7419245b816782b0435385d238f9f18ac090f, had 3532 cumulative stars, and had latest release v0.1.10 on 2026-07-31; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C059-1 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, the inspected engineering surface for EverMind-AI/Raven was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C059-2 -->

The repository's own GitHub metadata describes EverMind-AI/Raven as: “The memory-first, self-improving agent harness built on EverOS, with MiroThinker-powered deep research and reasoning.”
<!-- claim:GR-C059-3 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, fixed-source inspection of EverMind-AI/Raven supports this project-specific architecture reading: Raven 是完整 terminal agent harness；memory 由 host 侧 MemoryBackend Protocol 与 manifest-only plugin discovery 解耦，context_engine 在 turn 前组装 recalled memory，AgentLoop 在 turn 后 store/feedback。固定 SHA 将 EverOS 作为 bundled adapter，但重逻辑仍在 exact-pinned everos 包，另有 skill-forge 把 memory hits 与 skill sources 汇合。 The repository was not executed in v09.
<!-- claim:PRJ-A005 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, EverMind-AI/Raven has these inspected dependencies or services: everos[multimodal]==1.2.1: bundled backend 的实际 extraction/search/persistence substrate，精确 pin 因 adapter 使用 internal APIs; litellm + httpx + pydantic: LLM/provider调用、HTTP backend 与配置/schema; mcp + channel extras: tool/server interface 与 Telegram/Slack/Discord/Matrix 等 gateway integrations. Its recorded integration constraints are: EverOS adapter 直接依赖 everos internal APIs，文档要求升级时重新核对并可能重建 ~/.everos/.index；不能把版本 range 随意放宽。; memory.userId 与 memory.agentId 是唯一身份源；recall/store identity 不一致会让已写 memory 无法召回。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I005 -->

At pinned commit 14b7419245b816782b0435385d238f9f18ac090f, the inspected repository tree for EverMind-AI/Raven exposed these architecture or integration locations: LICENSES, benchmarks, bridge, demos, docs, raven, scripts, tests, ui-tui; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C005 -->

At the 2026-08-10T05:17:49Z GitHub/API snapshot for EverMind-AI/Raven, the inspected rolling-90d window contained 149 commits and 20 unique contributors, while open issues were 70; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M005 -->

<!-- synthesis:PRJ-S05 claims:GR-C059-1,GR-C059-2,GR-C059-3,PRJ-A005,PRJ-I005,PRJ-C005,PRJ-M005 clusters:MM-C05 -->

<!-- process:limitation -->
