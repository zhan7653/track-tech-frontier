# 从这里开始读 Subagent Memory

Subagent Memory 研究的不是“多个 Agent 共用一个向量数据库”这么单一的问题。它研究的是：一个 Agent 把工作交给另一个 Agent 时，什么状态应跨越边界；工作完成后，哪些局部结果可以成为 Parent、团队或未来 Agent 的可靠记忆。

建议阅读路径：

- **5 分钟：** [领域总览](overview.md)，理解两个关键边界与八个机制分支。
- **15 分钟：** 总览 + [一般架构](architecture.md)，跟随一次 spawn、执行、提交和未来复用的数据流。
- **30 分钟：** 再读[方案空间](solution-landscape.md)和[近期变化](trends.md)。
- **专题：** 进入[机制分支](mechanisms/README.md)或[场景视图](scenarios.md)。
- **工程：** 从[GitHub 雷达](github-radar.md)进入固定版本项目报告；Round 01 仅完成候选筛选，源码深潜将在后续轮次加入。
- **证据边界：** [方法与范围](method-and-scope.md)与[审计入口](../audit/README.md)。

当前是广度扩展后的完整阶段版，不是最终结论。它已经给出可独立阅读的领域解释，并新增 Subagent 局部持久化分支；分支内部算法、项目源码分析、Benchmark 对齐和负面证据仍会在后续轮次显著扩充。
