# 成本、可靠性与可观测性：多一层 Memory 就多一组状态机

Subagent Memory 的成本不只来自向量检索。Parent 要编译任务包，Child 可能重复探索，结果要结构化、验证、合并、索引、通知、压缩和清理；事务、critic、reranker 与 repair 又会增加模型调用和存储写放大。

## 成本拆解

| 阶段 | 主要成本 | 可见收益 | 隐藏成本 |
|---|---|---|---|
| Spawn | history filter、summary、snapshot、sandbox | Child 更快进入任务 | 漏信息导致返工；full history token 膨胀 |
| Execute | tool/model、checkpoint、workspace | 并行降低墙钟 | 总 token、重复检索和外部 API 调用增加 |
| Return | structured envelope、artifact、evidence | Parent 更易判断 | Child 为报告而额外生成内容 |
| Commit | schema、conflict、critic、transaction | 降低污染与 lost update | 延迟、validator 错误、重试与锁竞争 |
| Retrieve | index、embedding、graph、rerank | 发现已有知识 | stale index、过量上下文、consumer drift |
| Maintain | compaction、supersession、delete、repair | 控制长期规模 | 派生图、缓存和备份写放大 |

并行只保证可能降低 wall-clock，不保证降低总计算。评估必须同时报告 latency、total model calls、total tokens、tool calls、storage/embedding writes 和失败重试。

## 可靠性失败不是一种

### Namespace 与身份

LangGraph 的 thread id/namespace、OpenAI Sandbox 的 memories/sessions layout、AutoGen 的 participant name、Codex 的 AgentPath/root role各自决定状态归属。名称复用、布局部分重叠、不同 team 结构或同名并行调用都可能把“恢复”变成“串线”。

### Snapshot 不一致

AutoGen Team snapshot 不包含外部 Memory 内容；LangGraph checkpoint 与跨 thread Store 是两层；共享 workspace 还可能包含已经改变的文件。恢复一个 coordinator，并不证明它依赖的 memory/database/filesystem处于同一时刻。

### 并发与幂等

Statewave demo 需要进程内 lock 串行 post→compile→diff；memX 用 WATCH/MULTI 避免 lost update，却用 LWW 丢弃 loser 语义；PatchBoard 验证临时 state 后事务提交；MemTX 进一步检查 dependency stability。它们解决的是不同并发层，不能互相替代。

### 外部 side effect

Checkpoint 可重放 graph node，不会自动让邮件、支付、shell 或远程 API 幂等。Memory repair 能修订 belief，也不自动补偿已经发生的行动。高风险系统必须把 action idempotency/compensation 作为独立日志和 gate。

## 可观测性的最小 trace

每次跨 Agent 状态转移至少应能回答：

```text
who: agent / parent / user / tenant
why: task / goal / policy / write authority
read: source versions, namespace, projection and permissions
write: candidate type, base version, patch/value/artifact
decision: accepted, contested, quarantined, superseded or rejected
consumer: which later agent/retrieval/action used it
cleanup: retention, revoke, delete and repair status
```

只有 final transcript 无法定位 Child 输入不足、共享状态陈旧、冲突覆盖、检索漏召回或行动误用。只有 database audit 也不够，因为问题可能在 spawn message、application context 或 shared file。

## 工程实现给出的现实约束

- OpenAI Agents SDK Phase 2 consolidation 与 task Agent 共用 sandbox resource，且 summary 仍有 token 成本；
- Deep Agents 的 shared backend 让工件交换简单，也要求应用处理并行写和 reducer；
- UFO 全量序列化 Blackboard 与 screenshots，成本随历史线性增长；
- Caura 的 strong/fast/STM 以不同 latency/治理保证换取吞吐；
- MATM 的 consumer-specific ranker增加 feature/ranker维护与模型漂移；
- memX 很轻，但省略 history、conflict、provenance 与跨进程 fan-out。

不存在免费拓扑：简单系统把复杂度推给应用和事故处理，治理系统把复杂度前置到 control plane。比较时应把“未实现的保证”也算入采用成本。
