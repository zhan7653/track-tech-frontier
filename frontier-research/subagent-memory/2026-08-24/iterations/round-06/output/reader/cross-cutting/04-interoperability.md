# 互操作与集成：Transport 兼容不等于 Memory 语义兼容

Runtime session、application context、handoff item、Agent message、MCP resource/tool、workspace snapshot、checkpoint、Store document 和 memory record 都能携带状态，但它们不共享相同的主体、寿命、权限、版本和提交语义。

## 当前常被混在一起的层

| 层 | 例子 | 它保证什么 | 它不保证什么 |
|---|---|---|---|
| Orchestration | spawn、handoff、agent-as-tool | 把控制或任务交给另一个 Agent | 长期状态、workspace 隔离、可信提交 |
| Model context | messages、summary、input_items | 当前推理可见内容 | Session 是否保存、外部 store 是否同步 |
| Runtime state | application context、graph state | 程序字段随运行传播 | 主体权限和跨 session durability |
| Durable execution | checkpoint、snapshot | interrupt/resume/replay | 外部 side effect 幂等、长期知识正确 |
| Artifact/workspace | files、patch、sandbox image | 共享或隔离工程状态 | 语义冲突、来源和读写授权 |
| Long-term memory | Store、vector/graph/row | 跨调用检索持久记录 | 谁可行动、如何回流、如何撤销 |
| Transport | MCP/A2A/REST/pub-sub | 远程调用和数据交换 | 两端对 scope/version/delete 的同义理解 |

## 固定代码里的不对称

OpenAI Agents SDK 的 handoff filter 对 client-managed history生效，但 server-managed conversation没有同样路径；Deep Agents 可把 `/memories/` 路由到持久 StoreBackend，同时 child message context仍是临时的；AutoGen Team save/load与 external Memory lifecycle分开；LangGraph checkpoint和 Store分别解决 thread恢复与跨 thread数据。

这些不是实现缺陷，而是层次边界。集成失败来自应用误以为一个层的成功自动覆盖另一个层。

## 一个真正可 round-trip 的 Memory envelope

跨 runtime 交换至少需要下列语义，而不仅是 JSON：

```text
record_id / version / base_version
subject: agent, task, project, user, tenant
type: observation, claim, artifact, decision, trajectory, skill
content or content reference
writer and write_authority
source lineage and timestamps
visibility / capabilities / purpose
status: candidate, committed, contested, superseded, revoked
conflicts and dependencies
retention / delete / repair semantics
```

接收端还要返回 accepted/rejected/contested、local version、scope projection 和 unsupported capability。否则发送端无法知道状态是否真的成为对方可检索、可行动或可删除的记忆。

## Identity mapping 是核心难题

Codex AgentPath、AutoGen participant name、LangGraph thread/namespace、Sandbox layout、Caura tenant/fleet/agent、MCP connection identity不是同一主体。一个 gateway 如果只映射字符串名称，会把 runtime instance、角色、项目和用户混在一起。

可用的映射应区分：稳定 principal、临时 Agent instance、task/run、project/workspace、用户/租户，以及 delegated capability。映射变化还要触发旧记忆的权限复核，而不是仅修改 display name。

## Conflict 与删除也必须协商

一端的 `put(key,value)` 可能表示 LWW 当前值，另一端的 append可能表示不可变事件，第三端的 patch可能需要 base version。若 adapter 默认为覆盖，StateFuse/LatticeMind一类 conflict surface会在跨系统时消失。

删除同样有多种含义：停止召回、tombstone、物理删除、撤销授权、重建 embedding、修复 derived skill。协议只提供 DELETE endpoint，不代表下游 cache、summary 或 side effect 已经清理。

## 当前判断

现有框架已经具备丰富连接 primitive，但尚未形成跨 runtime 的 Subagent Memory capability negotiation 和一致 round-trip 语义。短期最实际的集成方式是明确 adapter contract：列出 identity、scope、version、conflict、return、delete 和 action gate 中哪些得到支持，哪些必须由 Parent 或外部 control plane承担。
