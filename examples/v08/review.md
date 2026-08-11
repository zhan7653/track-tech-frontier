# v08 最终独立只读评审

## 结论

**94/100，通过。** H1–H5 均通过，且高于 80。与 v07 相比，先前四个复合语义硬失败、不可重放的 `setup=verified`、dataset ID 混用和两个 benchmark canonical repo 缺失均已闭环。仍有 source-independence、未执行 setup/tests、采用/删除传播/统一成本基准不足等 advisories；它们是透明质量限制，不是本 rubric 的硬失败。

- `bundle/report.md` 与 `output.md` SHA-256 一致：`98C898A7A2980C2333631A2D48E25EDD00E6E175EB72897C490743AD56E35F34`。
- 机械复查：66 claims、51 high-risk、177 evidence joins；66/66 exact statement 在报告中出现并紧接 claim marker；66/66 至少一个 evidence join；报告/输出字节一致。
- validation transcript 报 normal/strict 均 exit 0、无 ERROR/WARNING；仅诚实 ADVISORY。

## Hard gates

| Gate | 判定 | 独立审计 |
|---|---|---|
| H1 | **通过** | 66 条 claim 均有 exact marker 与 source/evidence join。v07 的 C009/C027/C039/C041 类复合越界已拆为更小语义：不再把程序经验、多模态/多方、policy isolation、派生物自动删除、single-session/keyed state/更新速度等塞进无直接支持的句子。C016–C021 landscape 每行皆完整 atomic claim；C020 的“未核验 canonical code”明确限定为本轮可回放 code-search gap，不冒充外部已证实的不存在。C041/C055 都明确是三轮有界检索结论并指向 query/candidate ledger。C058–C060 明确是 12–24 月预测，正文给出削弱/推翻条件。 |
| H2 | **通过** | Survey S001 在 paper card 中标 T2 / `evidence_role=survey`，仅作 taxonomy map；vendor/README、作者 preprint、独立 COMPSAC/benchmark 的角色分开。 |
| H3 | **通过** | repo 卡有 pin/license/setup/CI/affiliation；能力/性能不从 stars 或 repo existence 推出；adoption 全部保持空 evidence 和 bounded abstention。 |
| H4 | **通过** | as-of=2026-08-10；Google GA/计费、AWS GA/Classic/strict 三键、Microsoft preview、LangGraph/LangMem 均有 dated primary source / fixed commit。 |
| H5 | **通过** | schema 1.7 update、16 requirements、20 exact queries、69 candidate decisions、45 sources、19 papers、13 repos、0 executions、16 coverage、66 claims、177 joins、66 semantic checks、delta 与 validation transcript 都可重放；操作时间为真实 2026-08-09 UTC。 |

## 评分

| 项目 | 分 | 依据 |
|---|---:|---|
| A1 relevance / RQ mapping | 14/15 | 16 RQ 覆盖 taxonomy、谱系、benchmark、管理成本、安全、开源/三云、反证、内部评测；RQ05/06/08/13/14 诚实 partial。 |
| A2 paper quality / primary status | 9/10 | 19 paper cards，peer-reviewed/preprint/survey/workshop/system-report 明确；MemoryAgentBench/Mem2ActBench paper↔repo↔dataset 复核。扣分：多项新方向只能 preprint/作者 evidence，部分无 code。 |
| A3 GitHub quality | 9/10 | 13 repo cards均 pin；license/setup/CI/affiliation/adoption 透明；`executions=0` 与 documented/present/missing 一致。扣分：6+ repos no CI、2 license unknown、2 affiliation unverified，未实际 smoke test。 |
| B1 depth | 23/25 | write–manage–read 生命周期、Memory OS、控制策略、成本 phase、tool grounding、产品治理和安全均有机制/边界。扣分：controlled deletion propagation/跨租户与统一 lifecycle cost 没有实测。 |
| B2 breadth / comparison / negative | 14/15 | 统一 landscape 表、LongMemEval/MemoryAgent/Mem2Act/MemCon/system study/independent cost 对照、MEXTRA/poisoning/STALE/experience negative、云产品都在。扣分：temporal/multimodal/multi-agent 仍主要作为缺口而非已评测路线。 |
| B3 claim-citation correctness | 14/15 | 66/66 合同结构及逐子句 semantic checks；外部重开关键 proceedings/docs 与资料一致。扣分：C020/C041/C055 的“未找到”依赖有界搜索账本，不能证明客观不存在；但措辞严格限定本轮范围。 |
| B4 coverage/source/freshness/replay | 10/10 | 全链条 replay、UTC、validation、hash、semantic audit 均优秀；保留 advisory。 |
| **总分** | **94/100** | A=32，B=62。 |

## 16 RQ 覆盖

