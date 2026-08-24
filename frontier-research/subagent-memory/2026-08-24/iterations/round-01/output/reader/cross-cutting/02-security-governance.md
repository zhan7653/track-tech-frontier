# 安全、权限与治理

风险链从 Parent 的 delegation view 开始，经过 Child 工具和局部状态、共享写入、摘要/巩固、Sibling 检索，最终到工具行动。威胁包括 inheritance injection、越权读取、confused deputy、memory poisoning、来源洗白、stale propagation、恶意 Agent、秘密跨 scope 泄漏和删除不完全。

防护需要组合文本过滤、能力隔离、write quarantine、provenance、动态 scope、版本、conflict state、action re-authorization、撤销和审计。单一 toxicity 或 prompt-injection filter 无法覆盖由摘要和多跳派生造成的隐藏传播。
