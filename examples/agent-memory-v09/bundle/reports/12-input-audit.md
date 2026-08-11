# 输入审计：有哪些、是什么时候的、质量怎么判断

## 审计结论

这版输入不再是“19 篇论文 + 13 个仓库”式的小型精选集。高召回 breadth tranche 包含 74 条可回放查询、7,535 条结果出现和 4,319 个 identifier-level 实体；论文 2,494、GitHub 仓库 1,825。两轮的 4,319 项全部有 screening decision，1,899 项获 `map` decision。Supervisor 再归并 deep/adoption/radar provenance 后，final bundle 为 292 queries、7,634 discovery rows、4,407 entities、385 sources、464 claims、773 evidence joins。后加的 88 direct evidence entities 服务证据闭环，不能冒充 broad-search yield。

因此本审计把问题拆成三个回答：

1. **输入有哪些？** 原始搜索 occurrence、去重后的 discovered entity、映射 corpus、deep packet source 和 GitHub current observation。
2. **分别是什么时候的？** 外部对象的 publication/creation/revision/push/release 时间与本轮 observed-at 分开。
3. **质量怎么判断？** discovery 只做 recall 和 signal；mapping 判断相关性和边界；deep 才判断来源、方法、版本、复现和工程现实。

## 1. 输入构成

### 1.1 Breadth provider 与数量

| Provider | Queries | Occurrences | Identifier-level entities | 主要用途 | 已知限制 |
|---|---:|---:|---:|---|---|
| arXiv | 38 | 4,140 | 1,780 papers | recent preprints、机制、benchmark、history、negative/security | 预印本多；一条早期 query 有 precedence bug；不是 peer-review 独立证明 |
| Crossref | 7 | 800 | 714 papers | DOI/venue metadata、benchmark identity、历史与 verify | 宽查询噪声高；与 arXiv 的 manifestation 未形成强 ID merge |
| GitHub Search | 28 | 2,595 | 1,825 repositories | 新建/活跃/高注意力 repo、工程机制、benchmark/security artifact | 公开 GitHub 偏倚；stars/rank 只是一时信号 |
| Semantic Scholar | 1 | 0 | 0 | 计划中的第二 scholarly index | HTTP 429；失败完整记账，不能声称已覆盖 |
| **合计** | **74** | **7,535** | **4,319** | 高召回候选宇宙 | entity 数按稳定标识符，不保证消除所有语义重复 |

“Occurrences” 是 provider 返回次数；同一个 entity 可在多个 query 中出现。当前 1,292 个 entity 至少出现两次，但没有 entity 通过强 ID 跨 provider 合并。后者意味着 provider overlap 不能被拿来证明 recall，也意味着 arXiv/Crossref 同题版本仍可能重复计数。

Standards/adoption 补查使用另一组独立 provider：4 条 exact web search、2 条 GitHub repository search、7 条 GitHub code search、1 条 GitHub REST repository/ref census、1 条 npm registry observation、3 条 direct primary-source open。它们先保存为 18 条 packet-local query，后由 supervisor 规范化并入 final query ledger；GitHub code detail re-fetch 的 rate limit 与 private/unindexed blind spot 都在 query limitation 中保留。

Final ledger 的 218 条 downstream additions 来自 deep/direct-open、standards/adoption、radar 与 C09 verification。292-query lane mentions 为 paper 136、mechanism 111、github 109、adoption 75、standards 72、negative 58、product 41、benchmark 36、cost 31、security 30、history 29；同一 query 可多 lane，且这些不能倒推为 breadth query coverage。

### 1.2 查询阶段

| Stage | Queries | Occurrences | 作用 |
|---|---:|---:|---|
| pilot | 4 | 300 | 校准生态规模、暴露 provider 限制；不作最终停止依据 |
| discover | 52 | 5,115 | 第一轮 terminology/mechanism/GitHub/benchmark/security 等高召回搜索 |
| gap-fill | 10 | 965 | 根据 mapper 和 cluster gap 补 storage、coding、lifecycle、cost、security、protocol 等 |
| deep-focus | 3 | 446 | 深挖 retrieval、shared memory 和 recently pushed GitHub |
| verify | 2 | 400 | Crossref identity 与 foundation manifestation 复核 |
| adversarial | 3 | 309 | no-memory/long-context/BM25、attack/privacy/deletion 和 executable attack artifact |