| RQ | 状态 | 评审 |
|---|---|---|
| 01 taxonomy/lifecycle | covered | C001/C004/C020/C022/C028/C058；系统 taxonomy 有边界。 |
| 02 history 2024–26 | covered | Generative Agents/MemGPT/Reflexion/MemCon/LongMemEval-V2 状态清楚。 |
| 03 paper↔repo quality | covered | 新补 MemoryAgentBench/Mem2ActBench 三向链。 |
| 04 benchmarks | covered | QA/interactive/tool action/continual 协议分开。 |
| 05 management/cost | partial | 有 systems + COMPSAC 对照；无全 lifecycle 统一协议。 |
| 06 safety/privacy/delete | partial | MEXTRA/poisoning/STALE/official guidance 有；无派生删除端到端实证。 |
| 07 MEXTRA units | covered | 30 prompt、each-agent 200 records、EHRAgent EN/RN=50/55、RAP=26/27 均正确。 |
| 08 products/adoption | partial | 工程状态充分；无独立生产部署。 |
| 09 Google | covered | 2025-12-16 GA、2026-01-28 billed，有官方 release note。 |
| 10 AWS | covered | AgentCore GA、Classic migration、STRICTLY_CONSISTENT ≤3 keys 分开表述。 |
| 11 Microsoft | covered | Memory/Store API public preview，TTL/CRUD/remember-forget 限定。 |
| 12 LangGraph/LangMem | covered | persistence/store 与 hot/background management 区分。 |
| 13 no-memory counterevidence | partial | BM25/GroupMemBench 是局部反证，报告不再外推。 |
| 14 emerging forecasts | partial | C058–60 有界预测与 falsifier，非当前事实。 |
| 15 internal eval | covered | 固定 contract + answer/recall/time/tool grounding/cost/security。 |
| 16 LongMemEval S/M/Oracle | covered | S/M 是规模，Oracle=evidence-session retrieval，未再误作第三数据版本。 |

## 论文、来源、仓库质量

| 类别 | 结论 |
|---|---|
| Survey | S001 是 preprint/T2/survey，仅作地图，符合 v07 修复要求。 |
| Key paper-code-data | LongMemEval 的 S008→S009→S010，MemoryAgentBench S011→S012→S013，Mem2ActBench S014→S015→S016 均为明确 reciprocal/单独 dataset 链；不再用 repo 冒充 dataset。 |
| Canonical benchmark repos | `HUST-AI-HYZ/MemoryAgentBench`：pin `455306d…`、文档 setup、no CI/no release；`Cantaloupe-M/Mem2ActBench`：pin `b007269…`、文档 setup、no CI/no release；paper/repo 两端互链，符合 corrective requirement。 |
| Repos / executions | 13 repos 都是 pinned revision；`executions.jsonl` 为空且所有卡为 documented/present/missing，未再误填 verified。 |
| Product freshness | Google/AWS/Microsoft 均为官方 product docs/release；AWS Classic 与 AgentCore 不混写，Microsoft 不误报 GA。 |

## 66 claim audit

以下 `P`=完整支持，`Q`=有界/推断但已正确限定；无 `F`。审计覆盖全部 66（51 high-risk + 15 normal）。

| Claims | Verdict | 审计摘要 |
|---|---|---|
| C001–C010 | P | 定义、MemoryAgentBench/Mem2ActBench、2026 system cost、poisoning、LongMemEval、LangGraph/LangMem/MemCon 皆有对应一手 papers/docs。 |
| C011–C015 | P | Generative Agents/UIST、MemGPT、Reflexion/NeurIPS、MemCon/preprint、LongMemEval-V2/preprint 均按发表状态限定。 |
| C016 | P | LongMemEval paper/repo/dataset、S/M/Oracle 条件、documented/no-CI 均一个 atomic row。 |
| C017 | P | MemoryAgentBench ICLR+repo+HF data、四能力、文档/no-CI、指标不可混。 |
| C018 | P | Mem2ActBench ACL+repo/data，tool-argument scope 与合成生产边界明确。 |
| C019 | P | MemCon 动作、repo/no-CI、author-report boundary 完整。 |
| C020 | Q | systems preprint 的两 suite/十系统/phase 与“无核验代码仓”分开；后者限定本轮 code-search ledger。 |
| C021 | P | COMPSAC acceptance、LoCoMo cloud-edge、比较对象和版本/网络/成本条件完整。 |
| C022–C028 | P | phase harness、77–81 vs 55–56、8.4× Pareto、MemCon 15.2pp/5–20%、comparability、全成本分层均有显式作者/独立边界。 |
| C029–C035 | P | LongMemEval S/M/Oracle、MAB metrics、Mem2Act 2029/12/400/91.3%、GroupMemBench、LoCoMo、cleaned data、compare contract 皆正确限定。 |
| C036–C040 | P | Mem0/Graphiti/new benchmark repos/LangMem+LangGraph pins、setup/docs/CI、zero execution 逐条限定。 |
| C041 | Q | 独立生产案例缺失限定“三轮公开检索范围”，直接指 query+candidates，不宣称世界中不存在。 |
| C042–C047 | P | Google GA+bill date；AWS GA/Classic/metadata 三键；Microsoft preview/CRUD/TTL/commands 均分别一手支持。 |
| C048–C050 | P | MEXTRA 30/200/EN/RN 计数单位与数值正确，未把 EN 混作 prompt。 |
| C051–C054 | P | poisoning persistence/aggressive write-retrieve、experience error propagation、selective add/delete 10% 均按实验范围陈述。 |
| C055 | Q | 同样是 query/candidate bounded no-evidence claim，未再外推 deletion behavior。 |
| C056–C057 | P | Microsoft injection/adversarial guidance 与 STALE capability gap 正确。 |
| C058–C060 | Q | 明示 12–24 月 forecast、基于 MemCon/tool grounding/poisoning-stale signals 且报告给出推翻条件。 |
| C061–C066 | P | frozen contract、distinct metrics、cost/failure metrics、安全 regression、local baseline gate、stars/vendor/CI 不等于 adoption 均为工程建议且有命名 evidence/限定。 |

