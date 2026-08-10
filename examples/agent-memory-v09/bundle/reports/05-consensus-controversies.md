# Agent Memory v09：共识、分歧、成熟度与决策

状态：最终跨包综合；as-of `2026-08-10`。本稿消费 canonical breadth map、七个 deep packets（含 C09 与 standards/adoption）与 GitHub radar，不从 broad-discovery metadata 直接引入技术事实。breadth map 的稳定口径是 1,899 项；direct provenance 归并后 ledger 中 mapped/deep-verified 为 1,994 项（989 papers、954 repositories，另含 dataset/product/standard/other），C01–C14 为 important。这些数字描述筛选与证据对象，不代表相同数量的独立证据组。

## 怎么读这些判断

这里的“共识”不是论文数、链接数或 star 数投票。论文与同作者 repository 合并为同一 independence group；厂商 README 只证明 inspected implementation/documentation surface；独立 reproduction、negative result 和可比较 protocol 对普遍化主张权重更高。结论使用四级：

- **dominant**：多个真正独立的 mechanism、benchmark、implementation 或 negative groups 在明确条件下方向一致，且没有同强度反证。
- **mixed**：机制方向一致，但收益、适用范围或风险随 protocol 变化。
- **disputed**：存在可直接改变结论的强反例或 ranking reversal。
- **evidence-thin**：没有足够直接、独立、可比较证据；正确动作是 abstain 和补证据。

“成熟度”与“结论置信度”分开：我们可以高置信地判断某方向**尚不成熟**。成熟度按 established / emerging / immature 标注；它不是项目排行榜。

## 八个待验证命题的裁决

| 命题 | 当前裁决 | 置信度 | 成熟度 | 决策含义 |
|---|---|---:|---|---|
| CP-01 lifecycle/control 比 store/retrieval 更接近核心工程问题 | **dominant，有条件共识** | high | 分层架构 established；transaction/learned control emerging | 对持久、可变、action-bearing state，先定义 write/update/forget/recover contract；静态只读 QA 不必照搬全套 |
| CP-02 temporal/relational/conflict-heavy tasks 需要超越 flat similarity | **mixed** | medium | 实现 active；成本对齐优势 immature | 把 time/version/scope/provenance 放进 IR；是否上 graph/active navigation 由匹配基线决定 |
| CP-03 selective write/consolidation/forgetting 降成本但制造删除与隐藏依赖风险 | **disputed** | high | heuristic established；可靠 purge/repair immature | raw trace 作为可追溯底座；summary/profile/skill 作为可重建派生状态；不可逆 mutation 单独 gate |
| CP-04 personalization utility 与 privacy/drift/staleness 同时增长 | **mixed** | medium | profile API established-active；longitudinal assurance immature | 最小必要 profile、principal scope、valid time、consent/correction/delete 和 dependency repair |
| CP-05 shared memory 提升复用但放大 contamination/authority/isolation | **mixed / evidence-thin on net benefit** | medium | team/shared implementations emerging；独立安全证据 immature | 默认不共享 raw profile/world state；只共享带 provenance、scope、适用条件和 revoke path 的 artifact |
| CP-06 benchmark ranking 对 protocol 敏感，单一 leaderboard 不足 | **dominant** | high | family taxonomy established；harmonized rerun immature | 用 protocol-family 向量 scorecard，不合并静态 QA、action、multimodal、shared 和 security 分数 |
| CP-07 model-native 与 external memory 是不同 assurance boundary | **evidence-thin，暂不裁决优劣** | high（对“证据不足”） | direct comparison absent | 不用 latency/集成便利推断 inspect/delete/provenance；补 external-vs-parametric 对齐实验 |
| CP-08 stars/recent push 只能触发调查 | **confirmed method guardrail** | high | N/A | GitHub first-class，但 popularity、maturity、adoption、performance 分栏；growth 需多时点观测 |

