# Raven：让终端 Agent 以插件协议使用记忆

[EverMind-AI/Raven](https://github.com/EverMind-AI/Raven) 的特殊之处是它本身是 terminal Agent harness，而非独立 Memory 数据库。它把记忆后端缩进一个 `MemoryBackend` 协议和 manifest 驱动的插件发现机制中：Agent 在 turn 前召回，在 turn 后存储/反馈。这个设计揭示了“Memory 如何被宿主使用”这一层，而不是某一种存储方案。

**固定观察。** 检查提交为 [`14b7419`](https://github.com/EverMind-AI/Raven/tree/14b7419245b816782b0435385d238f9f18ac090f)。仓库 2026-05-21 创建，2026-08-10 有 push，已观察到 `v0.1.10` release；滚动 90 天为 149 commits、20 位贡献者、70 个 open issue。Apache-2.0、CI、测试和安装说明可见；3,532 stars 是单次快照，不是趋势或采用结论。

## 组件与调用方向

[`raven/memory_engine/backend.py`](https://github.com/EverMind-AI/Raven/blob/14b7419245b816782b0435385d238f9f18ac090f/raven/memory_engine/backend.py) 定义 `recall/store/feedback/start/stop` 与 user/agent 双轨身份，并仅在选中插件后导入对应 factory。`context_engine` 在模型调用前渲染受预算限制的 memory segment；AgentLoop 负责每 turn 的召回、会话片段存储和反馈。另一个 `skill_forge` 将 memory hits 与本地/Hub skill 候选合并、评分和门控。

默认 bundled 路线适配 EverOS，不过真正的提取、检索和持久化主要在精确 pin 的 `everos` 包中；Raven 提供的是宿主接口和生命周期整合，而不是完整实现 EverOS 的所有内部数据模型。项目的[插件架构文档](https://github.com/EverMind-AI/Raven/blob/14b7419245b816782b0435385d238f9f18ac090f/docs/memory-plugin-architecture.md)对此划分最清楚。

## 一个 turn 的数据流

1. 配置选择 `memory.backend`，manifest/factory 启动相应后端。
2. AgentLoop 为当前 turn 传递 query、`user_id`、`agent_id`、`top_k` 到 `recall`。
3. 返回的 memory 被 `context_engine` 裁剪、渲染，必要时与 skill 候选融合，再放入本轮上下文。
4. turn 完成后，AgentLoop 将 session slice 交给 `store`，再将可用反馈交给 `feedback`。

这条链令后端可替换，但宿主和后端仍需共享准确的身份及生命周期语义；插件接口只是边界，不是自动互操作保证。

## 依赖、部署与版本陷阱

[`pyproject.toml`](https://github.com/EverMind-AI/Raven/blob/14b7419245b816782b0435385d238f9f18ac090f/pyproject.toml) 精确 pin `everos[multimodal]==1.2.1`，并依赖 LiteLLM、httpx、Pydantic、MCP 及渠道扩展。该精确 pin 的原因不是形式主义：EverOS adapter 使用了内部 API。按文档升级 EverOS 时应重新核对适配层，可能需要重建 `~/.everos/.index`；随意放宽版本范围会把 API/index 迁移风险带进 Agent 主循环。

`memory.userId` 与 `memory.agentId` 是唯一身份来源。若 store 和 recall 使用不同轨道，数据可以成功写入却永远召不回来，或落入错误轨道。这个约束比“插件能否加载”更影响跨会话正确性。

## 可见故障模式

- 插件 factory、import 或依赖初始化失败时，文档表示宿主会退化为 no backend：Agent 继续运行，但持久记忆缺失。
- EverOS 的内部 API 或 index schema 变化时，adapter 的 import、搜索或 `memorize` 可能失败，需要重建或迁移。
- user/agent 双轨身份不一致时，召回错误或跨轨暴露是合理风险；本研究未运行端到端的跨身份测试。

## 维护边界与未知

Raven 的代码能说明 host contract、bundled adapter 与 context 注入方式，不能证明第三方 Memory 插件的兼容矩阵，也不能证明 Raven/EverOS 的独立生产采用。快照未测 PR 时延、issue 关闭率、跨平台安装和 EverOS migration。README 的生态和测试数量属于维护方声明，未在本研究中复现。

**证据边界。** 本页以提交 `14b7419` 的协议、配置和架构文档为准，未运行 Agent、插件或 EverOS。
