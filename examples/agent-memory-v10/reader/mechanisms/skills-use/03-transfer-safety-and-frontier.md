# 程序性记忆的迁移、安全、评测与最新研究

程序性记忆的价值不在于“写出了一个 skill 文件”，而在于它能否在新情境中产生正确行为，同时不把过时、越权或被污染的经验带入真实行动。本篇把迁移、行为评测、安全供应链和 2026 年最新研究放在同一框架中。

## 1. 评测应区分六个事件

```text
经验被捕获
  → 候选工件被形成
  → 工件被晋升
  → 当前任务检索到工件
  → 工件被选择并执行
  → 产生任务结果或副作用
```

很多论文只测其中一段：反思是否进入下一轮、skill 是否写入库、或最终任务是否成功。安全论文也可能只证明恶意内容进入持久工件，不等于它已在真实权限下造成副作用。报告每个阶段的 conversion rate，才能定位 formation、retrieval、applicability、authorization 或 execution 失败。

## 2. Mem2ActBench：长期约束要进入工具参数

[Mem2ActBench](https://arxiv.org/abs/2601.19935)包括 2,029 个 session 和 400 个工具使用任务。请求本身可能不完整，Agent 需要从历史找出长期偏好或约束，再选择工具和填参数。它测的不是“能否复述记忆”，而是 memory 是否改变 action grounding。

该协议适合检查 procedural/use 层，却不能单独证明技能形成：系统可能只是检索一条用户约束，并没有从轨迹蒸馏 procedure。分析时应把 constraint memory、tool planning 和 executable skill 分开。

## 3. AFTER：迁移维度开始被显式拆分

[AFTER](https://arxiv.org/abs/2606.23127)在 382 个任务、六种角色和 22 类技能上区分 local improvement、cross-task、cross-role 和 cross-model transfer。作者结果显示某些技能能迁移，某些呈角色特化。

这比在原任务重复试验更接近程序性记忆的核心问题。仍需要进一步控制：源/目标工具版本、输入分布、model context、skill selection budget、失败任务是否进入形成、以及迁移提升来自内容还是更多推理 token。角色迁移还涉及权限与职责，不只是语义相似。

## 4. MemP、MemSkill 与 XSkill：正在形成的三条路线

### 4.1 MemP：分层的程序表示

MemP 从 trajectory 形成 step-by-step instruction 和 high-level script，并为 build、retrieval、update 设计不同策略。它的研究价值是把“经验”拆为多个复用粒度；关键问题是哪个粒度在不同预算和任务漂移下更稳定。

### 4.2 MemSkill：形成过程本身成为技能

MemSkill 的 controller 选择 memory-operation skills，executor 形成 skill-guided memory，designer 根据 hard cases 修改技能集合。它把手写 memory pipeline 推向 self-evolving policy。评测需要同时冻结 task solver 与 memory manager，否则两层变化难以归因。

### 4.3 XSkill：视觉动作经验与任务技能分流

XSkill 分别累积 action-level experience 和 task-level skill，再根据当前视觉上下文适配。具身场景要求表示 observation、visibility、空间状态和动作后果；仅保存文本 instruction 会丢 grounding。

这些工作共同说明前沿已从“有没有反思”转向“复用工件的层级、形成策略和迁移边界”。它们仍主要是作者协议，缺同一轨迹、模型和预算下的独立横向复现。

## 5. PoisonedEvolution：晋升流水线成为攻击面

2026 年 8 月的 [PoisonedEvolution](https://arxiv.org/html/2608.05563v2) 研究攻击者如何让不可信轨迹被 self-evolving Agent 归纳为持久技能。论文把 success 拆成 Inclusion、Evolution Attribution 和 Realization，而不是只看最终回答。

作者在 SkillClaw 的 10% attacker support 条件下，报告六种 evolver、四类目标行为的 600 个完成试验中有 546 个成功嵌入目标行为（91.0% SER）；在结构不同的 Trace2Skill 流水线上，同一支持比例为 369/600（61.5% SER）。这些数字证明所测形成流水线存在可转移的 promotion 风险，但不代表所有 Agent，也不等于每个恶意技能已获真实权限并产生危害。

攻击链说明“多数出现”“多 Agent 支持”可能只是同源协同污染。晋升不能只按频率或成功次数，应检查来源独立性、反例、环境、effect、签名/provenance 和 replay validation。

## 6. 防护应覆盖完整技能供应链

| 阶段 | 典型攻击/失败 | 可观察控制 |
|---|---|---|
| capture | 恶意或伪造 trajectory | principal、source、environment、tamper-evident log |
| distill | 模型将 payload 解释为规则 | untrusted fencing、structured extraction、counterexample |
| validate | 测试覆盖过窄或被污染 | held-out replay、negative tests、effect inspection |
| promote | 重复同源被当共识 | independence、risk tier、human/high-risk gate |
| retrieve | 相似但不适用、越界共享 | scope/version/applicability filter |
| execute | skill 继承过大权限 | sandbox、typed effect、action-time authorization |
| update | reward hacking、自我强化 | exposure log、shadow/canary、rollback |
| revoke | 派生/复制版本仍存在 | lineage、registry、dependency invalidation |

签名只能证明某个主体发布了工件，不能证明内容安全；sandbox 只覆盖所测环境；人工审核也可能看不到运行时参数和组合效果。可靠性来自多层边界，而不是单个“可信”标签。

## 7. 工具/API 漂移：程序性记忆的主要自然失效

技能可以在语义上仍合理，却因环境变化失效：API 参数改名、CLI flag 删除、schema migration、路径变化、模型行为改变、权限收紧、依赖漏洞或许可证变化。每个工件需要 environment fingerprint 和 compatibility range，并在依赖事件后触发：

```text
active → suspect → replay-needed → active(new revision) | deprecated
```

修复不应覆盖旧版本，而应产生 predecessor-linked revision，保留原适用范围和失败记录。组合技能还要沿 DAG 传播 invalidation；上游 output schema 改变会使下游即使代码未变也不再适用。

[STALE](https://arxiv.org/abs/2605.06527) 暴露了这一层的行为后果：权威 store 中的状态已经更新，不保证模型在规划与行动时放弃旧前提。对 procedure/skill 而言，修改事实或 API 文档只是第一步；旧技能、已编译计划、检索缓存和工具参数模板都可能继续携带旧假设。因此“修复完成”需要追踪 `revision → skill applicability → compiled plan → tool action`，并验证旧 version 不再被选择。STALE 的实验并非专门比较技能库，却构成了“状态更新不等于行为更新”的直接边界。

## 8. learned policy 的长期问题

Online controller 常以当前任务 reward 更新“是否检索、巩固、遗忘或用哪个技能”。短期 reward 不能代表长期记忆价值：删除一个低频规则可能数周后才暴露；自动选择熟悉技能会减少探索，使其他技能缺少反馈。

研究需要记录 propensity/exposure，使用 deterministic baseline、off-policy evaluation、shadow 或 canary，再限制 residual policy 的作用范围。长期指标包括 regret、catastrophic forgetting、policy churn、rollback rate、unsafe proposal 和 memory growth，而非只看最近任务成功率。

## 9. 当前共识与争议

较稳定的共识包括：

- 原始轨迹、反思、procedure 和 executable skill 是不同工件；
- 来源、适用条件、环境版本、结果和弃用状态需要随工件保存；
- recall 不应自动授予执行权限；
- 同任务重试不等于跨任务/角色/模型迁移；
- 自我演化扩大了 evidence-promotion 与 lifecycle 攻击面。

仍有争议的问题是：哪种抽象粒度能在压缩和长尾之间取得稳定平衡；多少自动验证足以晋升；meta-policy 是否在长期成本下优于显式规则；团队共享技能如何处理所有权、许可证和撤回；自然语言 reflection 与代码 skill 应否使用同一 registry。

## 10. 近期研究最需要补的实验

一个能回答这些争议的共同实验，应给不同方法同一批包含成功、失败和恶意样本的轨迹，固定任务模型、预算和工具版本，然后比较：

- raw trajectory、reflection、instruction、script、executable skill、meta-policy；
- original task、near transfer、cross-task、cross-role、cross-model、version drift；
- formation precision、source/step coverage、retrieval/applicability、first-action、task outcome；
- build/validation/retrieval/execution/repair 成本；
- poisoning inclusion、promotion、trigger、authorization 和 harmful action；
- deprecate/revoke 后的副本与派生清除。

只有把 formation、transfer、execution 和 security 放入同一 trace，才能说明最新研究到底在改进哪个环节。否则“更会学习经验”可能只是保存更多文本、调用更多模型，或更积极地执行未验证工件。

返回[使用、反馈与技能入口](../06-use-feedback-and-skills.md)。
