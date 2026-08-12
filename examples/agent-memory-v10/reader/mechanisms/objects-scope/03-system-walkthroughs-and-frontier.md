# 对象与作用域的现实实现：六种系统形状和它们没有解决的部分

论文常用 episodic、semantic、procedural 等术语描述对象；工程系统却必须把这些语义落到数据库表、文件树、API 参数、索引和 prompt 组装中。本篇选取六种差异足够大的固定版本工程形状，逐一回答：它保存哪些对象，作用域在哪里强制，写入与读取怎样流动，以及哪些保证仍然看不见。

这些项目不是排名。v09 没有执行其安装、迁移、恢复或 benchmark；代码检查只能证明固定提交中存在的组件和路径，不能证明性能、生产采用或端到端正确性。

## 1. MineEcho：一个应用内部同时存在四套“记忆”

[MineEcho 的固定提交工程报告](../../../../agent-memory-v09/bundle/projects/health-yang-mineecho.md)显示，它不是独立 Memory SDK，而是个人助手应用。BFF 同时维护：

- working memory：当前 prompt 组装所需状态；
- SQLite short-term：interactions、preferences、tasks、daily summaries；
- file-based long-term profile 与 L0–L3 memory tree；
- knowledge-base：raw/wiki/chunks、vector、graph 与 LightRAG 通道。

### 1.1 数据流

```text
chat / task / meeting
   → BFF memory routes
   → ShortTermDb(interaction / preference / task / summary)
   → dream/background review
   → long-term profile 或 L0–L3 tree
   → semantic/importance/recency + knowledge channels
   → chat context
```

这个形状说明个人助手中的“对象”常由业务 API 决定：偏好、任务、交互和摘要不是同一表；长期 profile 和知识库也不是同一来源。它的主要失败边界同样具体：`node:sqlite` 不可用时短期层会退回进程内 Map，重启丢失；摘要/tree compaction 可能固化错误；文件、SQLite、tree vector 与 LightRAG 可以部分更新而产生分歧。

MineEcho 能说明多层对象是现实工程模式，却不能证明 `user / consent / purpose / valid time` 已形成完整治理合同。应用 UI 中“看见某条记忆”也不等于所有上下文投影都已同步。

## 2. OpenViking：把资源、Memory 与 Skill 放进统一虚拟文件系统

[OpenViking](../../projects/volcengine--openviking.md) 将 resource、memory 和 skill 统一为 `viking://` 虚拟文件系统。完整内容进入 AGFS，向量索引只保存 URI、vector 和 metadata；Parser/TreeBuilder 负责构造目录，SemanticQueue 异步生成 L0/L1/L2 表示；session commit 再按 schema 抽取 self、peer 与 experience memory。

### 2.1 数据流

```text
resource / session
  → Parser / commit archive
  → AGFS tree
  → SemanticQueue 生成 L0/L1/L2
  → URI/vector metadata index
  → intent + hierarchical retrieval + rerank
  → 按层回到 AGFS hydrate 原文
```

这一设计把对象身份绑定到 URI/tree，解决了“向量命中后如何回到原内容”的工程问题，也让资源、记忆、技能共享一套访问面。但统一 namespace 不会自动统一生命周期：skill 的适用版本、peer memory 的共享权限、resource 的内容更新仍需要不同语义。

异步 queue 是最明显的边界。AGFS 已有内容时，L0/L1/vector 可能尚未就绪；索引 URI 也可能指向旧或缺失内容。对象层存在、访问层不可见的状态，需要 watermark、repair 和 reader-side fallback 才能解释。

## 3. Letta V1：直接进入 prompt 的 core blocks 与 archival passages

[Letta 固定提交](../../../../agent-memory-v09/bundle/projects/letta-ai-letta.md)是明确标记的 legacy V1 server。它把两类对象分开：

- core blocks：小而稳定、直接编译进 prompt，可被工具修改；
- archive/source passages：切分、embedding 后进入 SQL/向量路径，按需检索。

写入 archival text 时，PassageManager 分块、请求 embedding，写 SQLAlchemy rows/tags，并可向外部 Turbopuffer dual-write；core block 则经过 Memory schema 直接成为 in-context state。

