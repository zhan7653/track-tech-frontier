# 候选生成、排序与导航：一次 Memory 查询究竟怎样跑完

“从记忆中找出答案”在实现里至少包含七个不同问题：当前请求属于谁、问的是哪个时间切面、哪些对象有资格进入候选集、要走哪些索引、多个结果怎样融合、还要不要继续查，以及最终哪些证据真的进入模型上下文。只写一句“做向量检索”会把这七层全部折叠掉。

本篇从一条读取请求出发，拆开 query plan、硬过滤、候选生成、图与时间导航、融合重排、停止控制和上下文编译。下一篇会把同一链路落实到固定版本仓库；第三篇讨论评测、成本和最新研究缺口。

## 1. 读取请求先被编译成 query plan

自然语言 query 不是足够稳定的存储接口。读取层通常先构造一个显式计划：

```text
QueryPlan {
  principal: user_42,
  tenant: acme,
  agent: coding-agent,
  purpose: answer | plan | tool-call,
  object_types: [fact, decision, episode, procedure],
  time_view: current | as_of(t) | interval(a,b),
  revision_policy: current_only | include_conflicts | history,
  routes: [lexical, dense, entity, graph],
  candidate_budget: 80,
  context_budget: 2400 tokens,
  risk_mode: evidence_required,
  stop_rule: sufficient_sources_or_budget
}
```

其中 principal、tenant、purpose 和 revoke state 是安全过滤；object type、时间和版本决定语义；routes 与 candidate budget 控制召回；context budget 控制模型实际看见的内容。把这些参数留在 free-form prompt 中，系统便无法解释某条记忆为什么可见、为什么被排除，也无法稳定复现实验。

查询解析可以是规则、分类器或 LLM，但后续合法性校验不应由同一个生成模型自由决定。例如模型可以提出“查询项目决策和最近失败”，实际执行器仍需依据当前身份、许可目的和时间视图约束数据面。

## 2. 硬过滤必须发生在内容暴露之前

硬过滤常包含：

- tenant、user、agent、team、workspace、repository 和 session；
- private/shared/public visibility；
- allowed purpose 与数据类别；
- active/superseded/revoked/purged 状态；
- current、as-of 或 interval 时间视图；
- 对高风险对象的 approval/promotion state。

如果系统先从全库取向量 top-10，再删除其他租户的结果，合法集合可能被非法近邻挤出，形成 **filter dilution**。更重要的是，某些向量服务或 reranker 已经看到了越权内容。成熟实现会把可表达的过滤条件下推到 SQL、vector payload filter 或独立命名空间；无法下推时扩大候选预算，并记录 pre/post-filter 数量与内容暴露边界。

时间过滤还要区分 occurred time、valid time 与 recorded time。“去年十二月负责人是谁”需要 as-of resolver，而“最近得知负责人变更”可能按 recorded time 排序。只给对象一个 `updated_at` 无法同时回答这两类问题。

## 3. 词法召回：精确符号并不落后

倒排索引记录 term 到 object/chunk 的 posting。BM25 的常见形式是：

```text
score(q,d) = Σ IDF(t) * tf(t,d) * (k1 + 1)
                         / (tf(t,d) + k1*(1-b+b*|d|/avgdl))
```

IDF 提高罕见词权重，长度归一避免长日志天然占优。错误码、commit、函数名、工单号、配置键和人名常由词法路线首先命中。工程难点包括 tokenizer、camelCase/snake_case 切分、语言归一、字段 boost、对象更新后的 FTS shadow 同步，以及长文档拆分后如何回到权威对象。

Memory 里的 BM25 往往不是全文搜索终点，而是一个 route。返回项至少要携带 object/revision/source 和匹配字段；否则后续融合只能处理无身份文本片段。

## 4. 稠密召回：相似度背后的四个版本契约

稠密路线将 query 和对象投影为向量，再做 exact scan 或 ANN。真正的工程契约不只包括模型名，还包括：

1. embedding provider 与 model revision；
2. 预处理和对象文本模板；
3. dimension、distance metric 与归一化；
4. 索引构建参数和更新 watermark。

HNSW 通过多层邻接图做近似搜索，查询从稀疏高层下降到密集底层；`M`、`efConstruction` 和 `efSearch` 在内存、构建时间、查询延迟和 recall 之间取舍。IVF 先把向量分桶，查询只扫描若干 centroid 邻域；数据分布变化后需要重训或重建。小型本地系统也会直接 NumPy exact scan，以可预测性换规模上限。

embedding fingerprint 变化而旧索引未重建时，向量仍有正确维数却不再可比，这比显式报错更危险。Engraphis 的固定版本实现因此将 fingerprint 不明或改变视为 fail-closed 条件，而不是静默混用空间。

## 5. 混合融合：不要把不可比的原始分数直接相加

词法、向量、实体和图 route 的分数分布不同。常见融合有三类：

