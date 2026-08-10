# 方法、质量判断、限制与可复现性

**主题：** AI Agent Memory  
**研究截止：** 2026-08-10  
**模式：** fresh comprehensive snapshot  
**本文数据截点：** discovery iteration 2、incremental mapping、七个 deep packets（含 C09 coding/project-memory 与 standards/adoption）与 GitHub radar 均已归并；当前 post-merge bundle 为 292 queries、7,634 discovery rows、4,407 entities、385 sources、464 claims、773 evidence joins。

## 1. 方法原则

本轮首先修复的是工作流，而不是措辞。v08 把检索、资格审查和最终证据集压在同一个小漏斗里，导致结果虽精确，却难以支撑领域级判断，也容易写成逐项目介绍。v09 将任务拆成四个不可互相替代的层次：

1. **Breadth / discovered：** 以 recall、新近覆盖和边界发现为目标，允许噪声；保存每次出现和原始响应。
2. **Map / mapped：** 对实体做身份、相关性、日期和簇边界判断；领域结构只从这一层生成。
3. **Depth / deep packets：** 在每个重要簇内，按基础、近期、工程、benchmark、negative/security 分层选择并重新打开原始来源。
4. **Synthesis：** 从 cluster packet、proposition、contradiction 和 relation 写作，不从搜索结果列表直接写 executive report。

数量只回答“吸收了多大的候选空间”；质量由身份、适用性、来源直接性、版本、复现、协议可比性、工程可见性和反证分别判断。没有单一分数把这些维度折成一个看似精确的排名。

本版采用“报告质量优先”的验收口径：先确认 broad map、新鲜度、主簇边界和技术脉络，再把深度集中到重要、近期、争议或决策相关的论文与仓库。数字、版本、比较、安全、当前状态等关键事实继续逐项核证；普通背景与分析连接允许使用段落级引用和逻辑审阅。coverage matrix 用来发现偏科，不再要求每个 cluster × lane × window 都完成一套法证式证明。仓库默认做到固定版本的 README、架构、manifest 与关键代码检查；只有运行结果会实质改变判断时，才执行安装或测试。

## 2. 冻结研究合同与校准目标

[research-contract.md](../../research-contract.md) 固定了受众、截止日、Memory 边界和 12 条不可妥协要求，并先生成 10 个视角：系统架构、学习、检索、benchmark、平台工程、安全隐私、成本、产品采用、反方和 frontier scout。视角的作用不是装饰，而是决定独立 evidence lane 和后续 gap query。

小规模 pilot 只用于估计生态规模。根据 pilot 的 397 个 arXiv candidates、Crossref 的高噪声和一个 GitHub 广义查询的 52,649 个匹配，[acceptance.md](../../acceptance.md) 为本轮设置了 Memory 特定 floor；这些 floor 不是通用 Skill 默认，也不是停止条件。停止取决于字段树与重要簇的判断是否稳定、近期信号是否已检查、剩余缺口是否会改变报告结论。

## 3. 第一阶段：高召回发现

### 3.1 查询设计

第一阶段执行 56 条 exact query：4 条 pilot、52 条 discover。查询覆盖术语、lifecycle、episodic/semantic/procedural、graph/temporal、benchmark、multi-agent、tool/action、security、system/control plane、long-context/RAG alternative、personalization、multimodal/embodied、reflection/self-evolution 和 world model。

Provider 为 arXiv、GitHub Search、Crossref 和 Semantic Scholar。Semantic Scholar pilot 返回 HTTP 429，作为 failed query 保留；没有把失败 provider 从方法叙述中删掉。arXiv 的 Q0001 有 Boolean/date precedence 缺陷，因此标为 `partial`，由 Q0005 的括号化请求替代；Q0001 的原始结果仅保留作审计和宽松候选，不单独支撑覆盖结论。

GitHub 同时运行：