## 1. 架构共识：Memory 已经不是一个 `search(q, k)`

<!-- synthesis:CNS-S09 claims:FND-C17,FND-C21,FND-C23,REP-C12,REP-C14,REP-C22,EXP-C18,EXP-C19,EXP-C20,OPS-C01,OPS-C07,OPS-C12,OPS-C14,OPS-C16,OPS-C24,OPS-C27,BEN-C25 clusters:MM-C01,MM-C02,MM-C03,MM-C04,MM-C05,MM-C07,MM-C08,MM-C11,MM-C12 -->

跨七包最稳定的综合不是“选向量库还是图数据库”，而是一条可审计的数据流：

```text
raw turns / tool outcomes / observations
  → typed + scoped + time/versioned + provenance-bearing records
  → vector / lexical / entity / graph / temporal candidate access
  → scope/time/trust/cost-aware filtering and ranking
  → budgeted context compilation with conflict and source labels
  → explicit admit/update/consolidate/forget/delete/recover transaction
  → action-time authorization and outcome-linked write-back
```

FND 将 persistent state 综合成 data、retrieval、mutation/control 三平面 [FND-C23]；REP 进一步指出 provenance、time/version、scope 与 retrieval budget 必须贯穿 representation→context compilation，而不是在 top-k 之后补救 [REP-C22]；OPS 的 write→retrieve→action 攻击链表明，一条被持久化的错误或恶意记录会跨时间获得新的执行机会 [OPS-C01][OPS-C07]。共享和个性化包又把 principal/scope 与 user/world identity 加进状态模型 [EXP-C18][EXP-C19][EXP-C20]。

这形成 CP-01 的有条件共识：只要状态会跨 session 改变、被纠正、被删除或驱动工具行动，lifecycle/control 就不是“高级功能”，而是 correctness boundary。MemGPT、MemoryBank 与 MemoryOS 分别从 tier/control、store-retrieve-update 和 three-tier/four-module 方向支持分层 [FND-C03][FND-C05][FND-C11]；MemTxn 与 ForgetEval 将 admission/version/recovery 和 mutation-plane placement 变成可单独测试的机制 [FND-C17][FND-C21]。但 LightMem 的独立复现提醒：在固定 constructed store、只读 QA 和匹配 retrieval depth 的局部问题里，raw-turn Naive RAG 可以更强 [REP-C05][REP-C06]。因此完整控制面是持久可变系统的基线，不是每个一次性问答任务的强制复杂度。

<!-- synthesis:CNS-S01 claims:FND-C03,FND-C05,FND-C11,FND-C14,FND-C17,FND-C21,FND-C23,BEN-C03,BEN-C05,BEN-C06,BEN-C16,OPS-C07,OPS-C27,REP-C06 clusters:MM-C01,MM-C02,MM-C04,MM-C05,MM-C07,MM-C13 -->

**成熟度判断。** 分层、持久 store、hybrid retrieval 与 profile/episodic separation 已有多个论文和仓库实现表面，属于 established-active；source-supported transaction、control-plane placement、learned operation policy 和跨派生物删除属于 emerging/immature。没有一个本次执行过的仓库证明六段链全部闭合。

**反转条件。** 只有跨 backend、同模型、同预算的独立对照显示 passive/raw-history baseline 在 update、conflict、forget、recovery、action success 和成本上持续等同或优于显式 control plane，才应把 CP-01 降为 mixed。

## 2. 表示与检索：结构是能力，不是自动优势

<!-- synthesis:CNS-S02 claims:REP-C01,REP-C02,REP-C03,REP-C05,REP-C06,REP-C10,REP-C11,REP-C14,REP-C16,REP-C22,FND-C09 clusters:MM-C02,MM-C03,MM-C04,MM-C07,MM-C13 -->

