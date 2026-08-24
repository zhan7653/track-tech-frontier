# 群体经验与技能迁移

## 问题

Agent 团队希望避免重复探索，但过去轨迹包含模型习惯、工具版本、权限、偶然成功和失败条件。直接共享“成功步骤”可能把局部捷径变成群体偏差。

## 主要方案族

- **Central trajectory repository：** producer 提交完整或压缩轨迹，consumer 按任务检索；代表性思路是 [Multi-Agent Transactive Memory](https://arxiv.org/abs/2606.19911)。
- **Decentralized per-agent pools：** 每个 Agent 保留自身经验并动态探索，降低集中协调与同质化；[DecentMem](https://arxiv.org/abs/2605.22721)属于这一方向。
- **Critic-filtered circulation：** 强模型或集中 critic 评估完成轨迹，只发布可复用 guidance；例如 [CoMIC](https://arxiv.org/abs/2606.00756)。
- **Structured memory cards/graphs：** 把策略、线索、依赖和冲突组织成可组合对象；例如 [ConMem](https://arxiv.org/abs/2606.08702)。
- **Cross-model distillation：** 对比多个模型轨迹，提炼共享约束而不是复制表面 reasoning；例如 [MemCollab](https://arxiv.org/abs/2603.23234)。

## 信用与生命周期

经验需要记录谁产生、在哪个任务和环境验证、被哪些后续 Agent 使用、结果如何，以及何时因工具或世界变化失效。[TreeMem](https://arxiv.org/abs/2605.04811)说明多 Agent memory pipeline 本身还面临 builder、summarizer 和 retriever 的 credit assignment。

## 尚未解决

跨协议性能数字不可直接比较。更多 Agent、更多轨迹、额外 critic 和检索 token 都会改变预算。公开证据还不足以确定群体记忆何时优于保留多样化私有经验，以及怎样安全删除已经被蒸馏进技能的错误。
