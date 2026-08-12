# 写入系统 walkthrough：五种工程管线怎样把输入变成长期状态

这一组 walkthrough 不比较“谁最好”，而是选取五种结构明显不同的固定版本实现：facade 式事实合并、journal-first 事务管线、typed causal distillation、统一文件树抽取、以及多索引 Memory engine。重点是逐步跟踪一次写入，而不是复述 README 功能。

## 1. Mem0：检索旧事实后由模型决定 ADD/UPDATE/DELETE

[Mem0 固定版本报告](../../projects/mem0ai--mem0.md)显示，OSS Python orchestration 由 LLM、embedder、vector store、可选 reranker、SQLite history 和独立 entity store 组成。

### 1.1 一次 `add` 的主要步骤

```text
messages + user/agent/run parameters
  → normalize messages and bind identity filters
  → embed conversation / retrieve existing memories
  → LLM extracts candidate facts
  → LLM or orchestration decides ADD/UPDATE/DELETE/NOOP
  → batch embed and write main vector collection
  → append SQLite history
  → best-effort update entity collection
```

身份只从调用参数进入，并剥离 metadata 中可能伪造 identity 的字段。旧候选参与 mutation decision，因此 retriever 漏召回会制造重复事实，错召回会诱发错误更新。主 vector、history 和 entity 并非一个事务：entity 更新失败时主 memory 仍可见；部分路径只 warning 后继续。

### 1.2 这个实现真正说明什么

它说明 consolidation fact store 已是现实工程模式：写入不是简单 insert，而是 candidate retrieval + extraction + mutation。它也说明 provider facade 会带来 capability drift：某些 backend 支持 keyword/hybrid，另一些退化为 semantic；managed platform 的额外优化不能归因给固定 OSS SHA。未执行的代码检查无法证明长期更新正确率或生产一致性。

## 2. scope-recall-hermes：journal-first、promotion 与可重建 companion

[scope-recall-hermes 的固定提交报告](../../../../agent-memory-v09/bundle/projects/410979729-scope-recall-hermes.md)把原始 turn 与 durable facts 分开。SQLite 是权威 truth，LanceDB、SQLite vector 或 PGVector 是可重建 companion。

### 2.1 写入管线

```text
Hermes hooks
  → journal capture + secret/scope filters
  → digest / evidence packet
  → candidate proposal
  → review / promotion
  → SQLite transaction: truth + FTS + relations + freshness
  → enqueue vector outbox intent
  → companion replay
```

与 Mem0 不同，它把“捕获”和“晋升”为两个可观察阶段。journal 可以保留尚未成为 durable memory 的证据；promotion 决定候选是否生效；vector outbox 允许权威写成功后异步修复语义索引。

### 2.2 失败与修复

vector companion 落后时，系统标记 pending/needs_repair；scope 错误会造成跨 chat/agent 召回或 scratch 被永久化；SQLite contention 可能使事务 rollback，而 outbox 需要重放。这个形状比直接 dual-write 更容易解释部分失败，但仍没有跨进程负载、恢复演练或第三方部署证据。

## 3. Causal Memory：从 session log 蒸馏 facts 与 decision→outcome edges

[Causal Memory 工程报告](../../projects/jingxuanc--causal-memory.md)展示一个 Rust/MCP 系统：raw session logs、atomic facts 与 causal edges 共存于 SQLite。写时 gatekeeping 隔开原文与召回层，distill/consolidation 形成可用对象。

### 3.1 形成步骤

```text
session or MCP direct write
  → session_logs / typed input
  → per-session LLM distill
  → classify facts + causal edges
  → write agent_facts / causal_edges
  → update BM25 + optional embedding
  → retire superseded fact before writing new value
```

distill 失败时，raw logs 保留且 session 不写 done marker，因此可以重试。这个设计的优点是失败单位明确：capture 成功不等于 fact materialization 成功。读取再将 fact/causal 层的 BM25、semantic、entity-hop/trace 候选用 RRF 合并。

### 3.2 特有风险

一次 session 的 LLM distill 可能错误归因 decision 与 outcome；跨任务 meta-edge 可能把表面相似的失败类比为可复用规律；embedding backend 不可用时 semantic 通道消失。这说明“形成因果记忆”要求的不只是关系抽取，还要有可验证 outcome 和反例。

## 4. OpenViking：资源解析、层级语义生成与 session commit

[OpenViking](../../projects/volcengine--openviking.md)的形成管线有两条入口：资源 ingestion 与 session commit。前者把 PDF/Markdown/HTML/代码等解析成目录；后者将消息归档后抽取 self、peer 和 experience memory。

### 4.1 Resource formation

