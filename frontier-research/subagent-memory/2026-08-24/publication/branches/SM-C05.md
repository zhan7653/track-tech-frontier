# 回流与巩固：Child 输出怎样变成可复用状态

## 问题与三种对象

Child 结束时至少产生三层对象：raw trajectory/evidence、为当前 Parent 准备的 result envelope、可能跨任务复用的 memory/skill。三者不应由同一个摘要同时承担。

```text
raw local evidence
→ task result (what Parent needs now)
→ candidate durable lesson/artifact
→ validate/admit/version
→ team memory or capability repository
```

## 方案族及内部流程

### Final text 与普通 tool result

Child 返回一段答案，Parent 自行综合。接口最小、延迟低，但来源、失败、替代方案和适用条件通常丢失。它适合一次性低风险子任务，不足以支撑长期记忆晋升。

### Structured result envelope

返回 `conclusion/evidence/artifacts/validation/unknowns/risks/base_revision` 等字段。Parent 可以分别处理结论与工件，检测陈旧 base，并保留未决问题。字段不保证语义真实，但让 validator 和人知道要检查什么。

### Critic/curator candidate promotion

[CoMIC](https://arxiv.org/abs/2606.00756)把 edge Agent 的 subgoal episode 异步上传；cloud critic 给 trajectory-grounded summary/insight/suggestion 和 confidence，达到 admission threshold 的 `(observation, action, result)` 进入 experience store，再按 semantic subgoal id 聚合 global guidance。edge 只收到一个 advisory channel，不直接消费全部别的 Agent 轨迹。

这降低 edge context 和在线阻塞，但集中 critic 可把共同错误传播给所有 Agent，grouping identifier 也决定哪些经验被错误合并。

### Lineage-preserving synthesis

[MAP-Graph](https://arxiv.org/abs/2608.10509)让 summary/claim 保留 source ancestry，使 permission、trust、revocation 和 action risk 能沿派生链传播。它把 provenance 从“报告出处”变成 runtime control signal。

数据结构需要同时保存 direct parents、affected descendants、writer、source trust、scope 和 action dependencies。只有文本 citation 不足以支持 revoke；只有 graph 又不能证明 parent edge 本身正确。

### Typed artifact compilation

[AutoRefine](https://arxiv.org/abs/2601.22758)不是把所有 lesson 写成同一种 memory，而是先从失败/成功 trajectory 得到 evidence-linked intervention specification：触发条件、要改变的行为、所需 observation、persistent state、dependent decisions、completion condition。compiler 按 runtime-relative ownership 依次尝试：

1. Rule：局部决策；
2. Skill：由 Parent 执行的程序；
3. bounded Subagent：独立 interface、isolated state、control loop、termination。

选择第一个能关闭全部 obligation 的 schema，否则 defer。contract gate 检查对象是否真的实现边界；replay gate 要求 correction cases 改善且 preservation cases 不退步。保证只覆盖 replay evidence，不是全局正确性。

### Memory worker pipeline 与 credit assignment

[TreeMem](https://arxiv.org/abs/2605.04811)把 Builder、Summarizer、Retriever 的输出扩成树，用后续 branch 的 Monte Carlo 平均估计每个 memory worker 对 final reward 的贡献。它解释的是内部 memory pipeline 如何训练，不是 task Subagent 之间共享 memory；但提醒回流质量不能只把最终 reward 平均分给所有阶段。

## 方案比较

| 路线 | 保留来源 | 谁决定晋升 | 复用粒度 | 主要失败 |
|---|---:|---|---|---|
| Final text | 弱 | Parent 临时判断 | 当前任务 | 摘要丢证据 |
| Structured envelope | 中 | Parent/validator | 结论/工件 | schema-valid falsehood |
| Critic promotion | 中 | central critic | subgoal guidance | 共同偏差 |
| Lineage synthesis | 强 | graph policy | claim/evidence | 图维护与错误 edge |
| Typed artifact | 强 | compiler+contract+replay | rule/skill/subagent | case-bounded过拟合 |
| Worker credit | 实验 trace | RL credit | pipeline policy | 分支采样成本 |

## 安全、压缩与失败模式

[State Contamination](https://arxiv.org/abs/2605.16746)显示 compression 会把显式 toxic text 变成 detector-clean 但仍有行为影响的 summary；pre-summary sanitization 比只清洗结果摘要更有效。[MPBench](https://arxiv.org/abs/2606.04329)进一步区分 explicit、standing-policy、compaction、experience-to-procedure 四条写入 channel，说明“自动学技能”是高影响写入口。

## 当前研究在改变什么

前沿正从“每个 Child 返回一个摘要”转向 evidence envelope、candidate zone、typed artifact 和 replay admission。仍缺跨任务 preservation set 怎样构造、critic/validator 被污染时如何恢复、以及来源/权限在模型蒸馏成 procedure 后能否继续撤销。


## 证据账本绑定

主流 Child→Parent 回流仍以最终文本、ToolMessage、普通 state update 或共享工件为主；带来源、验证、replay 和候选晋升的回流协议存在于特定系统，但尚未成为 runtime 默认。
<!-- synthesis:SY-C05 claims:R5-C001,R5-C004,R5-C007,R4-C018,R4-C020 clusters:SM-C05 -->
