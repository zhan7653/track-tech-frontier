# mem0ai/mem0：固定提交工程深潜

**Cluster:** MM-C01  
**Selection:** keep-deep — Older repository with verified recent push; retained only when engineering surface is sufficient.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 4debc58a83377b18be81ae1e5969a300736b2fac |
| Created / pushed | 2023-06-20 / 2026-08-07 |
| Freshness bucket | established-active |
| Release | v2.0.17 / 2026-08-05T16:42:46Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 394 / 97 |
| Single snapshot stars / forks / open issues | 62901 / 7336 / 708 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

OSS Python Memory facade用factory组合LLM、embedder、vector_store、optional reranker和SQLite history。add先按user/agent/run filters隔离、检索existing candidates、LLM抽facts，再batch embed/insert memory vectors、写history并异步式容错地维护独立entity collection；search按provider能力融合semantic、BM25 keyword、entity signals并可rerank。server/TS/CLI是其外部表面，managed platform另有未开源优化边界。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| Memory orchestration | add/search/get/update/delete、identity filters、LLM fact extraction、event decision与telemetry | `GR-S002-T` — mem0/memory/main.py; blob 2a7b1b52dea59ed1dd3af517a57e6e5c0ad10a05; sha256 bc599309c85729d3107560b1d8d4889ca52e649e10df834d8491935a1a8b923e |
| LLM/embedder/vector/reranker factories | 按config装配OpenAI/others、Qdrant与多种vector stores、optional reranking | `GR-S002-T` — main.py Memory.__init__; tree mem0/{llms,embeddings,vector_stores,rerankers} |
| entity store | 在独立collection抽取/embedding entities并维护linked_memory_ids以增强检索 | `GR-S002-T` — main.py entity_store/_upsert_entity/batch entity linking |
| SQLiteManager history | 保存ADD/UPDATE/DELETE历史与近期session messages；不保存主vector records | `GR-S002-T` — mem0/memory/storage.py; blob 5bd5512436cc6f3cbd5ce03d10808d3e6eef067b; sha256 5f5ecdadd2b260fd14f36a0f338336eb760275465dd1056a99a47e1ef07702bd |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | add规范化messages并只从参数设置user_id/agent_id/run_id scope，剥离metadata伪造identity | SDK/server caller → Memory.add | `GR-S002-T` — main.py identity helpers/add |
| 2 | embed conversation并检索existing memories，LLM单次抽取facts/decisions | messages + vector candidates → fact memory texts | `GR-S002-T` — main.py _add_to_vector_store phases 1-2 |
| 3 | batch embed facts、写主vector collection与SQLite history，再best-effort更新entity collection | facts → vector store/history/entity store | `GR-S002-T` — main.py phases 3-7 |
| 4 | search embed query、按provider执行semantic/keyword/entity candidates、融合/rerank并返回 | query + scoped indexes → memory results | `GR-S002-R` — readmes/GRC002.md New Memory Algorithm/Basic Usage; main.py search paths |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| Qdrant client >=1.12 | 默认/核心vector store client | `GR-S002-T` — pyproject.toml blob 650fe0df334d04e573099ceae7a38804eb4a0a13; sha256 3214099a5fedbf2dec5bd1ef0d9858db89687c9fcbb399216ea0ef5bf623f7bb |
| OpenAI >=1.90 + httpx | 默认LLM与embedding provider/API transport | `GR-S002-T` — pyproject.toml dependencies; README default models |
| SQLAlchemy + sqlite3 history | history/session bookkeeping；self-host server DB surface | `GR-S002-T` — pyproject.toml; memory/storage.py |
| many optional vector stores/LLMs/spaCy | backend portability、hybrid entity extraction与NLP | `GR-S002-T` — pyproject.toml optional-dependencies |

**Integration constraints:**

