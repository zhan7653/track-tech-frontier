# 检索与上下文构造：从“找到相似文本”到“给行动提供合格证据”

> **深潜阅读路径：** 本页是读取链地图。query plan、硬过滤、BM25/ANN、RRF、图传播、主动检索和上下文编译见[候选生成、排序与导航](retrieval-context/01-candidate-generation-ranking-and-navigation.md)；Causal Memory、OpenViking、Engraphis、Mem0、claude-mem 和 Raven 的固定版本路径见[系统 walkthrough](retrieval-context/02-system-walkthroughs.md)；LongMemEval、MemoryAgentBench、Mem2ActBench、LightMem 反证、成本和最新研究见[基准与前沿](retrieval-context/03-benchmarks-cost-and-frontier.md)。

当 Agent 问“客户上次确认的交付日期是什么？”时，困难不是只在历史中找一段相似对话。系统还要排除其他客户的数据，区分旧日期和新日期，在冲突时保留不确定性，并把有限 token 用在足以支撑回答或工具调用的证据上。检索因此不只是向量数据库的 `top-k`：它是一条把记忆变成上下文和行动依据的读取链路。

本专题的边界是候选生成、筛选、排序、导航与上下文编译。写入时怎样抽取对象属于形成机制；版本替代和删除属于生命周期；模型怎样从上下文学习技能属于经验/技能机制。三者会在读取路径上相遇，但不能彼此替代。

## 为什么相似度检索不够

向量检索擅长处理同义改写，却通常不天然表达主体、权限、时间、版本、精确标识符和关系路径。关键词检索对订单号、函数名和罕见 token 很有用，但不擅长语义变体。图导航能把实体关系连接为多跳候选，却要付出建图和扩展成本。时间和版本过滤能避免过期事实，却要求写入时保留足够元数据。最后，即使候选正确，有限上下文也可能把关键原始片段压缩或截断掉。

独立复现材料还说明，检索器、检索深度和回答 token 预算足以改变结论：固定构造出的记忆，仅换一个检索器即可大幅改变结果；原始对话与压缩记忆的相对表现也会随深度和预算翻转。这不是否定结构化记忆，而是说明没有共同预算和输入构造的排行榜缺乏解释力。[v09 检索深度底稿](../../../agent-memory-v09/bundle/clusters/mm-c04-retrieval-ranking-active-navigation.md)

## 方案空间：不同路线在“候选从哪里来”上分工

| 方案族 | 核心机制 | 最能处理的信号 | 主要局限与成本 | 证据状态 |
|---|---|---|---|---|
| 词法 / 向量召回 | 关键词匹配、嵌入近邻或两者并用 | 精确 token、语义近邻、低延迟候选 | 时间、权限、冲突和多跳关系需外加机制 | 工程常见，混合检索较成熟 |
| 结构化与时间检索 | 先按实体、字段、作用域、有效时间和版本过滤 | “谁、何时、哪一版”的精确状态 | schema 与维护要求高；后过滤可能稀释合法候选 | 条件成熟，接口差异大 |
| 图或关系导航 | 从实体/关系图做邻居扩展、路径搜索或传播排序 | 多跳、关联追踪、跨事件联系 | 建图、更新和扩展预算；噪声会级联 | 活跃工程路线，普适收益未定 |
| 主动检索 | 根据首轮结果、计划或反馈再次改写查询、扩展或停止 | 长程任务中的信息缺口 | 额外模型/工具调用、循环和难归因 | 近一年活跃，独立复现不足 |
| 上下文编译 | 从候选中挑选原文、摘要、字段与冲突说明，分配 token | 预算有限且需可解释的输入 | 压缩可能丢失关键证据；不同编译策略难直接比较 | 必需工程层，统一算法尚未形成 |

这些不是互斥“产品类别”。同一个读取请求常经历硬过滤、多个候选路由、融合重排，再进入上下文编译。`Mem0` 的公开资料展示语义、关键词、实体和时间信号的组合；`A-MEM` 展示可调候选数与结构链接；`HippoRAG` 使用知识图与个性化 PageRank；`MemCon` 则把再次检索纳入在线决策。它们展示机制的存在与工程方向，所用数据、模型和预算却不同，不能据此排定赢家。[v09 方案与工程证据](../../../agent-memory-v09/bundle/clusters/mm-c04-retrieval-ranking-active-navigation.md)

## 五类读取路线到底怎样工作

### 1. 词法、向量与混合召回：建立低成本候选池

词法检索把 token 映射到倒排表，BM25 同时考虑词频、文档频率和长度，因而擅长函数名、订单号、错误码等精确项；向量检索把 query 与 memory object 映射到稠密空间，通过 ANN 找语义近邻。两者并行后可用 RRF、归一化加权或 cross-encoder reranker 合并。工程上还常加入 recency、importance 和 object type 作为独立 feature。

