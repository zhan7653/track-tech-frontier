# 记忆对象与作用域：先回答“记的是什么、属于谁”

> 本文面向已了解 Agent 与 LLM 的读者。它讨论跨会话、可更新、会影响后续推理或行动的外部 Memory；一次请求内的上下文、普通 RAG 文档库和模型参数本身只作为边界参照。证据与旧分类可回溯到 [v09 的基础分类报告](../../../agent-memory-v09/bundle/clusters/mm-c14-foundations-theory-taxonomies.md)、[结构化状态报告](../../../agent-memory-v09/bundle/clusters/mm-c03-structured-relational-temporal-memory.md) 和 [共享状态报告](../../../agent-memory-v09/bundle/clusters/mm-c11-shared-distributed-portable-memory.md)。

## 从一个看似简单的偏好开始

设想一个助手在上周记下“用户不吃花生”，今天又读到“用户对花生不过敏，只是不喜欢花生酱”。如果系统把两句话都当成无主的文本块，语义检索或许能找回它们，却很难回答四个更关键的问题：这是不是同一个人？哪句话描述的是事实、偏好还是一次偶发经历？第二句话是否修正了第一句话？这条信息可不可以被另一个 Agent、另一个团队或一个外部工具使用？

这就是 Agent Memory 的对象问题。记忆不是“一段可嵌入的文本”，而是带有行为语义的持久状态。对象类型决定写入时该抽取什么，更新时是否允许覆盖，读取时应带上哪些条件，以及它能否影响行动。作用域则决定状态属于谁、可被谁看见，以及过期或撤销如何传播。

