# v09 对 USER_FEEDBACK 的完成审计

**主题：** AI Agent Memory  
**研究截止：** 2026-08-10  
**验收口径：** 大方向、字段结构、输入广度、近期趋势与分析质量优先；版本、数字、性能、安全、采用和当前状态等关键事实保持严格；普通连接性分析允许使用代表性来源、段落级引用和明确限定的推理，不要求逐句原子化或为了流程字段运行仓库。

## 1. 输入端要求

| USER_FEEDBACK 要求 | 当前证据 | 判定 |
|---|---|---|
| 先广泛吸收，再选择深读对象 | breadth 阶段先执行 74 条查询，保留 7,535 个结果 occurrence、4,319 个 identifier-level entities；完成 mapping 后才进入 deep packets 和 GitHub radar | 完成 |
| 论文、仓库的绝对数量必须显著扩大 | breadth corpus 为 2,494 papers、1,825 repositories；final provenance ledger 为 2,510 papers、1,846 repositories | 完成 |
| discovered、mapped、deep 必须分开 | final stage 明确为 2,413 discovered、1,773 mapped、221 deep-verified；输入审计分别解释三层可支持的结论 | 完成 |
| 字段地图必须由广泛 corpus 生成，而非由精选证据反推 | 1,899 个 canonical map decisions 形成 5 roots、16 leaves 的 DAG；deep evidence 只验证判断，不定义字段边界 | 完成 |
| 深度证据门只用于选中的重要对象 | final bundle 有 73 paper cards、86 repository cards、16 fixed-commit engineering profiles；其余 mapped metadata 只进入 taxonomy、freshness 与 selection | 完成 |
| 新鲜度独立评价 | breadth corpus 中 rolling-12m 2,843、rolling-90d 1,403；GitHub creation、push、release、observation 分开记录，future metadata 单独隔离 | 完成 |
| v08 的高分不能代替广度验收 | [v08 对比](bundle/reports/13-v08-comparison.md) 将 v08 定位为 precision/provenance baseline，并逐项说明 v09 的结构性改变 | 完成 |

输入端的权威说明见 [输入审计](bundle/reports/12-input-audit.md) 与 [方法和限制](bundle/reports/09-method-and-limitations.md)。

## 2. 输出端要求

| USER_FEEDBACK 要求 | 当前证据 | 判定 |
|---|---|---|
| 不能写成论文、仓库简介串联 | [执行结论](bundle/reports/01-executive-decision.md) 以九个决策判断组织；[架构全景](bundle/reports/03-landscape-synthesis.md) 以 write–manage–read–action、control、security、evaluation、cost 组织，不按项目排列 | 完成 |
| 先形成技术树和分块，再在分块中分析 | [字段树](bundle/reports/02-field-tree.md) 给出 5-root/16-leaf DAG；[架构全景](bundle/reports/03-landscape-synthesis.md) 和 14 个 cluster reports 解释各块的问题、架构、实现、代价与边界 | 完成 |
| 要总结共识、分歧、成熟度、负面结果和开放问题 | [共识与争议](bundle/reports/05-consensus-controversies.md)、[安全与失败](bundle/reports/08-security-and-failure.md)、[Benchmark map](bundle/reports/07-benchmark-map.md) 分别保存条件共识、minority view、反证、不可比性和 reversal criteria | 完成 |
| 要形成历史和因果技术脉络 | [历史与因果](bundle/reports/04-history-and-causality.md) 区分 chronology、source-asserted influence、report inference、反事实与条件预测 | 完成 |
| 广度和深度必须是不同交付物 | broad map 和 input audit 独立；14 个技术簇深度报告与 16 个固定提交仓库深潜独立保存在 `bundle/clusters/`、`bundle/projects/` | 完成 |
| GitHub 是一等工程输入 | 28 条 breadth GitHub queries、1,825 个 breadth repositories、59 个 radar observations、16 个 fixed-commit engineering profiles；仓库报告包含组件、数据流、真实依赖、集成约束、维护信号和失败模式 | 完成 |
| 追踪新建、高关注、release、维护与增长信号 | [GitHub 雷达](bundle/reports/06-github-trend-radar.md) 分开 new-90d、new-12m、established-active、watchlist、release、push、commit/contributor 与当前 stars；增长历史专项核验发现 provider 数据不可比，因此明确关闭伪增长榜 | 完成（有透明限制） |
| 允许多阶段、多文件，不以成本最小为目标 | final reader suite 有 45 个 deliverables：14 个总览/专题报告、14 个 cluster reports、16 个 project reports 及兼容入口；底层另保留查询、mapping、source、claim、synthesis、relation 和 gap ledgers | 完成 |
| 证据正确仍必要，但不能成为主要组织结构 | 读者首先看到领域结构、判断和决策；原子证据集中放在 [claim audit](bundle/reports/14-claim-audit.md) 与底层 ledger，不再用来源介绍支配正文 | 完成 |

