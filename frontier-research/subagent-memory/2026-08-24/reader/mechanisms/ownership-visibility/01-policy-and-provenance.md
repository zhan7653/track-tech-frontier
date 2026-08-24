# 所有权与可见性：从 Namespace 到派生权限

## 问题与状态模型

共享 memory 的权限不是一列 `owner_id` 就能表达。一个记录可能由 Agent A 根据用户 U 的文件生成，经 Agent B 摘要，再被 Agent C 用于外部 action。读取权限、来源信任和行动授权是三个不同判断。

最小记录可表示为：

```text
record = content
       + writer_agent / principal / task / project / tenant
       + source resources and derivation parents
       + valid time / observed time / status
       + read policy / write policy / action constraints
```

## 方案族及内部流程

### Flat namespace / per-agent store

每个 Agent 或用户有独立 store，检索自动限定 namespace。隔离直观，但共享需要复制或另建 team store；复制后来源和撤销容易断链。将 `user_id` 仅当物理分区，也无法表达同一群聊中“相同事实由不同 speaker 陈述、对不同 asker 含义不同”。

### Private/shared 双层与动态 policy graph

[Collaborative Memory](https://arxiv.org/abs/2505.18279)维护 private user fragments 和 cross-user shared fragments，并用随时间变化的 user–agent、agent–resource 二部图决定当前可见性。read policy 先筛 admissible fragment，再可变换输出；write policy 决定保留、共享、匿名化或改写。fragment 保存 contributing agents、resources 和 timestamp，支持回溯权限。

其公开实验使用合成多用户 MultiHop-RAG 场景，因此能说明机制怎样工作，不能证明真实组织权限长期正确。

### Hierarchical scope 与 credential capability

Fleet service 常用 agent-local、team/fleet、tenant-global、restricted 多级 scope。请求身份可能来自 tenant key、agent-scoped key 或 runtime header；每条 read path 都必须应用相同 predicate。

[Governed Shared Memory](https://arxiv.org/abs/2606.24535)的 dated live-service study 展示了关键反例：系统能够解析 agent identity，但 GET-by-id handler 曾只检查 tenant，忽略 fleet/agent/scope；搜索 path 又有不同过滤行为。修复一个 handler 不等于所有 read/update/delete path 一致。权限测试必须覆盖按 ID 读取、搜索、批量导出、订阅和派生对象。

### Lineage-aware admissibility

若摘要来自不可见父记录，只检查摘要本身的 owner 会造成 provenance laundering。[MAP-Graph](https://arxiv.org/abs/2608.10509)把 agents、sources、memories、claims、actions 建成 typed execution graph：先执行 hard permission filtering，再沿 ancestry 传播 trust，最后按 action risk 决定 allow/reverify/redact/block。

关键区分是：permission 是 hard eligibility，trust 是 graded ranking，action gate 是 use-time authority。其消融显示移除 permission 可提高表面 utility，却使 conditional unauthorized access 上升；下游 gate 不能撤销已经发生的越权读取。

### Transactive ownership

不把所有知识复制到中央 store，而是保留各 Agent 私有 artifact，团队只维护“谁/哪个 artifact 可能知道什么”的目录。consumer 按需读取并重新判断 scope。这保留多样性和局部所有权，却把目录陈旧、producer 可用性和跨 Agent 信任变成新问题。

## 方案比较

| 路线 | 共享方式 | 权限检查点 | 派生传播 | 主要失败 |
|---|---|---|---|---|
| Per-agent store | 显式复制 | namespace | 弱 | 孤岛/复制漂移 |
| Private/shared | 发布 shared fragment | read/write policy | provenance metadata | 权限变更后的旧派生 |
| Hierarchical scope | 同一服务多 scope | 每个 API path | 取决于实现 | handler 不一致 |
| Lineage graph | 共享 typed graph | eligibility+trust+gate | 强 | 建图与递归成本 |
| Transactive | 目录+按需取回 | consumer 重新判断 | artifact-dependent | 目录陈旧与可用性 |

## 评测和失败边界

[GateMem](https://arxiv.org/abs/2606.18829)将 utility、access control、active forgetting 联合起来，包含 91 个多方 episode 和 2,218 个 hidden checkpoint；它测的是 agent-facing non-recovery，不是底层物理擦除。[GroupMemBench](https://arxiv.org/abs/2605.14498)进一步表明 speaker identity、thread structure 和 audience vocabulary 会改变答案，flat user namespace 不够。

## 当前研究在改变什么

最新路线把 scope 从检索 filter 提升为全生命周期 invariant，并让 derivation 参与权限。仍缺统一主体标识、跨 runtime scope mapping、完整 API surface 审计，以及 revoke/delete 穿过摘要、技能和 side effect 的证据。
