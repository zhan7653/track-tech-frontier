# Agent Memory 技术演进：从经验片段到受治理的状态系统

**As of 2026-08-10**

## 结论先行

Agent Memory 的主线不是“向量检索越来越复杂”，而是系统逐步承认了五类此前被折叠的问题：**要保存什么状态、如何在预算中找回、状态如何演化、谁有权读写、怎样证明它真的改善且没有破坏行为**。2023 年的标志性系统首先给出“外部记录—反思—再调用”进入后续 planning/action 的设计；2024–25 年把层级、结构、更新和服务边界显式化；2025–26 年则把 consolidation、forgetting、version、transaction、authority、repair 和 action-grounded evaluation 推到独立控制面。这个阶段划分是报告推断，不是任何单一论文的原话。 `[FND-C01,FND-C03,FND-C05,FND-C11,FND-C23; FND-S01,FND-S02,FND-S03,FND-S07]`

最新前沿同时给出了对这条主线的反证：构造后的 memory store 并不总胜过 raw-turn RAG，效果可由 retriever 和 token budget 反转；bitemporal filtering 在不同问题类型上也可能一升一降；consolidation 没有无条件最优算子。也就是说，领域正在从“增加 memory 机制”转向“为具体状态、预算、权限与协议选择 memory operation”。 `[REP-C03,REP-C05,REP-C06; REP-S02,REP-S03]` `[FND-C19,FND-C20; FND-S11]`

<!-- synthesis:TL-Y01 claims:FND-C01,FND-C03,FND-C05,FND-C11,FND-C23,REP-C03,REP-C05,REP-C06,FND-C19,FND-C20 clusters:MM-C01,MM-C03,MM-C04,MM-C05 -->

## 一、事件时间线：先后顺序不等于影响

| 时段 | 可核实事件与机制 | 证据等级 | 不能推出什么 |
|---|---|---|---|
| 2023 | Reflexion 把语言反馈放入 episodic buffer；Generative Agents 连接 experience stream、reflection、retrieval 与 planning；Voyager 把复用对象变成 executable skill library；MemGPT 用 tiers 与 interrupts 管理有限上下文。 `[EXP-C01,EXP-C02,EXP-C03,EXP-C04; EXP-S01,EXP-S03,EXP-S02,EXP-S04]` | dated events + primary mechanism claims | 不能说四者存在已证实的直接影响链；也不能把 reflection、skill、user fact 与 persistent service 视为同一对象 |
| 2023–24 | MemoryBank 将 store、retriever、updater 分开，并按时间/重要度做强化或遗忘。 `[FND-C05,FND-C06; FND-S03]` | dated mechanism; source-asserted Ebbinghaus inspiration | 不能据此证明该遗忘启发式在任意任务上正确 |
| 2024 | LoCoMo 与 LongMemEval 把长对话 memory 变成可重复的 post-hoc QA/summary protocol；AgentPoison 把 persistent memory/RAG poisoning 作为专门威胁模型。 `[BEN-C01,BEN-C02; BEN-S01,BEN-S02]` `[OPS-C01,OPS-C02; OPS-S01]` | dated benchmark/threat events | QA 分数不证明 write/update/action；作者攻击率不等于部署 prevalence |
| 2025 上半年 | A-MEM 以结构属性、动态链接和历史上下文更新组织 notes；MemoryOS 明确 short/mid/long tiers 与 Storage/Updating/Retrieval/Generation；Collaborative Memory 把 private/shared fragments、provenance 与动态读写策略带入 shared memory。 `[FND-C09,FND-C11; FND-S06,FND-S07]` `[EXP-C06; EXP-S08]` | dated mechanism events | 不能从架构图或 README 推出互操作、安全或生产成熟度 |
| 2025 中后段 | MemoryAgentBench 将 evaluation 拆成 retrieval、test-time learning、long-range understanding、selective forgetting；MEXTRA 与 query-only injection 工作分别暴露黑盒 extraction 与低权限写入路径。 `[FND-C13,BEN-C03; FND-S08,BEN-S03]` `[OPS-C03,OPS-C04; OPS-S02,OPS-S03]` | dated benchmark/security events | 不能把 lifecycle benchmark 与安全 benchmark 合成单分数 |
| 2025-08..2026-04 | MemP 把 trajectories 编译为 instructions/scripts；Hindsight 区分 world facts、experiences、entity summaries、beliefs；SimpleMem 把 compression、online synthesis、intent-aware retrieval 连成 pipeline；多项 action/state benchmark 开始把 memory 放回 tool/environment loop。 `[EXP-C09; EXP-S09]` `[REP-C08,REP-C04; REP-S11,REP-S12]` `[BEN-C07,BEN-C12; BEN-S07,BEN-S11]` | dated mechanisms + protocols | 不能说“更结构化”必然更准确；这些论文/协议仍有条件差异 |
| 2026-05..08 | rolling-90d 内同时出现 atomic/event hierarchy、bitemporal versioning、active navigation、trust-aware retrieval；learned memory controller、budget-dependent consolidation、transaction boundary、forgetting placement；procedural meta-skill、multimodal/world-state compression；以及 MAFIA、Salami、MutMem、DP-MemView、STALE 与 MemSecBench。 `[REP-C01,REP-C02,REP-C07; REP-S01,REP-S02,REP-S04]` `[FND-C14,FND-C17,FND-C19,FND-C21; FND-S09,FND-S10,FND-S11,FND-S12]` `[EXP-C10,EXP-C11,EXP-C14,EXP-C15; EXP-S10,EXP-S11,EXP-S14,EXP-S15]` `[OPS-C10,OPS-C11,OPS-C12,OPS-C14,OPS-C16; OPS-S08,OPS-S09,OPS-S10,OPS-S11,OPS-S12]` `[BEN-C16; BEN-S16]` | multiple dated frontier signals | 绝大多数是作者预印本；密集发表不等于共识、成熟或加速采用 |