### 5.1 Reciprocal Rank Fusion

```text
RRF(d) = Σ_route 1 / (k + rank_route(d))
```

它只依赖排名，不要求不同 route 的分数校准，适合工程基线。缺点是 route 数量、候选截断和固定 `k` 都会影响结果；同源重复对象若未先 canonicalize，会因多次出现被放大。

### 5.2 分数归一与加权

对每路做 min-max、z-score 或学习校准后，组合 relevance、recency、authority、confidence、importance。它能显式表达目标，却容易受 query 内候选分布和尾部异常值影响。

### 5.3 Cascade / rerank

低成本 route 先取较大候选集，cross-encoder 或 LLM 只重排 top-N。它把高质量判断集中在小集合，但增加模型延迟，并可能在候选阶段已经漏掉正确证据。

融合前应按 canonical object/revision 去重，保留每一路的 rank 和 score component。冲突对象不能因文本相似被合成一条流畅摘要；它们应作为带来源的不同 revision 进入编译层。

## 6. 图导航：先找 seed，再控制扩展

图路线通常不是“把全库跑一次图算法”。常见过程是：

```text
query
  → lexical/dense seed entities or facts
  → typed-edge expansion
  → path/activation scoring
  → source-span hydration
  → fusion with flat candidates
```

BFS 提供完整的固定深度邻域，但分支因子会指数增长；beam search 只保留得分最高的部分路径；Personalized PageRank 以 seed distribution 重启：

```text
p_(t+1) = α s + (1-α) Pᵀ p_t
```

其中 `s` 是 query seed，`P` 是转移矩阵。Spreading activation 还会把 edge type、time decay、positive/negative outcome 和 hop penalty 放入传播。Causal Memory 的实现同时维护事实与 decision→outcome edge，先分路检索，再以 RRF 汇合并可做 typed activation；这比“建一个知识图”具体得多。

图路线最常见的失败不是算法不会跑，而是 entity resolution 错误、hub 节点聚集无关路径、陈旧 edge 未随 supersede 修复，以及路径看似合理却没有回填原始 source。图是候选结构，不是事实本身。

## 7. 主动检索：将读取改成受预算约束的控制循环

Single-shot retrieval 假设第一次 query 已经表达完整需求。主动检索会在首轮后评估：是否覆盖必要实体/时间、是否存在相互矛盾的版本、是否只有派生摘要没有原文、是否足以支撑行动。若不足，controller 可以：

- 改写 query 或拆成子问题；
- 切换 lexical/vector/entity/graph route；
- 沿已知实体、时间或 provenance 继续导航；
- 请求 canonical object 或 source span；
- 扩大候选或上下文预算；
- 在预算耗尽时 abstain。

一个可审计循环形如：

```text
state_t = {question, plan, candidates, conflicts, coverage, budget}
action_t ∈ {search(route), expand(node), hydrate(source), rerank, stop, abstain}
```

MemCon 把 retrieve、plan injection、re-retrieve、consolidate、forget 和 no-op 纳入在线策略；这说明读取已开始与控制面结合。可比实验必须计入多出来的 LLM/tool calls，否则 learned planner 的收益可能只是预算更高。

## 8. 上下文编译：候选命中不等于证据进入模型

编译器把候选转成有限 token 的输入。典型步骤是：

1. canonical 去重与 revision grouping；
2. 将冲突、current/history 和 provenance 明确标注；
3. 按 object type、source 与 route 做多样性配额；
4. 在原文、结构字段、摘要和关系路径之间选择表示；
5. 计算 token，必要时 query-focused compression；
6. 保留回退到原始 source span 的 locator；
7. 输出 included/excluded/truncated receipt。

MMR 可在相关性与多样性之间取舍：

```text
argmax_d λ·sim(d,q) - (1-λ)·max_{s∈selected} sim(d,s)
```

但它不理解来源权威、版本冲突或行动风险，这些仍要独立建模。最小充分证据也不是最短摘要：删除“仅限测试环境”“截至某日期”等限定词，可能让 token 更少、结论更错。

## 9. 可观察读路径应留下哪些中间量

要判断失败发生在哪一层，至少需要：

- query plan 与身份/时间/权限过滤；
- 每条 route 的查询、候选数、版本和耗时；
- pre-filter、post-filter、去重和融合结果；
- graph path、hop、edge type 与 source hydration；
- reranker 输入/输出和模型版本；
- candidate token、compiled token、截断原因；
- 最终被回答或工具调用实际引用的对象；
- 是否触发 re-retrieve、stop 或 abstain。

这套 trace 让“权威对象根本没写入”“索引漏召回”“过滤位置错误”“重排压低”“编译删掉”和“模型没使用正确证据”成为不同故障，而不是统一记为 accuracy 下降。

接着看[固定版本工程 walkthrough](02-system-walkthroughs.md)，再看[基准、成本与研究前沿](03-benchmarks-cost-and-frontier.md)。
