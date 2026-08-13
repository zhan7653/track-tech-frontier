# 记忆对象模型：同一段经历怎样变成不同的持久状态

很多 Agent Memory 的介绍从存储后端讲起：向量库、图数据库、文件系统或关系数据库。但后端只回答“数据放在哪里”，没有回答“这条数据在系统中是什么”。同一句“部署改用新的凭据”可以是一次对话事件、一个当前项目事实、一条对旧配置的修订、一个供下次复用的操作步骤，也可以只是尚未核验的模型推断。若它们都被压成 `text + embedding`，检索仍然可以工作，更新、冲突、共享、删除和行动授权却失去明确语义。

本篇把对象模型拆到可实现的程度：每类对象保存哪些字段，怎样形成，如何改变，读取时返回什么，以及错误会在哪里发生。它不是一套强制 schema；它解释当前论文和工程实现为什么逐渐从“文本块”转向多对象状态。

## 1. 先区分三层：证据、权威状态与访问投影

一套可更新 Memory 至少面对三种性质不同的数据：

```text
原始证据 / receipt
    └─“发生过什么、谁提供、何时发生”
             │ extraction / validation
             ▼
权威对象 / revisioned state
    └─“系统目前允许引用什么、历史怎样演化”
             │ materialization
             ▼
访问投影 / derived index
    └─“怎样更快找到候选：摘要、FTS、embedding、图边、缓存”
```

三层可以使用同一个数据库，也可以分散在多个后端；区别是语义而不是物理部署。事件回执应能在抽取器升级后重新处理；权威对象应能回答 current/history/conflict；投影应能从已提交版本重建。把 embedding collection 当作唯一事实层时，更新通常退化成覆盖向量，删除退化成“搜索不到”，摘要也无法说明来自哪些证据。

