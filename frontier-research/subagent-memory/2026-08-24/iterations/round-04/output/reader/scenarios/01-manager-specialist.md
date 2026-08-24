# Manager–Specialist 委派

Manager 保留目标和最终答案所有权，把搜索、分析、代码检查或验证交给 Specialist。这里最重要的不是共享长期数据库，而是 **delegation packet** 和 **result envelope**。

Manager 需要选择目标、约束、输入工件、已有事实、权限和完成标准。Specialist 在局部上下文中工作，产生结论、证据、变更和未决项。Manager 决定哪些内容进入当前计划、团队状态或长期经验。

若使用 handoff，Specialist 可能接管同一 run；若使用 agent-as-tool，Manager 通常仍控制对话并接收嵌套结果。两者对历史继承、guardrail、trace 和写入责任的含义不同。当前主要风险是全历史继承、摘要遗漏、Parent 单点误判和 Child 结果被自动当作已验证事实。