现有机制正在把 memory unit 从“任意文本块”拆成 fact、event、profile、episode、belief、version 和 relation。AtomMem 的 atomic facts→event/profile→associative graph [REP-C01]，bitemporal store 的 identity/version + valid/transaction time [REP-C02]，A-MEM 的 structured note + evolving links [FND-C09]，以及 MemMachine 的 episodic graph、SQL profile、working memory 分离 [REP-C14]，都说明表示层承担了以后无法无损补回的语义。

工程上也没有一个索引足以覆盖全部问题。Mem0 文档化 semantic/BM25/entity fusion 与 temporal ranking [REP-C12]；Cognee 展示 vector + graph + ontology 的 self-hosted 组合 [REP-C11]；HippoRAG 把 knowledge graph 与 Personalized PageRank 接到 index→QA 路径 [REP-C16]。这些仓库证明“组合访问路径已经进入实现”，不证明 graph 一定优于 flat retrieval。

反证来自两个方向。第一，bitemporal 作者自己的 60-question sample 中，time-travel path 对 knowledge update 有利但 temporal reasoning 下降，作者归因于 post-filter dilution [REP-C03]。第二，独立 LightMem 复现仅替换 retriever 就把 answer accuracy 从 58.1% 改到 75.5%，并发现 matched depth 时 raw turns 通常更强、constructed memory 的优势主要出现在严格 answer-token budget [REP-C05][REP-C06]。这使 CP-02 成为 **mixed**，而不是 graph/temporal 共识。

**决策。** 先定义可迁移 IR：principal/tenant/user/agent/session scope、type、source、valid time、transaction time、version、conflict 和 index version。查询先 hard-filter scope/time/provenance，再 multi-index candidate fusion，最后记录 per-route budget、rerank trace 和 compiled tokens。只有 matched baseline 证明关系导航是瓶颈时，再增加 graph traversal 或 active navigation。

**反转条件。** 如果公开、可复现的 matched-cost 实验显示 flat retrieval 在 temporal/conflict/relational tasks 上持续匹配 structured approaches 且维护成本更低，“通常需要超越 flat”应撤销；反过来，多 backend 稳定领先才足以升级为 dominant。

## 3. Lifecycle、压缩和遗忘：我们高置信地知道“没有通吃策略”

<!-- synthesis:CNS-S03 claims:FND-C06,FND-C14,FND-C16,FND-C19,FND-C20,FND-C21,FND-C22,REP-C03,REP-C05,REP-C06,EXP-C13,EXP-C15,BEN-C05,BEN-C06 clusters:MM-C05,MM-C07,MM-C08,MM-C10,MM-C13 -->

CP-03 的裁决是 disputed，但对“争议存在”的置信度很高。MemoryBank 把 time/importance forgetting 变成显式 updater [FND-C06]；MemCon 将 retrieve、plan injection、re-retrieve、consolidate、forget、no-op 变成 online policy action，并报告其协议内的 task/token 收益 [FND-C14][FND-C16]；ForgetEval 把 supersede/release/purge 与 recall 分开，发现不同 placement 覆盖互补 failure modes [FND-C21][FND-C22]。这些都支持“操作符选择应受控制”。

但没有证据支持“总是摘要”或“总是遗忘”。Budgeted consolidation 明确指出 retention 保留 detail，consolidation 在紧预算下提高 coverage per token，却可能删除 query-critical evidence，并拒绝给 Merge/Abstract/Rewrite 普遍排序 [FND-C19][FND-C20]。LightMem reproduction 观察到 constructed store 丢失 answer-relevant information [REP-C06]。STALE 则表明 stored state 更新之后，行为仍可能围绕旧值规划 [EXP-C13]；这意味着 database mutation 并不等于依赖修复。MeMento 在自己的 multimodal preference protocol 内报告更低 memory use 与更高 accuracy [EXP-C15]，但不能跨协议变成“压缩总有效”。

<!-- synthesis:CNS-S13 claims:REP-C01,REP-C04,REP-C05,REP-C06,REP-C17,REP-C18,FND-C19,FND-C20,EXP-C15 clusters:MM-C03,MM-C04,MM-C05,MM-C07,MM-C13 -->

