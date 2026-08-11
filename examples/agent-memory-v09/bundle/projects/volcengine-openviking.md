# volcengine/OpenViking：固定提交工程深潜

**Cluster:** MM-C06  
**Selection:** keep-deep — Frontier-window creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 7f6085a2f95c8a79ec4eb82f973cae57628341a9 |
| Created / pushed | 2026-01-05 / 2026-08-10 |
| Freshness bucket | newly-created-12m |
| Release | python-sdk@0.1.7 / 2026-08-07T06:52:15Z |
| License | AGPL-3.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 862 / 102 |
| Single snapshot stars / forks / open issues | 28136 / 2219 / 455 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

OpenViking 把 memory/resource/skill 统一为 viking:// 虚拟文件系统。Service 层复用在 embedded、CLI 与 HTTP；Parser/TreeBuilder 先把内容写 AGFS，SemanticQueue 异步生成 L0/L1/L2 并写只含 URI/vector/metadata 的索引；Retrieve 做 intent→hierarchical search→rerank；Session commit 归档消息后按 schema 抽取 self/peer/experience memory。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| Client + Service layer | 统一 FS/Search/Session/Resource/Relation/Pack/Debug operations并复用于 embedded/HTTP/CLI | `GR-S016-T` — docs/en/concepts/01-architecture.md; blob 0e777d35246edc6aacd106580b3caf9440f235f3; sha256 f52bbae9fef1fc40f5d901f6d4c84e54adf4f24e6d53e1fb5f1cd4fb226e3a74 |
| Parser + TreeBuilder + SemanticQueue | 解析 PDF/MD/HTML等资源、构造目录树、异步自底向上生成 L0/L1 semantic representation | `GR-S016-T` — docs/en/concepts/01-architecture.md lines 56-62,89-99 |
| AGFS + Vector Index | AGFS 保存完整内容/多媒体/relations；vector index 只保存 URI、vector、metadata | `GR-S016-T` — docs/en/concepts/01-architecture.md dual-layer storage |
| SessionCompressorV2 + HierarchicalRetriever | commit 时抽取长期/执行 memory；query 时目录递归召回并 rerank | `GR-S016-T` — docs/design/session-memory-extraction-flow.md; blob c951543de556bba2063df9c2154e2f356265be6d; sha256 e9284538bcaa5b42395ba67501f840e3fa60a346dda8ff5bcb4d8195d8927e14 |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | resource/session input 被 Parser 或 commit archive 结构化 | file/messages → temporary tree/archive batch | `GR-S016-T` — architecture Adding Context + Session Commit |
| 2 | TreeBuilder 将目录移入 AGFS并 enqueue semantic processing | parsed tree → AGFS + SemanticQueue | `GR-S016-T` — docs/en/concepts/01-architecture.md lines 89-99 |
| 3 | SemanticQueue 生成 L0/L1/L2摘要或 Compressor 抽取 memory，再写 URI/vector metadata | AGFS/session archive → AGFS memory paths + vector index | `GR-S016-T` — architecture lines 111-121; extraction-flow commit |
| 4 | IntentAnalyzer 引导 priority-queue hierarchical retrieval，rerank 后从 AGFS按层读取内容 | query/vector index → context results/trajectory | `GR-S016-T` — architecture Retrieving Context/Design Principles |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| openviking-sdk + FastAPI/Uvicorn/httpx | SDK、独立 HTTP server 与 client transport | `GR-S016-T` — pyproject.toml blob defbab250de13c123a3e98507385cbbcede2a1ae; sha256 1f25d7d824e7146954132e87714782f3824296a609e0caa52cae16d665ae6c20 |
| OpenAI/LiteLLM/Volcengine SDK | 可配置 LLM、embedding、reranker/semantic generation providers | `GR-S016-T` — pyproject.toml dependencies |
| pdfplumber/trafilatura/scrapy/python-docx/openpyxl/tree-sitter family | 文档与代码资源解析 | `GR-S016-T` — pyproject.toml dependencies |

**Integration constraints:**

