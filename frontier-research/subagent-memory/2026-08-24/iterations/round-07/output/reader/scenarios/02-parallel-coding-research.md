# 并行 Coding 与 Research Subagents

多个 Subagent 同时检查代码、论文或数据时，常共享仓库、文件夹、搜索结果和任务板。它们可能读取相同 base version，却在不同时间产生冲突 patch、重复结论或互相依赖的摘要。

典型组合是：Parent 拆分任务；每个 Child 使用独立 worktree、sandbox 或笔记；共享 blackboard 记录任务和工件引用；结果以 diff、evidence packet 或结构化摘要回流；Parent 或 validator 执行 join 和 commit。

Coding 场景强调代码版本、秘密、测试和 patch 冲突；Research 场景强调来源、重复论文、相互引用和综合时丢失反方。两者都需要区分“Child 找到的材料”和“Parent 已接受的结论”。
