# 发现、检索与行动耦合

## 问题

团队保存了知识，不表示新的 Subagent 会发现它。新 Agent 可能不知道应搜什么，也可能被大量共享记录淹没。更危险的是，相关内容可能越权、过期、低可信或来自受污染的 sibling。

## 主要方案族

- **启动时注入：** 按项目或角色加载固定 memory 文件；稳定但可能过宽、过时。
- **Pull retrieval：** Child 根据任务主动查询关键词、语义、字段或图；灵活但依赖 query formulation。
- **Push/subscribe/inbox：** 相关更新主动送达 Agent；及时但产生中断、重复和顺序问题。
- **Transactive routing：** 先确定哪个 Agent、artifact 或 memory domain 可能知道答案，再获取局部证据。
- **Permission/trust-aware reranking：** 先排除不可见内容，再结合相关性、来源、时间、path trust 和成本排序。
- **Risk-gated use：** 对回答、计划和高风险工具调用采用不同 evidence threshold。

[MAP-Graph](https://arxiv.org/abs/2608.10509)把 hard permission、graded trust、lineage 与 action risk 连接起来，代表近期“检索不等于授权”的研究方向。

## 尚未解决

多数 memory benchmark 假设 query 已给定，较少测量 Agent 是否知道何时检索、能否找到 sibling 的正确 domain、以及共享 memory 是否导致错误行动。未来实验需要同时记录候选生成、过滤、上下文编译和最终行为，不能只报告 top-k recall。
