# 多后端一致性、恢复与研究前沿：Memory 数据库仍缺什么

Agent Memory 正在吸收数据库、搜索、图和文件系统的成熟原语，但“把这些后端组合起来”并没有自动生成可靠 Memory。困难集中在 canonical revision、派生投影、作用域、模型版本和行动状态如何共同恢复。本篇用失败场景解释一致性边界，并说明近期研究为什么开始讨论 transaction 和 state trajectory。

## 1. 多存储写入的四种策略

### 1.1 单事务同库

canonical rows、history 与 FTS 都在同一 SQLite/Postgres 事务中。原子性强、恢复简单，embedding/外部图等仍可能在事务外。适合 local-first 或规模较小的 typed store。

### 1.2 Synchronous dual write

一次请求同步写数据库与向量/图/对象存储。延迟高，任一路失败需要 rollback 或 compensation；许多外部服务不支持共同事务，最终仍可能部分成功。

### 1.3 Transactional outbox

canonical transaction 同时写 mutation 与 outbox intent，后台 worker 将 intent 应用到 projection并记录 watermark。它接受短暂 stale，换来可重放和诊断。scope-recall-hermes 是这一工程形状的例子。

### 1.4 Event sourcing / journal rebuild

不可变事件/receipt 是事实底座，current state 和索引全部由 replay 构建。恢复能力强，代价是 replay、snapshot、schema evolution 与敏感历史保留。MemTxn 的 durable snapshot journal和多种 journal-first实现属于这一方向。

## 2. 一致性不是只有 strong/eventual 两种标签

Memory 需要分别说明：

- canonical current 是否 read-after-write；
- history/revision 是否原子可见；
- FTS/vector/graph 是否允许 lag；
- deletion/revocation 是否允许旧投影暂时返回；
- action 是否可以消费 stale revision；
- backup/restore 后外部 projection 如何对齐。

普通搜索可以容忍几秒索引延迟，高风险工具行动可能不能消费旧权限或旧配置。因而 consistency 应按对象与动作分类，而不是给整个系统贴一个 eventual 标签。

## 3. 六个必须故障注入的场景

### 3.1 Canonical commit 成功、embedding 失败

对象 current view 已更新，semantic search 仍返回旧版本。需要 outbox retry、watermark 与 lexical/authoritative fallback；不能静默声称写入完全成功。

### 3.2 Graph/relationship 部分更新

节点已新建，部分 edge 缺失或旧 edge 未撤销。多跳结果可能比 flat search 更错误，因为 traversal 放大不完整结构。

### 3.3 Embedding model 或 dimension 迁移中断

新旧向量混在同一索引，score 不可比较。应使用 generation/fingerprint，双索引迁移或全量 rebuild，并在切换前验证 coverage。

### 3.4 Delete 后旧 snapshot 回灌

对象在 live store 已 purge，恢复旧备份后重新出现。需要 deletion ledger、backup retention 与 restore-time tombstone replay；仅删除当前数据库不足。

### 3.5 Scope metadata 丢失

payload 与 vector 仍在，tenant/principal filter 无法重建。系统宁可隔离/拒绝，也不能将 unknown scope 当 global。

### 3.6 WAL/segment/DB 恢复后投影不一致

进程可启动，但 FTS、HNSW、cache、graph 和 current pointer覆盖不同 revision。恢复验收必须运行 object/history/query/action probe，而不只检查文件可打开。

## 4. 为什么 revision、fingerprint 和 watermark 是三种不同标识

- **revision** 标识业务状态版本；
- **fingerprint** 标识生成投影的模型、schema、模板或算法；
- **watermark** 标识某个投影已经处理到哪个 revision/event。

例如 profile v12 可以同时有 embedding-generation-3 和 summary-generation-5；向量 watermark 到 v12，graph watermark 只到 v10。没有三者分离，系统无法决定该重算什么，也无法解释不同查询为何看到不同状态。

## 5. 删除与恢复的矛盾

为了可靠恢复，系统倾向保存 append log 和 snapshot；为了隐私删除，系统又需要消除内容与派生物。解决方案通常只能明确 policy 边界，而非让两者都无限成立：