- 无日期的基础/高注意力查询；
- `created` rolling-12-month 与 rolling-90-day 查询；
- mechanism、benchmark、security、multi-agent、multimodal、MCP、graph 和 context-engine 查询；
- 依 attention band 分开的 stars threshold 查询。

这里的 stars、rank、creation 和 push 只决定“要不要检查”。它们不决定 map、deep，更不证明技术质量、成熟度或采用。

### 3.2 occurrence 先于去重

每个结果出现先写入 [discovery_results.jsonl](../discovery_results.jsonl)，保留 query ID、provider、rank、page/cursor、observed-at、identifier、request 和 raw snapshot。之后才按稳定标识符归并 entity：论文优先 DOI、arXiv ID 或 provider stable ID；仓库优先 GitHub node ID。title/author/year 只可形成待审 duplicate lead，不自动合并。

这种顺序让 breadth tranche 的 7,535 occurrence 与 4,319 entity 都可解释。后续 deep/direct/radar/C09 merge 又加入 99 条 provenance rows 和 88 个 direct evidence entities，使 final ledger 为 7,634/4,407；这些 direct artifacts 用于证据闭环，不是新增 broad-search recall。由于 breadth compiler 没有形成跨 provider 的强标识符合并，4,319 仍可能包含 arXiv/DOI/venue manifestation 的语义重复；它应被视为稳定标识符口径的上界，而不是绝对唯一论文数。

### 3.3 原始输入保存

74 条 breadth query 共引用 91 个 raw snapshot。每条 query 保存 exact `request_url`、执行 UTC、状态、result count、information gain、target lanes/windows/clusters 和 parent query。编译先 dry-run，再正式写入；第二轮的 [gap-discovery-compile-dry-run.json](../../gap-discovery-compile-dry-run.json) 与 [gap-discovery-compile-summary.json](../../gap-discovery-compile-summary.json) 分别记录预演和正式结果。Deep/adoption/radar/C09 merge 把 218 条 packet-local direct-open/verify/adversarial query 规范化后追加到同一 ledger，最终为 292；两类 query 必须分开解释。

## 4. 时间、新鲜度与未来隔离

冻结窗口为：

- `W_FOUNDATION`：2000-01-01 至 2023-12-31；
- `W_2024_2025`：2024-01-01 至 2025-08-09；
- `W_ROLLING_12M`：2025-08-10 至 2026-08-10；
- `W_ROLLING_90D`：2026-05-13 至 2026-08-10；
- `W_FUTURE_METADATA`：2026-08-11 以后，只用于 quarantine。

初版 compiler 曾把“只与窗口相交”的 year/month 粗粒度日期算入 recent。hardening 后，year/month interval 必须完整落在窗口内且不跨越 as-of；147 个第一轮实体因此改变窗口，实体数、ID、query 和 occurrence 数不变。[freshness-hardening-delta.md](../../freshness/freshness-hardening-delta.md) 保存前后 SHA-256 和差异。

论文 freshness 依据首次 publication date，并独立保留 revision；仓库 entity freshness 依据 creation date。Push/release/commit activity 单独报告，不能改写“新建仓库”计数。当前完整 discovery 中有 1,323 个仓库创建于 rolling 12m、523 个创建于 rolling 90d；1,649 个仓库在 rolling 12m 内有 push、1,345 个在 rolling 90d 内有 push。后两者是 activity，不是 creation、growth 或 adoption。

116 条 post-cutoff paper metadata 被放入 future bucket；它们保持 `discovered`，不得贡献当前 map、freshness、deep 或趋势结论。

## 5. 第一轮全语料 mapping

### 5.1 可复现分包与独立判断

第一轮冻结 3,128 entities，并按 entity type 与 `sha256(entity_id) mod 3` 分成三包论文、三包仓库。六个 packet 互斥、合计完全守恒；[packet-manifest.json](../../mapping/packet-manifest.json) 保存每包数目与 SHA-256。

