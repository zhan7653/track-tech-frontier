# 共享协作底座

## 问题

自然语言消息适合开放协商，却难以表示当前权威值、部分修改、并发版本和可重放历史。共享协作底座把中间状态外化，使异步 Subagent 能读取已有工作并贡献新工件。

## 主要方案族

- **Blackboard：** Agent 围绕共同对象读写，适合任务状态和中间结论；控制器需决定触发和冲突。
- **Shared files/workspace：** 人可读、容易版本控制，适合代码和研究工件；跨主机同步与细粒度权限较弱。
- **Append-only event/episode log：** 保留原始观察和顺序，便于重放；需要另一个编译层得到当前视图。
- **Typed shared state：** 结构化 key、对象或 JSON document 支持 schema 与精确更新；开放任务可能受 schema 限制。
- **Memory service/pub-sub：** 通过 API、MCP 或通知连接多个 runtime；需要能力协商、身份和可靠交付。

Pilot 中 `memX`、`octopus-blackboard`、`shared-agent-memory`、`AMFS` 与 `Statewave` 分别代表这些形状的不同组合。目前它们只是映射候选，后续固定版本分析会确认 README 主张与真实代码组件是否一致。

## 尚未解决

共享层的接口往往只定义 get/set/search，而未定义观察、推断、已提交信念和可执行技能的不同语义。没有这个边界，后端即使事务可靠，Agent 层仍可能把半成品当作真相。
