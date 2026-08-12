# 生命周期系统 walkthrough：修订、重建、遗忘在代码中落在哪里

本篇跟踪五种固定版本实现中的 lifecycle surface。它们分别强调 journal/outbox、bi-temporal history、fact update/history、FTS rebuild，以及 encrypted vault journal。代码存在不代表端到端删除或恢复已被运行验证。

## 1. scope-recall-hermes：promotion、outbox 与 repair state

scope-recall-hermes 的 journal 保存原始 turn，digest/candidate/promotion 形成 durable fact，SQLite transaction 写 truth/FTS/relations/freshness并 enqueue vector intent。生命周期特征包括：

- 未 promotion 的 candidate 不进入 active state；
- truth 与 vector companion 分开，outbox 可 replay；
- companion 失败标记 pending/needs_repair；
- scope、temporal、conflict 与 freshness 都进入 SQLite truth。

它展示 mutation 与 projection repair 的明确边界。尚未验证的是高并发下 outbox 顺序、跨 host、长期 checkpoint 与 delete propagation。

固定版本 `867b9939e037299befd930647a5015ee6e4945c0` 可把一次状态变化重建为：

```text
Hermes turn
  → journal receipt
  → digest / evidence packet
  → candidate ledger
  → review + promotion
  → SQLite truth / FTS / relation / freshness transaction
  → vector outbox
  → LanceDB | sqlite-vector | PGVector companion
```

关键点是 promotion 与 projection 两次边界。candidate 即使已经由模型抽出，也不等于 durable state；truth commit 成功后，vector replay 仍可能失败。后者被标成 `pending/needs_repair`，使“对象已成为事实”和“语义投影已经追上”可以分别观察。`general` scope 是本地 scratch，默认不进入 durable vector；`user/memory/project/ops` 才是耐久作用域。adapter 若丢失这一约束，会把暂态信息永久化或让应持久的信息只留在当前进程。

## 2. Engraphis：bi-temporal history、conflict/evolution/retention policy

Engraphis 的 MemoryEngine 协调 remember、conflict、evolution、retention、recall、context pack 与 privacy/audit。SQLite 保存 memory/history/FTS/graph/receipt，vector 与 code index作为投影。

一次 remember 经 scope/secret/provenance，再做 dedup/conflict/evolution；embedding fingerprint mismatch 会禁用 persistent vector recall直到 rebuild；review gate 可以让对象存在但暂不可读。这个实现把 lifecycle policy 放在 engine 内，而不是散落在调用方。

它仍有多索引部分成功和 backend fallback：vector 退回 NumPy 时性能/语义变化；review/policy 零结果可能被误诊为索引故障；bi-temporal 表存在不证明所有 adapter 按相同时间语义写入。

固定版本 `128fe0515b842923df871a777eaacc3327f40513` 中，MemoryService 的 CLI、MCP、REST 和 dashboard 共同进入 MemoryEngine；Engine 再调 conflict、evolution、retention 与 privacy/audit policy。一个 remember 的生命周期不是简单 upsert：

```text
scope/secret/provenance validation
  → dedup / conflict lookup
  → current + history mutation
  → FTS / graph / receipt
  → embedding + vector index
  → prompt eligibility / review state
```

embedding fingerprint 改变时，persistent vector recall 被 fail-closed，直到重建；这让模型迁移成为显式 lifecycle event。另一个边界是 sqlite-vec 与 SQLCipher 的 native library 冲突：auto 模式回退 NumPy，显式 sqlite-vec 配置则失败。后端迁移不仅改变速度，也改变加密与恢复路径。

## 3. Mem0：事实 mutation 与 history，但非统一多存储事务

Mem0 通过旧候选 + LLM decision执行 ADD/UPDATE/DELETE，并在 SQLite history记录变化。主 vector memory、history 与 entity collection 是不同责任层。

其生命周期优势是调用方能看到事实级 update/history，而不是只覆盖对话摘要。边界是：entity 更新 best-effort；不同 vector provider 的 delete/filter 能力不同；managed/OSS 语义需分开；历史存在不自动保证主向量、entity 与外部 cache 的恢复一致。

固定版本 `4debc58a83377b18be81ae1e5969a300736b2fac` 的 `add` 会先按 user/agent/run scope 找 existing memories，再由 LLM 对抽取事实决定 ADD、UPDATE、DELETE 或无操作。主对象写入 vector store，ADD/UPDATE/DELETE history 写入 SQLite，entity collection 独立 best-effort 更新：

```text
messages + scoped existing candidates
  → LLM fact / event decision
  → batch embeddings + vector mutation
  → SQLite history
  → optional entity links
```

这不是跨三层事务。LLM extraction 失败时 infer-add 不写事实；vector 成功后 history/entity 失败则可能出现可检索对象缺少审计或实体链接。provider 没有 `keyword_search` 时 hybrid BM25 被禁用，也意味着 backend migration 会改变读取语义，不能只验证 CRUD 返回码。