后 18 条并非预先固定的“第 2–5 轮”；它们由第一轮 mapping 的具体缺口生成，query row 中保存 parent、target cluster、lane/window 和 information-gain rationale。

### 1.3 原始响应与可回放性

查询账本引用 91 个 raw snapshot；raw 文件按 stage/provider/query 保存。每条 query 都有 exact request URL、UTC 执行时间、result count、状态和限制。第二轮同时保存：

- [gap-discovery-execution.jsonl](../../gap-discovery-execution.jsonl)：命令级开始/结束/exit code 和输出路径；
- [gap-discovery-import-spec.json](../../gap-discovery-import-spec.json)：stage、iteration、parent、lane、window、cluster、information gain；
- [gap-discovery-compile-dry-run.json](../../gap-discovery-compile-dry-run.json)：写入前预演；
- [gap-discovery-compile-summary.json](../../gap-discovery-compile-summary.json)：正式导入结果。

## 2. 输入是什么时候的

### 2.1 研究截止与观察时间

研究 cutoff 是 2026-08-10。74 条 breadth query 的执行时间从 `2026-08-10T03:37:18Z` 到 `2026-08-10T05:07:30Z`；GitHub selected-repo observations 发生于随后同一天 UTC。Standards/adoption 查询覆盖同日 `04:45:00Z`—`05:46:38Z`（其中 repository/npm census 记录为时间区间），包级 JSON/外键验证于 `06:06:52Z` 完成，随后进入 supervisor merge。Cutoff 是“允许纳入的外部事实时间”，observed-at 是“我们实际读取/保存它的时间”，两者不能互换。

### 2.2 Breadth corpus 的时间分布

时间窗是互斥主区间，rolling 90d 是 rolling 12m 的子集：

| Window | 日期 | Papers | Repositories created | All entities | 其中已 mapped |
|---|---|---:|---:|---:|---:|
| Foundation | 2000-01-01—2023-12-31 | 270 | 232 | 502 | 79 |
| 2024–2025 | 2024-01-01—2025-08-09 | 588 | 270 | 858 | 210 |
| Rolling 12m | 2025-08-10—2026-08-10 | 1,520 | 1,323 | 2,843 | 1,610 |
| Rolling 90d | 2026-05-13—2026-08-10 | 880 | 523 | 1,403 | 889 |
| Future quarantine | 2026-08-11 以后 | 116 | 0 | 116 | 0 |

不能把 rows 相加：rolling 90d 已包含在 rolling 12m。主互斥区间 foundation + 2024–2025 + rolling 12m + future 恰好为 4,319。

日期精度为 4,086 exact、100 month、189 year、32 unknown。Hardened rule 不再把只“部分重叠” recent window 的 year/month interval 算作近期；这避免把 2026 年整年 metadata 在 8 月 10 日提前全部算作当前证据。

Final merge 后的 4,407 entities 包含 2,510 papers、1,846 repositories、3 datasets、14 products、2 standards 和 32 other。其窗口为 foundation 506、2024–2025 864、rolling-12m 2,890、rolling-90d 1,437、future 115；无日期窗口的 direct artifacts 不进入 freshness 分母。增量差异来自 source/direct provenance，不是新的 broad search round。

### 2.3 GitHub creation、activity、release 分开

仓库的“什么时候”至少有四种：created、pushed、latest release 和本轮 observed-at。本轮规定：

- entity freshness 用 **created date**；
- recent activity 用 **pushed date**；
- release freshness 单独存 latest release；
- stars 是 observed-at 时的累计值。

完整 discovery 中，1,323 个仓库创建于 rolling 12m、523 个创建于 rolling 90d；1,649 个仓库在 rolling 12m 内有 push、1,345 个在 rolling 90d 内有 push。活动数量比新建数量大是正常现象，不能混成“新增项目”。

59 个 radar repo 中，32 个创建于 2026、17 个创建于 2025、4 个创建于 2024、6 个创建于 2023；54 个有 rolling-90d push，39 个有可见 latest release，53 个有明确 license。它们只有一次 GitHub stars observation。后续对 59 仓运行 OSSInsight history 只得到 1 个 usable、3 个 qualified、55 个 unavailable；因此不能声称或排行 star 增长/加速。