这是一种很清楚的对象—访问差异：core block 不需要检索，但受 context budget 限制；archive 可扩展，却依赖 embedding、后端和检索。固定版本中外部 archive dual-write 失败只记录 error，SQL truth 可能有 passage 而向量侧缺项。更重要的是，该 SHA 属 legacy V1，不能把当前 Letta 的产品状态或采用归因给这套代码。

## 4. Mem0：fact consolidation facade 与多后端能力差异

[Mem0 工程页](../../projects/mem0ai--mem0.md)展示了一种流行的 SDK/facade 形状。`add` 先建立 user/agent/run filters，检索已有候选，调用 LLM 抽 facts 和更新决策，再写主向量 collection 与 SQLite history，并 best-effort 更新独立 entity collection；`search` 组合 semantic、keyword、entity signals 和可选 reranker。

### 4.1 对象语义在哪里

Mem0 的主要对象是被 consolidation 后的 memory fact；history 记录 ADD/UPDATE/DELETE 事件，entity collection 提供关联增强，session messages 又用于近期处理。它不是单一表，却也不是完整的通用 ontology：事实粒度、更新动作和 entity linkage 很大程度取决于模型与 provider capability。

### 4.2 作用域与一致性边界

身份从 API 参数进入，而不是相信 payload metadata，这是可见的隔离措施。但主 memory、history 和 entity 是分开的写路径：entity 更新失败时主 memory 仍可见；不同 vector provider 对 BM25/hybrid 的支持不同；managed platform 的优化也不能归因于固定 OSS SHA。这个系统很好地说明“统一 API”不等于后端语义完全相同。

## 5. Sibyl-Memory：本地 SQLite 权威层与多适配器

[Sibyl-Memory 固定版本](../../../../agent-memory-v09/bundle/projects/sibyl-labs-sibyl-memory.md)由五个 Python 包组成。client 使用 per-tenant SQLite、JSON constraints 与 FTS5 保存权威记录；MCP 将 remember/recall/search/list/forget/state/event 暴露为 tools，并给返回 body 加 untrusted fence；Hermes、LangGraph 与 CLI adapters 复用同一 client/schema family。

```text
MCP remember(category, name, body)
  → 类型/边界校验
  → per-tenant SQLite transaction
  → base tables
  → FTS5 trigger / rebuild shadow
  → search across tiers
  → bounded result + untrusted fence
```

它代表一种 local-first 形状：schema 与 tenant scope 在 client 层，adapter 只翻译宿主接口。FTS shadow 失配会造成 base rows 存在但搜索漏召回；SQLite 写锁会暴露为事务失败；untrusted fence 只能提醒下游，不会消除被召回内容的提示注入风险。它没有跨主机共享、独立采用或运行吞吐证据。

## 6. Open Memory Protocol：对象 schema 与 reference behavior 的差距

[OMP 工程页](../../projects/smjai--open-memory-protocol.md)同时提供 vendor-neutral JSON schema、Express reference server、SQLiteStorage，以及 browser/Claude-MCP/CLI adapters。对象包含 id、content、type、source、tags、namespace、time、可选 embedding 和 metadata；server 还暴露 conversations、extract、compress、handoff。

固定版本真正执行的检索流程是：memory row 写 SQLite，FTS5 trigger 索引 content/tags，search 将 query token 转成 quoted OR FTS expression，并按 type/namespace 过滤。embedding 可以作为 JSON 字段保存，但没有被 reference search 用作向量索引。

这个差距很有代表性：**schema expressiveness、reference implementation、跨实现 conformance 是三件事**。一套对象格式可以写出 embedding、expiration 和 namespace，但若 reference behavior 不执行 expiration、没有 semantic search、多租户过滤也未强化，就不能从字段存在推导语义已实现。项目协议也不能被称为正式标准或成熟生态。

## 7. 六种实现形状的实质差异

