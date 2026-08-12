# GitHub 候选雷达：从“记忆库”到可拆分的记忆系统

**观察截止：2026-08-10。** 本页是工程候选地图，不是排行榜。它把 59 个已观察仓库中值得继续理解的实现，按其在 Memory 生命周期中承担的角色放回技术脉络；重点项目的固定版本代码分析见 [projects/](projects/)。

## 先读这一页时应知道什么

Agent Memory 的 GitHub 生态正在从“给文本做向量检索”扩展成一条可拆开的链路：捕获与抽取、权威状态与派生索引、召回与上下文打包、更新/遗忘、权限与可迁移接口。项目之间最实质的区别通常在这些边界如何划分，而非是否提供一个名为 `memory` 的 API。

截至观察日，59 个仓库中有 19 个创建于滚动 90 天、39 个创建于滚动 12 个月；54 个在滚动 90 天内有提交。46 个可识别许可证、39 个有 release、40 个有 CI 工作流、53 个能找到测试路径。这些是可见工程表面，不是可靠性、性能、生产采用或“增长质量”的证明。

星标只是一张累计关注度快照。本轮对所有项目只有一个星标观测点，因此不声称任何项目“增长更快”或“正在加速”；提交数、贡献者数和 open issue 同样只能解释为有限的活动线索。

## 候选如何阅读