### 已找到的 source-asserted influence

本包只保留一个明确影响陈述：MemoryBank 的 updater 借鉴 Ebbinghaus forgetting curve。 `[FND-C06; FND-S03]` 由于 Ebbinghaus theory 不是当前 bundle 中的 Agent Memory entity，`relations-proposal.jsonl` 不制造 from/to entity join。

对 Generative Agents → A-MEM、MemGPT → MemoryOS/MemCon、AgentPoison → 后续 poisoning papers 等看似合理的谱系，当前来源只足以证明时间与机制相邻，**不足以证明作者明确受前作影响**。这些只以 `precedes(event)` 或 `extends/complements(inference)` 候选表达。

<!-- synthesis:TIME-AUTO-01 claims:BEN-C01,BEN-C02,BEN-C03,BEN-C07,BEN-C12,BEN-C16,EXP-C01,EXP-C02,EXP-C03,EXP-C04,EXP-C06,EXP-C09,EXP-C10,EXP-C11,EXP-C14,EXP-C15,FND-C05,FND-C06,FND-C09,FND-C11,FND-C13,FND-C14,FND-C17,FND-C19,FND-C21,OPS-C01,OPS-C02,OPS-C03,OPS-C04,OPS-C10,OPS-C11,OPS-C12,OPS-C14,OPS-C16,REP-C01,REP-C02,REP-C04,REP-C07,REP-C08 clusters:MM-C01,MM-C05,MM-C14 -->

## 二、为什么会从 stream/reflection/retrieval 走到 structured/lifecycle/control

### 1. Experience stream 解决了“模型不会跨运行保留经历”

2023 的关键突破不是数据库，而是闭合了行为回路：过去 observation/feedback 被保存、抽象并在未来 planning/action 前重新进入模型。Generative Agents 以 stream→reflection→planning 表达；Reflexion 保留 verbal feedback；Voyager 把可复用单元推进到 executable skills。 `[FND-C01,FND-C07,FND-C08; FND-S01,FND-S04,FND-S05]`

