# Subagent Memory 技术前沿调研

**研究模式：** comprehensive snapshot  
**证据截止：** 2026-08-24  
**当前阶段：** Round 08 完成；严格 Bundle、Reader 与测试验证通过

这套调研解释 Parent Agent、Subagent 和并行 Agent 之间的状态如何继承、隔离、共享、提交、合并、回流与复用。它以 [Agent Memory v10](../../../examples/agent-memory-v10/README.md) 为质量下限，但从新的输入独立推导技术地图。

从[读者入口](reader/README.md)开始；研究过程、输入与限制见[审计入口](audit/README.md)，最终验证见[验证记录](audit/final-verification.md)。
