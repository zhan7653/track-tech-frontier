# Agent Memory 七层架构重写问答记录

**目标文档：** `2026-08-25/reader/01-input.md` 至 `07-feedback-learning.md`，以及对应总览与层级地图  
**记录开始：** 2026-08-25  
**状态：** 问答进行中；尚未开始按本记录重写七层正文

## 记录规则

每轮问答保存以下内容：

1. 用户问题；
2. 回答；
3. 用户随后确认、修正或否定的结论；
4. 对七层正文的影响；
5. 状态：`待确认`、`部分确认` 或 `已确认`。

只有用户确认后的结论才能作为七层正文的写作约束。后续修正覆盖旧判断，但保留变更记录，避免把讨论中的临时解释误写成定论。

## 已确认的写作基线

### B001 — 从具体实现反推每层职责

TencentDB Agent Memory 与 Codex Local Memory 已经显示，七层并不是只能写成抽象分类。每层都可以落到具体对象、Prompt、状态、输入、输出、触发器、读取方式和失败边界。

**状态：** 已确认

### Q001 — 第一层的主要输入是否就是对话与工具轨迹

**用户问题**

> 从 TencentDB 与 Codex 两个架构来看，本质上形成 Memory 的输入还是以对话为主，也就是 `user input / assistant response / tool call / tool result`。是否正确？

**回答**

如果讨论的是两套系统共同的“经验型长期 Memory”主干，这个判断正确。更准确的名称不是狭义“对话”，而是**带顺序的交互—执行轨迹**：

```text
user input
→ assistant response
→ tool call
→ tool result
→ 后续 assistant response / 下一轮 user input
```

TencentDB 将它拆成两条输入链：Chat Memory 的 L0 主要接收 `user/assistant`；Skill 链接收 `user/assistant/tool_call/tool_result`。Codex 则把这些事件共同保存在 Rollout 中，再由 Phase 1 过滤和抽取。因此二者的共同原材料确实是用户与 Agent 的真实交互及执行证据。

四类事件的证据含义并不相同：`user input` 是意图、约束、偏好与纠正的主要证据；`assistant response` 可能只是建议或推断，不能因被说出就升级为事实；`tool call` 证明尝试了某个动作，不证明成功；`tool result` 才提供环境观察与执行结果。形成层必须保留这种角色差异。

但七层通用架构不能把它写成唯一输入。第一层应区分：

1. **主输入 payload：** `user input / assistant response / tool call / tool result`；
2. **必要 envelope：** user、agent、team、thread/session/task、时间、cwd、branch、commit、工具/环境版本、权限与 outcome；这些决定来源、作用域和适用条件；
3. **其他输入通道：** 外部文档、代码仓库、用户显式 remember/update/forget、外部 Agent 导入或环境事件；它们不是两套经验提炼主干的中心输入，但属于完整 Agent Memory 输入层；
4. **默认排除或降权：** system/developer 指令、已经注入过的 Memory/Skill、秘密和纯控制事件，避免递归学习、把系统规则误当用户事实或造成污染。

建议第一层的中心定义写成：

> Agent Memory 的主要原始输入，是带身份、任务、时间、环境版本和来源信息的交互—执行轨迹；其核心事件为用户输入、Agent 回复、工具调用和工具结果。文档、代码、显式更新与外部事件构成补充输入通道。

**影响章节**

- `01-input.md`：第一层中心定义、主输入事件、上下文 envelope、扩展输入和排除规则；
- `02-write-formation.md`：不同形成链如何从输入事件中筛选实际送入 Prompt 的内容。

**状态：** 已确认；共同主输入结论成立，扩展输入分类以 Q002 的纠正为准

### Q002 — 外部文档、显式更新、外部 Agent 与环境事件分别来自哪里

**用户问题**

> 外部文档、代码仓库是 TencentDB 涉及的；那么显式 `remember/update/forget`、外部 Agent 导入和环境事件分别是什么来源？

**回答**

上一轮把不同性质的项目混入了“第一层输入”，需要拆开：

1. **外部文档、代码仓库：来自 TencentDB 的独立资产形成链。** 文档经上传与 ingest 进入 Wiki；代码仓库经 clone/index/sync 进入 CodeGraph。它们不是 Chat Memory/Skill 共同的对话输入，而是 TencentDB 特有的非对话知识输入。
2. **显式 `remember/update/forget`：主要来自 Codex 的用户控制路径。** 用户明确要求后，主 Agent 只能在 `extensions/ad_hoc/notes/` 写一条 note，之后由 Phase 2 读取并修改正式 Memory。它绕过自动 Phase 1，不应与原始经验输入并列，更适合放在“管理与演化层”的 mutation/control input。
3. **外部 Agent 导入：来自 Codex 固定版本中的 `ExternalAgentMemoryImport` 实验路径。** 它把其他 Agent 的项目记忆作为带 cwd scope 的材料交给同一 Phase 2；该功能标为 UnderDevelopment、默认关闭，只能作为互操作前沿，不能写成稳定主输入。
4. **环境事件：不是 TencentDB 与 Codex 共同存在的独立输入通道。** Codex Rollout 虽含 WorldState 和内部事件，但 Phase 1 会过滤这些记录；真正保留下来的环境证据主要已经表现为 `tool result` 与 cwd/branch/commit metadata。TencentDB 的仓库 commit 变化由 CodeGraph sync 处理，仍属于代码输入。把“环境事件”另列为共同输入，是从更广泛 world-state/embodied Memory 研究外推，不能用于这两个案例的核心归纳。

据此，第一层应暂时收窄为：

```text
共同主输入：交互—执行轨迹
  user input / assistant response / tool call / tool result

共同必要上下文：
  identity / thread / task / time / scope / environment revision / outcome

实现特有的额外形成源：
  TencentDB：文档 → Wiki；代码仓库 → CodeGraph

不属于第一层共同原始输入：
  Codex remember/update/forget → 管理层控制输入
  ExternalAgentMemoryImport → 默认关闭的互操作扩展
  泛化 environment events → 当前两案例证据不足
```

**影响章节**

- `01-input.md`：删除没有案例支撑的泛化输入清单，明确共同主输入与实现特有输入；
- `04-management-evolution.md`：承接显式 remember/update/forget；
- 互操作/前沿部分：承接 ExternalAgentMemoryImport；
- world-state 场景若保留环境事件，必须单独举证，不从 TencentDB/Codex 推导。

**状态：** 已确认

### Q003 — 近期前沿是否出现新的 Memory 输入形式

**用户问题**

> TencentDB 与 Codex 的共同输入已经确定。此前文档还要求调研近期前沿技术，其中是否出现了新的输入形式？

**回答**

有，但应区分“新 payload”“新采集单元”和“新 envelope”。近期研究并没有推翻 `user/assistant/tool call/tool result` 这条主干；主要把它扩展到以下形态。

#### A. 真正新增的原始 payload

1. **视觉落地的 Agent 轨迹。** XSkill 的形成输入不再只有文本日志，而是把视觉观察与文本推理、工具调用、工具结果和任务 outcome 放在同一轨迹中；抽取时需要说明哪一个视觉状态触发了哪一个动作。
2. **环境/世界状态变化轨迹。** WorldLines 的输入同时含 dialogue、action、execution feedback、object/device state change，并保留 observer/visibility；关键不是多一段文本，而是区分直接观察、他人报告和动作后状态。
3. **跨应用的环境交互事件流。** OpenAI Computer History 从允许的应用与网站捕获 click、typing、keyboard shortcut、app switch 和 accessibility context，再形成本地 Memory。它明确不采集 screenshot、microphone 或 system audio。这是“用户与电脑的行为流”，而不是 Agent Chat。

#### B. 输入 payload 未变，但采集单元发生变化

4. **带 outcome 的多路径 Rollout 集合。** XSkill 针对同一任务采集多条成功/失败路径，再做 cross-rollout critique。输入单元从“一条会话轨迹”变成“同一任务的多个备选轨迹及其结果”，使系统可以区分偶然步骤和跨路径稳定经验。
5. **多主体的私有/共享轨迹。** 多 Agent Memory 仍以 message、tool result 和 artifact 为主，但同一内容来自不同 producer，并带 recipient/audience、private/shared visibility、authority 和共享 transition。它不是新模态，而是新的采集拓扑。

#### C. 不是新输入形式，而是更丰富的 envelope

近期 provenance/state 研究要求每条输入额外携带 observer、producer、source pointer、scope、purpose、valid time、transaction time、policy、action risk、dependency 和 outcome。这改变了后续能否提交、共享、撤回和用于行动，但 payload 仍可能只是同一条文本或工具结果。

据此，第一层可以采用如下结构：

```text
共同基线：
  对话—执行轨迹
  user / assistant / tool call / tool result

新 payload：
  visual observation
  world/object/device state change
  ambient computer interaction event

新采集单元：
  outcome-labeled multi-rollout set
  multi-agent private/shared trajectory

增强 envelope：
  observer / producer / audience / provenance / scope / time / policy / risk
```

不能把以下派生物误写成输入：世界状态图、Experience Bank、Skill Library、长期画像和摘要都是形成/表示阶段的输出；第一层输入只是它们所依赖的原始观测、事件和轨迹。

**主要证据**

- XSkill：`https://arxiv.org/abs/2603.12056`
- WorldLines：`https://arxiv.org/abs/2606.18847`
- OpenAI Computer History：`https://learn.chatgpt.com/docs/customization/computer-history`
- 多 Agent/private-shared/provenance 边界：v10 多 Agent 场景与 v09 shared-memory 深潜

**影响章节**

- `01-input.md`：按“共同基线 / 新 payload / 新采集单元 / 增强 envelope”重建输入地图；
- 多模态与具身场景：提供视觉与世界状态的完整输入示例；
- 多 Agent 场景：把 producer/audience/visibility 作为输入 envelope，而不是新记忆类型；
- `02-write-formation.md`：解释这些原始输入如何形成世界状态、experience、skill 等派生对象。

**用户确认与收窄**

输入层的前沿补充保留前述第一类“真正新增的原始 payload”中的三项，并合并简略说明、不作为重点：

1. 视觉观察进入 Agent 执行轨迹；
2. 世界、对象或设备的状态变化与动作反馈进入长期轨迹；
3. Computer Use/Computer History 的点击、输入、快捷键、应用切换和 accessibility context 等操作事件流。

后续两类不写：不展开 outcome-labeled multi-rollout、多 Agent 私有/共享采集拓扑，也不单独讨论 provenance、policy、risk 等增强 envelope。

第一层最终写作范围据此收敛为：

```text
重点：
  user input / assistant response / tool call / tool result
  + 必要身份、任务、时间和环境定位

实现补充：
  TencentDB 文档 → Wiki、代码仓库 → CodeGraph

前沿简短补充：
  visual observation
  world/object/device state change + action feedback
  computer-use interaction event stream

不写：
  multi-rollout / multi-agent topology / enhanced governance envelope
```

**状态：** 已确认；简写三种新增原始 payload，其余前沿输入候选删除

### Q004 — 输入层之后是否是写入层

**用户问题**

> 下一层是写入吧？

**回答**

是。七层架构的第二层应称为**写入与形成层**。它不是物理意义上的 `INSERT` 或写文件，而是把第一层原始输入变成可进入长期状态的对象：

```text
第一层输出：
  对话、工具轨迹、视觉/状态/Computer Use 事件、文档或代码输入
        ↓
第二层：写入与形成
  触发 → 筛选 → 抽取 → 分类 → no-op/准入 → 形成候选或初始 Memory
        ↓
第二层输出：
  带内容、类型、来源与作用域的 Memory 候选或已提交对象
```

这一层的中心问题是：

> 原始经历中的什么值得长期保存，以及应被写成什么形式？

它应重点解释形成 Prompt、最低信号门槛、过滤/脱敏、事实与偏好/程序的分类、输出 schema、候选与最终 Memory 的区别，以及输出怎样交给状态/存储层。

边界上：

- 第一层只说明“收到了什么”；
- 第二层决定“从中形成什么”；
- 第三层说明“形成结果以什么状态和索引保存”；
- 已有 Memory 后续怎样合并、修正、版本化和遗忘，主要留给第四层“管理与演化”。

Codex Phase 2 和 TencentDB L2/L3 同时具有形成与后续管理属性，具体如何跨第二、第四层归位，需要后续问答确认，不能按函数名机械切分。

**影响章节**

- `02-write-formation.md`：第二层主章节；
- `03-state-storage-indexing.md`：只承接形成结果的持久状态；
- `04-management-evolution.md`：承接已有 Memory 的后续变更。

**状态：** 已确认；第二层确定为写入与形成层

### Q005 — TencentDB 的写入与形成层怎样工作

**用户问题**

> 写入与形成这一层，TencentDB 是怎么做的？

**回答**

TencentDB 没有一个统一 Writer，而是四条形成管线。

#### A. 对话形成：L0 → L1 → L2 → L3

**L0 是输入捕获边界，不是语义形成。**

```text
输入：team/user/agent/session/task + user/assistant messages
处理：移除 system、tool 轨迹和已注入 memory/persona/scene 块
输出：带 id、role、content、timestamp 的逐消息记录和 accepted_ids
```

L0 接收成功不表示已经形成长期 Memory；真正形成从 L1 开始。

**L1 把若干 L0 消息形成可独立更新的原子记忆。**

```text
触发：累计对话阈值、新 Session 的 1→2→4→5 warm-up 或 idle
输入：背景消息 + 本轮新增消息 + mode（code/chat）
Prompt：判断什么具有未来价值，输出结构化候选
输出候选：type + content + priority + source
```

关键 Prompt 规则：

- 内容必须未来仍有价值并可独立理解；
- code mode 偏团队事实、任务、方法与资产；chat mode 偏用户事实、偏好与经历；
- 用户明确采纳的约定可以保存；Assistant 单方面建议不能自动成为团队事实；
- 不把整段对话原样复制成记忆。

每条新候选随后先检索 Top-K 相似旧 L1，再由去重 Prompt 选择：

```text
store / update / merge / skip
```

输出是带 team/user/agent/session/task、类型、优先级、来源消息和版本的原子 Memory。它可以直接检索、独立更新，也会成为 L2 输入。

**L2 把多条 L1 形成场景方法文档。**

```text
输入：本轮新 L1 正文 + team/agent 已有场景 path/summary
Prompt 动作：UPDATE / MERGE / CREATE / no-op
输出：一个或多个 scene Markdown
```

固定 Prompt 规定场景骨架：适用条件、核心 SOP、判断逻辑、禁忌与反模式、关键事实依据、相关任务与资产、演化记录和待确认问题；同时要求保持克制，避免每条 L1 都新建一个文件。

**L3 把多个 L2 形成跨场景长期准则。**

触发包括首次存在 L2、累计 50 条新 L1、L2 发出 `PERSONA_UPDATE_REQUEST` 或 persona 丢失恢复。输入是变化 L2 的完整正文、旧 `persona.md`、触发原因和计数；不直接读取 L0，也不读取整批 L1 metadata。

Prompt 要求比较新旧规则：已有规则被再次支持则保留，过于绝对则改写适用条件，重复规则合并删除，只有项目状态则不写。输出是 team+agent scope 下不超过约 1200 字的 `persona.md`，并附 L2 导航。

贯穿例子：

```text
L0：用户说“修 bug 前先写失败测试”
↓
L1：{type: work_method, content: 修复缺陷前先建立稳定失败的复现测试}
↓
L2：缺陷修复与回归验证.md
    适用条件 + SOP + 判断逻辑 + 反模式 + 证据
↓
L3：persona.md
    “修复行为缺陷时先建立失败证据；纯重构先建立行为基线”
```

#### B. 执行轨迹形成 Skill

```text
输入：user / assistant / tool_call / tool_result 的完整规范化轨迹
缓冲：space + user + team + agent + session
触发：10 次 tool_call 或约 40 KB
处理：归档后交给异步 Review Agent
输出：版本化 SKILL.md、supporting files 和 active head，或 no-op
```

Review Prompt 先在 Skill、Memory、Wiki、CodeGraph、Temporary Context 中分类；只有归入 Skill 且评分至少 72 才继续。它先获得最近最多 5 个 Skill 的 name/description 提示，再被要求调用 `skill_list` 和 `skill_view` 检查完整已有内容，然后决定：

```text
Nothing to save / create / update / patch / files_write
```

Prompt 强制 Skill 包含 When to use、When not to use、Required inputs、Workflow、Decision rules、Output format、Validation、Pitfalls 和 Supporting files。更新带 `expected_version`，形成新版本而不是覆盖历史快照。

#### C. 外部文档形成 Wiki

```text
输入：上传的 .md/.txt + Wiki purpose + extraction schema + 已有页面摘要
触发：显式 ingest，且 source SHA 新增/变化或上次未成功
处理：Analyze Prompt 制定页面计划 → Generate Prompt 输出 FILE blocks
工程校验：canonical path、locked 页面、source 合并和结构限制
输出：Wiki Markdown 页面
```

Markdown 页面是形成层输出；FTS5/page_meta 和 Wikilink graph 属于第三层存储与索引细节。

#### D. 代码仓库形成 CodeGraph

```text
输入：team、repo_url、branch、repo_name
处理：clone → 解析文件/符号/定义/调用边 → 全量 index 或增量 sync
输出：code_graph_id、commit_hash、files、nodes、edges、status/stats
```

这条形成链不用 LLM Prompt，说明第二层既包括生成式抽取，也包括确定性解析。图的持久结构和查询索引应在第三层展开。

#### 第二层与第四层的边界

- L1/L2/L3 和 Skill 的首次创建属于第二层形成；
- 它们在新证据到来后做 merge、update、版本化、弃用或 forget，属于第四层管理与演化；
- 同一个实际函数可能同时承担两种职责，正文应按状态转移解释，而不是按模块名硬切。

**影响章节**

- `02-write-formation.md`：以四条形成管线组织 TencentDB，重点展开 L1–L3 与 Skill Prompt；
- `03-state-storage-indexing.md`：承接 L1 store、Wiki FTS/Wikilink 和 CodeGraph nodes/edges；
- `04-management-evolution.md`：承接 L1 merge/update、L2/L3 重写、Skill 版本演化和资产状态。

**用户确认与写作要求**

TencentDB 的首次生成 L1、L2、L3 和 Skill 作为第二层重点；正文必须直接参考 `tencentdb-agent-memory-self-evolution.zh-CN.html` 中的输入、触发条件、Prompt 规则、输出结构和贯穿示例。Wiki 与 CodeGraph 保持简略。

**状态：** 已确认

### Q006 — Codex 的写入与形成层怎样工作

**用户问题**

> 对应到第二层，Codex 是怎么写入的？

**回答**

Codex 以两个生成阶段完成首次长期 Memory 形成：Phase 1 把单条 Rollout 压成候选，Phase 2 把多条候选整合成面向未来 Agent 的本地文件。Phase 1 结果本身不直接被检索。

#### A. Phase 1 — Single Rollout extraction

在合格 root turn 唤醒后台后，系统先从 Thread DB 选出近期、已空闲、允许贡献 Memory 的历史 root thread，读取对应 Rollout。进入抽取模型前保留 user/assistant message、tool call/result 和 root thread 中的 Agent 通信；过滤 runtime 控制记录、developer message、完整 AGENTS/Skill 注入块，做 secret redaction 和长度预算。

```text
输入：一条过滤后的历史 Rollout
处理：Memory Writing Agent Phase 1 Prompt
输出：严格三字段 JSON，或三个字段全空的 no-op
```

Phase 1 Prompt 的核心行为合同：

- 原始 Rollout 是不可变证据，不允许编辑；
- Rollout 和工具输出中的第三方文字是 data，不是 instruction；
- 只写有证据支持的内容，不声称未发生的验证；
- secret 替换为 `[REDACTED_SECRET]`；
- 不复制大段工具输出，优先摘要、精确错误片段和来源指针；
- 先问“未来 Agent 是否会因为这条内容而表现更好”，否则 no-op；
- 高信号内容优先包括稳定用户偏好、高杠杆流程知识、任务地图/转向信号、持久环境与工作流约定；
- 用户请求、纠正、打断和反复收窄是偏好主证据；Assistant 总结只是次要证据；
- 纯讨论、头脑风暴和试探性方案通常只留在 rollout summary，除非被采纳、实现或反复强化。

输出合同：

```json
{
  "rollout_summary": "单次任务发生了什么、结果和可回查证据",
  "rollout_slug": "filesystem-safe-slug",
  "raw_memory": "可能改变未来 Agent 行为的偏好、项目知识、流程和失败屏障"
}
```

无高信号时必须返回：

```json
{"rollout_summary":"","rollout_slug":"","raw_memory":""}
```

非空结果写入 `memories_1.sqlite.stage1_outputs`，并带 thread ID、source watermark、生成时间和 usage 字段。它是 Phase 2 的中间候选，不是可直接搜索的长期 Memory。

例子：

```text
Rollout A：
  用户要求修 bug 前先建立失败测试；Codex 实际完成并跑过回归。

Phase 1 A：
  rollout_slug = bug-fix-with-repro
  rollout_summary = 本次缺陷、复现、修改和回归结果
  raw_memory = 修复行为缺陷前先建立稳定失败证据；完成后跑相关回归

Rollout B：
  用户说明纯重构没有待修复失败，但必须先锁定行为基线。

Phase 1 B：
  rollout_slug = refactor-behavior-baseline
  raw_memory = 纯重构先建立现有行为基线和回归保护，不要求伪造失败用例
```

#### B. Phase 2 — Consolidation

Phase 2 先按 `usage_count`、`last_usage/source recency` 等选择最多 256 条 Stage 1 candidates。Host 将选中内容机械物化为 `raw_memories.md` 和 `rollout_summaries/*.md`，并生成相对上一次成功 Git baseline 的 workspace diff。

```text
输入：
  raw_memories.md
  existing MEMORY.md
  rollout_summaries/*.md
  existing memory_summary.md（首行必须为 v1）
  existing skills/*
  extensions/ad_hoc/notes/*
  phase2 workspace diff

处理：受限 Memory Writing Agent Phase 2 Prompt

输出：
  MEMORY.md
  memory_summary.md
  skills/*（可选）
```

Phase 2 Prompt 的核心行为合同：

- 支持 INIT 首次构建和 INCREMENTAL UPDATE 两种模式；
- `raw_memories.md` 是被选 Phase 1 内容的机械合并，不按文件顺序推断重要性；
- 先读 workspace diff，变更和删除必须传播到正式 Memory；
- 不打开原始 session/Rollout transcript；需要更强证据时只读相应 raw-memory 段和 rollout summary；
- 删除某个来源时，只删除由它单独支撑的结论；仍有其他证据支撑的内容保留并修正引用；
- 不追求固定块数，让信号决定粒度；
- `MEMORY.md` 必须比 `raw_memories.md` 更聚合、更可操作；
- `memory_summary.md` 首行必须是 `v1`，保持密集、区分性强且只负责导航；
- Skills 只在形成了独立、可复用程序时创建，可包含 `SKILL.md`、scripts、templates 和 examples；
- 没有新信号时保持最小变更。

