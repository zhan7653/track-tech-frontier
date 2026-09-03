# Agent Memory：六层实现架构与前沿机制

**证据截止：2026-08-25**

[六层 HTML 阅读版](../site/index.html)

这是一套独立的中文读者报告。它从 TencentDB Agent Memory 与 Codex Local Memory 的固定实现出发，按“输入 → 形成 → 状态 → 管理 → 读取 → 反馈”六层解释 Agent Memory，再用具体论文和仓库展示近期机制。

从[读者入口](reader/README.md)开始。完整 Codex 工程说明在[Codex 完整说明](reader/codex-complete.md)。研究过程和证据记录位于[audit](audit/README.md)。

## 文档组成

- [总览与通用架构](reader/overview.md)
- [第 1 层：输入](reader/01-input.md)
- [第 2 层：写入与形成](reader/02-write-formation.md)
- [第 3 层：状态、存储与索引](reader/03-state-storage-indexing.md)
- [第 4 层：管理与演化](reader/04-management-evolution.md)
- [第 5 层：读取与上下文](reader/05-retrieval-context.md)
- [第 6 层：反馈、经验与持续学习](reader/06-feedback-learning.md)
- [Codex 完整工程说明](reader/codex-complete.md)

这套报告以 Q050 确认目录为结构基准，区分固定代码事实与论文/原型机制。它不提供产品选型、部署方案或统一性能排名。
