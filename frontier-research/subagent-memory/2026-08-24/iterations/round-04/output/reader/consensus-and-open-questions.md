# 暂定共识、分歧与未解决问题

## Pilot 后较稳定的认识

- Subagent Memory 首先是跨主体状态边界问题，不是单一存储后端问题。
- Parent-to-child 继承与 child-to-team 提交需要分开建模；同一个 transcript 不能替代两种边界。
- Shared state 的“可写”不等于“已验证、可行动”；至少需要区分局部、候选和已提交状态。
- Agent、任务、项目、团队和租户 scope 会直接影响读取、删除和行动，不能只作为展示 metadata。
- GitHub repository 和作者 Benchmark 能证明实现或实验存在，不能单独证明生产采用或普遍优势。

## 仍有分歧

- 集中式 shared memory 是否比 per-agent/decentralized memory 更能支持长期学习；
- Parent 单写者是否是足够可靠的 commit 控制，还是需要 transaction 和显式 conflict state；
- 完整 trajectory、结构化 memory card 与蒸馏 constraint 哪种更能跨模型和任务迁移；
- 实时 push、共享 workspace 与按需 pull retrieval 的相对成本和正确性；
- 高风险 action gate 应放在 memory service、runtime、Parent 还是工具授权层。

## 当前证据稀薄的问题

- delegation packet 的充分性、泄漏和陈旧性缺少统一 Benchmark；
- 多 Agent memory 的性能增益常与额外模型调用、critic、token 和任务重复混杂；
- 动态权限、删除和撤销在摘要、图、缓存、技能和 side effect 间的级联证据不足；
- 新兴 transaction/conflict/provenance 方案缺少跨团队复现和真实 runtime 对照；
- 跨 MCP/A2A/runtime 的身份、scope 和 memory capability 尚未形成可验证互操作语义。

这些不是等待人工补写的占位。后续轮次会用广度扩展、固定版本工程分析、Benchmark 指纹和负面证据给出更完整的限定结论。
