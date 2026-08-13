# 使用、反馈与技能记忆：经历何时能变成可复用的行为资产

> **深潜阅读路径：** 本页先画经验复用地图。trajectory、reflection、procedure、executable skill、meta-policy 的形成和执行机制见[从经历到程序和技能](skills-use/01-experience-to-procedure-and-skill.md)；Causal Memory、Raven、OpenViking、claude-mem、Engraphis 与 JARVIS-1 的固定版本边界见[系统 walkthrough](skills-use/02-system-walkthroughs.md)；Mem2ActBench、AFTER、PoisonedEvolution、迁移和供应链安全见[迁移、安全与前沿](skills-use/03-transfer-safety-and-frontier.md)。

Agent 不只会记住“发生过什么”，也可能从一次成功或失败中保留“下次怎样做”。例如，Agent 调用一个接口失败后，可以保存一段反思文字；也可以提炼成带前置条件的操作步骤；在更强的形态中，它会保存可执行脚本或能管理其他记忆的元技能。这些对象都会改变后续行为，因此它们比对话摘要多了一层风险：错误经验可能被迁移到新的任务和环境中。

本专题讨论**经验如何在使用后的反馈中演化成程序性记忆或技能**。它不包括只在当前会话存在的推理草稿和计划，也不把用户画像、共享权限或底层删除语义作为主体；但它与生命周期、安全、检索密切相连，因为任何可复用工件都需要版本、适用条件、撤回路径和受限执行。

## 从经验到技能，不是一次自动升级

`Reflexion` 的代表性做法是把任务反馈写成语言反思，下一次尝试时取回；模型权重本身不需要改变。`Voyager` 则把持久对象推进到可组合的代码技能库。较新的 `MemP` 明确区分原始轨迹、逐步指令和高层脚本，并分别处理构建、检索和更新；`MemSkill` 进一步区分两层演化：一层学习“怎样完成任务”，另一层学习“怎样构造和管理记忆”。

这条谱系带来的核心认识是：成功轨迹不是天然可信的程序。它可能只适用于当时的工具版本、权限、数据和任务条件；失败轨迹也可能恰好揭示了重要边界。2026 年 8 月的 `PoisonedEvolution` 预印本给出早期攻击证据：不可信贡献可以被自我演化流水线固化为持久工件。其度量聚焦工件的持久修改，而非真实有害行动；因此它不能证明普遍危害，却足以说明“从经历晋升为技能”是安全边界，而不是普通摘要操作。[v09 程序性记忆底稿](../../../agent-memory-v09/bundle/clusters/mm-c06-experience-procedural-memory-skills.md)

## 方案空间：复用单位越可执行，约束越重要

| 方案族 | 保存的工件 | 如何影响下一次行为 | 优点 | 主要风险与成熟度 |
|---|---|---|---|---|
| 原始轨迹检索 | 观察、动作、工具结果和结局 | 让模型重新阅读相似经历 | 可审计、细节完整 | 上下文成本高，模型自行归纳；工程常见 |
| 反思记忆 | 失败原因、启发式、自然语言规则 | 在提示中提供经验性提醒 | 表达灵活、无代码执行 | 适用范围模糊，可能把偶然经验泛化；较成熟研究形态 |
| 指令 / 流程提炼 | 有步骤的 instruction、script 或 playbook | 按当前参数适配并执行步骤 | 复用粒度更清晰，token 更省 | 需要版本、验证和反例；活跃方向 |
| 可执行技能 | 代码、工具调用模板、工作流 | 直接产生行为候选 | 可组合、可测试、可复用 | 依赖、沙箱、权限、回滚和副作用风险；条件成熟 |
| 元技能 / 管理策略 | 如何抽取、检索、更新其他记忆的规则 | 改变 memory 操作本身 | 能适应复杂任务流 | 归因和安全面最复杂；早期 |

这些类别不是从弱到强的单一路径。原始轨迹保留了最多证据，反思与流程提炼增加抽象，可执行技能则把抽象推到行动层；每前进一步，都需要更严格地表达前置条件、环境版本、依赖、允许的副作用和撤回方式。不存在现有证据支持的统一“最优记忆对象”。

