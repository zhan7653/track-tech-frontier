# Round 02 技术地图变化

新增 `SM-C08 Subagent-Local Persistence and Identity`：研究同一个命名 Subagent 在 invocation、thread、session、project、user 与 runtime restart 之间保留什么状态。

该分支由 Claude Code、LangGraph、OpenAI Agents SDK Sandbox Memory、Deep Agents 和 AutoGen 的公开文档触发；详细推导见 [`work/round-02/map-delta.md`](../../work/round-02/map-delta.md)。原七分支未被删除，但 Parent-to-child 继承与 Child 自身 retention 的边界被明确拆开。