三个主要输出的职责：

```text
MEMORY.md
  跨 Rollout 聚合的用户偏好、项目知识、任务地图、流程与失败屏障

memory_summary.md
  每个新 Thread 自动加载的短索引，告诉 Agent 去 MEMORY.md 搜什么

skills/*
  值得独立复用的结构化程序和配套工件
```

前述两个 Phase 1 例子进入首次 Phase 2 后，可能形成：

```markdown
# MEMORY.md

## 缺陷修复与行为保护
- 修复行为缺陷时，先建立稳定失败的复现证据。
- 纯重构时，先建立现有行为基线和回归保护。
- 两类任务完成后都运行相关回归；不要把“必须失败”错误外推到纯重构。
- Sources: bug-fix-with-repro, refactor-behavior-baseline
```

```markdown
# memory_summary.md
v1

- 编码工作方式：缺陷复现、纯重构行为基线与回归要求，见 MEMORY.md。
```

若证据足以形成独立流程，还可输出：

```text
skills/behavior-safe-change/SKILL.md
```

#### 与 TencentDB 的对应关系

```text
TencentDB L0 + Skill 原始轨迹
≈ Codex Rollout

TencentDB L1 原子抽取
≈ Codex Phase 1 第一遍抽取
但 Codex Phase 1 更粗：每 Thread 一条候选、不可直接检索

TencentDB L2 + L3 + Skill
≈ Codex Phase 2 同时维护 MEMORY.md + memory_summary.md + skills
但 Codex 没有三个彼此独立的场景/persona/skill 状态机
```

最关键差异：TencentDB L1 写入后就是可独立搜索和更新的原子 Memory；Codex Phase 1 只是候选，必须被 Phase 2 选择并形成文件后，未来 Agent 才能使用。TencentDB 以显式对象和操作管理层级；Codex 主要依赖 Phase 2 Prompt、文件结构和 Git diff 维持语义。

#### 第二层与第四层边界

- 第一次 Phase 1 + Phase 2 INIT 构建属于第二层写入与形成；
- 后续 Phase 1 提供新候选仍属于形成；
- Phase 2 INCREMENTAL UPDATE 中对旧结论的修正、删除、重新聚合和 Skill 更新，在第四层管理与演化重点展开；
- 第二层只需说明增量模式存在，不在此重复管理细节。

**影响章节**

- `02-write-formation.md`：Codex Phase 1/Phase 2 首次形成，重点解释 Prompt 合同、输入输出、no-op 和贯穿例子；
- `03-state-storage-indexing.md`：承接 `stage1_outputs`、Memory 文件与 Git workspace 的持久形态；
- `04-management-evolution.md`：承接 Phase 2 增量重写、来源删除传播、notes 和 reset；
- `05-retrieval-context.md`：承接 `memory_summary → MEMORY → rollout summary/skill → rollout_path`。

**用户确认与写作要求**

Codex 的写入内容已确认。第二层必须保留 Phase 1/Phase 2 的具体 Prompt 合同，特别是 no-op、高信号标准、证据/安全边界、输出 schema、Phase 2 输入文件和正式输出文件；不能只写流程名称。

**状态：** 已确认

### Q007 — 近期前沿还有哪些有新意的写入/形成机制

**用户问题**

> TencentDB 和 Codex 的写入已经确定。近期前沿技术中，还有哪些有新意的写入？

**回答**

筛选标准是：必须改变“从原始输入到首次 Memory 对象”的形成方法。按这个标准，三类机制值得进入第二层。

#### A. AtomMem — 从单一摘要改为原子事实、事件与时间画像的分层形成

AtomMem 的新意不是再生成一份更好的 summary，而是先选择性抽取高价值 atomic facts，再把事实组织成 hierarchical events 和 temporal profiles；检索阶段才由 associative graph 连接碎片。

```text
输入：长对话/多 Session 交互
→ Fact Executor 选择性抽取 atomic facts
→ 将相关 facts 聚合为 event hierarchy
→ 由跨时间 facts 形成 temporal profile
输出：atomic fact + event + temporal profile
```

例如：

```text
原始交互：
  4 月：用户说最近改用 pytest
  5 月：多个任务都先写失败测试
  6 月：用户纠正纯重构只需行为基线

atomic facts：
  F1 使用 pytest
  F2 缺陷修复前先建立失败测试
  F3 纯重构先建立行为基线

event：
  E1 测试驱动的代码修改工作方式

temporal profile：
  当前偏好区分“缺陷修复”和“纯重构”，不再使用绝对的所有修改先失败规则
```

