# MM-C06 — Experience, Procedural Memory & Skills：深度报告

**研究截止：2026-08-10。** 本文把“经验记忆”按行为机制拆开，而不是逐个介绍 Reflexion、Voyager、MemP 或技能仓库。核心问题是：一次 trajectory、feedback、failure 或 demonstration 经过什么验证，才能成为以后可复用、可撤销且不会越权的 durable procedure/skill。

当前 bundle join 得到本簇 membership 345、primary 138、rolling-12m 298、rolling-90d 196；类型为 297 papers、48 repositories。数量仅代表 v09 覆盖，不能当增长、共识或成熟度；计数锚点为 `bundle/cluster_assignments.jsonl × bundle/entities.jsonl`。

## 1. 结论与边界

Procedural memory 的判定条件不是“保存过一段经历”，而是产生了 **会改变后续选择或动作的可复用工件**。工件可以是 reflection、step instruction、high-level script、executable skill、task policy，或负责抽取/管理记忆的 meta-skill。即时 chain-of-thought、单次 plan、没有跨任务保留的 feedback 不属于本簇；user profile 属于 C08；共享权限属于 C11；当 procedure 被写入、版本化、撤销时与 C05 相交。

本簇最重要的架构结论是区分两类 self-evolution：

- **content evolution**：从 trajectories 更新“以后怎么做”，如 MemP 的 instruction/script；
- **policy evolution**：更新“如何构造和管理 memory”，如 MemSkill 的 controller/executor/designer。

二者可组合，但 failure、version、测试和攻击面不同。PoisonedEvolution 又为 trajectory→durable instruction 的 promotion step 提供了早期经验性攻击证据，使其成为必须显式建模的安全边界：不可信经验可能被归一化为可信程序性资产。

证据锚点：claims `EXP-C09,EXP-C10,EXP-C16,EXP-C17,FM-PE-C01`；evidence `EXP-V17,EXP-V18,EXP-V19,EXP-V20,EXP-V31,EXP-V32,EXP-V33,EXP-V34,FM-PE-J01,FM-PE-J02`。

## 2. 演进脉络：memory object 怎样从 prose 变成 executable asset

### 2.1 Episodic reflection：把失败变成语言经验

Reflexion 把 task feedback 转成 linguistic reflection 并存入 episodic buffer，不更新模型权重。这一形状证明“外部持久语言工件可以改变后续尝试”，但 reflection 仍缺显式 precondition、tool version、side-effect contract 和执行隔离。

证据锚点：claims `EXP-C01`；evidence `EXP-V01,EXP-V02`。

### 2.2 Executable skill：把复用单位从文字变成行为

Voyager 的 persistent object 是持续增长的 executable code skill library；其复用单位是可组合行为，而不是检索到的 prose episode。由此出现新的工程责任：代码依赖、环境版本、sandbox、授权、失败回链和 skill deprecation。

证据锚点：claims `EXP-C03,FND-C08`；evidence `EXP-V05,EXP-V06,FND-EV14,FND-EV15`。

### 2.3 Procedure distillation：从 trajectory 抽出 instruction 与 script

MemP 显式把 past trajectories 蒸馏成 step-by-step instructions 与 higher-level scripts，并定义 build、retrieve、update。它把“储存经验”和“编译 procedure”分开；因此评测必须比较 raw trajectory、reflection、instruction、script，而不是把它们统称 memory。

证据锚点：claims `EXP-C09,EXP-C16`；evidence `EXP-V17,EXP-V18,EXP-V31,EXP-V32`。

### 2.4 Meta-memory skill：系统开始学习如何管理经验

MemSkill 的 controller 选择 memory-operation skills，executor 生成 skill-guided memories，designer 从 hard cases 修订 skill set。XSkill 又把 action-level experiences 与 task-level skills 分成两个视觉 grounding 的流，并在当前视觉上下文中适配。这表明“存什么”和“怎样管理所存之物”已经成为两层 policy。

