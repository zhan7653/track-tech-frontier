# Subagent 局部持久化与身份

## 问题

Subagent 结束一次任务后可能被销毁，也可能作为命名角色再次调用。系统需要决定它的 model context、scratch files、checkpoint、长期 memory 和技能分别保留多久。若所有调用都干净启动，Agent 会重复探索；若命名 Agent 无限积累，旧任务、其他用户和错误经验会跨边界污染。

## 方案族一：Stateless tool Subagent

每次调用创建全新上下文，只接收 Parent 的输入并返回结果。LangChain 的 supervisor-style subagents 明确采用这一形状，由 main agent 持有 conversation memory。它避免跨调用污染，适合独立短任务；代价是每次都需重新建立背景，无法形成角色经验。

## 方案族二：Per-invocation durable state

Subagent 在一次调用内部拥有 checkpoint、interrupt 和恢复能力，但调用结束后不保留对下一次调用可见的状态。LangGraph subgraph 的默认 per-invocation 模式属于这一形状：它可以继承 Parent checkpointer 支持 durable execution，却保持不同调用隔离。

## 方案族三：Per-thread named state

同一 thread 中的命名 Subagent 跨多次调用继续 model context 或 graph state。它适合持续研究和多轮 specialist，但同一 subgraph 的并行调用可能写入同一 checkpoint namespace；thread identity 也不一定等于用户、任务或项目 identity。

## 方案族四：Cross-session agent memory

记忆绑定到命名 Agent、project、user 或自定义 layout，跨 conversation 和 runtime 重启存在。Claude Code 为 Subagent 提供 `user`、`project`、`local` 三种目录作用域；OpenAI Sandbox Memory 以 `MemoryLayoutConfig` 和 conversation identifier 组织文件化 memory，并允许 `Memory(generate=None)` 让内部 Agent 读取但不产生新记忆；Deep Agents 可把 `/memories/` 路由到 LangGraph Store，并按 assistant、user 或 organization namespace 持久化。

## 数据与控制流

```text
agent definition / role id
→ invocation and thread identity
→ local context + checkpoint namespace
→ optional persistent memory layout
→ read policy / write policy / consolidation
→ next invocation resolves identity and loads state
→ deletion, reset or project/user boundary cleanup
```

身份解析是关键。如果 agent name 被当作唯一 key，两个用户或项目可能共享不应共享的状态；如果每个 invocation 都生成新 key，又无法复用。实现需要明确 tuple key，例如 tenant/project/agent/thread，并区分 checkpoint、memory artifact 和 team-committed state。

## 成本与失败模式

- 长期局部 memory 减少重复探索，却增加启动注入、搜索、巩固和清理成本；
- Per-thread state 能支持多轮，却可能在同名并行调用中冲突；
- Project memory 便于团队共享，但若进入版本控制，秘密和错误经验会变成仓库资产；
- User/global scope 复用最大，也最容易跨项目泄漏；
- 只读模式降低污染，却需要另一个明确 writer/curator；
- 删除 Agent 定义不一定删除 checkpoint、memory directory、summary、skill 和索引。

## 当前研究议程

公开产品已给出多种 retention knob，但缺少跨 runtime 的统一生命周期模型和实验。需要比较的不是“有无 memory”，而是同一任务在 stateless、per-invocation、per-thread 和 cross-session 条件下的重复探索、污染、并发、恢复与删除。还需固定版本代码检查这些文档语义怎样映射到实际 key、目录、checkpointer 和写入权限。