它与 TencentDB L1→L2→L3 很相似，因此正文不需要再做一个同等篇幅的系统介绍；适合用作外部前沿证据，说明“原子事实 → 事件 → 时间画像”正在成为独立形成路线。[AtomMem](https://arxiv.org/abs/2606.19847)

#### B. XSkill — 从单条轨迹总结改为多路径对照，同时形成 Experience 与 Skill

XSkill 针对同一任务生成多条 Rollout，用 visual-grounded summary 和 cross-rollout critique 比较成功、失败与局部路径，再同时输出两种对象：

```text
输入：同一任务的 N 条视觉/工具 Rollout + 各自 outcome
→ 每条 Rollout summary
→ cross-rollout critique
→ hierarchical consolidation
输出：
  action-level Experience Bank
  task-level Skill Library
```

Experience 表达：

```text
触发条件 → 建议动作
```

Skill 表达：

```text
metadata + workflow sequence + reusable tool templates
```

它比 TencentDB/Codex 的单 Session/单 Rollout 第一遍抽取多了一步“同任务多路径互证”，可以减少把偶然成功步骤直接编成 Skill。适合在 Skill 形成部分简短加入。[XSkill](https://arxiv.org/abs/2603.12056)

#### C. MemTxn — LLM 只提出写入 Proposal，来源支持后才提交

TencentDB L1 的去重 Prompt 和 Codex Phase 2 都会直接根据模型判断修改长期状态。MemTxn 增加了位于 answer model 之外的 transaction boundary：

```text
输入：source receipt + proposed patch + current Memory state
→ Ordered PatchTest：新断言是否受来源支持
→ Temporal Resolver：冲突版本中哪一个当前可见
→ durable snapshot journal：提交并保留恢复点
输出：
  committed revision + active visible state
  或 rejected proposal
  + recoverable snapshot/receipt
```

例如：

```text
旧状态：用户所有代码修改都先写失败测试
新来源：用户明确说明纯重构只要求行为基线
LLM proposal：删除旧规则，改成两类条件规则

PatchTest：检查 proposal 中每个新 clause 是否能回到用户原话
Temporal Resolver：旧规则保留历史版本，新规则成为 current
Commit：写入新 revision；失败时从 snapshot 恢复完整 active map
```

它最值得写进前沿部分，因为改变了“谁有权把候选变成正式 Memory”：抽取/巩固模型只负责提议，来源验证和事务层决定是否生效。[MemTxn](https://arxiv.org/abs/2607.27834)

#### 不建议放在第二层重点的候选

1. **Retain or Consolidate?** 根据 token budget 在 Retain、Merge、Abstract、Rewrite 中选 operator，研究很新，但其核心是 query-time/budget-dependent representation choice，更接近第五层上下文构造或第四层管理，而不是首次写入。[论文](https://arxiv.org/abs/2607.17545)
2. **MemCon。** 用在线策略选择 retrieve、plan injection、re-retrieve、consolidate、forget 和 no-op，核心是跨任务 Memory control，主要属于第四层管理与第七层反馈学习，不应提前塞进第二层。[MemCon](https://arxiv.org/abs/2607.13591)
3. **事务恢复的完整细节。** MemTxn 的 source-supported admission 可放第二层；snapshot recovery、版本冲突和故障恢复应在第三/第四层展开，避免重复。

建议第二层前沿部分的篇幅顺序：

```text
重点：MemTxn source-supported proposal → commit
简写：AtomMem atomic fact → event → temporal profile
简写：XSkill multi-rollout critique → Experience + Skill
移出本层：budget router、learned controller、forget/recovery 细节
```

**影响章节**

- `02-write-formation.md`：增加上述三项，其中 MemTxn 作为主要前沿机制；
- TencentDB L1–L3 后用 AtomMem 做同构对照；
- TencentDB/Codex Skill 形成后用 XSkill 补充多路径互证；
- `04-management-evolution.md`：承接 MemCon 与持续 consolidation/forget；
- `05-retrieval-context.md`：承接 budget-dependent retain/consolidate；
- `03-state-storage-indexing.md` 和第四层：承接 MemTxn journal/recovery。

**状态：** 部分确认；AtomMem 删除，XSkill 与 MemTxn 的层级边界转入 Q008

### Q008 — XSkill 多路径怎样形成，MemTxn 是否应归入管理层

**用户问题**

> 1. AtomMem 没有新意，不用写。  
> 2. XSkill 的多条路径怎样形成，是同一个任务跑多次吗？它的场景是否不同于 Codex 对话？  
> 3. MemTxn 可以展开，但它看起来像解决冲突，是否属于后面的管理部分？

**回答**

#### 1. AtomMem

删除。它与 TencentDB 已经详细展示的 L1→L2→L3 层级形成高度同构，没有必要以“前沿新机制”重复占用篇幅。

#### 2. XSkill 的 Multi-path Rollout

是，同一个任务会被主动执行多次。论文主实验对每个积累任务执行 `N=4` 条独立 Rollout；同一视觉问题在模型采样、工具选择、调用顺序和中间判断上形成不同路径，每条路径都有自己的最终 outcome。随后知识管理模型先分别总结，再做 cross-rollout critique。

```text
同一个 task + 同一视觉输入
├── Rollout A：路径 A → success
├── Rollout B：路径 B → failure
├── Rollout C：路径 C → partial/failure
└── Rollout D：路径 D → success
        ↓
每条 Rollout 的 visually-grounded summary
        ↓
横向比较哪些动作稳定有效、哪些只在失败路径出现
        ↓
Experience：条件 → 局部动作
Skill：跨路径工作流 + 工具模板
```

这与 Codex/TencentDB 的自然用户工作流不同：

- Codex 默认只消费用户真实完成的一次任务历史，不会为了形成 Memory 把同一用户任务自动重跑四次；
- TencentDB Skill 也主要从真实 Session 轨迹归档，不要求同一任务多次执行；
- XSkill 更接近 benchmark/training-set 上的离线或批量经验积累，需要可重复任务、额外执行成本和 outcome 判断器；
- 它适合视觉工具 Agent、自我改进实验、可重放环境或允许多次试错的任务，不是普通个人 Chat Memory 的默认形成方式。

在 Coding Agent 中可以类比为对同一 issue 开多个独立尝试/分支再比较，但这会把成本放大 N 倍，并要求统一测试或 judge 判断哪条路径成功。因此它不应写成通用第二层主路径；若保留，只能作为“多次试验型 Skill 形成”的特殊场景短注。

#### 3. MemTxn 的层级归属

MemTxn 确实主要解决 writable Memory 的更新、冲突和恢复，而不是一般的第一次摘要形成。它应按职责拆开：

```text
第二层：写入准入
  source receipt + LLM proposed patch
  → proposal 是否受来源支持
  → supported 才允许 commit，unsupported reject

第四层：管理与演化
  新旧事实冲突
  → Temporal Resolver 选择 current/history version
  → supersede / conflict / visible-state transition

第三/第四层的可靠性部分：
  durable snapshot journal
  → 故障后的完整 active state 恢复
```

因此第二层只需确立一条重要原则：

> 形成模型输出的是 write proposal，不是正式 Memory；proposal 的每个 consequential clause 应能回到 source span/tool receipt，通过准入后才提交。

MemTxn 的详细展开应放第四层，重点说明：

- 新事实怎样与旧版本冲突；
- current/history 版本怎样选择；
- patch 怎样传播；
- 部分失败后怎样从 snapshot journal 恢复；
- “存储写成功”与“应用可见状态完整”为什么不是一回事。

第二层用一段 source-supported admission 作为通往第四层的桥即可，不应在第二层展开 Temporal Resolver 和 recovery 实验。

**建议取舍**

```text
第二层：
  删除 AtomMem
  XSkill 最多作为特殊多试验 Skill 场景短注，是否保留待确认
  MemTxn 只写 source-supported proposal → admission → commit

第四层：
  详细展开 MemTxn conflict/version/recovery
```

**主要证据**

- XSkill：`https://arxiv.org/abs/2603.12056`
- MemTxn：`https://arxiv.org/abs/2607.27834`

**用户确认与最终归位**

1. AtomMem 删除，不进入七层正文的前沿重点；
2. XSkill 不进入第二层。它为了生成经验而主动重复同一任务，以 outcome 和 cross-rollout critique 形成 Experience/Skill，本质是反馈驱动的经验生产，归入第七层“反馈、经验与持续学习”；
3. MemTxn 按职责拆分：第二层只简要写 `proposal → source-supported admission → commit/reject`；第四层详细写 conflict、Temporal Resolver、version/supersede 和 recovery；snapshot journal 的物理可靠性可与第三层交叉引用。

第二层前沿部分最终仅保留：

```text
LLM/extractor output
→ write proposal
→ source-span/tool-receipt support check
→ admission
→ commit or reject
```

这段用 MemTxn 作为近期研究例子，不在第二层展开冲突解析和恢复实验。

**状态：** 已确认

### Q009 — 第三层是什么

**用户问题**

> 接下来第三层是什么？

**回答**

第三层是**状态、存储与索引层**。

第二层回答“从输入中形成什么”；第三层回答：

> 形成后的 Memory 以什么对象、身份、版本和物理载体长期存在，又建立哪些可重建入口供后续查找？

基本链路是：

```text
第二层输出：
  committed Memory object / file / skill / graph candidate
        ↓
第三层：状态、存储与索引
  分配 stable identity、scope、revision
  → 保存 authoritative payload/current/history/source
  → 建立 FTS/BM25、embedding、graph、目录或 summary 等派生投影
  → 记录 projection revision / build status / source pointer
        ↓
第三层输出：
  可持久恢复的 Memory state
  + 可供读取层使用的索引与定位入口
```

本层必须拆开三个概念：

1. **状态模型：** Memory object 有哪些字段，哪个版本当前有效，历史版本和来源在哪里，属于哪个 user/team/project/agent；
2. **权威存储：** 哪个载体是事实来源，例如 SQLite/Postgres row、Markdown 文件、event journal、对象文件或图记录；
3. **派生索引：** FTS/BM25、embedding/ANN、entity/graph edge、目录摘要等用于查找的投影；索引命中不等于权威状态本身。

边界：

- 是否值得写、形成何种对象：第二层；
- 已有对象怎样 merge、supersede、forget、recover：第四层；
- 查询怎样选候选、排序、展开和编译 Prompt：第五层；
- 第三层只负责让状态可持久、可定位、可重建，并说明主状态与索引是否一致。

这一层后续应重点用 TencentDB 和 Codex 回答：

- L1、L2、L3、Skill、Wiki、CodeGraph 分别存在哪里、是什么格式、哪些是权威正文、哪些是索引；
- Codex 的 `memories_1.sqlite`、Rollout JSONL、`MEMORY.md`、`memory_summary.md`、rollout summaries、skills 和 Git baseline 分别承担什么；
- 为什么“数据库里有候选”“文件已经形成”“索引已经可搜”是三个不同状态。

**影响章节**

- `03-state-storage-indexing.md`：第三层主章节；
- `04-management-evolution.md`：只引用存储原语，不重复第三层结构；
- `05-retrieval-context.md`：消费第三层索引，不把索引实现误写成检索策略。

**用户确认**

第三层确定为状态、存储与索引层，并按“状态模型 / 权威正文 / 派生索引”拆解 TencentDB 与 Codex。

**状态：** 已确认

### Q010 — TencentDB 的状态、存储与索引层怎样工作

**用户问题**

> 第三层先说 TencentDB。

**回答**

TencentDB 固定提交 `0aff21a` 没有把所有 Memory 放进一个统一 Store。不同对象保留不同权威正文，再用 SQLite、JSON 索引或图索引建立当前视图与查询入口。

#### A. L0 原始对话

本地逻辑布局：

```text
conversations/YYYY-MM-DD.jsonl
```

一条 user/assistant message 一行，带 message ID、session key/ID、user、agent、team、task、role、content 和 timestamp。JSONL 是可回放的原始记录。

同一份内容还进入 `vectors.db`：

```text
l0_conversations  当前消息元数据/正文视图
l0_fts            FTS5/BM25 索引
l0_vec            可选 vec0 cosine embedding 索引
```

未配置 embedding 时不创建/使用 `l0_vec`，FTS5 路径仍可用。

#### B. L1 原子 Memory

权威恢复记录采用每日 append-only JSONL：

```text
records/YYYY-MM-DD.jsonl
```

每条 Memory 包含：

```text
id / content / type / priority / scene_name
source_message_ids / metadata / timestamps
createdAt / updatedAt / version
session / task / team / user / agent
```

源码将 JSONL 称为 backup/recovery 的 source of truth；当前检索视图在 `vectors.db`：

```text
l1_records  当前 record_id 对应的 content/type/scope/version
l1_fts      FTS5/BM25
l1_vec      可选 vec0 cosine embedding
```

`update/merge` 会实时替换 `l1_records` 和相应 FTS/vector 当前视图；JSONL 继续 append 新版本并保留旧记录，之后由 cleaner 处理。因此应区分：

```text
JSONL：历史、审计与恢复轨迹
l1_records：应用当前视图
l1_fts/l1_vec：可重建查询投影
```

#### C. L2 场景文档

权威正文是文件：

```text
scene_blocks/*.md
```

每份 Markdown 内含场景正文及 summary、heat、created、updated 等 frontmatter/元信息。

工程侧扫描所有场景文件，生成：

```text
.metadata/scene_index.json
```

索引只保存：

```text
filename / summary / heat / created / updated
```

它用于向 Prompt 或新 Session 提供轻量导航；真正内容仍在 `scene_blocks/*.md`。该索引可以从 Markdown 重建，LLM 被 sandbox 在 `scene_blocks/`，不能直接修改 `.metadata/scene_index.json`。

#### D. L3 Persona

权威正文是 team+agent Profile Scope 下的一份：

```text
persona.md
```

正文包含跨场景准则；工程侧在文件尾部追加最新 L2 场景导航。L3 没有向量索引，也不需要 query-time search：新 Session 初始化时直接读取并注入全文。`session_init` 缓存意味着已有 Session 不一定看到刚更新的版本。

#### E. Skill

Skill 采用“版本表 + 内容文件”的组合。

SQLite `skills` 表每行是一份不可变版本：

```text
(skill_id, version) UNIQUE
is_head                 当前版本标记
user_id / owner_agent_id / team_id / task_id
name / description / content / content_hash
manifest_json / storage_dir
status / metadata / created_at / updated_at
```

`SKILL.md` 正文同时存为 `content`，supporting files 的结构写入 `manifest_json`，实际文件字节放在 local/COS storage directory。新版本写新行，旧版本不覆盖；`is_head=1` 表示当前 active head。

索引只覆盖 active head：

```text
skill_fts  name + description + content 的 FTS5
skill_vec  可选 cosine embedding，以 skill_id 为键
```

所以：

```text
skills 表 + storage files：版本化权威内容
is_head/status：当前可见状态
skill_fts/skill_vec：查询投影
```

#### F. Wiki

Wiki 的权威正文是 Markdown 页面目录；`page_meta` 不保存正文。每个 Wiki 有自己的 `index.db`：

```text
wiki_fts    预分词 FTS5/BM25
page_meta   page_id/title/type/rel_path/snippet
graph_edge  从 [[Wikilink]] 形成的有向边
source      source SHA 与 ingest 状态
```

FTS、page metadata、graph edge 和 source 在重建时由同一 SQLite 写事务更新。读取图时，再从 `graph_edge` 构建内存图执行 BFS。

另一个 Knowledge metadata DB 保存：

```text
knowledge_wiki：team/source/status/page_count/summary/version/last_sync
knowledge_wiki_audit：append-only 状态变更日志
```

它登记 Wiki 资源状态，不替代 Markdown 页面正文。

#### G. CodeGraph

CodeGraph 保存两类状态：

1. `knowledge_code_graph` metadata row：repo URL、branch、commit hash、team/user/agent/task、status、stats、version、last sync；另有 append-only audit；
2. 克隆仓库中的 CodeGraph 自有 DB/index：files、symbols/nodes 和 call/dependency edges。

首次 `init + indexAll` 建立索引，后续 `sync()` 只处理变化文件。查询工具消费预建 nodes/edges；但真正修改代码前仍应以当前 workspace source 为准，因为 CodeGraph 是某个 commit 的投影。

#### H. Asset Registry 不是统一正文 Store

`meta_assets` 统一登记：

```text
asset_id / type / owner / version / visibility / status
confidence / expires / usage / source_ref / content_ref
```

`content_ref` 只指向 Chat Memory、Skill、Wiki 或 CodeGraph 的真实内容位置。另有：

```text
meta_agent_fixed_assets  Agent 固定绑定、injection_mode、priority
meta_asset_acl           subject permission allow/deny
```

因此 Asset 只是登记卡、ACL 和绑定控制面，不是把四种内容重新复制进一张统一表。

#### TencentDB 第三层的总体结构

```text
L0  JSONL raw log
    + SQLite metadata/current view
    + FTS / optional vector

L1  append-only JSONL history/recovery
    + SQLite current records
    + FTS / optional vector

L2  scene Markdown authority
    + rebuildable scene_index.json

L3  persona.md authority
    + direct injection，无检索索引

Skill  immutable version rows + SKILL/supporting files
      + head-only FTS / optional vector

Wiki  Markdown pages
    + per-Wiki FTS/page_meta/Wikilink graph
    + resource metadata/audit

CodeGraph  repo/commit projection
         + files/nodes/edges index
         + resource metadata/audit

Asset  registry + ACL + binding
     → content_ref 指向上述真实内容
```

这一实现的关键不是“用了 SQLite 还是 Markdown”，而是明确区分了：原始/历史记录、当前可见状态、权威正文、可重建索引和统一控制面。

**固定版本源码依据**

- `MemoryCore/src/core/conversation/l0-recorder.ts`
- `MemoryCore/src/core/record/l1-writer.ts`
- `MemoryCore/src/core/store/sqlite.ts`
- `MemoryCore/src/core/scene/scene-index.ts`
- `MemoryCore/src/core/skill/skill-store-ddl.ts`
- `MemoryKnowledge/src/engines/wiki/index-db.ts`
- `MemoryKnowledge/src/db/schema.ts`
- `MemoryCore/scripts/db/sqlite-init.sql`

**影响章节**

- `03-state-storage-indexing.md`：用对象表而不是按数据库产品组织 TencentDB；
- 第三层重点解释 authority/current/history/projection/control-plane 五种状态；
- 第四层再讨论这些状态的 merge、version、sync、delete 和 recovery。

**状态：** 部分确认；事实核对成立，但正文组织过细，按 Q011 收缩为存储原语与职责

### Q011 — TencentDB 第三层本质上是否只是文件、数据库、向量和图

**用户问题**

> 本质上不还是 JSONL、DB、向量库和图吗？

**回答**

是。从物理和逻辑存储原语看，TencentDB 第三层可以收敛为四类：

```text
1. 文件存储
   JSONL：L0/L1 原始与历史记录
   Markdown：L2/L3、Wiki、SKILL.md
   supporting files：Skill scripts/templates/assets

2. 结构化数据库
   SQLite/Mongo：当前对象、版本、scope、status、asset/ACL/binding metadata

3. 查询索引
   FTS5/BM25：关键词全文索引
   vec0 embedding：语义相似索引

4. 关系/图索引
   Wikilink graph_edge
   CodeGraph files/nodes/call/dependency edges
```

这里甚至不应笼统写成“四种独立数据库”：

- `vectors.db` 本身是 SQLite；FTS5 和 vec0 是同一库中的虚拟表/扩展；
- Wiki graph 主要是 SQLite 中的 `graph_edge`，读取时构建内存图；
- CodeGraph 自有索引也由库内 DB 保存 files/nodes/edges；
- Asset Registry 仍只是结构化 metadata 表。

所以 TencentDB 在存储技术上没有发明新的 primitive。其架构价值只在于把不同 Memory 对象映射到合适载体，并区分：

```text
raw/history
current structured state
human-readable artifact
rebuildable lexical/vector/graph index
```

第三层正文不应逐表罗列实现。建议压缩成一张矩阵：

| 载体 | 保存什么 | 代表对象 | 是否权威 |
|---|---|---|---|
| JSONL | 原始/版本历史 | L0、L1 | 历史与恢复依据 |
| Markdown/文件 | 人类可读长期工件 | L2、L3、Wiki、Skill | 正文权威 |
| DB rows | 当前对象、版本和控制状态 | L1 current、Skill versions、Asset metadata | 当前结构状态 |
| FTS/vector | 关键词/语义入口 | L0、L1、Skill、Wiki | 可重建索引 |
| graph edges | 页面/代码关系 | Wiki、CodeGraph | 可重建关系投影 |

正文只需再用两个例子说明同一内容可能同时存在于正文与索引，不需要列所有表字段：

```text
L1：JSONL history + DB current row + FTS/vector
Wiki：Markdown page + FTS/page_meta + graph edges
```

**影响章节**

- `03-state-storage-indexing.md`：TencentDB 部分按“文件 / DB / lexical-vector / graph”组织；
- 删除大部分表字段和实现清单，只保留权威内容与派生索引边界；
- 版本冲突、同步、恢复和删除留第四层。

**用户确认与篇幅要求**

第三层不是七层正文重点。只需简要介绍文件、结构化 DB、全文/向量索引和图索引等载体，以及正文与派生索引的区别。

TencentDB 部分可略多写 Wiki 与 CodeGraph：

```text
Wiki：Markdown 页面 + FTS/BM25 + page metadata + Wikilink graph
CodeGraph：代码仓库/commit + files/symbols/nodes + call/dependency edges
```

目的只是展示普通文档知识与代码知识怎样组合正文、索引和关系，不展开 DDL、全部表字段、内部类或逐工具实现。L0/L1/L2/L3/Skill 的存储只在总表中各占一行。

**状态：** 已确认；第三层简写，Wiki/CodeGraph 适度展开

**补充确认**

TencentDB 的 Wiki 和 CodeGraph 直接按 `tencentdb-agent-memory-self-evolution.zh-CN.html` 的读者版介绍改写，不再为第三层补充源码 DDL、内部表或实现类。

### Q012 — Codex 的状态与存储载体是什么

**用户问题**

> Wiki 和 CodeGraph 按 TencentDB 专项 HTML 介绍；再看一下 Codex 的载体。

**回答**

Codex 的第三层比 TencentDB 简单，没有预建向量库或图索引。它由四类载体组成。

#### A. 原始经历：Rollout JSONL + Thread DB

```text
Rollout JSONL
  user/assistant messages
  tool calls/results
  inter-agent communication
  runtime events 与原始任务证据

state_5.sqlite
  thread ID/source/cwd/branch/commit/updated_at/archive/memory_mode
  rollout_path 与线程发现状态
```

Rollout JSONL 保存发生过什么；`state_5.sqlite` 让 Host 能按 Thread 找到它、筛选是否有资格进入 Phase 1。Thread DB 不是长期 Memory 正文。

#### B. Phase 1 候选与后台任务：memories_1.sqlite

```text
stage1_outputs
  thread_id
  source watermark
  raw_memory
  rollout_summary / slug
  generated_at
  usage_count / last_usage
  selected_for_phase2

jobs
  phase1/phase2 status
  worker / ownership token / lease / retry / error / watermark
```

这是候选和调度状态，不是未来 Agent 的检索库；新 Thread 不直接查询 `stage1_outputs`。

#### C. Phase 2 文件化 Memory 工作区

```text
~/.codex/memories/
├── memory_summary.md
├── MEMORY.md
├── raw_memories.md
├── rollout_summaries/*.md
├── skills/
└── extensions/ad_hoc/notes/*.md
```

各文件职责：

| 载体 | 作用 | 是否主要读取面 |
|---|---|---|
| `memory_summary.md` | 首行 `v1`；新 Thread 自动加载的高密度导航 | 是，常驻入口 |
| `MEMORY.md` | 跨 Rollout 聚合的偏好、项目知识、流程和失败屏障 | 是，主要长期手册 |
| `raw_memories.md` | 被选 Phase 1 `raw_memory` 的机械合并，供 Phase 2 使用 | 否，形成输入/临时工件 |
| `rollout_summaries/*.md` | 单次 Rollout 的提炼摘要和 `rollout_path` 指针 | 是，深一层证据入口 |
| `skills/` | 可复用流程，入口通常为 `SKILL.md`，可带配套文件 | 是，按需读取 |
| `extensions/ad_hoc/notes/` | 用户显式 remember/update/forget 的追加 note | 否，下一轮 Phase 2 控制输入 |

#### D. Git baseline

`~/.codex/memories/` 本身是 Git 工作区。Codex 用上一次成功 Phase 2 baseline 与当前物化输入生成 diff，让 Consolidation Agent 看到新增、修改和删除；成功后重置 baseline。

Git 在这里不是面向用户的 Memory 检索历史，而是 Phase 2 的增量形成与失败续跑边界。

#### E. Codex 没有预建 FTS、Vector 或 Graph Index

固定版本 Local Memory 的读取方式是：

```text
memory_summary.md  文本导航
→ 根据关键词扫描/grep MEMORY.md
→ 必要时打开 rollout summary 或 skill
→ 再必要时沿 rollout_path 打开原始 JSONL
```

本地 `search` 在查询时递归扫描普通文本，做 substring/同行/窗口匹配，并按 path/line 返回；没有 embedding、ANN、FTS materialized index 或 graph navigation。

因此 Codex 的“索引”更准确地说是两样东西：

```text
生成式文本索引：memory_summary.md
即时词法扫描：对 MEMORY.md 等文件 grep/search
```

#### 与 TencentDB 的第三层对照

```text
TencentDB：
  JSONL/Markdown 正文
  + SQLite current state
  + FTS/vector/graph 预建索引

Codex：
  Rollout JSONL 原始证据
  + SQLite candidate/job state
  + Markdown 长期 Memory
  + Git diff baseline
  + 查询时即时词法搜索
```

所以 Codex 的存储新意也不在 primitive，而在“SQLite 管后台候选和调度、Markdown 管可读长期状态、Git 管增量巩固、词法扫描替代预建语义索引”的组合。

**官方产品边界**

官方文档确认本地 Memory 文件位于 `$CODEX_HOME/memories/`，包含 summaries、durable entries、recent inputs 和 supporting evidence；这些属于 generated state。完整内部文件职责以上述固定提交代码分析为准。

**影响章节**

- `03-state-storage-indexing.md`：Codex 只用一张载体表和一张与 TencentDB 的对照图；
- 不在第三层展开 candidate selection、Phase 2 Prompt、citation feedback 或 reset；
- 第五层再解释即时词法 search 和渐进下钻。

**用户确认与篇幅要求**

Codex 没有值得在第三层重点展开的额外存储载体。正文只简要说明：

```text
Rollout JSONL：原始经历
state_5.sqlite：Thread 元数据与来源定位
memories_1.sqlite：Phase 1 candidates 与 Phase 1/2 jobs
Markdown files：正式可读长期 Memory
Git baseline：Phase 2 增量 diff/成功基线
```

不展开内部 schema，也不把即时词法搜索当成新的存储技术；搜索和渐进下钻放第五层。

第三层整体最终定位：非重点，TencentDB Wiki/CodeGraph 按专项 HTML 适度介绍，其余 TencentDB/Codex 载体用对照表简写。

**状态：** 已确认

### Q013 — 近期前沿是否出现新的 Memory 存储载体

**用户问题**

> 最新前沿技术中有什么新的载体吗？

**回答**

在本报告限定的“外部、可持久、可检查的 Agent Memory”范围内，没有出现真正新的物理载体。近期工作主要是在既有文件、关系库、向量和图之上增加新的状态表示与访问抽象。

#### 1. Graph-native bitemporal store：新的是时间模型，不是图载体

近期双时间 Memory 使用：

```text
Neo4j property graph
+ HNSW vector index
+ immutable identity node
+ versioned content node
+ valid-time interval
+ transaction-time interval
```

它能查询“事实在世界中何时成立”和“系统当时何时知道”，但底层仍是 property graph + vector index；新意是 bitemporal schema 与 version semantics，不是新存储介质。[A Graph-Native Bitemporal Memory Store](https://arxiv.org/abs/2607.26520)

#### 2. GEM/MemState：新的是 state-trajectory contract，不是数据库类型

GEM 将 Memory state 表达为：

```text
content + typed structure + declarative policy
```

并把 ingestion、revision、forgetting、retrieval 定义为 state-level operators。其 MemState 原型仍构建在 property-graph backend 上。新意是正确性从单条 record 提升到整个 state trajectory，而不是发明一种新载体。[GEM/MemState](https://arxiv.org/abs/2605.26252)

#### 3. OpenViking virtual filesystem：新的是统一 namespace，不是文件系统 primitive

OpenViking 用 `viking://` 把 resource、memory 和 skill 组织为虚拟文件系统，并按目录层级加载 L0/L1/L2 内容；底层仍组合完整内容存储、metadata 和 vector index。它的新意是统一命名空间、层级浏览和可观察检索轨迹，不是新的物理存储。[OpenViking](https://github.com/volcengine/OpenViking)

#### 4. 真正不同的载体只出现在范围外的 latent memory

若把范围扩大到模型内部或模型耦合 Memory，会出现：

```text
latent token sequence
hidden-state/content cache
soft memory token
learned latent memory bank
```

例如 MemGen 生成 latent token sequence 插入推理；ElasticMem 保存 latent memory bank，并按 query 分配可变 latent budget。这些不再是可直接阅读的 JSONL/Markdown/DB record，需要专门的模型或训练接口，也难以沿用外部 Memory 的引用、人工检查、ACL 和删除语义。[MemGen](https://arxiv.org/abs/2509.24704)；[ElasticMem](https://arxiv.org/abs/2605.30690)

它们属于参数/latent Memory 邻接路线，不与 TencentDB/Codex 的外部长期 Memory 直接比较，因此不进入第三层正文重点。

#### 第三层最终写法

前沿部分最多保留一个短结论：

> 近期创新主要发生在双时间版本、state trajectory 和虚拟文件命名空间等表示语义上，底层仍是文件、关系/图数据库和向量索引。Latent tokens/hidden states 是不同路线，但超出本文外部可检查 Memory 的主体范围。

不需要为上述论文分别开章节。

**用户确认与收窄**

第三层前沿不介绍 GEM/MemState、OpenViking 或 Latent Memory，只保留双时间版本图。

**状态：** 已确认；前沿载体/表示只简写双时间版本图

### Q014 — 双时间与版本模型是什么

**用户问题**

> 双时间和版本模型介绍一下。

**回答**

普通 Memory 更新常写成：

```text
record_id=office
content=上海
updated_at=2026-07-01

后来 UPDATE content=杭州
```

这样只能看到最终值，无法回答：用户实际何时搬到杭州、系统何时知道、Agent 在某次历史行动时依据的是哪一版。

双时间模型给每个版本保存两条时间轴：

1. **Valid time：** 该事实在现实世界中何时成立；
2. **Transaction/recorded time：** 该版本何时进入系统、何时成为系统可见知识。

例子：

```text
7 月 1 日，用户说：办公室在上海。
7 月 13 日，用户纠正：7 月 10 日已经搬到杭州，只是现在才告诉你。
```

版本状态可以表示为：

| Version | Content | Valid time | Transaction time |
|---|---|---|---|
| v1 | 上海 | `[-∞, 7/10)` | `[7/1, 7/13)` |
| v2 | 杭州 | `[7/10, +∞)` | `[7/13, +∞)` |

两类查询因此得到不同答案：

```text
现在根据最新证据，7 月 11 日办公室实际在哪里？
→ 杭州（按 valid time）

Agent 在 7 月 11 日运行时，当时系统知道办公室在哪里？
→ 上海（按 transaction-time as-of 7/11）
```

版本模型通常采用：

```text
稳定 Memory Identity
  ├── Version v1：immutable content + valid interval + transaction interval + source
  └── Version v2：immutable content + valid interval + transaction interval + source
```

更新不是覆盖旧正文，而是：

```text
识别同一事实 identity
→ 追加新 version
→ 关闭旧 version 的相应时间区间
→ 更新 current pointer/current view
→ 保留历史和来源
```

它比普通 `version=2 + updated_at` 多表达：

- 回溯更正：今天录入，但事实从过去某天起成立；
- 历史审计：Agent 当时能知道什么；
- point-in-time query：查询任意有效时间或任意系统快照；
- 不覆盖历史：旧版本仍能解释过去行动；
- 冲突保留：两个来源可暂时并存，而不是强制 last-write-wins。

它也不等于普通 event log。Event log 只保存“先后发生了哪些写操作”；双时间状态还给出了“现实有效区间”和“系统认知区间”的正式查询语义。

近期 Graph-Native Bitemporal Memory Store 的实现形状是：

```text
immutable identity node
→ versioned content nodes
→ valid-time interval
→ transaction-time interval
+ HNSW semantic index
```

底层仍是 Neo4j property graph 和向量索引；新意是版本/时间语义，不是新物理载体。[论文](https://arxiv.org/abs/2607.26520)

与两套案例对照：

```text
TencentDB：
  L1 有 version、timestamps 和 append-only JSONL；Skill 有不可变版本
  但没有统一的 valid-time + transaction-time 查询模型

Codex：
  有 Rollout 时间、source_updated_at 和 Git baseline
  但没有稳定的 per-fact identity 和双时间版本节点
```

主要难点：

- identity resolution：新陈述是否真的是同一事实的新版本；
- valid time extraction：自然语言中的“上周”“从下月开始”怎样变成区间；
- overlapping conflict：两个来源在同一有效时间给出不同值；
- filter placement：向量 top-k 后再做时间过滤可能把合法候选全部滤掉；
- 存储与维护成本：版本只追加，历史和索引持续增长；
- 双时间只保证历史可表达，不保证新内容本身正确或更权威。

层级归位：

```text
第三层简写：
  stable identity + immutable versions + valid/transaction time

第四层展开：
  怎样创建新版本、关闭区间、解析冲突、选择 current/history、恢复状态
```

**用户确认与篇幅要求**

第三层用一小段和一个简单例子介绍双时间版本图，重点只回答“要解决什么问题”和“怎样实现”；冲突解析与恢复细节仍留第四层。

**状态：** 已确认

### Q015 — 前沿是否有更复杂的 Memory 图结构

**用户问题**

> 前沿探索里有没有更复杂的图结构？

**回答**

有。近期复杂图的重点不再只是 `entity — relation — entity`，而是增加时间版本、证据依赖、认知类型、因果结果和权限/行动节点。代表结构可以分为五类。

#### 1. 双时间版本图

```text
MemoryIdentity
  ├── HAS_VERSION → ContentV1
  │                  valid_time / transaction_time / source
  └── HAS_VERSION → ContentV2
                     valid_time / transaction_time / source

ContentV2 ── SUPERSEDES / CONFLICTS ──> ContentV1
ContentVx ── SEMANTICALLY_RELATED ──> OtherMemory
```

用于 current/as-of 查询和历史审计。[Graph-Native Bitemporal Memory](https://arxiv.org/abs/2607.26520)

#### 2. Governed dependency/state-trajectory graph

GEM/MemState 不只保存相关边，而是区分：

```text
ASSOCIATED_WITH
  只说明相关，不触发更新传播

EXTENDS / DEPENDS_ON
  上游字段修订后，下游对象可能必须重算、失效或进入 unresolved

POLICY_GOVERNS
  指定某个对象或依赖可执行哪些 ingestion/revision/forget 操作
```

图表示从 `content graph` 扩展为：

```text
content + typed structure + policy + state transition history
```

新意是依赖传播和状态不变量，不只是多跳检索。[GEM/MemState](https://arxiv.org/abs/2605.26252)

#### 3. Epistemic multi-network graph

Hindsight 将 Memory 分为四个逻辑网络：

```text
World Network
  客观外部事实

Experience Network
  Agent 自己做过什么、发生了什么

Observation/Entity Summary Network
  从事实与经历综合出的实体画像

Opinion/Belief Network
  Agent 的可变信念、置信度与时间
```

核心是区分 evidence 与 inference：世界事实不能和 Agent 的观点混成同一种节点；Belief 可以由事实支持、被新证据修正，也应保存 confidence 和演化轨迹。[Hindsight](https://arxiv.org/abs/2512.12818)

#### 4. Causal experience graph

这类图把普通事件链扩展为：

```text
Context
→ Decision
→ Action / Tool Call
→ Observation / Tool Result
→ Outcome
→ Lesson / Skill
```

边可以表达：

```text
DECIDED_IN
LED_TO
FAILED_BECAUSE
VERIFIED_BY
DISTILLED_INTO
APPLIES_WHEN
```

它用于回答“什么做法在什么条件下导致了什么结果”，而不是只找相似文本。风险是模型从一次相关性错误推断因果，跨任务 meta-edge 会放大错误类比。

#### 5. Provenance/authorization/action graph

MAP-Graph 的节点不仅有 Memory，还包括：

```text
Agent
Source
Memory
Claim
Action
```

关系追踪：

```text
Source ── SUPPORTS ──> Claim
Memory ── DERIVED_FROM ──> Source/Memory
Agent ── MAY_READ ──> Memory
Claim ── USED_BY ──> Action
Policy ── AUTHORIZES / DENIES ──> Action
```

读取先沿 ancestry 排除权限不合格来源，再按路径 trust 排序；高风险 Action 需要更强证据门槛。Provenance 从事后审计 metadata 变成运行时控制信号。[MAP-Graph](https://arxiv.org/abs/2608.10509)

#### 综合起来的前沿图

上述方向可以综合为：

```text
Agent ── OBSERVED/REPORTED ──> Event
Event ── PRODUCED ──> ToolResult
Event/ToolResult ── SUPPORTS ──> ClaimVersion
ClaimVersion ── VERSION_OF ──> StableIdentity
ClaimVersion ── VALID_DURING / RECORDED_DURING ──> TimeInterval
ClaimVersion ── EXTENDS / CONFLICTS / SUPERSEDES ──> ClaimVersion
ClaimVersion ── SUPPORTS ──> Belief
Decision ── USED ──> ClaimVersion/Belief
Decision ── LED_TO ──> Action
Action ── PRODUCED ──> Outcome
Outcome ── DISTILLED_INTO ──> Lesson/Skill
Policy ── AUTHORIZES ──> Read/Action
```

没有一个已验证系统完整实现这张综合图；它是多个前沿方向的合成，用于看清复杂度来自哪里，不能描述成已形成的标准。

#### 层级归位

第三层仍不应详细展开这些图，只需说明图表示正在从实体关系扩展为 typed temporal/provenance/causal graph。细节应拆到：

```text
第三层：节点/边类型和载体概览
第四层：version、conflict、dependency propagation、belief revision
第五层：graph traversal、temporal filtering、path trust、ranking
第六层：Action authorization
第七层：decision→outcome→lesson/skill feedback
```

主要风险：图边本身常由 LLM 生成；结构越复杂，错误 entity resolution、虚假因果边、错误 dependency 和高连接污染节点的放大效应越严重。复杂图表达力更强，不等于结果必然更准。

**用户确认与最终取舍**

第三层不介绍 dependency graph、Hindsight 四网络、causal graph、MAP-Graph 或综合复杂图，只保留双时间版本图。正文目标段落：

```text
问题：覆盖更新会丢历史，也混淆“事实何时成立”和“系统何时知道”。

做法：
  stable identity
  → immutable version nodes
  → 每版保存 valid-time interval 和 transaction-time interval
  → 更新时追加版本、关闭旧区间，不覆盖旧内容

能力：
  current query
  valid-time historical query
  transaction-time as-of audit
```

示例只用“7 月 10 日搬到杭州、7 月 13 日才告诉系统”，说明 7 月 11 日现实状态与系统当时认知可以得到不同答案。

**状态：** 已确认；复杂图前沿只保留双时间版本图

### Q016 — 第四层是什么

**用户问题**

> 第四层呢？

**回答**

第四层是**管理与演化层**。

第二层负责首次形成，第三层负责保存；第四层回答：

> Memory 已经存在以后，新证据、用户纠正、时间变化、权限变化或故障发生时，它怎样改变，并怎样保证旧状态、派生物和当前可见状态仍可解释？

基本链路：

```text
输入：
  existing Memory state
  + new evidence / correction / outcome / policy change / delete request / failure
        ↓
第四层管理动作：
  amend / merge / supersede / conflict
  consolidate / promote / demote
  version / expire / decay
  forget / revoke / purge
  repair / rebuild / restore
        ↓
输出：
  new current state
  + preserved history / tombstone / conflict state
  + affected derived indexes/files/skills 的重建或失效状态
  + operation/commit/recovery receipt
```

这一层应重点拆成五类问题：

1. **修订与冲突：** 新内容是补充、替换、矛盾，还是仅在不同条件下分别成立；
2. **巩固与晋升：** 多条原子 Memory 何时合并为 Scene、Persona、Lesson 或 Skill，已有高层对象怎样被新证据改写；
3. **时间与生命周期：** version、valid time、transaction time、TTL、衰减、过期和 current/history；
4. **遗忘与撤销：** disable、forget、revoke、purge 的含义，以及原文删除后摘要、向量、图、缓存和 Skill 是否仍残留；
5. **故障与恢复：** 部分写入、索引滞后、文件/DB 不一致时，怎样 journal、snapshot、rebuild 和恢复完整可见状态。

边界：

- 第二层：第一次从输入形成 L1/L2/L3/Skill 或 Phase 1/2 文件；
- 第三层：当前对象、历史和索引放在哪里；
- 第四层：这些对象以后怎样改变、失效和恢复；
- 第五层：某次查询如何读取当前或历史版本并组装上下文；
- 第七层：任务 outcome 怎样反过来驱动管理策略学习。

这一层后续应重点回答：

- TencentDB：L1 `store/update/merge/skip`、L2 `UPDATE/MERGE/CREATE`、L3 增量重写、Skill immutable versions/active head、Wiki/CodeGraph sync、Asset status/ACL；
- Codex：Phase 2 incremental update、Git diff、usage/recency selection、ad-hoc remember/update/forget notes、thread disable、pollution、full reset 和跨 DB/文件恢复边界；
- 前沿：MemTxn 的 source-supported patch、Temporal Resolver、snapshot journal，以及双时间版本的 current/history 语义。

**影响章节**

- `04-management-evolution.md`：第四层主章节；
- `03-state-storage-indexing.md`：只提供版本、journal、index 等载体，不展开操作；
- `05-retrieval-context.md`：消费第四层生成的 current/history/conflict/revoked 状态；
- `07-feedback-learning.md`：承接 learned controller 和 outcome-driven promotion。

**用户确认**

第四层确定为管理与演化层，并作为重点章节继续拆 TencentDB、Codex 和 MemTxn。

**状态：** 已确认

### Q017 — TencentDB 的管理与演化层怎样工作

**用户问题**

> 第四层先看 TencentDB。

**回答**

TencentDB 不是一个统一 Evolution Engine。Chat Memory、Skill、Wiki、CodeGraph 和 Asset 各有自己的变化机制；真正形成层级联动的是 L1→L2→L3，Skill 是平行版本链。

#### A. L1 — 原子 Memory 的 store/update/merge/skip

每次 L1 抽取出新候选后，先检索 Top-K 相似旧 L1，再把“新候选 + 旧候选”交给冲突/去重 Prompt：

```text
store
  没有相关旧记录，创建新 ID，version=1

update
  新证据替换/修正一个旧记录，保留目标身份，version+1

merge
  多条表达同一对象，合并内容/类型/优先级/timestamps，删除旧 current rows，写新版本

skip
  重复、低价值或不应保存，不改变当前状态
```

历史写入 append-only JSONL，当前可见状态更新到 `l1_records` 及 FTS/vector 投影。因此更新不会抹掉全部历史，但应用查询通常只看当前记录。

#### B. L2 — Scene 的 UPDATE/MERGE/CREATE

新 L1 到来后，Scene Agent 获得：

```text
new L1 contents
+ current scene index(path/summary/heat/updated)
+ 必要的现有 scene Markdown
```

Prompt 决定：

```text
UPDATE  补强一个已有 Scene
MERGE   合并高度重叠的 Scenes
CREATE  新建真正独立的场景
NO-OP   新信息不足以改变 Scene
```

LLM 被限制在 `scene_blocks/`；运行前工程侧备份 Scene 目录，失败或留下部分写入时可恢复，成功后重新扫描 Markdown 并重建 `scene_index.json`。这是一种“生成式文件更新 + 工程备份/索引重建”的管理方式。

#### C. L3 — Persona 的条件触发增量重写

已有 `persona.md` 不会每次 L1/L2 变化都立即重写。触发包括：

```text
首次已有 L2 但没有 Persona
累计 50 条新 L1
L2 写出 PERSONA_UPDATE_REQUEST
系统记录曾生成但 persona.md 正文丢失
```

增量输入：

```text
上次 Persona 成功时间之后发生变化的 L2 完整正文
+ old persona.md
+ trigger reason / counters / scene stats
```

Prompt 要求在同一份 Persona 上：

- 新场景再次支持旧规则时不要重复追加；
- 新证据限制旧规则时改写适用条件；
- 重复原则合并；
- 只描述临时项目状态时不晋升为长期准则；
- 保持长度上限和固定结构。

大改用 `write`，局部修改用 `edit`；成功后计数归零，工程侧重新追加 L2 导航。L3 是重写 current file，不是每条规则拥有独立版本节点；历史主要依赖备份/外部同步，而不是双时间 per-rule model。

#### D. 一条跨 Session 修正怎样传播

```text
Session A：
  用户：所有代码修改都先写失败测试
  → L1 v1
  → L2“缺陷修复与回归”
  → L3“所有修改先写失败测试”

Session B：
  用户：纯重构没有待修复失败，但必须先建立行为基线
  → 新 L1
  → 与旧 work_method 做 update/merge
  → L2 UPDATE：区分缺陷修复与纯重构
  → 触发 Persona update 后重写 L3：
     缺陷修复先建立失败证据；纯重构先建立行为基线
```

这条传播不是数据库 dependency graph 自动执行，而是 L1 scheduler、L2 Prompt 和 L3 trigger/Prompt 串联完成；若某一级未触发或生成失败，高层状态可能暂时仍旧。

#### E. Skill — 不可变版本与 Active Head

Skill 按 `(skill_id, version)` 保存不可变快照。新 Session 轨迹到来时，Review Agent 先 `skill_list`/`skill_view` 当前版本，再选择：

```text
Nothing to save
create
update full SKILL.md
patch selected section
files_write supporting file
```

对已有 Skill 的每次写入都必须带刚读取的 `expected_version`。成功后：

```text
旧 version：is_head=0，保留历史
新 version：is_head=1，成为 active head
FTS/vector：只索引 active head
```

例子：

```text
v1：Token 撤销流程
v2：加入多实例必须使用共享 Store
v3：Validation 增加旧 Token 和并发刷新回归
```

“先读后写”主要由 Prompt 约束；工具层不会强制 Review Agent 一定先 list。代码能阻止同名 head 冲突和 stale `expected_version`，但语义相近、名称不同的重复 Skill 仍可能出现。后台 Review 没有 delete 工具。

#### F. Wiki — Source SHA 驱动的增量重建

Wiki 不是由对话反馈自动演化，而是原始文档发生变化后显式 ingest：

```text
source SHA unchanged
→ skip

source SHA changed/new/previous failed
→ Analyze Prompt
→ Generate/merge Markdown pages
→ 保护 locked pages、合并 sources
→ 同一事务重建 FTS/page_meta/graph_edge/source
→ version/status/audit 更新
```

它的演化权威来自文档 source，而不是 Agent 使用效果。

#### G. CodeGraph — Commit/文件变化驱动 Sync

```text
首次：clone + init + indexAll
已有：open + indexAll 或 sync changed files
触发：手工 sync 或 Auto Sync Scheduler
输出：新 commit_hash、files/nodes/edges、stats、status/version/audit
```

CodeGraph 的演化来自真实仓库变化，不由对话反思自动改写关系。索引失败会进入 failed/sync_error；实际改代码前仍需用当前 Workspace 源码确认。

#### H. Asset/ACL/Binding — 控制传播，不改变正文

人可以通过：

```text
visibility / ACL
bind / unbind
status：active / archived / deprecated / failed 等
version / fork
```

控制哪些资产能进入某个 Agent 的新 Session。Fork 会复制内容，之后两份独立演化；runtime 会过滤不可见或失效状态。`meta_assets` 和 binding 只改变传播/装配资格，不自动修改真实 Memory/Skill/Wiki/CodeGraph 正文。

#### I. 当前没有闭合的自动效果学习

Asset Reflection 默认关闭；即使开启，Agent 只在回答末尾写文字反思，系统当前不自动解析它，也不会据此调整 Asset 排名、修改内容或淘汰资产。

因此 TencentDB 已经闭合：

```text
新证据 → 对象更新/版本/索引同步 → 新 Session 可见
```

尚未闭合：

```text
资产被使用
→ 对最终任务质量的归因
→ 自动评分
→ 自动强化/降级/淘汰
```

后者应留第七层反馈学习讨论。

#### J. 删除与全链修复边界

L0/L1、Skill、Asset 和 Knowledge 各自有删除或状态操作，但当前材料没有显示一个统一 lineage engine 能保证：删除原始 L1 后，所有由它形成的 L2、L3、Skill、缓存和已分发副本都自动同步撤销。

所以不能把某个 `delete` API 写成“完整遗忘”。第四层应明确区分对象删除、检索不可见、Asset 失效和派生物清理。

**TencentDB 第四层的主线**

```text
Chat：
  L1 versioned mutation
  → L2 generated Scene update
  → conditional L3 Persona rewrite

Skill：
  immutable versions + optimistic expected_version + active head

Wiki/CodeGraph：
  source/commit-driven incremental rebuild

Asset：
  visibility/status/ACL/binding/fork governance

缺口：
  无自动 outcome attribution
  无统一 derived-delete propagation
  无跨所有子系统的单一 transaction/recovery boundary
```

**影响章节**

- `04-management-evolution.md`：TencentDB 重点展开 Chat L1→L2→L3 与 Skill 版本链；
- Wiki/CodeGraph 只简写 source/commit-driven sync；
- Asset 只写传播治理；
- 自动效果学习移第七层；
- 删除传播缺口作为第四层结论保留。

**用户确认与范围收窄**

TencentDB 第四层只写 L0–L3 与 Skill 的管理，并且作为重点详细展开。Wiki、CodeGraph、Asset Registry、ACL 和 Binding 不进入本节；效果反馈仍留第七层。

正文详细范围：

```text
L0
  增量捕获 cursor、重复保护、JSONL/当前视图、保留与清理、删除边界

L1
  store/update/merge/skip
  version increment
  append-only history 与 current row/index 的变化
  source_message_ids 与 scope

L2
  UPDATE/MERGE/CREATE/NO-OP Prompt
  Scene 文件改写、合并和删除
  运行前 backup、失败 restore、成功后 scene index rebuild

L3
  首次/阈值/PERSONA_UPDATE_REQUEST/recovery triggers
  old persona + changed scenes 的增量 Prompt
  write/edit、规则收窄/合并/删除、计数重置、导航重建与 Session cache

Skill
  list/view-before-write Prompt
  create/update/patch/files_write/no-op
  expected_version optimistic concurrency
  immutable versions、content_hash/manifest、active head、FTS/vector head 更新
  stale retry、后台 Review 无 delete、人工状态/Fork 的边界
```

使用“失败测试规则被纯重构例外修正”的跨 Session 例子贯穿 L1→L2→L3；使用 Token 撤销 Skill v1→v2→v3 贯穿 Skill 版本链。

事实与细节以 TencentDB Agent Memory 固定提交 `0aff21a` 原仓库为准，优先读取：

- `MemoryCore/src/core/conversation/`
- `MemoryCore/src/core/record/`
- `MemoryCore/src/core/scene/`
- `MemoryCore/src/core/persona/`
- `MemoryCore/src/core/skill/`
- 对应 prompts、store 和 pipeline worker

**状态：** 已确认

### Q018 — Codex 的管理与演化层怎样工作

**用户问题**

> 第四层对应的 Codex 呢？

**回答**

Codex 没有 TencentDB 那样独立的 L1/L2/L3 状态机。它的管理核心是：Stage 1 候选持续滚动，Phase 2 根据候选/旧文件/Git diff 重写同一套全局 Memory 文件；Thread policy、ad-hoc notes、pollution 和 reset 从不同入口影响这条链。

#### A. 候选生命周期与滚动选择

Phase 1 每次重新处理一个发生变化的 Thread 时，以新的 `source_updated_at` 覆盖/更新对应 Stage 1 output。Phase 2 从当前候选池中最多选择 256 条：

```text
usage_count DESC
→ last_usage 或 source_updated_at DESC
→ source_updated_at DESC
→ thread_id DESC
```

曾被引用的候选以 `last_usage` 判断 30 天新鲜度；从未使用的候选按 source 时间判断。长期未使用的候选可以在 startup cleanup 中被清理。

Phase 2 成功后，精确选中集合以 snapshot 一次写回：

```text
selected_for_phase2=true/false
selected_for_phase2_source_updated_at
```

这不是内容正确性评分，只是使用与新鲜度驱动的保留/巩固资格。

#### B. Phase 2 Incremental Update：Git diff 驱动全局重写

每次 Phase 2：

```text
领取 global singleton job + ownership token + lease
→ 选择 Stage 1 candidates
→ 物化 raw_memories.md / rollout_summaries
→ 相对上次成功 Git baseline 生成 bounded diff
→ 受限 Consolidation Agent 读取 diff、旧 MEMORY、旧 summary、skills 和 notes
→ 增量编辑 MEMORY.md / memory_summary.md / skills
→ 验证文件与 ownership
→ 重置 Git baseline
→ 事务提交 job watermark + selected snapshot
```

Prompt 明确要求：

- 新增候选应合并进恰当 task group，而非机械追加；
- 删除/修改输入必须传播；
- 一个 Memory block 若同时有已删除和仍有效来源，只移除 stale reference/局部结论，不能整块删除；
- `MEMORY.md` 清理后同步修正 `memory_summary.md`；
- 没有 meaningful signal 时保持最小变更；
- 不打开原始 Rollout transcript。

所以 Codex 的“版本”不是 per-fact revision，而是整套文件在连续 Git baseline 之间的生成式 current state。

#### C. Citation usage → Retention Signal

未来 Agent 使用 Memory 后，最终 citation 携带 rollout IDs。系统解析后：

```text
usage_count += 1
last_usage = now
```

这会让候选下一次更可能进入 Phase 2。它闭合的是：

```text
被引用 → 更容易保留
```

没有闭合：

```text
被引用 → 任务真的更成功
```

也没有记录“被展示但未采用”的 exposure。其自强化和 outcome attribution 应在第七层讨论。

#### D. 用户显式 remember/update/forget → Append-only Note

主 Agent 不允许直接编辑 `MEMORY.md`。只有用户明确提出记住、更新或忘记时，专用写工具才在：

```text
extensions/ad_hoc/notes/<timestamp>-<slug>.md
```

创建一个 `create_new`、不可覆盖的小文件。它记录用户希望怎样改变 Memory，不是直接 mutation。

下一次 Phase 2 把 note 当作必须处理的输入：

```text
用户：忘记“本地 Map 可用于生产”
→ append-only forget note
→ Phase 2 读取 note + 旧 MEMORY.md
→ 删除/收窄旧结论
→ 更新 MEMORY.md 和 memory_summary.md
```

这是异步、模型解释的 soft update；没有 stable entry ID、同步 patch result 或 clause-level deletion receipt。

#### E. Thread Mode 与 External-context Pollution

每条 Thread 可以 enabled/disabled：

```text
disabled
→ 只阻止该 Thread 以后成为 Phase 1 输入
→ 不自动删除已经进入 MEMORY.md 的派生结论
```

若启用 `disable_on_external_context`，Web Search、Tool Search、外部 MCP/tool content 可以把 Thread 标记为 polluted。若该 Thread 曾进入上一版 Phase 2 selection，系统排队新的 consolidation，让 Phase 2 移除仅由该 Thread 支撑的文件内容。

但该策略固定版本默认关闭，因此不是强制 invariant；污染清理仍由生成式 Phase 2 完成。

#### F. Full Reset：清生成状态，不清原始历史

Reset 顺序：

```text
1. 事务删除 memories_1.sqlite 的 stage1_outputs/jobs
2. 清空 ~/.codex/memories/ 文件工作区
```

它不删除：

```text
state_5.sqlite 中的原始 Thread
Rollout JSONL
Thread memory_mode
```

因此仍在 10 天窗口、已空闲且 enabled 的旧 Thread，可以在之后 startup 中再次被 Phase 1 抽取。Reset 的准确语义是“清除当前生成式 Local Memory”，不是不可逆删除历史来源。

DB 删除和文件清理也不是跨介质原子事务：若第二步失败，可能出现 DB 已空但旧文件仍在。

#### G. 并发、失败与恢复边界

已有确定性控制：

```text
Phase 1 per-thread job：ownership token / lease / retry / source watermark
Phase 2 global job：singleton / heartbeat / stale lease takeover
成功提交：job watermark + selected flags 同一 Memory DB transaction
文件侧：Git baseline 让下次运行看到未完成 diff
安全：拒绝 symlink、校验必要文件和 summary v1 header
```

仍未闭合：

- Phase 2 selector 多个 LIMIT/OFFSET 查询不在单一 read transaction，并发 Stage 1 insert 可能使分页漂移；
- Consolidation Agent 修改多个文件不是事务写，失败前可能留下部分文件；
- 没有明确 reader/writer snapshot，正在读取的新 Thread 是否可能看到中间状态不清楚；
- Git diff 能帮助下次修复，不证明当前文件语义完整；
- validator 只检查文件形状和路径安全，不验证事实来源、冲突或删除是否正确。

#### H. 一条规则在 Codex 中怎样修正

```text
已有 MEMORY.md：
  “所有代码修改前先写失败测试”

新 Thread B：
  用户明确说“纯重构只需行为基线”
→ Phase 1 B 产生 raw_memory
→ Stage 1 candidate B
→ 下一次 Phase 2 选中 A/B
→ Git diff 显示新增 B
→ Consolidation Agent 重写：
   缺陷修复先失败测试；纯重构先行为基线
→ 更新 memory_summary 导航
→ baseline reset + selection snapshot commit
```

这里没有 per-rule stable ID、`SUPERSEDES` edge 或 valid-time interval；旧规则的历史主要存在于旧 Rollout、Stage 1 source 与 Git 差异中，当前 Agent 只读取最新版文件。

#### Codex 第四层主线

```text
新/变化 Rollout
→ Stage 1 candidate refresh
→ usage/recency selection
→ Phase 2 Git-diff incremental rewrite
→ current Markdown Memory

显式控制：
  remember/update/forget → ad-hoc note → Phase 2
  thread disable → future formation eligibility only
  pollution → optional re-consolidation
  reset → candidates/files clear，sources retained

可靠性：
  DB jobs/lease/watermark 较明确
  文件语义与跨介质 transaction 较弱
```

**影响章节**

- `04-management-evolution.md`：Codex 重点沿 Phase 2 incremental update、notes、disable/pollution/reset 和失败恢复展开；
- usage 只作为 deterministic retention signal 简写，详细偏差移第七层；
- 搜索和 citation 生成过程移第五层；
- 与 TencentDB 对照时强调“显式对象版本链”与“全局文件重写”的差异。

**状态：** 待确认

### B002 — 每个机制统一回答五个问题

七层正文中的每个主要机制至少应写清：

```text
输入是什么
→ 如何处理
→ 输出是什么
→ 用一个具体例子完整走一遍
→ 输出进入下一层的哪里
```

不能用“支持形成、管理、检索、演化”等抽象动词替代数据结构和状态变化。

**状态：** 已确认

### B003 — Prompt 是实现机制的一部分

对于由 LLM 执行判断的阶段，Prompt 决定：

- 什么值得保存；
- 什么必须丢弃或 no-op；
- 如何区分事实、偏好、流程和临时信息；
- 输出 schema；
- 去重、更新、合并和遗忘规则；
- 安全、证据和来源边界。

因此 Prompt 不能只作为源码追溯材料；应提炼其中真正定义行为的规则，并配合输入输出例子解释。

**状态：** 已确认

### B004 — TencentDB 与 Codex 的共性优先于产品名词

两者的核心形状接近：

```text
原始对话与执行轨迹
→ 单次经历抽取
→ 候选状态
→ 跨经历巩固
→ 分层注入或按需读取
→ 使用反馈与后续更新
```

正文应先解释这类共同机制，再用 TencentDB、Codex 等实现展示粒度、状态机、作用域和治理差异，不能把不同文件名包装成不同架构范式。

**状态：** 已确认

### B005 — 问答驱动重写

接下来由用户逐项提问，回答和确认结论持续记录在本文。七层正文不提前一次性重写；待相应问题树澄清后，再依据确认记录更新目标章节。

**状态：** 已确认

## 问答记录

### Q019 — 第四层应聚焦更新和删除

**用户问题**

> Q017 的 7、8、9 太细枝末节，不应该作为 Memory 管理主线。第四层应关注管理本身，无非是增删改；增加已经在写入层说了，所以重点讲清更新和删除。

**回答与范围修正**

同意。第四层从“后台控制/故障清单”收缩为已有 Memory 的两类核心变更：

```text
更新（update / amend / merge / supersede）
删除（forget / revoke / expire / purge）
```

“演化”只是持续更新的总称；lease、usage 排序、pollution 标记、reset 顺序、snapshot 事务等只在解释某个更新/删除语义时作为实现证据或限制出现，不作为章节主线。

### 更新应回答什么

```text
输入：已有 Memory + 新证据/用户纠正/版本变化
处理：找到同一对象或相关对象
      → 判断补充、替换、合并、冲突或 supersede
      → 保留必要历史/来源
      → 更新当前可见表示及派生物
输出：更新后的 current Memory
      + history/version/provenance
      + 派生物是否已同步的状态
```

TencentDB 的重点例子：

- L1：`update/merge` 保留或递增对象版本；
- L2：Scene `UPDATE/MERGE` 改写已有场景；
- L3：用变化 L2 和旧 Persona 重写长期规则；
- Skill：以 `expected_version` 写入新 immutable version，移动 active head。

Codex 的重点例子：

- Phase 2 根据新增候选和 workspace diff 重写 `MEMORY.md`/`memory_summary.md`/skills；
- 它是文件级生成式更新，不是稳定 Memory ID 上的结构化 per-item update；
- 用户显式 update 先变成 ad-hoc note，再由 Phase 2 解释并改写正式文件。

### 删除应回答什么

```text
输入：用户 forget、来源撤销、过期条件或删除策略
处理：判断是停止产生、停止可见、逻辑删除、撤销传播还是物理清除
      → 找到由该对象派生的摘要/索引/场景/Persona/Skill
      → 清理、重建或标记 tombstone
输出：删除后的 current view
      + 哪些历史/审计仍保留
      + 哪些派生物已清理、待清理或未知
```

TencentDB 和 Codex 都不能简单把一个 delete API 等同于完整遗忘：

- TencentDB 需要分别看 L1、Scene、Persona、Skill 的删除/失效路径；
- Codex 的 forget 是 note→Phase 2 重写，Thread disable 只停止未来形成，reset 只清当前生成状态而保留来源历史。

这些差异应作为“更新/删除语义的实现对照”出现，而不是扩展成一长串运行细节。

### 第四层最终结构

```text
第四层：管理与演化

1. 更新
   - TencentDB L1/L2/L3/Skill
   - Codex Phase 2 文件更新

2. 删除
   - 对象删除、失效、撤销、派生清理
   - TencentDB/Codex 的不完整传播边界

3. 前沿短桥
   - MemTxn：source-supported proposal → commit/reject
   - 双时间版本：current/history 的管理基础
```

不再单独设：候选滚动选择、pollution、reset、lease、heartbeat、snapshot 等小节；这些只在相关更新/删除案例中用一句说明。

**影响章节**

- `04-management-evolution.md`：重写为“更新”和“删除”两大主节；
- `02-write-formation.md`：只保留首次新增/创建；
- `03-state-storage-indexing.md`：只介绍版本、历史、tombstone、索引载体；
- `07-feedback-learning.md`：承接 usage/outcome 如何决定未来是否更新、晋升或遗忘。

**状态：** 已确认；Q017/Q018 的细节降为更新/删除案例证据

### Q020 — TencentDB 是否根本没有删除

**用户问题**

> TencentDB 里面根本就没有删除的内容吧？

**核对与纠正**

需要区分“存在删除接口”和“存在统一 Forget/删除传播语义”。固定提交 `0aff21a` 中确实有删除路径：

```text
L0：/conversation/delete
    删除 l0_conversations 当前行及 l0_fts/l0_vec 投影

L1：/atomic/delete
    删除 l1_records 当前行及 l1_fts/l1_vec 投影，并写 L1 delete audit

L2：/scenario/rm
    删除 scene_blocks 文件，清理 L2 VDB profile，刷新 scene_index

Skill：/skill/delete
    按 expected_version 校验后物理删除所有版本和 storage files
```

但这些不构成统一的 Memory deletion：

- L0/L1 delete 路由操作当前 SQLite/VDB/索引视图，L0/L1 append-only JSONL 历史并不会因此自动变成不可恢复；
- 删除 L1 不会自动查找并删除由它形成的 L2 Scene、L3 Persona 或 Skill；
- L2 `scenario/rm` 是按文件路径移除场景，不是从来源 lineage 自动传播的 forget；
- L3 只有 `core/read`、`core/write`、`core/count`，没有独立 `core/delete` 路由；清空/改写 Persona 不能等同于有结构化删除语义；
- Skill Review Agent 的形成 Prompt 没有 delete tool，但外部 Skill API 有 delete/archive 路径；这属于显式管理 API，不是自动 Review 闭环。

因此第四层对 TencentDB 的准确写法应是：

```text
更新：有清晰的 L1/L2/L3/Skill 更新链

删除：各层有局部删除/移除 API，
      但没有统一的 cross-layer forget、lineage propagation
      或“删除收据证明所有派生物已清理”的闭环
```

如果从“自动 Memory 演化 Prompt”角度说“没有删除”，应改成：

> TencentDB 的自动 L1/L2/L3/Skill 形成链没有一个统一的 Forget 操作；仓库虽提供分层删除 API，但其语义和传播范围各不相同。

这比简单写“没有删除”准确，也比把局部 delete API 写成完整遗忘更准确。

**影响章节**

- `04-management-evolution.md`：TencentDB 主线以“更新”为重点；“删除”只用上述边界短节说明局部 API 与缺失的统一传播；
- 删除不再被写成一条已经闭合的 L0→L3 自动管理能力；
- `03-state-storage-indexing.md`：只说明删除后 current view/index 与历史正文可能分离。

**状态：** 待确认

### Q021 — 删除是谁发起的，和直接删数据库有什么区别

**用户问题**

> 这些删除不是 Agent 自己完成的吧？如果是人来删，和直接删数据库有什么区别？这也要讲吗？

**回答与纠正**

要区分“谁发起”“谁执行”和“删除的语义”。TencentDB 各层不一样：

| 层/对象 | 发起方式 | 实际执行 | 说明 |
|---|---|---|---|
| L0 | 外部 conversation/delete API/控制面 | Store 删除当前 L0 row + FTS/vector | 不是自动 Memory Agent 的 forget；原始 JSONL 历史不因此自动擦除 |
| L1 | 外部 atomic/delete；update/merge 时 Writer 也会移除旧 current row | Store/VectorStore 事务删除当前 row 和投影 | 是对象/当前视图删除，不是跨层派生清除 |
| L2 Scene | Scene Agent 可用文件工具写 `[DELETED]` 标记 | SceneExtractor 工程代码 unlink 文件、清 L2 VDB、重建 index | 这是 Agent 提议/发起 + 工程执行的软删到物理清理链 |
| L3 Persona | 没有独立 core/delete API | 可通过 core/write 重写内容；删除语义不单独建模 | 不是结构化 forget |
| Skill | Review Agent 没有 delete tool | 外部 skill/delete API 按权限与 expected_version 物理删版本/资源 | 是控制面管理动作，不是自动 Review 决策 |

所以“人来删”和“直接删数据库”不是一回事：

```text
用户/管理员/API 请求
→ 身份、owner、scope、版本和参数校验
→ 领域层删除语义
→ 同步当前正文、FTS/vector/scene 等相关投影
→ audit / quota / 状态反馈
```

而直接 SQL/文件删除：

```text
绕过鉴权、scope、expected_version 和业务审计
可能留下 JSONL 历史、向量/FTS、Scene index、Asset binding 或派生 Persona/Skill
也不会产生可解释的 deletion receipt
```

不过 TencentDB 的 API 删除本身也不是完整 Forget：L0/L1 的当前视图删除与 append-only 历史分离，删除一个 L1 不会自动沿 lineage 清理 L2/L3/Skill。因此报告不应把“有 API 删除”写成“系统支持完整遗忘”。

**是否写进第四层**

要写，但只保留一个简短的删除边界框，不展开运维细节：

1. 删除动作的发起者/执行者可能不同（Agent 提议、API/人发起、工程层执行）；
2. 领域 API 删除不等于直接删数据库；
3. TencentDB 只有分层局部删除，没有统一跨层 Forget。

这能解释删除语义，而不是增加一节“数据库怎么删”。

**源码依据**

- L0/L1 delete routes：`MemoryCore/src/gateway/v2-router.ts`；
- L2 `[DELETED]` Prompt 与 cleanup：`MemoryCore/src/core/prompts/scene-extraction.ts`、`MemoryCore/src/core/scene/scene-extractor.ts`；
- Skill Review 工具清单与 delete API：`MemoryCore/src/core/skill/prompts/skill-review-prompt.ts`、`MemoryCore/src/gateway/skill-handlers.ts`。

**状态：** 待确认

### Q022 — 第四层删除只讨论自动或 Agent 自主机制

**用户纠正**

通过 API、面板或人工直接发起的删除，不属于本次 Agent Memory 管理主线；直接操作数据库也不属于要研究的 Agent 机制。第四层只保留：

```text
自动生命周期清理
或
Agent 在形成/管理过程中自主决定的删除、替换、降级和淘汰
```

**范围修正**

TencentDB 第四层删除不再罗列外部 API 和数据库删除差异，只核对以下自动/Agent 内部机制：

1. **L1 自动更新/合并中的旧 current 移除：** Dedup Prompt 选择 `update/merge` 后，Writer 移除目标记录的当前 Store/FTS/vector 表示，再写入合并后的新记录；这是更新的一部分，不是用户 forget。
2. **L2 Scene Agent 的自主软删：** Scene Prompt 明确要求合并旧场景时用 `write(path, content="[DELETED]")`；工程 cleanup 随后 unlink 文件、清 L2 视图并重建 scene index。这是本仓库最明确的 Agent 自主删除机制。
3. **L3 Persona 的隐式删除：** Persona Agent 通过重写同一 `persona.md` 删除或收窄旧规则，但没有独立 delete operator；它应作为更新中的“旧内容被移除”说明。
4. **Skill：** Review Agent 工具集合没有 delete，因此不写成 Agent 自主删除；版本 TTL/后台清理若要提及，只作为自动存储清理，不等同语义 forget。
5. **L0/L1 retention cleaner：** 按 retentionDays 自动清理过期文件和当前 L0/L1 Store，可作为一句“物理保留策略”带过，但不把它解释为跨层语义删除。

外部 `conversation/delete`、`atomic/delete`、`scenario/rm`、`skill/delete` 只证明产品有管理 API，不进入 Agent Memory 主线，也不作为第四层重点。

**第四层删除的准确结论**

```text
TencentDB 有局部自动/Agent 删除：
  L1 update/merge 的旧 current 移除
  L2 Agent [DELETED] → cleanup
  L3 重写时移除旧规则
  L0/L1 TTL 物理清理

但没有：
  统一 Agent forget operator
  L1 → L2 → L3 → Skill 的自动派生删除传播
  跨层 deletion receipt / lineage proof
```

“人/API 删除”和“直接删数据库”的区别从第四层正文删除；若需要，只在方法限制中说明不把管理 CRUD 当作 Agent 自主行为。

**状态：** 已确认；第四层只保留自动/Agent 自主更新与删除

### Q023 — TencentDB 的自动/Agent 删除在什么情况下发生

**用户问题**

> 局部自动/Agent 删除在什么情况下会删除？

**回答**

只看自动机制和 Agent 自主决定时，TencentDB 的删除/移除条件如下。

#### L1：update/merge 时移除旧 current

这不是独立的 forget，而是 L1 去重决策的一部分：

```text
新 L1 候选
→ 向量或 FTS 找到 Top-K 旧候选
→ LLM 冲突 Prompt 判断 update 或 merge
→ target_ids 指向旧记录
→ Writer 从当前 Store/FTS/vector 移除 target_ids
→ 写入新/合并后的记录
```

触发条件是：新候选与旧记录被判断为同一事实的更具体版本、重复表达或需要合并；如果判断为 `store`，不删除；如果 `skip`，不写入也不删除。旧 JSONL 历史仍保留，这就是“当前表示替换”，不是完整遗忘。

#### L2：Scene Agent 合并或淘汰场景时自主软删

这是最明确的 Agent 自主删除：

```text
新 L1 + 现有 Scene summary
→ Scene Agent 判断需要 MERGE/删除旧 Scene
→ 用 write(path, "[DELETED]") 标记旧文件
→ 工程 cleanup 发现标记并 unlink
→ 清理 L2 当前视图
→ 重建 scene_index
```

Prompt 规定的触发情形包括：

- 场景文件数量达到/超过上限，必须先合并 2–4 个相似场景；
- 新旧场景属于同一项目链路、工作流或方法体系，应主动合并；
- 没有明显重叠时，优先合并或删除热度最低的场景；
- 合并新文件后，旧文件必须用 `[DELETED]` 删除，不能只写 `[ARCHIVE]` 或 `[CONSOLIDATED]`。

默认策略仍是 UPDATE，不是 CREATE；删除主要发生在 MERGE/容量治理的分支。

#### L3：没有独立删除动作，只有重写时移除旧规则

Persona Agent 的输入是旧 Persona + 变化 Scene。它可能因为新证据限制旧规则、规则重复或内容不再适用而把旧句子从 `persona.md` 中删掉或改写，但这是一次 Persona update：

```text
旧规则被重写/收窄
→ 新 persona.md
```

没有 `persona/delete` 或按规则 ID 的自主删除操作。

#### L0/L1：Retention Cleaner 的自动物理清理

配置 `retentionDays > 0` 时，定时 Cleaner 会按时间删除过期的 L0/L1 shard 文件和当前 Store 记录；同时有最小保留数量和一次清理比例保护。这是：

```text
时间/保留策略 → 物理清理
```

不是 LLM 根据语义判断“这条记忆应该忘记”。

#### Skill：Review Agent 不自主删除

Skill Review 的工具集合只有：

```text
list / view / create / update / patch / files_write
```

没有 delete tool。因此重复 Skill 通常通过 update/patch 或 no-op 处理，不会由 Review Agent 删除。若配置了非 head 版本 TTL，后台可清理过期历史版本，但那是存储保留策略，不是语义 Forget。

#### 结论

```text
真正的 Agent 自主删除：
  L2 MERGE/容量治理 → [DELETED] → cleanup

自动物理清理：
  L0/L1 retention TTL
  Skill 非 head version TTL（若启用）

更新中的旧表示移除：
  L1 update/merge
  L3 Persona rewrite

没有：
  统一的跨层语义 Forget
  从 L1 删除自动传播到 L2/L3/Skill
```

API、面板和直接数据库操作不纳入这一节。

**状态：** 待确认

### Q024 — Codex 的自动/Agent 自主更新与删除

**用户问题**

> TencentDB 的删除只看自动机制或 Agent 自主决定，不看人工/API。然后 Codex 呢？

**回答**

Codex 的第四层也只保留自动或内部 Consolidation Agent 的行为；用户通过 ad-hoc note 的显式请求、reset API 和直接文件/数据库操作不作为主线。

#### 更新

Codex 的主要更新机制是内部 Phase 2 Consolidation Agent：

```text
新增/变化 Stage 1 candidates
+ 旧 MEMORY.md / summary / skills
+ workspace diff
→ Consolidation Agent 判断保留、合并、改写或移除旧表述
→ 写出新的 MEMORY.md / memory_summary.md / skills
```

触发的不是某个稳定 item ID update，而是候选进入下一轮 Phase 2；因此 Codex 的更新是**全局文件级生成式重写**。

内部 Agent 可以在以下情况下移除旧内容：

- 新候选明确修正旧结论；
- diff 显示某个来源输入被删除或失效；
- 某个结论只由已删除来源支撑；
- 新旧内容重复，需要合并；
- 用户 note（这里只作为控制输入的实现边界，不作为自动反馈）要求 forget/update。

#### 删除

严格按自动/Agent 自主机制，Codex 没有独立的通用 `forget(item_id)` 自动操作。删除主要表现为：

```text
Phase 2 Consolidation Agent
→ 在增量重写 MEMORY.md / summary / skills 时删除或收窄旧内容
```

自动触发删除/重整的主要来源是：

1. **Phase 2 看到删除的输入：** workspace diff 中某个 `rollout_summary` 或扩展资源被删除；Prompt 要求只移除由该来源单独支撑的结论；
2. **外部内容污染（启用 opt-in 配置时）：** 被标记 polluted 的 Thread 若曾进入上一轮 selection，会排队下一次 consolidation，尝试移除仅由该 Thread 支撑的内容；
3. **生成式合并/修正：** 新证据使旧表述不再适用，Consolidation Agent 在重写时删掉旧句或缩小范围；
4. **候选保留清理：** 长期未使用的 Stage 1 rows 可被自动清理，但这只是候选库保留策略，不是已发布 Memory 的语义删除。

`memory_summary.md` 和 `MEMORY.md` 的删除由内部 Agent 通过文件写入完成；没有独立的逐条删除收据，也没有保证所有历史 Rollout、缓存或已编译上下文同步消失。

#### 与 TencentDB 的差异

```text
TencentDB：
  L2 Scene Agent 有明确 [DELETED] 文件动作
  L1 update/merge 有明确 target current 移除

Codex：
  主要是 Phase 2 重写文件时隐式删/改旧文本
  没有独立 delete tool 或稳定 item-level forget operator
```

因此 Codex 的自动删除更弱、更难审计；应在第四层用一段对照说明，不写 API CRUD 和 reset 运维细节。

**影响章节**

- `04-management-evolution.md`：Codex 只写文件级更新和隐式删除；
- 删除重点是“什么输入变化会让 Phase 2 移除旧内容”，不是操作接口；
- `07-feedback-learning.md`：usage 影响保留排序，但不等同删除决策。

**状态：** 待确认

### Q025 — 两套系统是否都没有真正的遗忘，管理重点是冲突更新

**用户判断**

> TencentDB 和 Codex 本质上都没有真正的遗忘功能；这些操作主要还是更新，主要特点在于解决冲突。

**回答与确认**

这个判断成立，需要把“删除”拆成三个层级：

```text
1. 检索抑制：不再把内容返回给 Agent
2. 当前视图删除：从当前 DB/file/index 中移除
3. 语义遗忘：
   原始来源、历史、摘要、向量、图、Persona、Skill、缓存、备份
   和未来再生成路径全部被撤销，并有可验证 deletion receipt
```

TencentDB 和 Codex 都能在局部做到第 1/2 层，但没有统一、可验证的第 3 层：

- TencentDB L1 update/merge 会替换当前记录，L2 `[DELETED]` 会移除场景文件，L3/Skill 可以被重写或失效；但没有跨 L1→L2→L3→Skill 的统一 lineage/revocation 传播；
- Codex Phase 2 可以在文件重写中删掉旧句子、段落或 Skill 内容，但原始 Rollout 仍保留，没有稳定 item identity、全派生删除和防止旧来源再生成的统一语义。

因此第四层的主问题不应写成“如何实现 forget”，而应写成：

```text
新证据/纠正到来
→ 找到相关旧对象
→ 判断 ADD 之外的 UPDATE / MERGE / SUPERSEDE / CONFLICT / NO-OP
→ 选择当前可见表示
→ 重写或重建派生对象
```

“冲突”也不只指两段文本互相矛盾，还包括：

- 同一事实的新旧版本；
- 更具体规则限制旧的绝对规则；
- 多条记忆重复但粒度不同；
- 不同 scope、时间或主体下各自成立的陈述；
- 一条来源失效后，哪些派生结论仍有其他来源支撑。

第四层最终主线收敛为：

```text
重点：更新与冲突解决
  dedup / merge / supersede / conditional rewrite / version

删除：只作为更新和冲突解决的边界结果简述
  hide / remove current / stale cleanup
  但不宣称是完整语义遗忘
```

MemTxn 的位置也更清楚：它不是先介绍一个“删除系统”，而是展示怎样把模型的 update proposal 放进 source-supported admission、版本冲突选择和可恢复提交边界。

**影响章节**

- `04-management-evolution.md`：标题和主线改为“更新、合并与冲突解决”；
- 删除只保留“局部移除不等于语义遗忘”的边界框；
- `07-feedback-learning.md`：讨论 outcome 如何影响未来保留、晋升或更新策略；
- 所有“forget”措辞必须注明是局部/派生层语义，不能写成端到端遗忘。

**状态：** 已确认

### Q026 — 第四层的现有实现与前沿遗忘应如何并列

**用户判断**

> 更新、合并与冲突解决是 TencentDB 和 Codex 主要覆盖的；遗忘是它们没有覆盖的，但也应作为管理的一部分，由前沿技术探索补充。

**回答与确认**

同意。第四层应明确分成两段，而不是把两者混写：

```text
A. 现有工程已覆盖
   UPDATE / MERGE / SUPERSEDE / CONFLICT
   TencentDB 与 Codex 的实际实现对照

B. 现有工程缺口 + 前沿补充
   FORGET / REVOKE / RELEASE / PURGE / RESTORE
   说明完整遗忘应怎样定义和验证
```

这里的“遗忘”不是一个模糊的 delete，而应由前沿研究拆成不同语义：

```text
suppression
  暂停召回，但对象/history 仍保留

tombstone / revoke
  对象被标记不可用，阻止未来读取或行动

supersede / release
  旧版本不再是 current，但作为历史保留

purge
  受管 payload、索引和允许清除的历史被物理清除

restore / repair
  从 revision/snapshot 恢复当前状态并修复派生投影
```

前沿部分应回答：

- 删除/撤销放在 store、retriever、context compiler 还是 Agent loop，语义有什么差异；
- 如何沿 lineage 找到 summary、profile、vector、graph、cache、Skill 和已编译上下文；
- 如何留下 deletion receipt，逐项标记 removed/revoked/retained-by-policy/unknown；
- 如何证明原始来源不会在下一次形成中重新写回来；
- 进程崩溃或索引失败后如何 restore/rebuild。

ForgetEval/Control-Plane Placement 等工作可作为“遗忘操作与放置位置开始被单独评测”的前沿信号；MemTxn 可作为事务/恢复桥接，但不把任何一项写成已经成熟的统一标准。

第四层最终结构：

```text
## 更新、合并与冲突解决
  TencentDB：L1→L2→L3、Skill version
  Codex：Phase 2 文件重写

## 遗忘：现有系统的缺口与前沿补充
  suppression / revoke / supersede / purge / restore
  lineage propagation / deletion receipt / re-generation prevention
```

手动/API 删除和直接数据库操作继续排除；它们不能替代 Agent 自主或自动生命周期机制。

**状态：** 已确认

### Q027 — 除遗忘外，前沿探索还有哪些值得放进第四层的管理机制

**用户问题**

> 看一下前沿探索有什么内容，如果除了遗忘以外在管理上有其他新的机制也可以。

**回答（待用户确认）**

按第四层已经确定的主线（更新、合并与冲突解决）筛选后，前沿材料里真正新增、且不只是存储或检索实现的管理机制主要有两项；另有两项应明确放到其他层：

#### 1. 事务化、来源支持的更新（MemTxn）

这不是再加一个 `update API`，而是改变更新的责任边界：

```text
update proposal + source span / tool receipt + 当前 revision
→ 检查候选是否得到来源支持
→ Temporal Resolver 处理时间/版本冲突
→ commit 或 reject
→ journal/snapshot 记录可恢复的完整状态
```

输出是已提交的 revision/current view 与提交记录，或明确拒绝；中断时可恢复到声明的活跃状态。它补上 TencentDB/Codex 中“模型直接决定如何改写长期状态”与“改写是否完整可恢复”之间的空档。[MemTxn](https://arxiv.org/abs/2607.27834)

#### 2. 依赖感知的修订传播与状态轨迹正确性（GEM/MemState）

它把管理对象从单条记忆提升为一条演化状态：

```text
上游对象 revision 变化
→ 沿 typed dependency / extension 边找出真正派生的对象
→ 只让受影响的摘要、画像、向量、图边、Skill 或缓存失效/重算
→ 检查当前状态与历史轨迹是否仍满足不变量
```

关键区别是把“相关”与“由其派生、必须随之修订”分开。TencentDB 目前靠 L1→L2→L3 的触发器和 Prompt 串联，Codex 主要靠 Phase 2 文件重写；前沿方向把 lineage、失效和重建变成显式管理语义，而不是隐含在某次 Prompt 中。[GEM/MemState](https://arxiv.org/abs/2605.26252)

#### 3. 已发现但暂不并入第四层的机制

- **预算驱动的 Retain/Merge/Abstract/Rewrite 选择**：确实是新的操作选择机制，但核心在压缩和上下文预算。既然当前先不展开压缩，暂放第五层或以后再补。[Retain or Consolidate?](https://arxiv.org/abs/2607.17545)
- **MemCon 的 learned operation policy**：根据任务反馈在 retrieve、re-retrieve、consolidate、forget、no-op 之间选动作。它学习的是“何时调用哪种管理操作”，不是新的 update/merge 语义，因此放第七层反馈学习更清楚。[MemCon](https://arxiv.org/abs/2607.13591)

TTL/衰减、普通容量淘汰、索引重建和双时间载体本身不算新的第四层机制：前两者是通用保留策略，索引重建是实现动作，双时间已在第三层简述；它们只在解释上述更新/恢复或遗忘边界时出现。

#### 建议的第四层前沿结构

```text
现有工程：TencentDB/Codex 的 UPDATE / MERGE / SUPERSEDE / CONFLICT
前沿 A：MemTxn 的 source-supported transaction + temporal resolver + recovery
前沿 B：GEM/MemState 的 dependency-aware propagation + trajectory correctness
缺口补充：forget / revoke / release / purge / restore，以及 lineage 和 deletion receipt
```

**对正文的影响（待确认）**

- 第四层除了“遗忘缺口”，新增 A、B 两个管理机制；
- 压缩操作选择移出本层，MemCon 移到第七层；
- 不把普通 TTL、API 删除或数据库运维写成前沿管理能力。

**状态：** 部分确认（MemTxn 纳入；遗忘的写法见 Q028）

### Q028 — MemTxn 可以写入第四层后，遗忘应如何写

**用户问题**

> 可以写一个 MemTxn，然后遗忘呢？

**回答（待用户确认）**

可以。MemTxn 作为第四层的一个前沿机制，写“更新如何经过来源验证、冲突解析和可恢复提交”。遗忘应紧接着作为另一个独立小节，但必须标成“现有系统缺口与前沿目标”，不能声称 TencentDB 或 Codex 已经具备完整遗忘。

遗忘首先要区分操作语义：

```text
suppression
  只是不再召回，原始对象和历史仍在

revoke / release
  当前对象或授权失效，阻止未来读取/使用，历史可能保留

supersede
  新版本替代旧版本，旧版本仍是可审计历史；这本身不是遗忘

purge
  在政策允许范围内清除来源、当前视图和派生投影

behavioral repair
  已编译上下文、计划、Skill 或行动不再继续依赖被撤销内容
```

一个真正的遗忘流程应写成：

```text
输入：
  forget/revoke 触发
  + 目标对象、来源或范围
  + 隐私/权限/安全/纠错政策

处理：
  找到目标及其 derived_from 后代
  → 选择 suppression、revoke、release 或 purge
  → 使 store、retriever、context compiler、Skill/cache 等派生物失效或清除
  → 阻止下一轮形成从原始来源重新生成
  → 验证下游行为不再使用旧状态

输出：
  每个对象的 removed / revoked / retained-by-policy / unknown 状态
  + deletion/forget receipt
  + 尚未追上的投影和修复任务
```

例如用户要求“忘掉旧的部署凭据”：仅从当前 Markdown 中删掉一行不够；还要检查原始 rollout、摘要、向量、Skill、缓存、已编译 prompt 和未来 Phase 1/Phase 2 是否会重新生成它。若某些历史因审计政策必须保留，应明确标为 `retained-by-policy`，而不是报告“已全部删除”。

ForgetEval/Control-Plane Placement 的价值在于说明：遗忘控制放在 store、写入/铭刻阶段、retriever、context compiler 或 Agent loop，能覆盖的失败类型不同；因此不能只给一个 `delete` API 就宣称遗忘闭环。[Control-Plane Placement](https://arxiv.org/abs/2606.15903)

对 TencentDB/Codex 的结论应保持克制：它们能做局部当前视图移除、来源排除或文件重写，但没有稳定的跨层 lineage、统一撤销传播、行为修复和可核验 deletion receipt。因此第四层写的是“它们做到哪里、前沿缺什么”，而不是把前沿目标倒推成现成功能。

**建议正文结构**

```text
4.x MemTxn：来源支持的更新、版本冲突与可恢复提交
4.y 遗忘：从检索抑制到可验证撤销
    - TencentDB/Codex 的局部边界
    - suppression / revoke / supersede / purge 的区别
    - lineage propagation、再生成阻断、行为修复、receipt
```

**状态：** 已修正（遗忘不等于删除；以 Q029 的三段结构为准）

### Q029 — 第四层应如何排列现有管理、MemTxn 与遗忘

**用户修正**

> 遗忘不是删除，应该作为这两个仓库没有的机制。第四层应该先写这两个仓库的管理方式，写有的就行了，然后是 MemTxn，然后是没有的遗忘机制的前沿探索。

**回答与对齐**

同意，并修正 Q028 的表述。第四层不把“删除动作”当作遗忘定义，而按以下顺序写：

```text
一、现有工程：TencentDB 与 Codex 已有的管理方式
   只写实际存在的 update / merge / supersede / conflict / version rewrite。
   局部 delete、文件清理或来源排除只作为边界事实，不能命名为遗忘。

二、MemTxn：更新管理的前沿增强
   source-supported proposal
   → temporal/version conflict resolution
   → commit/reject
   → recoverable state

三、遗忘：两个仓库都没有的语义机制
   不是“删掉一行或一条记录”，而是让某项信息不再作为
   当前有效状态、派生记忆、上下文依据或后续行动依据，
   同时处理它是否还能从原始来源重新形成。
```

这里要明确区分：

```text
删除：存储层动作，可能只移除某个 row、文件、索引或副本
遗忘：语义状态转变，未来不应再相信、召回、派生或据此行动
```

遗忘机制的前沿探索应回答：如何撤销一个事实/规则的有效性，如何沿派生关系修复摘要、Persona、Skill、向量和缓存，如何阻止下一轮从原始 rollout 重新生成，以及如何验证 Agent 的实际行为已经不再依赖旧状态。原始证据因审计或法律政策保留，并不必然否定语义遗忘；反过来，物理删除了原始记录也不代表摘要或 Skill 中的影响已经遗忘。

因此第四层建议改成：

```text
4.1 TencentDB：L1/L2/L3/Skill 的实际更新、合并、版本和冲突管理
4.2 Codex：Phase 2 对 MEMORY.md / summary / skills 的生成式更新与合并
4.3 MemTxn：来源支持、时间版本解析、事务提交和恢复
4.4 遗忘前沿：语义撤销、派生修复、再生成阻断、行为级验证
```

**状态：** 已确认

### Q030 — 第四层之后的下一层是什么

**用户问题**

> 行继续下一层是什么？

**回答（待用户确认）**

第四层之后是第五层：**检索与上下文构建（Retrieval & Context Construction）**。

它不负责改变 Memory 状态，也不负责首次写入；它回答的是：当前任务到来时，从已经存在的 Memory 中找什么、过滤什么、以什么形式交给 Agent。

```text
输入：
  当前 user task / query
  + 当前 Memory 状态与索引
  + scope、时间、权限、冲突状态和 token budget

处理：
  候选召回（关键词 / 向量 / 图 / 文件工具等）
  → 去重、按当前性与适用范围过滤
  → 重排与冲突标注
  → 编译成 Agent 可读的上下文

输出：
  带来源、revision、适用范围和截断信息的 context package
  → 注入下一轮 Agent prompt 或决定继续检索/回到原始来源
```

这一层与第四层的边界是：第四层决定“状态怎样更新或失效”，第五层只读取当下已经确定的 active/current 状态并组织证据；不在本层展开遗忘。

后续应先分别说明 TencentDB 和 Codex 的实际召回路径，再补充前沿的多路检索、主动再检索和上下文编译；不先讨论存储载体或管理操作。

**状态：** 已修正（遗忘不作为第五层主题；详见 Q031）

### Q031 — 第五层作为重点时，TencentDB 有哪些检索与上下文构建机制，遗忘是否属于本层

**用户问题**

> 第五层作为重点，看一下 TencentDB 有哪些内容，另外第五层跟遗忘有什么关系？这不是第四层的吗，为什么要提这个？

**回答（待用户确认）**

用户判断正确：遗忘属于第四层的管理机制，第五层不应把它再列成一个主题。第五层最多只接受第四层已经确定的 active/current 状态；如果被遗忘的信息仍出现在候选、索引或上下文中，那是第四层的语义传播/修复失败在第五层暴露出来，不是第五层的遗忘机制。

TencentDB 的第五层不是一个统一检索器，而是一套“会话装配 + 分资产读取 + 渐进式上下文构建”路径。当前固定仓库至少包含以下内容：

#### A. Session 初始化：先决定“能看见什么”

```text
输入：
  team / user / agent / task 身份
  + fixed-asset 绑定、ACL、资产状态、能力开关
  + agent/task 描述

处理：
  过滤不可见或未就绪资产
  → 为 Memory、Skill、Wiki、CodeGraph 分别运行 Injector
  → 对 session-stable 结果做 session_init prewarm/cache

输出：
  本 Session 可使用的资产目录、长期画像、场景索引和只读工具说明
```

这一步是访问前置和装配，不是把所有内容全文塞进 Prompt。仓库没有一个统一的 `LoadoutEntity` 或全局跨资产排名器。

#### B. Chat Memory：L3 直注，L2 导航，L1/L0 按需读取

```text
L3 Persona
  core/read → 完整 persona.md → 直接放入 system prompt

L2 Scene
  scenario/ls → path + summary + heat 的导航索引
  → Agent 判断相关后调用 scenario/read 取某个 Markdown 全文

L1 Atomic Memory
  atomic/search → 以当前问题为 query 的关键词/向量 hybrid 检索
  → 返回按相关度排序的原子记忆片段

L0 Conversation
  conversation/search → 从原始对话中找具体消息、时间线和上下文
  conversation/query → 按 session 顺序读取历史
```

L1/L0 的搜索输入通常是清洗后的当前用户问题，加上 team/user/agent/session/task 隔离；输出是带 type、content、score、时间或来源信息的候选。SQLite 路径并行跑 FTS5/BM25 和 embedding，再用 RRF 合并；TCVDB 路径可由后端一次完成 dense+sparse hybrid。检索结果还受 limit、score threshold 和上下文字符预算限制。

这里存在两种适配路径，正文不能混成一个“默认行为”：

- **当前 MemoryProxy 生产注入路径：** L3 与 L2 索引在 session_init 注入；L0/L1 不再逐轮自动注入，而是通过 `<tdai_memory_tools>` 让 Agent 用 Bash/curl 按需调用。这样保持 system prompt 稳定并利用 prompt/KV cache。
- **MemoryCore/OpenClaw 插件路径：** `before_prompt_build` 可并行执行 L1 search、L3 read、L2 list，把 L1 放在当前 user prompt 前，把 L3 与场景导航放入稳定 system context；`maxResults`、strategy、threshold 等由配置控制。

#### C. Skill：代码预筛，Agent 再取全文

```text
输入：agent description + agent prompt + task description + task goal
→ Session 初始化生成 listing query（弱信号时退回列表 head）
→ owner-agent 可见 Skill 的 BM25/RAG listing
→ 注入 available_skills（名称/描述/版本等摘要）
→ 当前任务命中后 skill_view 读取 SKILL.md
→ 需要资源时 skill_files_read；自带目录不足时 skill_search 团队库
```

因此 Skill 不是在每轮把所有正文注入，而是“目录导航 → 选中 → 读取正文/资源”。

#### D. Wiki 与 CodeGraph：工具自发现后按意图查询

Session 只注入已绑定资源的名称、摘要、ID、服务地址和 `tools/list → tools/call` 使用说明。

- Wiki：`search`（默认 BM25/关键词）→ `read_page`；需要目录或关系时再用 `list_pages`、`get_graph`。
- CodeGraph：按意图选择 `explore`、`search`、`node`、`callers`、`callees`、`impact`；它返回符号、调用和影响范围，不等同于全文检索。

#### E. 上下文构建的共同输出

TencentDB 最终交给 Agent 的不是单一“top-K 文本”，而是可以组合的 context package：

```text
稳定部分：L3 全文、L2 导航、Skill/Memory/Knowledge 工具说明
动态部分：本轮 L1/L0 片段、Agent 选中的 L2/Skill/Wiki/CodeGraph 正文
```

例如“按上次约定修复 refresh token 撤销问题，并说明设计原因和影响”可以同时读取：Chat Memory 的历史约定、Skill 的修复流程、Wiki 的设计背景和 CodeGraph 的影响关系。最终由主 Agent 根据意图组合这些结果；仓库没有独立的跨资产分类器替它做唯一选择。

**第五层正文应保留的重点**

1. 输入是当前任务/query、身份与范围、已有索引和预算；
2. 输出分为直接注入的全文/导航、按需工具结果和最终 context package；
3. TencentDB 的核心特色是 progressive disclosure：L3 直接生效，L2 先索引后读全文，L1/L0 和 Skill/Knowledge 按需查；
4. hybrid 检索、工具调用、session cache、字符预算和多资产组合要详细写；
5. 遗忘不在本层展开，只保留一句边界：本层只能读取第四层已经确定的 active/current 状态。

**对正文的影响（待确认）**

- 第五层以 TencentDB 的多路径装配和渐进式披露为重点；
- 说明 MemoryProxy 与 OpenClaw/MemoryCore 两条适配路径的差异，避免把可选 auto-recall 写成统一默认；
- 删除第五层原先关于“检索抑制/遗忘”的展开，遗忘全部回到第四层。

**状态：** 部分确认（遗忘相关内容由 Q032 再次收窄）

### Q032 — 第五层正文是否应该提遗忘

**用户修正**

> 遗忘跟第五层就没有关系，不应该在第五层说。

**回答与确认**

同意。第五层正文完全不讨论遗忘，也不需要用“检索抑制”“失效边界”或“遗忘失败暴露”等说法做旁注。第五层只描述：

```text
当前任务/query
→ 资产与索引读取
→ 候选检索、按需读取和路由
→ 上下文装配
→ 注入 Agent prompt 或返回工具结果
```

遗忘及其前沿机制只保留在第四层；第五层后续不再引用它。

**对正文的影响**

- 从 `05-retrieval-context.md` 删除所有遗忘、撤销、抑制和失效传播内容；
- 不在第五层设置与第四层的遗忘边界小节；
- 第五层重点收敛为 TencentDB 的检索路径、渐进式披露、工具读取、缓存和上下文编译。

**状态：** 已确认

### Q033 — 第五层的真正重点是什么

**用户判断**

> 第五层的关键点在于检索方式以及上下文如何编排。

**回答与确认**

同意。第五层只围绕两个轴展开：

```text
一、检索方式（怎么找到信息）
  自动召回还是 Agent 主动调用工具
  关键词/BM25、向量、hybrid、RRF
  直接读全文还是先读索引再按需展开
  单一资产检索还是按任务意图组合 Memory、Skill、Wiki、CodeGraph
  如何使用 scope、session、agent、时间和查询预算

二、上下文编排（找到后怎么交给 Agent）
  哪些内容直接放 system prompt
  哪些内容只放 path/summary 导航
  哪些内容作为本轮动态片段或工具结果返回
  稳定区与动态区如何排列、缓存和更新
  多个资产如何去重、排序、分段并控制 token/字符预算
```

每个机制都应写清：

```text
检索输入 → 检索处理 → 候选输出
候选输出 → 编排处理 → 最终 context package
```

因此 TencentDB 第五层的重点材料应是 L1/L0 的检索算法与工具路径、L2 的索引→正文渐进式读取、L3 的直接注入，以及 Skill/Knowledge 的任务意图路由和稳定/动态上下文编排；不再扩展管理、写入或其他层的主题。

**状态：** 已确认

### Q034 — Codex 的第五层检索方式与上下文编排

**用户问题**

> 然后 codex 呢？

**回答（待用户确认）**

Codex 第五层同样拆成“怎么检索”和“怎么编排”，但它不是 TencentDB 那种多后端检索器，而是**文件化 Memory 上的词法渐进读取**。

#### 一、Codex 怎么检索

```text
输入：
  新 Thread 的当前 user message
  + cwd / 项目线索
  + 常驻 memory_summary.md
  + Memory root 中可读的 Markdown 工件

处理：
  先看 memory_summary.md 的导航
  → 用关键词在 MEMORY.md 中 search
  → read 命中的行窗口
  → 需要更具体步骤时打开 rollout_summaries/ 或 skills/
  → 需要原始证据时沿 rollout_path 打开 rollout JSONL

输出：
  进入当前推理的相关文件片段
  + 文件路径/行号和 rollout provenance
```

Codex 的 `LocalMemoriesBackend` 是递归文本 substring search：支持任意词/全部词、行窗口、大小写/规范化选项、上下文和分页，按路径与行号返回。固定实现没有 embedding、向量库、ANN 或 learned reranker；搜索质量主要取决于 Phase 2 保留的标题、关键词、项目名和错误文本。Stage 1 的 `memories_1.sqlite` 主要是写入/巩固输入，通常不直接作为新 Thread 的读取索引。

读取工具有两种接入形态：启用 dedicated Memory tools 时使用 `list/read/search`；否则主 Agent 按只读指令使用普通文件搜索和读取 helper root。两者都是同一套文件渐进读取，不是两套语义检索系统。

#### 二、Codex 怎么编排上下文

Codex 的上下文不是一次性拼完整本 Memory，而是固定入口加按需展开：

```text
常驻层：
  memory_summary.md（固定快照约 2500 tokens）

第一层展开：
  MEMORY.md 中命中的手册段落

第二层展开：
  rollout summary / SKILL.md / supporting files

证据展开：
  原始 rollout JSONL（只有需要精确过程、错误文本或来源核对时才打开）
```

例如新 Thread 收到：

```text
cwd: /repo/auth-service
user: 按我们之前验证过的方式修改 refresh token 撤销逻辑
```

上下文编排是：

```text
memory_summary：auth-service / token revocation / shared store
→ search MEMORY.md：命中对应任务段
→ read 行范围：得到共享 store 规则和回归命令
→ 必要时 read rollout_summaries：确认历史测试证据
→ 将选中的片段与当前 Thread 对话、工具结果一起用于回答
```

因此 Codex 的编排特点是：

- `memory_summary.md` 是唯一常驻的长期 Memory 入口；
- `MEMORY.md`、Skill 和 rollout summary 都是按需展开，不会整本自动注入；
- 原始 rollout 是最深层来源，不是默认上下文；
- 读取结果以文件片段进入当前推理，而不是先生成一个独立的全局 context package；
- citation 的文件行和 rollout ID 随回答输出，作为这次采用了哪些片段的 provenance。

#### 三、与 TencentDB 的核心差异

```text
TencentDB：
  多种索引/工具路线 + Injector 编排
  L3 直注、L2 导航、L1/L0 搜索、Skill/Knowledge 分资产路由

Codex：
  memory_summary 导航 + MEMORY.md 词法搜索
  → 行范围读取 → rollout summary/Skill → 原始 rollout
  主要由 Agent 按 Prompt 自己决定搜索词和展开深度
```

所以 Codex 第五层最值得写的不是“用了什么向量数据库”，而是：**短索引常驻、文件词法检索、按指针逐层展开，以及把选中的片段和当前 Thread 上下文合并**。这也是它与 TencentDB 在检索方式和上下文编排上的根本差异。

**对正文的影响（待确认）**

- `05-retrieval-context.md` 中 Codex 重点写 `summary → MEMORY.md → rollout summary/skill → raw rollout`；
- 明确 Codex 没有 hybrid/vector/reranker 检索，主要依赖 lexical search 与 Agent 自主展开；
- 把当前 Thread 的对话/工具事件与跨 Thread Memory 读取分开描述；
- 重点写“常驻短索引 + 按需文件片段”的上下文编排，不写其他层主题。

**状态：** 部分确认（工具+文档渐进披露上升为共同主线，检索算法下沉为实现细节）

### Q035 — Agent Memory 的检索主流是否是工具加 Markdown 渐进式披露

**用户判断**

> 其实本质不都是以工具+md渐进式披露为主嘛，Agent memory的检索现在主流都是工具和md文档而不是向量检索了吧。

**回答与对齐**

这个判断需要分成两个层次：

```text
Agent-facing 交互层：
  工具（search/list/read）
  + Markdown/文档化结果
  + progressive disclosure
  是当前 coding-agent 和本地文件型 Memory 的共同形态。

Backend 检索层：
  BM25、向量、hybrid、图和 reranker
  仍可能藏在工具后面，负责候选生成或排序。
```

因此“工具 + Markdown”和“向量检索”不是互斥选项：

```text
Agent
  → 调用 search/read 工具
  → 工具内部使用词法、向量或 hybrid 找候选
  → 返回 Markdown/结构化片段
  → Agent 按需继续读取并编排上下文
```

Codex 是“工具/文件渐进读取 + 词法搜索”的例子；TencentDB 是“工具/Markdown 渐进披露 + 某些 L1 后端 hybrid 检索”的例子。Claude Code 的官方 Memory 文档也采用常驻 Markdown 入口、主题文件按需读取的形态。[Claude Code memory](https://code.claude.com/docs/en/memory) [Codex read path](https://github.com/openai/codex/blob/main/codex-rs/ext/memories/templates/memories/read_path.md)

但不能据此说整个 Agent Memory 后端已经放弃向量检索：Mem0 的官方说明仍把 semantic/vector、keyword、entity 和 temporal 信号融合进 search；近期 MemX 也明确采用 vector + keyword + RRF。另一方面，True Memory 这类近期工作又刻意采用不依赖外部 vector/graph index 的多阶段检索。更准确的结论是：**工具化渐进披露是面向 Agent 的主流接口形态，后端检索算法并未收敛到单一答案。** [Mem0 retrieval](https://github.com/mem0ai/mem0/blob/main/docs/core-concepts/how-it-works.mdx) [MemX](https://arxiv.org/abs/2603.16171) [True Memory](https://arxiv.org/abs/2605.04897)

**对第五层正文的影响**

第五层总纲应先写共同协议，而不是先按 BM25/向量分类：

```text
工具化读取
→ 文档/Markdown 结果
→ 渐进式展开
→ 上下文编排
```

然后在各实现下补一句后端差异：TencentDB 的 L1/Wiki 某些路径使用 BM25、向量或 hybrid；Codex 当前主要是文件词法搜索。这样既能体现二者的本质共同点，也不会错误地把向量检索说成已经过时或不存在。

**状态：** 部分确认（以 Q036 的“直接注入 / 工具检索”拆分为准）

### Q036 — 第五层还包括直接注入；工具检索和向量检索应怎样区分

**用户修正**

> 你这个又不对，那还有直接不通过工具直接放上下文里面的呢，比如 system prompt。我是说通过工具检索 Memory 的比较多，而且像 Claude Code/Codex 这种都不再用向量检索，而是 LLM 自主工具搜索这样。

**回答与对齐**

同意。第五层首先要区分“内容如何进入上下文”，不能把所有路径都叫工具检索：

```text
A. 直接注入 / 预装配
   系统在 Session/Thread 初始化时把选定内容直接放进 system prompt
   例：TencentDB L3 全文、L2 导航；Codex memory_summary；Claude Code 的 Markdown 记忆文件

B. Agent 自主工具检索
   LLM 根据当前任务决定搜索词、调用 search/list/read，
   再按结果继续展开文档
   例：Codex 的 MEMORY.md → rollout summary → raw rollout；
        Claude Code 的 Markdown 文件和标准文件工具

C. 系统自动召回
   宿主或插件根据当前 query 自动调用后端搜索，再把结果注入上下文
   例：TencentDB 某些自动 recall / OpenClaw 适配路径
```

其中 A 是上下文装配，不是检索；B 才是用户所说的“LLM 自主工具搜索”。对 Claude Code/Codex 这类 coding-agent/file-memory 路径，公开实现主要是 LLM 驱动的文件/词法搜索和按需读取，并没有把向量检索作为 Agent 面向的默认读取接口。向量或 BM25 若存在，应作为 C 或工具内部实现说明，不能作为第五层的第一分类。

因此第五层应先写：

```text
内容进入上下文的路径：直接注入 / Agent 工具检索 / 系统自动召回
→ 每条路径的输入、决策者、返回形态和上下文位置
→ 稳定内容、动态结果和按需展开如何组合
```

TencentDB 与 Codex 的共同点应表述为“文档化 Memory + 渐进披露”，但具体差异是：TencentDB 同时存在直接注入、工具检索和部分自动召回；Codex 的长期细节主要由 Agent 通过文件工具自主搜索，`memory_summary.md` 则是直接注入的常驻入口。

**对正文的影响**

- 第五层先按“直接注入 / Agent 自主工具检索 / 系统自动召回”分路径；
- 不把“工具 + Markdown”说成唯一进入上下文的方式；
- 不把向量检索与工具检索写成互斥的架构路线；
- 对 Claude Code/Codex，重点写 LLM 自主文件搜索，而不是虚构一个向量召回层。

**状态：** 已修正（第五层总纲以 Q037 的“Memory 类型 → 进入方式 → 检索方式”为准）

### Q037 — 第五层总纲应如何定义

**用户修正**

> 不对，第五层的总纲就是各种 memory 怎么进入上下文，如果是检索的是什么检索方式。

**回答与确认**

同意。第五层的总纲不是“工具、自动召回、向量”等并列分类，而是对每一种 Memory 统一回答：

```text
Memory 类型
  → 如何进入上下文？
       直接注入，还是先检索？
  → 如果先检索，用什么检索方式？
       Agent 工具驱动的文件/词法搜索，
       系统自动的 BM25/向量/hybrid，
       还是索引导航后按路径读取？
  → 最终以什么上下文形态出现？
       全文、摘要、索引、片段或工具结果？
```

因此第五层应先建立统一表格，再分别填 TencentDB 与 Codex：

| Memory 类型 | 进入上下文方式 | 若需检索，检索方式 | 最终形态 |
|---|---|---|---|
| L3 / `memory_summary` / Persona | 直接注入 | 无 | system 中的稳定全文/短索引 |
| L2 Scene / `MEMORY.md` | 索引或摘要先进入，再按需读取 | path/关键词/文件读取 | 导航 + 局部正文 |
| L1 / `MEMORY.md` 任务段 | 工具检索 | Codex 词法搜索；TencentDB 可为 BM25/向量/hybrid | 相关片段 |
| L0 / 原始 rollout 或 conversation | 工具检索 | 关键词、时间/session 查询或文件读取 | 原始消息/证据片段 |
| Skill | 目录可直接注入，正文按需读取 | 名称/描述搜索、`view`、文件读取 | Skill 摘要 + `SKILL.md` |
| Wiki / CodeGraph | 资源与工具入口可注入，正文/关系按需查询 | BM25、`search`、`explore`、关系查询等 | 页面、符号和关系结果 |

这个表格之后，再写上下文编排：直接注入的内容放在哪里，索引和正文怎样衔接，工具结果怎样与当前对话合并，以及如何控制顺序和预算。

**TencentDB 填法示例**

```text
L3：直接注入 persona.md
L2：直接注入 scene index；按 path 调工具读正文
L1：调用 atomic/search；后端可用 BM25/向量/hybrid
L0：调用 conversation/search 或 query；按消息/时间/session 查
Skill：available_skills 目录注入；skill_view/files_read 取正文和资源
Wiki/CodeGraph：资源与 tools 入口注入；调用 search/explore 等工具取内容
```

**Codex 填法示例**

```text
memory_summary.md：直接注入新 Thread
MEMORY.md：Agent 用 search/grep 后按行 read
skills/rollout_summaries：沿 MEMORY.md 指针按需 read
原始 rollout：需要精确证据时沿 rollout_path 搜索/读取
```

所以“工具 + Markdown”是许多路径的共同实现形态，但它只是某些 Memory 的进入方式；直接注入的 Memory 不经过工具，也不应被硬套成检索。向量/BM25 只有在对应 Memory 采用检索时，才作为该路径的检索方式填写。

**对正文的影响**

- `05-retrieval-context.md` 先用“Memory 类型 → 进入上下文方式 → 检索方式 → 输出形态”做总表；
- 直接注入、索引导航、Agent 工具检索和系统检索不再作为互斥的顶层架构；
- TencentDB/Codex 只需在同一张表中填各自实际路径，再展开上下文编排。

**状态：** 已确认

### Q038 — 第五层前沿探索还有哪些新机制

**用户问题**

> 这一块前沿技术有什么新内容吗？

**回答（待用户确认）**

有，但真正的新意不在于再列一种向量数据库，而在于“如何选择进入路径、如何逐层展开、如何判断哪些证据值得进入上下文”。目前值得放入第五层的前沿主要有三类：

#### 1. 意图驱动的检索路由与分层预算

```text
输入：
  当前 query
  + 当前 session/task
  + 可用 Memory 类型
  + candidate/context/tool budget

处理：
  识别 query 意图和所需证据类型
  → 选择 direct lookup、targeted retrieval 或 deep/multi-hop route
  → 为不同 route 分配不同 token 和调用预算
  → 首轮证据不足时改写 query、升级检索层级或重试

输出：
  可执行的 retrieval plan
  + 分层候选和最终 context
  + 是否继续检索/停止的理由
```

MemFlow 用 Router Agent 将查询分到 Profile Lookup、Targeted Retrieval、Deep Reasoning 三档，并让 Validator 在证据不足时升级检索层；OpenViking 也区分简单 `find` 与带 session context、intent analysis 和 query expansion 的 `search`。[MemFlow](https://arxiv.org/abs/2605.03312) [OpenViking retrieval](https://docs.openviking.ai/en/api/06-retrieval)

这比 Codex 当前“Agent 自己决定关键词和读取深度”更显式，也比 TencentDB 当前分散在各个工具提示里的路由规则更系统。重点不是替 Agent 禁止自主搜索，而是把“选择哪一种 Memory、查几层、何时停止”变成可观察的计划。

#### 2. 层级/目录式检索与渐进上下文返回

```text
输入：query + context root/URI
→ 先定位目录或摘要层
→ 在高相关目录内递归细查
→ rerank 后按预算返回 abstract / overview / full detail
→ 保留 URI、展开路径和检索轨迹
```

OpenViking 把 Memory、Resource、Skill 放进统一的虚拟文件系统，以目录递归检索取代一次性 flat top-k，并将 L0 摘要、L1 概览、L2 原文作为不同返回层级；结果还带可追踪的 retrieval trajectory。[OpenViking FAQ](https://docs.openviking.ai/en/faq/faq)

它与 TencentDB 的“L2 索引→读取场景”、Codex 的“summary→手册→rollout”方向相同，但前沿实现把目录、URI、层级选择、预算和轨迹统一成一个检索协议，而不是分散在不同 Injector 或 Prompt 中。

#### 3. 证据/行动感知的上下文编排

传统检索按“与 query 相似”排序；新的方向问的是：**哪一段证据会改变 Agent 下一步判断或工具行动？**

```text
输入：候选片段
  + 当前任务/可能行动
  + source、revision、风险和 token budget

处理：
  评估 evidence 的 necessity、action impact、outcome uplift、
  negative-transfer risk
  → 组成带类型和来源的 evidence cards
  → 在预算内选择最小充分上下文

输出：
  action-oriented context package
  + 每个片段的来源、选择理由和未纳入信息
```

CICL（Decision-Aware Memory Cards）把候选上下文按行动影响、必要性和负迁移风险评分，再组装成有类型的 Memory Card；它仍是早期研究，结果主要是文件级检索和受控实验，不能写成已经成熟的通用编译器。[CICL](https://arxiv.org/abs/2606.08151)

#### 应明确放在边界、不要作为第五层主线的内容

- MemCon 的长期 learned operation policy 主要属于第七层；第五层最多借用它的 `retrieve/re-retrieve` 例子。
- 纯向量、BM25、RRF、普通 reranker 是检索实现基线，不是新的架构主线。
- 版本解析、冲突解决属于第四层；这里只消费其结果。
- 纯压缩算法暂不展开；只有当它作为“证据选择/上下文编排”时才简述。

**建议第五层前沿结构**

```text
现有共同形态：
  直接注入 / Agent 工具检索 / 文档渐进披露

前沿 A：
  意图驱动的 Memory 路由与分层预算

前沿 B：
  统一目录/URI 的层级检索、按需 hydration 和可观测轨迹

前沿 C：
  证据/行动感知的上下文编排
```

**状态：** 已确认（三项前沿内容纳入第五层，正文最后统一改写）

### Q039 — 前沿内容先记问答，正文何时修改

**用户要求**

> 你先只改问答文档，这些正文最后统一改。

**回答与确认**

后续继续采用“先问答对齐、最后统一改正文”的顺序：当前只把已确认的结论和写作约束追加到本问答记录，不修改 `01-input.md` 至 `07-feedback-learning.md`、HTML 或其他正文。等七层的层级边界、共同结构和各层重点全部确认后，再一次性重写正文，避免同一概念在不同轮次反复搬动。

本轮已确认的第五层前沿候选为：

```text
A. 意图驱动的 Memory 路由与分层预算
B. 统一目录/URI 的层级检索、按需 hydration 和可观测轨迹
C. 证据/行动感知的上下文编排
```

三项都必须按 `输入 → 处理 → 输出 → 例子` 展开；向量、BM25、RRF 只作为具体检索路径的实现细节，不单独升级为第五层主线。

**状态：** 已确认

### Q040 — 第五层之后的第六层是什么

**用户问题**

> 接下来是第六层。

**回答（待用户确认）**

第六层是：**使用、行动与技能（Use / Action / Skill Execution）**。

第五层解决“哪些 Memory 进入当前上下文、以什么形式进入”；第六层解决“Agent 是否正确使用这些内容，并据此做出什么判断或行动”。

```text
输入：
  当前任务
  + 第五层编排出的 context package
  + 当前环境、工具、权限和约束
  + 可读取的 Skill / workflow

处理：
  判断 Memory/Skill 是否适用于当前条件
  → 形成计划、选择工具和参数
  → 检查前置条件与行动授权
  → 执行工具或生成回复
  → 根据执行结果决定继续、修正或停止

输出：
  assistant response
  / tool call 与参数
  / 文件或环境变化
  / 当前任务的成功、失败或未完成结果
```

这一层的关键不是“Memory 被读到了”，而是它是否改变了实际行为。例如 Memory 提示“修复 refund fixture 前先确认字段迁移”，第六层要检查当前仓库和测试，再决定是否执行迁移、运行哪组测试；不能因为读到一条历史经验就直接执行。

TencentDB 中，Skill 目录和 `SKILL.md` 在第五层被发现/读取后，第六层才把其中的步骤、分支和验证方法用于当前任务；L1/L2/L3 记忆通常只是约束、背景或决策依据。Codex 中，Memory 片段同样只影响 Agent 的计划和工具选择，sandbox、approval、当前工作区和工具本身仍是行动边界。两者都没有“读到 Memory 就自动执行”的通用隐式授权。

第六层与相邻层的边界：

```text
第五层：检索/读取并编排上下文
第六层：理解适用条件，选择并执行行动/Skill
第七层：观察结果、用户纠正和成本，形成反馈与经验更新
```

Skill 在本层是“被消费的可执行能力”；Skill 如何从轨迹中形成、晋升和持续改进，留在第二层的形成链和第七层的反馈学习中，不在本层重复。

**状态：** 待确认

### Q041 — 第六层“使用、行动与技能”是否有必要独立存在

**用户问题**

> 这一层有必要存在吗？

**回答（待用户确认）**

如果把文档严格限定为 **Agent Memory 机制**，第六层没有必要作为一个完整、重点的独立层存在。

原因是 TencentDB 和 Codex 都没有一个独立的“Memory Action Engine”：

```text
第五层：把 Memory/Skill 读进当前上下文
        ↓
普通 Agent runtime：自行判断、调用工具、执行任务
        ↓
第七层：记录结果、纠正和使用反馈
```

在两个仓库中，Memory 本身不会因为被读取就自动执行；sandbox、approval、当前工作区、工具权限和 Agent 的普通推理循环才决定是否行动。Skill 也主要是被读取的操作手册或 workflow，Skill 的形成属于写入/反馈，Skill 的读取属于第五层，真正执行仍是宿主 Agent 的正常工具调用。因此把“使用、行动与技能”写成一个完整 Memory 层，容易重复第五层，也会把普通 Agent runtime 误写成 Memory 子系统。

但“Memory 是否真正改变了行动”仍然是一个有价值的**边界/验证点**：

```text
context package
→ Agent decision / tool selection / parameters
→ tool result / task outcome
```

它可以用来回答：Memory 是否只被读到却没有被采用？是否被错误地套用到当前环境？是否改变了工具参数？结果是否应该进入第七层反馈？

**建议**

```text
第六层不作为重点机制层；
保留一个很短的“使用与行动边界”说明，作为第五层到第七层的桥：

第五层输出 context
→ Agent runtime 使用/行动
→ 结果与使用证据进入第七层反馈
```

如果必须保持七层编号，第六层可以保留为薄层，标题改成“Memory 使用与行动验证”，只写输入、行动结果和验证指标，不再展开 Skill 形成、执行框架或权限系统。若允许重新压缩七层，则它也可以并入第五层末尾和第七层开头。

**对正文的影响（待确认）**

- 不为第六层编写与 TencentDB/Codex 不相称的独立机制综述；
- Skill 形成留在第二/第七层，Skill 读取留在第五层；
- 第六层只保留 context → decision/tool call → outcome 的薄边界；
- 重点篇幅继续放在第五层检索/编排和第七层反馈/经验学习。

**状态：** 待确认

### Q042 — 完全去掉第六层会不会遗漏 TencentDB/Codex 的内容

**用户问题**

> 如果完全去掉第六层，TencentDB 和 Codex 会少讲什么内容吗？

**回答（待用户确认）**

如果目标是调研 **Agent Memory 机制本身**，完全去掉第六层不会丢失 TencentDB 或 Codex 的核心实现。第六层目前包含的内容可以重新归位：

| 原第六层内容 | 去掉后归位 | 是否会丢失核心机制 |
|---|---|---|
| L1/L2/L3/Skill 如何被读取 | 第五层检索与上下文编排 | 不会；本来就是第五层内容 |
| Skill 如何形成/晋升/版本化 | 第二层形成、第四层管理、第七层反馈 | 不会；不属于 Skill 执行层 |
| Memory 如何影响 Agent 的计划和工具选择 | 第五层结尾的一句结果说明，或第七层反馈输入 | 不会；两个仓库没有独立 Action Engine |
| sandbox、approval、当前工作区和工具权限 | Agent runtime / 横切约束 | 不属于 Memory 机制 |
| Mem2ActBench 等行动 grounding 评估 | 第七层反馈/评估 | 不会；它是效果评估，不是存储或检索实现 |

真正会少掉的只有一个**显式桥接视角**：

```text
Memory context
→ Agent 是否采用
→ 工具选择/参数
→ 任务结果
```

这条链对评估 Memory 是否真的有用很重要，但它不是 TencentDB 或 Codex 中独立存在的一层机制。可以把它作为第五层的输出说明和第七层的反馈输入保留，不必单独占一章。

因此建议：

```text
删除第六层独立章节；
第五层末尾保留“context 被 Agent 使用”的一句话；
第七层开头承接 action/tool outcome 与 citation/usage 反馈；
```

如果最终仍要保留“七层”这个编号，应说明第六层是一个薄的跨层桥，而不是完整 Memory 层；如果允许压缩层数，则可直接把当前第七层改为第六层。

**状态：** 已确认（第六层删除；原第七层顺延为新的第六层）

### Q043 — 删除第六层

**用户决定**

> 直接删掉第六层。

**回答与确认**

确认删除第六层，不再保留“使用、行动与技能”作为独立层。最终统一重写正文时：

```text
原第 1～5 层：保持当前已确认的职责
原第 6 层：删除
原第 7 层“反馈、经验与持续学习”：顺延为新的第 6 层
```

相关内容的归位约束保持不变：Skill 的形成/管理/反馈分别留在对应层；Skill 和 Memory 的读取留在第五层；Agent 行动只作为第五层输出到新第六层反馈之间的结果证据，不另设行动层。

在所有层级问答完成前，不删除 `06-use-action-skills.md` 文件，也不提前重编号其他正文；最终统一改写时一并处理目录、链接、总览和 HTML 引用。

**状态：** 已确认

### Q044 — 反馈、经验与持续学习层应如何重点展开

**用户问题**

> 行，看一下反馈、经验与持续学习，这是最重要的一层。

**回答（待用户确认）**

同意。删除原第六层后，原第七层顺延为新的第六层，而且它确实应是重点：前面各层只是让 Memory 被形成、保存和读出；这一层决定系统能否根据使用结果判断什么值得保留、什么经验能够迁移，以及下一轮系统是否真的变好。

第六层的核心闭环是：

```text
任务执行轨迹 + Memory/Skill 使用记录
  + 工具/测试结果 + 用户纠正 + 成本/环境信息
→ 归因与效果判断
→ 经验提炼、Skill 晋升或既有内容修订
→ 更新未来的 Memory、Skill、检索/操作策略
→ 下一次任务继续产生结果
```

#### 一、反馈输入不能只记录“被读过”

```text
曝光：进入了可见目录或上下文
读取：Agent 实际调用了 search/read/view
采用：内容出现在计划、回答或工具参数中
结果：测试/工具/任务成功、失败、返工或用户纠正
条件：cwd、版本、工具配置、权限、成本和延迟
```

`usage_count` 或一次 citation 只能证明“可能被使用”，不能证明内容正确或让任务变好。第六层要把使用和后果分开，才能避免“越容易被找到的内容越容易被继续保留”的自我强化。

#### 二、TencentDB 已有的反馈/经验闭环

```text
输入：
  完整 user/assistant/tool_call/tool_result 任务轨迹
  + 当前已有 Skill 提示与正文
  + 可选的资产反思文本

处理：
  Review Agent 判断是否存在可复用能力
  → 分类、评分、查重
  → create / update / patch / no-op
  → 生成新的 Skill 版本并回到后续 Session

输出：
  SKILL.md / supporting files / version head
  或明确不生成
```

这条链已经能把真实执行轨迹沉淀成 Skill，并要求 Review Agent 先查看已有 Skill；但仓库没有闭合的自动效果反馈：Asset Reflection 默认关闭，开启时的文字目前也不会自动解析、评分或调整资产排序；系统没有稳定记录“哪项资产被采用后是否提高了最终任务质量”。因此 TencentDB 当前更准确的定位是“自动经验沉淀与版本化复用”，不是完整的 outcome-learning 系统。

#### 三、Codex 已有的反馈闭环

```text
输入：
  最终回答中的 Memory citation
  + citation 指向的文件行和 rollout IDs

处理：
  citation parser 校验 ID
  → Stage 1 candidate 的 usage_count + 1
  → 刷新 last_usage
  → Phase 2 selection 更优先考虑该候选

输出：
  候选使用信号
  → 下一轮 MEMORY.md / summary / skills 的巩固输入
```

Codex 的工具结果、测试结局和用户纠正仍保存在 rollout 或后续 note 中，但固定实现没有把它们与某条 Memory 的最终任务质量做统一归因。它闭合了“引用 → 使用信号 → 后续巩固”，没有闭合“使用 → 结果 → 可信度/效用更新”。

#### 四、前沿机制一：经验/Skill 的验证式晋升

一次成功轨迹不等于可迁移技能。前沿路线把晋升拆成：

```text
同一任务的多条轨迹/不同路径
→ 跨轨迹比较成功、失败和分支条件
→ 提炼 workflow 与 tactical experience
→ 由 verifier/replay 检查前置条件、反例和版本
→ 晋升为可复用 Skill / Experience
→ 新任务使用后继续回写结果
```

[XSkill](https://xskill-agent.github.io/xskill_page/) 的 Phase I 使用 multi-path trajectories、cross-rollout critique 和 hierarchical consolidation，同时维护结构化 Skill Library 与 Experience Bank；它正好属于“执行反馈如何变成可复用经验”，而不是普通首次写入。[EvoSkills](https://arxiv.org/abs/2604.01687) 进一步让 Skill Generator 与 Surrogate Verifier 共同迭代，强调生成后要经过验证循环。

#### 五、前沿机制二：从“使用次数”到效果归因

更完整的反馈要估计某条 Memory/Skill 对结果的贡献，而不是把引用次数当效用：

```text
输入：memory_ref / skill_version
  + 是否被读、是否被采用
  + 当前任务结果与反事实对照
  + token、延迟、错误和返工成本

处理：
  区分曝光、采用和结果
  → 评估成功提升、失败风险和适用范围
  → 形成 utility / confidence / evidence ledger

输出：
  供下一轮检索、巩固、Skill 晋升和人工复核使用的效果信号
```

这也是为什么行动型基准比单纯“搜到了没有”更重要：它要检查 Memory 是否改变了后续工具选择、参数或任务结果。当前 TencentDB/Codex 都只有其中一小段信号，不能声称已经实现因果归因。

#### 六、前沿机制三：学习何时使用哪种 Memory 操作

当反馈被积累后，系统还可以学习操作策略，而不只是学习文本内容：

```text
状态：当前任务 + 已有候选 + 历史结果 + 预算
→ policy 选择 retrieve / re-retrieve / plan injection /
  consolidate / no-op 等操作
→ 执行并记录任务结果与成本
→ 更新 policy
```

[MemCon](https://arxiv.org/abs/2607.13591) 将 Memory 操作建模为在线策略，用任务级反馈学习何时、取什么以及取多少；它是跨后端的控制器研究原型，不等于 TencentDB 或 Codex 已有的自动策略，也不能仅凭作者实验外推长期稳定性。

#### 建议的新第六层结构

```text
6.1 反馈输入：使用、采用、结果、纠正、成本与环境
6.2 TencentDB：轨迹 → Review → Skill 版本，但缺少效果闭环
6.3 Codex：citation → usage → Phase 2 选择，但缺少结果归因
6.4 经验/Skill 验证式晋升（XSkill、EvoSkills）
6.5 效果归因与操作策略学习（MemCon 等）
6.6 持续评测、跨任务迁移与成本反馈
```

**状态：** 部分确认（排除安全主题；以 Q045 的范围为准）

### Q045 — 第六层主要由前沿探索补充，是否纳入安全问题

**用户修正**

> 对，这一层反而是 Codex 和 TencentDB 做得很浅的地方，这一层应该主要用前沿探索补充，但是不要考虑安全相关的问题，这不是要调研的内容。

**回答与确认**

同意。新第六层的现有仓库部分只做短基线对照：

```text
TencentDB：执行轨迹 → Review → Skill 版本
Codex：citation → usage → Phase 2 选择
```

主体改为前沿的反馈/经验/持续学习机制，重点放在：

1. **效果归因**：把曝光、读取、采用、任务结果、用户纠正、成本和环境条件分开，判断某条 Memory/Skill 是否真的带来效用；
2. **经验与 Skill 的验证式晋升**：多路径/多轨迹比较、跨轨迹批评、流程与战术经验分离、验证器或 replay 后再晋升（XSkill、EvoSkills 等）；
3. **学习型 Memory 操作策略**：根据任务状态、候选内容、预算和历史结果，学习何时检索、再次检索、注入计划、巩固或保持不动（MemCon、AgeMem 等）；
4. **持续评测与迁移**：观察经验在新任务、不同环境/版本和不同成本预算下是否仍有效，并把结果反馈到后续经验更新。

安全、污染攻击、技能后门、权限治理和供应链问题全部排除，不进入第六层的正文或前沿综述。

**建议的新第六层结构**

```text
6.1 现有基线（简写）
6.2 效果反馈与因果/效用归因
6.3 经验 → 流程/Skill 的验证式晋升
6.4 学习型 Memory 操作策略
6.5 持续评测、迁移与成本反馈
```

每个前沿机制仍按 `输入 → 处理 → 输出 → 例子 → 当前证据边界` 展开；不把安全主题作为额外小节或横切补充。

**状态：** 已确认

### Q046 — 第六层前沿是否还有更多机制

**用户问题**

> 还是有点少，前沿探索还有什么？

**回答（待用户确认）**

前面的四项把几个不同方向合并得太粗。排除安全主题后，第六层前沿还可以展开为以下八类；它们分别改变反馈信号、经验表示、晋升方式、迁移范围或学习对象。

#### 1. 反馈信号建模：从“使用过”到“结果证据”

```text
输入：曝光、读取、采用、工具/测试结果、用户纠正、成本和环境
→ 区分使用行为与任务后果，并建立 memory/skill → outcome 关联
→ 输出 utility、confidence、applicability 和可追溯反馈记录
```

这是一切持续学习的基础。Codex 的 citation/usage 只覆盖读取信号；TencentDB 还没有稳定的资产使用和效果账本。前沿应进一步区分“被看见”“被采用”和“确实带来结果”。

#### 2. 经验对象分层：Experience 与 Skill 分开

一次经验可以是局部战术提示，也可以是跨任务的流程。XSkill 将二者拆成 Experience Bank 与 Skill Library：前者记录触发条件→动作建议，后者记录任务级 workflow、工具模板和步骤。这样读取时可以分别复用“当前分支的小技巧”和“完整 SOP”，不必把所有内容都压成同一种 Memory。[XSkill](https://xskill-agent.github.io/xskill_page/)

```text
轨迹结果
→ tactical experience（局部条件/动作/失败模式）
→ procedural skill（跨任务流程/工具模板）
→ 分别进入后续检索与使用
```

#### 3. 多轨迹对照与并行经验归纳

不是每条成功轨迹都值得学习。前沿路线会收集同一任务的多条成功/失败路径，再做 cross-rollout critique，区分稳定方法、偶然步骤和失败分支。Trace2Skill 更进一步：并行分析轨迹池，提出多个 patch，再层次化合并成一个可迁移 Skill，而不是按单条轨迹顺序追加。[Trace2Skill](https://arxiv.org/abs/2603.25158)

```text
同一任务的多条轨迹 + outcome
→ 并行分析成功/失败原因
→ 提出局部经验 patch
→ 归纳共同前置条件、分支和验证步骤
→ 输出统一 Skill/Experience
```

#### 4. 失败驱动与验证器驱动的技能演化

经验学习不只从成功案例提炼，也可以从 hard cases、失败测试和“已有 Skill 没有解决的问题”反向驱动修改。EvoSkills 让 Skill Generator 与 Surrogate Verifier 交替迭代；MemSkill 则让 Designer 针对困难样例扩展或修订 memory-skill bank。[EvoSkills](https://arxiv.org/abs/2604.01687) [MemSkill](https://arxiv.org/abs/2602.02474)

```text
失败/未解决案例
→ 定位现有 Skill 的缺口
→ 生成修订或新 Skill
→ verifier/replay 检查是否解决原案例且没有破坏旧案例
→ 晋升新版本或保留旧版本
```

这比“LLM 读完轨迹后直接写一份 SKILL.md”多了一个可反复验证的学习循环。

#### 5. 跨任务、跨角色、跨模型的迁移反馈

持续学习不能只看原任务是否再次成功，还要看经验换到新任务和新环境是否仍有效。AFTER 用跨任务、跨角色和跨模型的 split 测量 procedural memory 的迁移；它显示有些 Skill 可以广泛复用，有些会过拟合某个角色或工作流。[AFTER](https://arxiv.org/abs/2606.23127)

```text
输入：同一 Skill 在不同 task / role / model / environment 的结果
→ 估计 transfer、specialization 和环境漂移
→ 更新 Skill 的适用范围、条件和版本
→ 输出可迁移性与需要重新验证的标记
```

#### 6. 学习“Memory 操作”的技能库，而不只是学习 Memory 内容

MemCon 学的是操作策略：何时 retrieve、re-retrieve、plan injection、consolidate 或 no-op。MemSkill 更进一步，把“如何抽取、整合和维护 Memory”本身做成可选择、可进化的 memory skills，由 controller 选用、executor 执行、designer 更新。[MemCon](https://arxiv.org/abs/2607.13591) [MemSkill](https://arxiv.org/abs/2602.02474)

```text
任务状态 + Memory 状态 + 历史结果
→ controller 选择 memory-operation skill
→ executor 执行该操作
→ 结果和失败案例反过来改进 controller/skill bank
```

这和第五层的“某次查询走哪条路径”不同：这里学习的是跨任务的 Memory 管理行为。

#### 7. 元学习 Memory 架构本身

ALMA 把学习对象再提高一层：Meta Agent 搜索用可执行代码表达的 Memory design，包括表示、存储、检索和更新机制，而不是只调整某条 Memory 内容或操作策略。[ALMA](https://arxiv.org/abs/2602.07755)

```text
多个任务的长期结果与成本
→ Meta Agent 提出/修改 Memory design
→ 在顺序决策环境中评估
→ 保留更有效的表示、检索和更新组合
```

这是“学习如何设计 Memory”，证据仍主要来自研究原型，不能写成 TencentDB/Codex 已有能力。

#### 8. 持续评测、回放与成本效用闭环

反馈层还需要一个长期 evaluation loop：固定一组历史任务和新任务，周期性 replay 已有 Memory/Skill，比较成功率、迁移、返工、token、延迟和后台维护成本。否则系统只会知道“某条经验被用过”，不知道它是否已经过时或不值得维护。

```text
历史任务/新任务 replay
→ 对比 no-memory、旧版本、新版本和不同 policy
→ 计算效果增益 − token/延迟/维护成本
→ 将结果写回 utility、晋升和下一轮实验计划
```

Omri 等人的分阶段系统表征可以作为成本拆分参考；`MemoryAgentBench`、`AFTER`、`Mem2ActBench` 和 `SkillsBench` 则分别覆盖读写、迁移、行动和技能质量的不同切面，不能压成一个总分。

**扩展后的新第六层结构**

```text
6.1 现有基线（TencentDB Review；Codex citation/usage）
6.2 反馈信号与效果归因
6.3 Experience / Skill 分层
6.4 多轨迹对照与经验归纳
6.5 失败驱动、verifier/replay 与 Skill 晋升
6.6 跨任务/角色/模型迁移与环境适应
6.7 学习 Memory 操作技能与操作策略
6.8 元学习 Memory design
6.9 持续评测与成本效用反馈
```

这些方向之间有层次差异：Experience/Skill 是学习结果的表示，verifier/replay 是晋升机制，MemCon/MemSkill 是学习操作，ALMA 是学习整个 Memory 设计；不能把它们都写成“自动总结经验”。安全相关内容按本轮要求排除。

**状态：** 部分确认（案例写法由 Q048 修正）

### Q047 — 第六层前沿是否以具体论文或仓库详细展开

**用户确认**

> 嗯，这样也可以，就以具体的论文或仓库详细展开。

**回答与确认**

确认。第六层前沿不写成抽象的趋势清单，而采用“一个机制对应一个代表性论文或固定仓库”的详细 walkthrough；但不为所有案例强行套同一个模板。

每个案例按照自己的机制结构、实验流程和产物来写，只要求始终扣住第六层的主题：反馈如何变成经验、技能、策略或新的 Memory design。

当前候选的主线来源为：

| 第六层机制 | 代表来源 | 重点展示 |
|---|---|---|
| Experience/Skill 分层与多模态经验 | XSkill 项目/论文 | multi-path trajectory、cross-rollout critique、Experience Bank 与 Skill Library |
| 并行轨迹归纳与可迁移 Skill | Trace2Skill 论文/官方仓库 | trajectory pool → parallel patch → hierarchical consolidation |
| 失败驱动与验证式晋升 | EvoSkills 论文 | Generator 与 Verifier 的迭代反馈 |
| 可学习、可进化的 Memory 操作 | MemSkill 论文 | controller、executor、designer 与 hard-case evolution |
| 任务反馈驱动的操作策略 | MemCon 论文/仓库 | retrieve、re-retrieve、plan injection、consolidate、no-op 的在线策略 |
| 跨任务/角色/模型迁移 | AFTER 论文与基准 | transfer split、specialization、环境适应 |
| 元学习 Memory 架构 | ALMA 论文/仓库 | Meta Agent 搜索表示、检索和更新设计 |
| 效果归因与长期成本 | Causal Memory 仓库、Omri 表征研究、行动/技能基准 | decision→outcome、utility、replay、token/延迟/成功率 |

这些来源不是都要写成同等篇幅：XSkill、Trace2Skill、EvoSkills、MemSkill、MemCon、ALMA 作为机制 walkthrough；AFTER、Causal Memory、Omri 和基准按各自特点作为迁移、归因或成本材料。正文不做逐案例的 TencentDB/Codex 对比；两套仓库只在入口处用极短篇幅说明反馈闭环很浅。安全相关论文和攻击面不纳入。

**状态：** 部分确认（案例写法、比较范围和“证据边界”栏目由 Q048 修正）

### Q048 — 第六层案例是否统一模板、是否对比仓库、是否写“证据边界”

**用户修正**

> 不要每个案例统一写，每个案例按照自己的特点详细写，关键是扣到第六层的主题。然后不用写与 TencentDB/Codex 的差异，他们根本没什么反馈闭环写什么对比呢。证据边界是什么，看着也像是你乱搞的。

**回答与确认**

同意，Q047 的写法全部收窄：

1. **不设统一案例模板。** XSkill 重点写 multi-path、Experience/Skill 双产物和 cross-rollout critique；Trace2Skill 重点写并行 patch 与层次化归纳；EvoSkills 重点写 Generator–Verifier 迭代；MemSkill 重点写 controller/executor/designer；MemCon 重点写在线操作策略；ALMA 重点写 Meta Agent 搜索 Memory design。每篇按其真实机制展开，不强行补齐相同字段。
2. **不做逐案例的 TencentDB/Codex 对比。** 只在第六层开头极简交代两套仓库现有闭环：TencentDB 的轨迹 Review/Skill 版本、Codex 的 citation/usage；之后正文主体全部用于前沿机制本身。
3. **删除“证据边界”这一泛化栏目。** 不再使用这个抽象术语。只有当某篇论文或仓库的实验范围、输出或限制是理解其机制所必需时，才用具体事实自然说明，例如“该流程在其 benchmark 的多路径轨迹上运行”或“该仓库输出的是 Skill patch 而不是运行时策略”；不额外添加统一的成熟度/不能外推段落。

第六层最终写作原则是：

```text
以具体论文/仓库为主角
→ 详细还原它自己的反馈输入、处理循环和学习产物
→ 说明这些产物怎样影响后续经验/Skill/策略
→ 只保留与第六层主题直接相关的事实
```

**状态：** 已确认

### Q049 — 六层正文的目录脉络

**用户问题**

> 现在六层经过这么多问答了，给我写一下每一层要写的脉络，类似目录形式不用展开。

**回答（目录草案，待用户确认）**

```text
第 1 层  输入：什么进入 Memory
  1.1 共同主输入：user input / assistant response / tool call / tool result
  1.2 输入事件的证据角色与必要 envelope
      thread/session/task、identity/scope、time、cwd/branch/commit、环境/版本/结果
  1.3 TencentDB 输入链
      Chat L0、Skill 完整执行轨迹、Wiki 文档、CodeGraph 仓库/commit
  1.4 Codex 输入链
      Thread/rollout 事件与项目元数据
  1.5 前沿新增 payload（简写）
      视觉观察、世界/设备状态、Computer Use 事件流
  1.6 排除与边界
      控制请求、外部 Agent 导入等不作为共同主输入展开

第 2 层  写入与形成：输入怎样变成 Memory
  2.1 形成层职责与首次生成 L1/L2/L3/Skill
  2.2 TencentDB
      L0 capture
      L1 extraction + dedup/update/merge
      L2 Scene CREATE/UPDATE/MERGE/NO-OP
      L3 Persona 首次生成与增量重写
      Skill trajectory Review、分类、评分、版本生成
  2.3 Codex
      Phase 1：rollout → raw_memory/rollout_summary/no-op
      Phase 2：候选 + 旧文件 + diff → MEMORY/summary/skills
  2.4 Prompt、准入、来源和 no-op 约束
  2.5 前沿补充
      MemTxn 的 proposal → source-supported admission → commit（只写桥接）
  2.6 明确不纳入
      AtomMem 删除；XSkill 移到第六层；压缩不作重点

第 3 层  状态、存储与索引：Memory 放在哪里
  3.1 权威状态、历史与派生投影的载体
  3.2 TencentDB 载体
      JSONL/Markdown、SQLite/数据库、FTS/BM25、vector、graph
      Wiki Markdown + FTS/BM25 + links；CodeGraph repo/commit + nodes/edges
  3.3 Codex 载体
      rollout JSONL、state DB、memories DB、Markdown Memory root、Git baseline
  3.4 载体与索引的简要关系
  3.5 前沿简述
      双时间版本图：stable identity、immutable revision、valid time、transaction time
  3.6 范围边界
      不展开复杂图、latent memory；检索算法放第五层

第 4 层  管理与演化：已有状态怎样更新
  4.1 管理主线
      UPDATE / MERGE / SUPERSEDE / CONFLICT / VERSION
  4.2 TencentDB（只写实际管理）
      L1 update/merge/version
      L2 Scene update/merge/rewrite
      L3 Persona rewrite/narrow
      Skill immutable version、expected_version、active head
  4.3 Codex
      Phase 2 文件级合并、改写、supersede 与隐式旧表述收窄
  4.4 MemTxn
      source-supported update、Temporal Resolver、commit/reject、snapshot/recovery
  4.5 两个仓库缺少的语义遗忘前沿
      遗忘不等于删除
      active-state revoke、派生修复、再生成阻断、行为不再依赖
  4.6 不展开
      人工/API CRUD、数据库运维和安全专题

第 5 层  读取与上下文：各种 Memory 怎样进入上下文
  5.1 统一阅读表
      Memory 类型 → 直接注入/先检索 → 检索方式 → 输出形态
  5.2 TencentDB
      L3 直接注入
      L2 index/path → read scene
      L1/L0 工具检索（BM25/vector/hybrid 或消息/时间查询）
      Skill 目录 → view/files；Wiki/CodeGraph 工具入口 → 正文/关系
  5.3 Codex
      memory_summary 直接注入
      MEMORY.md 词法 search/read
      skills/rollout summaries/raw rollout 按指针渐进读取
  5.4 上下文编排
      全文、摘要、索引、片段、工具结果的组合、顺序、缓存和预算
  5.5 前沿（具体来源详细展开）
      意图驱动路由与分层预算
      统一目录/URI 层级检索、hydration、轨迹
      证据/行动感知上下文编排

第 6 层  反馈、经验与持续学习：使用后怎样变得更好（重点）
  6.1 现有基线（极简）
      TencentDB：trajectory → Review → Skill version，但无效果闭环
      Codex：citation → usage → Phase 2 selection，但无结果归因
  6.2 反馈信号与效果归因
      exposure / read / adopt / outcome / correction / cost / environment
  6.3 Experience 与 Skill 的分层产物
  6.4 多轨迹对照、cross-rollout critique、并行归纳
  6.5 失败驱动、verifier/replay 与 Skill 晋升
  6.6 跨任务/角色/模型迁移与环境适应
  6.7 学习 Memory 操作技能与操作策略
  6.8 元学习 Memory design
  6.9 持续评测、回放与成本效用反馈
  6.10 具体论文/仓库 walkthrough
      XSkill、Trace2Skill、EvoSkills、MemSkill、MemCon、AFTER、ALMA、
      Causal Memory/Omri/相关基准
  6.11 排除
      安全、污染攻击、权限治理、供应链问题
```

**详略权重**

```text
第 1 层：简略
第 2 层：重点（首次形成 L1/L2/L3/Skill）
第 3 层：简略
第 4 层：重点（更新/合并/冲突、MemTxn、遗忘前沿）
第 5 层：重点（进入方式、检索方式、上下文编排）
第 6 层：最重点（前沿论文/仓库驱动的反馈与持续学习）
```

**状态：** 部分确认（目录结构按 Q050 重排）

### Q050 — 六层目录应按系统/案例展开，而不是抽象总节

**用户修正**

> 2.1 不对，这些东西不都是 TencentDB 的嘛，你要不就直接从 TencentDB 开始说。3.5 不对，这写了干什么，尤其是这是让你写什么，你把不写什么放上去干什么，不写的直接不写不就行了。4.6 一样的问题。5.4 单独出一节要写什么？第六层每一部分不是应该都有对应案例吗，为什么把案例都放一块写？

**回答与确认**

同意，目录按以下原则重排：

1. 每层直接从 TencentDB 的具体实现开始，再写 Codex，再写前沿案例；不先放一个把具体内容重新概括一遍的抽象总节。
2. 删除“边界/不展开/排除项”目录项；目录只列真正要写的内容。
3. 第三层的双时间版本图改成具体前沿案例，写它怎样构造、解决什么查询问题和输出什么状态，不再写成“前沿简述”。
4. 第四层的遗忘改成具体前沿案例（如 GEM/MemState、Control-Plane Placement），不单列“哪些不写”。
5. 第五层不单独设一个空泛的“上下文编排”节；每个 Memory 路径都同时写进入方式、检索方式、输出形态和上下文如何落位，最后可用一个具体任务例子串起来。
6. 第六层每篇论文/仓库单独成节，按自己的机制展开；不把所有案例集中放在一个 walkthrough 清单里，也不做逐案例 TencentDB/Codex 对比。

**修订后的六层目录脉络**

```text
第 1 层 输入
  1.1 TencentDB：Chat、Skill、Wiki、CodeGraph 的实际输入
  1.2 Codex：Thread/rollout 事件与项目元数据
  1.3 前沿输入案例：视觉观察、世界/设备状态、Computer Use 事件流

第 2 层 写入与形成
  2.1 TencentDB：L0 → L1 → L2 → L3 与 Skill 的首次形成
  2.2 Codex：Phase 1 候选与 Phase 2 文件化 Memory/Skill 形成
  2.3 MemTxn：source-supported proposal → admission → commit（简述桥接）

第 3 层 状态、存储与索引
  3.1 TencentDB：JSONL/Markdown、数据库、FTS/vector/graph、Wiki、CodeGraph
  3.2 Codex：rollout JSONL、state/memories DB、Markdown、Git baseline
  3.3 双时间版本图案例：stable identity、immutable revision、valid/transaction time

第 4 层 管理与演化
  4.1 TencentDB：L1/L2/L3/Skill 的 update、merge、version、conflict
  4.2 Codex：Phase 2 文件级合并、改写、supersede 与冲突处理
  4.3 MemTxn 案例：来源校验、Temporal Resolver、提交与恢复
  4.4 GEM/MemState 案例：状态级 revision 与派生关系管理
  4.5 Control-Plane Placement / ForgetEval 案例：语义遗忘操作如何落地

第 5 层 读取与上下文
  5.1 TencentDB：L3 直注、L2 导航→正文、L1/L0 工具检索、Skill/Knowledge 路径
      每条路径内写：进入方式 → 检索方式 → 输出 → 上下文位置
  5.2 Codex：summary 直注、MEMORY 词法 search/read、summary/skill/rollout 渐进读取
      每条路径内写：进入方式 → 检索方式 → 输出 → 上下文位置
  5.3 MemFlow 案例：意图路由、检索层级与动态预算
  5.4 OpenViking 案例：目录/URI 递归检索、L0/L1/L2 hydration 与轨迹
  5.5 CICL 案例：证据/行动感知的上下文选择与编排

第 6 层 反馈、经验与持续学习
  6.1 TencentDB：轨迹 Review → Skill 版本（简短现状）
  6.2 Codex：citation → usage → Phase 2 selection（简短现状）
  6.3 XSkill 案例：Experience Bank、Skill Library、多路径与 cross-rollout critique
  6.4 Trace2Skill 案例：轨迹池、并行 patch、层次化 Skill 合并与迁移
  6.5 EvoSkills 案例：Generator–Verifier 迭代晋升
  6.6 MemSkill 案例：controller、executor、designer 与 hard-case evolution
  6.7 MemCon 案例：任务反馈驱动的 Memory 操作策略
  6.8 AFTER 案例：跨任务、角色、模型的程序性经验迁移
  6.9 ALMA 案例：Meta Agent 搜索 Memory design
  6.10 Causal Memory / Omri / 基准案例：结果归因、成本和持续评测
```

第六层的每个案例都按自身机制和材料结构写，不能强行套统一字段；“证据边界”不再作为固定栏目，只有理解该案例必需时才写具体实验或仓库事实。

**状态：** 已确认

### Q051 — 正文统一改写的 Goal Prompt 与执行约束

**用户要求**

> 接下来我需要完成正文的改写。我需要写一个 goal prompt，重点就是看这个问答文档，尤其是最后的这个目录是绝对的重点最高原则，然后内容写作可以参考这两份 HTML，最终目的是重写 `frontier-research/agent-memory-practical/2026-08-25`，可以迭代几版。

**已确定的执行原则**

- `seven-layer-architecture-rewrite-qa.zh-CN.md` 是最高优先级规范；以最后确认的 Q050 六层目录为最终结构，后续旧草稿、旧目录和助手早期判断均服从它；
- `tencentdb-agent-memory-self-evolution.zh-CN.html` 与 `codex-local-memory-self-evolution.zh-CN.html` 只作为内容组织、输入/处理/输出表达、案例和渐进披露展示方式的参考；
- 目标目录最终重写为六层，删除原第六层，原第七层顺延为新的第六层；
- 正文重写允许多轮迭代，每轮都要基于上一轮结果复查问答覆盖、事实准确性、结构清晰度和链接一致性；
- 不做实验；事实核验使用固定源码、论文、仓库和现有研究材料的静态证据；
- 安全主题不纳入第六层前沿；不把安全、权限治理或攻击面扩写成反馈机制。

**状态：** 已确认