**报告推断：** 这一步把 memory 从“上下文材料”变为“能够改变后续 policy input 的持久对象”，但尚未回答对象的类型、版本、权限或删除。后续分叉因此不是装饰，而是不同状态对象对不同失败的响应：episode 需要 provenance/time，profile 需要 correction，procedure 需要 applicability/deprecation，world state 需要 visibility/action grounding。 `[EXP-C16,EXP-C19,EXP-C20; EXP-S02,EXP-S08,EXP-S12,EXP-S14]`

### 2. Tiering 与 retrieval 解决了“所有历史不能同时进入有限上下文”

MemGPT 将内容在 memory tiers 间移动并以 interrupts 管理控制流；MemoryBank 分开 store/retriever/updater；MemoryOS 再把 short/mid/long tiers 与四个模块固定下来。 `[FND-C03,FND-C05,FND-C11; FND-S02,FND-S03,FND-S07]`

**为什么发生：** 早期 stream 一旦增长，就同时产生容量、locality、token budget 和选择问题。把外部 store 与 active context 分开，允许系统只在当前任务中注入一部分历史；也让 retrieval latency、context cost 和 update cadence 可被单独测量。这个解释由多系统共同支持，但不是来源明确声明的单一因果链。 `[FND-C23; FND-S02,FND-S09,FND-S10]`

**反证边界：** 更长的外部 store 并不自动产生更好上下文。独立 LightMem reproduction 发现仅更换 retriever 可把同一 constructed store 的准确率从 58.1% 改到 75.5%，且 matched depth 下 raw-turn Naive RAG 通常更强；constructed memory 主要在紧 answer-token budget 下占优。 `[REP-C05,REP-C06; REP-S03]`

### 3. Structured/temporal representation 解决了“top-k snippets 丢失关系、时间与身份”

AtomMem 选择 atomic facts，再组织为 hierarchical events 与 temporal profiles；Hindsight 将 world facts、experiences、entity summaries、beliefs 分成逻辑网络；bitemporal store 把 immutable identity 与 versioned content 分开并同时保存 valid time / transaction time。 `[REP-C01,REP-C02,REP-C08; REP-S01,REP-S02,REP-S11]`

**为什么发生：** flat similarity 可以找到语义近邻，却不保证知道“谁的事实”“当时是否为真”“现在是否仍有效”“这个结论来自哪一事件”。一旦 personalization、shared principals、world state 和 corrections 进入系统，scope、time、version、provenance 就必须在 representation→index→context compilation 全路径中存活。 `[REP-C07,REP-C22; REP-S04,REP-S02,REP-S03]`

**反证边界：** graph 或 time-travel 不是无条件增强。bitemporal paper 自身在 60-question sample 中报告 knowledge-update recall 提升、temporal-reasoning recall 下降；post-filter 可能稀释 candidate budget。 `[REP-C03; REP-S02]` 图、时间与 schema 应由 query intent 和 failure mode 触发，而不是成为默认复杂度。

### 4. Lifecycle/control plane 解决了“retrieval 无法替代状态突变”

A-MEM 的 write 会建立 links 并更新历史 contextual representations；MemCon 把 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 作为在线 policy actions；MemTxn 将 source-supported write validation、temporal version selection、snapshot recovery 放到 answer model 外；ForgetEval 则把 supersede/release/purge 与 recall 分开。 `[FND-C09,FND-C14,FND-C17,FND-C21; FND-S06,FND-S09,FND-S10,FND-S12]`

**为什么发生：** retrieval 只回答“现在读什么”，不能独立回答“什么可写入”“哪个版本有效”“该合并还是保留”“删除传播到哪些 derived artifacts”“崩溃后如何恢复”。因此 data plane、retrieval plane、mutation/control plane 的分离，是长期状态从 demo 走向可审计系统的必要架构推断。 `[FND-C23; FND-S02,FND-S09,FND-S10]`

**反证边界：** consolidation 的最优性取决于预算和任务；retention 保留细节，consolidation 提高单位 token coverage 但可抹掉 query-critical evidence。作者明确不提供 Merge/Abstract/Rewrite 的普遍排序。 `[FND-C19,FND-C20; FND-S11]` MemCon 的增益也是单作者组、指定 benchmark/framework/backbone 下的结果，尚无独立复现。 `[FND-C16; FND-S09]`

