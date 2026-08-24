# 当前共识、分歧与未解决问题

## 相对稳固的共识

- Subagent Memory 首先是跨主体状态边界问题，不是单一存储后端问题。
- Parent-to-child 继承与 child-to-team 提交需要分开建模；同一个 transcript 不能替代两种边界。
- Shared state 的“可写”不等于“已验证、可行动”；至少需要区分局部、候选和已提交状态。
- Agent、任务、项目、团队和租户 scope 会直接影响读取、删除和行动，不能只作为展示 metadata。
- GitHub repository 和作者 Benchmark 能证明实现或实验存在，不能单独证明生产采用或普遍优势。
- Checkpoint、session history、shared backend、workspace 和 long-term memory 是不同状态面；“持久化”不能作为统一能力标签。
- 简单共享底座、显式治理服务和 transactional belief state 解决的不是同一问题，复杂度应按风险与并发需求选择。

## 主要争议

- 集中式 shared memory 是否比 per-agent/decentralized memory 更能支持长期学习；
- Parent 单写者是否是足够可靠的 commit 控制，还是需要 transaction 和显式 conflict state；
- 完整 trajectory、结构化 memory card 与蒸馏 constraint 哪种更能跨模型和任务迁移；
- 实时 push、共享 workspace 与按需 pull retrieval 的相对成本和正确性；
- 高风险 action gate 应放在 memory service、runtime、Parent 还是工具授权层。

## 已经能形成的限定判断

1. **继承：** 现实 runtime 已把历史、普通 state、application context、workspace 和 capability 暴露为不同面；当前没有统一的最小充分 delegation protocol。
2. **身份：** Subagent persistence 实际绑定 thread、layout、project、participant 或 root/child role，而不是一个跨框架通用 Agent ID。
3. **共享：** object、file/backend、checkpoint/store、Redis current value 与 governed database 不是可互换的“shared memory”。
4. **提交：** 工程常见仍是 reducer、LWW、Parent 串行或应用锁；conflict surface、validated patch、belief transaction 与 repair 主要是新研究/治理系统。
5. **回流：** final text、ToolMessage、state update 和 artifact 是主流；evidence-linked promotion/replay 尚非 runtime 默认。
6. **经验：** utility、role 和适用条件开始替代纯相似度，但 negative transfer 和过量检索否定“共享越多越好”。
7. **安全：** 风险跨 inheritance→return→shared memory→action 传播，单点 filter 或 final-output audit 不足。
8. **评价：** 现有协议可互补但不可汇总成统一 Memory 排名。

## 尚未解决的问题长名单

- delegation packet 的充分性、泄漏和陈旧性缺少统一 Benchmark；
- 多 Agent memory 的性能增益常与额外模型调用、critic、token 和任务重复混杂；
- 动态权限、删除和撤销在摘要、图、缓存、技能和 side effect 间的级联证据不足；
- 新兴 transaction/conflict/provenance 方案缺少跨团队复现和真实 runtime 对照；
- 跨 MCP/A2A/runtime 的身份、scope 和 memory capability 尚未形成可验证互操作语义。

## 人工评审最值得判断的事项

完整报告已经给出默认判断，人工不需要逐方向重做调研。最值得评审的是：

- 哪些业务场景真的需要 shared authoritative belief，而不是共享工件和 Parent 合并；
- 哪些高风险状态必须强制保留冲突、来源与 action gate；
- 是否需要给某类命名 Subagent 跨 session 记忆，以及它的清理/撤销边界；
- 哪个新研究机制值得继续做独立复现或更深项目审计；
- 当前 10 个工程深潜是否遗漏了用户实际采用的关键 runtime/service。

这些问题是完整研究后的决策点，不是把不完整方向交给人补写。
