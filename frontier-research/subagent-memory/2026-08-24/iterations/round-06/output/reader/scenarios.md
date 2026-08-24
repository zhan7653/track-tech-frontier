# 场景视图

场景不是新的机制分类，而是观察七个分支怎样被组合、替换或省略。

| 场景 | 关键状态边界 | 最突出的机制 | 入口 |
|---|---|---|---|
| Manager–Specialist delegation | Parent 构造任务视图，Specialist 返回候选结论 | 继承、回流、权限 | [Manager–Specialist](scenarios/01-manager-specialist.md) |
| 并行 Coding/Research Subagents | 多个 Child 共享仓库、资料和中间工件 | workspace、冲突、来源、join | [并行工作](scenarios/02-parallel-coding-research.md) |
| 长期运行 Agent Fleet | Agent 跨任务、主机和时间积累经验 | scope、governance、transactive memory | [Agent Fleet](scenarios/03-persistent-fleets.md) |
| 跨工具与跨 runtime 协作 | Claude Code、Codex、MCP/A2A Agent 等交换项目状态 | 协议、身份、能力与可移植性 | [跨 Runtime](scenarios/04-cross-runtime.md) |

这些页面描述约束和组合，不提供配置建议。