| 所在链路 | 当前可见路线 | 候选项目（非排序） | 这里真正值得比较的工程问题 |
|---|---|---|---|
| 写入、抽取与生命周期 | 对话抽事实、候选/整合、版本与因果边 | [mem0](https://github.com/mem0ai/mem0)、[Sibyl Memory](https://github.com/Sibyl-Labs/Sibyl-Memory)、[Causal Memory](https://github.com/JingxuanC/causal-memory)、[scope-recall-hermes](https://github.com/410979729/scope-recall-hermes)、[MemOS](https://github.com/MemTensor/MemOS) | 写入失败后是否留下原文、更新/冲突是否可见、权威数据与索引是否可恢复 |
| 表示、存储与索引 | 多层资源树、图/实体、向量+关键词、文件或本地 vault | [OpenViking](https://github.com/volcengine/OpenViking)、[cognee](https://github.com/topoteretes/cognee)、[memvid](https://github.com/memvid/memvid)、[xerj](https://github.com/xerj-org/xerj)、[Compartment](https://github.com/MaxFreedomPollard/Compartment) | 是单一权威库还是权威状态加可重建索引；异步索引延迟、迁移与加密怎样处理 |
| 检索、上下文与 Agent 使用 | 多路融合、预算打包、生命周期 hook、插件化后端 | [Raven](https://github.com/EverMind-AI/Raven)、[claude-mem](https://github.com/thedotmack/claude-mem)、[Engraphis](https://github.com/Coding-Dev-Tools/engraphis)、[headroom](https://github.com/headroomlabs-ai/headroom)、[basic-memory](https://github.com/basicmachines-co/basic-memory) | 写入和读出是否解耦；召回遗漏时宿主如何退化；身份、项目和会话 scope 怎样贯穿 |
| 多人、治理与可迁移 | schema、命名空间、共享/私有边界、加密 | [Open Memory Protocol](https://github.com/SMJAI/open-memory-protocol)、[agent-file](https://github.com/letta-ai/agent-file)、[trade memory protocol](https://github.com/mnemox-ai/tradememory-protocol)、[OpenHuman](https://github.com/tinyhumansai/openhuman)、[Compartment](https://github.com/MaxFreedomPollard/Compartment) | 字段不是授权；导入导出能否保留语义、过期/撤销和跨租户边界是否真的落实 |
| 评测与比较基础设施 | backend adapter、生命周期隔离、任务 verifier | [OmniMemEval](https://github.com/MemTensor/OmniMemEval)、[MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench)、[agent-memory-leaderboard](https://github.com/AML-memory/agent-memory-leaderboard)、[precisionMemBench](https://github.com/tenurehq/precisionMemBench) | 不同 API 与清理语义是否被错误归一；模型、judge、数据和后端版本能否复现 |

这张表用于说明方案空间，不表示哪一行更好，也不表示各仓库具有相同成熟度或可互换性。

## 当前主流：已被反复工程化的形态

**记忆服务层。** [mem0](https://github.com/mem0ai/mem0)、[supermemory](https://github.com/supermemoryai/supermemory)、[MemOS](https://github.com/MemTensor/MemOS) 与 [Redis Agent Memory Server](https://github.com/redis/agent-memory-server) 都把宿主 Agent 与具体后端隔开：调用侧提交带 scope 的消息或事实，服务侧负责抽取、索引和查询。但“统一 API”并不自动带来统一能力；例如混合检索、实体索引、删除和历史在不同后端中可能是可选或降级的。

**编码与会话记忆。** [claude-mem](https://github.com/thedotmack/claude-mem)、[basic-memory](https://github.com/basicmachines-co/basic-memory)、[byterover-cli](https://github.com/campfirein/byterover-cli) 和 [Engraphis](https://github.com/Coding-Dev-Tools/engraphis) 表明，项目记忆除了聊天摘要，还可能包括工具观察、代码符号、决策、时间线和来源。它们的共同难点是：捕获不能妨碍开发流程，而漏捕获、会话标识错误或项目边界错误又会使后续召回失去可信度。

**结构化/分层状态。** [OpenViking](https://github.com/volcengine/OpenViking)、[cognee](https://github.com/topoteretes/cognee)、[HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) 与 [memU](https://github.com/NevaMind-AI/memU) 把实体、关系、资源层级或时间放进检索路径。这改变了可回答的问题，也引入异步建图、派生索引和源状态不一致的运维问题。

## 近 12 个月：工程重心的移动

2025-08-10 至 2026-08-10 创建的项目中，Terminal/IDE 接入、资源/技能统一建模和可替换后端格外显眼。新建的 [Raven](https://github.com/EverMind-AI/Raven)、[OpenViking](https://github.com/volcengine/OpenViking)、[claude-mem](https://github.com/thedotmack/claude-mem)、[MemPalace](https://github.com/MemPalace/mempalace)、[codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)、[OpenHuman](https://github.com/tinyhumansai/openhuman) 和 [Hindsight](https://github.com/vectorize-io/hindsight) 具有较高关注或近期活动，但这仍不足以证明其架构已经稳定。

一个更有意义的共同信号是：写入控制与读时控制正在分开。项目不再只讨论“存什么”，还显式出现候选、审核、整合、检索融合、token 预算、反馈与恢复等位置。该分化是工程方向的变化，不是某个仓库已经解决这些问题的证明。

## 近 90 天：应继续观察的弱信号

2026-05-13 至 2026-08-10 的新建项目横跨搜索引擎、桌面 Agent、协议与评测，说明边界仍在移动：

- [Raven](https://github.com/EverMind-AI/Raven)：终端 Agent 以插件协议挂接记忆后端。
- [xerj](https://github.com/xerj-org/xerj)：把检索引擎作为 Agent Memory 的底座，而不是 Memory SDK。
- [Causal Memory](https://github.com/JingxuanC/causal-memory)：把决策—结果边显式写入 SQLite，并把原始会话与可召回事实分开。
- [Compartment](https://github.com/MaxFreedomPollard/Compartment)：本地加密 vault，把密钥、嵌入模型身份与检索放在同一封装中。
- [Open Memory Protocol](https://github.com/SMJAI/open-memory-protocol)：尝试定义可交换对象和 reference server，但尚不能由此推出协议生态已经形成。
- [OmniMemEval](https://github.com/MemTensor/OmniMemEval) 与 [agent-memory-leaderboard](https://github.com/AML-memory/agent-memory-leaderboard)：把比较焦点从单次问答扩展到生命周期、隔离与任务验证。

这些项目中有些工程表面已完整，有些尚缺 release、多人维护或长期运行证据。新近性只能说明“值得检查”，不能直接升级为主流结论。

## 重点工程报告：为什么只选八个

以下八个不是“最佳八个”。它们被选择是因为代码结构分别揭示了不同的架构边界：服务层、多层资源系统、宿主插件、会话 hook、本地单库、因果/生命周期、加密 vault 与交换协议。评测项目保留在候选层，避免把评测编排仓误作可部署记忆系统。

- [mem0：抽取驱动的服务层与多后端能力差异](projects/mem0ai--mem0.md)
- [OpenViking：资源、记忆与技能共用的分层文件系统](projects/volcengine--openviking.md)
- [Raven：终端 Agent 如何以协议接入记忆后端](projects/evermind-ai--raven.md)
- [claude-mem：编码会话的 hook、worker 与双存储索引](projects/thedotmack--claude-mem.md)
- [Engraphis：本地单库、版本历史与代码图的组合](projects/coding-dev-tools--engraphis.md)
- [Causal Memory：原始日志、事实与因果边的分层](projects/jingxuanc--causal-memory.md)
- [Compartment：加密本地 vault 的边界](projects/maxfreedompollard--compartment.md)
- [Open Memory Protocol：交换 schema 与 reference server 的真实能力](projects/smjai--open-memory-protocol.md)

## 仍不能从这批仓库得到的结论

目前不能可靠回答“复杂生命周期系统比简单向量检索多带来多少收益、代价多少”。各项目的模型、抽取策略、后端、任务、数据边界和 token 预算不同；很多公开 benchmark 与托管产品结论也不能直接归因于对应 OSS 提交。还缺少跨 backend 的同任务、同预算、带删除/恢复/权限扰动的独立比较。

同样，公开 star、安装说明、CI 和 release 不能证明生产采用。除少量公开依赖线索外，本轮未核实第三方部署、SLO、安全审计、PR 响应时间、issue 关闭率或多人维护风险；这些未知不是负面结论，而是这份雷达的边界。

## 证据边界

所有固定版本、提交活跃度、release、许可证和测试/CI 可见性来自 v09 在 2026-08-10 保存的 GitHub/API 快照与固定源码检查；本轮未运行仓库。项目页将“代码可见”“README 声称”“根据代码作出的推断”分开写出。完整观测和审计材料保留在 v09 底稿，不占用读者正文。