每个 mapper 必须为每个 entity 产生恰好一个 proposal：`map`、`deep-candidate`、`defer` 或 `exclude`，同时记录 relevance、自然 cluster label、secondary bridge、problem、architecture/implementation tags、evidence role、freshness/quality signal 和理由。`deep-candidate` 仍是 metadata screen，不是 deep verification。

六包合计：884 map、457 deep-candidate、105 defer、1,682 exclude。输入/输出 ID 集合、一行一实体、enum、UTF-8 和 hash 由 [proposal-validation.json](../../mapping/proposal-validation.json) 验证。

### 5.2 独立审计与 override

[audit-report.md](../../mapping/audit-report.md) 使用固定 seed `v09-mapping-audit-20260810`，抽取 120 条分层样本：paper/repository 各 60，四类 decision 各 30，并覆盖五个时间 bucket。审计还全查 top-30 stars repositories、30 个最新 deep-paper candidates、30 个最新 deep-repository candidates 和全部 99 个第一轮 future records。

在 60 个 map/deep 分层样本中发现 8 个明确 false inclusion（13.3%）。这是等 decision 分层样本的风险信号，不是总体错误率估计。错误集中于 KV-cache/serving、human memory、generic vector DB/RAG、feature-list framework，以及 stars/recent signal 越权。审计给出 20 条优先 override。

### 5.3 Canonical reconciliation

Mapper 的 113 个自然 primary labels 不是最终 taxonomy。[reconciliation.md](../../mapping/reconciliation/reconciliation.md) 采用 decision-first precedence：

1. mapper exclude 保持在 DAG 外；
2. mapper defer 和 future 进入 HOLD；
3. 应用 23 planner demotions 与 23 planner holds；
4. 应用 20 audit overrides，优先级最高；
5. 用 frozen exact alias table 把剩余标签归并为 16 个 leaves，并继承到 5 个 structural roots。

这一阶段只形成历史性的 first-wave baseline；最终口径统一采用下一节的两轮 mapping 和 post-merge ledger，不再把 first-wave subtotal 当作 current count。每个 map decision 恰好有一个 primary leaf，可有去重 secondary membership；future 不得映射。Planner 草案曾出现 recent subtotal 漂移，冻结 corpus 重算后由 materializer 纠正，说明报告必须从 ledger 重算而不能抄 planner 文本。

## 6. 递归 gap filling 与增量 mapping

Mapper summary 和 canonical map 暴露出 storage/index、coding memory、benchmark lifecycle、forget/revoke、security repair、cost、active retrieval、shared memory、protocol、history identity 和 counterexample 缺口。于是第二轮新增 18 条查询，而不是重复第一轮：

- 10 条 `gap-fill`；
- 3 条 `deep-focus`；
- 2 条 `verify`；
- 3 条 `adversarial`。

它们产生 2,120 条 occurrence，并按稳定 key 增加 1,191 个 entity，使总 discovered 由 3,128 增至 4,319。这是 GPT Researcher/dzhng 式“learning → follow-up”的实际 artifact，而不是仅有同名阶段。

### 6.1 第二轮如何 materialize

第二轮不是把 1,191 直接加到 mapped。正式 materializer 对所有 382 个新增仓库的 description/topic 做 census，逐项复核所有 rolling-90d papers、frozen likely/high-signal papers、17 条新增 future metadata，并从剩余 low-signal papers 取固定规则的 80 条分层人工样本；未进入这些人工范围的低信号论文仍由 strict decision-first classifier 给出有界理由。各 inspection scope 有重叠，不能相加为“人工看过多少个唯一实体”。

第一次 preview 过度纳入带 memory feature 的通用框架，也漏掉部分真正 memory provider；另一版又因摘要中的 evaluation 词把主机制论文过度推向 C13。修正规则与人工边界后才执行 `--apply`，随后用同一最新脚本 `--check` 做字节级重算。最终增量为 587 map（280 papers、307 repositories）、37 defer、567 exclude，并新增 1,264 条 primary/secondary assignments。

