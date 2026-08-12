# 删除、依赖修复与研究前沿：Memory 生命周期最难的最后一公里

Memory 研究正在从“能更新一条记录”走向“能证明整个状态轨迹已改变”。困难在于对象被摘要、索引、图、cache、profile 和 skill 重复派生，并曾经影响过行动。数据库 current view 正确只是第一步。

## 1. 删除的五个层次

1. **retrieval suppression**：默认查询不返回；
2. **logical tombstone/revoke**：对象被标记不可用，history仍在；
3. **projection removal**：FTS/vector/graph/cache失效；
4. **physical purge**：受管 payload、索引和允许清除的历史删除；
5. **behavioral repair**：Agent 后续行动不再依赖旧对象，已产生副作用被补偿。

不同场景需要不同层次。降噪可能只需 suppression；撤销共享权限需要 revoke；隐私请求可能要求 purge；错误部署规则还需要 behavioral repair。报告“delete API succeeded”没有说明完成哪一层。

## 2. 派生物图如何支持 repair

每个 derived object应记录 lineage：

```text
event → fact → profile/summary → embedding/graph → compiled context → action
                  └──────────→ procedure/skill
```

revision/revoke 发生后，系统沿 dependency edge产生 invalidation tasks。可重建投影直接删除/重算；summary/profile重新生成；procedure降级为 pending revalidation；历史 action只记录影响并触发补偿。association edge不应自动传播，避免把所有相关内容一起删除。

当前多数系统没有完整 lineage，修复只能靠重新索引整个库或人工排查。GEM/MemState 所提 extension edge、transaction/journal 和 hashed receipt 是朝这一方向的机制信号。

一个可执行 repair planner 可以先计算闭包，再按对象类型调度：

```text
affected = transitive_closure(changed_revision, edge_type ∈ DERIVES_FROM)

for object in topological_order(affected):
    if object.rebuildable:
        invalidate(object)
        enqueue_rebuild(object, target_revision)
    elif object.external_effect:
        create_compensation_case(object)
    else:
        mark_needs_review(object)
```

这里必须使用 typed dependency edge，而不是所有 graph neighbor。`MENTIONS`、`SIMILAR_TO` 或 entity association 不表示派生依赖；沿它们传播会造成过度删除。循环依赖需要先压缩 strongly connected component，再把整组标为 invalid 或重算。

repair 完成也不是队列清空：每个投影要回报 target revision、水位和验证 hash。读取层在 watermark 未追上时，应阻断高风险查询或显式标 stale，而不是继续返回旧结果。

## 3. STALE：状态已改，行为为何仍旧