| 系统 | 权威对象 | 主要作用域 | 访问投影 | 最有辨识度的机制 | 关键未验证边界 |
|---|---|---|---|---|---|
| MineEcho | interaction/preference/task/profile/tree | personal app/user | vector/BM25/graph/LightRAG | 应用内多层 personal state | fallback durability、长期一致性 |
| OpenViking | AGFS URI/tree + session memory | self/peer/resource tree | L0/L1/L2 + vector metadata | 统一虚拟文件系统与分层 hydrate | queue lag、peer routing、独立部署 |
| Letta V1 | core blocks + archival/source passages | agent/archive/source | SQL/vector archive | prompt-resident 与 retrieved state 分离 | legacy drift、dual-write、当前架构 |
| Mem0 | consolidated facts + history/entity side stores | user/agent/run | vector/BM25/entity/rerank | provider facade + fact update actions | 多存储一致性、provider 语义 |
| Sibyl | per-tenant SQLite records | tenant/category/tier | FTS5 shadow | local-first schema family + adapters | 跨主机、锁竞争、安全效果 |
| OMP | schema-conformant memory rows/conversations | namespace/type | SQLite FTS5 | 交换对象 + reference server/adapters | semantic behavior、expiry、conformance |

没有一个系统完整覆盖对象 ontology、双时间、多写者冲突、派生删除、跨实现 round-trip 和 action authorization。这不是简单的“功能缺失清单”，而是当前领域的分层现实：应用、SDK、runtime、local store 和 protocol 各自在不同位置定义对象。

## 8. 论文路线正在把工程缺口提升为状态语义

近期论文的共同变化不是再增加一种 memory 类型，而是把对象演化变成可检查的状态操作：

- [AtomMem](https://arxiv.org/abs/2606.19847)：从 atomic facts 形成 event、profile 与 associative graph，暴露粒度和派生关系；
- [双时间图存储](https://arxiv.org/abs/2607.26520)：将 stable identity、version、valid/transaction time 放入表示；
- [MemTxn](https://arxiv.org/abs/2607.27834)：把 source-supported write、temporal resolver 与 durable snapshot journal放到回答模型外；
- [GEM/MemState](https://arxiv.org/abs/2605.26252)：把 memory state 表为 content、structure、policy，并区分 association 与 extension；
- [MemCon](https://arxiv.org/abs/2607.13591)：把 retrieve、consolidate、forget 等 operation 交给受学习策略选择。

这些方向尚未在同一 backend、同一 workload 中组合验证。它们更像一组正在收敛的问题定义：对象需要稳定身份和来源，修订需要显式 operation，投影需要可重建，策略需要受提交与权限边界约束。

## 9. 当前最重要的研究缺口

### 9.1 Taxonomy 到 conformance

领域已经有足够多分类名称，却缺少能让两个实现验证“同一对象、同一版本、同一 forget”是否具有相同行为的 test pack。JSON 可解析不是语义 round-trip。

### 9.2 Object formation 与 source loss

原子事实、画像、图和技能都由抽取产生。缺少跨系统、匹配预算的 source-span coverage、false merge/split、dependency error 与 downstream action 对照，因此无法判断结构收益是否抵消形成误差。

### 9.3 多主体与多写者

当前公开证据对 private/team/org scope、动态撤销、并发冲突、复制与共享视图的差别覆盖有限。共享协议增长很快，独立当前版本互操作和生产部署证据很少。

### 9.4 修订是否真的改变行为

对象 current view 正确不代表上下文、缓存、技能和 Agent 行动已经更新。需要 trajectory benchmark 将一次 correction/revoke 追踪到候选、compiled context、tool action 和修复结果。

## 10. 读完这组专题后应能回答什么

读者现在应能解释：为什么事件、事实、关系、程序和共享状态不能共用一套更新规则；双时间与 revision 分别解决什么；Mem0、OpenViking、Letta、Sibyl、MineEcho 和 OMP 的对象模型为何实质不同；以及为何当前研究重点从“存什么格式”移动到“对象操作能否跨后端保持可检查语义”。

若还需回到该分支的短地图，请读[记忆对象与作用域](../01-memory-objects-and-scope.md)；写入算法怎样形成这些对象，见[写入与记忆形成](../02-write-and-formation.md)。
