# 第 7 章　反馈、经验与持续学习：Memory 怎样越用越好，也可能越用越偏

## 结论

持续学习并不等同于不断追加更多记忆。系统需要把一次使用、一次失败、一次用户纠正或一次环境变化，连接回此前的来源、候选、摘要、流程和技能；然后决定保留、降权、修订、撤回，还是保持不动。

Codex 已经实现了一条很具体但受限的反馈闭环：Agent 使用 Memory 后，在最终回答里给出 citation；解析器从 citation 得到实际使用的 rollout ID，再更新 Phase 1 候选的 `usage_count` 和 `last_usage`；之后的 Phase 2 会在巩固时参考使用与新近程度，重写全局 `MEMORY.md`、摘要、rollout summaries 和 skills。它证明了“使用记录可以进入 Memory 生命周期”，但还没有证明“常被引用的内容更正确”。

第 7 层因此是整套架构的控制中心：它要同时处理效果、成本、错误、自强化、晋升、遗忘、恢复和评测。

## 7.1 Codex 的真实反馈数据流

固定版本代码中的读写闭环可压缩为：

```text
Phase 1：一条 rollout → raw_memory + rollout_summary + rollout_slug
                         ↓
                  stage1_outputs（含来源与使用状态）
                         ↓
新线程读取 memory_summary / MEMORY.md / detailed files
                         ↓
最终回答中的隐藏 Memory citation
                         ↓
citation parser 提取文件行号与 rollout IDs
                         ↓
usage_count + 1，last_usage 更新
                         ↓
Phase 2 选择候选，启动受限 consolidation Agent
                         ↓
重写 MEMORY.md / memory_summary.md / summaries / skills
```

read-path prompt 要求 Agent 在使用 Memory 时给出 citation；`citations.rs` 解析该块，使用 rollout IDs 回写 Stage 1 usage。[citation 解析代码](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/read/src/citations.rs) Phase 2 则是受限的内部 Agent：它处理选中的 Phase 1 候选和 ad-hoc notes，维护文件化 Memory 工件；其任务领取、lease、selection snapshot 和完成状态写入 Memory state DB。[Memory pipeline 说明](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories)

这条链路有三个必须分开的信号：

| 信号 | Codex 能观察到什么 | 它代表什么 | 它不代表什么 |
|---|---|---|---|
| citation / usage | Agent 声称使用了哪些 Memory 来源 | 内容可能对当前回答有帮助 | 内容正确、回答成功或用户满意 |
| 工具结果 | rollout 中的命令、测试或工具返回 | 当时环境下的一个可观察结局 | 该结局能迁移到别的项目/版本 |
| 用户更新 | 显式 remember / update / forget note | 用户提供了需要处理的修订意图 | 已同步删除所有派生内容 |

## 7.2 具体例子：一次使用怎样影响下一轮巩固

下面用一组伪数据展示使用回写的含义；字段名按 Codex 的公开数据流简化，数值为示例。

```text
stage1_output
  rollout_id: T-1842
  raw_memory: "refund fixture uses refund_state; run refunds integration test"
  usage_count: 3
  last_usage: 2026-08-23
  selected_for_phase2: false

本次任务
  当前 cwd: /work/payments
  Agent 读取 MEMORY.md 第 83–89 行
  最终 citation: MEMORY.md:83-89; rollout_id=T-1842

回写后
  usage_count: 4
  last_usage: 2026-08-25

下一次 Phase 2
  将 T-1842 与新候选、用户 notes 一并考虑
  可能：保留、改写、合并到更一般的测试流程，或在新证据冲突时降级/移除
```

`usage_count` 表示的是这条候选被可解析 citation 指向的次数。它有助于 Phase 2 区分从未被采用的冗余内容和反复出现的工作线索，但它没有结果标签：Agent 可以引用错误信息、引用后仍失败，也可能使用了 Memory 却忘记输出 citation。

因此更完整的反馈记录应把“使用”与“后果”分开保存：