[STALE](https://arxiv.org/abs/2605.06527)研究 Agent 是否知道其记忆已不再有效。它代表的重要问题是 capability gap：store update、retrieval visibility、context interpretation 与 action policy是四个阶段；任一阶段仍可使 Agent遵循旧前提。

一次 correction benchmark应记录：

- old/new revision是否正确；
- retriever是否仍返回旧值；
- context是否明确冲突/替代；
- model是否引用新值；
- tool action是否停止旧行为；
- downstream procedure/cache是否修复。

只测回答“知道新事实吗”不足以证明行为已更新。

STALE 在 400 个冲突场景、1,200 个查询的作者协议中，报告最佳被测模型总体准确率为 55.2%。该数字受模型与协议限制，却足以否定“把最新事实写入 store 后，Agent 会自然放弃旧策略”的强假设。行为修复必须将 revision 与 plan/tool premise 连接，而不能只重新跑 retrieval QA。

## 4. Consolidation 的稳定性—可塑性矛盾

巩固减少噪声与 token，却会让状态更难局部修订；保持全部原始事件可塑性高，却增加候选和成本。预算、query horizon、对象风险和修复成本共同决定 operator。

近一年的工作开始将 retain/consolidate/forget建模为条件或 learned policy。尚缺的是长 horizon 对照：同一 stream 上，未来 query分布变化、错误更正、隐私删除和成本累积同时发生时，哪种策略净收益更高。

预算约束下可把 operator 看作：

```text
o* = argmax_o E[future utility | history, workload, o]
     - λ·token_cost - μ·latency - ν·information_loss
     - ρ·repair_cost - κ·irreversibility
```

`retain` 保存细节但增加读取负担；`merge/abstract/rewrite` 提高单位 token 覆盖却可能删除 query-critical span；`forget` 降低增长和隐私暴露，却增加 future false-forget。现有 budgeted-consolidation 研究支持“最佳 operator 随预算而变”，不支持固定排序。

## 5. Learned controller 的安全边界

控制器可根据 state/budget/outcome选择 operation，但三类动作风险不同：

- reversible：retrieve、re-rank、临时 context injection；
- recoverable：consolidate/supersede，有 revision/snapshot可回退；
- destructive/external：purge、share、procedure promotion、tool action。

训练或在线探索应对风险分级，破坏性动作需要更强 policy/authorization/human gate。reward不能只看当前 task success，否则策略可能通过少写、过度删除或记住投机规则获得短期高分。

MemCon 将 retrieve、plan injection、re-retrieve、consolidate、forget 和 no-op 建模为在线 action；作者描述的实现使用 contextual bandit、UCB 和二值任务反馈。它是“operation selection”路线的清晰实例，却没有独立证明跨 backend 安全泛化。较可控的运行形态会让 learned controller 只产生 proposal：

```text
policy proposal
  → action mask by risk/state
  → deterministic precondition/version check
  → shadow or canary
  → commit primitive
  → outcome + rollback receipt
```

retrieve/no-op 可在线探索；supersede/consolidate 只有在 revision/snapshot 可回退时进入受控 canary；purge/share/action 等破坏性操作不应由稀疏 reward 自主探索。

## 6. 安全攻击为什么开始瞄准生命周期

攻击者可以让恶意内容通过重复检索、反思或成功任务获得更高 salience，再被巩固为 profile/rule/skill。删除原始攻击文本时，派生 summary/skill可能仍在。因而防御需要 admission、promotion、lineage、revoke、action authorization与incident repair，而不是单一 detector。

[PoisonedEvolution](https://arxiv.org/html/2608.05563v2)展示 trajectory poisoning 进入自演化技能的路径；MemSecBench 的 Write–Execute–Forget 视角也把忘记纳入安全链。作者协议不等于现实攻击概率，但改变了生命周期应测的边界。

Sleeper-memory 工作进一步把成功拆为 write、later retrieval 和 later action；这使 incident response 不能停在删除攻击原文。系统还要反向枚举被它影响的 summary/profile/skill、缓存 prompt、已安排 action 和共享副本，再验证修复后行为。来源签名或 predecessor hash 只能证明 transition 来自谁、是否被改写，不能证明内容真实或安全。

## 7. 当前缺失的工程与实验

### 7.1 End-to-end deletion harness

需要可注入对象及其 summary/vector/graph/cache/skill，再执行 revoke/purge/restore，验证各层与未来行动。当前公开工具多只覆盖 store API。

### 7.2 Cross-backend mutation contract

同一 supersede/forget 在 SQLite、vector provider、graph、managed service中是否具有相同 current/history语义？缺少 conformance tests。

### 7.3 Concurrent writers and late evidence

多 Agent同时修订、离线数据迟到和共享撤销同时发生时，last-write-wins不足。需要版本/authority/conflict benchmark。

### 7.4 Full lifecycle cost

形成、巩固、修复、重建、删除、备份与人工 review应与下游收益共同计量。当前多数结果只覆盖 query token或静态任务。

### 7.5 Crash 与并发写

单机 happy path 不覆盖：truth commit 后索引更新前崩溃、两个 writer 从同一 parent 生成 revision、late evidence 覆盖较新 valid-time、restore 后 queue 重放重复、旧进程写回 stale image。最低 fault matrix 应在 transaction boundary 的每个阶段注入中断，并验证 idempotency、compare-and-swap/version precondition、outbox ordering 与 projection watermark。

### 7.6 Delete 的可验证收据

删除收据应列出 authoritative payload、current/history revision、FTS/vector/graph/cache、summary/profile/skill、backup、审计保留例外和 external effect。每项状态是 removed、cryptographically-erased、revoked、retained-by-policy 或 unknown，并记录验证时间。没有清单时，“已删除”只是接口响应。

## 8. 最新研究议程

| 方向 | 当前机制 | 下一步决定性问题 |
|---|---|---|
| explicit mutation operators | supersede/release/purge/restore分离 | 跨实现语义是否一致 |
| transaction & snapshot | source validation + journal | 并发/崩溃/多后端完整恢复 |
| dependency-aware repair | typed lineage/extension edge | 派生 summary/skill能否精确重算 |
| adaptive operation policy | budget/任务驱动的 learned control | 长期净收益、policy drift、安全约束 |
| verifiable forgetting | tombstone、purge、key deletion | backup/cache/action 层是否真正闭环 |
| behavioral correction | revision→retrieval→action trace | 更新是否改变真实工具行为 |

另一个重要趋势是把 lifecycle placement 作为变量。ForgetEval/Control-Plane Placement 区分 supersede、release、purge，并研究 mutation hook 放在 store、retriever、context compiler 还是 agent loop；不同位置看到的状态和能执行的修复不同。它的作者结果依赖模型、backend、subset 和 LLM quality，当前尚不能给出通用 placement 排名。

MemTxn 则把 source-supported admission、temporal resolver 和 durable snapshot journal 放到 answer model 外，代表 transaction boundary 外置的路线。真正决定性证据仍是多 writer、崩溃、异构索引和 restore 的运行结果，而不是机制图本身。

## 9. 当前成熟度判断

TTL、append history、DB transaction、snapshot、reindex等原语成熟；显式 revision、conflict与multi-index repair处于中等工程成熟度；跨后端 transaction、完整派生删除、learned lifecycle control和behavioral repair仍早期。没有证据支持任一 operator普遍最好，也没有现有开源系统在本次检查中证明完整链。

回到短入口：[生命周期与演化](../04-lifecycle-and-evolution.md)。写入形成见[写入专题](../writing-formation/01-capture-extraction-and-consolidation.md)，安全横切见[安全、隐私与治理](../../cross-cutting/02-security-privacy-governance.md)。

## 10. 能回答问题的共同生命周期实验

同一对象流应包含：初始事实、重复使用、相互矛盾更新、late evidence、容量压力、共享撤销、隐私 purge、索引失败和进程崩溃。分别替换 deterministic rule、budget-aware operator 和 learned controller，固定 backend、模型、检索、预算和 fault schedule。

输出不应是一个总分，而是：

- admission/update/current/history/conflict correctness；
- source-span retention 与 false merge/false forget；
- stale retrieval 和 stale action；
- derived-delete coverage、backup residue 和 repair latency；
- crash recovery、duplicate replay 和 writer conflict；
- write/manage/read/action 的模型调用、token、P50/P95、存储与人工成本；
- poisoning inclusion、retrieval、action 和 post-repair recurrence。

只有这种跨状态与故障的长期协议，才能判断“会演化”究竟表示正确维护状态，还是只是频繁重写文本。
