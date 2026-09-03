# Agent Memory 总览与架构

Agent Memory 是让 Agent 把一次任务中的经历，转化为以后还能继续使用的状态与能力的机制。这里的“经历”不只包括用户说过的话，也包括 Agent 的输出、工具调用、工具结果、文档、代码和环境变化。

它不是简单地保存聊天记录，也不等于“接一个向量数据库”。真正的 Agent Memory 要回答四个连续问题：系统收到了什么，哪些内容应该形成、更新或退出 Memory，需要时怎样进入当前上下文，以及使用结果怎样影响下一轮。

## 四个处理阶段

| 阶段 | 回答的问题 |
|---|---|
| 输入材料 | Agent 实际收到了哪些对话、工具结果、文档、代码和环境变化？ |
| 提炼与管理 | 哪些信息值得保留，应该新增、更新、合并还是删除？ |
| 读取与编排 | 当前任务需要哪些 Memory，它们怎样进入上下文？ |
| 反馈与持续学习 | Memory 使用后的结果，怎样改变下一轮行为和 Memory？ |

历史记录、当前有效内容和检索索引是这四个阶段共同使用的持久状态：提炼与管理负责改变它们，读取与编排负责从中选择当前任务需要的内容。

## 为什么选择 TencentDB 和 Codex

这套报告主要用 TencentDB Agent Memory 和 OpenAI Codex Local Memory 来讲解，是因为两者都能从公开实现中看到一条相对完整的 Memory 生命周期，但采用了不同的组织方式。

### TencentDB Agent Memory

[TencentDB Agent Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a)把聊天经历逐步整理为原始记录、原子记忆、场景和长期 Persona，同时还分别处理 Skill、文档知识和代码知识。它适合用来说明：不同类型的材料怎样形成不同 Memory，以及这些 Memory 怎样分层存储、更新和读取。

### Codex Local Memory

[Codex Local Memory](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)以 Coding Agent 的真实任务轨迹为起点，先从单次任务中提取候选，再把多次候选整理成可供新任务读取的本地文件。它适合用来说明：执行历史怎样跨任务沉淀，以及短摘要、完整 Memory 和原始证据怎样逐层展开。
