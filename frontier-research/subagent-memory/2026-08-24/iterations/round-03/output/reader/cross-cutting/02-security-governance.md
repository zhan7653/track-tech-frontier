# 安全、权限与治理

风险链从 Parent 的 delegation view 开始，经过 Child 工具和局部状态、共享写入、摘要/巩固、Sibling 检索，最终到工具行动。威胁包括 inheritance injection、越权读取、confused deputy、memory poisoning、来源洗白、stale propagation、恶意 Agent、秘密跨 scope 泄漏和删除不完全。

防护需要组合文本过滤、能力隔离、write quarantine、provenance、动态 scope、版本、conflict state、action re-authorization、撤销和审计。单一 toxicity 或 prompt-injection filter 无法覆盖由摘要和多跳派生造成的隐藏传播。

近期负面证据把风险进一步拆开：MPBench 研究不可信输入怎样进入持久 memory；Bad Memory 显示已经存在于 memory file 的 payload 可以影响后续 session；When Child Inherits 关注 parent compromise 随 spawn 传播；StateFuse、MemTX 和 Governed Shared Memory 则分别暴露早期折叠冲突、错误 belief commit 与 pipeline ordering 问题。它们的实验对象不同，不能合成统一攻击成功率，但共同说明过滤、继承、提交和行动四个位置都需要独立观察。
