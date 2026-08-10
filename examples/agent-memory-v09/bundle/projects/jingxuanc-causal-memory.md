# JingxuanC/causal-memory：固定提交工程深潜

**Cluster:** MM-C03  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 054af36507537f7b616fa41db07be483cc6e55c3 |
| Created / pushed | 2026-07-26 / 2026-08-10 |
| Freshness bucket | newly-created-90d |
| Release | v0.3.1 / 2026-07-26T16:29:54Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 163 / 2 |
| Single snapshot stars / forks / open issues | 30 / 1 / 9 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

Rust/MCP 系统把 raw session logs、atomic facts 和 decision→outcome causal edges 放在同一 SQLite 骨架上：写时 gatekeeping 隔开审计原文与召回层，distill/consolidation 形成 facts/edges，读时 BM25 与可选 embedding 用 RRF 融合并可做 typed spreading activation。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| store/write + SQLite schema | 写 session_logs、agent_facts、causal_edges，处理 supersede、embedding blob 与 distill marker | `GR-S010-T` — crates/causal-memory/src/store/write.rs; blob 59ea4d02d81b2acf671fa85c350a484f78b527d2; sha256 30ca88aa17e541d05d6bd0b7b83f16bd9fb23f7e457f437b23f8c5d842a5f50f |
| distill/consolidate/hippocampus | 每 session 抽取 facts/causal edges、SWR-style consolidation 与图上正负激活 | `GR-S010-T` — tree paths crates/causal-memory/src/{distill.rs,consolidate/,hippocampus/}; docs/architecture.md |
| retrieve fusion | 分别检索 fact/causal 层的 BM25、semantic、entity-hop/trace，再以 RRF 汇合 | `GR-S010-T` — tree paths crates/causal-memory/src/store/retrieve/{bm25,semantic,fusion,entity_hop,trace}.rs; docs/architecture.md blob d888ef8399fe74b6621a4d3bfef97542a56c31c3 |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | session 或 MCP direct write 先写 session_logs/typed input | agent/MCP → SQLite staging | `GR-S010-R` — readmes/GRC010.md lines 128-167,241-268 |
| 2 | distill 用每 session 一次 LLM call 分类并写 facts 与 causal edges，失败单位不打 done marker | session_logs → agent_facts/causal_edges | `GR-S010-T` — docs/architecture.md write map |
| 3 | 写路径维护 BM25 与可选 embedding，更新会先 retire 旧 fact 再写新值 | typed rows → layer indexes/version state | `GR-S010-T` — store/write.rs + docs/architecture.md lines 47-69 |
| 4 | search_facts/search_causal 取候选并由 search_memory RRF k=60 组合 | BM25/semantic indexes → answer memory lines | `GR-S010-T` — docs/architecture.md retrieve map |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| rusqlite | 单文件 SQLite 权威存储 | `GR-S010-T` — crates/causal-memory/Cargo.toml blob 8c31f8d3aad39612669661f0a6dd6a21d1836cdb; sha256 728630395c058bee4268b26d6c22ca9232f7661f664c667a9ee0475bff87600b |
| reqwest + tokio | HTTP embedding/LLM 调用与异步等待 | `GR-S010-T` — crates/causal-memory/Cargo.toml dependencies |
| fastembed optional local-embed | BAAI/bge-small-en-v1.5 ONNX 384-d embedding；首次需下载模型且动态加载 ONNX runtime | `GR-S010-T` — crates/causal-memory/Cargo.toml feature local-embed |

**Integration constraints:**