证据锚点：claims `EXP-C10,EXP-C11,EXP-C17`；evidence `EXP-V19,EXP-V20,EXP-V21,EXP-V22,EXP-V33,EXP-V34`。

### 2.5 Promotion security：重复经验不等于可信经验

2026-08 的 PoisonedEvolution 研究把 attack success 分解为 Inclusion、Evolution Attribution 与 Realization。在作者的 10% attacker-support 设置下，SkillClaw 六个 evolvers/四种行为族报告 546/600 durable embeddings；不同结构的 Trace2Skill 报告 369/600。该结果是作者预印本、以 inert canary 衡量 artifact modification，不证明 harmful action、credential theft 或生产 prevalence；但它实质改变了本簇边界：promotion 必须成为 security gate。

证据锚点：claims `FM-PE-C01,FM-PE-C02,FM-PE-C03,FM-PE-C05`；evidence `FM-PE-J01,FM-PE-J02,FM-PE-J03,FM-PE-J04,FM-PE-J06,FM-PE-J07`。

## 3. 问题分解与参考架构

本报告建议把系统拆成六层：

1. **Trace ledger**：保存 task、observation、action、tool/schema/environment version、outcome、failure、principal 与 source。
2. **Candidate distiller**：从多个 traces 生成 reflection/instruction/script/code candidate，并保留 supporting/contradicting examples。
3. **Promotion gate**：做 provenance diversity、scope、license、security scan、validation cases 与 reviewer policy；不让重复频次直接成为 trust。
4. **Versioned skill registry**：保存 preconditions、payload、dependencies、validation set、confidence、status、parent 与 rollback target。
5. **Applicability retriever/adaptor**：先硬过滤 task/environment/tool/principal，再检索相似工件并适配当前参数。
6. **Sandboxed executor + feedback**：action 前重新授权，记录 side effects 与 outcome；失败回到 trace ledger，不能直接全局强化。

这是设计综合。它把 content evolution、meta-policy evolution 与 evidence-promotion attack 放在一条可审计链上；现有来源并未定义统一 schema 或 production reference architecture。

证据锚点：claims `EXP-C09,EXP-C10,EXP-C11,EXP-C16,EXP-C17,EXP-C22,FM-PE-C01,FM-PE-C04`；evidence `EXP-V17,EXP-V18,EXP-V19,EXP-V20,EXP-V21,EXP-V22,EXP-V31,EXP-V32,EXP-V33,EXP-V34,EXP-V43,EXP-V44,FM-PE-J01,FM-PE-J02,FM-PE-J05`。

## 4. 算法与 write→manage→read→action 数据流

### 4.1 Write：捕获 outcome-rich trajectory

只保存成功对话会制造 survivorship bias。建议每条 trace 至少包含：`task_id, principal, environment/tool/schema version, observation refs, actions, tool results, side effects, success criterion, failure class, reviewer, timestamp`。原始 trace 追加写入；distiller 只能产生 candidate，不能直接覆盖现有 skill。

证据锚点：claims `EXP-C01,EXP-C03,EXP-C09,EXP-C16`；evidence `EXP-V01,EXP-V02,EXP-V05,EXP-V06,EXP-V17,EXP-V18,EXP-V31,EXP-V32`。

### 4.2 Manage：distill、validate、promote、version、deprecate

本报告建议用两阶段晋升：

`candidate = distill(traces, failures, target abstraction)`

`promote iff scope_match ∧ source_diversity ∧ validation_pass ∧ security_pass ∧ reviewer_policy`

candidate 应保存 inclusion set、counterexamples、attribution trace 与 validation version。PoisonedEvolution 的 pilot provenance-diversity gate 在一个 n=30,k=3 setting 中阻断 25/25 single-cluster candidates、接受一个五 session diverse control，但论文自称 preliminary；因此 diversity 是可测试防线，不是已证通用防御。

