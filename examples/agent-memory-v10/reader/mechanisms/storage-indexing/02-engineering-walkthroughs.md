# 存储与索引工程 walkthrough：七种底座如何组合权威状态与访问面

本篇选取七种固定版本实现，覆盖 local-first SQLite、搜索引擎、typed causal store、虚拟文件系统、多索引 engine、加密 vault 和 Postgres memory backend。它们展示的不是功能清单，而是权威状态、派生索引和恢复边界的不同安排。

## 1. Sibyl：SQLite base tables + FTS5 shadow

Sibyl client 以 per-tenant SQLite 保存 schema、事务与迁移，FTS5 trigger/rebuild 维护词法 shadow；MCP/Hermes/LangGraph/CLI 都接入同一 client。

```text
remember
  → tenant/category validation
  → SQLite transaction/base table
  → FTS5 trigger or rebuild
  → search/list/recall
```

base rows 是权威，FTS 为空或形状错误时启动逻辑可 rebuild。这个设计简单、可本地部署，也使“对象存在但搜索漏召回”可诊断。边界是 SQLite 写锁、单机共享、无 semantic vector，以及 untrusted content 只靠返回 fence 提醒下游。

## 2. xerj：WAL/segment + BM25/HNSW 的通用搜索 substrate

[xerj 固定提交](../../../../agent-memory-v09/bundle/projects/xerj-org-xerj.md)用 Axum HTTP/Elasticsearch-compatible handlers解析 DSL，engine 协调 WAL、sharded memtables、immutable segments、BM25 与 persistent HNSW/exact vector。

```text
PUT/bulk
  → append WAL + memtable
  → background flush/segment
  → merge/compaction

search DSL
  → memtable + segments
  → BM25 / HNSW / exact scan / aggregation
  → merged JSON result
```

它展示成熟搜索原语怎样成为 Memory 的候选层，却没有定义 Agent object、revision、scope 或 lifecycle。ES compatibility 也只是子集，协议迁移可能在 query/aggregation semantics 上漂移。README benchmark 未复跑，不能据其数字做性能结论。

## 3. Causal Memory：同一 SQLite 中的日志、facts、causal edges 与多路检索

Causal Memory 将 session_logs、agent_facts、causal_edges、BM25 和 optional embedding 放进一个本地骨架。distill 生成 facts/edges；更新会 retire 旧 fact；读时分别检索 fact/causal 的 lexical、semantic、entity-hop/trace，再以 RRF 融合。

它比普通向量库多了 typed causal state 与 retry marker，也仍有 projection 边界：embedding backend 不可用时 semantic 通道消失；跨任务 meta-edge 可能放大错误类比；SQLite 中关系一致不等于 causal extraction 正确。

## 4. OpenViking：AGFS 权威内容 + URI/vector metadata index

OpenViking 的 AGFS 保存完整资源、多媒体和 relations，向量索引只保存 URI、vector 和 metadata。SemanticQueue 自底向上生成 L0/L1/L2，HierarchicalRetriever 按 intent 在目录中导航、rerank，再回 AGFS hydrate 内容。

这种分离避免把完整文档复制进向量库，也支持人工浏览。部分失败很明确：内容先写入、semantic queue 后完成；索引 URI 可能 stale；tree move 和 peer routing 会改变对象位置。系统需要 queue/watermark 和 repair 才能知道“存在但未可搜”。

## 5. Engraphis：SQLite history/FTS/graph + 可替换向量 backend

Engraphis 的 MemoryEngine 在一个 SQLite 文件中保存 memories、FTS、bi-temporal history、layered graph/code links 与 receipt；vector 默认 NumPy exact scan，可选 sqlite-vec。读时融合 lexical/vector/graph/code，并在 hard token budget 下打包。

它的关键机制是 embedding fingerprint：模型空间不一致时 persistent vector recall 被禁用，直到一致 rebuild。native backend 冲突可自动退回或显式失败；scope/review gate 也可能让数据存在但结果为空。它展示“零结果”需要区分 policy、index 和 data 三类原因。

