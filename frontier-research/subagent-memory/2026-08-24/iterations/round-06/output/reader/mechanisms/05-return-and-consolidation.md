# 回流、巩固与来源

## 问题

Subagent 的局部工作通常比最终答案丰富。若只保留结论，Parent 无法区分观察、推断、失败与猜测；若保留整条轨迹，又会把噪声和成本转移到未来检索。

## 主要方案族

- **Final text：** 最小接口，适合低风险一次性子任务；长期复用和审计弱。
- **Structured result envelope：** 返回结论、证据、工件、验证、未决项和风险，便于 Parent 按字段处理。
- **Artifact/patch-first：** 代码、文档、数据和状态差异是权威返回，文字只是解释。
- **Critic/curator promotion：** Child 输出先进入候选区，由 critic、测试或 Parent 决定是否晋升。
- **Lineage-preserving synthesis：** 摘要保留来源与派生关系，使权限、撤销和风险能沿链传播。

[CoMIC](https://arxiv.org/abs/2606.00756)让 cloud critic 过滤轨迹，[MAP-Graph](https://arxiv.org/abs/2608.10509)把 lineage 直接用于可见性和行动判断。[State Contamination](https://arxiv.org/abs/2605.16746)则提示：若在不可信内容已经被摘要后才清洗，隐藏影响可能保留下来。

## 尚未解决

系统缺少一致的 child-result contract。成功测试能证明某个工件当前有效，却未必证明其策略可跨任务复用；Parent 综合也可能删除少数反例。后续需要比较不同 runtime 的实际 result item、trace、artifact 和 memory writer 边界。

深入机制见[Child 输出怎样变成可复用状态](return-consolidation/01-compilation-and-lineage.md)。
