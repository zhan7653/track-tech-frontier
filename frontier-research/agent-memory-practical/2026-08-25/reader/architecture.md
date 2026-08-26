# Agent Memory 六层架构

本页是六层正文的架构入口；完整解释见[总览](overview.md)。它描述当前实现与研究案例的共同数据流，不表示推荐部署组合。

```text
1 输入
  对话/工具轨迹、文档、代码、视觉与状态事件
      ↓
2 写入与形成
  过滤、抽取、分类、no-op、来源准入
      ↓
3 状态、存储与索引
  原始历史、current state、可读正文、派生索引
      ↕
4 管理与演化
  update、merge、supersede、version、semantic forgetting
      ↓
5 读取与上下文
  直接注入、工具检索、渐进展开、预算化编排
      ↓
6 反馈、经验与持续学习
  citation/outcome → Experience、Skill、operation policy、Memory design
      └────────────────────────────→ 回到形成或管理
```

| 层 | 工程状态 | 代表入口 |
|---|---|---|
| 1 输入 | 原始 payload 与项目/时间定位 | [01-input.md](01-input.md) |
| 2 写入与形成 | TencentDB L1–L3/Skill；Codex Phase 1/2；MemTxn admission | [02-write-formation.md](02-write-formation.md) |
| 3 状态、存储与索引 | JSONL/DB/Markdown/FTS/vector/graph/Git；双时间版本 | [03-state-storage-indexing.md](03-state-storage-indexing.md) |
| 4 管理与演化 | 两套现有更新；MemTxn、GEM/MemState、ForgetEval | [04-management-evolution.md](04-management-evolution.md) |
| 5 读取与上下文 | 每种 Memory 的进入、检索、输出和上下文位置 | [05-retrieval-context.md](05-retrieval-context.md) |
| 6 反馈与学习 | 具体论文/仓库驱动的 Experience、Skill、policy 与 design 演化 | [06-feedback-learning.md](06-feedback-learning.md) |

Skill 不构成独立行动层：形成在第 2 层，版本管理在第 4 层，读取在第 5 层，使用结果与持续改进在第 6 层。
