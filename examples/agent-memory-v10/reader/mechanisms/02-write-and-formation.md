# 写入与记忆形成：什么内容有资格成为未来状态

> 本文关注 Memory 的写入入口：从对话、工具结果或环境观察到可被后续使用的持久状态。它不把“模型生成了一段摘要”自动等同于“系统形成了可靠记忆”。底稿见 [v09 生命周期报告](../../../agent-memory-v09/bundle/clusters/mm-c05-lifecycle-consolidation-forgetting.md)、[控制面报告](../../../agent-memory-v09/bundle/clusters/mm-c01-memory-services-control-planes.md) 和 [个性化报告](../../../agent-memory-v09/bundle/clusters/mm-c08-personalization-identity-conversational-continuity.md)。

## 为什么 `add(memory)` 不够

一次客服会话里，用户可能说出偏好、临时情绪、错误陈述和敏感数据；一次 Coding Agent 工具调用可能同时包含可复用的构建步骤、失败日志、机密令牌和过期分支信息。若系统把所有内容即时总结并写入，短期内似乎“记住得更多”，长期却会积累三种债务：模型的推断被伪装为事实；不该共享或不该保留的内容进入索引；错误状态被后续检索和行动放大。

所以写入的核心问题不是吞吐量，而是**形成**：原始输入怎样被保留、抽取、分类、核验、提交，并和之后的修订连接。MemoryBank 的 storage/retrieval/updating 分离奠定了这个问题；较新的 [MemTxn](https://arxiv.org/abs/2607.27834) 把“有来源支撑的写入验证”和可恢复的状态边界显式化；[MemCon](https://arxiv.org/abs/2607.13591) 则把写入、合并、遗忘等操作看成会随任务在线选择的动作。它们代表一条清晰趋势：写入从文本管道变成状态转移。

## 方案家族：自动化程度不同，失误位置也不同

| 写入路线 | 如何形成记忆 | 擅长处理 | 主要代价和失败模式 | 证据状态 |
|---|---|---|---|---|
| 直接保留原始记录 | 将对话、工具结果、观察按时间追加 | 可追溯性、低语义误判、日后重建 | 量大、检索噪声和隐私面扩大 | 基础且成熟，但不是完整 Memory 系统 |
| 摘要/反思驱动 | 模型把多段经历压缩成摘要、偏好或反思 | 长历史压缩、显式高层语义 | 丢失细节、把推断写成事实、难以纠正 | 工程广泛，效果高度依赖预算与检索 |
| 类型化抽取 | 把输入拆成事实、事件、画像、实体关系、程序候选 | 更新语义、定向访问、关系查询 | schema 设计、抽取误差、对象混淆 | 当前主流方向之一，跨实现一致性尚弱 |
| 来源支持与准入 | 在提交前核验来源、主体、策略、重复/冲突和风险 | 污染控制、版本化、审计与回滚 | 延迟、模型/规则成本、误拦截与漏拦截 | 控制面共识增强，端到端防护仍早期 |
| 反馈或策略学习 | 用任务结果改变何时写、合并、遗忘或保留 | 可变负载与预算下的自适应 | 探索错误被持久化、跨域漂移、难解释 | 近一年强信号，独立复现不足 |

这些路线常被组合，但组合本身不构成“更先进”。例如，原始事件可与类型化对象并存：前者保存证据，后者是可被当前查询使用的投影。真正的差异在于写入失败时是否能知道发生了什么、能否撤回以及派生索引会不会继续泄露旧状态。

## 五类写入路线到底怎样运行

### 1. 原始保留：确定性 capture，而非语义判断

最简单的写入路线把 turn、tool call、tool result 或观察包装成带 `source / subject / session / timestamp / content hash` 的事件后追加。它不调用 LLM 判断重要性，也不改写已有内容；可选的 chunk、关键词或 embedding 只是索引。读取时返回原始片段，由当前模型完成解释。

它的优势是写入便宜、可回放，而且不会在形成阶段主动制造“用户事实”。缺点也很具体：历史线性增长，跨 session 的同一事实分散在多个位置，隐私和检索噪声不断累积。近期系统研究把它保留为必要基线，因为 [Agent Memory systems characterization](https://arxiv.org/abs/2606.06448) 显示，BM25/embedding 这类确定性构造在作者的统一 harness 中拥有完全不同于 LLM 抽取路线的成本形状；这不是性能冠军证明，而是提醒形成算法必须把 write-path 成本列入比较。

### 2. 摘要与反思：用生成模型形成更高层对象

摘要路线一般按 turn window、session boundary 或 token threshold 触发：取一段历史和已有摘要，要求模型生成新摘要、显著事件或反思，再把它作为独立对象保存。递归摘要会把旧摘要与新内容继续合并；分层摘要则保留 session、topic 和 global 多个粒度。`Generative Agents` 以 observation importance 触发 reflection，`MemoryBank` 生成 event summary 与 evolving assessment，`SimpleMem` 则把滑动窗口变成带 semantic、lexical 和 structured view 的 distillation entry。

这类方法减少 query-time prompt，但把成本和风险移到 construction：每个窗口都可能产生 LLM prefill；早期压掉的专名或限定词以后无法召回；递归摘要会放大旧误差；“重要”又高度依赖当时任务。它适合需要压缩和高层解释的历史，但不能代替原始证据。当前研究正在做的是**预算相关的 operator selection**：在什么 query volume、token 预算和更新频率下应该 retain、summarize 或 consolidate，而不是默认越早摘要越好。

### 3. 类型化抽取：先构造候选，再决定对象关系

类型化路线通常分两次判断。第一步把原输入抽取为原子事实、事件、画像属性、实体/关系或 procedure candidate；第二步检索相关旧对象，判断新候选是 `ADD`、`UPDATE`、`MERGE`、`CONTRADICT` 还是 `NOOP`。`Mem0` 的 consolidating fact store 是这一模式的典型；[AtomMem](https://arxiv.org/abs/2606.19847) 进一步从 selective atomic facts 生成 event、temporal profile 与 associative graph；[A-MEM](https://arxiv.org/abs/2502.12110) 则会在新 note 到来时分析历史链接并更新邻近 contextual representation。

粒度选择决定后续所有成本。事实切得太粗，更新一小项会覆盖无关内容；切得太细，读取必须跨许多对象重新拼接，关系和 provenance 数量迅速增长。entity resolution 错误会把不同主体合并，relation extraction 错误会制造虚假多跳路径。最新研究因此不只提高抽取 F1，而是在研究 typed object、stable identity、temporal version 和 dependency edge 如何共同进入 state transition。

### 4. 来源支持与事务准入：把 LLM 输出降为 proposal

准入路线不让抽取器直接写入当前视图。每个 candidate 必须带 source span 或 tool receipt，并依次通过 schema、identity/scope、policy、duplicate/conflict、security 和 budget 检查。通过后，系统产生 revision 与 commit receipt；权威记录先提交，embedding、summary、graph 等投影按该 revision 异步构建。任一步失败都应可重试或回滚，而不能留下“主表没有、向量索引有”的幽灵状态。

[MemTxn](https://arxiv.org/abs/2607.27834) 把 source-supported validation、temporal version selection 和 durable snapshot journal 放在 answer model 外部；[MemState/GEM](https://arxiv.org/abs/2605.26252) 则把 content、typed structure 与 declarative evolution policy 同时放进 state，并在 commit 前检查 postcondition。前者强调恢复边界，后者强调 trajectory-level correctness。两者都是预印本/原型方向，尚没有跨后端的独立恢复与并发实测。

### 5. 学习型控制：把“做哪种写入动作”变成策略

策略路线把 memory operations 暴露为动作集合，例如 retain、retrieve、re-retrieve、inject plan、consolidate、forget、no-op。controller 根据当前任务、已有状态、预算和反馈选择动作，奖励来自任务成功、记忆质量或成本。[MemCon](https://arxiv.org/abs/2607.13591) 展示了这种 MDP 式控制；Agentic Memory/AgeMem 一类工作还把短期和长期记忆操作作为 tool actions，用分阶段训练或强化学习学习何时调用。

真正困难的是 reward delay 和不可逆副作用：当前任务成功不表示写入对未来任务有益；忘掉内容后很难观测反事实；controller 可能通过少写或过度压缩取得短期成本奖励。较可信的研究方向是**受约束控制器**：策略只提议操作，版本、权限、来源和恢复层仍决定能否提交，并以跨 session 的 trajectory 指标而非单次答案评分。

## 一条可解释的形成链

写入链可用下列顺序解释。它是一种通用架构模型，不是任何单一产品的固定实现。

```text
捕获原始输入
  → 绑定来源、主体、时间和用途
  → 提取一个或多个候选对象
  → 校验/去重/冲突识别/隔离
  → 产生可回放的提交与版本
  → 生成摘要、向量、关键词和图等派生索引
  → 记录策略、模型、索引和成本观测
```

**捕获**的含义是保留发生过什么，而不是立即相信其中每个断言。对话轮次、工具输出、传感器观察和人工导入的可信度不同，来源类别本身应被记下。

**绑定上下文**是在 LLM 抽取前确立主体、租户、会话、时间和可见范围。否则一个语义正确的抽取结果，也可能在错误的用户、项目或团队中生效。

**提取候选**把一段输入变为可能的事件、事实、偏好、关系或程序。这里的“候选”很重要：抽取器的产物不是无条件真值。[AtomMem](https://arxiv.org/abs/2606.19847) 用原子事实作为进入事件、画像和关联图的粒度；[A-MEM](https://arxiv.org/abs/2502.12110) 把结构属性、动态链接和历史演化并入笔记构造。两者显示了减少“大块摘要”歧义的方向，也把错误空间从 chunk 切分转移到事实切分和关系判断。

**准入**决定候选能否成为权威状态。常见检查包括 schema 是否完整、来源是否足以支持断言、是否与既有记录重复或冲突、是否超出保留/共享策略、是否疑似提示注入或恶意污染。高风险候选可处于隔离状态而非直接暴露给检索。

**提交和派生**最后才把通过检查的版本写入权威状态，并由这一版本构建可重建的摘要、向量、关键词和图索引。这个先后关系使“索引里出现了什么”不再等于“系统正式相信什么”。

## 写入控制与安全边界

持久写入是一条安全边界，因为被写入的内容可能在许久之后被检索并影响工具调用。v09 的安全材料收录了从 write 到 retrieve 再到 action 的攻击链；它支持的结论是攻击面跨越输入、状态、检索、提示和行动，而不是“给每条记忆打一个安全分就够了”。[OWASP Agent Memory Guard](https://github.com/OWASP/www-project-ai-security-and-privacy-guide) 所呈现的 detector、policy、rollback 等控制点可以解释为可插入的防线，但它们本身不证明端到端安全已解决。

来源记录也不是内容真实性证明。签名或前驱链能说明某次变化由谁做出，却不能保证内容正确；时间顺序能说明先后，却不能自动判定新陈述在语义上推翻旧陈述。对于个人画像，`observed`、`asserted`、`inferred` 的分离尤为重要：用户说“我可能喜欢 X”与模型从点击行为推断“用户喜欢 X”不应拥有同样的保留、共享和行动资格。

## 真实工程实现：可见形状与看不见的保证

固定版本的开源代码显示了几种形成路径。[Mem0](https://github.com/mem0ai/mem0) 文档公开了通过模型、embedding、向量后端和 reranker 组成的记忆处理面，并保留历史记录；[Causal Memory](../../../agent-memory-v09/bundle/projects/jingxuanc-causal-memory.md) 的工程检查呈现原始日志、原子事实和决策—结果边的组合；[AtomicMemory](https://github.com/atomicstrata/atomicmemory) 是近期的类型化后端候选。它们能帮助读者观察接口、依赖和数据流，却没有被本次底稿执行，也没有独立运行、删除传播或攻击抵抗证据。

工程上最容易被忽视的是失败后的回路。写入模型调用失败时，是否留下半成品？索引先于权威记录更新时，能否重建？纠正一条事实后，之前的摘要、图边和技能是否还引用它？同一 API 在不同后端上是否改变去重、过滤或事务语义？这些都是“记忆形成”而非单纯数据库问题。

## 当前主流与近期信号

当前常见做法已不只是保存原对话，也会形成摘要、事实或画像；近期系统更常把事件、语义状态和过程性经验分开。过去十二个月的增量集中在原子事实构造、来源支持的写入、版本/快照边界，以及按预算选择保留或合并操作。近 90 天中，MemTxn 和 MemCon 让“控制器决定何种记忆操作”成为鲜明信号；但两者都不应被读成已经稳定的通用基础设施：前者是作者提出的事务协议，后者是尚缺独立长期复现的学习控制策略。

成熟度同样需要拆分。保留输入证据、记录来源和把派生索引视为可重建材料，是较稳定的工程原则；抽取事实/画像并做去重是工程中等成熟的模式；自动决定何时遗忘、自动修复冲突或让学习策略拥有不可逆删除权限，仍处于早期，且安全代价尚未被充分量化。

## 最新研究究竟在推进什么

近期工作可以按正在改变的写入层归纳，而不是按论文名排列：

| 正在推进的层 | 旧做法哪里不够 | 当前尝试 | 还缺什么 |
|---|---|---|---|
| 构造粒度 | chunk/摘要把多个断言粘在一起 | 原子事实、typed event/profile/procedure、关系化候选 | 对粒度错误、entity merge 和 provenance loss 的共同评测 |
| 提交语义 | LLM 抽取结果直接 upsert | source-supported proposal、版本选择、journal/snapshot | 并发、崩溃、跨 backend 的独立恢复实验 |
| 操作选择 | 固定 token/时间阈值触发摘要或删除 | budget-dependent retain/consolidate、learned operation policy | 同任务、同预算、长期 horizon 下的净收益与误操作率 |
| 安全准入 | 只在输入时做一次检测 | quarantine、policy gate、promotion check、rollback | 从恶意写入到实际行动的完整攻击/防御链 |
| 系统成本 | 只报告回答准确率和 query token | construction/retrieval/generation 分阶段 profiling | 可公开复放的多系统 harness 与全生命周期成本账本 |

这里最重要的新认识来自系统视角：[2026 年的系统表征研究](https://arxiv.org/abs/2606.06448) 把十类系统分解为 ingestion、construction、storage、retrieval、prompt assembly、generation 和 maintenance，并显示复杂方法往往把成本从读时搬到写时。它的具体数字只适用于作者的模型、适配和硬件设置，但“必须同时测 construction 与 serving”应成为形成机制的最低解释要求。

## 反例：更多处理不必然形成更好的记忆

形成链的主要反例来自预算与检索条件。[关于 budgeted consolidation 的研究](https://arxiv.org/abs/2607.17545) 把保留原始细节与合并后的 token 覆盖视为相互制约的目标；而 [LightMem 的独立复现](https://arxiv.org/abs/2607.29104) 发现，在固定存储的设置中，检索器、候选深度和 token 上限足以改变结论，原始轮次在匹配深度下常常更强。这意味着“先摘要再存”并不存在无条件的优势，也说明实验中若未匹配模型调用和上下文预算，就无法把提升归因给形成算法。

写入更积极也可能更危险：错误合并会抹掉 query-critical 细节，错误抽取会制造持久臆测，错误隔离会让有效信息永远不可见，学习控制器可能把短期奖励误当长期价值。因而“形成得更多”与“后续行为更可靠”是两个不同命题。

## 未解问题

第一，缺少跨后端、同任务流、同模型预算的对照，尚无法量化从原始记录升级到类型化准入和自动合并的净收益与净成本。第二，来源支持、冲突判断、隐私过滤和恶意写入检测分别有研究与工程线索，但缺少把它们放进同一长生命周期的独立验证。第三，模型生成的推断何时可以升级为可行动的状态，仍没有跨场景通行的语义标准。第四，纠正和删除在派生摘要、向量、图、缓存、备份和工具轨迹中的传播，公开可检验的证据依然稀缺。

这些空白意味着，阅读一个系统的写入能力时，应区分它是否仅能“生成并保存摘要”，还是能说明候选从何而来、何时生效、如何修订，以及哪些后续表示和行动会受其影响。
