# Subagent 局部持久化：Invocation、Thread 与命名身份

## 问题与状态对象

一个 Subagent 可同时拥有 model context、checkpoint、scratch files、memory files、skills 和工具 side effects。它们的 key 与保留期可能不同。最常见的错误是把 thread checkpoint 当成长久经验，或把全局 agent name 当作安全的唯一 namespace。

可将状态身份表示为：

```text
(tenant, user, project, agent_definition, thread, invocation, workspace_revision)
```

不同 runtime 只使用其中一部分。使用的维度越少，复用越容易，跨边界碰撞也越危险。

## 方案族及内部流程

### Stateless tool Subagent

每次调用创建新消息上下文，Parent 负责全部 conversation memory。Child 只接受当前 input，返回一次 result。LangChain supervisor-style subagent 文档属于此形状。

```text
call input → fresh child context → tools → one result → destroy context
```

适合独立查找和验证。若背景构造昂贵，重复调用会重复读文件、搜索和推理；任何“学到的经验”必须显式回流 Parent/Team，否则随调用消失。

### Per-invocation durable execution

Child 在一次调用内有 checkpoint，可 interrupt、恢复和容错；调用结束后，下次同名 Child 仍从空状态开始。LangGraph subgraph 的默认 per-invocation persistence 接近这一语义：它能继承 Parent checkpointer 以支持 durable execution，但 invocation namespace 保持隔离。

Checkpoint 保存的是运行状态，而不是自动整理后的长期知识。它适合失败恢复，却会把半完成 tool result 和控制状态一起保留；恢复时必须检查外部 side effect 是否已发生。

### Per-thread named state

同一 thread 的多次调用共享 Child graph/model state：

```text
(thread_id, subgraph_namespace)
→ load checkpoint
→ append new call state
→ save checkpoint
```

它支持持续 Specialist，但同一 subgraph 在一个 node 中并行调用可能写同一 namespace。thread 也未必代表一个用户或项目；若 thread 被复用，局部记忆会跨任务漂移。

### Cross-session named memory

记忆绑定 agent/project/user/layout，跨 thread 和进程存在。Claude Code 文档暴露 `user`、`project`、`local` 三种 Subagent memory scope；Deep Agents 可把 `/memories/` 路由到 Store backend；OpenAI Sandbox Memory 以 layout 与 conversation identity 管理 memory artifacts，而不是自动按 agent name 隔离。

典型流程是：启动加载摘要或 memory file → 运行中按需读取详细记录 → 运行后写候选/巩固 → 下一次按 namespace 解析并加载。`read-only` 或 `generate=None` 模式把读者与 writer 分开，避免一次性 checker 向长期层写入低价值记录。

### Background consolidation

运行不直接修改稳定记忆，而是把 transcript/trajectory 放入 queue，由后台 curator 或 model 批量巩固。这样减少在线延迟，也能集中去重；代价是 write-to-visible 延迟、并发 consolidation、失败重试和 source rollout 与 consolidated memory 的双重生命周期。

## 生命周期比较

| 模式 | 保存什么 | 跨调用 | 并行风险 | 删除对象 |
|---|---|---:|---|---|
| Stateless | 无 Child 状态 | 否 | 低 | 无/仅外部工件 |
| Per-invocation | checkpoint、scratch | 仅恢复本次 | side-effect replay | invocation state |
| Per-thread | graph/model context | 同 thread | namespace collision | thread checkpoints |
| Cross-session | memory/skills/files | 是 | scope collision、stale | files、summary、index、skills |
| Background consolidation | raw rollout + stable memory | 是 | queue/lease/concurrent merge | source与派生层 |

## 成本与失败模式

- 名称稳定不代表身份安全：同名 Agent 可服务不同用户/项目；
- 删除 Agent 定义不一定清除其 memory directory、checkpoint 和 skills；
- 项目级 memory 可版本控制，但也可能把秘密提交进仓库；
- 全局 user scope 会把项目特定策略迁移到无关环境；
- 读写同一文件的并行 Agent 需要锁、CAS、Git merge 或单 writer；
- checkpoint 恢复若不记录 tool side effect，会重复执行不可逆动作。

## 当前研究在改变什么

产品已提供 retention knob，但公开评测仍常只比较“memory on/off”。真正缺少的是以同一任务比较 stateless、per-invocation、per-thread 与 cross-session：测重复探索、污染、namespace 冲突、恢复正确性和彻底删除。固定版本工程报告还要确认文档中的 scope 最终映射到哪个数据库 key、目录和 writer policy。


## 证据账本绑定

Subagent 的持久身份在真实实现中分别绑定 layout、thread/namespace、team participant、shared object 或 root/child role，而不是统一绑定“Agent 名称”；checkpoint 恢复、角色长期学习和团队共享必须分别配置。
<!-- synthesis:SY-C08 claims:R5-C002,R5-C004,R5-C005,R5-C009,R5-C011 clusters:SM-C08 -->