Constructed versus raw memory 是一个独立争议面。SimpleMem/AtomMem 等作者路线支持 structured construction [REP-C01][REP-C04]；独立 reproduction 则显示 retriever、k/depth 和 answer-token cap 能反转结论 [REP-C05][REP-C06]。因此所有“memory compression 提升”都必须同时公布 raw baseline、source-span coverage、candidate budget、compiled token budget、reader/judge 和数据版本。

**当前最稳妥实现。** append-only raw evidence + versioned derived state。summary、profile、semantic fact、procedure 和 embedding 是可以重建或撤销的派生物；delete/overwrite 必须说明 logical hide、supersede、physical purge、index/cache/profile/backups 传播和 recovery。learned controller 可以在稳定 primitive 上选择操作，但不能不受约束地拥有 irreversible mutation。

**反转条件。** 如果多系统 matched-budget 复现证明某一 consolidate/forget operator 在 detail retention、action success、privacy deletion、rollback completeness 和 cost 上跨任务稳定占优，争议才可收窄。

## 4. Memory 的主体：procedure、person、team 和 world 不能混为一个 store

EXP packet 给出了比“episodic/semantic”更可执行的边界：看 memory 允许什么 state transition。

- **Experience/procedure**：episode/feedback 被编译为 reflection、instruction、script 或 executable skill，供以后行为复用。Reflexion、Voyager 与 MemP 分别覆盖 verbal reflection、code skill 和 trajectory→instruction/script [EXP-C01][EXP-C03][EXP-C09]。
- **Person/identity**：user fact、preference、persona 与 self-state 必须按当前时间、同意和纠正解释。POLAR 把 personalized semantic/visual context 与 embodied episodes 分开 [EXP-C12]。
- **Team/principals**：共享 pool 只解决 availability；private/shared fragments、provenance、dynamic read/write policy 才解决 authority [EXP-C05][EXP-C06][EXP-C18]。
- **World**：visual/spatial state、visibility、action and feedback trail 解决部分可观测环境中的“现在发生了什么”。AriGraph、WorldLines 和 DunphyBench/MeMento 属于这一边界 [EXP-C08][EXP-C14][EXP-C15]。

错误替换会直接制造 failure：把 raw chat 当 skill，无法表达 procedure applicability；把一个 global vector store 当 organization memory，无法表达 principal 或 revoke；把 current summary 当 temporal profile，会接受 stale premise；把文本摘要当 world model，会丢失 visibility 和 action consequence。

### Personalization：净效用是 mixed

<!-- synthesis:CNS-S04 claims:FND-C05,REP-C07,REP-C13,REP-C14,EXP-C12,EXP-C13,EXP-C19,OPS-C03,OPS-C14,OPS-C15,OPS-C16,OPS-C18,OPS-C19 clusters:MM-C08,MM-C10,MM-C12,MM-C13 -->

工程实现已经出现 profile/episodic 分离、scope 与 TTL/revision/forget API：Supermemory、MemMachine 和 Microsoft 文档分别提供了这些表面 [REP-C13][REP-C14][OPS-C18][OPS-C19]。但可信搜索研究指出 semantic relevance 不等于 contextual appropriateness，可能导致跨域泄露、迎合、tool drift 或 jailbreak [REP-C07]；MEXTRA 提供 black-box private-memory extraction 证据 [OPS-C03]；DP-MemView 把 repeated responses 的 cumulative leakage 单独建模 [OPS-C14][OPS-C15]；STALE 又暴露了“取回更新证据但行为仍接受旧 premise” [EXP-C13][OPS-C16]。

因此目前共识不是“profile 越多越好”，而是：个性化必须是 temporal identity resolution + scope + consent/correction/delete。净效用需用长期 matched no-profile baseline 验证。

### Shared memory：有实现方向，没有已证明的净收益

