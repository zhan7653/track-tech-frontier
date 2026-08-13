# 从经历到记忆：capture、抽取、合并与提交的完整算法链

“写入 Memory”常被包装成一个 `add()` 调用，内部却可能包含多次模型调用、候选检索、事实抽取、冲突判断、embedding、图更新与历史记录。不同系统的主要差异也不在 API 名称，而在于它们何时丢弃原始信息、谁决定一条候选有资格进入长期状态，以及失败后能否知道哪一步完成了。

本篇把形成算法拆成六个阶段，并比较五类主流路线。它讨论的是跨会话、可更新的外部 Memory；纯日志记录和一次性 RAG ingestion 只作为边界。

## 1. 一条写入请求实际上经过什么

较完整的形成链可以表达为：

```text
capture
  → normalize & bind identity/scope/time
  → segment / group into evidence units
  → propose typed candidates
  → retrieve related existing state
  → decide ADD / MERGE / SUPERSEDE / CONFLICT / NOOP
  → policy & security admission
  → commit authoritative revision
  → materialize summary / FTS / embedding / graph
  → emit receipt, cost and repair state
```

其中任何两步都可以被合并，但问题仍然存在。若 extractor 直接写向量库，candidate proposal、state transition 和 index materialization 被压成一个不可观察动作；若摘要生成后立刻删除原文，形成误差无法重新处理；若主表、向量和图分别写入，部分成功需要明确权威层与补偿路径。

## 2. Capture：先完整记录，还是先选择什么值得记录

### 2.1 全量事件 capture

确定性 capture 将 user turn、assistant response、tool call、tool result、环境 observation 和 outcome 分别保存。算法通常只做：

1. 从宿主 hook 获取结构化事件；
2. 绑定 principal、session、task/project 与时间；
3. 对敏感字段做 masking 或存 pointer；
4. 计算内容 hash 和 parent event；
5. append 到 journal。

优势是形成阶段不需要猜“什么重要”，以后可以用新模型重处理。缺点是 volume、隐私和后续构造成本线性增长；工具输出还可能很大、重复或包含二进制资源。Coding Agent 中的 lifecycle hooks、Causal Memory 的 session log，以及 scope-recall-hermes 的 journal-first pipeline 都属于这种方向。

### 2.2 选择性 capture

选择性路线在保存前按 event type、长度、重复度、重要性、任务阶段或模型判断过滤。例如只保留 tool result 的摘要，忽略低信息量 assistant turn，或在 session end 才聚合整段轨迹。

它节省存储和下游模型调用，却产生不可恢复的 selection bias：当前看来无关的错误日志，可能是未来问题的唯一证据；模型也容易偏爱显著、情绪化或与当前目标相关的内容。因而需要将“未捕获”与“捕获后未晋升”分开观测。前者永久消失，后者仍可重处理。

### 2.3 Capture 的工程失败

- hook 超时后宿主 fail-open，任务完成但记录缺失；
- tool result 与调用 ID 没有关联，之后无法重建因果顺序；
- retry 形成重复事件，后续被误认为多次独立证据；
- redaction 在摘要之后发生，敏感内容已进入模型或派生索引；
- session end 未触发，依赖终止钩子的 consolidation 永远不运行。

## 3. Segment 与 group：形成算法的第一个信息瓶颈

原始流必须被划成候选单位。常见边界包括固定 token window、单个 turn、session、topic segment、tool transaction、task episode 和 causal trajectory。

### 3.1 固定窗口

固定窗口最容易实现，适合 embedding 和批量摘要。overlap 可以减少边界信息丢失，却增加重复候选。它不知道一个决策跨越了几个 turn，也不知道一次工具失败与后续修复属于同一事件。

### 3.2 语义/主题分段

模型或 embedding change-point 判断 topic boundary，再为每段生成标题、摘要或 facts。它让对象更接近语义单元，但分段模型的错误会向下游传播：错误合段让多个主体/条件混在一起，错误切分让因果链断裂。

### 3.3 事件与任务分组