证据锚点：claims `EXP-C09,EXP-C10,EXP-C17,FM-PE-C01,FM-PE-C04,FM-PE-C05`；evidence `EXP-V17,EXP-V18,EXP-V19,EXP-V20,EXP-V33,EXP-V34,FM-PE-J01,FM-PE-J02,FM-PE-J05,FM-PE-J06,FM-PE-J07`。

### 4.3 Read：先判断 applicability，再做 semantic retrieval

retrieval key 不应只有 query embedding。先用 principal、task type、preconditions、tool/API/environment version、risk tier 与 license 做 hard filter；再检索 reflection/procedure/skill；最后由 adaptor 把参数映射到当前环境。若版本、scope 或 required tool 不满足，应 abstain 或回退 raw trace，而不是强行迁移。

证据锚点：claims `EXP-C03,EXP-C09,EXP-C11,EXP-C16`；evidence `EXP-V05,EXP-V06,EXP-V17,EXP-V18,EXP-V21,EXP-V22,EXP-V31,EXP-V32`。

### 4.4 Action：执行权不能从 memory payload 继承

executable skill 只提供候选行为，不授予 filesystem/network/payment 等 authority。action gateway 对当前 principal 和 environment 重新授权，在 sandbox/canary 中先验证；记录 actual side effects、first-attempt outcome、fallback 与 rollback。失败应更新 applicability 或 deprecate revision，不能因一次失败删除所有同类经验，也不能因一次成功全局提升 trust。

证据锚点：claims `EXP-C03,EXP-C16,FM-PE-C01,FM-PE-C05,OPS-C07`；evidence `EXP-V05,EXP-V06,EXP-V31,EXP-V32,FM-PE-J01,FM-PE-J02,FM-PE-J06,FM-PE-J07,OPS-J07`。

## 5. 实现与集成：三种工程形状

### Host/backend/skill 解耦

Raven 的固定 SHA 把 memory 放在 host-side `MemoryBackend Protocol` 后，通过 manifest-only plugin discovery 接入；turn 前 context engine recall，turn 后 AgentLoop store/feedback，另有 skill-forge 汇合 memory hits 与 skill sources。其 bundled EverOS adapter 精确 pin 到 internal APIs；身份由 `memory.userId`/`memory.agentId` 一致性决定。这说明 backend、host loop、skill synthesis 和 identity 是不同集成责任，但仓库未执行，不能证明 correctness。

证据锚点：claims `PRJ-A005,PRJ-I005`；evidence `PRJ-AE005-01,PRJ-AE005-02,PRJ-AE005-03,PRJ-IE005-01`。

### Resource/memory/skill 统一资产层

OpenViking 把 memory/resource/skill 放进 `viking://` 虚拟文件系统：内容先写 AGFS，异步 semantic queue 生成 L0/L1/L2 与索引；session commit 再按 schema 抽取 self/peer/experience memory。调用方必须等待处理完成或接受短时不可召回；memory policy 与 peer routing 错误会漏写或越界。该形状强调 artifact hierarchy 与 asynchronous projection，而非证明 skills 已安全可迁移。

证据锚点：claims `PRJ-A006,PRJ-I006`；evidence `PRJ-AE006-01,PRJ-AE006-02,PRJ-AE006-03,PRJ-IE006-01,PRJ-IE006-02`。

### Trace-to-skill 与 team asset pipelines

现有 repository evidence 展示 skill-file distillation、trace-to-playbook consolidation 与 layered team memory；Acontext、Hivemind、TencentDB Agent Memory 等支持“工程上正在把 trajectory 变成可审核资产”的判断，但这些是维护者/静态实现表面，不是独立 adoption、安全或 comparative performance。

证据锚点：claims `EXP-C22,GR-C-M005`；evidence `EXP-V43,EXP-V44,GR-V-M005-01,GR-V-M005-02,GR-V-M005-03`。

### 不完整 lineage 不能当现成系统

