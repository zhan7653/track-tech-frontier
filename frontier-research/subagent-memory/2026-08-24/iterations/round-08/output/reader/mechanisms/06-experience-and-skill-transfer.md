# 群体经验与技能迁移

## 问题

Agent 团队希望避免重复探索，但过去轨迹包含模型习惯、工具版本、权限、偶然成功和失败条件。直接共享“成功步骤”可能把局部捷径变成群体偏差。

## 主要方案族

### Central trajectory repository

Producer 提交完整或压缩轨迹，consumer 按任务/utility 检索；MATM 使用 consumer-specific features/LTR，而非只做语义相似度。

### Decentralized per-agent pools

每个 Agent 保留自身 exploitation/exploration 经验并动态路由，降低集中协调与同质化；DecentMem 属于这一方向。

### Critic-filtered circulation

强模型或集中 critic 评估完成轨迹，只发布可复用 guidance；CoMIC 是 central-critic/decentralized-execution 实例。

### Card/graph 与 cross-model distillation

ConMem 把成功/失败策略变成 signed card graph；MemCollab 对比 preferred/unpreferred 轨迹，提炼 enforce/avoid constraint。

## 数据流、实现、成本与信用

经验需要记录谁产生、在哪个任务和环境验证、被哪些后续 Agent 使用、结果如何，以及何时因工具或世界变化失效。[TreeMem](https://arxiv.org/abs/2605.04811)说明多 Agent memory pipeline 本身还面临 builder、summarizer 和 retriever 的 credit assignment。

额外 producer、critic、embedding、LTR 和检索 token 都是成本；若不固定预算，收益无法归因给 memory。实现还要处理 tool/version condition、secret stripping、producer trust、duplicate 和 revoke。

## 失败、最新研究与尚未解决

跨协议性能数字不可直接比较。更多 Agent、更多轨迹、额外 critic 和检索 token 都会改变预算。公开证据还不足以确定群体记忆何时优于保留多样化私有经验，以及怎样安全删除已经被蒸馏进技能的错误。

深入机制见[Trajectory、Card、Constraint 与 Skill](experience-transfer/01-trajectories-cards-and-skills.md)。