- Mem0需要LLM执行fact extraction且默认OpenAI模型/embedding；无key或provider failure会阻断infer=True add。 (`GR-S002-R` — readmes/GRC002.md Basic Usage lines 194-198)
- identity必须通过filters/entity params传递；metadata中的user_id/agent_id/run_id会被剥离，旧调用签名需迁移。 (`GR-S002-T` — main.py _strip_identity_keys/_reject_top_level_entity_params)
- vector backend若未实现keyword_search，代码明确禁用hybrid BM25，只保留semantic；不同backend能力并不等价。 (`GR-S002-T` — main.py Memory.__init__ keyword_search capability check)
- README明确managed benchmark含OSS没有的proprietary optimizations，不能用platform分数代表此SHA。 (`GR-S002-R` — readmes/GRC002.md lines 45-60)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=394、unique contributors=97、open issues snapshot=708；release v2.0.17；CI/tests 存在。 (`GR-S002-O` — observations.jsonl/repositories.jsonl GRC002)
- open issues snapshot=708；PR latency、issue close-time、按cloud/OSS/backend分类未测。 (`GR-S002-O` — observations.jsonl GRC002)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| LLM extraction failure | rate limit/timeout/5xx或无效response | 代码raise LLMError，infer add不写facts | GR-S002-T; inference=false |
| entity index partial failure | entity embed/search/update/insert失败 | 主memory仍存在但entity boost/links缺失，代码多处warning并继续 | GR-S002-T; inference=false |
| multi-store partial consistency | vector insert后history或entity write失败 | memory可检索但audit/history或entity状态缺项，恢复语义不统一 | GR-S002-T; inference=true |
| backend capability degradation | 所选vector store无keyword_search | BM25关闭，README所述multi-signal算法不完整 | GR-S002-T; inference=false |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** 服务/控制面是否把 durable records、mutation policy、retrieval 和 admin/observability 分开。

**首要失败风险：** tenant/ACL、迁移、删除、恢复与 centralized blast radius。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

有广泛integration surface但本次未核实独立生产部署/客户；managed platform与OSS实现必须分开，README平台benchmark不归因于固定SHA。stars不作质量判断。

公开代码引用只作为弱集成线索：

- `IPADS-SAI/MobiAgent/requirements.txt`（different owner=true；blob `60d79a6e3f9c63fd10abd1a2168774afa856f7e3`）
- `OTA-Tech-AI/web-agent-protocol/requirements.txt`（different owner=true；blob `b73222900fd6ad14ba46ffdb011d723ff76de217`）
- `zjunlp/MemBase/envs/mem0_requirements.txt`（different owner=true；blob `6f58bb3c2bf480c6ae9af3666904354f5d7cff18`）

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 独立adoption未验证
- 各vector backend一致性矩阵未知
- OSS与managed差异未完全公开

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 固定版本完成 CRUD→retrieve→supersede→delete→restore，并注入中断和跨 tenant 访问。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:07:45Z GitHub snapshot, mem0ai/mem0 was created 2023-06-20, last pushed 2026-08-07, pinned at 4debc58a83377b18be81ae1e5969a300736b2fac, had 62901 cumulative stars, and had latest release v2.0.17 on 2026-08-05; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C002-1 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, the inspected engineering surface for mem0ai/mem0 was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C002-2 -->

The repository's own GitHub metadata describes mem0ai/mem0 as: “Universal memory layer for AI Agents”
<!-- claim:GR-C002-3 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, fixed-source inspection of mem0ai/mem0 supports this project-specific architecture reading: OSS Python Memory facade用factory组合LLM、embedder、vector_store、optional reranker和SQLite history。add先按user/agent/run filters隔离、检索existing candidates、LLM抽facts，再batch embed/insert memory vectors、写history并异步式容错地维护独立entity collection；search按provider能力融合semantic、BM25 keyword、entity signals并可rerank。server/TS/CLI是其外部表面，managed platform另有未开源优化边界。 The repository was not executed in v09.
<!-- claim:PRJ-A015 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, mem0ai/mem0 has these inspected dependencies or services: Qdrant client >=1.12: 默认/核心vector store client; OpenAI >=1.90 + httpx: 默认LLM与embedding provider/API transport; SQLAlchemy + sqlite3 history: history/session bookkeeping；self-host server DB surface; many optional vector stores/LLMs/spaCy: backend portability、hybrid entity extraction与NLP. Its recorded integration constraints are: Mem0需要LLM执行fact extraction且默认OpenAI模型/embedding；无key或provider failure会阻断infer=True add。; identity必须通过filters/entity params传递；metadata中的user_id/agent_id/run_id会被剥离，旧调用签名需迁移。; vector backend若未实现keyword_search，代码明确禁用hybrid BM25，只保留semantic；不同backend能力并不等价。; README明确managed benchmark含OSS没有的proprietary optimizations，不能用platform分数代表此SHA。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I015 -->

At pinned commit 4debc58a83377b18be81ae1e5969a300736b2fac, the inspected repository tree for mem0ai/mem0 exposed these architecture or integration locations: cli, docs, examples, integrations, mem0, mem0-ts, scripts, server, skills, tests; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C015 -->

At the 2026-08-10T05:07:45Z GitHub/API snapshot for mem0ai/mem0, the inspected rolling-90d window contained 394 commits and 97 unique contributors, while open issues were 708; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M015 -->

<!-- synthesis:PRJ-S15 claims:GR-C002-1,GR-C002-2,GR-C002-3,PRJ-A015,PRJ-I015,PRJ-C015,PRJ-M015 clusters:MM-C01 -->

<!-- process:limitation -->