正式 mapping snapshot 为 1,899 map decisions；对应 969 papers、930 repositories，rolling 12m 为 1,610，rolling 90d 为 889，future mapped 为 0。Deep/radar/C09 merge 最终形成 105 个 `deep-verify` decisions，并把 direct-open paper/repository evidence 与原 map entities 一并闭合到 `deep-verified` stage。最终 screening 为 1,899 map、105 deep-verify、136 defer、2,278 exclude；stage 为 1,773 mapped、221 deep-verified、2,413 discovered；assignment 为 1,994 primary、2,236 secondary、0 bridge。增量没有产生第 17 个一阶 leaf；它主要加厚 C09 coding/project memory，以及 C01 services、C11 portability、C12 security 和 C13 evaluation 等既有边界。这是 map-level saturation 的正信号，不是 open-world recall 证明。

必须保留一条边界：`--check` 证明 decision conservation、one-primary、future quarantine、ID 和 byte equality；它不证明分类器的语义判断正确。第二轮还没有像第一轮那样由另一个角色保存完整的独立分层 verdict ledger，尤其是未人工逐项阅读的 low-signal paper，仍是 mapping precision 风险。

## 7. 深度研究与选择质量

五个基础 deep packet 不是按项目类型分工，而是按问题链分工：

- foundations/lifecycle/control plane；
- representation/storage/retrieval/context compilation；
- experience/procedural/multi-actor/personalization/embodied；
- benchmarks/protocol comparability；
- security/privacy/integrity/operations。

每包必须同时给 scope、selection、sources、papers、repositories、claims、evidence、synthesis report 和 gaps。选择覆盖 foundation、2024–2025、rolling 12m、rolling 90d，并优先 foundation、current mechanism、engineering repository、benchmark 和 negative/contradiction。仓库与论文是平级证据对象；一个仓库可在没有 paper 的情况下凭 implementation relevance 入选。

最初五个主题 deep packets（不含后续 standards/adoption 与 C09）的 107 条 selection 按 canonical URL 去重为 98 个对象，其中 60 papers、34 repositories、3 products、1 dataset。包内 114 source rows 归并为 106 unique URLs；112 rows 标 T1、2 rows 是仅支持有界方法推断的 T3 research logs，113 rows `opened`、1 row `metadata-only`。119 条 packet-local claims 中 79 条 high-risk；229 个 evidence joins 保存 locator、relation、limitation 和 independent group。

GitHub engineering radar 是独立 engineering work unit，不是上述仓库的星标附录。它检查 59 个仓库，其中 48 `keep-deep`、4 `keep-lineage`、7 `watchlist`；与五个主题包按 canonical URL 合并前，选择/检查对象为 142 个：60 papers、78 repositories、3 products、1 dataset。这个 raw subtotal 只用于解释 worker coverage，不能直接当 final unique evidence。

C09 coding/project/environment memory 是第六个独立问题包；它补上通用 Memory 综述容易漏掉的 codebase、session handoff、artifact/state 与环境连续性。Standards/adoption 是第七个 thematic packet。它执行 18 条可回放查询（6 standards、12 adoption），审查 24 个 candidates，保留/延后 18 个 selection，并产生 27 sources（22 T1、5 T3）、30 claims 和 64 evidence joins。所有 research log 已规范为 T3；npm registry metadata 与外部引用查询拆开，避免“包存在/有下载”被写成采用。这个包能支持对 W3C Community Group、个人 IETF draft、MCP 邻接层、若干项目 spec 和 MemTools 的有界状态判断；它已由 supervisor 归并进 final ledger，但没有发现满足门槛的独立生产部署、外部 conformant implementation 或 round-trip/conformance result。

