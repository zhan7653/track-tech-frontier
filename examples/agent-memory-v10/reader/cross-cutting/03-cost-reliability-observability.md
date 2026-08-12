# 成本、可靠性与可观测性：Memory 的代价不止是多花了多少 Token

长期 Memory 经常被描述为“节省上下文”，但它也会增加抽取、嵌入、索引、版本、远程服务、重建和事故修复的成本。更重要的是：每一次异步写入、摘要更新或索引迁移，都可能让 Agent 在某段时间读到不完整、陈旧或不可解释的状态。于是成本、可靠性和可观测性不是运行后的附加层，而是贯穿 `write → manage → read → act` 的系统属性。

## 五本账和一条可解释链路

```text
write               manage                  read                    act
事件 ─► capture ─► projection/index ─► retrieve/compile ─► tool/action
  │        │            │                     │                 │
  └── 延迟、失败 ───────┴── 存储、重建 ───────┴── token、p95 ───┴── 成功/副作用
                       ▲                                              │
                       └──── trace、版本、水位线、fallback ───────────┘
```

应区分的账目是：

| 账目 | 发生位置 | 典型组成 | 只看 Token 会漏掉什么 |
|---|---|---|---|
| 建造成本 | write/manage | 抽取、LLM 摘要、embedding、实体/图构建 | 异步积压、重复写入与失败重试 |
| 在线读成本 | read | 过滤、检索、多路候选、rerank、远程调用 | p95 抖动、权限检查和 fallback |
| 编译成本 | read | 原始证据/派生摘要选择、上下文和工具输出 | answer reserve 被挤压、source loss |
| 持久化成本 | manage | raw、派生对象、索引、revision、备份 | 迁移、re-embed、删除后重建 |
| 运行与事故成本 | 全链路 | telemetry、审计、隔离、回滚、人工核查 | capture gap、陈旧 cache、污染传播 |

这不是一个统一计价公式。不同模型价格、存储后端、数据寿命和任务风险使“总成本”无法直接横比；但把这些账目分开，才能看见所谓节省究竟转移到了哪里。

## 可靠性不是单一可用率

| 可靠性维度 | write | manage | read | act |
|---|---|---|---|---|
| 完整性 | 事件是否捕获、来源是否齐全 | 派生物是否覆盖原始证据 | 是否取到应有证据 | 是否基于完整/正确证据行动 |
| 新鲜度 | 新事件何时可见 | 索引/摘要水位线是否追上 | 是否尊重 `as-of` 和版本 | 是否仍遵循旧规则或状态 |
| 一致性 | 重试是否重复写入 | 多写者冲突、版本迁移 | 查询是否跨越不一致快照 | 外部副作用能否与记忆版本关联 |
| 可恢复性 | 写入失败能否重放 | 是否可重建、回滚、删除派生物 | fallback 是否有来源边界 | 失败后是否能停止或补偿 |
| 可解释性 | 为什么收下/拒绝一条记录 | 哪个模型/提示生成了摘要 | 为什么它被选入 prompt | 哪个 memory 影响了工具调用 |

