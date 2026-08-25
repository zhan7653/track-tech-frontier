# 七层实现地图

Codex 的实现锚点和近期补充已分别写在七个根目录章节中。本页提供导航和最小的方案、数据流、实现、成本/失败、最新研究索引。

### 方案

七层链路把输入、形成、状态、管理、读取、使用和反馈分开，Codex 以两阶段形成和文件化读取贯穿其中。

### 数据流

`rollout → Phase 1 → SQLite candidates → Phase 2 → Markdown/skills → read → citation/usage`。

### 实现

对应章节分别记录 Codex 文件路径、数据库字段、工具边界和近期官方仓库/论文。

### 成本与失败

后台模型调用、上下文预算、索引或文件更新、跨项目 scope、语义合并错误和删除传播是主要成本与失败面。

### 最新研究

近期研究集中在 source-supported write、状态级 revision/forgetting、主动检索、行动门控、技能晋升和持续反馈。

| 层 | 入口 |
|---|---|
| 输入 | [01-input.md](../01-input.md) |
| 写入 | [02-write-formation.md](../02-write-formation.md) |
| 状态 | [03-state-storage-indexing.md](../03-state-storage-indexing.md) |
| 管理 | [04-management-evolution.md](../04-management-evolution.md) |
| 读取 | [05-retrieval-context.md](../05-retrieval-context.md) |
| 使用 | [06-use-action-skills.md](../06-use-action-skills.md) |
| 反馈 | [07-feedback-learning.md](../07-feedback-learning.md) |