<!-- synthesis:CNS-S05 claims:EXP-C05,EXP-C06,EXP-C18,EXP-C22,BEN-C11,BEN-C13,OPS-C10,OPS-C11,OPS-C19,OPS-C26,OPS-C27 clusters:MM-C06,MM-C08,MM-C11,MM-C12,MM-C13 -->

INMS 代表 shared pool + mediator；Collaborative Memory 代表 private/shared + provenance + dynamic policy [EXP-C05][EXP-C06]。MEMTRACK 与 GroupMemBench 又说明 organizational timeline 和 speaker/audience state 是不同于 dyadic QA 的评测对象 [BEN-C11][BEN-C13]。实现侧，Acontext、TencentDB Agent Memory 等展示 skill-file distillation 与 layered team memory，但这些 repository surfaces 不证明安全或采用 [EXP-C22]。

MAFIA 和 Salami 提醒共享读取面会遇到 benign-pool dilution、active auditing 和 individually benign but jointly harmful fragments [OPS-C10][OPS-C11]。因此 shared-memory 的条件共识是“scope/authority/provenance 是必要设计项”，而不是“shared memory 已经证明提高团队效能”。

## 5. 安全共识：威胁是 lifecycle，防御证据仍薄

<!-- synthesis:CNS-S11 claims:OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C09,OPS-C10,OPS-C11,OPS-C14,OPS-C16,OPS-C27,REP-C07,EXP-C18,BEN-C16 clusters:MM-C05,MM-C08,MM-C11,MM-C12,MM-C13 -->

多个独立 2024–2026 组已经覆盖不同 attack prerequisites：AgentPoison 的 persistent backdoor [OPS-C01]、MINJA 的 query/observation-only injection [OPS-C04]、eTAMP 的 environmental write path [OPS-C05]、sleeper memory 的 delayed retrieval→action [OPS-C07]、MAFIA 的 benign pool + active auditing [OPS-C10]、Salami 的 collusive fragments [OPS-C11]，以及 MEXTRA/DP-MemView 的 read/transcript privacy [OPS-C03][OPS-C14]。这些协议的 attack rate 不能合并，也不证明生产 prevalence；但它们共同建立了 dominant threat-surface 判断：安全边界跨 write、mutation、retrieve、prompt、action 和 repair。

provenance 是必要而非充分。MutMem 绑定 signed predecessor-linked transitions，却明确不证明 content truth [OPS-C12][OPS-C13]；STALE/StateAuditor 区分 chronology/provenance 与 semantic supersession [OPS-C16][OPS-C17]。Microsoft、AWS、Google 和 mem0 提供 scope、TTL/CRUD、memoryId、revision、IAM、delete 等治理接口 [OPS-C18][OPS-C19][OPS-C20][OPS-C21][OPS-C22][OPS-C23][OPS-C26]，OWASP Agent Memory Guard 文档化 detector→policy→rollback 与 source class [OPS-C24][OPS-C25]；这些是可组合 control points，不是完整防御的独立证据 [OPS-C27]。

当前 release baseline 应包含：每类 write channel 的 quarantine/admission、principal/tenant/source/authority provenance、scope/purpose/freshness-aware retrieval、action-time reauthorization，以及覆盖 raw record、summary、embedding/index、revision、cache、backup、profile 和 trace 的 deletion/repair test。

## 6. Benchmark 共识：先选失败模式，再选协议

<!-- synthesis:CNS-S06 claims:BEN-C01,BEN-C02,BEN-C03,BEN-C05,BEN-C07,BEN-C12,BEN-C16,BEN-C22,BEN-C25,REP-C05,REP-C06,REP-C17,REP-C18,EXP-C21,FND-C13 clusters:MM-C04,MM-C05,MM-C07,MM-C08,MM-C10,MM-C11,MM-C12,MM-C13 -->