## 3. 广度如何判断

广度不是“query 数多”或“结果数大”，而是以下代理共同成立：

- paper 与 GitHub 独立 lane 都有足够的 absolute count；
- foundation、established、rolling 12m、rolling 90d 都有 coverage；
- terminology、mechanism、benchmark、negative/security、cost、product、history 和 alternatives 有独立 query families；
- broad corpus 经过 mapping，能形成稳定 cluster boundary；
- 新 query 的 unique yield、new cluster、new stance、recent signal 和 boundary change 有记录；
- high-signal exclude、defer、future、collision 和 unmapped 得到复核；
- 剩余 lane/perspective gap 显式存在，不用数量掩盖。

原始 breadth tranche 的 discovered 4,319、papers 2,494、repos 1,825、mapped 1,899、recent discovered 2,843 和 queries 74 均超过最低值。final 292-query ledger 另合并 deep、radar、standards/adoption 与 saturation follow-up，adoption/standards lane mentions 分别为 75/72。这些数量只证明搜索漏斗足够宽；G1 还必须由逐 cluster×lane×window coverage 和真实 saturation events 独立验收，不允许用总数补偿未闭合单元格。

## 4. Mapping 的质量判断

### 4.1 漏斗结果

第一轮 3,128 个 entity 的 metadata screen 为：

| Mapper decision | Count | 含义 |
|---|---:|---|
| deep-candidate | 457 | 值得打开原始来源；仍不能作技术结论 |
| map | 884 | 足以影响 taxonomy/trend count |
| defer | 105 | 身份、日期、scope 或 lineage 未解决 |
| exclude | 1,682 | 词义碰撞、generic RAG/framework、普通系统 memory、列表/教程等 |

第一轮 subtotal 只用于解释审计历史，不再作为 current count；最终 mapping 口径由两轮合并账本给出。

第二轮 1,191 个新 entity 不沿用第一轮 proposal enum，而直接进入严格增量 decision：

| Incremental disposition | Count | 说明 |
|---|---:|---|
| map | 587 | 280 papers + 307 repos；metadata 足以影响 map，不是 deep verification |
| defer | 37 | scope/身份/边界仍不足，留在 discovered/HOLD |
| exclude | 567 | generic framework/app、词义碰撞、无 Agent Memory bridge 等 |

正式 mapping snapshot 为 **1,899 map decisions**；mapped decision population 中有 969 papers、930 repositories。Deep/radar/C09 merge 随后追加或提升 105 个 `deep-verify` decisions；final screening 为 1,899 map、105 deep-verify、136 defer、2,278 exclude；final stage 为 1,773 mapped、221 deep-verified、2,413 discovered。4,230 条 assignments 由 1,994 primary 与 2,236 secondary 组成。

### 4.2 审计如何发现错项

固定 seed 的 120 条样本按 entity type × decision 分层，不是只抽“看起来不错”的项。60 个 map/deep 样本中有 8 个 false inclusion，常见原因是：

- KV-cache、显存、serving 或硬件 memory 被误当 persistent Agent Memory；
- 人类神经科学或 generic continual learning 缺 Agent Memory bridge；
- vector DB、RAG、framework 或 app 的 feature list 被过度解释；
- stars、creation、push signal 导致 promotion 过头；
- metadata 没展示 version/audit/tier mechanism，却在 proposal 中被推断；
- defer 仍带 substantive cluster label，污染 cluster count。

20 条 audit overrides 与 planner demotions/holds 写入逐实体 decision ledger。这个过程提高了 precision，但不能把 13.3% 外推为总体错误率，也不能证明其余 mapped 项全部正确。

增量 mapping 又在正式 apply 前经历多次语义 preview：先撤回带 memory feature 的通用框架误纳并补回真正 provider，再修正由 abstract 中 evaluation 词造成的 C13 越权。最终对 382 个新增仓库做完整 metadata census，对所有 rolling-90d/likely/high-signal/future papers 逐项检查，并抽查 80 个 low-signal papers；其余 low-signal 由 strict classifier 判定。`--check` 的 count/ID/byte PASS 只证明结构一致，不是独立语义 audit，也没有产生总体 error estimate。