| 字段 | 示例 | 用途 |
|---|---|---|
| `memory_ref` | `T-1842`, `MEMORY.md:83-89` | 回到来源和派生材料 |
| `context` | payments / refund test / schema v4 | 判断适用范围 |
| `action` | 更新 fixture，再运行指定测试 | 观察行为是否改变 |
| `outcome` | test passed / failed / permission denied | 区分技术结局与授权结局 |
| `feedback_source` | 用户、测试、工具、自动 judge | 评估证据的强弱 |
| `revision` | 保留、限定条件、弃用、回滚 | 让后续更新可审计 |

Codex 当前公开实现明确保留 citation 与 Stage 1 usage 这一部分；上述更细的 outcome 账本是从它的闭环抽出的通用设计，不应误写成 Codex 已有的数据模型。

## 7.3 使用强化为什么会自我偏向

如果系统把“使用次数高”直接理解为“真理程度高”，它会出现曝光偏差：常驻摘要中已经突出的内容更容易被搜索、引用和再次保留；难搜到、表达不够显眼或只在少数任务中关键的内容，则较少获得强化。错误记忆也可能沿着同一回路被持续放大。

```text
摘要中已有旧规则
       ↓
Agent 更容易读到并引用
       ↓
usage 增加
       ↓
巩固时更容易继续保留
       ↓
旧规则继续占据摘要位置
```

这里讨论的是“citation → usage → consolidation”这一结构需要面对的控制问题，并非对 Codex 已发生故障的断言。固定代码可证明 usage 回写存在；是否造成实际自强化，需要运行日志、用户纠正记录和对照实验，公开代码本身无法证明。

可操作的缓解方式包括：

- 把 usage 与任务结果、用户纠正、当前证据新鲜度分开计分；
- 为高风险或跨项目经验要求明确来源和适用条件，不能只看频率；
- 保存未采纳、失败和反例，避免只对成功轨迹做巩固；
- 在 Phase 2 中保留“未知/待复核”状态，避免强行合并为单一规则；
- 对新 summary 或 skill 先做 shadow 使用或离线 replay，再决定是否晋升。

## 7.4 经验怎样升为技能，以及为什么要慢一步

一次成功的 rollout 通常只能证明“这个具体环境下曾经成功”。要升为流程或技能，系统至少要补齐两个问题：它适用于什么条件？如果不适用，怎样撤回或修订？

```text
原始轨迹与工具结果
        ↓
候选反思 / 流程
        ↓
来源、前置条件、版本、反例、测试
        ↓
受限晋升为可复用 playbook 或 skill
        ↓
当前任务中的授权使用
        ↓
结果回写：保留、修订、弃用或回滚
```

