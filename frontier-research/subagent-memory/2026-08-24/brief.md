# Subagent Memory：研究与读者契约

**模式：** comprehensive snapshot  
**研究截止：** 2026-08-24  
**默认读者：** 熟悉 LLM Agent 基本概念、但尚不了解 Subagent Memory 的技术读者  
**默认入口：** `reader/README.md`，主报告为 `reader/overview.md`

## 研究目标

解释父 Agent 创建、委派、监督、回收 Subagent，以及多个 Subagent 并行协作时，状态、经验、知识、观察、计划、技能和结果如何被隔离、继承、共享、检索、合并、验证、回流和遗忘。最终成果必须让读者理解领域整体问题、一般架构、主要机制路线、真实工程实现、最近变化、共识、分歧和未解决问题，而不是阅读一组论文或仓库简介。

## 基准

最低质量基准为 `examples/agent-memory-v10`，固定在 commit `714fd00953cffe185b661143f4a9cfd70a7a1ceb`。基准只规定读者效果、输入广度、分支深度、工程分析和可追溯性的下限，不规定本研究的分支结构和结论。Subagent Memory 的地图必须由本次独立发现语料推导，不复制 Agent Memory 的六分支结构。

## 核心问题

- Parent 应传给 Subagent 什么，如何选择、压缩并保留来源与权限？
- Subagent 记忆由 Agent、任务、项目、团队、租户还是全局控制面拥有？
- 临时 Subagent 结束后，什么应回流，什么应随实例销毁？
- 并行 Subagent 的重复、冲突、过时与相互污染如何检测、表示和处理？
- 共享状态如何同时支持可见性、最小披露、撤销、审计和失败恢复？
- 记忆如何影响后续任务分派、检索、规划、工具调用、技能复用与信用分配？
- 现有 Benchmark 能否把记忆收益与模型、通信、长上下文和额外 token 预算区分开？
- 最近论文、Coding Agent、Research Agent 与多 Agent runtime 正在改变哪一层机制？

## 纳入与排除

纳入 hierarchical agent memory、multi-agent shared memory、handoff state、blackboard/working artifacts、collective or organizational memory、memory synchronization、provenance-aware sharing、experience/trajectory/skill transfer，以及 Coding/Research/long-running Agent 中承担持久状态职责的 Subagent 机制。

普通消息传递、workflow state、checkpoint、shared workspace、long context、RAG、event log、task queue 和一般 Agent Memory 仅在它们实际承担跨 Agent 状态生命周期职责时纳入。相邻技术只解释边界。报告不提供选型建议、推荐架构、部署路径或实现清单。

## 证据与写作原则

输入先广后深，分别保留 discovered、mapped 与 deep-verified。关键数字、版本、安全、采用和重要比较需要直接证据；普通架构分析以保守措辞、逻辑完整和可检查来源为准，避免让审计工作压倒研究与写作。GitHub 与论文同等重要，项目深潜以固定 commit/release 的实际组件和数据流为中心。
