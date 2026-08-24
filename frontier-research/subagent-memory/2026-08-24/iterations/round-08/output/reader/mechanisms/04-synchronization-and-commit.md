# 同步、冲突与 Belief Commit

## 问题

并行 Subagent 会读到不同版本，并对同一对象提出修改。数据库 last-write-wins 可以避免写入报错，却会隐藏语义冲突；让 LLM 事后总结所有版本又可能丢失因果和少数证据。

## 主要方案族

### 单写者与应用锁

Child 只提交候选，Parent 串行合并；或用 subject/process lock保护临界区。实现简单，但吞吐、判断和故障恢复集中。

### Version check 与 LWW

写入携带 base version，陈旧修改被拒绝/重算；LWW 选择确定 winner。它们处理 lost update，不自动处理语义分歧。

### Schema-grounded patch 与 conflict surface

PatchBoard 只允许满足 schema/role 的局部 mutation；StateFuse/LatticeMind 保留 incompatible claims、状态和理由，避免早期折叠。

### Transactional belief commit

MemTX 将写入先 stage，经 evidence、permission、dependency 与 action-safety 验证后提交，撤销再触发 repair。

## 数据流、实现与成本

需要区分 record id、logical key、base version、writer agent、task/run、observed time、valid time、evidence、status 和 derived dependencies。冲突处理还要定义 side effect：若错误信念已经触发工具行动，只修改数据库不足以恢复系统。

显式 conflict/transaction 提高可审计性，也增加 validator、storage history、锁/重试、repair 和 latency 成本；低风险 scratch state 未必值得同等控制面。

## 失败、最新研究与尚未解决

现有论文协议差异很大，且许多结果来自合成状态或单一任务。validator、judge 和 reconciliation model 自身也可能共享同一错误模式。统一 transaction 会提高正确性，却可能把低风险协作变成昂贵控制面。

深入机制见[共享写入何时成为团队信念](synchronization/01-conflict-and-commit.md)。
