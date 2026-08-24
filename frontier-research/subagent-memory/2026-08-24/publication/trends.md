# 当前主流、12 个月变化与 90 天前沿

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

## 固定版本代码确认了什么

Round 05 让“趋势”不只依赖论文标题：

- Codex 的 child thread 默认可 full-history fork，但 memory startup 对 non-root 有显式 guard；这把“继承丰富、长期形成集中”变成真实 runtime 形状。
- OpenAI Agents SDK 把 handoff filter、agent-as-tool input、application context、session、sandbox snapshot 和 memory layout 分成独立 API；统一 memory switch 并不存在。
- Deep Agents 把 task child 的 messages 重置，却复制非 private state 并共享 backend；“stateless Subagent”一词需要限定状态面。
- LangGraph 明确区分 per-invocation checkpoint、持久 subgraph namespace 与跨 thread Store；durable execution 与长期 memory 不再是一层。
- Caura 把 scope、write mode、enrichment、dedup、contradiction、search、lifecycle 和 audit放入多服务 pipeline；这代表治理控制面扩张，也增加 path-specific guarantee 风险。
- UFO、memX 与 Statewave demo 作为对照显示，新项目仍常以 in-process blackboard、LWW current value 或外部 compiler client解决局部问题，而没有全套 commit/governance。

这些代码事实支持“状态面正在分层”和“治理从应用约定走向显式 control plane”两个变化，但不能证明所有应用已经采用。

## 现在最前沿的六个问题

| 前沿问题 | 新研究在做什么 | 为什么还没有解决 |
|---|---|---|
| 最小充分继承 | history filter、typed intent、bounded context、capability-scoped view | 没有共同任务与泄漏/充分性联合指标 |
| Child 独立身份 | thread/layout/project memory、root/child write policy | 同名并发、跨任务污染和清理协议不统一 |
| Belief commit | validated patch、transaction、conflict lattice、action gate | 研究 state object 不同，真实 runtime 默认仍较弱 |
| 派生权限与撤销 | provenance graph、scope projection、supersession/repair | summary、cache、embedding、skill 与 side effect 难级联 |
| Population experience | utility ranker、contrastive constraints、signed cards、decentralized pools | 负迁移、恶意 producer、版本漂移与多样性不足 |
| 端到端 Benchmark | access/forget、leak channel、conflict、action、trajectory transfer | 资源预算和 topology 不同，无法形成共同协议 |

## 哪些是主流，哪些仍是前沿

**当前主流 primitive：** manager/Parent 编排、消息或 ToolMessage 回流、共享文件/backend、thread checkpoint、应用构造 namespace、简单检索。它们在多个成熟 runtime 中出现。

**正在进入工程的能力：** project/user memory layout、read-only writer split、tenant/fleet/agent scope、background consolidation、hybrid retrieval、contradiction/lifecycle service。

**仍偏前沿：** 冲突保留的公共 memory contract、snapshot-isolated belief transaction、派生图上的动态权限、跨模型 negative-transfer-aware skill bank、与 action risk 统一的 commit/retrieval gate。

这里的“前沿”表示近期有明确机制和初步证据，不等于推荐采用。复杂控制面是否值得，取决于并发、风险、主体数量、长期保留和 side effect。

## 下一步验证

最终轮次会把这些判断与 claim/synthesis ledger、deliverable manifest 和 reader marker 双向绑定。当前 adoption 搜索主要返回第一方和自述案例，因此不会把“生产使用”外推为行业采用率；90 天 GitHub commit/contributor 只表示维护活动，不表示增长或质量。