最终 supervisor merge 对 source identity 去重、保留 blocked source 状态，并把 research log 限定为 T3。Current bundle 为 385 sources（366 T1、0 T2、19 T3；384 opened、1 blocked）、464 claims、773 evidence joins、464 semantic checks；221 deep-verified entities 包含 72 papers、98 repositories、3 datasets、14 products、2 standards 和 32 direct `other` artifacts。这是 final ledger；0 execution 仍限制运行时结论。

这些数字不自动证明深度。真正的质量判断按维度保留：

- paper：publication/preprint status、original source、任务/数据/模型/metric、artifact、限制和独立复现；
- repository：canonical node/owner、commit、release、license、setup、tests/CI、layout、dependencies、maintenance、integration 和 independent adoption；
- benchmark：protocol fingerprint 与 comparability group；
- claim：直接性、T1、精确 locator、适用条件、反证和 clause-level semantic check；
- consensus：独立 evidence group、可比性、复现、时间与最强 minority view，而不是链接数投票。

Packet 中的 `published` 是 packet-local 候选状态；只有 supervisor 完成跨包去重、final source/claim/evidence remap、semantic audit 和 reader marker 后，才能成为 bundle 的 published deep claim。

## 8. GitHub 观察和趋势边界

GitHub radar 选择 59 个 foundation、active、recent、security、benchmark、protocol、storage、retrieval 和 coding-memory 候选，59/59 observation run 完成。每个 run 获取 repository metadata、latest release、default-branch commit，以及 rolling-90d commit pages；共保存 376 个 API request snapshots。

观察完整性为：59/59 有 current repository snapshot、commit count 和 contributor count；54 个在 90 日内有 push；39 个有 latest release；53 个有明确 license。缺 release/license 是 unknown，不编码为 0。

Radar 又在 fixed SHA 上检查 README、recursive tree、manifest/workflow/test path：58 complete、1 partial；没有安装或运行。它保存 203 source rows、207 claims、274 evidence joins。Packet 内两条 `source_type=research-log` 曾误标 T1；final merge 已降为 T3，并只允许它们支持 bounded corpus/run inference。这个已纠正的缺陷仍作为 provenance audit 记录，而不是从限制中抹去。

Stars 只有一个 GitHub observation，因此只能报告 cumulative snapshot。为补查增长信号，本轮对 59 个 radar 仓库调用 OSSInsight history；只有 1 个达到窗口 delta 门槛，3 个仅可诊断，55 个因与 GitHub 当前快照明显失配或无历史行而不可用。结合 GitHub 2026 年 7 月对公开 stargazer-list endpoint 的访问限制，本轮不发布 star growth/acceleration 排名。Commit/contributor、created/pushed/release activity 可说明近期工程活动，但不能单独证明成熟度、质量或采用。

## 9. 饱和与停止规则

不能因为达到某个 entity、query 或轮数就机械停止。停止判断以字段树和重要 cluster 为主，并回答：

- 是否产生新的一阶 cluster 或改变边界；
- 是否补入新近高信号实现；
- 是否出现可信 opposing stance/negative evidence；
- 是否找到 canonical artifact 或改变 decision conclusion；
- 剩余 gap 是否可明确且后续查询不再改变当前 scoped conclusion。

当前 packet 判断并不一致：benchmark 对一阶协议族较稳定；foundation/lifecycle 和 representation 的架构脉络稳定，但独立性能与工程保证较弱；experience、security、standards/adoption 仍保留不同程度的证据缺口。saturation 记录是信息增益日志和方法附录，不是报告成立的逐格许可证。只有当“没有发现某类证据”会直接改变决策时，才要求额外的多路径、连续无实质新增补查；普通停止判断以字段树不再变化、代表性实现已覆盖、近期信号已检查和残余缺口已披露为准。

## 10. 研究系统行为对照

