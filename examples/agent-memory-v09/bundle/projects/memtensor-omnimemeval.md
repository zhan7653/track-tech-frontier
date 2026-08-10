# MemTensor/OmniMemEval：固定提交工程深潜

**Cluster:** MM-C13  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d |
| Created / pushed | 2026-06-24 / 2026-08-06 |
| Freshness bucket | newly-created-90d |
| Release | none returned / — |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / not-found-in-inspected-tree / present / not-executed |
| 90d commits / contributors | 18 / 3 |
| Single snapshot stars / forks / open issues | 41 / 6 / 1 |
| Engineering surface | moderate-surface (6/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

这是评测编排仓而非memory implementation。User-memory track用client_factory把不同backend归一为add/search并跑LoCoMo/LongMemEval/BEAM/Persona/HaluMem；agent-memory track把Agent Runtime+Memory Plugin+Task Domain+Verifier组合，runner严格编排cleanup→train→settle→backup/restore→test，最后judge/aggregate/report。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| user-memory adapters/pipelines | 将REST/SDK backends映射为add/search并执行数据集ingest、retrieve、answer、judge、metrics | `GR-S036-R` — readmes/GRC036.md User Memory Evaluation; tree scripts/client_factory and benchmark dirs |
| AgentBench runner + memory lifecycle | 选择protocol并执行plugin validate/mode/cleanup/train/settle/backup/restore/test顺序 | `GR-S036-T` — docs/agent_memory/architecture.md; blob 5109d7b1dceccf6d85aa6467482762a840c5ac1b; sha256 51f77f17ddb421a636e41c16ccbfcbb0f2f84c8edfd6b25879e7776764df8416 |
| task domains | reasoning、information retrieval、knowledge work、code implementation、SWE-bench任务执行 | `GR-S036-T` — tree configs/agentbench/domains; scripts/agentbench/domains |
| verifier/aggregation/reporting | 任务特定判分、LLM-as-Judge、metric aggregation与results目录报告生成 | `GR-S036-R` — readmes/GRC036.md evaluation tracks/results; architecture execution flow |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | 加载benchmark data、backend/plugin config与credentials，validate环境 | configs/datasets/env → runner | `GR-S036-R` — README Installation/Quick Start |
| 2 | cleanup后训练阶段把train interactions写入被测memory backend | train tasks → external memory system | `GR-S036-T` — architecture Runner and Memory Lifecycle |
| 3 | settle并执行backup/restore，test agent或adapter从被测系统检索 | memory lifecycle → test task execution | `GR-S036-T` — architecture memory_train_backup_test protocol |
| 4 | verifier/LLM judge评分，aggregate后写results报告 | task outputs/retrieval evidence → metrics/report | `GR-S036-R` — readmes/GRC036.md lines 16-24 |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| OpenAI/httpx/datasets/pandas | runner、LLM answer/judge、dataset与metrics | `GR-S036-T` — requirements_agentbench.txt blob a1c2c98fe80b75b5e2b03644c001991e133afb99; sha256 b7ddc6c28253631f6e3cc36135fd872ba9fcae8ae9cec85b993d27e5f71355ac |
| FAISS/Transformers/Torch/Pyserini/Tevatron | BrowseComp-Plus dense/sparse retrieval baseline与indexing | `GR-S036-T` — requirements_agentbench.txt |
| Docker/SWE-bench/document toolchain | software engineering/knowledge work domains | `GR-S036-T` — requirements_agentbench.txt |
| backend APIs + answer/eval LLM credentials | 被测系统与judge外部服务 | `GR-S036-R` — readmes/GRC036.md prerequisites |

**Integration constraints:**

- 不同memory plugin必须显式实现cleanup/train/settle/backup/restore lifecycle；缺一项会破坏跨trial隔离或公平比较。 (`GR-S036-T` — docs/agent_memory/architecture.md lifecycle)
- requirements包含Tevatron git main且多数依赖不pin，重复实验需另做lockfile/container固定。 (`GR-S036-T` — requirements_agentbench.txt)
- LLM-as-Judge与backend credentials/model versions是外部变量，报告必须记录实际配置而不能只报仓库SHA。 (`GR-S036-R` — README prerequisites/results layout)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=18、unique contributors=3、open issues snapshot=1；无release；CI未发现、tests tree存在。 (`GR-S036-O` — observations.jsonl/repositories.jsonl GRC036)
- open issues snapshot=1；PR latency、issue close-time、benchmark protocol change review未测。 (`GR-S036-O` — observations.jsonl GRC036)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| cross-trial contamination | cleanup/reset失败或backend最终一致性未settle | test读到前trial/train外数据，分数虚高/不稳定 | GR-S036-T; inference=true |
| adapter semantic mismatch | 不同backend的add/search/filter/identity语义被强行归一 | 比较反映adapter差异而非memory能力 | GR-S036-R, GR-S036-T; inference=true |
| dependency/protocol drift | unpinned packages、Tevatron main、datasets或judge model更新 | 同config重复运行结果/可执行性改变 | GR-S036-T; inference=true |
| judge variance | LLM judge nondeterminism或prompt/model变化 | aggregate metrics变化且不可归因于memory backend | GR-S036-R; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** benchmark 是否固定 dataset/model/agent/memory policy/budget/judge 并保留执行工件。

**首要失败风险：** 任务族混榜、数据污染、不同 access path 和作者自评。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

只应作为evaluation harness候选，不是可部署memory。仓库results是作者运行输出，需核对protocol/config/raw artifacts后才能比较；独立复用/adoption未验证。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- protocol versioning policy未知
- 独立adoption未验证
- 实际results配置/seed/judge variance未审计

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 按 static QA、lifecycle、action、multimodal、security 分组做 matched no-memory/raw/constructed ablation。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:13:32Z GitHub snapshot, MemTensor/OmniMemEval was created 2026-06-24, last pushed 2026-08-06, pinned at 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, had 41 cumulative stars, and had no latest release returned by the releases endpoint; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C036-1 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, the inspected engineering surface for MemTensor/OmniMemEval was setup=documented, CI=not-found-in-inspected-tree, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C036-2 -->

The repository's own GitHub metadata describes MemTensor/OmniMemEval as: “Evaluation framework for benchmarking memory systems.”
<!-- claim:GR-C036-3 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, fixed-source inspection of MemTensor/OmniMemEval supports this project-specific architecture reading: 这是评测编排仓而非memory implementation。User-memory track用client_factory把不同backend归一为add/search并跑LoCoMo/LongMemEval/BEAM/Persona/HaluMem；agent-memory track把Agent Runtime+Memory Plugin+Task Domain+Verifier组合，runner严格编排cleanup→train→settle→backup/restore→test，最后judge/aggregate/report。 The repository was not executed in v09.
<!-- claim:PRJ-A013 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, MemTensor/OmniMemEval has these inspected dependencies or services: OpenAI/httpx/datasets/pandas: runner、LLM answer/judge、dataset与metrics; FAISS/Transformers/Torch/Pyserini/Tevatron: BrowseComp-Plus dense/sparse retrieval baseline与indexing; Docker/SWE-bench/document toolchain: software engineering/knowledge work domains; backend APIs + answer/eval LLM credentials: 被测系统与judge外部服务. Its recorded integration constraints are: 不同memory plugin必须显式实现cleanup/train/settle/backup/restore lifecycle；缺一项会破坏跨trial隔离或公平比较。; requirements包含Tevatron git main且多数依赖不pin，重复实验需另做lockfile/container固定。; LLM-as-Judge与backend credentials/model versions是外部变量，报告必须记录实际配置而不能只报仓库SHA。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I013 -->

At pinned commit 0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d, the inspected repository tree for MemTensor/OmniMemEval exposed these architecture or integration locations: configs, data, docs, env_examples, scripts; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C013 -->

At the 2026-08-10T05:13:32Z GitHub/API snapshot for MemTensor/OmniMemEval, the inspected rolling-90d window contained 18 commits and 3 unique contributors, while open issues were 1; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M013 -->

<!-- synthesis:PRJ-S13 claims:GR-C036-1,GR-C036-2,GR-C036-3,PRJ-A013,PRJ-I013,PRJ-C013,PRJ-M013 clusters:MM-C13 -->

<!-- process:limitation -->
