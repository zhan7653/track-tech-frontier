# 共享协作底座

## 问题

自然语言消息适合开放协商，却难以表示当前权威值、部分修改、并发版本和可重放历史。共享协作底座把中间状态外化，使异步 Subagent 能读取已有工作并贡献新工件。

## 主要方案族

### Blackboard

Agent 围绕共同对象读写，适合任务状态和中间结论；控制器需决定触发和冲突。UFO 的固定代码是 in-process object 对照。

### Shared files/workspace

人可读、容易版本控制，适合代码和研究工件；跨主机同步、原子写和细粒度权限较弱。Codex/Deep Agents 展示共享 workspace/backend 的双刃形状。

### Append-only event/episode log

保留原始观察和顺序，便于重放；需要另一个 compiler 得到当前视图。Statewave demo 展示 client integration，但 compiler 在外部。

### Typed state 与 memory service

结构化 key/JSON 支持 schema 和精确更新；独立 service 可跨 runtime、做 scope/search/audit。memX 是最小 current-value 对照，Caura 是多服务治理对照。

Pilot 中 `memX`、`octopus-blackboard`、`shared-agent-memory`、`AMFS` 与 `Statewave` 分别代表这些形状的不同组合。目前它们只是映射候选，后续固定版本分析会确认 README 主张与真实代码组件是否一致。

## 数据流、实现、成本与失败

数据流可为 append→compile→view、get/set→notify、file→reader 或 API→database→search。实现要明确 authoritative object、history、version、delivery 与 recovery。成本从简单共享文件的低门槛，到 service 的数据库、worker、embedding、audit 控制面。主要失败是半成品直接可见、LWW 隐藏语义冲突、通知不持久、全量 prompt 增长和外部 compiler 不可审计。

## 最新研究与尚未解决

共享层的接口往往只定义 get/set/search，而未定义观察、推断、已提交信念和可执行技能的不同语义。没有这个边界，后端即使事务可靠，Agent 层仍可能把半成品当作真相。

深入机制见[黑板、结构化状态、日志与服务](shared-substrates/01-state-surfaces.md)。