- **STORM / Co-STORM：** 十个视角先于 final map；通过自然 labels、audit 和 canonical merge 改变初始结构。最终应引用 perspective 与 cluster iteration artifact，而不是只说“用了多视角”。
- **GPT Researcher：** 第一轮 mapping gaps 生成 Q0057–Q0074；全量增量 screening 后没有新增一阶 leaf，但改变了多个 leaf 的密度与边界。standards/adoption 又独立追加 18 条定向查询；没有 evidence 的 deployment、conformance、deletion、replication 等必须 abstain 或继续查。
- **Open Deep Research：** 五个隔离 packet 先写 raw evidence 与 compressed report；executive writer 应只消费 cluster/synthesis packet，不拼接 worker prose。
- **dzhng/deep-research：** query 记录 parent、iteration、information gain 和停止原因；本轮不是固定三 pass。

## 11. 关键限制

1. **增量 mapping 语义审计仍弱。** 1,191 个新增实体已全部有 decision，但人工覆盖是全仓库、全部 recent/likely/high-signal/future papers 加 80 条 low-signal 分层样本；其余 low-signal papers 由 strict classifier 判定。结构 `PASS` 不等于语义 `PASS`，也没有保存与第一轮同等的独立逐行审计 ledger。
2. **跨 provider identity 弱。** 4,319 个实体中未出现强标识符支持的跨 provider merge；Crossref/arXiv manifestation duplicate 仍可能存在，identifier-level count 是上界。
3. **Provider 偏倚。** Semantic Scholar 被 429 阻断；论文 discovery 主要来自 arXiv 和 Crossref，GitHub 只覆盖公开仓库，非英语、闭源、企业内部和非 GitHub artifact 易被漏掉。
4. **Breadth 与 downstream query 不能混算。** Breadth tranche 的 74 条 query 原本只有 adoption 0、standards 1；final 292-query ledger 在归并 deep/adoption/radar/C09 后有 adoption 75、standards 72 次 lane mention。后两个数证明 downstream verification provenance 已保存，不证明 early broad discovery 已有同等 lane coverage，也不能让 official product docs、stars 或 package downloads 代替独立 deployment/conformance evidence。
5. **早期 query 缺陷。** Q0001 precedence bug 已公开并由 Q0005 supersede，但其 noisy occurrence 仍保留在 discovery audit trail。
6. **Mapping error risk。** 第一轮 120 条分层审计发现 8/60 map/deep false inclusion；20 override 修复已知错误，但不证明其余项目准确。第二轮 preview 又实际暴露 generic framework、provider boundary 和 evaluation-keyword 漂移；最终规则已修正，但尚无独立总体 error estimate。
7. **Future metadata。** 116 条 post-cutoff 记录被 quarantine；粗粒度 provider date 仍可能错标版本或 publication status。
8. **Star-history 不可可靠复原。** GitHub stargazer-list 已受限；OSSInsight 在 59 仓核验中只有一个对象达到可用覆盖。因此没有 stars velocity 排名，近期趋势改由 creation/push/release/commit/contributor 交叉观察；这些仍不等于 adoption。
9. **无执行真值。** 没有安装、测试或 benchmark execution；setup/CI 仅 documented/present。
10. **深研仍偏 author evidence。** 多个 2026 机制/安全结果是 preprint，独立 replication、删除传播、tenant isolation、统一成本和生产 failure data 仍缺。
11. **Packet merge 已闭环关键 identity/joins，未执行仓库。** Supervisor 已归并 385 sources、464 claims、773 joins 与 464 semantic checks；但一个 deep source blocked、31 个 direct `other` entity 无日期窗、repository execution 为 0。未执行是本轮只读研究的明确边界，不是默认失败；它只限制安装可复现性、真实性能和运行行为判断。
12. **数量不可补偿，细节也不能反客为主。** 即使 discovered、paper、repo 和 mapped 数量远超 floor，也不能掩盖字段树错误、近期趋势缺失、重要簇无深度、关键事实错引或最终 synthesis 退化成项目简介；反过来，某个非关键审计字段不完整，也不应让整体方向正确、边界诚实的报告失败。
13. **Audit 可重放粒度有限。** [audit-report.md](../../mapping/audit-report.md) 保存了 seed、分层口径、汇总发现和扩展检查范围，[audit-overrides.jsonl](../../mapping/reconciliation/audit-overrides.jsonl) 保存了 20 条实际改判；但 120 条样本的逐行 verdict 没有单独 ledger，因此可以复核抽样设计和落盘 override，不能逐条重放全部审计判断。
14. **Radar research-log tier 曾发生漂移。** GitHub radar packet 的两条 research-log source 曾误标 T1；merge 已改为 T3。最终 bundle 中的 T3 research logs 必须继续只支持有界方法推断，不能在 reader rewrite 中再次升级。
15. **Standards/adoption 是 bounded packet。** 18 条专项查询中的 private repositories、非 GitHub 代码、非英语材料与未索引 operator artifacts 不可见；GitHub code-search 还发生过 rate limit。`未找到`只限于记录的 query/time/public-index 范围，不是普遍不存在。