当前较稳定的看法并不是一套唯一分类法，而是用三个正交维度描述状态：**对象**（保存的内容及其行为语义）、**操作**（它如何形成、变化和消失）、**控制信息**（主体、时间、来源、版本、权限和预算）。[MemoryBank](https://arxiv.org/abs/2305.10250) 已将存储、检索和更新分开，并同时处理对话、事件摘要与人格评估；[MemTxn](https://arxiv.org/abs/2607.27834) 则把来源支持、时间版本和恢复日志放到回答模型之外。它们并未证明全行业已有统一标准，但共同说明：对象、操作和控制信息不能再由一个 `text + embedding` 字段代替。

从实现角度看，一个最小对象不应只有正文。更接近真实系统的形状是：

```text
MemoryObject {
  immutable_id
  kind                  # event / fact / profile / relation / procedure / ...
  subject, owner, tenant
  payload_or_pointer
  observed | asserted | inferred
  source_receipts[]
  valid_time, recorded_time
  revision, supersedes[], conflicts_with[]
  visibility, allowed_purposes[], retention
  derivation_links[], index_generation
}
```

这些字段不是建议所有系统照抄的 schema，而是用来检查语义有没有丢失：若一个实现没有不可变身份，就很难把“同一事实的新版本”和“两条独立事实”分开；没有 source receipt，就无法从摘要回到原始证据；没有作用域和用途，检索层只能事后过滤；没有 derivation link，纠正或删除便不知道要失效哪些摘要、向量、图边和技能。

## 方案空间：对象不是按数据库品牌划分

下表是读者理解当前系统的一个实用谱系。一个系统可以同时拥有多类对象；它们不应被理解为彼此竞争的“产品类型”。

| 对象家族 | 保存什么 | 为什么不只是文本块 | 常见读取方式 | 主要风险与成熟度 |
|---|---|---|---|---|
| 事件与原始证据 | 对话轮次、工具输出、环境观察、导入回执 | 是其他摘要、事实和技能的可追溯依据 | 按时间、任务、来源定位 | 容量与隐私负担高；作为证据底座较成熟 |
| 事实、画像与信念 | 稳定事实、用户偏好、主体属性、带置信度的判断 | 需要主体、有效时间、来源和纠正语义 | 当前事实、历史事实或有冲突的事实 | 过时、臆测被写成事实、跨主体泄露；工程常见但治理不完整 |
| 关系、实体与世界/项目状态 | 人物、实体、依赖、空间关系、代码库决策和环境状态 | 查询常需要多跳关系、版本或“当时的状态” | 实体导航、图遍历、时间解析 | 建模和维护昂贵；在关系密集任务中处于早期到中期成熟度 |
| 程序、反思与技能 | 指令、脚本、工具序列、失败经验、可执行技能 | 它不是“关于用户的事实”，而是未来行动的候选方法 | 按任务、前置条件、工具版本匹配 | 旧工具假设、错误迁移、危险执行；研究活跃、工程保证较弱 |
| 共享与组织状态 | 团队知识、任务交接、跨 Agent 约定 | 关键是共享边界、角色、合并和撤销，不是更大的 profile | 按角色、任务和共享策略解析 | 权限坍塌、冲突传播、租户泄露；协议与互操作仍早期 |
| 控制元数据 | 来源、主体、版本、保留期、策略、索引版本、回滚点 | 它决定内容是否可用、可审计和可恢复 | 与任一对象一同传递 | 常被遗漏；职责层面已形成较强共识 |

这里的“事实”也不等于客观真理。它更准确地说是某个来源、某个主体、某段有效时间内可被系统引用的陈述。把 `observed`（直接观察到）、`asserted`（某人声称）、`inferred`（模型推断）分开，能避免把一次猜测写成永久画像。对世界状态和项目状态，观察位置、分支、提交版本、可见性及不确定性同样是内容的一部分，而非可选标签。

## 六类对象内部到底怎样工作

### 1. 事件和证据：用追加事实保留“发生过什么”

事件对象的核心不是一段聊天文本，而是不可变回执：输入、工具调用、结果、发生时间、主体、环境和来源指针。写入通常是 append，不尝试立即解决全部语义；管理阶段可以分段、归档或生成摘要，但保留能回放的原始顺序；读取既可以直接取原文，也可以作为派生事实的证据回填。它的优势是最少引入模型判断，代价是增长快、隐私面大、后续查询需要昂贵筛选。

`Generative Agents` 的 observation stream 和 `MemoryBank` 的 conversation/event summaries 是这一层的早期形状。到了工程系统，日志常成为可恢复的权威层：例如 v09 检查到的 `scope-recall-hermes` 先保留 journal，再把内容晋升为 durable fact。这里最新的研究问题不是“还要不要日志”，而是怎样给高吞吐工具轨迹建立统一 receipt、如何在不保留敏感明文的情况下维持可追溯性，以及怎样把一次事件精确关联到它后来产生的画像、图边和技能。

### 2. 事实、画像和信念：维护一个可纠正的当前视图

事实对象需要做 entity resolution：先确定陈述说的是谁或什么，再判断新陈述是新增、强化、矛盾还是替代。常见实现会把原对话交给 LLM 抽取原子事实，用现有候选作为上下文，让模型或规则返回 `ADD / UPDATE / DELETE / NOOP`，最后保存当前值与历史修订。画像则把多个事实组织成面向某主体的属性集合；信念还要显式保留置信度和推断来源。

[Mem0](https://github.com/mem0ai/mem0) 是这种 consolidating fact store 的工程代表：固定版本中，写入按 user/agent/run 过滤已有候选，再抽取事实并执行更新决策，同时保留历史；这说明 identity filter、fact extraction 和 consolidation 是不同步骤。`MemoryBank` 的 evolving personality assessment 则说明画像会随观察变化。二者共同的薄弱点是：LLM 判断“这是同一事实”可能误合并，推断可能被升级为真值，后端差异也会改变过滤和历史能力。

### 3. 关系、时间和世界状态：保存“什么依赖什么、何时成立”

当查询涉及多跳关系、项目依赖或历史状态时，单个事实值不够。结构化路线会把实体和断言设为稳定节点，把 `supports`、`depends_on`、`supersedes`、`causes`、`located_at` 等关系设为有类型边；每条边也携带来源、方向、有效时间和版本。读取时可以沿边扩展、做 PPR/spreading activation，或先解析 as-of 再选择版本。

[A-MEM](https://arxiv.org/abs/2502.12110) 会为新 note 生成结构属性、寻找相关历史并更新相邻表示；[Hindsight](https://arxiv.org/abs/2512.12818) 把 world facts、experiences、entity summaries 与 beliefs 分到不同逻辑网络；[双时间图存储](https://arxiv.org/abs/2607.26520) 则把有效时间和系统记录时间分开。近期 [MemState/GEM](https://arxiv.org/abs/2605.26252) 更进一步区分 association edge 与会触发修订传播的 extension edge：相关不等于依赖。其研究议程正从“能建图”转向 typed dependency propagation、语义与历史联合索引，以及读取引起 salience 更新时的一致性。

### 4. 程序、反思和技能：保存“下一次可能怎样做”

程序性对象至少包含任务模式、前置条件、步骤或代码、工具/API 版本、依赖、历史结果、失败反例、风险等级和弃用状态。写入不是把成功轨迹原样复制，而是从带结果的 trajectory 中提炼候选；管理阶段验证、版本化和晋升；读取先匹配适用条件，再匹配语义；使用时仍要重新授权。它和事实对象的根本差异在于：一次误用可能产生副作用，而不只是回答错误。

`Reflexion` 保存语言反思，`Voyager` 保存可组合代码技能，`MemP` 区分 trajectory、instruction 与 script，`MemSkill` 还学习管理这些工件的策略。2026 年的新研究重点已转向**迁移边界**和**晋升安全**：技能能否跨任务、角色、模型和工具版本复用，来自多个轨迹的共识是否真的可靠，以及不可信经验怎样在进入注册表前被阻断。这部分在[使用、反馈与技能分支](06-use-feedback-and-skills.md)展开。

### 5. 共享和组织状态：同一内容产生多个授权视图

共享记忆不是把 `user_id` 换成 `team_id`。它必须同时表示 actor、subject、owner、tenant、private/shared scope、用途、版本、authority、冲突和撤销。写入时先进入私有或证据区，通过显式 transition 才能分享；读取时根据当前 principal 和 purpose 生成视图；撤销时既要停止新读取，也要处理已派生的索引、缓存和下游副本。

当前协议线仍很早：W3C 的 Agent Memory Interop 是 Community Group，SAIHM 是 individual Internet-Draft，若干 AMP/OMP/UMP 是项目级草案；它们不能合称成熟标准。工程难点集中在身份映射、scope 保真、schema 往返、冲突合并和可验证撤销，而不是 JSON 字段是否相同。[v09 共享与可移植报告](../../../agent-memory-v09/bundle/clusters/mm-c11-shared-distributed-portable-memory.md) 的采用审计只找到弱集成信号，尚无跨实现的当前版本一致性证明。

### 6. 控制元数据：让其他对象具有可治理行为

控制元数据是独立 plane，而非业务内容附注。它包括 admission policy、retention/TTL、risk state、revision graph、index watermark、model/prompt version、transaction receipt 和 rollback point。它在 write 时决定候选能否提交，在 manage 时约束 merge/forget，在 read 时约束 visibility/as-of，在 action 时约束用途与权限。

[MemTxn](https://arxiv.org/abs/2607.27834) 将 source-supported admission、temporal resolver 与 durable snapshot journal 放在回答模型之外；[MemCon](https://arxiv.org/abs/2607.13591) 则把 retrieve、re-retrieve、consolidate、forget、no-op 等操作变成可学习控制动作。当前前沿不是让 learned controller 绕过规则，而是研究如何让它只能在可审计、可回滚的 primitive 内探索。

## 一条对象如何走过系统

对象分类只有进入数据流才有用。下图描述的是常见解剖结构，而不是推荐架构：不同系统可能合并、替换或省略其中模块。

```mermaid
flowchart LR
    E[对话 / 工具结果 / 观察] --> R[证据回执]
    R --> T[抽取候选对象\n事件、事实、画像、技能、状态]
    T --> G[作用域与准入\n主体、来源、时间、策略]
    G --> V[版本化权威状态]
    V --> P[派生表示\n摘要、向量、关键词、图]
    Q[当前任务、主体、as-of] --> F[作用域/时间过滤]
    P --> F --> C[带来源与冲突的上下文包]
    V --> C
    C --> A[推理或行动]
    A --> E
```

关键分界在于：原始证据、权威对象和派生表示不是同一层。一次工具调用可以留下事件回执；抽取器可能从中提出“用户偏好”“项目决策”或“可复用步骤”；这些候选经过范围、冲突和来源检查后成为可版本化状态。摘要、embedding 与图边则是为了访问而生成的投影。投影失效或索引重建不应改变“当时到底记录了什么”。

[AtomMem](https://arxiv.org/abs/2606.19847) 的原子事实、事件/画像层和关联图，是这种分层的近期代表；[A-MEM](https://arxiv.org/abs/2502.12110) 则把结构化笔记、历史链接和记忆演化放入写入过程。二者都说明写入会改变周围表示，但都不足以证明任意对象模式优于简单记录。对象越丰富，抽取误差、迁移和解释成本也越高。

## 作用域：谁的记忆，什么时候有效

“作用域”常被缩写为 `user_id`，但在实际 Agent 中至少有五个独立问题：主体是谁、可见范围多大、用途是否允许、何时成立、哪个版本可用。可将它们理解为一张随对象同行的身份证：

| 维度 | 需要表达的含义 | 典型错误 |
|---|---|---|
| 主体与租户 | 此状态属于用户、Agent、项目、团队还是组织 | 把单用户偏好当作全局事实 |
| 可见性与用途 | 可读、可写、可分享、可导出、可用于行动的范围 | 检索后才让模型“自觉忽略”越权内容 |
| 有效时间与记录时间 | 事实在现实中何时成立，以及系统何时得知 | 用最新记录回答历史问题，或把延迟导入当实时观察 |
| 版本与冲突 | 何者替代何者，是否仍存在未决冲突 | 静默覆盖，失去旧版本和纠正原因 |
| 来源与保留 | 谁或什么产生，能保存多久，删除影响哪些派生物 | 删除正文却遗留摘要、向量、缓存或工具痕迹 |

双时间（有效时间与记录时间）是解决“那时知道什么”和“现在认为何时成立”混淆的一种明确模型。[一项图原生双时间存储研究](https://arxiv.org/abs/2607.26520) 用不可变身份、版本节点和两类时间来表达此事；其价值主要在语义清晰，而非已经证明图数据库在所有任务上更好。对于变化快的世界或项目状态，这类区分尤其有意义；对于一次性、只读的问答，它可能只增加负担。

共享状态把作用域进一步推向动态权限和合并语义。v09 收录的 [Collaborative Memory 证据](../../../agent-memory-v09/bundle/clusters/mm-c11-shared-distributed-portable-memory.md) 将私有片段与选择性共享片段区分开，并要求来源与随时间变化的读写策略。一个“多人可访问的向量库”因此不自动成为组织记忆：它仍可能没有撤销、冲突、共享目的或责任归属。

## 真实实现能看见什么

开源项目提供的是实现形状，不是成熟度排行榜。固定版本的 [MemMachine](https://github.com/MemMachine/MemMachine) 文档把 episodic graph、SQL profile 与 working memory 分开；[Mem0](https://github.com/mem0ai/mem0) 公开了语义、BM25、实体和时间相关的检索面；[Cognee](https://github.com/topoteretes/cognee) 展示知识图、向量与图推理的组合。这些代码和文档足以说明“多对象、多表示”是现实工程模式，却不能单独证明隔离、删除、性能或生产采用。

不同项目的共同难题不是缺少一个新的对象名，而是语义能否穿透所有层：profile 的主体与纠正信息，能否随摘要、embedding、缓存和最终提示一起传递？技能的适用工具版本，能否在行动时再次核验？共享事实的撤销，能否使派生索引和下游 Agent 停止使用？这些问题把对象建模与生命周期、检索、安全和评测直接连在一起。

## 当前主流、近期变化与证据强弱

当前主流已从“把会话切块后向量检索”扩展为至少区分事件、语义/画像、过程性经验和控制元数据；存储、检索、更新的职责分离也较常见。过去十二个月的实质变化集中在三处：原子化与关系化的对象构造、带版本/有效时间的状态表达，以及把记忆操作本身当作受控动作。近 90 天内，MemTxn、双时间图存储与围绕控制面的工作是强信号，但大多仍是作者预印本或静态工程检查，尚未形成跨后端的统一对象协议。

成熟度应拆开看：对象与控制信息的职责分层可视为较成熟的架构共识；profile、事件和混合访问已在工程中常见；双时间、可移植共享语义和自动化的对象演化仍是中早期。没有足够的同任务、同预算、跨实现对照来证明“对象越结构化越好”，也没有公开证据证明任何现有接口已完整处理版本、撤销、物理删除与行动影响。

## 最新研究议程：从对象命名走向可执行语义

当前工作已不缺 episodic、semantic、procedural 等分类名称，真正缺的是把分类变成可运行且可测试的合同：

| 研究层 | 正在解决什么 | 为什么旧表示不够 | 决定性缺口 |
|---|---|---|---|
| Identity 与粒度 | stable object、atomic fact、topic/field 边界 | chunk 无法区分同一事实修订与相似事实 | 粒度变化下的 source coverage、merge/split error |
| Time 与 revision | valid/recorded time、current/history、late evidence | timestamp + last-write-wins 无法解释历史 | 多写者、冲突与迟到证据的共同语义 |
| Typed dependency | association 与会触发修订的依赖边分离 | 相似关系无法指导更新传播 | dependency ground truth 与 repair benchmark |
| Scope 与 portability | owner/tenant/purpose/revocation 随对象跨系统传播 | namespace 或 `user_id` 不等于授权合同 | 当前版本跨实现 round-trip/conformance |
| Procedure applicability | 工具版本、前置条件、effect 与 deprecation | 语义相似不表示技能可安全执行 | 跨任务/角色/模型/环境迁移和 action safety |
| Policy-bearing state | retention、admission、forget、retrieve side effect | 外部脚本和 prompt 约定无法验证状态轨迹 | policy language、commit enforcement 与隐私隔离 |

[GEM/MemState](https://arxiv.org/abs/2605.26252) 是该转向的鲜明例子：它把 memory state 表成 content、structure、policy 的组合，并将 ingestion、revision、forgetting、retrieval 视为状态级 operator；其 property-graph 原型只是可行性草图，尚未证明这是最终抽象。下一步研究需要让不同 backend 能表达同样的对象/操作语义，并通过 trajectory benchmark 检查当前值、依赖传播、活跃 footprint 和派生删除。

## 共识、争议与未解问题

**共识较强。** 跨会话、可变且会影响行动的 Memory 需要把对象语义与来源、主体、时间、版本分开保存；工作上下文不应成为唯一事实副本；过程性经验不应与用户事实使用同一套更新和授权语义。

**仍有争议。** 图、双时间或原子事实是否带来稳定净收益，取决于任务、检索器、token 预算、数据质量和维护成本。独立的 [LightMem 复现](https://arxiv.org/abs/2607.29104) 表明，在固定存储下，仅改变检索器和候选深度就可能反转表面优势；它反驳的是无条件优越性，而不是对象/版本语义本身的必要性。

**尚未解决。** 首先，缺少可以把 taxonomy 映射到真实 schema、操作语义和一致性测试的跨实现规范，因此“同名对象”常有不同含义。其次，缺少覆盖更新、删除、索引、缓存、备份和行动链路的端到端实验，无法确认一个纠正是否真正改变了后续行为。最后，个人、团队、项目与世界状态的边界在多 Agent 系统中会相互重叠；现有证据还不足以给出可移植的统一 ontology。

这些未知会影响的不是术语选择，而是读者如何解释系统声明：一个项目若只展示 `add/search`，只能证明它保存和访问了内容；若声称处理“长期记忆”，仍需看到对象、作用域、演化和行动之间的完整语义链。
