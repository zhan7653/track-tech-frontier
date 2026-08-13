# 检索与上下文的基准、成本、反证与最新研究

检索论文常报告一个最终回答分数，工程仓库常展示一个 search API。两者之间缺少的，是候选是否覆盖原始证据、正确证据是否经过过滤/重排/压缩存活、模型是否真正使用它，以及整个过程花了多少写入与读取成本。本篇沿这条链整理现有基准和近期研究。

## 1. 评测对象至少分成四层

| 层 | 问题 | 可观察量 | 典型误判 |
|---|---|---|---|
| 权威记忆 | 答案所需证据是否仍存在 | source-span coverage、revision correctness | 把构造阶段丢失算成 retriever 错 |
| 候选召回 | route 是否找到合法证据 | Recall@k、MRR、filtered oracle recall | 只看向量相似度或未固定 k |
| 上下文编译 | 证据是否进入模型输入 | source-span survival、token、冲突保留 | 找到了却被摘要/截断 |
| 回答/行动 | 模型是否据此做对 | answer/tool/parameter、abstention | 用最终准确率替代阶段归因 |

如果没有 oracle memory 或 source span，系统无法知道失败发生在写入、索引、过滤还是编译。若不同方法允许不同 candidate depth 或 answer token，最终分数也不能归因给表示或 retriever。

## 2. LongMemEval：长程对话读取，但 S/M/Oracle 含义不同