JARVIS-1 固定 SHA 是离线评估快照；README 明确 multimodal descriptor、retrieval、learning.py 与 online growing memory 未发布，且其 Minecraft/Malmo、model weights 与 API key 集成成本显著高于普通 memory library。它是 embodied procedural lineage 和发布完整性的负例，不是可直接采用的 write/index/read stack。

证据锚点：claims `PRJ-A010,PRJ-I010`；evidence `PRJ-AE010-01,PRJ-AE010-02,PRJ-AE010-03,PRJ-IE010-01,PRJ-IE010-02`。

## 6. 成本模型

Procedural memory 的成本不能只算 retrieval tokens。至少包括：raw trajectory storage、distillation/model calls、validation/sandbox runs、registry/index、adaptation、human review、failed transfer、rollback 与 contaminated-skill incident response。Executable assets 还引入 dependency pin、environment image、license review 和 side-effect monitoring。

当前 deep claims 没有同一 workload 下对 reflection、procedure、script、code skill、meta-skill 的完整 cost ledger；repository 也未执行。因此建议报告 `cost per captured trace`、`cost per promoted artifact`、validation cases/time、artifact bytes、retrieval/adaptation latency、first-attempt success、rollback time、human minutes 与 contamination loss。任何“self-evolution 自动降低成本”的陈述在当前 evidence 下都应 abstain。

证据锚点：claims `EXP-C21,EXP-C22,PRJ-I010`；evidence `EXP-V41,EXP-V42,EXP-V43,EXP-V44,PRJ-IE010-01,PRJ-IE010-02`。

## 7. Benchmark protocol：从 recall 转为迁移、首次行动与安全晋升

建议采用五臂 matched protocol：`no-memory`、`raw trajectory retrieval`、`reflection`、`procedure/script`、`executable skill/meta-skill`。固定 model、task set、tool versions、context budget 与 judge；训练阶段给相同 trajectory/outcome，测试阶段包含：

- in-distribution reuse；
- compositional transfer；
- wrong-scope near match；
- stale tool/API version；
- failure-only evidence；
- adversarial trajectory contribution；
- artifact revoke/rollback；
- first-attempt 与 later-attempt behavior。

ImplicitMemBench 的 Learning/Priming–Interfere–Test 与 first-attempt scoring 可诊断 implicit/procedural behavior；MemoryArena 检查 earlier action/feedback 是否改变 later decisions；Mem2ActBench 检查长期约束进入 tool selection/parameters。三者协议不同，不能汇总一个总分。PoisonedEvolution 的 Inclusion/Evolution Attribution/Realization 可作为 promotion-security 子协议，但必须另测 harmful execution 与 utility-security frontier。

证据锚点：claims `BEN-C07,BEN-C12,BEN-C15,BEN-C22,BEN-C25,FM-PE-C01,FM-PE-C05`；evidence `BEN-EV13,BEN-EV14,BEN-EV23,BEN-EV24,BEN-EV29,BEN-EV30,BEN-EV43,BEN-EV44,BEN-EV49,BEN-EV50,FM-PE-J01,FM-PE-J02,FM-PE-J06,FM-PE-J07`。

## 8. 限制、失败与负面证据

| 失败面 | 当前证据 | 设计含义 |
|---|---|---|
| promotion poisoning | 两种 self-evolution pipeline 均有作者报告的 durable embedding | provenance/diversity/security gate 位于晋升前 |
| metric underreach | SER 只测 artifact modification，不测有害执行 | security benchmark 必须接到 action/impact |
| stale applicability | 本包没有 stale tool/API 的直接程序性复现 | 作为高优先 gap，不能假装已解决 |
| wrong-scope transfer | 没有共同 benchmark 比较跨 user/team/environment 迁移 | hard scope/precondition filter + abstention |
| repository completeness | JARVIS-1 未发布 online growing-memory paths | tree/README 不等于完整系统 |
| independent outcome evidence | performance/formal claims主要来自作者/维护者 | 不做项目胜者或生产推荐 |