## v07 缺陷闭环

| v07 finding | v08 | 判定 |
|---|---|---|
| C009/C027/C039/C041 复合越界（H1） | 拆为 C001–66 的 atomic claims；不受支持子句移除或改 bounded search/forecast。 | 已闭环 |
| `setup=verified` 无执行（H5） | executions=0；所有不运行字段降 documented/present/missing。 | 已闭环 |
| dataset IDs 用 repo | 新建 S010/S013/S016/S043 dataset sources，paper cards 指向独立 data source。 | 已闭环 |
| survey 误作 T1 | S001=T2/evidence_role survey。 | 已闭环 |
| Missing MAB/Mem2Act repo | S012/S015 canonical repos，paper↔repo↔dataset、pins/license/CI 已记录。 | 已闭环 |
| candidate funnel 浅/无验证 | 3 pass 6/8/6 queries；69 candidates，pass 均有 non-retained。 | 已闭环 |
| landscape 缺共同表 | v08 landscape table 以一行一 atomic claim 覆盖任务/机制/证据/成熟度/边界。 | 已闭环 |
| validation delivery 缺失 | validation.txt 含 normal+strict stdout、advisory、counts、hash/byte equality。 | 已闭环 |

## Advisories

ADVISORY 不应单独变成硬失败：它们诚实记录了 repo CI/license/affiliation 缺口，以及 22 个 high-risk claims 不足两 independent groups。Rubric H1 要求可访问蕴含的一条 claim-level source；第二独立来源是质量目标。v08 没有 ERROR/WARNING。注意：这些 advisory 应继续在后续更新优先补强，尤其非厂商的 product/deployment、delete propagation、跨租户和统一成本实验。

## 相对参考项目

| Reference behavior | v08 |
|---|---|
| DeerFlow broad→focused | 强：requirements 冻结、Map/Focus/Verify 及 candidate decisions 可见。 |
| daymade traceability | 很强：source class/status/independence/claim/evidence/semantic/pin/hash 完整。 |
| hec-ovi contrarian | 强：MEXTRA、poisoning、STALE、GroupMemBench/BM25 和无 adoption 结论。 |
| hv-analysis longitudinal×cross-sectional | 强：2023 谱系、2024–26 变化、统一比较表、产品/工程横截面。 |
| STORM perspectives | 强：16 维 requirements 与对应 coverage。 |
| GPT Researcher abstention | 很强：production、deletion propagation、uniform cost 均明确缺口。 |
| LangChain ODR budgets | 强：3 pass、20 query、验证/manifest 计数/停止记录。 |
| dzhng query loop | 强：query→candidate→source/evidence 链可回放。 |
| claim-citation verification | 很强：66 atomic exact markers + 177 joins + 66 semantic checks；需继续防止自评 semantic check 取代外部复核。 |
| paper+GitHub joint quality | 很强：19 papers/13 repos，纠正 MAB/M2A data/pin/CI。 |

## Remaining limitations / next work

1. 无统一公开实验同时覆盖写入、派生删除、存储增长、失败恢复、权限/跨租户和全生命周期成本。
2. 未执行任何仓库；repo quality 是 documentation/CI 检查，不是运行可复现性。
3. 无第三方可审计生产案例；不可将 stars/CI/customer names/README 替代。
4. 产品、preprint 和 forecast 仍应随时间重核；预测必须维持有界和 falsifier。

评审为独立只读审计：完整读取 v08 指定材料、冻结 Skill 及直接 references、bundle 全部文件和 v07 review，并对关键论文、产品文档与仓库作公开只读复核；未修改 v08 bundle/output/skill、installed Skill、项目仓库或远程状态。
