# 从这里开始读 Subagent Memory

Subagent Memory 研究的不是“多个 Agent 共用一个向量数据库”这么单一的问题。它研究的是：一个 Agent 把工作交给另一个 Agent 时，什么状态应跨越边界；工作完成后，哪些局部结果可以成为 Parent、团队或未来 Agent 的可靠记忆。

建议阅读路径：

- **5 分钟：** [领域总览](overview.md)，理解两个关键边界与八个机制分支。
- **15 分钟：** 总览 + [一般架构](architecture.md)，跟随一次 spawn、执行、提交和未来复用的数据流。
- **30 分钟：** 再读[方案空间](solution-landscape.md)和[近期变化](trends.md)。
- **专题：** 进入[机制分支](mechanisms/README.md)或[场景视图](scenarios.md)。
- **工程：** 从[GitHub 雷达](github-radar.md)进入 10 份固定版本项目报告，查看 commit、数据流、依赖、维护边界和项目特有失败模式。
- **横切：** [评价、安全、成本与互操作](cross-cutting/README.md)把八个分支放进统一约束。
- **证据边界：** [方法与范围](method-and-scope.md)与[审计入口](../audit/README.md)。

当前已经完成广度发现、八分支地图、42 篇论文深读、10 个固定版本仓库和横向综合。最终轮次仍会处理 reader 吸收、双向证据发布、饱和记录与严格验证，但主体内容已经可以独立阅读。
