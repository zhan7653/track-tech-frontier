# Round 01 Pilot 技术地图

## 从输入中出现的结构

Pilot 不是先按通用 Agent Memory 生命周期分桶，而是沿着 Subagent 的两个边界观察状态：**spawn 时 Parent 向 Child 投影什么**，以及 **Child 结束或协作过程中，什么被提交回 Parent/团队权威状态**。在两个边界之间，多 Agent 系统还需要回答谁拥有状态、共享面是什么、并发写入如何提交、经验如何跨人群复用，以及每个 Agent 怎样发现并安全使用他人知识。

由此形成七个候选一级机制分支：

1. Context Inheritance and Delegation Boundaries
2. Ownership, Namespace and Visibility
3. Shared Coordination Substrates
4. Synchronization, Conflict and Belief Commit
5. Return, Consolidation and Provenance
6. Population Experience and Skill Transfer
7. Discovery, Retrieval and Action Coupling

安全/权限、评价、成本/可靠性/可观测性、互操作保持横切，不成为与生命周期平行的来源分类。

## 改变地图的 Pilot 证据

- OpenAI Agents SDK 的 handoff、agent-as-tool、application context 与 sandbox memory 文档线索表明，“委派”至少包含 active-agent 转移、嵌套工具 Agent 和隔离 workspace 三种不同状态边界。
- `When Child Inherits` 把恶意指令、旧状态、资源与终止权沿 parent-child spawn 传播的问题变成显式安全机制，而不是一般 prompt injection 的附录。
- PatchBoard、MemTX、LatticeMind 和并发异常研究共同把“共享内存”从读写 API 推向 validated mutation、transaction、conflict set 和 repair。
- Collaborative Memory、Governed Shared Memory、GateMem 与 MAP-Graph 把主体、权限、来源和 action risk 放入读写路径，说明 namespace/visibility 不能只作为数据库 metadata。
- Multi-Agent Transactive Memory、DecentMem、CoMIC、ConMem 与 MemCollab 展示了集中式轨迹库、去中心化个体池、云端 critic、关系化 memory card 和跨模型约束蒸馏等不同 population-learning 路线。
- GitHub Pilot 同时出现 blackboard、MCP shared store、file handoff、pub/sub memory service 与 fleet governance，说明真实工程形态比“一个向量库给所有 Agent”更分化。

## 边界修正

- “Subagent Memory”不是稳定统一的论文关键词。后续发现必须联合 hierarchical agent、shared/collective/transactive memory、handoff state、blackboard、experience/trajectory sharing、agent fleet、workspace 和 provenance 等词族。
- 并非所有 multi-agent memory 论文都研究 Parent/Child；只要其机制直接承担 Subagent 间状态隔离、共享、提交、回流或后续复用，仍在范围内。
- 普通 agent routing、纯消息通信和单 Agent 长对话 memory 暂不进入主分支；它们只有在改变跨 Agent 持久状态时才作为证据。

## 下一轮缺口

- Pilot 对 Semantic Scholar 的两条路线被 429 阻断，需要其他独立学术索引、引用扩展和作者/组织路线补偿。
- Parent-to-child delegation 的公开论文少于 shared-store 论文，需要从 runtime code、handoff APIs、sandbox/worktree 和安全研究补充。
- GitHub 高召回结果含大量新建小仓库，需要按 canonicality、真实机制差异、活跃度与固定版本可分析性重新映射。
- 尚未系统覆盖 multi-agent benchmark、multi-party memory、组织记忆、A2A/ACP/MCP 等协议边界与负面生产事件。
