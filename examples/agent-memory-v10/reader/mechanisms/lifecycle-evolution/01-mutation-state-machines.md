# 生命周期状态机：更新、合并、遗忘和恢复不是 CRUD 同义词

Memory 一旦可修改，核心问题就从“能否存取”转为“状态怎样合法变化”。`update()` 可能表示补充字段、替代旧事实、解决冲突或重写摘要；`delete()` 可能只是不再召回，也可能要求物理清除原文、索引、备份和派生技能。把它们都压成 CRUD，会隐藏行为语义和恢复边界。

本篇把生命周期操作写成状态机，逐一解释版本修订、巩固、衰减、逻辑遗忘、物理清除、修复与 learned control。

## 1. 一个对象的可观察状态

```text
captured
  → proposed
  → quarantined | rejected | admitted
  → active revision
  → conflicted | superseded | consolidated
  → hidden/released | purged
  → restored/rebuilt (when policy allows)
```

不同对象可以有不同子状态。事件证据常 append 后归档；事实有 current/history/conflict；profile 字段可修订；procedure 还需要 validated/deprecated；共享对象有 private/shared/revoked。状态机的作用是让每个 operation 有前置条件、actor、reason、effect 和 receipt。

## 2. Amend、merge、supersede 与 conflict resolution

### 2.1 Amend

对同一对象补充兼容字段，例如给项目决策增加 source link。生成新 revision 或在可审计事务中追加字段，不改变其核心断言。

### 2.2 Merge / consolidate

多个对象被聚合为较少对象。算法可能按语义相似、共同主体、时间窗口、topic cluster 或模型判断选组，再生成 summary/profile/procedure。应保留 predecessor links 与 source coverage；否则 merge 后无法知道哪些细节被丢弃。

### 2.3 Supersede

新 revision 明确取代旧 revision。current pointer 改变，旧版保留在 history；valid time 决定新值何时成立。supersede 不等于 purge，因为历史查询和审计仍可能需要旧版。

### 2.4 Conflict

两个来源不相容且 authority/时间不足以自动选择时，状态进入 unresolved conflict。读取可以返回冲突和来源，或在高风险场景 abstain；静默选择流畅版本会制造虚假 certainty。

## 3. 巩固算法：从多个事件形成更稳定状态

### 3.1 时间/容量触发

按 turn 数、token、时间或 store size 触发批量总结。简单可控，但不理解 query horizon；固定阈值在不同任务上可能过早或过晚。

### 3.2 相似聚类

embedding/关键词将相关事件聚类，再生成 cluster summary 或 canonical fact。聚类提高主题覆盖，错误 cluster 会把不同主体/条件混合；更新后还需决定增量重算还是全量巩固。

### 3.3 反思/规律提炼

从多次经历提取高层 pattern、belief 或 procedure。Generative Agents 的 reflection、MemoryBank 的 assessment、experience-to-skill 路线都使用类似思想。它提高抽象层级，也最容易把偶然相关固化为规则。

### 3.4 Budget-aware consolidation

将 retain、summarize、merge、drop 视为在 token/storage/latency 预算下的 operator selection。[Retain or Consolidate?](https://arxiv.org/abs/2607.17545)强调 retention 保存细节，consolidation 提高紧预算下覆盖但可能丢 query-critical evidence；最佳操作随预算变化。

## 4. TTL、衰减和访问频率到底改变什么

### 4.1 TTL

到期后对象不可见或进入归档。TTL 是确定性 policy，适合临时状态和法律/业务保留期；它不判断内容价值，也不自动清理派生物。

### 4.2 时间衰减

在 ranking 中降低旧对象分数，典型形状是指数/分段 decay。对象仍存在，只是较难被取回。它适合 preference/episode 的 recency signal，却可能让低频但重要的规则消失。

### 4.3 使用强化

被成功使用的对象提高 salience，长期未用降低。问题是检索与使用会产生反馈回路：早期偶然命中的对象更常被展示，又因此更“重要”；错误状态也可能自我强化。

### 4.4 容量淘汰

LRU/LFU/utility score 在空间预算下删除/归档对象。它来自 cache 思维，但 Memory 不是纯缓存：少用不表示可丢，删除还可能影响历史、合规和程序依赖。

## 5. Forget、release、revoke 与 purge

| 操作 | 外部含义 | 仍可保留什么 | 典型用途 |
|---|---|---|---|
| hide / forget | 默认检索不再返回 | canonical/history 仍在 | 降噪、策略不可见 |
| release | 从 active working/prompt 层释放 | durable store 仍在 | context/tier 管理 |
| revoke | 某 principal/purpose 不再有权使用 | 对象可对其他范围存在 | 权限/共享撤销 |
| supersede | 新版成为 current | 旧版 history 可查询 | 事实修订 |
| purge | 物理删除受管 payload/投影 | 最小删除 receipt/tombstone | 隐私/合规清除 |

[ForgetEval / Control-Plane Placement](https://arxiv.org/abs/2606.15903)将 recall 与 supersede、release、purge 等 mutation-plane operation 分开，指出“记不起来”并不能证明系统实现了遗忘语义。

## 6. Dependency repair：更新一条对象为何会波及整个系统

对象可能派生出 summary、profile、embedding、graph edge、procedure、compiled prompt 和外部 action。一次 supersede/revoke 后，需要沿 lineage 判断：

```text
source event e1
  → fact f1
  → profile field p1
  → summary s1
  → procedure k1
```

若 f1 被纠正，p1/s1 可能需要重算，k1 可能需要降级或弃用。association edge 只表示相关，不应触发 repair；extension/dependency edge 才传播 invalidation。GEM/MemState 的这一差别指出 lifecycle 需要 typed derivation，而不只是知识图关系。

## 7. Journal、snapshot 与 recovery

事务式生命周期通常包含：

1. append mutation intent/receipt；
2. 验证前置 revision、source 与 policy；
3. commit canonical new revision；
4. enqueue projection updates；
5. checkpoint/snapshot；
6. 失败时 replay、rollback 或 restore；
7. 验证 current/history/index/action view。

[MemTxn](https://arxiv.org/abs/2607.27834)将 source-supported validation、temporal resolver 与 durable snapshot journal放在 answer model 外，代表“完整状态恢复”方向。它仍需要跨后端、并发和崩溃实验来证明通用性。

## 8. 学习型生命周期控制

[MemCon](https://arxiv.org/abs/2607.13591)等工作把 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 设为 policy actions。策略根据任务、memory state、budget 与 outcome 选择。相对固定规则，它可能适应 query distribution；风险是 reward delay、policy drift 和不可逆 mutation。

当前较受控的一类研究形态把 learned controller 限定为 operation proposer，再由显式 primitive 检查 source、scope、version、permission、budget 和 rollback。它把“模型生成 free-form 指令”与“删除或改变共享权限”分成两道状态转换；但这种分层的实际安全收益仍缺跨后端实验。

## 9. 生命周期操作的可观测性

能够区分 lifecycle 故障的实现通常会暴露 object/revision、actor、operation、reason、source set、policy/model version、pre/post state hash、derived targets、projection status、cost 与 rollback point。字段缺失时，“策略选择错误”“commit 部分失败”“投影 stale”和“Agent 继续使用旧状态”会在观测上混成同一种失败。

继续阅读[生命周期系统 walkthrough](02-system-walkthroughs.md)和[删除、修复与研究前沿](03-deletion-repair-and-frontier.md)。
