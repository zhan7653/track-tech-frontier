# 发现、检索与行动耦合

## 问题

团队保存了知识，不表示新的 Subagent 会发现它。新 Agent 可能不知道应搜什么，也可能被大量共享记录淹没。更危险的是，相关内容可能越权、过期、低可信或来自受污染的 sibling。

## 主要方案族

### 启动时注入

按项目、角色或 layout 加载固定 memory 文件；稳定但可能过宽、过时，并把启动成本固定化。

### Pull retrieval

Child 主动查询关键词、向量、字段或图；灵活但依赖 query formulation 和是否知道该检索。

### Push/subscribe 与 transactive routing

更新可进入 inbox/notification；或先定位哪个 Agent/artifact/domain 知道什么。前者及时但有顺序/重复，后者依赖目录新鲜度。

### Permission/trust-aware 与 risk-gated use

先硬过滤不可见内容，再结合相关性、来源、时间、path trust、consumer 和成本排序；回答与高风险 action 使用不同 threshold。

[MAP-Graph](https://arxiv.org/abs/2608.10509)把 hard permission、graded trust、lineage 与 action risk 连接起来，代表近期“检索不等于授权”的研究方向。

## 数据流、实现、成本与失败

数据流是 task/role → candidate generation → scope/trust filter → rerank/context compile → answer/plan/action gate。实现要记录候选被哪一步排除。成本包括 embedding、graph traversal、reranker、notification 和 prompt；失败包括不知何时搜、目录陈旧、越权候选先暴露给模型、过量 hop/token 反而降质。

## 最新研究与尚未解决

多数 memory benchmark 假设 query 已给定，较少测量 Agent 是否知道何时检索、能否找到 sibling 的正确 domain、以及共享 memory 是否导致错误行动。未来实验需要同时记录候选生成、过滤、上下文编译和最终行为，不能只报告 top-k recall。

深入机制见[共享知识怎样到达正确 Subagent](retrieval-action/01-routing-navigation-and-gates.md)。