利用 tool_call_id、task_id、repo/branch、environment episode 或 outcome，把输入组织成带结果的 trajectory。程序性记忆和项目记忆更依赖这种分组，因为没有 outcome 的步骤无法判断是否值得复用。

这一阶段决定 extractor 看见多少上下文，也是 construction cost 的主要来源。较新的系统研究将 ingestion、construction、storage、retrieval、prompt assembly、generation、maintenance 分开计量，正是因为长窗口摘要和逐事件抽取会产生完全不同的 write-path prefill 与延迟。[Agent Memory 系统表征](https://arxiv.org/abs/2606.06448)

## 4. 从文本提出 typed candidates

### 4.1 摘要式形成

摘要路线的输入是历史片段与旧摘要，输出是一段更短的状态。递归摘要写作：

```text
summary_t = LLM(summary_{t-1}, new_events_t, length/budget constraint)
```

层级摘要则分别形成 turn/session/topic/global 表示。Generative Agents 还基于 recency、importance 和 relevance 选择 observations，再触发 reflection，生成更高层结论。

摘要的优势是读时便宜、叙事连贯；弱点是它是有损状态压缩。专名、否定词、条件、时间和少见分支最容易消失；递归摘要还会把上一轮误差当成下一轮输入。若没有 source span，系统无法在读时补回原证据。

### 4.2 原子事实抽取

事实路线要求模型输出结构化候选，例如：

```json
{
  "subject": "user:42",
  "predicate": "prefers_editor",
  "value": "VS Code",
  "qualifiers": {"project": "P", "valid_from": "..."},
  "source_spans": ["event:...#span=..."]
}
```

抽取可以一次生成多个 facts，也可以先生成 free-text facts 再做 schema normalization。AtomMem 的选择性 atomic facts 进一步用于 event/profile/graph；SimpleMem 将滑动窗口蒸馏成 semantic、lexical 和 structured views；Hindsight 则组织 world facts、experiences、entity summaries 与 beliefs。

原子化的核心难题是 granularity。把“用户在项目 P 中更喜欢 VS Code，因为远程插件”拆成一条、两条还是三条事实，会改变后续更新和检索。事实越细，identity/link 数量越多；越粗，局部修订越容易覆盖无关条件。

### 4.3 关系和程序候选

关系抽取不仅要找实体，还要给边定类型、方向、时间和来源；程序抽取则需要步骤、前置条件、工具版本、outcome 与失败分支。两者不能只使用普通事实 schema。Causal Memory 从 session distill facts 与 decision→outcome edges；MemP/MemSkill 一类工作则从 trajectory 形成 procedure 或管理策略。

## 5. 先检索旧状态，再决定如何变化

候选抽取后，系统通常检索同主体、同 predicate、相似语义或邻近 graph 的旧对象，将它们交给规则/模型进行 consolidation。典型动作是：

| 动作 | 何时使用 | 应保留的关系 |
|---|---|---|
| ADD | 没有等价或冲突对象 | 新 identity + source |
| REINFORCE | 相同陈述得到额外证据 | 追加 source，不重复对象 |
| MERGE | 多条互补片段组成更完整对象 | predecessors + merge reason |
| SUPERSEDE | 新陈述明确替代旧陈述 | revision parent + validity |
| CONFLICT | 互不相容且无法自动解决 | 双方可见 + unresolved state |
| NOOP | 重复、无价值或超出范围 | 仍记录 decision receipt |

### 5.1 为什么 candidate retrieval 会改变写入结果

若检索漏掉旧事实，系统会重复 ADD；若取回错误相似项，模型会 false merge；候选数量太少会漏冲突，太多又会增加 token 和混淆。写入质量因此依赖一个隐含的 retrieval protocol，而不仅是 extractor。

Mem0 的固定版本正是先用 scope filter 和语义候选查旧 memory，再让模型做 fact/update decision。A-MEM 在新 note 到来时找历史链接并更新邻近 contextual representation。它们说明“写入”已经包含一次读，但公开 benchmark 很少把 candidate recall 与 mutation error 分开报告。

### 5.2 决策模型怎样出错

- 将更具体的事实误判为冲突并覆盖旧值；
- 将真正冲突误判为补充，生成自相矛盾 summary；
- 根据措辞相似而合并不同主体；
- 只看到当前候选，忽略迟到证据或历史版本；
- 为减少条目数量过度 MERGE，损害未来召回。

## 6. Admission：从模型 proposal 到可生效状态

抽取/合并模型的输出不必直接成为权威状态。较强的 admission chain 会依次检查：

```text
schema
→ authenticated identity/scope
→ source support
→ duplicate/conflict
→ privacy/retention/purpose
→ security/quarantine
→ budget/rate limit
→ commit authorization
```

### 6.1 Source-supported validation

候选的每个 consequential field 应能回到 source span 或 tool receipt。source support 不是“来源一定真实”，而是防止模型在抽取时加入源中不存在的断言，并允许后来重新解释。[MemTxn](https://arxiv.org/abs/2607.27834)把 source-supported write validation、temporal version selection 与 durable snapshot journal放在 answer model 外部，是这一方向的近期代表。

### 6.2 Quarantine 与 promotion

不可信网页、跨 Agent 贡献、模型推断或可能含指令的内容可以先进入 quarantine。安全 detector、policy、人审或后续独立证据决定是否 promotion。重要的是 quarantine 不能与“彻底丢弃”混同，也不能因为对象被签名就自动认为内容安全。

### 6.3 Commit 与 projection

通过 admission 后，系统分配 revision、写权威状态和 receipt，然后构造 FTS、embedding、graph、summary 等投影。事务可以覆盖单一数据库；跨后端通常需要 outbox、watermark、replay 或 reconciliation。主状态成功而 projection 失败时，读取应能解释 stale/repair 状态，而不是悄悄少返回候选。

## 7. 学习型写入控制器究竟学习什么

[MemCon](https://arxiv.org/abs/2607.13591)把 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 建模为在线动作；其他 agentic-memory 工作也将记忆操作暴露成 tools，让策略根据任务、状态和预算选择。它们试图解决固定阈值无法适应不同 query horizon 与成本的问题。

一个控制器的 observation 可能包括当前任务表示、store size、retrieval confidence、token budget、最近 outcome 和对象 age；action 是形成/检索/合并/遗忘 primitive；reward 由任务成功、memory quality 和成本组合。难点在于 reward 延迟：当前任务成功不证明某次写入会长期有益，忘记后的反事实也无法观察。

因此近期更可信的方向不是让策略拥有无限制写权限，而是**proposal policy + constrained commit**：控制器决定尝试哪个 operator，identity、source、policy、transaction 和 rollback 层仍决定是否生效。需要跨 session、长期 horizon 的评价来测 policy drift 和不可逆误操作。

## 8. 五类形成路线的实质比较

| 路线 | 主要判断发生在哪里 | 读时形状 | 成本转移 | 典型失败 |
|---|---|---|---|---|
| raw retain | 几乎不做语义判断 | 大量原始事件检索 | 低 write、高 read/storage | 噪声、隐私、候选爆炸 |
| summary/reflection | construction LLM | 少量高层文本 | 高 write、低 prompt | 细节/条件丢失、递归误差 |
| typed extraction | schema + candidate resolution | 字段/关系/当前视图 | 抽取、identity、维护 | false merge/split、幻觉事实 |
| transaction admission | policy/validation/commit | revision + source-aware state | 额外延迟、日志、reconcile | 误拦/漏拦、部分提交 |
| learned control | online policy | 动态对象与操作组合 | 训练、探索、观测 | reward hacking、策略漂移、不可逆动作 |

现实系统常混合这些路线：raw journal 保留证据，typed state 提供当前视图，summary 降低 prompt，learned/规则控制器选择操作。混合并不自动更好；它增加了跨层一致性与成本归因问题。

继续阅读[写入系统 walkthrough](02-system-walkthroughs.md)，看 Mem0、Causal Memory、scope-recall-hermes、OpenViking 和 Engraphis 怎样具体实现上述步骤；[形成失败与前沿](03-cost-security-and-frontier.md)则讨论成本、信息损失与攻击链。