## 3. GitHub star-growth 的有界结论

GitHub 2026 年 7 月限制公开 stargazer-list endpoint 后，本轮使用 OSSInsight history 对 59/59 个 radar repositories 做了一次补查。只有 1 个满足窗口 delta 使用门槛、3 个仅可诊断、55 个不可用；52 个能计算覆盖率的对象中有 50 个低于 90%，另有 7 个返回空历史。因此：

- 不发布跨仓库 star-growth、velocity 或 acceleration 排名；
- 不把历史缺口补成 0；
- 当前累计 stars 只作为深读触发器；
- 近期趋势改用 created、pushed、release、90-day commits/contributors 与工程表面交叉判断。

专项结果见 [star-growth packet](work/github-radar/star-growth/report.md)。这是对 USER_FEEDBACK 中“增长应成为趋势信号”的真实执行结果；数据不可可靠复原时，透明失败优于制造精确排名。

## 4. Skill 的设计纠偏

仓库内 [SKILL.md](../../SKILL.md) 已把流程改为：

1. recall-first breadth discovery；
2. discovered / mapped / deep 三层分离；
3. broad corpus 诱导 taxonomy 和 cluster；
4. 每个重要 cluster 做选择性深研；
5. GitHub 与论文并列，创建、活动、release、历史 lineage 分开；
6. consensus、contradiction、timeline、cross-cluster synthesis 后置为独立阶段；
7. 只有关键事实使用严格 atomic evidence；普通分析允许保守段落级证据；
8. 只有运行结果会改变架构、兼容、复现或性能判断时才执行仓库；
9. coverage matrix 是诊断工具，不是必须逐格填满的配额；
10. 停止条件是新增检索是否仍改变字段边界、核心命题或决策，而不是形式上的全格闭环。

## 5. 当前验证

- bundle normal validation：PASS；
- bundle strict validation：PASS；
- Skill tests：104/104 PASS；
- final-integrity：PASS；
- 45 个 Markdown deliverables、61 个相对链接、45 个 deliverable hashes、17 个 Skill snapshot files 均通过；
- GitHub star-growth packet：59 observations、59 metrics、59 raw snapshots，hash 与结构校验 PASS；
- coverage 的 partial/gap cells 保留为诊断 advisory，不再错误地充当发布硬门。

## 6. 不影响交付但必须保留的边界

1. star-history 不能可靠复原，因此没有增长榜；
2. 未运行第三方仓库，故不声称安装可复现性、真实性能或生产行为；
3. Crossref/arXiv manifestation 仍可能重复，identifier count 是广度上界；
4. 多项 2026 work 仍是 preprint 或作者证据，独立复现有限；
5. 没有当前版本独立 conformance、可归因 production deployment 或完整 two-party round-trip evidence；已有两个外部集成信号仍只算弱证据。

这些限制已经进入 reader reports，并未被总体数量、stars、README 或绿色验证器掩盖。

## 结论

v09 已实现 USER_FEEDBACK 要求的核心转变：从小型精选来源和介绍式报告，变为 breadth-first 的字段地图、分析型多文件综述、逐重要簇深研、GitHub 工程雷达和可行动的执行结论。剩余限制会影响个别结论的置信度，但不再构成报告结构、输入广度或研究方法方向上的缺口。