`OpenViking` 的工程形状很具体：资源进入后由异步处理生成分层描述与索引，调用方需要等待处理完成或接受短时不可语义检索。这是“projection lag 是 API 合同”的实例，不是其延迟或质量的性能证明。[OpenViking](https://github.com/volcengine/OpenViking)

`claude-mem` 以 host hooks 捕获会话，worker 失效时采用 fail-open；它优先保证宿主不被阻塞，却也意味着 capture completeness 不能被假定为 100%。这正是可用性和记忆完整性会分离的例子。[claude-mem](https://github.com/thedotmack/claude-mem)

本地加密实现 `Compartment` 还展示了另一种取舍：解锁后在内存 SQLite 中做 FTS、向量和融合检索，embedding 模型变更需要显式 re-index/re-embed，容量会作用到启动和内存占用。它说明“本地”不等于没有运行成本。[Compartment](https://github.com/maxfreedompollard/compartment)

## 为什么压缩的收益常被误判

从原始对话生成摘要或结构化记忆，可能减少 prompt token，却增加 write-time LLM 调用、派生存储、索引和重建。一旦候选召回不足，短 prompt 只是更快地给出错误答案。对 LightMem 的独立复现显示，固定构造记忆库后，retriever 和 answer-token cap 可以改变结论：匹配 retrieval depth 时 raw-turn Naive RAG 通常更强，紧答案预算下构造记忆才较有利。[Reproducing LightMem](https://arxiv.org/abs/2607.29104)

因此“tokens saved”是局部观测量。更有解释力的是从 `source bytes → derived bytes → index bytes → candidate tokens → compiled tokens → action outcome` 的漏斗，并把每一级的版本、时间、水位线和错误一起记录。

## 可观测性的最小语义单元

不需要公开原始私密内容才能描述一条 Memory 的旅程。一个可关联的 trace 至少可记录：

| 记录 | 用途 |
|---|---|
| source / principal / scope / event time | 说明谁的何种信息在何时进入系统 |
| memory 与 revision 标识、predecessor | 解释更新、冲突、删除与回滚 |
| derivation | 原始片段、摘要、embedding、技能之间的依赖 |
| policy decision | 为什么准入、拒绝、遮蔽或降级 |
| retrieval and compilation trace | query、过滤、候选、排除原因、token 分配、watermark |
| action linkage | 被模型实际使用的证据、工具调用、结果与补偿 |
| cost and timing | write/read/compile 的 p50/p95、LLM 调用、远程依赖、重试 |

其中 `watermark` 是“系统已处理到哪一个事件/版本”的明确标记。没有它，异步队列或最终一致索引让“刚写入却找不到”看起来像模型不记得，实际可能只是尚未可读。

## 当前主流、近期变化与证据边界

当前工程主流是把向量检索、摘要/压缩和基础日志组合起来；较成熟的是单一后端内的延迟、错误和资源监控。仍不成熟的是跨原始/派生状态的完整谱系、跨后端的统一费用账本，以及把 action outcome 反向归因到一条被编译的 Memory。

近 12 个月的明显变化是 context compiler 从“把 top-k 拼到 prompt”变成单独的预算与可观测性表面：分层选择、异步投影、会话 hooks、可替换评测后端都在出现。近 90 天的信号包括把插件 lifecycle、backup/restore 和安全生命周期放进 harness；这说明可靠性开始进入 benchmark，但还不能推出某一架构已经可靠或低成本。[OmniMemEval](https://github.com/MemTensor/OmniMemEval)

已知反证是：作者协议中的 token 或 memory-usage 改善，不可自动推断为端到端成本下降；单次平均延迟也掩盖冷启动、重建、队列积压和远程服务尾延迟。缺少的是同一任务流、同模型、同预算下对 raw、选择性 raw、构造记忆和结构化/版本化记忆的独立全成本复现。

## 未解问题

仍需回答：多写者和异步投影下，何种一致性语义足以支撑行动；删除/撤销后如何证明所有派生物都已失效；embedding 或模型迁移时如何测量语义漂移；以及如何在不暴露敏感文本的前提下保留可审计的行动归因。这些问题决定了“系统看起来可用”是否能被解释为“状态可依赖”，而不是优化某个仪表盘数字。

## 证据与阅读边界

- 压缩收益的协议反证：[Reproducing LightMem](https://arxiv.org/abs/2607.29104)。
- 异步分层处理的工程实例：[OpenViking](https://github.com/volcengine/OpenViking)。
- Hook 捕获与 fail-open 的工程实例：[claude-mem](https://github.com/thedotmack/claude-mem)。
- 本地加密、混合检索与 re-embed 边界：[Compartment](https://github.com/maxfreedompollard/compartment)。
- 插件生命周期评测：[OmniMemEval](https://github.com/MemTensor/OmniMemEval)。

这些材料说明系统形状与证据边界，不构成成本预测、SLO 或部署选择建议。