## 12. 可复现步骤

1. 从 [research_plan.json](../research_plan.json) 读取 as-of、lanes、windows 和 targets。
2. 按 [queries.jsonl](../queries.jsonl) 重放 exact requests；用每行 `raw_snapshot_paths` 和 response hash 检查原始响应。
3. 重新编译 breadth [discovery_results.jsonl](../discovery_results.jsonl) 的原始 tranche，验证 7,535 occurrence 与 4,319 search entity；再用 merge summaries 解释 final 7,634 rows / 4,407 entities，不能把新增 88 direct evidence entities 算成 broad search yield。
4. 对第一轮，校验 [packet-manifest.json](../../mapping/packet-manifest.json)、[all-proposals.jsonl](../../mapping/all-proposals.jsonl)、[audit-overrides.jsonl](../../mapping/reconciliation/audit-overrides.jsonl) 和 [decision-ledger.jsonl](../../mapping/reconciliation/decision-ledger.jsonl)。
5. 用 [materialization-summary.json](../../mapping/reconciliation/materialization-summary.json) 复核 count conservation、DAG acyclic、future-not-mapped 和 one-primary invariants。
6. 对第二轮，核对 [gap-discovery-execution.jsonl](../../gap-discovery-execution.jsonl)、import spec、dry-run 与正式 compile summary；然后在 [mapping/incremental](../../mapping/incremental/README.md) 运行 `python materialize_incremental_mapping.py --check`，验证 1,191 decisions、1,264 新 assignments 与 bundle byte equality。
7. 对 deep packet，先按 canonical URL/entity ID 去重，再检查 source access、claim/evidence joins、paper/repo cards 和 gaps；不要直接相加 worker totals。
8. 对 standards/adoption 原始包，从 [queries.jsonl](../../work/deep-packets/standards-adoption/queries.jsonl) 追到 [claims.jsonl](../../work/deep-packets/standards-adoption/claims.jsonl)、[evidence.jsonl](../../work/deep-packets/standards-adoption/evidence.jsonl) 和 [sources.jsonl](../../work/deep-packets/standards-adoption/sources.jsonl)，再核对 [deep-merge-summary.json](../../work/deep-merge-summary.json) 的 ID remap；保持 T3 bounded inference 与 T1 direct fact 分离。
9. 对 GitHub radar，核对 59 个 `.run.json` 的 request hashes与 [github-radar-merge-summary.json](../../work/github-radar-merge-summary.json)；不要从一次 stars observation 计算增速。
10. 最后运行 normal/strict bundle validator、reader hash/link validator 和 independent review。Schema pass 只证明内部一致；终审重点是字段结构、广度与新鲜度、选择性深度、关键事实可靠性和综合判断，而不是审计记录数量。


<!-- process:method -->
