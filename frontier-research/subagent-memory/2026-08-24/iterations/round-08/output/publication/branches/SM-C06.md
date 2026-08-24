# 群体经验迁移：Trajectory、Card、Constraint 与 Skill

## 问题与迁移单元

经验共享不是“把成功历史搜出来”这么简单。raw trajectory 保真但很长；summary 短却可能丢失状态与失败；skill 可执行却会扩大权限；不同模型还会对同一提示采用不同 reasoning style。方案差异首先在**迁移单元**。

## 方案族及内部流程

### Population trajectory repository

[Multi-Agent Transactive Memory](https://arxiv.org/abs/2606.19911)让 producer Agent 提交 action–observation trajectory chunk，consumer Agent 检索复用。index 先由公开/生成训练轨迹 pre-populate，再随 producer 成功轨迹增量增长。检索不是只用 similarity：论文在 trajectory prefix 的 branching point 注入不同候选，比较 consumer 相对 no-retrieval 的 outcome improvement，训练 consumer-specific learning-to-rank retrieval。

ALFWorld index 使用 3,553 train episodes、274 held-out test；WebArena 自建 724/88 split，涉及 35–37 producer 与 34 consumer。test question 未直接入库，但 task type/environment 可相似。它代表开放 population reuse，不处理 permission、恶意 producer 和 trajectory deletion。

### Hierarchical collaboration graph

[G-Memory](https://arxiv.org/abs/2506.07398)保留 interaction graph、query graph、insight graph。新任务先 dense retrieve query nodes，再 1-hop 扩展；向上找到 supported insight，向下对历史 collaboration graph 做 LLM sparsification，最后按当前 Agent role 生成不同 memory packet。任务完成后更新三层图。

其 sensitivity result 很重要：更多 hop 和更大 k 会引入无关 insight，性能可下降。角色化和多粒度 retrieval，而不是单纯增加历史，是论文所支持的机制。

### Decentralized dual pools

[DecentMem](https://arxiv.org/abs/2605.22721)不设统一 team repository：每个 Agent 有 exploitation pool（已巩固 trajectory）和 exploration pool（未见 context 的候选），online router 根据 stage-wise feedback 调整两者权重。它试图保留 specialization 和多样性，降低中央通信。

代价是 LLM-as-judge feedback、per-agent store 管理和全局一致性弱。论文跨 AutoGen/DyLAN/AgentNet 与多个任务报告收益，但不能推出所有 decentralized memory 优于集中式；对高风险/真实异构 Agent 的验证仍有限。

### Signed strategy cards + typed relation graph

[ConMem](https://arxiv.org/abs/2606.08702)把成功/失败 trajectory 提炼为 signed card，包含 PLAN/EXEC/EVAL 等策略字段；card 之间有 supports、satisfies、constrains、conflicts 等 relation。运行时执行 retrieve → graph expansion → coordinate → compose，删除依赖缺失或互相冲突的候选，生成 budgeted slate。

coordination 在实验中删掉超过一半扩展候选，planning 中超过八成；消融表明 graph expansion、coordination、failure reflection 和 failure admission 都有贡献。它把 memory unit 与 skill unit合并，但 relation extraction 和 profile calibration 仍可能把错误结构固化。

### Cross-model contrastive constraints

[MemCollab](https://arxiv.org/abs/2603.23234)首先证明 naive cross-model memory transfer 可能降低目标 Agent 性能。它让多个 backbone 在同一训练 task 上生成 trajectory，选择正确或 strongest trajectory 为 preferred，将其与其他 trajectory 对比，提取 violation pattern 与 reasoning invariant，再写成 `enforce invariant / avoid violation` constraint。memory 共享，但保留 model identity tag，并按 task category 检索。

这比复制 32B reasoning 给 7B 更抽象，也依赖 designated/strongest summarizer 判断差异；数学/代码任务的可验证答案并不代表开放工具环境也同样有效。

### Rule、Skill 与 bounded Subagent

AutoRefine 提醒“技能”不是唯一经验形式。局部 constraint 应成为 Rule；Parent 可执行流程成为 Skill；只有需要 private search state、独立 decision loop 和 termination 的 lesson 才成为 Subagent。representation 选择与 contract/replay validation 耦合，避免把一个规则包装成拥有过多 runtime authority 的 Agent。

### 内部 memory workers 与任务 Agent

MIRIX 的六个 Memory Managers、MAPLE 的 Memory/Learning/Personalization workers、TreeMem 的 Builder/Summarizer/Retriever 都属于“用 Agent 实现 memory pipeline”。它们能说明路由、抽取和 credit assignment，却不自动证明 Parent、Sibling 和长期 task Subagent 之间有共享记忆。报告将其作为 bridge，而非共享拓扑的主证据。

## 方案比较

| 单元 | 保真 | token/计算 | 跨模型 | 权限影响 | 主要失败 |
|---|---|---|---|---|---|
| Raw trajectory | 高 | 高 | 弱 | 重放工具步骤 | 噪声/过期 |
| Hierarchical graph | 高到中 | 建图+LLM稀疏 | 中 | role packet | graph drift |
| Per-agent dual pool | 中 | 多 store/judge | Agent-specific | 私有为主 | 目录和一致性 |
| Signed card graph | 中 | relation/coordination | 中 | 作为提示 | 错误 card/edge |
| Contrastive constraint | 低粒度抽象 | offline 多 trajectory | 强一些 | 作为 guidance | summarizer bias |
| Skill/Subagent | 可执行 | validation 高 | 依 runtime | 高 | 权限与失效 |

## 安全与负面结果

MPBench 的 experience-to-procedure channel说明一次被污染的 task trace 可被提升为广泛适用 skill；MemCollab 的 naive transfer 说明“来自更强模型”也可能伤害较弱 consumer。公开文献对长期 stale skill、恶意 producer、跨 Agent 撤销的直接 90-day negative evidence仍薄弱。

## 当前研究在改变什么

研究重点从单 Agent reflection 转向 population artifact infrastructure、role-aware graph、cross-model abstraction 和 representation admission。下一结论受阻于统一的 marginal utility/permission/expiration protocol：当前各论文使用不同 task、backbone、budget 和 update stream，无法排出一个普遍赢家。


## 证据账本绑定

跨 Agent 经验复用正在从相似度检索转向 consumer-specific utility、对比约束、分层图和失败卡片；现有证据同时表明跨模型负迁移与过量检索是真实边界，不能假设共享越多越好。
<!-- synthesis:SY-C06 claims:R5-C016,R4-C027,R4-C030,R4-C035 clusters:SM-C06 -->