BEN packet 已把第一阶协议拆成五组：static conversational QA；incremental lifecycle；action/state；multi-party/multimodal/implicit context；reliability/security [BEN-C22]。LoCoMo/LongMemEval 测 evidence localization 与 answer production [BEN-C01][BEN-C02]；MemoryAgentBench、Memora、HaluMem 测 incremental ingest/update/forget 与 operation failure [BEN-C03][BEN-C05][BEN-C06]；Mem2ActBench 和 MemoryArena 把 memory 接到 tool parameters 和 interdependent actions [BEN-C07][BEN-C12]；MemSecBench 追踪 Write–Execute–Forget [BEN-C16]。

<!-- synthesis:CNS-S10 claims:EXP-C01,EXP-C02,EXP-C03,EXP-C09,EXP-C13,EXP-C16,BEN-C07,BEN-C12,BEN-C22,BEN-C25,OPS-C16 clusters:MM-C05,MM-C06,MM-C08,MM-C10,MM-C13 -->

跨包的更强共识是：如果系统声称 memory 会改善后续行为，就必须在 later decision/action loop 验证，而不能只交一个 recall score。固定-history QA 是必要诊断，但不证明 procedure reuse、state revision、tool grounding、embodied planning 或 safe action。内部 scorecard 应分别报告：

1. recall + evidence localization；
2. update/conflict/forget + stale penalty；
3. tool/action grounding + trace；
4. multi-party/tenant scope；
5. multimodal/world-state；
6. implicit/procedural behavior；
7. write→execute→forget security；
8. token/latency/storage/rebuild/review cost。

每个数字必须绑定 dataset/version、input construction、memory access、model/prompt、retriever/k、context/tool budget、judge/metric、seed、artifact 和 runtime。OmniMemEval/MemoryData 是 harness candidates，不是新的独立 score authority [BEN-C23]。

## 7. GitHub 工程证据：一等输入，不是项目简介或星标排行榜

<!-- synthesis:CNS-S12 claims:FND-C04,FND-C10,FND-C12,REP-C10,REP-C11,REP-C12,REP-C13,REP-C14,REP-C15,REP-C19,EXP-C22,OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C24,OPS-C25,OPS-C26,OPS-C27,BEN-C18,BEN-C19,BEN-C20,BEN-C21,BEN-C23 clusters:MM-C01,MM-C02,MM-C03,MM-C04,MM-C06,MM-C09,MM-C11,MM-C12,MM-C13,MM-C16 -->

仓库在本次综合中的作用是回答“真的怎么实现”，不是给 README 做摘要。

| 工程模式 | 仓库证据能成立什么 | 不能成立什么 |
|---|---|---|
| runtime / tier / migration | Letta README 确认 MemGPT lineage、legacy V1 和迁移边界 [FND-C04][REP-C15]；MemoryOS tree 暴露 ChromaDB/MCP/playground/PyPI/eval 分解 [FND-C12] | 当前 successor 的兼容性、执行成功、production maturity |
| representation / retrieval | A-Mem note/link/evolution 与 `retrieve_k` tuning [REP-C10]；Cognee graph+vector+ontology [REP-C11]；Mem0 hybrid retrieval [REP-C12]；MemMachine episodic/profile/working split [REP-C14] | headline benchmark 的独立有效性、跨系统排名 |
| procedure / team state | MemP offline/online paths；Acontext skill-file distillation；TencentDB layered components；其他 team repos 展示不同 artifact data flows [EXP-C22] | procedure correctness、tenant safety、adoption |
| governance | OWASP Guard 的 detector/policy/rollback/source class [OPS-C24][OPS-C25]；vendor APIs 的 scope/revision/TTL/delete surfaces [OPS-C18][OPS-C19][OPS-C20][OPS-C21][OPS-C22][OPS-C23] | end-to-end attack resistance、derived-data deletion、tenant isolation |
| benchmark artifacts | LoCoMo data/eval、LongMemEval variants/retrievers、MemoryAgentBench framework dirs、LongMemEval-V2 packaging [BEN-C18][BEN-C19][BEN-C20][BEN-C21] | runner 目录存在等于完整 reproduction、跨 family 可比 |

