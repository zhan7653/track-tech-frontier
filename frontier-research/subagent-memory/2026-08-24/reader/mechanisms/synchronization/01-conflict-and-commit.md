# 同步、冲突与 Commit：共享写入何时成为团队信念

## 问题与状态转换

多 Agent 系统至少要区分四件事：Agent 提交了一个 observation；系统保存了这次写入；团队把它接受为当前 belief；某个高风险 action 被允许依赖它。把四者压成一次 `put()`，会让半成品、旧值和污染直接驱动行动。

## 方案族及内部流程

### Single-writer Parent 与顺序 merge

所有 Child 只返回候选，Parent 串行决定当前状态。它把并发降维成一个队列，容易解释，也能用 Parent 的全局目标裁决。代价是吞吐、单点判断和 Parent context 膨胀；若 Parent 只接收短摘要，仍可能看不到冲突证据。

### LWW、CAS 与 versioned record

Last-write-wins 选择 timestamp 或 version 最大值；compare-and-swap 要求 writer 声明 base revision。它们能检测陈旧写，但不知道两个内容是否语义冲突。更完整的 record 至少包含 logical key、value、writer、base revision、valid time、observed time、evidence 和 status。

### CRDT/OpSet + 冲突保留

[StateFuse](https://arxiv.org/abs/2607.05844)用 immutable operations 做 CRDT/OpSet merge；public projection 显式暴露 conflict object，resolver 只能选择或 abstain，不能改写 replicated history。correction 可用精确 `claim_id`，也可用跨 replica 的 semantic `claim_ref`。

它最重要的反证是：在 282-question conflict slice 中，StateFuse 与强 conflict-preserving flat baseline 的 top-line accuracy 相同。价值不在普遍准确率，而在 conflict visibility、correction handle 和 auditable projection。CRDT 解决 convergence，不自动解决 truth、authorization 或 compaction。

### Status lattice + selective reconciliation

[LatticeMind](https://arxiv.org/abs/2608.08236)将 item 表示为 `(key, content, evidence, time, status)`，status 包括 PROPOSED、CONFIRMED、CONTESTED、SUPERSEDED。cheap symbolic checker 处理 dependency cycle、resource constraint 等机械冲突；未解决的 semantic case 才调用 LLM reconciler。

它区分 credibility conflict（谁更可信）和 coordination conflict（多个局部有效方案不能同时执行）。论文主要验证前者；后者只有 conservative override，不能把强 ConflictBank 数字外推到所有协作冲突。

### Schema-grounded transactional patch

[PatchBoard](https://arxiv.org/abs/2605.29313)的 worker 不直接写状态，而是针对 bounded view 提交 JSON Patch。kernel 在临时副本上检查 operation subset、role write contract、schema 和 invariant，通过后原子推进 committed state；接受和拒绝都进入 transaction log。

这条路线适合已知状态对象。它能拒绝坏 path、类型和越权字段，但 schema-valid false claim 仍需要 evidence layer。Architect 自动生成 schema 带来适应性，也增加另一个模型错误点。

### Staged belief transaction + action gate + repair

[MemTX](https://arxiv.org/abs/2607.23929)把 write 放入 snapshot-isolated transaction，按 evidence、validity、semantic conflict、dependency stability 顺序 admission。其他 Agent 在 committed-read tier 之前看不到 tentative record。不可逆工具调用还受 action gate：Agent 自己的 plan 未提交、或 external-action snapshot 没有 action-safe support 时拒绝。

撤销不是把 record 标 stale：系统沿 derivation DAG 执行 typed cascading repair，并区分可逆/不可逆 side effect。作者 90-case main、56-case hardened suite 和五 backbone 结果支持该协议内判断；其结论仍指出 transcription/retry 跨 commit 的步骤未被保护。

## 方案比较

| 路线 | 保存冲突 | 并发保证 | 行动控制 | 修复 | 主要未知 |
|---|---:|---|---|---|---|
| Parent merge | 取决于 Parent | 串行 | Parent 决定 | 手工 | 单点误判 |
| LWW/CAS | 常否 | version check | 无 | 重写 | 语义冲突 |
| CRDT/OpSet | 是 | convergence | projection policy | explicit retract | truth/permission |
| Status lattice | 是 | 状态机 | 可接 gate | supersede | coordination evidence |
| Validated patch | log 保留 | transaction | invariant | rollback/replay | false claim |
| Belief transaction | 是 | snapshot isolation | maturity gate | cascading repair | 真实 side effect |

## 并发异常与工程代价

即使数据库事务正确，Agent 流程仍会出现 dirty read、lost update、write skew、duplicate action、stale summary 和 pipeline ordering。[Governed Shared Memory](https://arxiv.org/abs/2606.24535)报告 pre-commit near-duplicate gate 会阻止后置 contradiction detector 看到第二条写入，说明多个“安全组件”也会互相抵消。

显式 commit 增加 state machine、dependency graph、validator、storage 和 latency；对低风险笔记可能过重。关键不是所有写入都采用最强事务，而是风险 tier 与状态语义要可观察，不能由模型临时猜测。

## 当前研究在改变什么

前沿正把“冲突解决”从最终 answer aggregation 前移到 persistent state update，并把 action safety 与 repair 纳入同一协议。仍缺真实数据库/队列/多进程 fault injection、跨工具 side-effect compensation、validator compromise 和长期 compaction 后 invariant 的公开复现。