证据锚点：claims `FM-PE-C02,FM-PE-C03,FM-PE-C04,FM-PE-C05,EXP-C21,EXP-C22,PRJ-A010`；evidence `FM-PE-J03,FM-PE-J04,FM-PE-J05,FM-PE-J06,FM-PE-J07,EXP-V41,EXP-V42,EXP-V43,EXP-V44,PRJ-AE010-01,PRJ-AE010-02,PRJ-AE010-03`。

## 9. 替代方案与适用条件

1. **Raw trajectory + scoped retrieval**：任务少、错误可审计时，避免早期有损 distillation。
2. **Reflection-only memory**：不能安全执行代码、环境变化快或 side-effect 高时，只提供 advisory text。
3. **Human-curated playbook**：高风险 workflow 由人审版本、测试与签名；自动 distiller 只提案。
4. **Ephemeral adaptation**：一次 session 内适配但不跨 session 晋升，适用于来源不可信或用户 consent 不明确。
5. **Parameter training**：可作为另一路线，但它改变 audit/delete/recovery boundary，不能当 external procedural store 的等价替换。

采用自动 self-evolution 的前提应是：artifact schema、applicability、independent validation、rollback 与 poisoning test 均闭合。若污染、stale-tool 或 wrong-scope rate 高于 raw/reflection baseline，则回退到人工晋升或 advisory-only。

证据锚点：claims `EXP-C01,EXP-C03,EXP-C09,EXP-C16,FM-PE-C01,FM-PE-C05`；evidence `EXP-V01,EXP-V02,EXP-V05,EXP-V06,EXP-V17,EXP-V18,EXP-V31,EXP-V32,FM-PE-J01,FM-PE-J02,FM-PE-J06,FM-PE-J07`。

## 10. 共识、分歧与决策

**条件共识：** durable behavior-changing artifact 才是 procedural memory；原始 trajectory 与 derived skill 应分开；artifact 需要 preconditions、version、source/outcome、scope、validation 与 deprecation；execution authority 不能从 memory 自动继承。

**仍有分歧：** reflection、instruction、script、code skill 或 meta-policy 哪种跨任务最好；何时自动晋升；是否需要 graph organization；如何把视觉/环境 grounding 带入 portable skill；共享 skill 的 license、tenant 与 revoke contract。

**决策建议：** 采用 `pilot with versioned artifacts`。先部署 raw ledger、manual/guarded promotion、applicability filter、sandbox 与 rollback；meta-skill 只在 shadow/canary 中演化。扩大条件是 matched procedure extraction/update benchmark 与独立 execution；缩小条件是 promotion poisoning、不可解释迁移、stale tool assumption 或 unsafe side effect。

证据锚点：claims `EXP-C16,EXP-C17,EXP-C21,EXP-C22,FM-PE-C01,FM-PE-C05`；evidence `EXP-V31,EXP-V32,EXP-V33,EXP-V34,EXP-V41,EXP-V42,EXP-V43,EXP-V44,FM-PE-J01,FM-PE-J02,FM-PE-J06,FM-PE-J07`。

## 11. 分层代表证据