[Generative Agents](https://arxiv.org/abs/2304.03442) 的 observation stream、reflection 与 planning 已经体现了“记录—派生解释—行为使用”的分层；[MemoryBank](https://arxiv.org/abs/2305.10250) 同时保存对话、事件摘要与不断变化的用户评估。后来的 [MemTxn](https://arxiv.org/abs/2607.27834) 和 [GEM/MemState](https://arxiv.org/abs/2605.26252) 将这一区别推进到提交、版本与状态轨迹，但它们仍是近期研究方向，而不是跨实现标准。

## 2. 事件与证据对象：保存能够回放的发生记录

### 2.1 状态结构

事件对象的最小语义不是 `content`，而是一张带身份的回执：

```text
Event {
  event_id
  actor, subject, tenant, session
  event_type                  # user_turn / tool_call / tool_result / observation
  payload_ref, payload_hash
  occurred_at, recorded_at
  source, trust_class
  parent_event_ids[]
  sensitivity, retention_class
}
```

`occurred_at` 与 `recorded_at` 分开，可以表达离线导入、迟到日志和“系统当时尚不知道”的事实；`actor` 与 `subject` 分开，可以表达“Agent A 记录了关于用户 B 的观察”；`payload_ref` 允许原文位于受控存储中，而索引只保存可检索表示。

### 2.2 写入与读取

事件写入通常是追加式：宿主 hook 捕获一次 turn 或工具结果，绑定 session、principal、时间和来源，计算 hash 后提交。此时不必判断其中每个陈述是否真实。管理阶段可以归档、分段或生成摘要，但不会悄悄改变原事件。读取有两条路径：按时间/任务直接回放，或者作为事实、画像、关系和技能的 source span 回填。

事件底座最重要的性质是**重处理能力**。当抽取 schema、embedding 模型或安全策略变化时，系统可以从原事件重新生成派生对象。代价是原始历史增长快、敏感内容保留面大，且仅靠事件检索很难直接回答“当前事实是什么”。

### 2.3 失败位置

- capture hook fail-open：Agent 继续运行，但关键工具结果未进入日志；
- session/subject 绑定错误：事件存在，却被归入错误用户或项目；
- 原文过早丢弃：摘要保留下来，但无法修复后来发现的抽取错误；
- retention 与审计冲突：为了回放保留完整内容，同时扩大隐私与泄露风险。

这些失败解释了为什么“保存全部聊天记录”既是重要基线，又不是完整 Memory。

## 3. 原子事实、画像与信念：维护一个可以被纠正的当前视图

### 3.1 从候选陈述到稳定身份

事实写入通常包含四步：

1. 从一段事件中抽取候选陈述和 source span；
2. 解析 subject、predicate、object 以及时间/条件；
3. 在相同 subject/predicate/scope 下查找旧对象；
4. 判定 `ADD / REINFORCE / SUPERSEDE / CONFLICT / NOOP`。

这个过程看似类似数据库 upsert，实际多出两个不确定层：抽取器可能把一个限定句切错，entity resolution 也可能把同名主体合并。因而较完整的对象会把“当前解释”与“原始来源”分开：

```text
Assertion {
  assertion_id, subject_id, predicate, value
  epistemic_status            # observed / asserted / inferred
  source_event_ids[]
  valid_from, valid_to
  recorded_at
  confidence, extraction_model
  revision, supersedes[], conflicts_with[]
  consent, allowed_purposes[]
}
```

`observed`、`asserted`、`inferred` 不是置信度的同义词。用户明确说出的偏好是 asserted；工具 API 返回的账户状态可能是 observed；模型根据多次行为总结的偏好是 inferred。三者在自动共享、行动使用和删除时具有不同资格。

### 3.2 画像不是一段不断重写的摘要

画像可以被看作多个 assertion 的 subject-scoped view，而不是唯一的一段 personality summary。当前视图由有效、未撤销、适用于当前用途的字段组成；历史视图保留各字段的修订轨迹；冲突视图呈现尚未解决的断言。这样，“用户不吃花生”与“用户只是不喜欢花生酱”可以先构成冲突，再由更精确的后续证据分别修订 allergy 与 preference 字段，而不是让模型重写整段画像。

[Mem0](https://github.com/mem0ai/mem0) 的固定版本写入会按 user/agent/run scope 找旧候选，调用模型抽取事实和更新动作，再维护主 memory、history 与可选 entity signals；它展示了工程中的 consolidation 形状，也暴露了多存储部分成功和模型误判问题。[AtomMem](https://arxiv.org/abs/2606.19847) 则把选择性原子事实继续组织成 event、temporal profile 和 associative graph，强调粒度会影响后续表示。

### 3.3 事实对象的典型失败

- **false merge**：两个相似事实被当作同一对象，新值覆盖无关旧值；
- **false split**：同一事实形成多个 identity，读取时出现重复或互相矛盾；
- **inference promotion**：模型猜测进入事实层，之后又被当作来源重新强化；
- **condition loss**：抽取保留结论，删掉“仅在某项目/日期/环境下”的条件；
- **profile inertia**：字段已修订，派生摘要或 prompt block 仍继续暴露旧值。

## 4. 关系、世界与项目状态：保存依赖、位置与演化路径

### 4.1 关系对象不能只是一条无类型边

结构化 Memory 常把实体设为节点，把关系设为边。但用于更新和行动时，至少要区分三类边：

- **association**：两项内容相关，适合扩大候选，但不触发修订；
- **dependency/extension**：下游状态由上游派生，上游变化可能要求重新计算；
- **causal/action**：决策、动作和结果之间的有向关系，用于经验复用与归因。

边本身也应带来源、方向、有效时间、置信度和 revision。否则“相关”容易被误读为“支持”，“先发生”容易被误读为“导致”。[GEM/MemState](https://arxiv.org/abs/2605.26252) 明确区分 association 与 extension，后者会影响 revision propagation；[Causal Memory 工程剖面](../../projects/jingxuanc--causal-memory.md)则展示 decision→outcome edge、facts 与 raw session log 如何落在同一 SQLite 骨架上。

### 4.2 世界状态与项目状态的额外字段

世界状态需要 observation frame、位置、可见性、对象持续身份和 action consequence；项目状态需要 repository、branch、commit、worktree、task、decision 和 artifact version。它们不是“更长的用户画像”：

```text
WorldFact  = object + spatial/temporal frame + observer + visibility + uncertainty
ProjectFact = repo + branch + commit/range + artifact + decision/task + validity
```

具身系统中的“箱子在房间里”可能只在某次观察时成立；Coding Agent 的“接口已迁移”可能只对某分支或 commit 之后成立。读取时若丢失 frame 或 commit，语义相似的内容反而会产生错误行动。

[AriGraph](https://arxiv.org/abs/2407.04363) 将 episodic memory 与 knowledge-graph world model 结合，用于环境中的状态与行动；[A-MEM](https://arxiv.org/abs/2502.12110) 会在新 note 到来时建立动态链接并更新相关历史表示。它们说明结构化状态能表达更多问题，但建图错误、entity merge 和维护成本也随之增加。

## 5. 程序、反思与技能：保存能够改变行动的工件

程序性对象的 payload 可能是语言反思、步骤清单、工具调用模板或代码。它的关键字段不是“用户/事实”，而是适用性与执行边界：

```text
Procedure {
  procedure_id, goal_pattern
  preconditions[], environment_fingerprint
  tool/API versions, required_capabilities[]
  instruction | script | executable_ref
  expected_effects[], known_failures[]
  source_trajectory_ids[]
  validation_status, risk_class
  revision, deprecated_at
}
```

写入时从包含 outcome 的 trajectory 中提出候选；管理阶段去重、验证、晋升、版本化或弃用；读取先检查 precondition/environment，再做语义匹配；使用时仍需重新授权。一次程序误用可能修改文件、发消息或调用外部服务，因此它与 profile/fact 不能共享“相似就取回”的全部语义。

[Reflexion](https://arxiv.org/abs/2303.11366) 保存 verbal reflection，[Voyager](https://arxiv.org/abs/2305.16291) 维护可组合的 executable skill library；二者标出了从“解释经验”到“执行经验”的两个端点。后续 [MemSkill](https://arxiv.org/abs/2602.02474) 和 [XSkill](https://arxiv.org/abs/2603.12056) 将问题推进到 skill evolution 与跨模态经验，而近期安全研究表明错误轨迹也会被压成持久指令。完整算法与系统 walkthrough 见[使用、反馈与技能入口](../06-use-feedback-and-skills.md)及其[深潜索引](../README.md)。

## 6. 共享状态与控制元数据：内容之外仍有一套状态

### 6.1 共享对象是引用、复制还是共同修订

“团队记忆”至少存在三种不同形状：

1. 私有对象保持不变，只向团队暴露一个受限 view；
2. 对象被复制到共享 namespace，之后产生独立版本；
3. 多个 principal 共同修订同一 canonical object。

三者的冲突、撤销和删除含义完全不同。共享对象需要 actor、owner、subject、authority、visibility、purpose 和 revocation；单一 `namespace=team` 只能表达地址，不能表达谁有权修改或撤回。[Open Memory Protocol 工程页](../../projects/smjai--open-memory-protocol.md)展示了一套 schema + reference server + adapters 的项目级尝试，但固定版本的实际搜索是 FTS，并不证明跨实现语义已经一致。

### 6.2 控制元数据不是普通 metadata

以下信息会直接改变状态行为，因而更接近控制对象：

- admission、quarantine 与 promotion decision；
- retention、TTL、legal hold、forget/purge state；
- revision parent、transaction receipt、snapshot/rollback pointer；
- extractor、embedding、index 与 policy version；
- index watermark、rebuild/reconciliation status；
- query budget、selection trace、action authorization receipt。

如果这些信息只存在于日志文本，系统无法查询“哪些对象仍由旧模型生成”“哪些索引落后于当前 revision”“这条技能为何获得执行资格”。控制元数据把写入、存储、生命周期、读取和行动连接为可观察的状态轨迹。

## 7. 粒度选择本身是一种算法

对象模型的困难不只是选字段，还包括决定一段经历应拆成几个对象。常见的粒度策略有：

| 策略 | 形成方式 | 主要收益 | 主要失败 |
|---|---|---|---|
| turn/chunk | 按消息或 token 窗口分段 | 确定、便宜、保留原文 | 多个断言粘在一起，更新困难 |
| atomic assertion | LLM/规则拆成 subject–predicate–value | 可精确修订和过滤 | false split/merge，条件丢失 |
| event bundle | 围绕一次任务/工具结果聚合 | 保留因果与上下文 | 边界依赖任务定义 |
| entity profile | 按主体和字段合并 | 当前视图紧凑 | 推断固化、历史细节丢失 |
| graph neighborhood | 按实体和关系动态连接 | 支持多跳与依赖传播 | 建图和维护成本高 |
| procedure/skill | 按可复用行为单元提炼 | 能直接影响行动 | 适用性、安全和版本问题最重 |

较新的工作并没有给出通用最优粒度。真正可比较的实验需要同时测 source-span coverage、merge/split error、更新正确性、候选召回、compiled token、行动结果和维护成本。只测最终 QA，会把对象形成和检索器的影响混在一起。

## 8. 当前可以确认什么，仍不能确认什么

可以较有把握地说：跨会话、可更新、会影响行动的 Memory 需要区分原始证据、可修订对象和访问投影；事实、程序、共享状态与控制元数据具有不同生命周期；主体、时间、来源和版本不能在检索后才补上。

仍不能确认的是哪一种对象 ontology 普遍最好。原子化可能改善精确更新，也可能丢掉上下文；图可能支持多跳，也可能放大错误边；画像可能提高连续性，也可能固化推断；技能可能提升复用，也可能把错误变成可执行资产。当前前沿真正需要的是从 taxonomy 到 schema、operator、conformance test 和 trajectory benchmark 的闭环，而不是再增加一组同义对象名称。

继续阅读：[身份、时间与共享语义](02-identity-time-and-shared-authority.md)解释对象怎样在多版本、多主体环境中保持意义；[代表系统与前沿](03-system-walkthroughs-and-frontier.md)解剖六种现实工程形状。