### 5. Security/governance 解决了“持久状态会把低信任输入变成未来权威”

AgentPoison、MINJA、eTAMP 与 sleeper poisoning 分别展示 retrieval-triggered backdoor、query-only injection、environment-derived contamination 与延迟 action chain；MEXTRA 展示黑盒 memory extraction。 `[OPS-C01,OPS-C04,OPS-C05,OPS-C07,OPS-C03; OPS-S01,OPS-S03,OPS-S05,OPS-S06,OPS-S02]`

**为什么发生（报告推断）：** 与不把低信任内容写入长期状态相比，持久 write 增加了跨会话再次取回、注入 prompt 或驱动 tool action 的路径。共享、个性化和多租户进一步引入 principal、scope、authority 与 revocation。于是安全边界从 input filter 扩展为 `write → store/mutate → retrieve → act → delete/repair` 生命周期。 `[OPS-C10,OPS-C11,OPS-C12,OPS-C16; OPS-S08,OPS-S09,OPS-S10,OPS-S12]`

**反证边界：** provenance 不等于 truth。MutMem 可证明 signed predecessor-linked transition，却明确不证明内容为真；StateAuditor 验证 chronology/provenance，也不证明 semantic supersession。 `[OPS-C12,OPS-C13,OPS-C17; OPS-S10,OPS-S12]` 产品 API 的 CRUD、TTL、scope、memoryId、IAM 等只是治理接口，不是独立的全链防御或删除传播证明。 `[OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C23; OPS-S19,OPS-S18,OPS-S17]`

### 6. Benchmark 从 recall 走向 action/lifecycle/security，是因为“答对问题”不等于“记忆改变了行为”

LoCoMo/LongMemEval 建立 fixed-history recall 参考；MemoryAgentBench、MemBench、Memora、HaluMem 逐步拆开 ingestion、update、forget、capacity 与 operation hallucination；Mem2ActBench、MemoryArena、StoryBench、EMemBench、MEMTRACK 把 memory 放进 tool/action/environment state；GroupMemBench、Mem-Gallery、ImplicitMemBench 与 MemSecBench 再补 principal、multimodal、implicit adaptation 与 write–execute–forget security。 `[BEN-C01,BEN-C02,BEN-C03,BEN-C04,BEN-C05,BEN-C06,BEN-C07,BEN-C09,BEN-C10,BEN-C11,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16; BEN-S01..BEN-S16]`

**为什么发生：** static QA 允许系统在固定历史上事后找答案，却不测何时写、如何改、能否把记忆落实为参数/行动、错误是否持久、是否能安全忘记。因而“一个 Agent Memory 分数”在定义上越来越站不住脚。 `[BEN-C22,BEN-C25; BEN-S01,BEN-S07,BEN-S11,BEN-S16]`

<!-- synthesis:TIME-AUTO-02 claims:BEN-C01,BEN-C02,BEN-C03,BEN-C04,BEN-C05,BEN-C06,BEN-C07,BEN-C09,BEN-C10,BEN-C11,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16,BEN-C22,BEN-C25,EXP-C16,EXP-C19,EXP-C20,FND-C01,FND-C03,FND-C05,FND-C07,FND-C08,FND-C09,FND-C11,FND-C14,FND-C16,FND-C17,FND-C19,FND-C20,FND-C21,FND-C23,OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C10,OPS-C11,OPS-C12,OPS-C13,OPS-C16,OPS-C17,OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C23,REP-C01,REP-C02,REP-C03,REP-C05,REP-C06,REP-C07,REP-C08,REP-C22 clusters:MM-C01,MM-C05,MM-C14 -->

## 三、最新 12 个月与 90 天：什么变了，什么仍只是信号

最终 post-merge 可回放 ledger 有 1,994 个 mapped/deep-verified entities，其中 1,659 落在 rolling 12m、924 落在 rolling 90d；breadth 阶段的 canonical map 是 1,899 项，后加的 direct evidence objects 只闭合 provenance，不冒充搜索召回。rolling-90d primary membership 最密集的是 Coding, Project & Environment Memory（195）、Evaluation, Benchmarks & Comparability（94）、Security, Privacy, Integrity & Governance（92）、Experience, Procedural Memory & Skills（86）、Shared, Distributed & Portable Memory（80）。这些数字描述本次查询与筛选的时间分布，不是全球论文产量或采用率；锚点是 final entities×assignments join。