- 写入语义处理异步；调用方在 add_resource 后需 wait_processed 或接受短时间不可语义召回。 (`GR-S016-T` — architecture ResourceService.wait_processed and SemanticQueue flow)
- self/peer memory 路由受 memory_policy、schema stage、peer_enabled 与 safe peer_id 控制；错误 policy 会漏写或越界。 (`GR-S016-T` — session-memory-extraction-flow.md policy/routing/storage targets)
- AGPL-3.0 对服务分发/修改有许可边界，生产集成需法律审查。 (`GR-S016-O` — repositories.jsonl GRC016 license)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=862、unique contributors=102、open issues snapshot=455；release python-sdk@0.1.7；CI/tests 存在。 (`GR-S016-O` — observations.jsonl/repositories.jsonl GRC016)
- open issues snapshot=455；PR latency、issue close-time、duplicate/support issue 比例未测。 (`GR-S016-O` — observations.jsonl GRC016)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| semantic queue lag/failure | provider不可用、队列积压或 worker 中断 | AGFS 已有内容但 L0/L1/vector 尚未就绪，semantic recall 漏召回 | GR-S016-T; inference=true |
| dual-layer divergence | AGFS mutation 与 vector index 更新不一致 | 索引 URI 指向缺失/旧内容，或内容存在但不可检索 | GR-S016-T; inference=true |
| peer routing leak | 错误 peer_id/policy/schema peer_enabled 组合 | memory 写入错误用户 peer space 或 self memory 被漏写 | GR-S016-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** experience 是否形成有前提、效果、失败和版本的 procedure，而非自由文本摘要。

**首要失败风险：** 错误程序复用、过度泛化、环境漂移与技能污染。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

官方 Studio/managed service 与 README benchmark 属项目方运营/陈述；本次未验证独立第三方部署。仓库覆盖广泛 context DB，不等同纯 memory plugin。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- queue durability/retry SLO 未测
- 独立 adoption 未验证
- 未运行 embedded/server/migration

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 跨任务复用并加入 hard negative、版本变化与 rollback，测 action success 和 harmful transfer。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:13:51Z GitHub snapshot, volcengine/OpenViking was created 2026-01-05, last pushed 2026-08-10, pinned at 7f6085a2f95c8a79ec4eb82f973cae57628341a9, had 28136 cumulative stars, and had latest release python-sdk@0.1.7 on 2026-08-07; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C016-1 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, the inspected engineering surface for volcengine/OpenViking was setup=documented, CI=present, tests=present, license=AGPL-3.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C016-2 -->

The repository's own GitHub metadata describes volcengine/OpenViking as: “Self-evolving Context Database for AI Agents. Unify Agent Memory, Knowledge RAG and Skills.”
<!-- claim:GR-C016-3 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, fixed-source inspection of volcengine/OpenViking supports this project-specific architecture reading: OpenViking 把 memory/resource/skill 统一为 viking:// 虚拟文件系统。Service 层复用在 embedded、CLI 与 HTTP；Parser/TreeBuilder 先把内容写 AGFS，SemanticQueue 异步生成 L0/L1/L2 并写只含 URI/vector/metadata 的索引；Retrieve 做 intent→hierarchical search→rerank；Session commit 归档消息后按 schema 抽取 self/peer/experience memory。 The repository was not executed in v09.
<!-- claim:PRJ-A006 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, volcengine/OpenViking has these inspected dependencies or services: openviking-sdk + FastAPI/Uvicorn/httpx: SDK、独立 HTTP server 与 client transport; OpenAI/LiteLLM/Volcengine SDK: 可配置 LLM、embedding、reranker/semantic generation providers; pdfplumber/trafilatura/scrapy/python-docx/openpyxl/tree-sitter family: 文档与代码资源解析. Its recorded integration constraints are: 写入语义处理异步；调用方在 add_resource 后需 wait_processed 或接受短时间不可语义召回。; self/peer memory 路由受 memory_policy、schema stage、peer_enabled 与 safe peer_id 控制；错误 policy 会漏写或越界。; AGPL-3.0 对服务分发/修改有许可边界，生产集成需法律审查。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I006 -->

At pinned commit 7f6085a2f95c8a79ec4eb82f973cae57628341a9, the inspected repository tree for volcengine/OpenViking exposed these architecture or integration locations: benchmark, bot, build_support, crates, deploy, docker, docs, examples, integrations, npm, openviking, openviking_cli; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C006 -->

At the 2026-08-10T05:13:51Z GitHub/API snapshot for volcengine/OpenViking, the inspected rolling-90d window contained 862 commits and 102 unique contributors, while open issues were 455; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M006 -->

<!-- synthesis:PRJ-S06 claims:GR-C016-1,GR-C016-2,GR-C016-3,PRJ-A006,PRJ-I006,PRJ-C006,PRJ-M006 clusters:MM-C06 -->

<!-- process:limitation -->
