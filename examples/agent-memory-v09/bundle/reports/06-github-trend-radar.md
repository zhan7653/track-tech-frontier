# Agent Memory GitHub 工程雷达（v09 深验证）

**As of 2026-08-10。** 这不是按 stars 排序的项目清单，而是把当前工程生态拆成“新建信号、现有活跃、历史谱系、工程表面、独立采用弱信号与证据缺口”的分析。所有代码均未执行。

## 结论先行

本轮完整观测 59 个仓库：19 个创建于滚动 90 天内，39 个创建于滚动 12 个月内，54 个在 90 天内有 push。

固定 SHA 工程卡显示：可识别 license 46/59、latest release 39/59、CI workflow 40/59、测试路径 53/59、90 天窗口至少两名贡献者 40/59；这些只衡量可检查的工程表面，不等于生产成熟度。

工程主线不是“谁用了更大的向量库”，而是把写入抽取、组织/版本、检索融合、上下文编译和治理拆成可替换层。Mem0、Cognee 与 Neo4j Agent Memory 展示了事实/实体/图/时间/检索融合的复合管线。

同时，写入控制与读出控制开始分离：A-Mem 侧重动态组织和演化，MemChain 让 read-time 选择与证据链显式化。

目前没有单一部署或表示共识：local-first 文件/Wiki、图数据库、托管 API、容器服务和混合形态并存。 

## 1. 架构脉络：从存储层走向记忆控制面

基础操作层已形成 add/remember、search/recall、forget/update 的最小词汇，但不同仓库返回的对象和副作用差异明显：文本片段、图上下文、反思、整合或技能晋升都可能被叫作 memory operation。

复杂架构把事实抽取、实体链接、混合检索、时间/冲突处理和整合连成管线；这类系统的主要工程风险也从“能否查到”扩展到写入污染、陈旧状态、删除/版本、scope 与可审计性。

另一条路线刻意保持简单：append-only 文本、逐字存储或单文件 agent state 优先可检查、保真和迁移，不默认叠加 LLM consolidation、graph 和 hosted service。

## 2. 当前工程分块

**生命周期与选择。** 写入组织、读时选择与后台 consolidation 正在成为独立模块；这使测试可以分别问“记住了什么”“召回了什么”“更新/忘掉了什么”。

**上下文压缩。** Headroom、Claude-Mem、LightMem 所在分支与永久用户事实库相邻但不等价：它们处理工具输出、会话观察、摘要和 token budget，重点是模型前的 context compilation。

**经验与技能。** MemRL、Hivemind、TencentDB Agent Memory 把轨迹转为带效用的策略、技能或团队资产，目标是改变后续行为而非仅返回过去文本。

**个人状态。** MIRIX、OpenHuman、MineEcho 把 profile 扩成 episodic/semantic/procedural/resource、周期摘要、Wiki/图和技能路由；隐私与 scope 因而成为数据模型的一部分。

**编码代理。** 当前实现分为会话观察/摘要、代码结构图和决策/风险图三条路径，说明“记住项目”既包括文本历史，也包括可查询的代码与意图结构。

**共享与迁移。** OMP、Agent File、Markdown/Wiki 资产分别在协议、序列化和人可编辑文件层解决迁移；目前还没有核实过的跨格式互操作共识。

**安全。** 攻击代码、运行时拦截和来源/敏感读取审计已经形成三层工具链，但统一威胁模型和独立对抗评测仍缺失。

**评测。** 新仓库把 backend API、agent runtime、增量多轮、precision/noise isolation/latency 分开，意味着未来不应再用一个总分代表整个 memory system。

## 3. 新建仓库：rolling 90-day

下表按当前 stars 单快照排序，只用于决定检查优先级。`surface` 是 8 项工程表面量表，非质量分数。

