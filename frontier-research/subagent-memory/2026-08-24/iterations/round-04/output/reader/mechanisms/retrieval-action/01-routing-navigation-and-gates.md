# 发现、检索与行动：共享知识怎样到达正确 Subagent

## 问题与读取链路

共享 memory 的读取至少包含：是否知道要查、查哪个 scope/Agent/artifact、怎样产生候选、怎样处理冲突和权限、如何压进 context、能否驱动 action。多数单 Agent benchmark 从“给定 query 检索”开始，跳过了前两步。

## 方案族及内部流程

### 启动注入与 always-loaded memory

runtime 在 Subagent 启动时注入 project rules、memory summary 或 agent-specific file。无需 Agent 主动查询，适合短小关键约束；内容过多会每次付 token，过期内容也持续影响所有任务。summary 应提供“有什么可查”而不是复制全部细节，否则 progressive disclosure失效。

### Pull retrieval：semantic、keyword、field 与 hybrid

Child 根据 task/query 主动 search。semantic 处理改写，keyword/field 处理 identifier、version、Agent、time 和 scope。hybrid 将多个候选面融合。问题是 Agent 可能不知道存在相关记忆，也可能从未发起 search；top-k recall 不测这种 omission。

### Hierarchical/graph navigation

G-Memory先在 query graph 找相似 task，向上取 insight、向下取 sparsified interaction，再按 role 过滤。ConMem 从 card seed 扩展 typed neighbor，协调 conflict/dependency 后压缩。二者都说明多跳不是越多越好：过度 expansion 引入无关 context，协调/稀疏本身是核心算法而非后处理。

### Transactive routing 与 marginal-utility ranking

MATM 将 Agent-generated trajectory 当 corpus。consumer-specific ranker用“注入该 chunk 相对 no-retrieval 是否改善 outcome”作为监督，而不只用文本相关性。这更接近“对这个 consumer 有用”，但标签采集需要大量 branch rollout，且一个 benchmark 上的 marginal utility不自动迁移到权限、模型版本和工具环境变化后的 consumer。

### Push、subscription 与 inbox

pub/sub service 在 key、task 或 topic 更新时通知 Agent；handoff inbox 把定向信息推给下一个 Agent。它解决“Agent 不知道要搜”，同时引入重复 delivery、顺序、backpressure、interrupt timing 和 notification poisoning。subscriber仍需按 current permission 和 base revision验证。

### Permission/trust-aware retrieval

MAP-Graph 先执行 hard eligibility：不允许的 record 不进入模型；再沿 provenance path 计算 graded trust并 rerank。Collaborative Memory 也在 similarity候选前后应用 private/shared policy projection。关键顺序是**先授权、后排序**；把越权内容送给模型再要求不使用，已经发生泄漏。

### Zero-trust path calibration

[EquiMem](https://arxiv.org/abs/2605.09278)在 multi-agent debate 的 shared memory 中，不请求另一个 LLM judge，而利用 Agent 已有 retrieval query和 graph traversal path作为 evidence，结合 local/path consistency与 auditor probe校准 update。论文覆盖 embedding/graph memories、AutoGen/MacNet/DyLAN 和四类任务，并报告低 token/latency；它仍是特定 debate/update game，不能外推为通用 access control。

### Risk-sensitive action gate

同一记忆用于回答和转账应有不同 threshold。MAP-Graph 在 retrieved/context support 上按 risk输出 Allow、Block、Reverify、Redact；MemTX要求 external-action transaction存在 action-safe committed support。gate 是最后一道防线，不能撤销越权读取，也不能修复已经执行的 side effect。

## 方案比较

| 路线 | 解决“何时查” | scope/权限 | budget | 主要失败 |
|---|---|---|---|---|
| 启动注入 | 自动 | 静态 | 固定成本 | stale/过宽 |
| Pull hybrid | Agent 决定 | 可 filter | top-k | 不发 query |
| Graph navigation | seed 后扩展 | 可编码 | 协调压缩 | 错 edge/过扩展 |
| Transactive | 先找 artifact/producer | consumer判断 | trajectory 长 | 目录陈旧 |
| Push/inbox | 主动通知 | subscription ACL | interrupt | 重复/污染 |
| Trust-aware | query后控制 | hard+graded | graph cost | lineage缺失 |
| Action gate | use-time | 重新授权 | risk tier | 读取已泄漏 |

## Benchmark 边界

[GroupMemBench](https://arxiv.org/abs/2605.14498)测 speaker-grounded、threaded、audience-adapted group memory，最强系统平均仍仅 46%，BM25匹配/超过多种 memory system；它说明 ingestion/retrieval会抹掉 speaker与词义结构。[GateMem](https://arxiv.org/abs/2606.18829)则把合法 utility、拒绝越权和 deletion non-recovery联合评估。两者与 MATM、G-Memory、MAP-Graph 的 task/metrics完全不同，不能拼总榜。

## 当前研究在改变什么

前沿从 top-k similarity 转向 role/consumer-specific routing、graph coordination、permission-before-ranking 和 action-time evidence。仍缺端到端测量“是否知道该查”、push/pull取舍、跨 Agent source re-authorization，以及检索失败如何触发 targeted clarification而非自信行动。