- 固定 SHA 状态只提供 MCP stdio；README 明确 HTTP transport 尚未实现，网络服务接入需另加 wrapper。 (`GR-S010-R` — readmes/GRC010.md lines 346-369)
- 启用 local-embed 时需要可动态加载的 ONNX Runtime 与首次模型下载；HTTP embedding 则需要 endpoint/model 配置。 (`GR-S010-T` — crates/causal-memory/Cargo.toml local-embed comments)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=163、unique contributors=2、open issues snapshot=9；release v0.3.1；CI/tests 存在。 (`GR-S010-O` — observations.jsonl/repositories.jsonl GRC010)
- open issues snapshot=9；PR latency、issue close-time 与 migration breakage rate 未测。 (`GR-S010-O` — observations.jsonl GRC010)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| distill 未完成 | LLM/解析在 session distillation 失败 | raw logs 保留但 facts/causal recall 缺失；done marker 不写使其可重试 | GR-S010-T; inference=false |
| embedding backend 不可用 | ONNX dylib/模型缺失或 HTTP endpoint 失败 | semantic 通道不可用，召回退回/依赖 BM25，效果边界未知 | GR-S010-T; inference=true |
| 跨任务 meta-edge 误联 | 相似/重复/矛盾挖掘在弱证据上建立关系 | spreading activation 放大错误类比；README 亦将 lesson transfer 列为限制 | GR-S010-R, GR-S010-T; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** 实体、关系、valid/transaction time、revision 与 conflict 是否是一等状态。

**首要失败风险：** edge truth、旧版本召回、post-filter candidate loss 与图删除传播。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

本次只确认仓库实现与 paper-oriented benchmark harness；未确认独立生产采用。README 分数、231 tests 等为项目方陈述，未执行。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- HTTP transport 不存在于该 SHA
- 独立 adoption/线上规模未知
- 未运行 benchmark

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 构造更新/冲突/time-travel 查询，验证 current/history/all-version 和 provenance。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:11:54Z GitHub snapshot, JingxuanC/causal-memory was created 2026-07-26, last pushed 2026-08-10, pinned at 054af36507537f7b616fa41db07be483cc6e55c3, had 30 cumulative stars, and had latest release v0.3.1 on 2026-07-26; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C010-1 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, the inspected engineering surface for JingxuanC/causal-memory was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C010-2 -->

The repository's own GitHub metadata describes JingxuanC/causal-memory as: “Causal memory layer for AI agents — MCP server that records decision→outcome relationships. Survives compaction.”
<!-- claim:GR-C010-3 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, fixed-source inspection of JingxuanC/causal-memory supports this project-specific architecture reading: Rust/MCP 系统把 raw session logs、atomic facts 和 decision→outcome causal edges 放在同一 SQLite 骨架上：写时 gatekeeping 隔开审计原文与召回层，distill/consolidation 形成 facts/edges，读时 BM25 与可选 embedding 用 RRF 融合并可做 typed spreading activation。 The repository was not executed in v09.
<!-- claim:PRJ-A003 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, JingxuanC/causal-memory has these inspected dependencies or services: rusqlite: 单文件 SQLite 权威存储; reqwest + tokio: HTTP embedding/LLM 调用与异步等待; fastembed optional local-embed: BAAI/bge-small-en-v1.5 ONNX 384-d embedding；首次需下载模型且动态加载 ONNX runtime. Its recorded integration constraints are: 固定 SHA 状态只提供 MCP stdio；README 明确 HTTP transport 尚未实现，网络服务接入需另加 wrapper。; 启用 local-embed 时需要可动态加载的 ONNX Runtime 与首次模型下载；HTTP embedding 则需要 endpoint/model 配置。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I003 -->

At pinned commit 054af36507537f7b616fa41db07be483cc6e55c3, the inspected repository tree for JingxuanC/causal-memory exposed these architecture or integration locations: benches, crates, docs, scripts; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C003 -->

At the 2026-08-10T05:11:54Z GitHub/API snapshot for JingxuanC/causal-memory, the inspected rolling-90d window contained 163 commits and 2 unique contributors, while open issues were 9; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M003 -->

<!-- synthesis:PRJ-S03 claims:GR-C010-1,GR-C010-2,GR-C010-3,PRJ-A003,PRJ-I003,PRJ-C003,PRJ-M003 clusters:MM-C03 -->

<!-- process:limitation -->