```text
file / URL / resource
  → Parser
  → TreeBuilder writes AGFS hierarchy
  → SemanticQueue bottom-up processing
  → L0 detail / L1 summary / L2 overview
  → URI + vector + metadata index
```

### 4.2 Session formation

```text
session messages
  → archive
  → SessionCompressorV2
  → schema-based self / peer / experience objects
  → AGFS path + semantic representations
```

它把 summary 形成与文件树结构结合，读时可以逐层展开。但异步 SemanticQueue 会让内容先存在、索引后就绪；peer routing 错误会写入错误主体；统一资源/memory/skill namespace 也不自动赋予三者相同的更新语义。

## 5. Engraphis：一个多控制点、可回执的 Memory engine

[Engraphis 工程页](../../projects/coding-dev-tools--engraphis.md)以 MemoryService 统一 CLI/MCP/REST/dashboard ingress，MemoryEngine 组合 Store、embedder、vector、reranker、conflict/retention/graph policies。

### 5.1 写入数据流

```text
remember/import
  → service validates scope, secret, provenance
  → MemoryEngine performs embedding, dedup, conflict, evolution
  → SQLite writes memory/history/FTS/graph/receipt
  → vector backend upsert
  → code index incrementally updates symbols/edges by content hash
```

一个 SQLite 文件保存 records、FTS、bi-temporal history、layered graph/code links 与 hashed receipts；向量可用 NumPy exact scan 或 sqlite-vec。相比纯 facade，这个实现把 conflict/evolution/retention 和 receipt 放入同一 engine；相比 journal-first，它的多投影更密集，embedding fingerprint mismatch 会直接禁用 persistent vector recall，直到一致 rebuild。

### 5.2 形成与 review gate

scope/review gate 可能让对象存在但召回为空；native backend 冲突可能自动退回 NumPy 或启动失败。它说明控制面可以进入本地 engine，但静态代码存在不代表这些 gate、bi-temporal history 和 recovery 已在生产负载中共同验证。

## 6. 五条管线为何不可压成同一个 `add()`

| 系统 | 原始证据层 | 形成器 | mutation/admission | 权威状态 | 派生物/部分失败 |
|---|---|---|---|---|---|
| Mem0 | messages/session context | LLM facts | candidate-based ADD/UPDATE/DELETE | vector memory + history | entity best-effort、provider drift |
| scope-recall-hermes | journal | digest/candidate | review/promotion + transaction | SQLite truth | vector outbox 可 repair |
| Causal Memory | session_logs | per-session distill | gate + retire/write | SQLite facts/causal edges | embedding optional、done marker retry |
| OpenViking | AGFS resource/session archive | parser/tree/compressor | schema/routing | AGFS tree | async semantic queue lag |
| Engraphis | import/remember receipt | engine policies | secret/scope/conflict/evolution/review | SQLite memory/history/graph | vector fingerprint/rebuild |

这些差异会改变故障恢复和评测：Mem0 需要检查 mutation decision 与 side-store 一致性；journal-first 管线要检查 promotion 与 outbox lag；Causal Memory 要检查 distill/edge precision；OpenViking 要检查层级语义 queue；Engraphis 要检查 policy gate 与多索引 rebuild。用同一 QA 分数无法定位它们的形成失败。

## 7. 论文机制如何补充这些工程形状

工程代码常展示“怎样跑”，论文则更明确地提出“为什么这样形成”：

- Generative Agents：observation importance 与 reflection，展示高层概念如何从事件形成；
- MemoryBank：conversation、event summary、user assessment 并存，展示形成对象并非单一摘要；
- A-MEM：新 note 到来时构建结构属性和动态历史链接；
- Hindsight：world facts、experiences、entity summaries、beliefs 分层；
- SimpleMem：滑动窗口生成 semantic、lexical、structured views；
- MemTxn：source-supported proposal 与 durable commit；
- MemCon：让策略在线选择形成/管理 operator。

尚没有一个公开实现把这些机制放在相同后端、相同输入和相同预算下独立比较。项目 walkthrough 的作用不是宣布成熟路线，而是把论文里的 formation concept 映射到真实组件和故障点。

## 8. 形成系统仍缺哪些共同接口

不同实现若要互相比较，至少需要共同暴露：capture receipt、candidate/source span、formation model/prompt、related-old candidates、mutation decision、committed revision、projection watermark、cost trace 和 failure/retry state。当前 SDK 多只返回生成后的 memory ID，导致形成误差被隐藏在一个成功响应里。

继续阅读[形成失败、成本与前沿](03-cost-security-and-frontier.md)，理解为什么“抽取得更多”不等于长期状态更好，以及当前研究正在补哪些实验。