该路线的关键不是“top-k 取多少”一个参数。chunk/object 粒度决定索引单位，pre-filter 与 post-filter 决定合法候选是否在 ANN 截断前保留，fusion 决定罕见精确项是否被语义项淹没，reranker 又决定延迟和 token 开销。`Mem0` 与 `SimpleMem` 展示了不同 multi-route 组合；[LightMem 复现](https://arxiv.org/abs/2607.29104) 则提醒：仅换 retriever 与 matched depth 就可能反转 raw/constructed 的表面胜负。

### 2. 结构化和时间检索：先求合法状态，再谈相似度

结构化路线把 query 解析为 subject/tenant、object type、valid-time/as-of、revision status、purpose 和精确字段。SQL/DSL 先筛出当前或历史合法集合，再对其做词法或向量召回。若查询“去年 12 月项目负责人是谁”，resolver 不能直接返回最新 profile，而要选择该时间区间有效的 revision；若存在冲突，则上下文应携带两个版本及来源。

最常见的工程错误是后过滤：先对全库取 top-10，再删掉其他租户或旧版本，结果可能只剩一条；正确做法是让权限/时间进入候选生成或扩大取样并记录 dilution。时间检索的前沿在于 valid time 与 recorded time 联合解析、迟到证据、interval overlap，以及同一查询中 current/historical evidence 的组合。

### 3. 图与关系导航：从 seed 沿结构扩展证据

图导航先用关键词/embedding 找 seed entity、passage 或 fact，再沿 typed edge 扩展一至多跳。BFS/beam search 控制路径深度，Personalized PageRank 将 query seed 的概率沿图传播，spreading activation 则结合边权、衰减和节点新鲜度。最后仍要回填原始 source passage；图节点或路径只是候选和解释结构，不是事实证明。

[HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) 将 passage、entity、fact 连接并用 PPR 传播；`causal-memory` 组合 semantic/lexical 候选、RRF 和 activation；`A-MEM` 让历史链接随新 note 更新。这些实现适合多跳和关系问题，却容易受到 entity resolution、错误 hub、陈旧边和扩展预算影响。研究正在探索 query-conditioned edge selection、temporal graph traversal 和 graph+raw fallback，而非简单扩大邻居数量。

### 4. 主动检索与导航：把“证据够不够”放入控制循环

主动路线先生成 retrieval plan：查询需要哪类对象、哪些时间、是否要图/工具、停止条件是什么。首轮返回后，controller 估计 coverage 或 contradiction；若不足，改写 query、切换 route、沿实体继续查，或请求原始证据。`SimpleMem` 带有 intent-aware planning/reflective expansion，`MemCon` 将 retrieve 与 re-retrieve 视为策略动作，Letta/MemGPT 形态则让 Agent 自己调用 archival-memory tools。

它比 single-shot 能处理长程信息缺口，但每轮都增加 LLM/tool latency，并可能陷入循环或被不可信候选引导。可靠实现需要 hard budget、route trace、evidence sufficiency 判据与 abstention；评测也要把“第一次就找到”“通过几轮找到”“最终仍没有足够证据”分开。当前还缺跨 backend 的独立对照，无法确定 learned planner 的净收益有多少来自更多调用预算。

### 5. 上下文编译：把候选变成模型实际看见的证据

编译器接收带 source、revision、score components 和冲突状态的候选，先去重和 grouping，再在 token budget 内选择原文、结构化字段、摘要或 relation path。常见策略包括按对象配额、MMR 多样化、层级摘要、query-focused compression 和 source-span fallback。最终 prompt 不应只是拼接文本，还可显式表达“当前值”“已替代历史”“冲突未决”“来源”和“截断原因”。

编译失败常被错算成 retrieval 失败：索引已经找到正确证据，但摘要删掉了限定词，或预算分给多个冗余候选而漏掉原始片段。近期系统工作开始把 candidate budget 与 compiled-token budget 分开，并追踪 construction、retrieval、prompt assembly、generation 的成本。[系统表征研究](https://arxiv.org/abs/2606.06448) 显示不同 memory paradigm 会把工作负载搬到不同阶段，因此最终上下文短不等于系统整体便宜。

## 读取链路：授权不是排序后的注释

```text
查询 / 当前任务
      │  识别主体、目的、时间视图、风险与预算
      ▼
硬过滤 ──► 路由选择 ──► 各路候选 ──► 去重与重排 ──► 上下文编译 ──► 回答或工具行动
 scope       词法/向量      记录候选来源        相关性、时间、       原文、字段、
 time        实体/图/时间  与版本              权威性、冲突、成本   冲突和截断理由
 revoke
```

先做硬过滤意味着租户、用户、Agent、项目、目的、撤销状态和时间视图在语义检索前就缩小可见集合。原因很简单：模型在看到越权内容之后再被提示“不要使用”，不能视为可靠隔离。检索路径还需要保留每一路候选及其来源、版本和淘汰原因，才能回答“没找到”是索引漏召回、过滤正确排除、重排压低，还是上下文预算截断。

重排不只是把几个分数相加。相关性、时效性、来源权威性、冲突、风险和成本可能相互抵触；图扩展得到的候选与原始文本也需要去重和保留关系来源。上下文编译则是独立步骤：它决定给模型的是原始片段、结构化字段、摘要，还是“此处存在两个版本”的说明。把它隐藏在 `top-k` 后面，会掩盖检索成功但证据没有进入模型上下文的失败。

`scope-recall-hermes` 的固定版本工程检查给出了一个可观察形状：原始日志和耐久事实分开，以 SQLite 为权威状态，LanceDB、SQLite brute-force 或 PGVector 可作为可重建的伴随检索层，并融合词法、向量、图和新鲜度信号。该检查并未运行仓库，因而只能说明接口和数据流的表面，不能证明吞吐、恢复目标或真实采用。[v09 GitHub 雷达](../../../agent-memory-v09/bundle/reports/06-github-trend-radar.md)

## 当前主流与近期信号

在当前工程实践中，词法与向量混合、metadata filter 和有限的 rerank 是最容易见到的读取形状。实体、时间、版本与冲突成为重要查询条件的系统，正把这些条件前置到召回之前。近 12 个月的实质变化包括：更显式的 retrieval planning、结构链接与图导航、将读取纳入在线 memory-operation policy，以及把上下文压缩视为独立的质量与成本控制点。研究截止日前约 90 天的信号主要来自新评测和主动控制/安全边界的加密，而非一个已经公认取代混合检索的新范式。[v09 历史与因果报告](../../../agent-memory-v09/bundle/reports/04-history-and-causality.md)

成熟度不应由 star 或单次榜单决定。混合候选和过滤属于较成熟的工程手段；图导航在关系密集任务上有清晰动机，但建图和维护成本使其收益高度依赖任务；主动导航能表达“首轮不够时继续查”，却仍缺跨后端、匹配预算的独立净收益证据。可信检索——把授权、来源和撤销视为读路径的一部分——是明确的安全需求，但各实现的完整性边界仍需逐项检查。

## 最新研究议程：优化目标从 recall 转向 evidence-to-action

最近研究正在同时推进四层，而不是寻找单一新 retriever：

- **候选层**研究 multi-route、图/时间导航和 query-dependent k，目标是提高 source-span coverage，而不是只提高 embedding 相似度。
- **控制层**研究何时检索、换哪条 route、何时停止或 abstain；需要把额外调用预算和循环失败计入结果。
- **编译层**研究在固定 token 下保留最小充分证据、冲突和 provenance，并能回退到原文。
- **行动层**研究正确证据是否真的改变 tool selection、参数和后续状态；`Mem2ActBench`、`MemoryArena`、`LongMemEval-V2` 等正把评测从静态 QA 推向此处。

下一步最缺的是一个可拆阶段的共同 harness：同一权威记忆、同一模型和预算下，分别替换 flat hybrid、typed temporal、graph、active planner 和 compiler；同时报告 candidate oracle recall、source-span survival、compiled evidence、answer/tool outcome、延迟和总成本。没有这个实验，大家仍会把“索引更丰富”“prompt 更短”或“最终分数更高”误当成同一件事。

## 代价、失败与评测

读取成本至少包括查询理解、每种检索路由的 I/O 与计算、候选回填、去重融合、重排、图扩展、上下文 token、再次检索和追踪记录。写入侧还要分摊嵌入、索引版本和关系维护。因此，单独报告回答准确率或 token 数不足以描述读取代价。

失败可按阶段定位：原始信息在构造记忆时丢失；近似索引没有召回；权限或时间过滤位置错误；重排把陈旧或低权威项放在前面；编译器压掉关键原文；模型收到正确证据却没有据此行动；查询或观察文本诱导系统把不可信内容排到前面。不同失败需要不同修复，不能统称“检索不好”。

可比较的实验需要固定任务集与版本、历史构造、模型/Agent 包装、存储和检索实现、候选/上下文/工具预算、随机种子和 judge。`LoCoMo`、`LongMemEval` 主要覆盖长程对话；`MemoryAgentBench` 强调增量读写与遗忘；`Mem2ActBench` 与 `MemoryArena` 把记忆推到工具和后续行动。它们衡量的单位不同，应保留为不同协议族，而不是平均成一个“记忆分数”。[v09 基准地图](../../../agent-memory-v09/bundle/reports/07-benchmark-map.md)

## 共识、争议与未解问题

较稳定的判断是：预算和实验指纹会改变检索结论；作用域与时间应在模型看到内容前处理；候选生成、排序和上下文构造是不同阶段，应该能分别观察。仍有争议的是：压缩表示相对原始记录是否有普适优势，图导航在何种任务上值得其维护成本，融合公式和主动控制是否能跨后端泛化。

最关键的缺口是缺少把平面、混合、图、时间版本和主动导航放在同一记忆库、模型、候选/token/tool 预算和维护成本下的对照；也缺少跨系统的原始证据覆盖率、oracle 上界与行动成功追踪。没有这些证据，读者可以理解各路线解决的不同问题，却不能把不同论文或仓库中的分数直接比较。

**暂定判断：** 读取链路正在从“相似文本检索”演化为可分层、可追踪的证据构造过程。混合检索是当前成熟的基线形状；时间/关系路由和上下文编译的工程价值正在增加；主动导航仍属于值得关注但证据较弱的前沿信号。本判断描述现状，不提供选型建议。
