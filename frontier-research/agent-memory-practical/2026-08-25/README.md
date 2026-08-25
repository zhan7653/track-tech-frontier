# Agent Memory：从 Codex 抽象的七层架构与近期进展

**证据截止：2026-08-25**

这是一套独立的中文读者报告。它以公开的 Codex Memory 实现为成熟工程锚点，从中抽出一条七层链路，再把近 90 天优先、半年兜底的论文、官方文档和代码实现放回对应层解释。

从[读者入口](reader/README.md)开始。完整 Codex 工程说明在[Codex 完整说明](reader/codex-complete.md)。研究过程和证据记录位于[audit](audit/README.md)。

## 文档组成

- [总览与通用架构](reader/overview.md)
- [第 1 章：输入层](reader/01-input.md)
- [第 2 章：写入与形成层](reader/02-write-formation.md)
- [第 3 章：状态、存储与索引层](reader/03-state-storage-indexing.md)
- [第 4 章：管理、演化与遗忘层](reader/04-management-evolution.md)
- [第 5 章：读取、检索与上下文层](reader/05-retrieval-context.md)
- [第 6 章：使用、行动与技能层](reader/06-use-action-skills.md)
- [第 7 章：反馈、经验与持续学习层](reader/07-feedback-learning.md)
- [Codex 完整工程说明](reader/codex-complete.md)

这套报告解释系统当前如何运行、哪些机制正在进入实现、哪些仍停留在论文或原型阶段。它不提供产品选型、部署方案或统一性能排名。
