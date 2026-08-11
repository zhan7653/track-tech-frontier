# v09 与 v08 的实质对比

## 结论

v09 不是在 v08 报告上加更多条目，而是替换了研究架构。v08 的优势是小集合上的 evidence/provenance control；它的失败是把这个小集合误当成完整领域，并从 source cards 直接写报告。v09 把“搜到什么、领域怎么分、哪些值得深读、跨来源结论是什么”拆成独立阶段。

当前 v09 已显著解决输入广度、近期 GitHub、两轮 field mapping 和并行深研问题；七个 deep packets（含 C09 coding/project-memory 与 standards/adoption）与 GitHub radar 已归并为 final evidence ledger。尚未自动解决的是增量 mapping 的独立语义抽审、真实 deployment/conformance、repository execution 与部分独立复现。

对比依据是 v08 的 [historical decision](../../../v08/change.md)、[independent review](../../../v08/review.md) 和 [bundle report](../../../v08/bundle/report.md)，以及 v09 的 [user feedback](../../../USER_FEEDBACK.md)、[research contract](../../research-contract.md) 与当前账本；不沿用 v08 已被用户推翻的“94/100 即最终接受”结论。

## 1. 输入规模和漏斗

| 项目 | v08 | v09 当前 | 解释 |
|---|---:|---:|---|
| Query | 20，固定 Map 6 / Focus 8 / Verify 6 | 74 breadth queries；归并 downstream verification 后 final 292 | v09 follow-up 由 map gaps 生成；downstream query 不冒充 breadth |
| Search / provenance rows | 未单独保留大规模 occurrence universe | 7,535 breadth occurrences；final 7,634 | occurrence 与 entity 分开，direct-open provenance 不冒充 search yield |
| Candidate / merged entity | 69 candidates | 4,319 breadth entities；final 4,407 | final 新增 88 direct/deep entities；仍可能有 manifestation duplicate |
| Papers | 19 paper cards | 2,494 breadth；969 map decisions；72 final deep-verified | breadth、map、depth 三个数字分别报告 |
| Repositories | 13 repo cards | 1,825 breadth；930 map decisions；98 final deep-verified；59 radar observations | GitHub 既参与 taxonomy，也参与独立工程深检 |
| Recent coverage | 主要 2023–2026 小集合，近期不是独立 gate | rolling-12m 2,843；rolling-90d 1,403；future 116 quarantine | 新鲜度独立于 general quality |
| Mapping / final stage | 53 retained / 11 excluded / 5 deferred | 1,899 map decisions；final stage 1,773 mapped + 221 deep-verified | mapping 前置为全 breadth corpus；增量 semantic audit 仍弱 |
| Sources | 45 | final 385 sources（366 T1、0 T2、19 T3；384 opened、1 blocked） | merge 已去重并修正 radar research-log tier |
| Claims / evidence | 66 / 177 | final 464 claims / 773 joins / 464 semantic checks | v09 已继承 claim closure；运行时与 reader-level gate仍分开 |
| Repository execution | 0 | 0 | 两版都诚实不宣称执行 |

## 2. 工作流变化

### v08

v08 的工作流是一个三 pass 的精密筛选器：冻结 requirements，执行 20 query，保留 53 candidates，打开 45 sources，写 66 atomic claims，再做 semantic audit。它适合做可追溯技术 memo，却不适合证明“完整当前领域”。

它的结构性后果是：

- taxonomy 主要来自 19 papers/13 repos 的 deep shortlist；
- report 的自然写作单元容易变成论文、仓库或产品；
- GitHub 被放在 paper/artifact 后面，没有近期仓库雷达；
- fixed three-pass 与 source budget 让后续 gap expansion 提前结束；
- 16 requirements 被误当成 STORM-style perspective expansion 的充分替代。

### v09

v09 的工作流为：