| Stratum | 代表项 | 用途 | 边界 | Claim / evidence |
|---|---|---|---|---|
| foundational | Reflexion、Voyager（2023） | reflection 与 executable skill 两种 durable object | 缺统一 lifecycle/security contract | `EXP-C01,EXP-C03` / `EXP-V01,EXP-V02,EXP-V05,EXP-V06` |
| recent paper | MemP、MemSkill、XSkill（2026） | procedure、meta-memory policy、multimodal dual stream | 作者机制，缺共同独立比较 | `EXP-C09,EXP-C10,EXP-C11,EXP-C17` / `EXP-V17,EXP-V18,EXP-V19,EXP-V20,EXP-V21,EXP-V22,EXP-V33,EXP-V34` |
| repository | Raven、OpenViking、Acontext/TencentDB | host/backend、统一资产、trace-to-skill integration | fixed-SHA/static 或 maintainer surface，未执行 | `PRJ-A005,PRJ-A006,EXP-C22` / `PRJ-AE005-01,PRJ-AE005-02,PRJ-AE005-03,PRJ-AE006-01,PRJ-AE006-02,PRJ-AE006-03,EXP-V43,EXP-V44` |
| benchmark | ImplicitMemBench、MemoryArena、Mem2ActBench | first attempt、later action、tool grounding | 任务单元不可合并 | `BEN-C07,BEN-C12,BEN-C15,BEN-C22` / `BEN-EV13,BEN-EV14,BEN-EV23,BEN-EV24,BEN-EV29,BEN-EV30,BEN-EV43,BEN-EV44` |
| negative/security | PoisonedEvolution；JARVIS-1 incomplete snapshot | promotion attack 与 artifact-completeness boundary | preprint/inert canary；仓库未执行 | `FM-PE-C01,FM-PE-C05,PRJ-A010` / `FM-PE-J01,FM-PE-J02,FM-PE-J06,FM-PE-J07,PRJ-AE010-01,PRJ-AE010-02,PRJ-AE010-03` |

## 12. 命名缺口与真实 saturation

- **GAP-C06-01 — independent procedural reproduction：** 在同一任务/模型/预算下比较 raw、reflection、procedure、skill 与 meta-skill。
- **GAP-C06-02 — stale tool and environment：** tool/API/schema 变化后的 applicability、deprecation 与 repair。
- **GAP-C06-03 — harmful execution：** 从 durable artifact modification 延伸到 trigger、action、credential、exfiltration 与 destructive impact。
- **GAP-C06-04 — anti-Sybil promotion：** provenance diversity 面对协调 contributor、copy/near-duplicate trajectories 与 collusion 的稳健性。
- **GAP-C06-05 — shared skill governance：** principal/tenant/license/revocation 与跨团队 transfer。
- **GAP-C06-06 — total cost：** distillation、validation、sandbox、review、rollback 与污染事故的同口径账本。

真实 saturation 过程不能写成“搜不到了”。Cycle 11 的 `SAT11-C06-OA` 首次带来 material change：PoisonedEvolution 将 poisoned experience 从纯 gap 改为早期经验性证据。C06 因而重开；cycle 12 的 `SAT12-C06-ARXIV`（10）、`SAT12-FOUNDATION-ARXIV`（10）、`SAT12-GH-C05C06`（10）无进一步 material change；cycle 13 的 `SAT13-C06C12C13-12M-OA`（10）、`SAT13-C06C12C13-OA`（10）、`SAT13-GH-C06C12C13`（1）再次无 material change。详见 `work/saturation-followup/field-matrix/scope-saturation.jsonl`。

结论是第一阶 taxonomy 与新 promotion-security stance 已 decision-useful；不是 independent defense、harmful execution、cost 或 production safety 已饱和。出现独立 poisoning reproduction、validated defense、新 durable artifact class 或 matched outcome/cost reversal 时应重开。

证据锚点：claims `FM-PE-C01,FM-PE-C02,FM-PE-C03,FM-PE-C04,FM-PE-C05,EXP-C21,EXP-C22`；evidence `FM-PE-J01,FM-PE-J02,FM-PE-J03,FM-PE-J04,FM-PE-J05,FM-PE-J06,FM-PE-J07,EXP-V41,EXP-V42,EXP-V43,EXP-V44`。


<!-- synthesis:CLY-C06 claims:EXP-C01,EXP-C03,EXP-C09,EXP-C10,EXP-C16,EXP-C17,FM-PE-C01,FM-PE-C02,FM-PE-C03,FM-PE-C04,FM-PE-C05 clusters:MM-C06 -->
