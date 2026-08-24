# 评价与 Benchmark

Subagent Memory 至少需要分别测量：delegation packet 是否充分、Child 是否泄漏或继承不应看到的状态、共享是否减少重复工作、并发提交是否正确、来源是否保真、删除是否影响后续 Agent，以及最终回答/工具行动是否改善。

Round 02 的 runtime 文档增加了 retention 维度：同一系统还要在 stateless、per-invocation、per-thread 和 cross-session 条件下分别报告结果，避免把 checkpoint 恢复、角色长期学习和团队共享混成一个“有记忆”设置。

GateMem、GroupMemBench、multi-agent task benchmark 和通用 long-memory benchmark 测量的对象不同。比较数字前必须对齐 Agent 拓扑、模型、任务、通信轮次、检索与 token 预算、memory warm-up、工具环境、judge 和失败定义。只报告 recall 或最终 success 无法定位是继承、检索、合并还是行动层产生收益。