```text
用户合同与视角
  → 高召回 paper/GitHub discovery
  → occurrence-first provenance 与 stable-ID entity compile
  → 全语料独立 mapping
  → audit + canonical field DAG
  → map-guided gap/deep-focus/verify/adversarial search
  → 每个重要问题组独立 deep packet
  → propositions / contradictions / history relations
  → multi-file reader synthesis
```

这个变化使“广度”和“深度”成为两个可单独失败的 gate。大量 discovery 不会自动提高 claim quality；少量精确 deep evidence 也不能掩盖未覆盖的 cluster 或 recent window。

## 3. 输出结构变化

| 用户指出的问题 | v08 | v09 目标与当前 artifact |
|---|---|---|
| 像论文/仓库简介 | 一个主 report，统一表后仍以 source-led prose 为主 | 先 materialize field DAG、cluster packets、consensus/relations，再写 executive；禁止从 raw source cards 直接写 |
| 没有领域脉络 | 历史线与横向表存在，但由小 shortlist 形成 | 5 roots + 16 leaves，final 1,994 primary / 2,236 secondary assignments；另保存 merge/split rationale |
| 没有共识/争议权重 | claims 很精确，但 independent stance weighting 弱 | proposition 需区分 independent groups、directness、reproduction、comparability、freshness、negative evidence 和 reversal criteria |
| 每个部分不够深 | 全报告共用少量 paper/repo cards | 七个 deep packets（含 C09 与 standards/adoption）；每包有 standalone scope、source/claim/evidence、report 和 gaps；14 个 important clusters 均有 reader report |
| GitHub 只是附录 | 13 pinned repos，偏 foundational/canonical | 1,825 discovered repos + 59 complete observations；creation/activity/release/maturity/adoption 分列 |
| 最近趋势跟不到 | 无完整 recent-created/radar | created rolling windows、pushed query、selected observation、recent watchlist；没有两个 stars observation时拒绝 velocity |
| 单文件太简陋 | `report.md` / `output.md` | README、executive、field tree、landscape、history、consensus、GitHub radar、benchmark map、method、source index、cluster reports、project dives |

## 4. 参考研究系统行为

### STORM / Co-STORM

v08 把 16 requirements 视作多视角已完成，但没有保存“视角如何改变 outline”。v09 先生成十个 stakeholder/technical perspectives；六个 mapper 的自然 labels、120 条独立 audit 和 canonical reconciliation 共同把初始 outline 改成 5 roots/16 leaves。cluster iteration log 已保存新增、merge/split 与无变化轮次；是否完成由字段结构、代表性覆盖、近期信号和残余缺口共同判断。

### GPT Researcher

v08 有 query→candidate→source trace 和 bounded abstention，但 early findings 没有大幅生成新 query。v09 由 mapper gap 产生 Q0057–Q0074，明确分为 gap-fill、deep-focus、verify 和 adversarial；例如 storage/index、coding memory、forget/rollback、cost、protocol、no-memory/BM25 和 poisoning artifact 都来自第一轮缺口。

### Open Deep Research

v08 是单分支写作。v09 将 foundations、representation、experience/multi-actor、benchmark、security/operations 交给隔离 packet；worker 返回 raw sources/claims/evidence 和 compressed report，supervisor 应合并 identity/evidence，而不是拼接 prose。final writer 只消费已归并的 canonical ledgers、cluster syntheses 与工程 profiles；最终交付再检查综合质量、关键证据、链接和 hash。

### dzhng/deep-research

v08 有三 pass budget，却把 pass 数当停止机制。v09 query 保存 parent、iteration、information gain 和 gap；cluster packet 分别做 scoped saturation 判断。当前多个 packet 明确为“架构叙述已饱和，独立复现/工程保证未饱和”，比全局一刀切更真实。

## 5. v08 仍然更强的部分

不能因为 v09 数量更大就否定 v08 的工程价值。v08 已经闭环：

- 66/66 exact claim markers；
- 177 evidence joins；
- 66 clause-level semantic checks；
- report/output byte equality；
- normal/strict validator 通过；
- 13 repository cards 全部 pinned，execution truth 诚实为 0；
- benchmark paper↔repo↔dataset 关系和 publication status 较整齐。

