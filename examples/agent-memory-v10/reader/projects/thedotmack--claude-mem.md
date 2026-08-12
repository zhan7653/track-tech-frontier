# claude-mem：把编码会话捕获接到异步记忆流水线

[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) 关注的不是长期用户 profile，而是“开发时发生过什么”。它利用 Claude Code/OpenCode 的生命周期 hook 收集 prompt、工具观察和 session 结束事件，再以每用户 worker 将这些事件整理为 observation 和 summary。它是理解 Coding Agent Memory 的一个好案例：写入完整性与不中断 IDE/CLI 工作流之间存在直接张力。

**固定观察。** 检查提交为 [`4702c33`](https://github.com/thedotmack/claude-mem/tree/4702c337d85aa12e8ab7f845264a78885676261f)。2026-08-10 快照中，仓库创建于 2025-08-31、最新 push 为 2026-08-10、release 为 `v13.14.0`，滚动 90 天有 484 commits、36 位贡献者和 389 个 open issue；可见 Apache-2.0、CI 与测试。90,236 stars 是一次累计快照，不能说明增长、可靠性或生产采用。

## 它如何把 session 变成可召回材料

项目的[架构概览](https://github.com/thedotmack/claude-mem/blob/4702c337d85aa12e8ab7f845264a78885676261f/docs/architecture-overview.md)描述了四层：Hook/CLI 接收 `SessionStart`、`UserPromptSubmit`、`PostToolUse`、`Stop` 和 `SessionEnd`；Bun worker 中的 SessionManager、SDKAgent、PendingMessageStore、SearchManager、ChromaSync 负责异步编排；SQLite 保存 sessions、observations、summaries、prompts、pending messages、feedback；ChromaDB 保存 observation embeddings。MCP 的 `search` 先返回定位线索，再经 timeline 或 observation ID 做渐进披露。

1. 用户 prompt 触发 hook，worker 初始化会话并在 `/api/context/semantic` 请求上下文。
2. 工具调用产生 observation，先进入 pending queue，再交给 SDKAgent 解析。
3. 可解析的结果写入 SQLite；`content_hash` 用于去重。ChromaSync 将 observation 同步为语义索引。
4. 后续会话中，SearchManager 融合 Chroma 和 SQLite 的线索；MCP 再把结果展开为时间线或具体 observation。

这不是“SQLite 加向量库”的简单替代关系：SQLite 是会话事实和管理状态，Chroma 是可滞后的语义通道，MCP 的渐进披露则决定 Agent 实际看见多少。

## 部署实际要求

`package.json` 要求 Node 20.12+ 与 Bun 1+；安装还涉及 worker 进程、SQLite，以及通过 `uv` 启动的 ChromaDB/chroma-mcp 相关 Python 环境。全局 npm 安装只安装 SDK，不会注册 hooks 或 worker；文档要求使用 `npx` installer 或宿主插件安装。这一点使“包已安装”与“会话正在被捕获”成为两件不同的事。

另一个细节是 `contentSessionId` 与 `memorySessionId` 语义不同，错误映射会破坏外键/会话连续性。hooks 被设计为 fail-open：worker 未启动、端口冲突或请求超时时，宿主继续执行。它保护开发工作流，但代价是这一段事件和召回都可能丢失。

## 该架构最脆弱的地方

**异步解析积压。** SDKAgent 输出不可解析时，pending queue 保留以便继续处理；积压会推迟 observation 的物化。

**双存储不同步。** SQLite commit 成功而 ChromaSync 或 MCP 进程失败时，关键词/时间线仍可能可用，语义召回却陈旧或缺项。

**会话身份漂移。** content 与 memory session 映射在重启或转换中失配时，summary/observation 可能归属错误。

这些是从固定源码与架构描述可见的行为边界；未通过故障注入来量化概率或恢复时长。

## 维护与未知

可见提交与贡献者说明项目有活跃维护表面，但 389 个 open issue 不告诉我们其分类、优先级或响应时间。独立组织采用、worker/Chroma 恢复 SLO、跨平台安装成功率和生产数据保留边界均未核实。README 的安装和能力说明不能替代这些证据。

**证据边界。** 结论限定于提交 `4702c33` 的静态源码/文档和 2026-08-10 仓库快照；没有运行 hook、worker、Chroma 或 MCP。