这一宽度信号与 deep packets 的变化方向一致：

- **operation selection 成为研究对象**：learned controller、budgeted consolidation、transaction boundary、forgetting placement 不是新增 store，而是在问何时、由谁、以什么保证执行 memory operation。 `[FND-C14,FND-C17,FND-C19,FND-C21; FND-S09,FND-S10,FND-S11,FND-S12]`
- **representation 进入 version/trust/compilation 阶段**：atomic/event hierarchy、bitemporal identity、active navigation 与 trustworthy retrieval 同时出现。 `[REP-C01,REP-C02,REP-C07; REP-S01,REP-S02,REP-S04]`
- **安全从单 poison record 走向 adaptive/collusive/full-chain**：MAFIA、Salami、MutMem、DP-MemView 与 STALE 分别攻击或约束 auditing、fragment composition、mutation provenance、repeated disclosure、update→behavior adaptation。 `[OPS-C10,OPS-C11,OPS-C12,OPS-C14,OPS-C16; OPS-S08,OPS-S09,OPS-S10,OPS-S11,OPS-S12]`
- **memory object 从 prose episode 向 procedure/meta-skill/world state 分化**：MemP、MemSkill、XSkill、POLAR、WorldLines、MeMento 所保存和消费的对象不同，不能用一个“长期记忆”桶概括。 `[EXP-C09,EXP-C10,EXP-C11,EXP-C12,EXP-C14,EXP-C15; EXP-S09..EXP-S15]`
- **evaluation 变成协议族**：action、multi-party、multimodal、implicit learning 与 security lifecycle 已形成不同 protocol family，跨族分数不可合并。 `[BEN-C07,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16,BEN-C22; BEN-S07,BEN-S11..BEN-S16]`

GitHub 深验证提供了另一只“工程时钟”：截至 2026-08-10，有界选择的 59 个仓库均完成状态观测，其中 19 个创建于 rolling 90d、39 个创建于 rolling 12m、54 个在 rolling 90d 有 push；固定 SHA 检查还分别观察到 46 个可识别 license、39 个 latest release、40 个 CI workflow、53 个测试路径，以及 40 个在 90 天窗口内至少两名可归属贡献者。它证明的是 dated presence 与可检查表面，不是质量、生产成熟或采用。 `[GR-C-RUN01,GR-C-RUN02]`

这一工程窗口补强了“为何继续分层”的解释：复合管线开始拆开事实/实体抽取、组织与版本、检索融合和上下文编译；写入组织与读时选择成为不同控制面；context compression、procedure/skill、personal state、coding/project graph、portable asset、安全拦截与细分评测各自形成实现表面。这里是跨仓库的 report inference，不是项目间影响链，也不是统一架构已经收敛。 `[GR-C-M001,GR-C-M002,GR-C-M004,GR-C-M005,GR-C-M006,GR-C-M007,GR-C-M008,GR-C-M009,GR-C-M010]`

这里没有 growth/acceleration 结论。论文日期只能证明出现时间；GitHub 当前观察只能证明某 commit/release/activity surface 在观察时存在。所有 GitHub stars 都只有单次同轮快照；外部 OSSInsight event histories 虽可回放，但 [59 仓有界核验](../../work/github-radar/star-growth/report.md) 中只有 1 个达到窗口 delta 门槛、3 个仅可诊断，其余因覆盖失配或空历史不可用，因此不能做跨仓可比的 stars acceleration 判断，更不能据此推断社区或采用正在加速。 `[GR-C-RUN03]`