## 4. Sibyl：迁移与 FTS rebuild 的 local-first 生命周期

Sibyl client 负责 SQLite schema bootstrap、transaction、migration 与 FTS5 rebuild。base table 是权威，FTS shadow可以在启动/迁移时重建；MCP 暴露 forget/state/event 等 surface。

它的生命周期较传统数据库化：事务失败向上传播，索引缺失可重建。却没有跨主机共享、向量模型迁移或全链 purge 证据；forget tool 的存在不等于 backups/derived prompts 已清除。

固定版本 `e2241dbcff6840674d616c3ab3c1389ddf0c2f2d` 由五个 Python 包共享同一 schema family。Client 用 SQLite base table 保存每租户权威状态，FTS5 trigger/shadow 负责词法访问；MCP/Hermes/LangGraph/CLI 只是接入面。启动或迁移可以检查并重建“形状正确但内容为空”的 FTS shadow。这个机制解决索引修复，却不回答 summary、prompt 或其他进程副本的撤销。

SQLite 需要 JSON1/FTS5，默认数据库和凭据在 `~/.sibyl-memory`；因此它的 transaction/rebuild 语义停在单机文件边界。多进程写超过 busy timeout 时事务失败向上传播，没有证据支持跨主机协调。

## 5. Compartment：vault journal、lock/unlock 与 model hash

Compartment 把解锁后的 SQLite 放在 RAM，record text/vector分别加密，再将整个 database image封装进 AEAD journal。生命周期不仅是对象变化，还包括 lock/unlock、keyslot、journal seal、backup 与 re-embed。

- model hash mismatch：拒绝打开或要求显式 re-embed，避免混合空间；
- journal/auth failure：vault不可用，恢复依赖 journal/backup；
- foreign-write reload race：旧 image 可能覆盖新 journal 或产生 stale read；
- purge：需要同时处理加密 records、vectors、journal history 与 key material。

本地加密降低云暴露，却把恢复、密钥和宿主内存安全纳入 lifecycle；未经过独立安全审计或生产恢复演练。

固定版本 `3053e289eac7438ff8f58be17eb6b66bf57ff6e3` 的更完整链路是：

```text
MCP/hook memory
  → bundled ONNX embedding windows
  → record-key encryption of text/vector
  → RAM-only SQLite records/FTS/relations/audit
  → serialize database image
  → XChaCha20-Poly1305 sealed vault journal
```

vault 记录 embedding model SHA-256；不匹配时拒绝打开，需显式 `reindex --re-embed`，防止混合向量空间。小库做 exact SIMD，超过阈值才可选 HNSW。所有查询在解锁后的 RAM 中运行，所以容量直接影响 RSS 与重载时间；宿主 OS 完全失陷时，内存中的明文和 key material 仍可能暴露。

`forget` 的物理效果要放在 journal/backup 语义中理解：即使当前 image 没有 record，旧 journal segment、备份或 keyslot 如何处理仍需单独验证。foreign-write reload race 还可能让旧 image 覆盖新 journal 或短暂读到 stale state。

## 6. 五种生命周期形状对照

| 系统 | mutation 单位 | history/receipt | projection repair | forget/delete 表面 | 主要边界 |
|---|---|---|---|---|---|
| scope-recall-hermes | candidate→durable fact | journal + transaction | outbox/pending/needs_repair | lifecycle/scope primitives | 跨 host/并发未验证 |
| Engraphis | memory revision/conflict | bi-temporal history + receipt | fingerprint rebuild | retention/review/privacy | 多索引/backend fallback |
| Mem0 | consolidated fact | SQLite ADD/UPDATE/DELETE history | side stores best-effort | API delete/update | provider capability drift |
| Sibyl | SQLite row/tier | DB transaction/events | FTS rebuild | MCP forget/state | 单机、派生删除未知 |
| Compartment | encrypted record/vault image | audit + AEAD journal | re-embed/reload | MCP forget/lock | key/journal/OS boundary |

## 7. 工程代码还没有回答的共同问题

这些实现展示了 lifecycle surface，却没有共同证明：一次 correction 是否使所有 prompt/cache/skill停止使用旧值；一次 purge 是否穿过 backup；恢复后 current/history/index是否一致；多个 writer 的 conflict如何合并；learned policy 能否在真实系统中安全调用这些 primitive。

下一篇[删除、修复与研究前沿](03-deletion-repair-and-frontier.md)聚焦这些未闭环问题。

## 8. 怎样比较 lifecycle 实现而不把 API 动词当语义

对每个固定版本，至少需要重放同一序列：

```text
add(v1) → retrieve(v1) → update(v2) → conflict(v2b)
        → supersede(v3) → hide/revoke → purge → crash → restore
```

每一步分别检查 canonical current/history、FTS/vector/graph、receipt、cache/context、action premise 和 backup。若某实现没有该 primitive，就记录“不适用/未提供”，而不是用 `delete` 猜测。这样才能比较的是状态合同，而不是函数名数量。