审计的 seed、分层设计、汇总结果和扩展检查范围已落在 [audit-report.md](../../mapping/audit-report.md)，20 条实际改判在 reconciliation ledger 中可逐项复核；但 120 条样本没有单独保存逐行 verdict。这是审计可重放性的限制，不应被 `PASS` 汇总掩盖。

### 4.3 Cluster 不是质量分

113 个 mapper natural labels 归并为 16 leaves/5 roots；它们表示问题和机制边界，不表示成熟度排名。`MM-C01` 服务/control plane、`MM-C02` storage/index、`MM-C03` structured/temporal、`MM-C05` lifecycle 等保持分离，是为了避免“都叫 memory infrastructure”掩盖不同工程问题。

## 5. Deep input 的质量判断

### 5.1 选择方式

每个重要问题组从 mapped/deep candidates 中分层选：

- foundational lineage；
- 2024–2025 established work；
- rolling-12m 与 rolling-90d frontier；
- canonical/representative repository；
- benchmark/dataset；
- strongest negative、security 或 contradiction；
- decision-critical engineering implementation。

当前五个主题 packet 合计 107 selections，canonical URL 去重后为 98 个对象。GitHub radar 另有 59 个仓库工程卡；合并去重后是 142 个对象，其中 60 papers、78 repositories、3 products、1 dataset。重复不是错误：MemGPT、Reflexion、Voyager、A-MEM、Letta 和 Mem0 跨多个问题包出现；supervisor 合并时必须只算一个 deep entity，但保留多个 cluster role。

### 5.2 论文质量

论文不按 citation 数或是否“新”做单分排序，而逐项记录：

- 原论文/proceedings 是否打开；
- peer-reviewed、preprint、workshop 或 system report status；
- first publication 与 revision；
- task、dataset/version、model/configuration、baseline、metric 和 limitation；
- paper↔repo↔data identity；
- artifact availability；
- independent reproduction 与 opposing evidence；
- 结论适用的 protocol/population boundary。

新 preprint 可以是 frontier signal，也可作为“作者在该设置下报告什么”的 T1 source；它不能因为新就被升级为社区共识或工程成熟。

### 5.3 仓库质量

仓库逐项检查 canonical owner/node、pinned commit、created/pushed/release、license、archive/fork、setup、tests/CI、architecture layout、dependencies、integration constraint、maintenance 和 independent adoption。判定层级为：

- `documented`：README/docs 写了；
- `present`：tests/workflow/code path 可见；
- `executed`：本轮在记录环境里成功运行且有 execution record。

当前没有 `executed`。仓库 existence、stars、CI badge、vendor customer logo 或 README benchmark 都不能填 adoption/performance evidence。

### 5.4 Source 与 claim 质量

Worker subtotal 曾为五个主题包 114 sources/119 claims/229 joins、GitHub radar 203/207/274、standards/adoption 27/30/64。Supervisor 按 canonical source identity 去重、跳过一个缺 commit/date 的 blocked deep source，并把 radar 两条 research log 从 T1 降为 T3。Final ledger 为 **385 sources（366 T1、0 T2、19 T3；384 opened、1 blocked）、464 claims、773 evidence joins、464 semantic checks**。T3 research log 只能支持“本轮在某个 query/time/public-index 范围里没有找到/统计到什么”，不能证明外部世界不存在。

专项包把“成熟采用”的门槛冻结为至少一类可审计的独立证据：非作者组织的 deployment/operator artifact、当前版本 conformant implementation、公开 fixture/conformance/双向 round-trip result，或能识别规范版本且可独立归因的生产案例。Stars、forks、downloads、README logo、same-project demo、目录或镜像都只作 lead。本轮确认了两个较弱但真实的外部集成信号：一个不同 owner 的旧 UMP 0.1-shaped adapter，以及一个未固定版本的外部 Engramory installer；它们证明“有人做了外部接入”，但达不到当前版本一致性或独立生产采用的门槛。

## 6. 第二轮与专项补查的状态

第二轮 18 条全局查询增加 2,120 occurrence；按 compiler stable key 增加 1,191 entity。现在每项都已落 screening decision 和可重算 rationale，587 项进入既有 16-leaf DAG；没有出现新的一阶 cluster，主要增厚了 coding/project memory、services、portability、security/evaluation 等既有区域。这说明 follow-up search 对边界和密度有信息增益，也提供了 scoped map-saturation 信号。

