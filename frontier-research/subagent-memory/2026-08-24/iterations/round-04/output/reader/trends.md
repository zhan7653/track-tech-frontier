# 当前主流、12 个月变化与 90 天弱信号

## 当前主流

在广度语料和打开的公开 runtime 文档中，最常见的工程形态仍是 manager 编排、消息/工具结果回流，以及共享文件、checkpoint、应用状态或简单 memory service。Claude Code、LangGraph、OpenAI Agents SDK 和 Deep Agents 已把 stateless、per-invocation、per-thread、project/user scope、read-only writer policy 等生命周期选择显式暴露给开发者；transactional belief commit、级联修复和动态 derivation-aware permission 仍属于较新的研究或少量项目主张。

## 最近 12 个月的实质变化

- **共享对象从文本记录变成有状态语义的对象。** Private/shared tiers、typed state、trajectory、patch、claim、evidence 和 skill 开始分开。
- **Memory 拓扑不再默认集中。** Transactive memory、decentralized per-agent pools 和 central-critic/decentralized-execution 对集中共享库提出替代。
- **写入被重新定义为提交。** PatchBoard、MemTX 和 conflict-aware memory 关注 validation、transaction、conflict 和 repair。
- **权限从静态 ACL 进入派生链。** Collaborative Memory、Governed Shared Memory、GateMem 与 MAP-Graph 分别处理动态策略、多租户传播、删除和 lineage-aware use。
- **经验共享开始处理异构模型和信用。** MemCollab、TreeMem、ConMem 与 MATM 关注跨模型偏差、pipeline credit、关系化经验和 population retrieval。
- **Subagent 自身持久化成为显式 runtime 选择。** 干净启动、调用内恢复、thread 连续性和跨 session 角色记忆不再被混成一个布尔开关。

## 最近 90 天弱信号

截至 2026-08-24，Pilot 已发现一批非常新的方向：

- `When Child Inherits`：把 subagent spawn inheritance 视为独立安全边界；
- `MemTX`：memory write 与 belief commit 分离；
- `LatticeMind`：保存并处理 incompatible claims；
- `MAP-Graph`：来源路径影响权限、信任和 action gate；
- `Multi-Agent Transactive Memory`：跨 Agent population 检索 trajectory；
- `StateFuse`：用冲突保留和 correction handle 替代早期折叠；
- 大量新建 coding-agent memory、handoff、blackboard 和 fleet repository。

这些信号大多仍是预印本、作者实验或新仓库。它们说明问题重心在移动，但不足以证明统一主流、性能优势或生产成熟度。

## 下一步验证

后续轮次将把每项信号放回机制分支，检查论文版本、代码关系、Benchmark 协议、复现状态和项目固定 commit。当前 adoption 搜索主要返回第一方和自述案例，因此不会把“生产使用”外推为行业采用率。
