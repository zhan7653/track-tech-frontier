# 所有权、命名空间与可见性

## 问题

共享记忆必须回答“这是谁的状态”。用户偏好、Agent 私有反思、任务假设、项目决策和 fleet 规则的传播范围不同。只在检索后让模型判断归属，会把越权内容先暴露给模型，也无法可靠执行撤销。

## 主要方案族

- **Per-agent store：** 隔离强，跨 Agent 复用依赖显式复制或检索。
- **Private/shared 双层：** 写入时决定保留私有还是发布共享；难点是后续权限变化和派生摘要。
- **Task/project/team namespace：** 通过 namespace 或路径限定有效范围；需要处理 Agent 同时属于多个范围。
- **Policy graph：** 把 user、agent、resource 与动态 read/write policy 建模，能够表达非对称和随时间变化的权限。
- **Transactive directory：** 不集中复制全部知识，而是记录哪个 Agent 或 artifact 可能知道什么，再按需获取。

[Collaborative Memory](https://arxiv.org/abs/2505.18279)展示了动态权限投影，[GateMem](https://arxiv.org/abs/2606.18829)把多主体授权和 active forgetting 放入评测，[Governed Shared Memory](https://arxiv.org/abs/2606.24535)则提供 fleet 级 scoped retrieval 的工程案例。

## 尚未解决

写入时权限、读取时权限和行动时权限可能不同。来源被摘要、合并或蒸馏后，权限是否随 derivation 传播仍缺少统一语义；多 runtime 之间的 agent/task/project 标识也不稳定，使跨系统 scope mapping 容易失真。