| Repository | Cluster | Created | Pushed | stars snapshot | surface | release | claim |
|---|---|---|---|---:|---:|---|---|
| [EverMind-AI/Raven](https://github.com/EverMind-AI/Raven) | MM-C05 | 2026-05-21 | 2026-08-10 | 3532 | 8/8 | v0.1.10 | GR-C059-1, GR-C059-2 |
| [xerj-org/xerj](https://github.com/xerj-org/xerj) | MM-C02 | 2026-06-30 | 2026-08-10 | 1321 | 8/8 | v1.0.0-rc.13 | GR-C006-1, GR-C006-2 |
| [VictorTaelin/OptMem](https://github.com/VictorTaelin/OptMem) | MM-C07 | 2026-07-25 | 2026-07-31 | 1185 | 4/8 | none returned | GR-C018-1, GR-C018-2 |
| [MaxFreedomPollard/Compartment](https://github.com/MaxFreedomPollard/Compartment) | MM-C12 | 2026-07-20 | 2026-08-09 | 701 | 8/8 | v4.5.0 | GR-C046-1, GR-C046-2 |
| [atomicstrata/atomicmemory](https://github.com/atomicstrata/atomicmemory) | MM-C02 | 2026-05-18 | 2026-08-09 | 421 | 7/8 | cli-v0.2.0 | GR-C058-1, GR-C058-2 |
| [Brain0-ai/brain0](https://github.com/Brain0-ai/brain0) | MM-C12 | 2026-07-02 | 2026-07-19 | 368 | 7/8 | v0.1.0 | GR-C034-1, GR-C034-2 |
| [Health-Yang/MineEcho](https://github.com/Health-Yang/MineEcho) | MM-C08 | 2026-05-28 | 2026-06-05 | 245 | 6/8 | none returned | GR-C056-1, GR-C056-2 |
| [AML-memory/agent-memory-leaderboard](https://github.com/AML-memory/agent-memory-leaderboard) | MM-C13 | 2026-07-29 | 2026-08-07 | 232 | 3/8 | none returned | GR-C047-1, GR-C047-2 |
| [410979729/scope-recall-hermes](https://github.com/410979729/scope-recall-hermes) | MM-C04 | 2026-05-15 | 2026-08-08 | 220 | 8/8 | v1.9.1 | GR-C057-1, GR-C057-2 |
| [memorax-ai/memorax-code](https://github.com/memorax-ai/memorax-code) | MM-C09 | 2026-08-01 | 2026-08-10 | 169 | 5/8 | none returned | GR-C025-1, GR-C025-2 |
| [Coding-Dev-Tools/engraphis](https://github.com/Coding-Dev-Tools/engraphis) | MM-C09 | 2026-06-30 | 2026-08-10 | 153 | 8/8 | v1.5 | GR-C026-1, GR-C026-2 |
| [Sibyl-Labs/Sibyl-Memory](https://github.com/Sibyl-Labs/Sibyl-Memory) | MM-C01 | 2026-05-20 | 2026-08-07 | 98 | 8/8 | v0.1.0 | GR-C003-1, GR-C003-2 |
| [mayiwen0212/MemChain](https://github.com/mayiwen0212/MemChain) | MM-C05 | 2026-06-29 | 2026-06-30 | 97 | 5/8 | none returned | GR-C015-1, GR-C015-2 |
| [noamschwartz/atlas-memory-demo](https://github.com/noamschwartz/atlas-memory-demo) | MM-C04 | 2026-05-26 | 2026-07-28 | 93 | 6/8 | none returned | GR-C012-1, GR-C012-2 |
| [SMJAI/open-memory-protocol](https://github.com/SMJAI/open-memory-protocol) | MM-C11 | 2026-06-29 | 2026-07-02 | 73 | 5/8 | none returned | GR-C030-1, GR-C030-2 |
| [zjunlp/LightMem-Ego](https://github.com/zjunlp/LightMem-Ego) | MM-C08 | 2026-05-20 | 2026-07-28 | 65 | 7/8 | v1.0.0 | GR-C022-1, GR-C022-2 |
| [MemTensor/OmniMemEval](https://github.com/MemTensor/OmniMemEval) | MM-C13 | 2026-06-24 | 2026-08-06 | 41 | 6/8 | none returned | GR-C036-1, GR-C036-2 |
| [JingxuanC/causal-memory](https://github.com/JingxuanC/causal-memory) | MM-C03 | 2026-07-26 | 2026-08-10 | 30 | 8/8 | v0.3.1 | GR-C010-1, GR-C010-2 |
| [tenurehq/precisionMemBench](https://github.com/tenurehq/precisionMemBench) | MM-C13 | 2026-05-27 | 2026-07-28 | 13 | 5/8 | none returned | GR-C037-1, GR-C037-2 |

## 4. 当前高关注仓库（非增长榜）

所有 stars 只有一个观测时间点，因此本报告不计算 growth/velocity/acceleration。

| Repository | Bucket | stars snapshot | 90d commits | 90d contributors | surface | current-status caveat |
|---|---|---:|---:|---:|---:|---|
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | newly-created-12m | 90236 | 484 | 36 | 8/8 | single snapshot only; GR-C020-1 |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | newly-created-12m | 65677 | 1186 | 216 | 8/8 | single snapshot only; GR-C040-1 |
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | established-active | 62901 | 394 | 97 | 8/8 | single snapshot only; GR-C002-1 |
| [MemPalace/mempalace](https://github.com/MemPalace/mempalace) | newly-created-12m | 58263 | 728 | 53 | 8/8 | single snapshot only; GR-C038-1 |
| [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | newly-created-12m | 38323 | 1596 | 89 | 8/8 | single snapshot only; GR-C041-1 |
| [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) | newly-created-12m | 36134 | 2758 | 144 | 8/8 | single snapshot only; GR-C042-1 |
| [topoteretes/cognee](https://github.com/topoteretes/cognee) | established-active | 29898 | 1540 | 91 | 8/8 | single snapshot only; GR-C008-1 |
| [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) | established-active | 28834 | 267 | 37 | 8/8 | single snapshot only; GR-C039-1 |
| [volcengine/OpenViking](https://github.com/volcengine/OpenViking) | newly-created-12m | 28136 | 862 | 102 | 8/8 | single snapshot only; GR-C016-1 |
| [letta-ai/letta](https://github.com/letta-ai/letta) | foundational-lineage | 24170 | 6 | 2 | 8/8 | legacy/lineage; GR-C001-1 |
| [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) | newly-created-12m | 19422 | 1040 | 110 | 8/8 | single snapshot only; GR-C043-1 |
| [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | newly-created-12m | 18945 | 8 | 4 | 6/8 | single snapshot only; GR-C031-1 |
| [memvid/memvid](https://github.com/memvid/memvid) | established-active | 16197 | 4 | 2 | 8/8 | single snapshot only; GR-C004-1 |
| [NevaMind-AI/memU](https://github.com/NevaMind-AI/memU) | established-active | 14276 | 140 | 16 | 7/8 | single snapshot only; GR-C044-1 |
| [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | newly-created-12m | 11939 | 83 | 7 | 8/8 | single snapshot only; GR-C029-1 |
| [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | established-active | 10662 | 292 | 40 | 8/8 | single snapshot only; GR-C045-1 |
| [campfirein/byterover-cli](https://github.com/campfirein/byterover-cli) | established-active | 4937 | 185 | 8 | 7/8 | single snapshot only; GR-C024-1 |
| [CortexReach/memory-lancedb-pro](https://github.com/CortexReach/memory-lancedb-pro) | newly-created-12m | 4460 | 121 | 11 | 7/8 | single snapshot only; GR-C053-1 |
| [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) | established-active | 3929 | 15 | 6 | 7/8 | single snapshot only; GR-C009-1 |
| [aiming-lab/SimpleMem](https://github.com/aiming-lab/SimpleMem) | newly-created-12m | 3685 | 46 | 7 | 7/8 | single snapshot only; GR-C011-1 |
| [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) | established-active | 3612 | 372 | 21 | 8/8 | single snapshot only; GR-C023-1 |
| [Mirix-AI/MIRIX](https://github.com/Mirix-AI/MIRIX) | established-active | 3547 | 3 | 2 | 8/8 | single snapshot only; GR-C021-1 |
| [EverMind-AI/Raven](https://github.com/EverMind-AI/Raven) | newly-created-90d | 3532 | 149 | 20 | 8/8 | single snapshot only; GR-C059-1 |
| [microsoft/kernel-memory](https://github.com/microsoft/kernel-memory) | foundational-lineage | 2174 | 1 | 1 | 7/8 | legacy/lineage; GR-C050-1 |
| [activeloopai/hivemind](https://github.com/activeloopai/hivemind) | newly-created-12m | 1541 | 1297 | 9 | 8/8 | single snapshot only; GR-C055-1 |
| [mnemox-ai/tradememory-protocol](https://github.com/mnemox-ai/tradememory-protocol) | newly-created-12m | 1408 | 31 | 2 | 8/8 | single snapshot only; GR-C051-1 |
| [xerj-org/xerj](https://github.com/xerj-org/xerj) | newly-created-90d | 1321 | 907 | 10 | 8/8 | single snapshot only; GR-C006-1 |
| [letta-ai/agent-file](https://github.com/letta-ai/agent-file) | watchlist | 1193 | 0 | 0 | 5/8 | single snapshot only; GR-C048-1 |
| [VictorTaelin/OptMem](https://github.com/VictorTaelin/OptMem) | newly-created-90d | 1185 | 42 | 3 | 4/8 | single snapshot only; GR-C018-1 |
| [zjunlp/LightMem](https://github.com/zjunlp/LightMem) | established-active | 1078 | 26 | 9 | 6/8 | single snapshot only; GR-C019-1 |

特别需要防止累计热度误导当前性：`letta-ai/letta` 的固定 README 已把自身标为 legacy 并指向后继开发面。 `microsoft/kernel-memory` 则明确标为 archived research project。

## 5. 成熟活跃与观察名单

`established-active` 只表示创建较早且 90 天内有 push；是否 strong/moderate 取决于可见工程表面。

| Established-active | Cluster | surface | last push | release | status claim |
|---|---|---:|---|---|---|
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | MM-C01 | 8/8 | 2026-08-07 | v2.0.17 | GR-C002-1 |
| [memvid/memvid](https://github.com/memvid/memvid) | MM-C02 | 8/8 | 2026-07-14 | v2.0.140 | GR-C004-1 |
| [topoteretes/cognee](https://github.com/topoteretes/cognee) | MM-C03 | 8/8 | 2026-08-09 | v1.4.2 | GR-C008-1 |
| [Mirix-AI/MIRIX](https://github.com/Mirix-AI/MIRIX) | MM-C08 | 8/8 | 2026-07-25 | v0.1.6 | GR-C021-1 |
| [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) | MM-C09 | 8/8 | 2026-08-10 | skills-latest | GR-C023-1 |
| [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) | MM-C01 | 8/8 | 2026-08-10 | server-v0.0.7-rc.2 | GR-C039-1 |
| [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | MM-C05 | 8/8 | 2026-08-07 | memos-local-plugin-v2.0.14 | GR-C045-1 |
| [redis/agent-memory-server](https://github.com/redis/agent-memory-server) | MM-C02 | 7/8 | 2026-08-09 | server/v0.15.2 | GR-C005-1 |
| [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) | MM-C03 | 7/8 | 2026-07-29 | v1.0.0 | GR-C009-1 |
| [campfirein/byterover-cli](https://github.com/campfirein/byterover-cli) | MM-C09 | 7/8 | 2026-06-25 | v3.16.1 | GR-C024-1 |
| [NevaMind-AI/memU](https://github.com/NevaMind-AI/memU) | MM-C11 | 7/8 | 2026-08-09 | v2.0.0-beta.0 | GR-C044-1 |
| [zjunlp/LightMem](https://github.com/zjunlp/LightMem) | MM-C07 | 6/8 | 2026-08-06 | none returned | GR-C019-1 |
| [AI-secure/AgentPoison](https://github.com/AI-secure/AgentPoison) | MM-C12 | 5/8 | 2026-06-17 | none returned | GR-C032-1 |
| [HUST-AI-HYZ/MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench) | MM-C13 | 5/8 | 2026-05-21 | none returned | GR-C035-1 |

观察名单不是失败项目清单；它表示当前证据不足以进入主推荐面。完整原因见 `selection.md`。

| Watch item | Cluster | Bucket | surface | why watch |
|---|---|---|---:|---|
| [WujiangXu/A-mem](https://github.com/WujiangXu/A-mem) | MM-C05 | watchlist | 4/8 | No push in the rolling 90-day window; retained as a bounded watch item rather than a current trend. (GR-C014-1) |
| [VictorTaelin/OptMem](https://github.com/VictorTaelin/OptMem) | MM-C07 | newly-created-90d | 4/8 | Recent creation deeply inspected; engineering surface determines keep versus watchlist. (GR-C018-1) |
| [shihao1895/MemoryVLA](https://github.com/shihao1895/MemoryVLA) | MM-C10 | newly-created-12m | 3/8 | Frontier-window creation deeply inspected; engineering surface determines keep versus watchlist. (GR-C028-1) |
| [AML-memory/agent-memory-leaderboard](https://github.com/AML-memory/agent-memory-leaderboard) | MM-C13 | newly-created-90d | 3/8 | Recent creation deeply inspected; engineering surface determines keep versus watchlist. (GR-C047-1) |
| [letta-ai/agent-file](https://github.com/letta-ai/agent-file) | MM-C11 | watchlist | 5/8 | No push in the rolling 90-day window; retained as a bounded watch item rather than a current trend. (GR-C048-1) |
| [supermemoryai/memorybench](https://github.com/supermemoryai/memorybench) | MM-C13 | newly-created-12m | 4/8 | Frontier-window creation deeply inspected; engineering surface determines keep versus watchlist. (GR-C052-1) |
| [jakops88-hub/Long-Term-Memory-API](https://github.com/jakops88-hub/Long-Term-Memory-API) | MM-C01 | watchlist | 3/8 | Audit-requested relevant API repository, but no rolling-90d push or independent deployment evidence. (GR-C054-1) |

审计点名的 `Long-Term-Memory-API` 已核实为 MemVault/GraphRAG 项目；由于 90 天内无 push 且没有独立部署证据，保留为 watchlist。

## 6. 采用、工程质量与流行度必须分开

本轮有界 code-search 在 8 个目标之外、且至少一个不同 owner 的公开仓库中核实了依赖或集成文本；不同 owner 不保证组织独立，它也不证明生产部署。

10 个 adoption 查询中 9 个留下 target-specific 公开引用；MemOS 查询因 `MemoryOS` 名称碰撞被主动丢弃。其他仓库没有被推断为“无人采用”，而是保持未验证。

工程质量也没有压成一个总分：本包保留 license、setup、CI、tests、release、commit/contributor window、archive/fork、固定 SHA 和执行真值。stars 与 forks 永远不填 adoption 字段。

## 7. 共识、分歧与决策建议

**较强工程共识：** memory 必须有明确写入/读取边界、scope/identity、可更新或可忘却路径，以及能被 agent 框架调用的稳定接口。这个共识是接口形状，不是协议兼容。

**仍然分歧：** 图 vs 文件/Wiki、LLM consolidation vs append-only、managed vs local-first、自动写入 vs review gate。当前仓库证据支持并存而非单一路线。  

**决策建议：** 先按数据边界与失败成本选架构。用户偏好/身份优先 scope、删除和审计；编码代理优先项目结构与来源；团队技能优先 review/ownership；高敏感场景先做写入拦截和 tamper/provenance，再比较召回分数。  

**反转条件：** 若跨项目兼容测试证明某一协议可无损迁移多类 memory asset，或独立部署/事故数据证明某种架构显著更可靠，本报告关于“多契约并存”的判断应重开。

## 8. 关键缺口

PHILIA 是有效的 rolling-90d 具身 memory 论文信号，但没有定位到 canonical repository；因此具身 cluster 的工程雷达仍证据薄。

当前没有第二个 stars 观测点、没有统一 issue/PR health protocol、没有运行第三方代码，也没有对 59 个项目全量做独立 deployment 搜索。任何性能、生产可用性或增长判断都必须继续深查。

---

证据入口：`sources.jsonl` → `claims.jsonl` → `evidence.jsonl`；逐仓固定 SHA 工程卡见 `repositories.jsonl`；完整选择/淘汰原因见 `selection.md`。

## 9. 跨论文与 GitHub 的趋势综合

### 2. Deep radar：五个最重要的变化

#### T1 — Mutation/control plane 从隐式启发式变成可选择、可恢复、可评测的动作集

**新信号。** MemCon 把 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 建模为在线 policy actions；MemTxn 把 source-supported validation、temporal version selection 与 snapshot recovery 放到 answer model 外；budgeted-consolidation 显式建模 operator×budget；ForgetEval 分开 recall 与 supersede/release/purge。 `[FND-C14,FND-C17,FND-C19,FND-C21; FND-S09,FND-S10,FND-S11,FND-S12]`

**确认范围。** 多个独立机制表明“如何管理 memory”已成为研究对象，而不只是某 retriever 的参数。

**反证/限制。** MemCon 的收益没有本包内独立复现；consolidation 没有普遍 operator ranking；ForgetEval 结果受 model/backend/protocol 影响。 `[FND-C16,FND-C20,FND-C22; FND-S09,FND-S11,FND-S12]`

**状态：qualified。** 研究方向确认；性能和生产控制保证未确认。

#### T2 — Representation 的竞争点从 vector-vs-graph 转为“哪些语义能穿过编译链”

**新信号。** AtomMem 保存 atomic facts→events→temporal profiles；bitemporal store 保存 identity/version 与 valid/transaction time；Hindsight 分 world facts、experiences、entity summaries、beliefs；MemMachine 在实现中分 episodic graph、SQL profile、working memory。 `[REP-C01,REP-C02,REP-C08,REP-C14; REP-S01,REP-S02,REP-S11,REP-S22]`

**为什么重要。** 这些设计都在尝试让 time、scope、provenance、type、conflict 在 representation→index→retrieval→context compiler 中不丢失。这个归纳是 report inference。 `[REP-C22; REP-S02,REP-S03]`

**反证。** bitemporal time-travel path 有问题类型间反向结果；LightMem reproduction 表明 memory construction 可损失 answer-relevant detail，retriever 本身可能主导结果。 `[REP-C03,REP-C05,REP-C06; REP-S02,REP-S03]`

**状态：mixed but decision-relevant。** 结构语义的需求明确，哪种表示/查询计划更优仍取决于 protocol。

#### T3 — Security 已形成“低信任写入 → 持久状态 → 检索 → 行动 → 修复”的威胁链

**信号序列。** AgentPoison 建立 backdoor poisoning；MEXTRA 做 black-box extraction；MINJA 降低为 query/observation-only；eTAMP 把来源扩到环境；sleeper memory 测 write/retrieve/action；MAFIA 针对 benign pools + active auditing；Salami 用 individually benign fragments 组合；MutMem/DP-MemView/STALE 分别约束 mutation provenance、adaptive transcript privacy 与 update→behavior adaptation。 `[OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C10,OPS-C11,OPS-C12,OPS-C14,OPS-C16; OPS-S01,OPS-S02,OPS-S03,OPS-S05,OPS-S06,OPS-S08,OPS-S09,OPS-S10,OPS-S11,OPS-S12]`

**反证/限制。** MutMem 自己说明 authorization/traceability 不证明 truth；生产 API 与 Agent Memory Guard 只展示 control surface，未独立验证全链。 `[OPS-C13,OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C23,OPS-C24,OPS-C25,OPS-C27]`

**状态：threat surface confirmed; defense evidence-thin。**

#### T4 — Benchmark 由“记得吗”迁移到“写、改、做、共享、感知、忘与修复了吗”

**新 protocol families。** incremental lifecycle（MemoryAgentBench/Memora/HaluMem）、tool/action（Mem2ActBench/MemoryArena）、group/organizational（GroupMemBench/MEMTRACK）、multimodal/embodied（Mem-Gallery/EMemBench）、implicit/procedural（ImplicitMemBench）、security lifecycle（MemSecBench）。 `[BEN-C03,BEN-C05,BEN-C06,BEN-C07,BEN-C10,BEN-C11,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16]`

**反证/限制。** static QA、action success、first-attempt adaptation 和 write–execute–forget 的 task unit、memory access、agent loop、judge、metric 不同。 `[BEN-C22; BEN-S01,BEN-S11,BEN-S14,BEN-S16]`

**状态：confirmed diversification。** 统一 harness 可标准化 execution envelope，但不能抹掉 protocol label；当前 OmniMemEval/MemoryData 只作为 harness candidates。 `[BEN-C23; BEN-S26,BEN-S27]`

#### T5 — Memory object 本身分化：procedure、principal-scoped state、identity 与 world state

**新信号。** MemP 保存 instruction/script；MemSkill 演化 memory-operation skill；XSkill 分 action-level experience 与 task-level skill；Collaborative Memory 增加 private/shared provenance/policy；POLAR 分 personalized semantic/visual concepts 与 embodied episodes；WorldLines/MeMento 处理 partial observation 和 multimodal compression。 `[EXP-C06,EXP-C09,EXP-C10,EXP-C11,EXP-C12,EXP-C14,EXP-C15]`

**反证/限制。** 这些 protocol 不可直接排名；shared repository artifacts 没有独立 adoption、tenant isolation 或 revocation proof；STALE 表明状态更新后行为仍可能陈旧。 `[EXP-C13,EXP-C21,EXP-C22; EXP-S13,EXP-S19..EXP-S23]`

**状态：qualified taxonomy shift。** 四类对象边界决策有效，性能排序未闭合。

<!-- synthesis:TREND-AUTO-01 claims:BEN-C03,BEN-C05,BEN-C06,BEN-C07,BEN-C10,BEN-C11,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16,BEN-C22,BEN-C23,EXP-C06,EXP-C09,EXP-C10,EXP-C11,EXP-C12,EXP-C13,EXP-C14,EXP-C15,EXP-C21,EXP-C22,FND-C14,FND-C16,FND-C17,FND-C19,FND-C20,FND-C21,FND-C22,OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C10,OPS-C11,OPS-C12,OPS-C13,OPS-C14,OPS-C16,OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C23,OPS-C24,OPS-C25,OPS-C27,REP-C01,REP-C02,REP-C03,REP-C05,REP-C06,REP-C08,REP-C14,REP-C22 clusters:MM-C05,MM-C12,MM-C13 -->

### 4. 反证雷达

| 反证 | 它削弱什么结论 | 当前处理 |
|---|---|---|
| LightMem reproduction：retriever 与预算可反转 constructed-memory 优势 `[REP-C05,REP-C06]` | “压缩/结构化 store 默认优于 raw history” | 所有表示比较必须固定 retriever、k、reader、token budget |
| Bitemporal sample：update recall 上升但 temporal reasoning 下降 `[REP-C03]` | “更多版本/时间过滤默认改善所有 query” | intent-specific candidate generation；禁止总分外推 |
| Budgeted consolidation 无普遍 operator ranking `[FND-C19,FND-C20]` | “始终 merge/abstract/rewrite” | operator 绑定 budget、task distribution、recoverability |
| STALE：新状态存在但行为仍旧 `[EXP-C13]` | “更新 store 就完成 correction” | 测 propagation、policy adaptation 与 action-time revalidation |
| Benchmarks 协议不兼容 `[BEN-C22,BEN-C25]` | “单 leaderboard 代表 memory 能力” | 按 protocol family 输出 outcome vector |
| Provenance 不证明 truth `[OPS-C12,OPS-C13,OPS-C17]` | “签名/日志等于可信内容” | 另建 authority、semantic reconciliation、action authorization |

<!-- synthesis:TREND-AUTO-03 claims:BEN-C22,BEN-C25,EXP-C13,FND-C19,FND-C20,OPS-C12,OPS-C13,OPS-C17,REP-C03,REP-C05,REP-C06 clusters:MM-C05,MM-C12,MM-C13 -->

### 5. Watchlist 与缺口优先级

#### P0：会改变当前工程决策

1. **删除传播与恢复：** raw record、summary、embedding/index、revision、cache、backup、tool trace 的 purge/rollback contract。
2. **跨 backend 独立 lifecycle reproduction：** MemCon、MemTxn、ForgetEval、budgeted consolidation 的 matched protocol。
3. **全链 security benchmark：** poisoning/extraction/stale repair/scope isolation/action authorization/cost 在同一 harness 下测试。
4. **adoption 与 operations：** p50/p95 write/read/repair、storage growth、human review load、真实 tenant isolation；当前 sources 不足。

#### P1：会改变 field map 或趋势判断

1. **Coding/project memory（MM-C09）：** final primary=307；all-membership R12=352、R90=218。专属 deep packet 已比较结构索引、事件溯源、静态上下文反证与反馈策略，后续重点转为 branch/worktree、secret、index invalidation 与独立执行。
2. **Model-native boundary（MM-C15）：** final primary=25；all-membership R12=35、R90=28。需要与 external memory 在 deletion、provenance、update、latency 下做同协议比较。
3. **Portable/shared standards（MM-C11）：** mapped signal 不等于标准；需 normative spec、versioning/merge semantics、independent implementations。
4. **Graphiti identity：** deep packet 明确未在 v09 mapped corpus 找到 canonical `getzep/graphiti` entity，相关工程结论保持空白。 `[REP-C20; REP-S23]`
5. **Gap-fill incremental map：** 新发现必须完成 identity、future quarantine 与 canonical assignment 才能更新密度表。

<!-- synthesis:TREND-AUTO-04 claims:REP-C20 clusters:MM-C05,MM-C12,MM-C13 -->

### 6. 趋势停止/继续条件

继续追踪某信号，若新证据能：改变一阶 cluster boundary；提供独立 reproduction；把 repository signal 变成 verified architecture/operation/adoption evidence；反转上述反证；或补齐 rolling-90d 的 opposing stance。

停止扩展某一子方向，只有在连续 expansion 不再增加机制、边界、反证、代表实现或 decision conclusion，并把剩余 gaps 明确写出。当前 timeline 的机制主线已 decision-useful；工程成熟度、采用、删除与独立防御尚未饱和。

## 10. Star growth 跟踪：为什么没有增长榜

GitHub 在 2026 年 7 月开始把 repository stargazer-list endpoint 限制给管理员和协作者；这使第三方难以继续从公开事件流稳定复原其他仓库的历史。见 [GitHub REST 文档](https://docs.github.com/en/rest/activity/starring) 与 [GitHub changelog](https://github.blog/changelog/2026-06-30-upcoming-access-restrictions-to-public-api-endpoints-and-ui-views/)。

本轮仍对 59/59 个 radar 仓库运行一次 [OSSInsight stargazer-history](https://ossinsight.io/docs/api/stargazers-history) 有界核验：可用于窗口 delta 的只有 1 个，另有 3 个仅可诊断，55 个因事件累计值与 GitHub 当前 stars 快照明显不一致或无历史行而不可用。因此本报告明确关闭跨仓库 star-growth/acceleration 排名，不把缺失历史补成 0，也不以当前累计 stars 冒充增长。

工程趋势改用可直接观察的当前信号：19/59 在 rolling 90 days 内新建、39/59 在 rolling 12 months 内新建、54/59 在 90 天内有 push、34/59 在 90 天内有 release，并结合 90 天 commit/contributor、固定 SHA 架构、测试/CI 与维护边界决定是否深读。这些是调查触发器，不是质量、成熟度或生产采用证明。完整 provider 覆盖审计见 [star-growth packet](../../work/github-radar/star-growth/report.md)。

<!-- process:limitation -->
## GitHub 雷达原子证据附录

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

本轮对 59 个候选仓库完成了完整 GitHub 状态观测；其中 19 个创建于滚动 90 天内，39 个创建于滚动 12 个月内，54 个在滚动 90 天内有 push。
<!-- claim:GR-C-RUN01 -->

在 59 个固定 SHA 工程卡中，46 个返回可识别 SPDX license，39 个有 latest release，40 个检查到 CI workflow，53 个检查到测试路径，40 个在 90 天提交窗口内有至少两名可归属贡献者；1 个 tree/README 深检为 partial。
<!-- claim:GR-C-RUN02 -->

代表性工程已从“向量库加相似度搜索”扩展为复合记忆管线：Mem0 的当前自述把事实抽取、实体链接、BM25/语义融合与时间排序放在同一链路；Cognee 与 Neo4j Agent Memory 则把向量检索、知识图谱、关系抽取和审计/整合能力组合起来。
<!-- claim:GR-C-M001 -->

“写入什么”和“读出什么”已经成为两个独立控制面：A-Mem 在写入侧做动态组织与演化，MemChain 在读出侧显式决定 keep/drop/refine/merge 并生成可检查的 memory trace。
<!-- claim:GR-C-M002 -->

工程路线并未收敛到单一表示：OpenViking 用 viking:// 虚拟文件系统和 L0/L1/L2 分层加载，MemPalace 保留逐字文本并允许替换检索后端，OptMem 则选择 append-only 日志加正则召回。
<!-- claim:GR-C-M003 -->

部署边界没有形成单一共识：Mem0 同时提供 library/self-hosted/cloud，Neo4j Agent Memory 保持 hosted NAMS 与 self-hosted Bolt 的同 API，OpenHuman 与 MineEcho 强调 local-first，而 Hindsight 推荐容器/服务加客户端。
<!-- claim:GR-C-M015 -->

README 中常见的 add/remember、search/recall、forget/update 等动词形成了事实上的最小接口共识，但底层语义差异很大：有的返回文本片段，有的返回图上下文，有的还执行 reflect/consolidate 或 skill promotion。
<!-- claim:GR-C-M016 -->

最小实现仍有明确位置：OptMem 的 append-only 文件加 regex、MemPalace 的逐字保存、Agent File 的单文件序列化分别优先可检查性、保真和迁移；它们提醒工程选择不应默认把图、LLM consolidation 和托管服务全部叠加。
<!-- claim:GR-C-M017 -->

上下文压缩与长期事实记忆是相邻但不同的工程层：Headroom 在模型前压缩工具输出、日志、代码和历史并保留可逆取回；Claude-Mem 从编码会话中提取观察与语义摘要；LightMem 同时提供记忆管理、MCP 和基准脚本。
<!-- claim:GR-C-M004 -->

程序性记忆的工程目标是把成功轨迹变成可复用策略或技能，而不只是保存对话：MemRL 把反馈效用引入两阶段检索，Hivemind 从团队轨迹提炼技能，TencentDB Agent Memory 把会话和工具轨迹转成可审核、可分享的 Skill 资产。
<!-- claim:GR-C-M005 -->

个性化记忆正在从单一 user profile 扩展为多层状态：MIRIX 分出 core/episodic/semantic/procedural/resource/knowledge-vault，OpenHuman 把个人数据压缩为本地图结构，MineEcho 同时保留交互记忆、周期摘要、Wiki/图与技能路由。
<!-- claim:GR-C-M006 -->

编码代理记忆形成了三种互补路径：Claude-Mem 保存会话观察与摘要，codebase-memory-mcp 把代码解析为可查询结构图，Brain0 把提交、符号、代理轨迹与风险/意图连成决策图。
<!-- claim:GR-C-M007 -->

“可移植”至少有三种互不等价的实现：OMP 规定 memory object/storage/HTTP API，Agent File 序列化 prompt、editable memory、tools 与模型设置，EverOS/memU 则把 Markdown/Wiki 作为跨代理可读写资产。
<!-- claim:GR-C-M008 -->

安全工程已经覆盖“攻击—运行时阻断—审计”三层：AgentPoison 提供 memory/knowledge-base poisoning 的红队代码，OWASP Agent Memory Guard 在存取路径上执行检测器与策略，Brain0 增加敏感读取和来源/意图审计。
<!-- claim:GR-C-M009 -->

评测仓库正在拆开以往混在一起的能力：MemoryAgentBench 关注增量多轮交互中的检索、测试时学习等能力；OmniMemEval 分为 memory-backend API 与带插件 agent runtime 两条轨；PrecisionMemBench 单独检查精度、噪声隔离和会话延迟。
<!-- claim:GR-C-M010 -->

所有 bundle 内 GitHub stars 数据都来自同一轮单快照；因此本报告不从这些 GitHub snapshots 计算或声称任何仓库的 star growth、velocity 或 acceleration。
<!-- claim:GR-C-RUN03 -->

仓库热度与当前实现位置可能分离：letta-ai/letta 的固定 README 明确称该仓库为 legacy server，并把活跃开发指向 letta-code/App Server，因此其累计 stars 不能直接代表当前代码面的活跃度。
<!-- claim:GR-C-M012 -->

microsoft/kernel-memory 当前应作为历史/集成谱系而非活跃候选：其固定 README 自称 archived research project、无支持、非 production software。
<!-- claim:GR-C-M013 -->

Long-Term-Memory-API 实际解析为 MemVault/GraphRAG 托管 API 仓库，并在 README 中声明定时 consolidation、pgvector hybrid search 与图抽取；但其最近 push 不在本轮 90 天窗口，且没有独立部署证据，因此只进入观察名单。
<!-- claim:GR-C-M018 -->

本轮 GitHub code-search 的有限抽样在目标仓库之外、且至少一个不同 owner 的公开仓库中核实了 mem0ai、letta-client、cognee、memvid、basic-memory、Microsoft.KernelMemory、hindsight-client 与 LightMem 的依赖或集成文本；这些只证明存在公开代码引用，不证明生产部署、用户规模或效果。
<!-- claim:GR-C-M014 -->

本轮只对 10 个目标运行了有界 GitHub code-search adoption 查询，其中 9 个查询保留了目标仓库之外的可核实公开代码引用；不同 owner 不保证组织独立，其余仓库的独立部署证据保持未验证。
<!-- claim:GR-C-RUN04 -->

具身记忆仍是工程证据薄弱的边界：MemoryVLA 仓库提供 paper-linked 机器人操控代码与多个分支，但 PHILIA 在本轮检查的论文页面和三条精确 GitHub repository 查询中没有出现可核实的 canonical repository。
<!-- claim:GR-C-M011 -->
