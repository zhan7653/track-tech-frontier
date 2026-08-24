# 同步、冲突与 Belief Commit

## 问题

并行 Subagent 会读到不同版本，并对同一对象提出修改。数据库 last-write-wins 可以避免写入报错，却会隐藏语义冲突；让 LLM 事后总结所有版本又可能丢失因果和少数证据。

## 主要方案族

- **单写者 Parent merge：** Child 只提交候选，Parent 串行合并；简单但吞吐和判断集中。
- **Version check/optimistic concurrency：** 写入携带 base version，陈旧修改被拒绝或重算；无法自动解决语义分歧。
- **Schema-grounded patch：** 只允许满足结构和角色规则的局部 mutation。[PatchBoard](https://arxiv.org/abs/2605.29313)属于这一方向。
- **Conflict set/lattice：** 同时保留 incompatible claims、状态和理由，再由符号规则或模型 reconciliation 更新。[LatticeMind](https://arxiv.org/abs/2608.08236)提供近期实例。
- **Transactional belief commit：** 写入先 stage，经过 evidence、permission 和 action-safety 验证后提交；撤销触发依赖修复。[MemTX](https://arxiv.org/abs/2607.23929)把这一思路形式化。

## 工程关键点

需要区分 record id、logical key、base version、writer agent、task/run、observed time、valid time、evidence、status 和 derived dependencies。冲突处理还要定义 side effect：若错误信念已经触发工具行动，只修改数据库不足以恢复系统。

## 尚未解决

现有论文协议差异很大，且许多结果来自合成状态或单一任务。validator、judge 和 reconciliation model 自身也可能共享同一错误模式。统一 transaction 会提高正确性，却可能把低风险协作变成昂贵控制面。

深入机制见[共享写入何时成为团队信念](synchronization/01-conflict-and-commit.md)。