## 五类复用工件内部怎样运行

### 1. 轨迹检索：把完整经验作为 in-context demonstration

系统将任务描述、环境版本、观察、动作、工具参数、结果、错误和人工反馈组成 episode。读取时先用任务/状态 embedding 或结构字段找相似 episode，再把关键步骤或完整轨迹放进当前上下文，让模型自行类比。管理主要是去重、分段、标注 outcome 和控制容量；它不主动假设哪一步是因果关键。

这种路线保留证据最完整，也最容易审计，但 token 成本高，失败步骤和成功步骤会一起进入 prompt。相似任务可能只在一个关键约束上不同，模型又可能复制过时参数。研究重点是 outcome-aware retrieval、counterexample pairing、trajectory segment credit 和首次行动评测，而不是单纯把成功轨迹数量做大。

### 2. 反思记忆：把 outcome 解释为语言规则

`Reflexion` 的循环是 `attempt → evaluator feedback → verbal reflection → next attempt`：反思被保存在 episodic buffer 中，下次与任务一起输入，而不更新模型权重。反思通常是自然语言诊断，例如“先检查 API 返回 schema，再生成调用参数”，读取时按任务或最近失败加载。

它实现简单、无可执行副作用，但抽象边界模糊：反思可能把偶然相关当成因果，也可能在不同任务中互相冲突。更严谨的管理需要让反思携带 source attempts、适用条件、支持/反例、版本与 confidence；多次重复也不能自动当作独立证据。当前工作正在研究 evaluator 质量、反思选择与跨任务迁移，而不是继续无限追加 self-critique。

### 3. 指令和流程提炼：从 trajectory 抽出有结构的 procedure

流程路线将多条轨迹对齐，识别稳定步骤、输入/输出 schema、分支条件和错误恢复，生成 instruction、script 或 playbook。`MemP` 明确区分 trajectory、step-by-step instruction 和 high-level script，并为不同工件设置构建、检索与更新流程。读取先匹配任务和前置条件，再参数化变量；执行结果回写到该 procedure 的 success/failure history。

