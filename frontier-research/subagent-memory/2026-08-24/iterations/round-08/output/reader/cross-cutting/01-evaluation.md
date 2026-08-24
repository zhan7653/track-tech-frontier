# 评价与 Benchmark：不能再用一个“Memory 分数”概括

Subagent Memory 的因果链至少经过委派视图、Child 局部执行、共享/回流、检索和最终行动。只测最终 success，会把输入更完整、模型调用更多、检索更好、冲突更少和工具更强混成一个数字；只测 recall，则根本看不到越权、错误 commit 和行动后果。

## 要分开测的八个对象

| 对象 | 最小实验问题 | 典型指标 | 常见混淆 |
|---|---|---|---|
| 委派充分性 | Child 是否拿到完成任务所需状态？ | constraint coverage、missing dependency、clarification rate | 更长 prompt 被当成更好 memory |
| 委派隔离 | Child 是否看到不应继承的状态？ | secret/injection leakage、capability overreach | 只检查返回文本，不看内部 channel |
| 局部持久化 | 调用中断、thread 复用和跨 session 是否按预期保留？ | recovery、cross-task contamination、cleanup | checkpoint 与长期学习混为一谈 |
| 共享收益 | Sibling 是否减少重复探索并提高任务结果？ | duplicate work、wall time、total tokens、success | 并行计算增量被记在 memory 头上 |
| 提交正确性 | 候选写入是否正确接受、拒绝、冲突或撤销？ | false commit、conflict recall、repair completeness | LWW 的确定性被当成事实正确性 |
| 回流保真 | Parent 是否保留证据、unknowns、失败和 dissent？ | lineage completeness、unsupported compression | final answer 流畅度代替来源保真 |
| 经验迁移 | 旧轨迹/技能是否帮助当前 consumer？ | marginal utility、negative transfer、staleness | 相似度命中等同于可复用性 |
| 行动安全 | 召回内容能否在当前权限和风险下驱动工具？ | unsafe action、false abstention、revoke response | 正确回答被外推为安全行动 |

## 当前协议实际测了什么

现有深读材料没有一个覆盖全链：GateMem 测 requester-specific utility、权限与主动遗忘；AgentLeak 观察 coordinator-worker 的七条泄漏 channel；StateFuse 测 conflict visibility 和 correction contract；PatchBoard 测 schema/patch kernel 与 fault injection；MAP-Graph 把 lineage 接到 simulated action gate；MATM 测 population trajectory 对 consumer 的边际效用；GroupMemBench 测多人对话记忆；Bad Memory 测已经存在于 workspace memory 的 payload 能否跨 session 影响 coding agent。

这些协议可以互补，但不能合并成一个排行榜。StateFuse 与 PatchBoard 的 state object 不同；GateMem 的删除是行为不可恢复，不等于物理清除；MATM 的成功来自固定 population/split，不回答恶意 producer；Bad Memory 从 payload 已落盘开始，不估计真实写入发生率。

更细的协议和边界见 [Benchmark 协议地图](benchmark-protocols.md)。

## Runtime retention 对照是目前明显空白

真实 runtime 已经提供多种 retention：stateless task child、per-invocation checkpoint、per-thread subgraph、project/user memory、sandbox layout 和 root-only consolidation。但选中论文几乎没有在同一个模型、任务和工具环境中，系统比较这些生命周期。

一个直接的实验矩阵应固定 task/model/tools，只改变：

```text
history: full / filtered / none
child retention: none / invocation / thread / project
workspace: shared / snapshot / isolated
return: final text / structured envelope / patch+evidence
commit: direct / parent review / deterministic gate / transaction
```

每个 cell 同时报告 success、total tokens、wall time、重复工作、泄漏、错误 commit、恢复与清理。否则“有长期 Child memory 更好”仍是没有隔离计算预算和污染成本的概括。

## 可比性最低要求

任何可比较结果至少应记录 topology/identity/scope、数据与版本、模型和 decoding、delegation packet、memory warm-up、写入/合并/检索预算、工具环境、side-effect model、judge、重复运行、权限/删除条件以及代码 commit。

尤其要报告总模型调用和总 token。多 Agent memory 方法经常附加 critic、summary、retriever、reranker 或 compiler；若只展示最终准确率而不计额外推理，无法判断收益来自记忆结构还是额外计算。

## 当前可下的结论

现有 Benchmark 分别测 conflict visibility、validated patch、访问/遗忘、lineage action、trajectory transfer 或多人问答，尚不存在一个可把 Subagent Memory 整体排成单一榜单的共同协议。

这不是说现有结果无效，而是说每个数字必须留在自己的协议边界内。下一步最有价值的不是再造一个综合平均分，而是提供可复用的 runtime retention × governance × action 实验矩阵和固定资源预算。