## 6. Compartment：RAM SQLite + encrypted journal + local embedding

[Compartment](../../projects/maxfreedompollard--compartment.md)是本地加密 vault。解锁后只在 RAM 打开 SQLite，records、FTS5、relations、audit、vectors 都在内存；每条 text/vector 加密，整个数据库 image 再序列化到 AEAD journal。bundled BGE-small ONNX 在 CPU 生成 384-d vectors；小规模 exact scan，超过阈值可用 HNSW；查询将 vector 与 BM25 做 RRF。

```text
capture
 → local embedding windows
 → per-record encryption
 → RAM SQLite + FTS/vector/audit
 → serialize & seal vault journal
```

这个形状把隐私与存储底座绑定，避免必需云服务，但模型 hash mismatch 会拒绝打开或要求 re-embed；journal auth failure 使整个 memory 不可用；宿主 OS 被攻破时 RAM plaintext/master material 仍可能暴露。加密保证不是完整端点安全。

## 7. AtomicMemory：Postgres/pgvector canonical objects 与外部 raw artifact

[AtomicMemory 固定版本](../../../../agent-memory-v09/bundle/projects/atomicstrata-atomicmemory.md)的 TypeScript/Rust monorepo以 Postgres/pgvector 为 Core。MemoryService 注入 episode/memory/claim/entity/link/lesson/raw-content stores；ingest 形成 canonical objects、representations 和 lineage；search 融合 vector/keyword/entity/temporal/contradiction signals。SDK、MCP、CLI 与多个 Agent framework adapter 复用 backend。

外部 S3/Filecoin/IPFS-style raw storage由 registry/reconciler 管理，因此 metadata/object truth 与 raw artifact 仍可能分歧；canonical write 也可能只完成部分 derived network。这个实现接近 typed memory database，但 Core 依赖 Postgres/pgvector，package matrix 包含 deprecated 或未发布表面；仓库未执行，不能把架构完整性当成运行保证。

## 8. 七种底座的对照

| 系统 | 权威层 | 词法 | 向量 | 图/时间 | 恢复/修复边界 |
|---|---|---|---|---|---|
| Sibyl | SQLite base tables | FTS5 | 无 | tiers/state | FTS rebuild；单机锁 |
| xerj | WAL/memtable/segments | BM25 | HNSW/exact | aggregation | WAL replay/segment merge；不含 Memory schema |
| Causal Memory | SQLite logs/facts/edges | BM25 | optional | causal graph | distill retry；embedding 降级 |
| OpenViking | AGFS URI/tree | hierarchy | metadata index | relations/tree | async queue/URI divergence |
| Engraphis | SQLite memory/history | FTS | NumPy/sqlite-vec | bitemporal/layered graph | fingerprint rebuild/policy gate |
| Compartment | encrypted RAM SQLite image | FTS5 | exact/HNSW | relations/audit | AEAD journal/model hash |
| AtomicMemory | Postgres canonical stores | keyword | pgvector | entity/link/temporal | DB/raw artifact reconcile |

这里没有“最佳底座”。它们针对本地性、吞吐、typed state、层级资源、安全或生态接入做了不同取舍。真正的比较必须匹配 object schema、write/update/delete workload、candidate budget 和 recovery fault，而不能拿 README feature 或单一 ANN latency 排名。

## 9. 工程实现反复暴露的共同问题

1. **source of truth 不清**：向量、history、graph 和 raw artifact 各自成功；
2. **fingerprint 漂移**：embedding/schema/ranker 版本混用；
3. **scope 只在 adapter**：换入口后隔离语义变化；
4. **delete 只删一层**：历史、索引、备份或外部 artifact 遗留；
5. **零结果不可诊断**：对象不存在、scope/policy 拒绝、索引 stale 被混在一起；
6. **恢复只测启动**：没有验证 current/history/index/action 重新一致。

这些共同问题构成下一篇[一致性、恢复与研究前沿](03-consistency-recovery-and-frontier.md)的主线。