<!-- synthesis:TIME-AUTO-03 claims:BEN-C07,BEN-C12,BEN-C13,BEN-C14,BEN-C15,BEN-C16,BEN-C22,EXP-C09,EXP-C10,EXP-C11,EXP-C12,EXP-C14,EXP-C15,FND-C14,FND-C17,FND-C19,FND-C21,GR-C-M001,GR-C-M002,GR-C-M004,GR-C-M005,GR-C-M006,GR-C-M007,GR-C-M008,GR-C-M009,GR-C-M010,GR-C-RUN01,GR-C-RUN02,GR-C-RUN03,OPS-C10,OPS-C11,OPS-C12,OPS-C14,OPS-C16,REP-C01,REP-C02,REP-C07 clusters:MM-C01,MM-C05,MM-C14 -->

## 四、替代解释与反事实

### 反事实 A：也许问题只是 retriever，不需要复杂 memory construction

LightMem reproduction 是最强直接反证：fixed constructed store 下 retriever 改动显著改变答案准确率，raw-turn RAG 在 matched depth 下通常更好。 `[REP-C05,REP-C06; REP-S03]` 因此结构化 memory 的支持者必须证明收益来自表示/生命周期本身，而非更大 k、不同 reader 或更宽 token budget。

### 反事实 B：更长 context 或保留 raw trace 可能优于 consolidation

budgeted-consolidation 研究本身承认 retention 与 consolidation 的条件性交换。 `[FND-C19,FND-C20; FND-S11]` 决策应使用相同 task distribution、retrieval budget、answer budget 与 recoverability audit 比较，而不是预设“摘要必优”。

### 反事实 C：更新 store 后，agent 仍可能按旧状态行动

STALE 把 storage update 与 behavior adaptation 分开；其作者在 400 conflicts/1,200 queries 下报告最好模型总体 55.2%，说明“新事实可检索”不等于“旧 policy dependence 已消失”。 `[EXP-C13; EXP-S13]` 这支持将 revision propagation 和 action-time validation 纳入 lifecycle/security，而不是只提高 recall。

### 反事实 D：复杂 protocol 可能只扩大不可比性

从 recall 到 action/security 的扩展提高 realism，却也改变 unit、oracle、agent wrapper、judge 与 metric。 `[BEN-C22; BEN-S01,BEN-S11]` 解决办法不是把所有结果归一化成总分，而是保留 protocol fingerprint，并只在同一 comparability group 内排序。 `[BEN-C25; BEN-S07,BEN-S16]`

<!-- synthesis:TIME-AUTO-04 claims:BEN-C22,BEN-C25,EXP-C13,FND-C19,FND-C20,REP-C05,REP-C06 clusters:MM-C01,MM-C05,MM-C14 -->

## 五、因果主张审计

| 主张 | 分类 | 置信度 | 支持 | 可能推翻它的证据 |
|---|---|---:|---|---|
| 有限 context 与增长历史共同推动 tiering/retrieval/control 分层 | report inference | 中高 | MemGPT、MemoryBank、MemoryOS 的不同分层 `[FND-C03,FND-C05,FND-C11]` | 受控实验显示单一 raw-context path 在同预算、同生命周期任务中持续等同或更优 |
| stale/conflict/version 问题推动 structured temporal representation 与 mutation plane | report inference | 中 | bitemporal、A-MEM、STALE、MemTxn `[REP-C02,FND-C09,OPS-C16,FND-C17]` | 无 version/mutation primitives 的 flat store 在 matched correction/rollback tests 中稳定通过 |
| autonomy/shared scope 使 memory 变成 authority/security boundary | report inference | 高 | 多个独立 attack/privacy/shared-policy sources `[OPS-C01,OPS-C03,OPS-C04,OPS-C05,EXP-C06]` | 全链独立测试显示 prompt/input filter 单独阻止 write→action、extraction、cross-scope 与 stale-state failure |
| benchmark 扩展是 static recall 不能代表 action/lifecycle 的响应 | report inference | 高 | Mem2ActBench、MemoryArena、MemSecBench 与 protocol incompatibility `[BEN-C07,BEN-C12,BEN-C16,BEN-C22]` | 同-agent controlled reruns 显示 static QA 对 action、update、forget、安全结果具有稳定高预测力 |
| 未来工程会把 learned controller 放在 transaction/provenance primitives 上层 | forecast | 中 | 当前 mechanisms 互补 `[FND-C14,FND-C17,OPS-C12]` | learned controller 在无独立 control primitives 下也能安全处理 irreversible mutation，或 fixed policies 持续胜出 |