- envelope encryption + key destruction 降低历史内容可恢复性；
- tombstone/forget ledger 保留最小不可逆删除事实；
- snapshot 有 retention window，restore 后重放删除；
- derived index 按 object/revision lineage 定向失效；
- audit receipt 保留操作而非敏感 payload。

公开实现对这一完整链的验证仍很少。搜索不到某条内容不证明 backup、summary、cache 和技能都已清除。

## 6. 成本模型：复杂底座把成本分散到生命周期

应同时记录：

```text
storage = raw + canonical revisions + indexes + snapshots + audit
write = transaction + extraction + embedding + graph/index fan-out
read = route I/O + ANN/BM25/graph + rerank + hydration
maintain = compaction + reindex + migration + backup + repair
recover = replay + rebuild + validation + downtime
```

HNSW 内存和写成本、图维护、bitemporal history、raw artifact、encrypted journal都可能让一个查询看似快而总生命周期昂贵。当前缺少同 workload、同 hardware、同模型的全链成本账本，因此不能给底座做统一性价比排名。

## 7. 负面证据如何限制复杂表示

[LightMem 独立复现](https://arxiv.org/abs/2607.29104)表明，固定 store 下仅改变 retriever 和 candidate depth 就足以显著改变结果；matched depth 下 raw-turn baseline 常更强。这意味着 constructed/indexed memory 的表面优势可能来自更多候选或不同 token budget。

[双时间图存储](https://arxiv.org/abs/2607.26520)的小样本同时呈现 update 增益与 temporal reasoning 下降，作者将部分下降归因于 post-filter dilution。它说明更明确的时间模型仍可能因访问算法失效。

反证并不否定 revision、scope 或 source lineage，而是要求复杂底座在相同 protocol 下证明它保留了必要 evidence，并将 maintenance cost 纳入比较。

## 8. 最新研究正在把“数据库正确”提升为“轨迹正确”

[GEM/MemState](https://arxiv.org/abs/2605.26252)提出 memory state `(D,S,P)`：content、typed structure 与 declarative policy共同组成状态，ingestion/revision/forgetting/retrieval 是状态级 operator；[MemTxn](https://arxiv.org/abs/2607.27834)强调 source-supported transaction 与 complete-state recovery；双时间研究强调 history/as-of；ForgetEval 将 recall 与 mutation operation 分开。

共同变化是正确性不再只检查某行或某次 query，而是检查：

1. operation 前置条件是否成立；
2. canonical state 和 dependency 怎样变化；
3. projection/compiled context是否追上；
4. action 是否消费允许的 revision；
5. repair/forget 是否使未来轨迹满足不变量。

这些方向仍是预印本、原型或分散实现，没有一个经过跨后端 conformance 和故障演练的通用 Memory database contract。

## 9. 决定性实验应长什么样

一套底座对照应固定 raw inputs、object schema、extractor、embedding/ranker、candidate/compiled budget、reader 和硬件，并运行：

- insert/update/conflict/late arrival；
- current/history/as-of；
- lexical/semantic/relation queries；
- concurrent writes 与 crash points；
- partial projection failure；
- embedding/schema migration；
- forget/purge + snapshot restore；
- source-span recall、action outcome；
- p50/p95、bytes/revision、write amplification、rebuild/recovery time。

对照至少包含 flat raw/FTS、vector/hybrid、typed relational、graph/bitemporal和组合方案。只有这样，才能判断复杂表示解决的是任务语义，还是用更多 construction 和维护换来更宽候选。

## 10. 当前可以形成的成熟度判断

SQL transaction、WAL、FTS、ANN、object storage 等原语本身成熟；local-first SQLite + FTS、Postgres + pgvector 和搜索 engine作为底座也有大量工程经验。中等成熟的是多对象、多索引和 provider abstraction。仍早期的是跨后端 transaction、bitemporal/graph 的 matched net benefit、完整派生删除、统一 recovery/conformance，以及 trajectory-level database contract。

回到短入口：[表示、存储与索引](../03-representation-storage-indexing.md)。候选怎样被检索并编译，见[检索与上下文构造](../05-retrieval-and-context.md)。