[MemP](https://arxiv.org/abs/2508.06433)（2025-08，历史背景）用 trajectory、step-by-step instruction 和高层 script 的分层，说明经验对象可以分阶段形成；[MemSkill](https://arxiv.org/abs/2602.02474) 和 [XSkill](https://arxiv.org/abs/2603.12056)（早期研究）继续讨论 Memory 操作和任务技能抽象。这些材料用于解释问题来源；它们尚未构成通用的技能晋升协议。

对于可改变文件、网络或外部系统的工件，晋升记录还应包含：

| 要保留的信息 | 为什么需要 |
|---|---|
| 输入、工具和依赖版本 | 识别环境漂移 |
| 成功证据与失败/反例 | 防止把偶然成功写成普适规则 |
| 允许的副作用 | 防止检索到 skill 就默认获得权限 |
| 测试与 sandbox 结果 | 区分“可编写”与“可在受控环境运行” |
| 版本、来源与撤回链 | 出错后知道需要替换哪些派生工件 |

2026 年 8 月的 [PoisonedEvolution](https://arxiv.org/html/2608.05563v2) 正是在这条晋升链上给出风险证据：不可信轨迹可能被 self-evolving 流程吸收，进而影响持久技能。它采用作者构造的、惰性 canary 规格；论文报告的是工件持久化与演化过程中的阶段性成功，不能外推为现实中任意系统的攻击概率，更不能当作已针对 Codex 固定版本复现的漏洞。

## 7.5 学习“何时管理 Memory”：AgeMem（v3，2026-07）与 MemCon

第 7 层还包含另一类学习：系统同时学习任务经验，以及何时检索、合并、遗忘或保持不动。[AgeMem v3](https://arxiv.org/abs/2601.01885v3)（2026-07-23，论文/代码研究原型）把短期/长期 Memory 管理暴露为 Agent 可调用的 tool actions；[MemCon](https://arxiv.org/abs/2607.13591)（2026-07，预印本）将 retrieve、plan injection、re-retrieve、consolidate、forget 与 no-op 看作在线策略动作。输入可以包含当前任务、候选记忆、预算和历史反馈，输出是某个 Memory 操作。

```text
状态：当前任务 + 候选 Memory + 预算 + 过去结果
                         ↓
控制器提出：retrieve / consolidate / forget / no-op
                         ↓
确定性边界检查：scope、来源、权限、版本、预算
                         ↓
执行允许的 primitive，记录结果
                         ↓
用任务效果和成本更新策略或规则
```

它解决的是“每个任务都全量检索、全量巩固”的成本和迟钝问题。风险也很直接：一个学习中的控制器可能把早期偶然反馈当成普遍规律，或过早遗忘以后才重要的状态。更稳妥的工程形状是让控制器只选择可审计、可回滚的 primitive；它不能绕过来源验证、项目范围、行动授权或删除保留规则。

AgeMem 和 MemCon 都是近期研究信号；其作者协议能说明机制在指定环境下可被训练或比较，不能证明长期在线学习在不同工具、用户和数据分布中稳定。

## 7.6 MemTxn / MemTX：把反馈与更新放进可恢复边界

[MemTxn](https://arxiv.org/abs/2607.27834) 代表另一条重要路线：回答模型提出更新，但提交边界在模型外。它把 source-supported write validation、temporal version selection 和 durable snapshot journal 放入更新流程。这里把 `MemTX` 作为对这类 memory transaction 机制的简称；本章引用的具体论文和机制是 MemTxn，不能把两个名称当作不同的成熟产品。

它解决的反馈问题是：用户纠正或新证据到来时，系统如何避免只改了摘要、忘记改索引，或在中途崩溃后留下半套状态。

```text
新证据 / 用户纠正
        ↓
模型提出 patch 与引用来源
        ↓
外部验证：新断言能否由来源支持？时间版本是否冲突？
        ↓
写入 journal / snapshot，再提交可见状态
        ↓
失败时恢复完整旧状态；成功时保留可追溯版本
```

对照 Codex：Codex 有 Stage 1/Phase 2 jobs、lease、selection snapshot 和 Git baseline，能处理一部分后台并发与下一轮修复；它的 `MEMORY.md` 等文件写入没有与 SQLite 状态库构成统一的事务提交。MemTxn 是预印本及原型层面的设计与作者评测，提供了值得补入架构的恢复边界，尚没有证明 Codex 或一般 Memory 系统已经拥有 ACID 级保证。

## 7.7 成本反馈：必须把“有帮助”与“值得”分开

[Omri 等人的系统表征研究](https://arxiv.org/abs/2606.06448) 将 stateful long-horizon Agent Memory 工作负载的 construction、retrieval 和 generation 阶段分开观察。它提醒反馈控制器：一次“回答更好”也可能伴随更高的抽取、巩固、索引、检索、上下文占用和恢复成本。

| 反馈决策 | 只看任务成功时容易漏掉什么 | 还应观察的成本/风险 |
|---|---|---|
| 多写一条候选 | 后续抽取和巩固队列膨胀 | token、延迟、重复和污染面 |
| 保留常被引用的摘要 | 曝光导致的使用偏差 | 覆盖面、错误强化和过时风险 |
| 升级为技能 | 一次任务的局部成功 | 验证、sandbox、维护和撤回成本 |
| 频繁重巩固 | 文档表面更整洁 | 后台模型费用、并发和文件中间态 |
| 自动遗忘 | 当前上下文更短 | 未来任务的不可恢复损失 |

这篇论文是作者针对多种系统与设定的表征研究，并非针对 Codex 的生产账单。它的价值在于提供了反馈优化的单位：不要把 Memory 成本只算作一次搜索或一个向量库查询。

## 7.8 怎样评测持续学习，不能只看一次问答

下面的评测面彼此不能替代：

| 测试面 | 要回答的问题 | 代表性证据类型 |
|---|---|---|
| 回忆与检索 | 历史能否被找到和正确理解 | LongMemEval、LoCoMo 等长程任务 |
| 增量读写与遗忘 | 新信息能否修订旧状态、是否删对 | [MemoryAgentBench](https://arxiv.org/abs/2507.05257)、[ForgetEval](https://arxiv.org/abs/2606.15903) |
| 行动 grounding | 记忆是否改变工具选择和参数 | [Mem2ActBench](https://arxiv.org/abs/2601.19935)（2026-01，历史基准） |
| 适应失效信息 | 新证据是否压过旧经验 | [MemTxn](https://arxiv.org/abs/2607.27834) 的时间版本选择与故障恢复实验 |
| 安全闭环 | 写入、执行和遗忘能否抵抗污染 | [MemSecBench](https://arxiv.org/abs/2607.27080)、PoisonedEvolution |
| 恢复与一致性 | 中断、双写、旧快照回灌后能否恢复 | MemTxn 提出的 transaction/recovery 方向；需运行时故障注入 |

一个足够严格的持续学习实验，应固定初始历史、任务分布、模型/Agent 包装、工具版本、Memory 预算和评判器；然后同时报告无 Memory、只读历史、使用反馈、启用自动晋升和启用控制器等条件。还需要加入错误反馈、过期工具版本、跨项目相似任务、删除后检索和 crash/replay。单个最终成功率无法告诉读者：是哪条记忆、哪次反馈或哪项控制器动作造成了变化。

## 7.9 Codex 已有的恢复边界与仍未解决的问题

Codex 当前的工程控制包括：Phase 1 job 的 ownership token、lease、retry 和 source watermark；Phase 2 的全局 job、heartbeat、selection snapshot 和成功 cooldown；文件工件的 Git baseline；以及在下次运行中修复未提交 diff 的机会。这些是固定代码可以支持的静态结构判断。

它仍有明确边界：

- citation 缺失或错误时，usage reinforcement 会漏记或失真；
- usage 回写没有内建的“任务成功/失败/用户纠正”统一账本；
- Phase 2 的生成式语义合并没有独立事实 verifier；artifact 检查不能证明事实判断正确；
- SQLite job 状态与 Markdown 文件工件没有共用一个原子提交面，崩溃或并发下仍需观察读写一致性；
- `forget`、thread disable、污染处理和 full reset 是不同操作，缺少统一 entry ID 和可验证的派生删除回执；
- public GitHub issue 是用户报告和故障线索，不能替代本机复现或发生率统计。例如关于 selection 并发、后台 worker 或 context window 的 issue，只能用于指出需要验证的路径。

## 本章小结

Codex 展示了一条可检查的最小闭环：引用 Memory → 记录使用 → 在下一轮 Phase 2 中重巩固。它已经把“被用过”从纯粹的提示词行为带入持久状态管理。

接下来最值得补强的是让反馈携带结局、来源、时间、范围、成本和撤回关系；让经验晋升经过验证；让 learned controller 只在受限 primitive 内动作；让更新和恢复拥有清楚的事务边界。近期的 AgeMem/MemCon、MemTxn、Omri 系统表征、行动基准与自演化安全研究，分别补充了控制、恢复、成本、结果和风险这几个缺口。它们多数仍是论文或原型证据，适合用来解释架构演进，不足以声称行业已解决持续学习问题。