但“全部有 decision”不等于“全部深读”：增量材料是 title/abstract/description/topic 等 metadata，人工与 classifier 覆盖必须分开报告。Mapped 项只可进入 taxonomy、freshness 和 deep selection，不能直接支持 performance、adoption、architecture guarantee 或 consensus。

Standards/adoption 的 18 条补查是另一种输入：6 条 standards、12 条 adoption，24 candidates、18 selections、27 packet sources。它证明专项查过 W3C/IETF/MCP/project specs/independent adoption probes，并已在 final merge 中进入 query/source/claim ledger；但它不是 breadth query tranche。它找到的是一个有界 abstention：在记录的公开查询范围内，没有满足门槛的独立生产部署、外部 conformant implementation 或 round-trip/conformance report；这不是“世界上没有采用”。

## 7. 当前输入 gate 判定

| Gate | 当前判断 | 理由 |
|---|---|---|
| Absolute discovery breadth | PASS | 4,319 entities，paper/GitHub 均远超本轮 floor |
| Freshness discovery | PASS with qualification | 2,843 rolling-12m、1,403 rolling-90d；future 116 quarantine；creation/activity 已拆分 |
| Provider diversity | PARTIAL | arXiv/Crossref/GitHub 有效；Semantic Scholar 429；无跨 provider strong-ID convergence |
| First-wave map integrity | PASS for frozen wave | 3,128 一一筛选；audit/override/reconciliation/count invariants 完整 |
| Full discovered-to-screen coverage | PASS structurally, PARTIAL semantically | final 4,407/4,407 有 decision；增量 classifier 未获同等级独立逐行审计 |
| GitHub engineering input | PASS for observation, PARTIAL for trend | 59 complete repo observations；star-history 补查因 provider coverage 失配而关闭增长榜，改用 creation/push/release/activity 信号 |
| Product/standards/adoption | PARTIAL | final ledger 已纳入 standards/adoption queries；有两个 qualified weak integration signals，但没有当前版本独立 conformance、可归因生产部署或双向 round-trip evidence，因此仍保持 bounded abstention |
| Key evidence closure | PASS | 关键数字、版本、比较、安全、当前状态和限制已进入 source/claim/semantic ledger；普通分析不以逐句建账作为目标 |
| Repository execution | NOT RUN, by design | 默认采用固定版本文档、manifest、关键代码和工程 profile 检查；0 executions 限制运行时/性能判断，但不是只读调研失败 |

## 8. 对用户输入反馈的逐项回答

| 用户反馈 | v09 的实质改动 | 尚未解决 |
|---|---|---|
| 论文、仓库太少 | discovered 扩至 2,494 papers、1,825 repos；deep unique 60/34 | 不能用数量替代 identity、relevance 与 source quality |
| 新的不够多 | rolling-12m 2,843，rolling-90d 1,403；GitHub created/pushed/release 分开 | future-dated metadata 仍多；近期 preprint/repo 质量与独立复现未自动提高 |
| 广度与深度混在一起 | 三层 corpus + 独立 mapping + 七个 deep packets（含 C09 coding/project-memory 与 standards/adoption） | final bundle 已形成 221 个 deep-verified entities；仍缺 repository execution 与部分独立复现 |
| GitHub 太旧、不是一等输入 | 28 GitHub queries、1,825 repos、59 current observations、创建/活动查询 | star-history lane 已执行但绝大多数 provider history 与 GitHub 当前值失配；不造 velocity，adoption 与工程执行仍缺 |
| 应先广泛吸收再挑高质量 | 两轮 4,319 全量 decision，1,899 canonical mapped 后才 stratified deep | 增量 low-signal classifier 的独立语义审计弱于第一轮 |

## 9. 最重要的解释边界

“搜索到了 4,319 项”说明输入广度有明显改善；它不说明 4,319 项都相关、都独特或都高质量。“mapped 1,899 项”说明两轮 metadata 可以形成广泛领域地图；它不说明这些 metadata 能支持技术结论。“deep packet 有 98 个主题对象、radar 又检查 59 个仓库、standards/adoption 另有 18 个 selections”说明可以做多簇深研与专项补查；只有最终证据归并、矛盾保留和语义审计闭环后，才说明报告中的具体句子可信。
