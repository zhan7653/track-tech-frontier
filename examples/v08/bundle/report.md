# AI Agent Memory 技术前沿纠错快照（截至 2026-08-10）

<!-- section:executive -->

## 执行结论

截至2026-08-10，AI Agent Memory 不是单一“记忆库”，而是覆盖持久状态、写入提取、检索装配、更新压缩、遗忘与安全控制的系统问题。<!-- claim:C001 --> [系统表征研究](https://arxiv.org/abs/2606.06448)；[learned memory control](https://arxiv.org/abs/2607.13591)

MemoryAgentBench 把记忆评测从静态长上下文改成了信息逐块注入的增量多轮交互。<!-- claim:C002 --> [论文](https://arxiv.org/abs/2507.05257)；[官方仓库](https://github.com/HUST-AI-HYZ/MemoryAgentBench)

Mem2ActBench 把记忆评测从回答问题扩展到依据历史状态选择工具并补全调用参数。<!-- claim:C003 --> [ACL 论文](https://aclanthology.org/2026.acl-long.370/)；[官方仓库](https://github.com/Cantaloupe-M/Mem2ActBench)

2026年的系统研究开始把构建、检索、生成、存储与网络成本纳入 Agent Memory 的受控比较。<!-- claim:C004 --> [系统表征预印本](https://arxiv.org/abs/2606.06448)；[独立成本研究](https://arxiv.org/abs/2601.07978)

持久记忆把不可信输入变成可长期复用状态，因此一次恶意写入可以持续影响后续代理行为。<!-- claim:C010 --> [memory poisoning 原始研究](https://arxiv.org/abs/2606.04329)

<!-- section:scope-method -->

## 范围与方法

本报告是 schema 1.7 full-profile update，topic 与截至日继承 v07，时间重点为2024—2026并回看2023关键谱系；第一次查询前冻结16项需求，按 Map、Focus、Verify 三轮执行20条可重放查询，69个候选中保留53个、非保留16个，最终核验45个来源、19张论文卡、13张仓库卡与0条执行记录。paper 与 GitHub 双 lane 逐 claim 建 evidence join 与 semantic check；survey S001 仅以 T2 地图使用，产品状态只取官方发布/文档，独立采用搜索没有用 stars 或 vendor 自述替代部署证据。本轮没有第四轮，也没有安装或运行大型仓库。<!-- process:method -->

<!-- section:field-map -->

## 领域地图：从记忆类型到 write–manage–read 生命周期

LongMemEval 的500个问题覆盖信息提取、多会话推理、知识更新、时间推理与拒答五种能力。<!-- claim:C005 --> [论文](https://arxiv.org/abs/2410.10813)

MemoryAgentBench 将能力划分为准确检索、测试时学习、长程理解与冲突消解四类。<!-- claim:C006 --> [论文](https://arxiv.org/abs/2507.05257)

LangGraph 的 checkpointer 保存线程内图状态，Store 保存跨线程的应用自定义长期数据。<!-- claim:C007 --> [官方 persistence 文档](https://docs.langchain.com/oss/python/langgraph/persistence)；[canonical repo](https://github.com/langchain-ai/langgraph)

LangMem 在存储层之上提供热路径记忆工具和后台提取、合并、更新管理器。<!-- claim:C008 --> [canonical repo](https://github.com/langchain-ai/langmem)

MemCon 把检索、计划注入、重检索、合并、遗忘与不操作建模为在线策略可选动作。<!-- claim:C009 --> [预印本](https://arxiv.org/abs/2607.13591)；[官方仓库](https://github.com/ericjiang18/MemCon)

<!-- section:evolution -->

## 关键谱系与2024—2026演进

Generative Agents 在2023年的25-agent沙盒中把 memory stream、reflection 与 planning 连接成可观察的记忆架构。<!-- claim:C011 --> [论文](https://arxiv.org/abs/2304.03442)；[代码](https://github.com/joonspk-research/generative_agents)

MemGPT 在2023年用类似操作系统的分层存储与上下文换页来管理超出上下文窗口的状态。<!-- claim:C012 --> [论文](https://arxiv.org/abs/2310.08560)；[代码演进](https://github.com/letta-ai/letta)

Reflexion 在2023年把自然语言反馈保存在 episodic memory 中并用于后续试次。<!-- claim:C013 --> [NeurIPS 论文](https://papers.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)；[代码](https://github.com/noahshinn/reflexion)

MemCon 在2026年把固定启发式 memory access 改写为依据任务反馈学习的控制策略问题。<!-- claim:C014 --> [预印本](https://arxiv.org/abs/2607.13591)

LongMemEval-V2 在2026年把长期记忆评测进一步扩展到需要浏览器操作的 Web agent 轨迹。<!-- claim:C015 --> [预印本](https://arxiv.org/abs/2605.12493)

<!-- section:landscape -->

## 统一维度 landscape 对照

| 共同维度原子结论：任务/机制、证据等级、代码成熟度、适用边界与最强限制 | 直接证据 |
|---|---|
| LongMemEval 以 ICLR 2025 论文、官方仓库和单独登记的 Hugging Face 数据集来源提供多会话问答评测；其代码安装仅有文档、未发现 CI，且 S、M、Oracle 三种条件不能混作同一上下文预算。<!-- claim:C016 --> | [论文](https://arxiv.org/abs/2410.10813)；[仓库](https://github.com/xiaowu0162/LongMemEval)；[数据集](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned) |
| MemoryAgentBench 以 ICLR 2026 论文、官方仓库和 Hugging Face 数据集覆盖检索、测试时学习、长程理解与冲突消解；仓库安装有文档但没有 CI，且不同任务使用不同指标。<!-- claim:C017 --> | [论文](https://arxiv.org/abs/2507.05257)；[仓库](https://github.com/HUST-AI-HYZ/MemoryAgentBench)；[数据集](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench) |
| Mem2ActBench 以 ACL 2026 论文、官方代码与数据目录测试从长期记忆补全工具参数；仓库安装有文档但没有 CI，且自动合成任务不能直接代表生产工具流量。<!-- claim:C018 --> | [论文](https://aclanthology.org/2026.acl-long.370/)；[仓库](https://github.com/Cantaloupe-M/Mem2ActBench)；[数据目录](https://github.com/Cantaloupe-M/Mem2ActBench/tree/main/Mem2ActBench) |
| MemCon 以2026年预印本和官方仓库把检索、计划注入、重检索、合并与遗忘建模为在线控制动作；仓库安装有文档但没有 CI，且所有收益均为作者报告。<!-- claim:C019 --> | [预印本](https://arxiv.org/abs/2607.13591)；[仓库](https://github.com/ericjiang18/MemCon) |
| Agent Memory 系统表征论文在两个 benchmark suites 上剖析十个系统的构建、检索与生成阶段；它提供系统成本视角，但目前是未独立复现的预印本且没有已核验代码仓。<!-- claim:C020 --> | [预印本](https://arxiv.org/abs/2606.06448)；[代码检索账本](bundle://queries.jsonl) |
| IEEE COMPSAC 2026 接收稿在 LoCoMo 云边模拟中比较 Mem0、Graphiti、Cognee、RAG 与 full-context；它是独立受控对照，但结论只适用于该版本、网络约束与成本模型。<!-- claim:C021 --> | [接收稿](https://arxiv.org/abs/2601.07978)；[LoCoMo artifact](https://github.com/snap-research/locomo) |

<!-- section:deep-analysis -->

## 机制、成本与系统权衡

该系统表征研究使用 phase-aware harness，在两个 benchmark suites 上测量十个系统的写路径、读路径与生成阶段。<!-- claim:C022 --> [实验设计](https://arxiv.org/abs/2606.06448)

在该 LoCoMo 云边模拟中，Mem0、RAG 与 full-context 的准确率为77%至81%，Graphiti 与 Cognee 为55%至56%。<!-- claim:C023 --> [独立受控研究](https://arxiv.org/abs/2601.07978)

在同一 LoCoMo 云边模拟中，RAG 的总拥有成本比 Mem0 低8.4倍，且两者是该实验 Pareto 前沿上的两个非支配后端。<!-- claim:C024 --> [独立受控研究](https://arxiv.org/abs/2601.07978)

MemCon 作者报告其在六个 benchmark、三个 agent framework 与三个 LLM backbone 上将任务成功率最多提高15.2个百分点。<!-- claim:C025 --> [作者预印本](https://arxiv.org/abs/2607.13591)

MemCon 作者报告同一实验组合中的 token 消耗下降5%至20%。<!-- claim:C026 --> [作者预印本](https://arxiv.org/abs/2607.13591)

不同论文若没有固定相同的数据修订、模型、prompt、retrieval budget、judge 与硬件，就不能按公开分数直接排名。<!-- claim:C027 --> [独立成本对照](https://arxiv.org/abs/2601.07978)；[Mem2ActBench 协议](https://aclanthology.org/2026.acl-long.370/)

长期运行的成本模型应分别记录写入构建、检索装配、最终生成、存储维护与网络传输，而不能只报生成 token。<!-- claim:C028 --> [系统阶段分解](https://arxiv.org/abs/2606.06448)；[云边成本模型](https://arxiv.org/abs/2601.07978)

<!-- section:benchmarks -->

## Benchmark、数据版本与证据质量

LongMemEval_S 约为115k tokens和约40个历史会话，LongMemEval_M 约为500个历史会话，而 Oracle 仅给出证据会话。<!-- claim:C029 --> [论文](https://arxiv.org/abs/2410.10813)；[官方仓库](https://github.com/xiaowu0162/LongMemEval)；[cleaned 数据集](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned)

MemoryAgentBench 的任务指标混合使用 substring exact match、exact match、Recall@5 与 LLM-as-judge。<!-- claim:C030 --> [论文](https://arxiv.org/abs/2507.05257)

Mem2ActBench 由2,029个平均约12轮的会话生成400个工具任务，人工评估判定其中91.3%强依赖记忆。<!-- claim:C031 --> [ACL 论文](https://aclanthology.org/2026.acl-long.370/)；[公开数据目录](https://github.com/Cantaloupe-M/Mem2ActBench/tree/main/Mem2ActBench)

GroupMemBench 中最强系统平均准确率为46.0%，而简单 BM25 与多数 agent memory 系统持平或更好。<!-- claim:C032 --> [预印本](https://arxiv.org/abs/2605.14498)

LoCoMo 官方仓库固定提交发布的 locomo10.json 是一个十段对话、2.68 MB 的评测数据文件。<!-- claim:C033 --> [固定数据文件](https://github.com/snap-research/locomo/blob/main/data/locomo10.json)

LongMemEval 的 cleaned 数据集替代原始版本并移除了会干扰答案正确性的噪声历史会话。<!-- claim:C034 --> [官方仓库说明](https://github.com/xiaowu0162/LongMemEval)；[cleaned 数据集](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned)

benchmark 结论只有在数据版本、输入历史、模型、记忆写入过程、检索预算、判分器与失败处理一致时才可比较。<!-- claim:C035 --> [LongMemEval 协议](https://arxiv.org/abs/2410.10813)；[MemoryAgentBench 协议](https://arxiv.org/abs/2507.05257)；[Mem2ActBench 协议](https://aclanthology.org/2026.acl-long.370/)

<!-- section:implementation -->

## 实现、仓库与产品现实

截至2026-08-10，Mem0 固定提交4debc58提供安装文档且存在 GitHub Actions，但本轮没有执行安装或测试。<!-- claim:C036 --> [canonical repo](https://github.com/mem0ai/mem0)

截至2026-08-10，Graphiti 固定提交425bf24提供安装文档且存在 GitHub Actions，但本轮没有执行安装或测试。<!-- claim:C037 --> [canonical repo](https://github.com/getzep/graphiti)

截至2026-08-10，MemoryAgentBench 固定提交455306d提供安装文档，但没有 GitHub Actions、tagged release 或本轮执行记录。<!-- claim:C038 --> [canonical repo](https://github.com/HUST-AI-HYZ/MemoryAgentBench)

截至2026-08-10，Mem2ActBench 固定提交b007269提供安装文档，但没有 GitHub Actions、tagged release 或本轮执行记录。<!-- claim:C039 --> [canonical repo](https://github.com/Cantaloupe-M/Mem2ActBench)

截至2026-08-10，LangMem 与 LangGraph 的固定提交均有安装文档和 GitHub Actions，但本轮都没有执行 setup 或 tests。<!-- claim:C040 --> [LangMem](https://github.com/langchain-ai/langmem)；[LangGraph](https://github.com/langchain-ai/langgraph)

在本次三轮公开检索的有界范围内，没有找到同时披露部署版本、流量规模和故障数据、且可由第三方独立核验的 Agent Memory 生产案例。<!-- claim:C041 --> [冻结查询账本](bundle://queries.jsonl)；[候选漏斗](bundle://candidates.jsonl)

Google 的2025-12-16 release note 将 Vertex AI Agent Engine Sessions 与 Memory Bank 标为 GA，并写明2026-01-28开始计费。<!-- claim:C042 --> [Google 官方 release notes](https://docs.cloud.google.com/vertex-ai/docs/release-notes)

AWS 的官方 release note 将 Amazon Bedrock AgentCore 平台标为2025年10月在九个区域 GA。<!-- claim:C043 --> [AWS AgentCore release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html)

Bedrock Agents Classic 自2026-07-30起不再向新客户开放并进入 maintenance mode，AWS 建议新开发与迁移评估 AgentCore。<!-- claim:C044 --> [AWS Classic maintenance 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html)

AgentCore Memory 的 STRICTLY_CONSISTENT 元数据每个 strategy 最多三个键；这不是 indexed keys 每个 memory 最多十个键的上限。<!-- claim:C045 --> [AWS structured metadata 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/long-term-memory-metadata.html)

截至2026-08-10，Microsoft Foundry Agent Service 的 Memory 与 Memory Store API 仍是 public preview。<!-- claim:C046 --> [Microsoft 官方文档](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-memory?view=foundry)

Microsoft Foundry Memory preview 提供 item-level CRUD、store-level 默认 TTL 与直接 remember-or-forget 命令。<!-- claim:C047 --> [Microsoft 官方文档](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-memory?view=foundry)

<!-- section:negative-open -->

## 反证、安全、隐私与开放问题

MEXTRA Table 1 的静态条件是每个 agent 的 memory 含200条记录，并使用30个 attacking prompts。<!-- claim:C048 --> [ACL 论文](https://aclanthology.org/2025.acl-long.1227/)；[官方仓库](https://github.com/wangbo9719/MEXTRA)

在 MEXTRA 的该条件下，EHRAgent 的 extracted number 为50，retrieved number 为55。<!-- claim:C049 --> [ACL 论文 Table 1](https://aclanthology.org/2025.acl-long.1227/)

在 MEXTRA 的该条件下，RAP 的 extracted number 为26，retrieved number 为27。<!-- claim:C050 --> [ACL 论文 Table 1](https://aclanthology.org/2025.acl-long.1227/)

memory poisoning 研究表明，单次 adversarial memory write 可以在多个后续交互中持续施加影响。<!-- claim:C051 --> [原始攻击研究](https://arxiv.org/abs/2606.04329)

同一 poisoning 研究发现，写入和检索记忆更激进的 agent 更容易被利用。<!-- claim:C052 --> [原始攻击研究](https://arxiv.org/abs/2606.04329)

experience-following 实验观察到错误经验会传播，而过时或不相关经验会造成 misaligned replay。<!-- claim:C053 --> [ACL 论文](https://aclanthology.org/2026.acl-long.27/)

在该 experience-following 实验中，选择性 addition 与 deletion 相比 naive memory growth 带来平均绝对10%的性能增益。<!-- claim:C054 --> [ACL 论文](https://aclanthology.org/2026.acl-long.27/)

本次有界检索没有找到能证明删除原始记忆会自动清除其摘要、embedding 邻域、图关系、cache 与工具 transcript 的可靠实证。<!-- claim:C055 --> [冻结查询账本](bundle://queries.jsonl)；[候选漏斗](bundle://candidates.jsonl)

Microsoft 的官方指南要求对进入和离开 memory system 的内容做 prompt-injection 检查，并定期进行对抗测试。<!-- claim:C056 --> [Microsoft 安全指南](https://learn.microsoft.com/en-us/security/zero-trust/sfi/manage-agentic-memory-safety)

STALE 将过时记忆识别定义为独立能力缺口，说明“能检索”不等于“知道记忆何时失效”。<!-- claim:C057 --> [STALE 预印本](https://arxiv.org/abs/2605.06527)

<!-- section:outlook -->

## 未来12—24个月：有界预测

未来12至24个月，learned memory control 最可能先作为现有 memory backend 的策略层落地，而不是取代所有存储实现。<!-- claim:C058 --> [MemCon 信号](https://arxiv.org/abs/2607.13591)；[系统分层信号](https://arxiv.org/abs/2606.06448)

未来12至24个月，能否把历史状态正确落到 tool arguments 将成为比纯问答 recall 更重要的 memory gate。<!-- claim:C059 --> [Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)

未来12至24个月，poisoning、隐私抽取、陈旧记忆与可验证遗忘将更可能与准确率一起进入 memory evaluation。<!-- claim:C060 --> [poisoning](https://arxiv.org/abs/2606.04329)；[隐私抽取](https://aclanthology.org/2025.acl-long.1227/)；[陈旧记忆](https://arxiv.org/abs/2605.06527)；[官方安全治理](https://learn.microsoft.com/en-us/security/zero-trust/sfi/manage-agentic-memory-safety)

<!-- section:practical -->

## 技术负责人的内部评测与采用门槛

内部评测必须先冻结任务、数据版本、模型、prompt、写入顺序、retrieval budget、judge 与随机种子。<!-- claim:C061 --> [LongMemEval](https://arxiv.org/abs/2410.10813)；[Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)

内部指标应把问答正确性、memory recall、时间一致性与 tool-argument grounding 分开报告。<!-- claim:C062 --> [LongMemEval](https://arxiv.org/abs/2410.10813)；[MemoryAgentBench](https://arxiv.org/abs/2507.05257)；[Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)

内部系统指标应分别报告构建时延、检索时延、端到端 p50/p95、token、存储增量、网络流量与失败恢复。<!-- claim:C063 --> [系统表征研究](https://arxiv.org/abs/2606.06448)；[独立成本研究](https://arxiv.org/abs/2601.07978)

安全回归应至少覆盖 MEXTRA 式 extraction、poisoning、越权检索、过期冲突与删除后再检索。<!-- claim:C064 --> [MEXTRA](https://aclanthology.org/2025.acl-long.1227/)；[poisoning](https://arxiv.org/abs/2606.04329)；[STALE](https://arxiv.org/abs/2605.06527)；[Microsoft 安全指南](https://learn.microsoft.com/en-us/security/zero-trust/sfi/manage-agentic-memory-safety)

是否进入试点应由本地无记忆、长上下文、BM25/RAG 与目标 memory backend 的同条件对照决定，不能照搬外部论文阈值。<!-- claim:C065 --> [独立成本/准确率对照](https://arxiv.org/abs/2601.07978)；[GroupMemBench 反证](https://arxiv.org/abs/2605.14498)；[Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)

在没有独立部署证据时，stars、vendor customer names、CI 存在与 README 的 production-ready 表述都不能单独证明生产成熟度。<!-- claim:C066 --> [有界采用检索](bundle://queries.jsonl)；[Mem0 repo](https://github.com/mem0ai/mem0)；[Graphiti repo](https://github.com/getzep/graphiti)

<!-- section:limitations-sources -->

## 研究限制、明确缺口与来源附录

本次快照仍保留五类真实缺口：没有统一公开协议同时测长期写入、删除传播、存储增长与故障恢复；没有实证证明删除原始记忆会自动清理所有派生 artifact；没有同时披露版本、规模与故障数据的第三方生产案例；BM25/简单 RAG 的局部反证不能外推为所有 single-session 或权威状态场景都无需 memory；三项12—24个月预测都不是已发生事实，若公开产品和 benchmark 没有转向 learned control、tool grounding 以及安全/删除联合指标，预测应被削弱或推翻。仓库检查只读 README、代码、release 与 CI 元数据，因此 setup 仅记 documented、CI 仅记 present 或 missing，executions.jsonl 为空；未声明 license、无 release、affiliation unverified 与独立 adoption 缺失均诚实保留。<!-- process:limitation -->

来源按用途分层：T2 survey 只作[领域地图](https://arxiv.org/abs/2512.13564)；关键历史取[Generative Agents](https://arxiv.org/abs/2304.03442)、[MemGPT](https://arxiv.org/abs/2310.08560)与[Reflexion](https://papers.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)原始论文；benchmark 取[LongMemEval](https://arxiv.org/abs/2410.10813)、[MemoryAgentBench](https://arxiv.org/abs/2507.05257)、[Mem2ActBench](https://aclanthology.org/2026.acl-long.370/)、[GroupMemBench](https://arxiv.org/abs/2605.14498)及其 canonical code/data；系统与成本取[Agent Memory characterization](https://arxiv.org/abs/2606.06448)和[COMPSAC 2026 接收稿](https://arxiv.org/abs/2601.07978)；负面证据取[MEXTRA](https://aclanthology.org/2025.acl-long.1227/)、[experience-following](https://aclanthology.org/2026.acl-long.27/)、[STALE](https://arxiv.org/abs/2605.06527)与[poisoning](https://arxiv.org/abs/2606.04329)；产品状态取[Google](https://docs.cloud.google.com/vertex-ai/docs/release-notes)、[AWS](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html)、[Microsoft](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-memory?view=foundry)和[LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence)一手材料。完整45源 manifest、逐轮 queries/candidates、19张 paper cards、13张 repo cards、66条 claims、177条 evidence joins 与66条 semantic checks 保存在同一 bundle。<!-- process:source-list -->
