# 01 输入层：哪些运行记录进入 Memory

## 结论

输入层处理 Agent 已经做过的工作：对话、工具调用、工具结果、文件或环境观察，以及线程的范围信息。它不判断一条内容最终是否应写成长期知识；它提供后续判断所需的材料，并排除不应送入该流程的内容。

Codex 已经把这一层做成后台、按线程运行的流水线。它不会在每次回答后立刻把聊天保存为 Memory。一个后续的合格 root session 启动时，系统才从近期已空闲线程中认领候选，读取 rollout，过滤运行控制和规则注入内容，做秘密清理与长度控制，再交给 Phase 1 抽取。这个设计的读者可见结果是：刚完成的任务未必立刻出现在 Memory；长期规则仍应写在 `AGENTS.md` 等权威文件中；一段没有进入候选的历史，后续阶段无法凭空恢复。

```text
root session 启动
  → 筛选近期且空闲的 root rollout
  → 读取 rollout JSONL 与 thread 元数据
  → 过滤、脱敏、截断
  → Phase 1 逐线程抽取
  → 候选记忆与来源定位进入 stage1_outputs
```

这里的“输入”与“最终记忆”要分开看。rollout 是任务发生过程的原始记录；Phase 1 的 `raw_memory` 是模型生成的候选；`MEMORY.md` 则是后续巩固后的可读手册。三者用途不同，不能互相替代。

## Codex 的真实输入数据流