v09 已完成跨包 source identity dedupe、ID remap、464 条 claim semantic checks 和 773 个 evidence joins；因此 v08 的 evidence-closure 优势已被实质继承。final reader 的结构、关键证据、marker、hash 与链接由 deliverables manifest 和独立终审检查；repository execution 仍为 0；不能用 4,407 的大数字抵消这些不同层级的缺口。

## 6. 按用户反馈逐项验收

| 用户反馈 | v09 状态 | 证据 | 当前 verdict |
|---|---|---|---|
| 论文、仓库太少 | 2,494 papers、1,825 repos discovered | bundle entities/discovery ledger | 已显著改善 |
| 新的不够多 | rolling-12m 2,843、rolling-90d 1,403；GitHub created/activity 分开 | time windows、compile summary | 已显著改善，但 recent quality仍需deep |
| 先广度再深度 | 4,319 breadth；1,899 map decisions；221 final deep-verified | mapping/deep merge | 架构与 evidence merge 已实现；增量独立语义审计仍弱 |
| 输出只是简介 | field DAG + deep packets + synthesis branches + merged evidence ledger | mapping reconciliation、work/synthesis | 所有最终 reader deliverables 已生成并进入独立复审 |
| 需要像综述一样分块/共识 | 16 leaves、proposition/consensus contract | clusters、consensus synthesis work | final 文字、链接、marker 与 hash 已进入独立复审 |
| GitHub 工程性不够 | 28 GitHub queries、59 fixed-SHA cards/observations、207 repo claims | github-radar | current-state 已改善；production adoption/execution仍弱 |
| 最新高星/趋势追踪 | created/pushed/high-attention searches；stars只signal | queries、observation runs | signal 已覆盖；没有两点stars因此不声称增长 |
| 不考虑成本、多阶段、多文件 | 74 全局 queries、六个 mapper、七个 deep packets（含 C09 coding/project-memory 与 standards/adoption）、GitHub radar、18-query standards/adoption 专项、multi-file reader suite | stage artifacts | 已实现多阶段；所有 reader deliverables 均进入 manifest 和严格验收 |
| 对比 research repos 不够真实 | 保存 perspective、recursive query、worker packet、compression evidence | contract/query/deep packet | final compression 的 perspective→outline→packet→synthesis 消费链已单独落盘 |

## 7. 最终验收边界与仍保留的限制

1. 第二轮 1,191 个新 entity 虽已全量 decision/materialize，但 low-signal papers 只有 80 条分层人工样本，其余靠 strict classifier；结构自检不是独立语义审计。
2. Standards/adoption 已进入 final ledger，并确认两个 qualified weak external integration signals；但没有当前版本独立 conformance、可归因 production deployment 或双向 round-trip evidence，bounded abstention 不能写成普遍不存在。
3. Final merge 已形成 385 sources、464 claims/semantic checks、773 joins，并把 radar 两条 research log 降为 T3；final reader suite 已保持这条 tier 边界。
4. 一个 source blocked，31 个 direct `other` entities 无日期窗，不能用于 freshness denominator。
5. 没有 repository execution；59 GitHub stars 都是单点快照。
6. 多个 packet明确指出 independent replication、delete propagation、tenant isolation、cost 和 production adoption 未饱和。
7. Final reader deliverables、relations/syntheses、saturation/link/hash manifest 由本轮真严格 validator 与独立复核共同验收。

v09 的正确验收标准不是“比 v08 大很多”，而是：以更广、更近的 corpus 形成稳定 field map；把深度放在重要、近期和决策相关的簇与项目；最终 synthesis 不按来源介绍；同时保证关键事实的 claim-level correctness。字段树、趋势、核心深度、关键证据和最终综合属于不可互相替代的结果门；逐格 coverage proof、逐句低风险建账和仓库执行则按实际决策价值启用。