REP packet 明确记录：selected repositories 均未执行 [REP-C19]；EXP 也只把 repositories 当作 distinct implementation data-flow evidence，而非 adoption/safety/performance [EXP-C22]。因此 maturity 必须至少拆成 documentation、artifact present、executed、maintained、independently adopted 五级。本次只能在前两级做多数项目判断。

<!-- synthesis:CNS-S08 claims:FND-C04,FND-C10,FND-C12,REP-C15,REP-C19,REP-C21,EXP-C22,OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C24,OPS-C26,OPS-C27,BEN-C18,BEN-C19,BEN-C20,BEN-C21,BEN-C23 clusters:MM-C01,MM-C06,MM-C09,MM-C11,MM-C13,MM-C16 -->

CP-08 是方法 guardrail：stars、single recent push 或 repository creation 可以决定“先查谁”，不能决定“谁更好”。单次 snapshot 只能报告当时状态；growth/acceleration 至少需要两次可比观测或可重放 event history。

## 8. 明确没有形成的共识

以下说法目前都不应进入 executive 结论：

1. **“Graph memory 普遍优于 vector/raw retrieval。”** bitemporal 与 LightMem evidence 足以否定无条件版本 [REP-C03][REP-C05][REP-C06]。
2. **“Consolidation/summary 总能节省成本且不伤质量。”** budget-dependent operator 与 answer-evidence loss 直接反驳 [FND-C19][FND-C20][REP-C06]。
3. **“Learned memory controller 已经成熟。”** MemCon 是重要趋势，但仍是单组预印本、无独立 reproduction [FND-C16]。
4. **“Shared memory 已证明改善团队且安全。”** 可见的是机制和仓库表面，不是 matched benefit/safety deployment [EXP-C18][EXP-C22][OPS-C27]。
5. **“Vendor CRUD/scope/IAM 等于 deletion、isolation 或 poisoning defense。”** 官方 docs 只证明 API surface [OPS-C18][OPS-C19][OPS-C20][OPS-C21][OPS-C22][OPS-C23][OPS-C27]。
6. **“一个 recall leaderboard 能选出最佳 Agent Memory。”** protocol family 不兼容 [BEN-C22][BEN-C25]。
7. **“Model-native memory 比 external 更快，所以总体更好”，或反向结论。** 本次没有 direct assurance comparison；CP-07 保持 evidence-thin。
8. **“高 stars 或 recent push 证明增长、成熟、采用。”** 这是 discovery signal，不是结论证据。

## 9. 决策顺序

对近期平台选择，先问 state transition，再选系统：

1. **只是找回历史证据？** 保留 raw baseline，固定 retriever/k/token/judge，再决定是否 constructed/graph。
2. **事实会变化？** 需要 valid/transaction time、source support、version、supersession、rollback 和 dependency repair。
3. **经验要复用？** 明确保存 reflection、instruction、script 还是 executable skill；记录 outcome、applicability、version 和 deprecation。
4. **涉及多个 principal？** private/shared scope、ACL/policy、provenance、revoke/merge 与 tenant isolation 是前置条件。
5. **涉及个性化？** 最小 profile、consent、correction/delete、stale/sycophancy/extraction gates。
6. **涉及工具或高影响行动？** memory 不继承 authority；action-time 重新授权。
7. **需要声称效果或成熟？** 选对应 benchmark family，执行 pinned repo，报告 protocol fingerprint、成本、failure 和 independent adoption。

详细 adoption/hold 条件见本报告各命题的“决策与反转标准”；machine-readable proposition、relation 与 gap 分别位于 bundle 根目录的 `syntheses.jsonl`、`relations.jsonl` 与 `gaps.jsonl`。