本章的 Codex 锚点是公开仓库的固定快照 [`c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)，观察日期为 2026-08-23。代码能够证明组件、默认值和控制流；它不能证明每个托管客户端都使用相同配置。

Memory startup 在新的 root turn 开始时异步触发。`codex-rs/memories/write/src/start.rs` 会直接跳过 ephemeral session、未启用 Memory 功能的运行和 non-root agent session；随后调用 state 层领取可处理的历史线程，并依次运行 Phase 1 与 Phase 2。也就是说，Subagent 私有 trace 不会独立成为长期 Memory 的输入；但它发回 root thread 的 `InterAgentCommunication`，仍可能作为 root rollout 的一部分被保留。

候选选择发生在 `codex-rs/state/src/runtime/memories.rs`。系统依据 thread source、归档状态、`memory_mode`、更新时间和 idle cutoff 筛选，并排除当前线程；它还用 Memory 数据库中的 watermark 和 lease 判断是否已处理或正被其他 worker 处理。固定版本的默认行为如下：

| 默认项 | 值 | 对读者意味着什么 |
|---|---:|---|
| `max_rollout_age_days` | 10 天 | 很久以前的线程不会在这轮后台扫描中自动补写 |
| `min_rollout_idle_hours` | 6 小时 | 正在持续工作的线程暂不进入抽取 |
| `max_rollouts_per_startup` | 2 | 一次新启动只处理少量历史任务 |
| Phase 1 最大并发 | 8 | 配置调高候选数后可并行抽取，但不改变候选资格 |
| `min_rate_limit_remaining_percent` | 25% | 额度较低时可跳过后台形成 |

这些数值来自开源默认配置，不能当作产品 SLA。它们解释了一个常见现象：用户修正了内容后，系统不会同步刷新长期 Memory，必须等待线程空闲并遇到后续合格启动。

### 一条 rollout 如何被准备

`codex-rs/memories/write/src/phase1.rs` 读取 rollout JSONL，按 `RolloutItem` 类型选择可用内容。对 Memory 有价值的通常包括用户和 Agent 的消息、工具调用及其结果、root thread 内的 Agent 间通信。下面用一段简化的支付项目记录展示这个筛选：

```text
thread_id: T-1842
cwd: /work/payments
git_branch: fix/refund

1. user: “退款集成测试需要先跑 integration suite”
2. tool: cargo test -p payments --test refunds
3. result: fixture 仍使用旧字段 refund_status
4. assistant: “先更新 fixture，再重新运行测试”
5. AGENTS.md 注入：发布必须走内部流程
6. Compacted marker
```

| 记录 | Phase 1 处理 | 原因 |
|---|---|---|
| 用户的测试要求 | 保留 | 可能减少未来重复沟通 |
| 命令和失败结果 | 保留 | 是项目经验的直接证据 |
| Agent 的修复步骤 | 保留 | 可形成失败屏障或流程候选 |
| Developer、完整 `AGENTS.md`、Skill 注入块 | 排除 | 这些内容已有权威来源，不应被模型重写成漂移副本 |
| `Compacted` 与部分 runtime metadata | 排除 | 它们控制当前运行，不描述可复用经验 |
| secret/token | 脱敏 | 避免敏感字符串进入模型输入和候选输出 |

长 rollout 还会经过上下文预算。`prompts.rs` 按 active model 的有效 context window 估算预算，并把约 70% 分给 rollout；缺少元数据时退回 150,000 token 上限，截断逻辑保留头尾。这能降低单次抽取失败，但任务中段的决定、反复试验或用户纠正仍可能不在请求中。公开的 [#38860](https://github.com/openai/codex/issues/38860) 报告过旧版本的 context-window failure；它是用户报告，不表示当前所有版本都有同样故障，但说明输入覆盖率必须按 rollout 长度和版本审视。

### Phase 1 交出什么

抽取模型返回严格 JSON：

```json
{
  "rollout_summary": "退款集成测试的失败原因与修复路径",
  "rollout_slug": "refund-fixture",
  "raw_memory": "在 /work/payments 中，退款测试先运行 integration suite；旧 fixture 的 refund_status 字段会导致失败，更新 fixture 后重跑。"
}
```

输出被写入 `memories_1.sqlite` 的 `stage1_outputs`。`raw_memory` 的名称容易造成误解：它是模型从原始材料中写出的较详细候选，并非原始对话。原始证据仍由 `rollout_path` 指向的 JSONL 保存。候选行同时带有 thread ID、source watermark、生成时间和后续使用统计，因此后面的阶段能定位来源和判断是否需要重做。

默认 OpenAI provider 让 Phase 1 使用较轻的 `gpt-5.6-luna`（low reasoning effort），Phase 2 使用 `gpt-5.6-terra`（medium）。这是一种明确的成本分层：大量单线程筛选使用较轻模型，低频全局巩固才使用更强模型。模型和 effort 可被配置覆盖。[provider defaults](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/model-provider/src/provider.rs#L126-L169)

## 从 Codex 抽出的通用结构

Codex 的实现给出四个可复用动作：

| 动作 | Codex 中的实现 | 需要解决的问题 |
|---|---|---|
| 触发 | 后续 root turn 的后台 startup | 避免每个 turn 都付出形成成本 |
| 发现 | state DB 按 source、idle、age、mode 选择 | 找到可能有价值且已稳定的经历 |
| 准备 | item filter、secret redaction、context budget | 将控制信息和敏感信息隔在抽取输入之外 |
| 交接 | Phase 1 JSON + `stage1_outputs` | 把原始经历变成可调度、可定位的候选 |

其他产品可在每 turn、session end 或显式 `add()` 时触发，但仍需要回答相同问题：事件来自哪里，谁允许它进入，原始证据在哪里，哪些内容不能交给形成模型。输入层保存得越少，成本和污染面越小；保存得越少也意味着之后无法回放或重新抽取被丢弃的信息。

## 近期补充：输入开始携带更强的状态信息

近半年的研究把重点放在输入进入状态系统时携带更完整的来源、范围与治理信息。

### 系统测量：把 ingestion 从隐形成本变成单独阶段

[Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads](https://arxiv.org/abs/2606.06448)（2026-06，预印本）把系统拆为 ingestion、construction、storage、retrieval、prompt assembly、generation 与 maintenance。它解决的是过去只看回答质量或读时 token、看不见写入成本的问题：原始日志保留、向量构造和 LLM 抽取会把成本放在不同阶段。论文给出的是统一 harness 下的测量框架；它没有给出某一种输入策略的普适胜负结论。

对 Codex 而言，这提醒读者不能只问“Phase 1 生成了什么”，还要问“每次 startup 认领多少 rollout、截断丢了什么、抽取和失败重试消耗多少”。Codex 已有 rate-limit guard、候选上限和分层模型；公开代码没有显示一套面向用户的全生命周期成本账本。

### 治理化 ingestion：候选带类型、策略和依赖进入状态

[Is Agent Memory a Database?](https://arxiv.org/abs/2605.26252)（2026-05，预印本）提出 GEM/MemState，把 ingestion、revision、forgetting 和 retrieval 描述为受策略约束的状态操作，并使用 typed dependencies。它关注候选的主体、项目和权限范围为何成立。其原型强调内容、结构和演化策略共同进入状态；尚未成为通用 runtime 接口。

[MAP-Graph](https://arxiv.org/abs/2608.10509)（2026-08-11，arXiv 预印本）进一步把 provenance 用于权限和行动风险，而不仅用于事后审计。放到输入层，含义是候选除了正文，还应保留 producer、来源链和 scope，后面的读取与行动才能按来源做限制。Codex 已保留 thread、cwd、branch 与 rollout path，却主要靠全局文件中的文本组织 scope；它还没有把 provenance 发展为强制的读取权限图。

一个具体例子：Subagent A 从内部仓库得到一条“可以删除旧账单”的建议，Subagent B 从网页得到相同措辞。两条输入都进入共享池时，MAP-Graph 方向会保留类似下面的字段：

```json
{
  "claim": "delete legacy billing rows",
  "producer": "subagent-a",
  "source": "repo://billing/commit/91f3",
  "scope": "tenant-7/project-payments",
  "purpose": "maintenance",
  "action_risk": "high",
  "derivation": []
}
```

查询时，来自网页的记录可能因为 scope、信任或 action risk 检查被排除；来自内部 commit 的记录可以进入候选，但仍需当前权限和当前代码状态复核。Codex 当前的 rollout path、cwd、branch 和 citation 能支持回查，却没有在读取 API 层执行这套 provenance gate。这就是近期输入机制给成熟架构增加的具体字段和控制点。

## 当前边界

- Codex 的后台延迟降低了在线成本，也延迟了用户纠正进入长期状态的时间。
- context budget 和 item filter 建立了明确边界；过滤掉的材料不能由后续巩固自动找回。
- secret redaction 是必要保护，但无法证明所有敏感业务事实都不会进入候选。
- 线程 metadata 提供 project 线索，Memory root 和摘要仍是全局物理空间，项目隔离主要依赖后续文本路由。
- Subagent 独立 trace 不进入同一 writer，root thread 是否保留其结果取决于通信是否回流。

下一章从这里继续：Phase 1 候选如何被合并、忽略、更新或写入长期 Memory。