<!-- synthesis:TIME-AUTO-05 claims:BEN-C07,BEN-C12,BEN-C16,BEN-C22,EXP-C06,FND-C03,FND-C05,FND-C09,FND-C11,FND-C14,FND-C17,OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C12,OPS-C16,REP-C02 clusters:MM-C01,MM-C05,MM-C14 -->

## 六、条件性预测（不是事实）

1. **近期最可能收敛的是接口责任，而不是统一 backend。** 若多 backend benchmark 开始固定 write admission、version selection、delete/rollback 与 context compilation contracts，Memory OS/control-plane 语言会转化为可测试接口；否则仍只是项目命名。依据是 MemoryOS、MemTxn、ForgetEval、MemCon 的功能互补。 `[FND-C11,FND-C14,FND-C17,FND-C21]`
2. **retrieval 会从相似度排序变成受 scope/time/trust/budget 约束的 query plan。** 这一预测需要 matched retriever/reader/budget reproduction；LightMem 反证意味着复杂 planner 必须证明净收益。 `[REP-C02,REP-C05,REP-C06,REP-C07,REP-C18]`
3. **安全评测会向 write→retrieve→action→forget/repair 的全链协议发展。** MemSecBench 已提供一个 protocol signal，但独立复现、tenant isolation、deletion propagation 与 cost 尚缺。 `[BEN-C16; BEN-S16]` `[OPS-C27; OPS-S01..OPS-S19]`
4. **procedural、shared、personalized、embodied memory 不会合并成一个万能 store。** 它们的 durable object、principal 与 action semantics 不同；若未来共用底座，更可能共用 provenance/version/scope contracts，而不是共用一套 retrieval score。 `[EXP-C16,EXP-C18,EXP-C19,EXP-C20]`

<!-- synthesis:TIME-AUTO-06 claims:BEN-C16,EXP-C16,EXP-C18,EXP-C19,EXP-C20,FND-C11,FND-C14,FND-C17,FND-C21,OPS-C27,REP-C02,REP-C05,REP-C06,REP-C07,REP-C18 clusters:MM-C01,MM-C05,MM-C14 -->

## 七、未闭合缺口

- **直接影响关系：** 除 MemoryBank→Ebbinghaus 外，未打开足以证明项目间 influence 的原文；需查 related-work、作者访谈或官方设计文档。
- **独立复现：** MemCon、MemTxn、budgeted consolidation、ForgetEval、近期 representation/security/embodied work 大多仍是作者预印本。
- **工程迁移：** Letta README 表明 inspected repo 是 legacy V1、active development 已迁移；需另查当前 `letta-code`，不能把 paper-era identity 外推到当前产品。 `[FND-C04,REP-C15; FND-S14,REP-S19]`
- **删除与恢复：** logical hide、supersede、physical purge、embedding/summary/revision/cache/backup propagation 尚无跨产品独立证明。
- **采用与标准：** early breadth coverage 中 adoption/standards cells 为空；后续 standards/adoption 专项补了协议状态与采用探针，并确认两个 weak external integration signals，但没有当前版本独立 conformance、可归因 production deployment 或双向 round-trip evidence；README、stars 与 vendor docs 不能补位。
- **边界性 breadth signal：** coding/project memory（MM-C09）已有独立 deep packet，覆盖结构索引、事件溯源、上下文反证与反馈策略；model-native boundary（MM-C15）仍只作相邻机制视图，不被提升为独立成熟路线。
- **第二轮 mapping：** 1,191 个 gap-fill 实体已完成全量 screening，587 个进入既有字段图；它显著改变 cluster density，但没有产生新的一阶 leaf。低信号论文的独立语义抽审仍弱于第一轮。

<!-- synthesis:TIME-AUTO-07 claims:FND-C04,REP-C15 clusters:MM-C01,MM-C05,MM-C14 -->