相比反思，它更节省 token，也更容易做静态检查；但 distillation 可能删掉少见而关键的分支。最新 [AFTER/procedural-memory 研究](https://arxiv.org/abs/2606.23127) 用 382 个任务、六种角色和 22 类技能，将 local improvement、cross-task、cross-role 与 cross-model transfer 分开，显示有些技能能迁移，有些会角色特化。这个结果属于作者协议，但它把“技能是否可复用”从单任务成功推进到受控迁移评测。

### 4. 可执行技能：把经验编译为代码或工具模板

可执行技能通常是带 manifest 的函数、脚本或 workflow：声明入口、参数、依赖、工具/API 版本、允许的资源和测试。`Voyager` 在 Minecraft 中让 curriculum 产生任务，迭代生成可执行代码，验证成功后把技能按描述嵌入并存入 library；复杂任务再组合已有技能。现实 Coding Agent 还会把技能落为 repository-local command、hook 或 MCP tool。

可执行性带来可组合和可测试，也让 memory 直接靠近副作用。检索到技能只产生行为候选：当前 principal 仍需重新授权文件、网络、凭据和支付权限；依赖和 schema 要在运行前核验；失败要区分代码缺陷、环境漂移和任务不适用。沙箱测试也不证明 production 数据和权限下安全。研究前沿正集中在 typed effect、capability manifest、sandbox-to-live promotion、dependency repair 和撤销传播。

### 5. 元技能与管理策略：学习“如何形成和治理其他记忆”

`MemSkill` 把两层演化分开：task-level skill 解决任务，meta-memory skill 学习怎样抽取、合并和修剪记忆；`MemCon`/AgeMem 一类控制器则学习何时调用 retrieve、consolidate、forget 等操作。它们的 state 包括任务、已有记忆、预算和历史反馈，policy 输出 memory operation，结果再用于更新 policy。

这是能力最广也最难归因的路线。若最终任务成功，无法直接知道是技能内容、检索器还是 memory policy 起作用；若 policy 删除了未来有用内容，反事实很晚才出现。更可控的方向是让元策略只操作可版本化 primitive，用 policy log 记录每次 proposal 和结果，并在 offline replay、shadow mode 或可回滚范围内学习。

## 一条可解释的数据流

```text
任务轨迹、工具结果、人工反馈
              │
              ▼
      事件记录：任务、环境、主体、动作、结局、失败
              │
              ▼
 候选提炼：反思 / 指令 / 脚本 / 可执行技能
              │
              ▼
 晋升与版本：来源多样性、适用条件、测试、风险状态
              │
              ▼
  当前任务：先过滤环境与权限，再检索并参数化候选
              │
              ▼
  受限执行与结果回写 ───────────────► 更新、弃用或回滚
```

读取时，语义相似只回答“它看起来像不像”；适用性还要检查用户/团队边界、任务类别、工具/API/数据 schema 版本、环境依赖、许可证和风险等级。可执行技能提供的是候选行为，不继承文件、网络或支付等执行权限；这些权限只能在当前行动点重新核对。失败结果也不应直接把某个技能整体删除或无限强化，而要区分“技能本身错误”“环境已变”“任务其实不适用”“执行权限被拒绝”。

固定版本的工程检查让这些责任可以在代码层看见。`Raven` 将 host loop、memory backend、插件发现和 skill synthesis 分开，turn 前取回、turn 后写入反馈；`OpenViking` 将 memory、resource 与 skill 置于统一资产层，内容先写入，再异步生成多层语义表示，处理尚未完成时可能暂时不可召回。这些观察能说明架构形状和集成边界，不能替代实际运行、安全测试或生产采用证明。[v09 项目与工程材料](../../../agent-memory-v09/bundle/clusters/mm-c06-experience-procedural-memory-skills.md)

## 当前主流、近期变化与成本

保留原始轨迹、以检索辅助后续提示或计划，是最直观也最常见的形态；反思文本和可复用步骤已有较清晰的研究谱系。近 12 个月的变化在于把轨迹进一步蒸馏为指令/脚本、把记忆操作本身纳入学习策略，以及在多模态任务中分别处理动作级经验和任务级技能。研究截止日前约 90 天的最强新信号不是新的技能库规模，而是晋升投毒的初步实证和由此暴露的安全、度量边界。[v09 趋势雷达](../../../agent-memory-v09/bundle/reports/06-github-trend-radar.md)

成本不能只算取回时的 token：还包括轨迹存储、提炼模型调用、验证和沙箱运行、注册表与索引、当前环境中的参数适配、人工审核、回滚以及受污染工件的处置。当前没有同一任务、模型、预算下比较轨迹、反思、流程、代码技能和元策略的完整成本账本。因而“自我演化一定降低成本”在现有证据下并不成立。

典型失败包括：把一次成功错误地推广到不同工具版本；从相似但越界的用户或团队迁移做法；技能依赖在环境更新后失效；重复或协调的轨迹把恶意规则伪装成共识；可执行工件获得了它本不应有的行动权；仓库只发布评估快照而未公开真正的在线学习路径。`JARVIS-1` 的公开快照即提醒读者：有“记忆”目录或论文 lineage，并不等于完整的可运行持续演化系统。[v09 工程边界记录](../../../agent-memory-v09/bundle/clusters/mm-c06-experience-procedural-memory-skills.md)

## 真实工程形状：研究算法怎样落到运行时

工程系统通常把四个表面分开：host loop 捕获 turn/tool outcome；memory backend 保存 episode 与对象；skill registry 管理可复用工件；runtime 在当前权限下加载和执行。固定版本的 `Raven` 就将 host loop、MemoryBackend protocol、plugin discovery 与 skill synthesis 分开，turn 前 recall、turn 后写回；[OpenViking](../projects/volcengine--openviking.md) 将 resource、memory 和 skill 放在统一资产层，内容先持久化，再异步生成多层语义表示；处理未完成时可能暂时不可召回。

这种分层暴露出具体集成边界：backend adapter 要维持 user/agent identity；异步 pipeline 要提供 processing state 和 watermark；registry 要保留 source、version 与 deprecation；host 不可把 skill payload 当成权限。当前开源仓库能展示这些接口和固定代码路径，却很少公开跨版本 migration、sandbox escape、安全 promotion 或独立生产采用结果。

## 最新研究议程：从“记住经验”到可治理的能力供应链

近 12 个月的重点已经明显转移：

| 研究问题 | 旧评测的不足 | 新方向 | 仍缺的证据 |
|---|---|---|---|
| 什么是可复用单位 | 只比较有/无 memory | trajectory、reflection、instruction、script、skill 分层 | 同轨迹、同预算的独立消融 |
| 能否迁移 | 只在原任务重试 | cross-task、cross-role、cross-model、组合技能 | 工具/API 漂移和长期迁移 |
| 如何晋升 | 成功一次就写入 | 多来源支持、测试、risk state、shadow/promotion | 何种证据阈值能抑制误晋升 |
| 如何治理执行 | 把技能文本直接塞进 prompt | manifest、typed effect、沙箱、action-time authorization | 从 recall 到真实副作用的端到端安全实验 |
| 如何自我演化 | 只优化任务 reward | constrained meta-policy、version/rollback、trajectory metrics | 长期 regret、不可逆操作和分布外稳定性 |

2026 年 8 月的 [PoisonedEvolution](https://arxiv.org/html/2608.05563v2) 将不可信轨迹写入持久技能的风险变成了可测信号；AFTER 将技能迁移拆成多个维度。下一步不是证明“Agent 会写 skill 文件”，而是建立从 evidence → distillation → validation → promotion → retrieval → authorized execution → outcome → deprecation 的完整、可归因供应链。

## 如何判断它真的帮助了 Agent

仅看最终成功率无法区分：Agent 是读到原始经历后临时推理成功，还是确实因程序性工件而首次就采取了正确行为。相对有解释力的评测会让不同形态接受同一批轨迹与反馈，再比较无记忆、原始轨迹、反思、流程/脚本、可执行技能和元策略；并额外观察组合迁移、近似但不适用的任务、过期工具版本、失败样本、撤销回滚和对抗性轨迹。

`ImplicitMemBench` 关注首次尝试，`MemoryArena` 观察先前行动和反馈是否改变后续决策，`Mem2ActBench` 检查长期约束是否进入工具选择和参数。它们和安全实验的任务单位不同，不能相加为“技能记忆总分”。特别是，工件被成功写入不等于它已触发有害行动；这两层需要分别测量。[v09 基准地图](../../../agent-memory-v09/bundle/reports/07-benchmark-map.md)

## 共识、争议与未解问题

当前较稳定的判断是：只有会改变后续选择或动作的持久工件，才可称为程序性记忆；原始轨迹与派生技能应可区分、可回溯；技能需要适用条件、版本、来源、结果和弃用状态；工件本身不能自动继承执行权限。争议仍在于反思、流程、代码技能还是管理策略在跨任务迁移中更有效，何时可以自动晋升，多模态/环境 grounding 如何携带，以及团队共享下的许可证、主体边界和撤回语义。

最重要的未解问题是缺少独立的匹配实验来比较不同复用单位；缺少面对工具/API/schema 变化的弃用和修复评测；也缺少从“污染工件被写入”延伸到触发、权限、凭据和真实副作用的完整安全链路。它们影响的不是一个小优化，而是我们能否把经验视为可复用资产，还是只能把它视为待审查的候选。

**暂定判断：** 经验记忆已经从语言反思扩展到流程、可执行技能和管理策略，但工件越接近执行，证据、权限、验证和回滚的要求越高。轨迹与反思属于可理解的成熟研究形态；流程与技能注册处于快速工程化阶段；自动晋升和元策略演化仍受安全、迁移和成本证据限制。本判断是描述性的，不构成部署或选型建议。