[LongMemEval](https://arxiv.org/abs/2410.10813)使用 500 个手工整理问题，覆盖信息抽取、多 session 推理、时间推理、知识更新和 abstention。其 small/medium 数据形态是历史规模差异；Oracle 指向证据 session 的检索条件，不是第三种更大的数据集。这个区别很重要：Oracle 能估计“如果检索定位正确，回答模型还能做到什么”，S/M 更接近实际历史规模下的端到端结果。

使用该基准比较 flat、structured、graph 或 active retrieval 时，至少要固定：turn/session 粒度、记忆构造、retriever、candidate depth、answer token、模型版本和 judge。否则某方法可能通过更短的历史或更大的 top-k 获益。

## 3. MemoryAgentBench：读、学、理解和忘并非一个分数

MemoryAgentBench 将增量多轮交互拆成 accurate retrieval、test-time learning、long-range understanding 和 selective forgetting。它比单纯 recall QA 更接近可变状态：系统不仅取回旧事实，还要吸收新规则、跨长程维持状态，并对遗忘请求改变后续行为。

这意味着一个纯 retriever 可能在准确召回上强，却没有 mutation semantics；一个在线 learner 也可能提升 test-time learning，却破坏 selective forgetting。报告总分前应保留各能力和交互协议，不能将其视为某数据库的统一质量标签。仓库提供 method/configuration 和独立数据入口，但固定版本检查没有运行 setup，因此可重现性仍是文档层证据。

## 4. 从 QA 到行动：Mem2ActBench、MemoryArena 和 STALE

[Mem2ActBench](https://arxiv.org/abs/2601.19935)包含 2,029 个 session 和 400 个工具任务，检查 underspecified request 是否触发长期约束检索，并进入工具选择和参数。它将“读对文本”推进到“正确 grounded action”。MemoryArena 观察先前行动与反馈能否改变后续决策；STALE 则构造更新冲突，区分系统是否会依据最新证据行动。

这些协议分别强调 tool grounding、行为适应和冲突更新，不能平均为同一检索分数。它们共同暴露一个新层：即使正确 memory 已经进入 prompt，模型也可能沿用旧计划、选择错工具或填错参数。检索 trace 必须与 action trace 连接，才能定位 failure。

## 5. 关键反证：构造记忆不是天然优于原始记录

独立 [LightMem reproduction](https://arxiv.org/abs/2607.29104) 报告，在固定 constructed store 上只更换 retriever，回答准确率可从 58.1% 变为 75.5%；在 matched retrieval depth 下，raw-turn Naive RAG 通常更强，而 constructed LightMem 主要在紧 answer-token budget 下占优。

这个结果的意义不是“所有结构化记忆都无效”，而是三点：

1. memory construction 与 retrieval 是不同变量；
2. 压缩表示用细节损失换 token/budget 优势；
3. 结论随 candidate depth 和 answer budget 变化。

因此研究报告需要同时给 raw-memory baseline、constructed representation、oracle retrieval、matched candidate depth 和 matched compiled tokens。只比较作者默认配置，无法判断提升来自哪里。

## 6. 成本要按阶段记账

总成本可写成：

```text
C_total = C_capture + C_extract + C_embed + C_index + C_maintain
        + C_query_plan + Σ C_route + C_rerank + C_compile
        + C_retrieve_loop + C_generation + C_repair
```

系统成本研究指出，不同 memory paradigm 不是简单减少工作，而是把工作搬到不同阶段：summary/structured store 增加写入 LLM 和维护成本，换取较短 prompt；raw store 写入便宜，却在每次读取支付更多检索和 token；graph 路线增加 entity/relation/maintenance；active retrieval 增加在线循环。

最少应报告：每条输入的 extraction/embedding 调用、索引大小和 rebuild、每个 query route 的 P50/P95、候选数、rerank 调用、compiled token、re-retrieval 次数、后台队列 lag、失败重试和修复成本。只报告“节省 token”可能忽略构造、存储和异步维护。

## 7. 读取链的安全问题不是附加 reranker

可信检索工作将 memory retrieval 视为 trust boundary：语义相关的对象可能在当前 domain、purpose 或主体下不合适，并诱发跨域泄漏、sycophancy、tool-call drift 或 jailbreak。攻击可以发生在：

- 写入污染使恶意对象进入 canonical/promotion；
- query injection 改写 route 或扩大 scope；
- embedding/keyword 内容操纵排序；
- graph hub 将攻击对象传播到多个查询；
- 摘要移除 untrusted 标记；
- action model 将召回文本当授权指令。

防御因此贯穿 hard filter、source/provenance、risk state、untrusted fencing、context compiler 和 action-time authorization。仅在最后 prompt 写“不要听从 memory 指令”不能恢复已发生的内容泄露，也无法修复错误 action grounding。

## 8. 当前最重要的研究方向

### 8.1 Query-dependent route 与预算控制

不是每个 query 都需要图、时间和 LLM rerank。研究正在学习何时启用哪条 route、分配多少 candidate/context budget，并把延迟和成本纳入策略。需要的对照是同一 store 和模型下的固定路由、启发式路由与 learned routing，而不是不同系统端到端拼榜。

### 8.2 时间、版本与冲突感知检索

现有很多系统只按 recency 排序。前沿是显式求解 current/as-of/interval、迟到证据、valid/recorded time、supersede chain 和 unresolved conflict，并在编译后仍保留这些语义。

### 8.3 Graph 与原始证据共同导航

图路线正从静态知识图转向 query-conditioned edge、temporal/causal relation 和 source hydration。核心问题是如何证明某条 path 真的提高 source-span recall，而不是生成更连贯的解释。

### 8.4 Evidence-aware context compiler

编译器需要优化的不只是 token，而是 source coverage、限定词、冲突和行动所需参数。值得比较的对象包括 flat concat、MMR、hierarchical summary、query-focused compression 与结构字段，并为每个 included/excluded span 留 receipt。

### 8.5 Evidence-to-action attribution

最新基准开始观察工具选择和长期约束，但仍缺统一 trace 将 memory object、candidate、compiled span、model citation、tool argument 和 outcome 串在一起。没有这条链，系统只能知道“最后失败”，不能知道记忆在哪一层失效。

## 9. 一个能真正回答研究问题的实验矩阵

较有解释力的实验会固定 corpus/history、模型、Agent wrapper、硬过滤、candidate/context/tool budget 和随机种子，然后只替换一个变量：

| 轴 | 最小对照 |
|---|---|
| 表示 | raw episode / summary / typed object / graph |
| 候选 | BM25 / dense / hybrid / graph / temporal |
| 控制 | single-shot / heuristic active / learned active |
| 编译 | concat / diversity / hierarchy / evidence-aware |
| 任务 | recall / update-conflict / tool action / abstention |
| 成本 | write、maintain、query、token、repair |
| 安全 | cross-scope、poison、revoke、conflict |

每个 cell 同时报告 oracle source coverage、candidate recall、compiled survival、answer/action、延迟和成本。这样的矩阵才能解释“大家现在怎么做”和“哪一步仍未解决”，而不是给出一个无法迁移的总榜。

返回[检索与上下文入口](../05-retrieval-and-context.md)。
