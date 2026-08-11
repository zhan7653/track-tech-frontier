# MM-C13｜评测、基准与可比性：深度报告

> 状态：final standalone cluster report；截至 2026-08-10。本文只使用 v09 已打开的论文、数据集、固定仓库与证据账本；不引入未落账事实，不声称执行过 runner。

## 1. 决策摘要：不存在一个“memory 分数”，只有受协议约束的能力向量

MM-C13 最重要的结论是拒绝跨协议总榜。静态对话问答、增量更新/遗忘、环境任务成功、工具参数落地、程序性首试、组织多人状态、具身轨迹、安全生命周期分别改变了任务单位、可访问输入、agent 包装、干预与指标；它们的数值不能平均成一个 memory quality。一个系统在静态 recall 上高分，并不自动证明会用最新约束完成工具动作、能在部分可观测环境维护世界状态、能忘掉失效内容，或能抵御持久化投毒。

可执行决策是建立**协议族 × 生命周期阶段 × 成本**的矩阵。每项结果必须带 dataset/version、agent/model、memory API、写入/检索/token/tool 预算、seed、judge、runner commit 与产物；报告写入、更新、检索、推理/行动、遗忘/修复的分段结果，以及延迟、模型调用、tokens、存储/版本成本。统一 harness 可以统一执行外壳，却不能抹掉协议族标签，也不能成为独立分数权威。

**本节证据索引** — Claims: `BEN-C03`, `BEN-C05`, `BEN-C07`, `BEN-C10`, `BEN-C12`, `BEN-C15`, `BEN-C16`, `BEN-C22`, `BEN-C23`, `BEN-C25`, `EXP-C21`, `STD-C023`. Evidence: `BEN-EV05`, `BEN-EV06`, `BEN-EV09`, `BEN-EV10`, `BEN-EV13`, `BEN-EV14`, `BEN-EV19`, `BEN-EV20`, `BEN-EV23`, `BEN-EV24`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `EXP-V41`, `EXP-V42`, `STD-J045`, `STD-J046`.

## 2. 边界与演化：评测对象从“能否回忆”扩展到“能否正确改变行为”

本簇包含数据集、任务生成、agent/memory 接口、执行协议、judge、指标、成本与可复现产物。只提供 memory library 的 demo 不算基准；只聚合数据集而没有固定协议的工具不自动成为评分权威；论文中的作者对照如果缺少共同任务和预算，也不能跨系统排序。

演化可分为五个协议族，而不是按年份罗列项目：

1. **长对话与静态/时态 recall**：LoCoMo、LongMemEval 把长会话 QA、总结和多种记忆能力变成可检查任务。
2. **操作分解与更新/遗忘**：MemoryAgentBench、MemBench、Memora、HaluMem 将准确检索、test-time learning、反思、更新、失效内容与 selective forgetting 分开。
3. **记忆到行动**：Mem2ActBench、StoryBench、MemoryArena、LongMemEval-V2 把约束落到 tool use、分支决策、多 session 行动与 web-agent 经验。
4. **多人、多模态与具身**：GroupMemBench、Mem-Gallery、EMemBench 分别处理 speaker/audience、长期多模态对话和 agent 自身的文本/视觉游戏轨迹。
5. **程序与安全生命周期**：ImplicitMemBench 用首试的 Learning/Priming–Interfere–Test，MemSecBench 用 Write–Execute–Forget；PoisonedEvolution 又表明仅测 artifact modification 的 SER 仍不等于实际危害。

这条演化的重心从“答案是否含过去事实”转向“何时写、如何更新、取回后是否行动、如何忘、成本多少、是否安全”。

**本节证据索引** — Claims: `BEN-C01`, `BEN-C02`, `BEN-C03`, `BEN-C04`, `BEN-C05`, `BEN-C06`, `BEN-C07`, `BEN-C08`, `BEN-C09`, `BEN-C10`, `BEN-C12`, `BEN-C13`, `BEN-C14`, `BEN-C15`, `BEN-C16`, `BEN-C17`, `FM-PE-C05`. Evidence: `BEN-EV01`, `BEN-EV02`, `BEN-EV03`, `BEN-EV04`, `BEN-EV05`, `BEN-EV06`, `BEN-EV07`, `BEN-EV08`, `BEN-EV09`, `BEN-EV10`, `BEN-EV11`, `BEN-EV12`, `BEN-EV13`, `BEN-EV14`, `BEN-EV15`, `BEN-EV16`, `BEN-EV17`, `BEN-EV18`, `BEN-EV19`, `BEN-EV20`, `BEN-EV23`, `BEN-EV24`, `BEN-EV25`, `BEN-EV26`, `BEN-EV27`, `BEN-EV28`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV33`, `BEN-EV34`, `FM-PE-J06`, `FM-PE-J07`.

## 3. 机制地图：用协议族聚类，而不是用项目名堆目录

| 协议族 | 被操纵的状态 | 主要观测点 | 代表协议 | 不可直接推出 |
|---|---|---|---|---|
| G1 长对话 recall | 会话历史、时间事实 | QA/总结/生成 | LoCoMo, LongMemEval | 工具行动、在线写入安全 |
| G2 更新/遗忘诊断 | 事实、反思、有效/失效记忆 | extraction/update/QA/forgetting | MemoryAgentBench, MemBench, Memora, HaluMem | 环境任务成功 |
| G3 action grounding | 用户约束、经验、反馈 | tool 选择/参数、任务成功、自恢复 | Mem2Act, StoryBench, MemoryArena, LongMemEval-V2 | 静态 QA 总体能力 |
| G4 社会/多模态/具身 | speaker/belief、图像、轨迹、世界信号 | audience adaptation、视觉/文本状态、game ground truth | GroupMem, Mem-Gallery, EMemBench | 纯文本 benchmark 排名 |
| G5 procedural/security | priming/interference、poisoned write | first attempt、Write–Execute–Forget、artifact modification | ImplicitMem, MemSec, PoisonedEvolution | 完整危害或生产安全 |

同一系统应在多个族内形成 profile，而不是把不同分母归一后求均值。组内也需要固定访问路径：例如 oracle 数据形态与检索器产生的候选不同；batch 与 stream 执行不是中性包装。LongMemEval 仓库公开 small/medium/oracle 数据形态与可配置 retriever/granularity，MemTools 报告 AWM 在 stream 为 33.58、batch 为 40.30，直接证明协议实现会改变结果；这两个数字只在 MemTools 的作者设置内使用。

**本节证据索引** — Claims: `BEN-C01`, `BEN-C02`, `BEN-C03`, `BEN-C04`, `BEN-C05`, `BEN-C06`, `BEN-C07`, `BEN-C09`, `BEN-C10`, `BEN-C12`, `BEN-C13`, `BEN-C14`, `BEN-C15`, `BEN-C16`, `BEN-C17`, `BEN-C19`, `BEN-C22`, `STD-C023`, `FM-PE-C05`. Evidence: `BEN-EV01`, `BEN-EV02`, `BEN-EV03`, `BEN-EV04`, `BEN-EV05`, `BEN-EV06`, `BEN-EV07`, `BEN-EV08`, `BEN-EV09`, `BEN-EV10`, `BEN-EV11`, `BEN-EV12`, `BEN-EV13`, `BEN-EV14`, `BEN-EV17`, `BEN-EV18`, `BEN-EV19`, `BEN-EV20`, `BEN-EV23`, `BEN-EV24`, `BEN-EV25`, `BEN-EV26`, `BEN-EV27`, `BEN-EV28`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV33`, `BEN-EV34`, `BEN-EV37`, `BEN-EV38`, `BEN-EV43`, `BEN-EV44`, `STD-J045`, `STD-J046`, `FM-PE-J06`, `FM-PE-J07`.

## 4. 参考评测架构：把 dataset、runner、memory 与 judge 解耦

```text
[Dataset + version + protocol-family label]
                     │
                     ▼
[Episode/Session driver] ──> [Agent/model wrapper] ──> [Memory adapter]
        │                         │                       │
        │                         │                 write/read/update/delete
        │                         ▼                       │
        └──────────────────> [tool/environment] <─────────┘
                                  │
                ┌─────────────────┼────────────────┐
                ▼                 ▼                ▼
          [observable trace] [memory trace] [action/tool trace]
                └─────────────────┼────────────────┘
                                  ▼
           [family-specific scorer + judge + cost meter]
                                  │
                                  ▼
   [result vector + fingerprint + seed/raw artifacts + failure taxonomy]
```

协议族标签位于最上游，避免统一 runner 在下游把不同任务压成同一分数。memory adapter 要显式记录 write/read/update/delete，而不是只向 scorer 交最终答案；tool/environment trace 用于区分“记得但没有行动”和“根本没取回”；family-specific scorer 保留原任务语义；cost meter 同时记录性能代价。统一 harness 的价值是固定执行变量和保留中间产物，不是改写 benchmark 的任务单位。

OmniMemEval 与 MemoryData 在当前证据中只是 evaluation-harness candidates，公开描述不足以使其成为独立 benchmark-score authority。LongMemEval-V2 的仓库展示 data preparation、validation 与 leaderboard packaging，且 leaderboard 使用固定 latency–accuracy frontier；它为产物结构提供实例，但不证明能统一全部协议族。

**本节证据索引** — Claims: `BEN-C07`, `BEN-C12`, `BEN-C16`, `BEN-C21`, `BEN-C22`, `BEN-C23`, `BEN-C25`, `STD-C023`. Evidence: `BEN-EV13`, `BEN-EV14`, `BEN-EV23`, `BEN-EV24`, `BEN-EV31`, `BEN-EV32`, `BEN-EV41`, `BEN-EV42`, `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `STD-J045`, `STD-J046`.

## 5. 算法与数据流：先归因失败阶段，再计算最终指标

建议每个 episode 生成一条分段状态链：`input available → memory write attempted → canonical state changed → candidate retrieved → evidence used → answer/action emitted → environment feedback → update/forget/repair attempted`。对每一段保留 success/failure 与成本。这样可将同一个最终错误分成：未写、写错、更新错、没取回、取回错、取回正确但推理/动作错、忘记失败、修复失败。

评分流程应按以下顺序执行：

1. 校验 dataset/version 与 protocol-family；不匹配则不进入同组比较。
2. 固定 agent/model、memory adapter、history access、retrieval/token/tool/action budget、seed 与执行模式。
3. 记录 memory/tool/environment 中间 trace；对于 first-attempt 协议，不允许事后重试覆盖第一次结果。
4. 运行 family-specific scorer；LLM judge 若存在，记录模型/提示/版本并保留原始判定。
5. 输出结果向量与成本向量，不跨族平均；对缺失阶段使用 `not measured`，不以 0 代替。

HaluMem 对 extraction/update/QA 的分解、ImplicitMemBench 的 first-attempt、MemSecBench 的 Write–Execute–Forget，以及 Mem2Act 的 tool selection/parameter grounding共同支持“阶段化归因”。这是评测控制面综合，尚未由一个统一 runner 完成。

**本节证据索引** — Claims: `BEN-C06`, `BEN-C07`, `BEN-C08`, `BEN-C15`, `BEN-C16`, `BEN-C22`, `BEN-C25`, `STD-C023`. Evidence: `BEN-EV11`, `BEN-EV12`, `BEN-EV13`, `BEN-EV14`, `BEN-EV15`, `BEN-EV16`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV43`, `BEN-EV44`, `BEN-EV49`, `BEN-EV50`, `STD-J045`, `STD-J046`.

## 6. 实现与集成：固定仓库让协议可检查，但 v09 没有运行它们

官方仓库提供了不同程度的可复核性：LoCoMo 包含 data、`task_eval` 与 scripts；LongMemEval 暴露 small/medium/oracle 数据形态、retriever 与 turn/session granularity；MemoryAgentBench 含 method/config 目录和 linked dataset；LongMemEval-V2 文档化数据下载、准备、validation 与 leaderboard packaging。这些支持“协议/资产可检查”，不等于本轮复现了论文结果。

工程雷达进一步表明：MemoryAgentBench pinned `455306…` 的 setup 有文档、tests 存在、CI 在检查树中未找到、未执行；OmniMemEval pinned `0b1ea…` setup 有文档、tests 存在、CI 未找到、未执行；`supermemoryai/memorybench` pinned `118209…` setup 有文档、CI/tests 在检查树中未找到、未执行。“未找到”只描述所查树，不能写成零实现。stars 同样只是 2026-08-10 单点累计值。

集成验收应先做 pinned install/test，再核对数据许可/版本、模型/API 依赖、可复现 seed、并行/缓存行为、judge 稳定性和 raw artifact；本稿没有这些运行证据，因此不对三个 runner 的易用性、速度或正确性排序。

**本节证据索引** — Claims: `BEN-C18`, `BEN-C19`, `BEN-C20`, `BEN-C21`, `GR-C035-1`, `GR-C035-2`, `GR-C036-1`, `GR-C036-2`, `GR-C052-1`, `GR-C052-2`. Evidence: `BEN-EV35`, `BEN-EV36`, `BEN-EV37`, `BEN-EV38`, `BEN-EV39`, `BEN-EV40`, `BEN-EV41`, `BEN-EV42`, `GR-V035-1`, `GR-V035-2`, `GR-V036-1`, `GR-V036-2`, `GR-V052-1`, `GR-V052-2`.

## 7. 成本模型：效果与运行代价必须共享同一个实验指纹

一个可比较结果至少需要两组向量。

**效果向量**：write/update accuracy、retrieval/source coverage、answer/reasoning、tool selection/parameter grounding、environment task success、selective forgetting、stale-state error、security inclusion/retrieval/action/repair。**成本向量**：write/retrieve/consolidate/delete/repair/action 的 model calls、tokens、p50/p95、持久 bytes/revisions、index rebuild、audit retention 与 human review load。

当前 ledger 支持“应报告向量而非跨组均值”，但不提供覆盖全链的共同实测。LongMemEval-V2 的固定 latency–accuracy frontier体现了把延迟与准确性并列的方向；ForgetEval 的 LLM-hook gain/cost 是 model- 和 protocol-dependent 作者结果，并记录 external subset、backend 与 LLM-quality 限制；MemTools 的 stream/batch 差异又说明执行模式会改变效果。因而成本必须和同一个 dataset/model/runner/seed 指纹绑定，不能从另一个协议补齐。

**本节证据索引** — Claims: `BEN-C21`, `BEN-C22`, `BEN-C25`, `FND-C22`, `STD-C023`. Evidence: `BEN-EV41`, `BEN-EV42`, `BEN-EV43`, `BEN-EV44`, `BEN-EV49`, `BEN-EV50`, `FND-EV42`, `FND-EV43`, `STD-J045`, `STD-J046`.

## 8. 基准条件：最小实验指纹与组内可比规则

每次结果发布必须包含以下指纹：`benchmark_id + dataset version/hash + protocol family + split + agent/model/version + prompt/config + memory implementation/commit + write policy + retriever/granularity + context/retrieval/tool/action budgets + seed(s) + stream/batch + judge/version + hardware/service region when relevant + raw artifact locations`。其中多数是为确保已知协议差异不被隐藏的工程要求；并非声称当前每个来源都已提供全部字段。

组内比较还需满足：

- LoCoMo/LongMemEval 类固定 history access、turn/session granularity 与 oracle/retrieved 数据形态。
- MemoryAgentBench/MemBench/Memora/HaluMem 类固定更新/失效干预和分段 scoring。
- Mem2Act/MemoryArena/LongMemEval-V2 类固定工具权限、动作预算、环境反馈与 success 定义。
- EMemBench/Mem-Gallery 类固定模态可见性、图像/轨迹处理和 ground-truth 生成。
- ImplicitMem/MemSec/PoisonedEvolution 类固定 first-attempt、污染/attacker support、写—执行—忘记步骤，并把 artifact modification 与实际 harmful action 分开。

若任何关键字段不同，结果仍可报告，但必须作为不同 cell，不能被写成同一 leaderboard 行。

**本节证据索引** — Claims: `BEN-C01`, `BEN-C02`, `BEN-C03`, `BEN-C04`, `BEN-C05`, `BEN-C06`, `BEN-C07`, `BEN-C08`, `BEN-C10`, `BEN-C12`, `BEN-C14`, `BEN-C15`, `BEN-C16`, `BEN-C17`, `BEN-C19`, `BEN-C22`, `FM-PE-C02`, `FM-PE-C03`, `FM-PE-C05`, `STD-C023`. Evidence: `BEN-EV01`, `BEN-EV02`, `BEN-EV03`, `BEN-EV04`, `BEN-EV05`, `BEN-EV06`, `BEN-EV07`, `BEN-EV08`, `BEN-EV09`, `BEN-EV10`, `BEN-EV11`, `BEN-EV12`, `BEN-EV13`, `BEN-EV14`, `BEN-EV15`, `BEN-EV16`, `BEN-EV19`, `BEN-EV20`, `BEN-EV23`, `BEN-EV24`, `BEN-EV27`, `BEN-EV28`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV33`, `BEN-EV34`, `BEN-EV37`, `BEN-EV38`, `BEN-EV43`, `BEN-EV44`, `FM-PE-J03`, `FM-PE-J04`, `FM-PE-J06`, `FM-PE-J07`, `STD-J045`, `STD-J046`.

## 9. 失败与负面证据：最危险的是“同名指标、不同实验”

第一类失败是**construct collapse**：把 recall、reasoning、action、forgetting/security 压成一个总分。第二类是**protocol leakage**：oracle history、不同 granularity、batch/stream、重试或不同 tool permission 未标明。第三类是**stage masking**：最终任务失败却不知道是写入、检索还是行动；或 artifact modification 成功便被误称为实际危害。第四类是**engineering overclaim**：仓库公开、有 stars 或有 setup 文档被升级为可运行/可复现。第五类是**cost omission**：精度提升没有在同指纹下报告 model calls/tokens/latency/storage/repair。

已有负面证据能钉住这些边界：benchmark families 的任务单位和指标不一致；MemTools 的 stream/batch 分数不同；ForgetEval 报告自身后端/子集/LLM 质量限制；PoisonedEvolution 明确 SER 只测持久 artifact modification；三项工程仓库在 v09 都未执行。因此本稿拒绝给出“最佳 benchmark”或“最佳 memory system”。

**本节证据索引** — Claims: `BEN-C22`, `BEN-C23`, `BEN-C25`, `STD-C023`, `FND-C22`, `FM-PE-C05`, `GR-C035-2`, `GR-C036-2`, `GR-C052-2`. Evidence: `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `STD-J045`, `STD-J046`, `FND-EV42`, `FND-EV43`, `FM-PE-J06`, `FM-PE-J07`, `GR-V035-2`, `GR-V036-2`, `GR-V052-2`.

## 10. 替代方案与取舍

| 方案 | 优点 | 关键损失 | 决策 |
|---|---|---|---|
| 单一总榜 | 易传播、易采购 | 混淆任务单位、访问路径与成本 | 拒绝 |
| 每基准单独报告 | 尊重原协议 | 难以形成系统级画像 | 保留为原始层 |
| 协议族内排名 | 有条件可比 | 仍需严格指纹与预算匹配 | 推荐的比较层 |
| 跨族能力向量 | 展示系统覆盖面 | 不产生单一赢家 | 推荐的决策层 |
| 统一 harness | 固定 runner/产物/成本 | 不能自动统一任务语义 | 作为执行基础设施 |
| 独立 matched reproduction | 最高比较价值 | 运行与维护成本高 | 对关键采购/论文结论必做 |

统一 harness 的最低职责是锁定变量、保存 trace 和成本，并输出各协议族原生指标。它不应重写数据、judge 或任务成功定义以换取表面统一。对于没有独立复现的作者结果，只在其协议 cell 内使用并明确来源。

**本节证据索引** — Claims: `BEN-C22`, `BEN-C23`, `BEN-C25`, `EXP-C21`, `STD-C023`. Evidence: `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `EXP-V41`, `EXP-V42`, `STD-J045`, `STD-J046`.

## 11. 共识、少数路线与矛盾

**强共识**：长期 memory 不能只由单轮 recall 衡量；更新、遗忘、行动和成本需要显式协议；静态 QA、环境任务、tool grounding 与 security lifecycle 不是共同 leaderboard；开源 runner 是可复核基础而非自动的独立权威。

**正在形成的共识**：第一方数据/代码、fixed commit、raw artifact 和分段 trace 应共同构成可复现单元；结果应为向量。这里的共识是语料中的多源趋同，不是标准组织裁决。

**少数/竞争路线**：一类 benchmark 加深单一能力诊断（例如 extraction/update/QA 或 first-attempt procedural）；另一类追求更真实的 environment/action；还有工具希望跨数据集统一运行。它们可互补，但前两类保留构念深度，后一类降低运行摩擦。矛盾点是统一度越高，越容易隐藏原协议差异；MemTools 的执行敏感性说明这种风险不是纯理论。

**本节证据索引** — Claims: `BEN-C03`, `BEN-C05`, `BEN-C06`, `BEN-C07`, `BEN-C10`, `BEN-C12`, `BEN-C15`, `BEN-C16`, `BEN-C18`, `BEN-C19`, `BEN-C20`, `BEN-C21`, `BEN-C22`, `BEN-C23`, `BEN-C25`, `STD-C023`. Evidence: `BEN-EV05`, `BEN-EV06`, `BEN-EV09`, `BEN-EV10`, `BEN-EV11`, `BEN-EV12`, `BEN-EV13`, `BEN-EV14`, `BEN-EV19`, `BEN-EV20`, `BEN-EV23`, `BEN-EV24`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV35`, `BEN-EV36`, `BEN-EV37`, `BEN-EV38`, `BEN-EV39`, `BEN-EV40`, `BEN-EV41`, `BEN-EV42`, `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `STD-J045`, `STD-J046`.

## 12. 决策门：什么结果可以支持什么结论

1. **只有论文摘要/作者结果**：支持“该协议/作者报告存在”，不支持跨系统排名。
2. **数据与固定仓库可检查**：支持协议和实现表面审计，不支持结果复现。
3. **pinned runner 成功执行且 raw artifacts 完整**：支持该环境下可运行与结果复现，不自动支持外部有效性。
4. **同 dataset/model/agent/budget/seed/judge 的 matched comparison**：支持协议族内相对判断。
5. **多个协议族、独立组织与成本向量复现**：支持系统级部署决策，但仍以 profile 表达。

对应的拒绝规则：没有 protocol-family label 不进入总览；没有版本/commit 不进入复现表；没有成本不声称效率；没有 write/retrieve/action trace 不解释失败原因；安全 SER 不改写为 harmful-action rate；未执行仓库不进入“通过”列。

**本节证据索引** — Claims: `BEN-C18`, `BEN-C19`, `BEN-C20`, `BEN-C21`, `BEN-C22`, `BEN-C23`, `BEN-C25`, `FM-PE-C05`, `GR-C035-2`, `GR-C036-2`, `GR-C052-2`. Evidence: `BEN-EV35`, `BEN-EV36`, `BEN-EV37`, `BEN-EV38`, `BEN-EV39`, `BEN-EV40`, `BEN-EV41`, `BEN-EV42`, `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `FM-PE-J06`, `FM-PE-J07`, `GR-V035-2`, `GR-V036-2`, `GR-V052-2`.

## 13. 分层深选：以协议覆盖、资产可检查性和反证能力取样

全部为已打开 T1。选择刻意覆盖 foundation、2024–25、rolling-12m/90d、paper/repo/dataset、正向协议与负面边界。

| 层 | 代表来源（日期/版本） | 角色 | claim → evidence |
|---|---|---|---|
| foundation | Memory Gym（2023-09-29） | 部分可观测 RL 轨迹边界 | `BEN-C24` → `BEN-EV47`,`BEN-EV48` |
| conversational | LoCoMo（2024-02-27）、LongMemEval（2024-10-14） | 长对话与能力基线 | `BEN-C01`,`BEN-C02` → `BEN-EV01..04` |
| operation | MemoryAgentBench（2025-07-07）、HaluMem（2025-11-05） | 增量交互与阶段诊断 | `BEN-C03`,`BEN-C06` → `BEN-EV05`,`BEN-EV06`,`BEN-EV11`,`BEN-EV12` |
| action | Mem2Act（2026-01-13）、MemoryArena（2026-02-18） | tool grounding 与跨 session 行动 | `BEN-C07`,`BEN-C08`,`BEN-C12` → `BEN-EV13..16`,`BEN-EV23`,`BEN-EV24` |
| multimodal/social | EMemBench（2026-01-23）、Mem-Gallery（2026-01-07）、GroupMem（2026-05-14） | 轨迹、图像、speaker/audience | `BEN-C10`,`BEN-C13`,`BEN-C14` → `BEN-EV19`,`BEN-EV20`,`BEN-EV25..28` |
| procedural/security | ImplicitMem（2026-04-09）、MemSec（2026-07-29） | first-attempt 与生命周期安全 | `BEN-C15`,`BEN-C16` → `BEN-EV29..32` |
| current repo | LongMemEval-V2 repo `2cc8…`（2026-08-09） | validation/leaderboard packaging | `BEN-C21` → `BEN-EV41`,`BEN-EV42` |
| harness candidates | OmniMemEval `0b1e…`（2026-08-06）、memorybench `1182…`（2026-08-06） | 统一执行雷达、未执行边界 | `BEN-C23`,`GR-C036-1..2`,`GR-C052-1..2` → `BEN-EV45`,`BEN-EV46`,`GR-V036-1`,`GR-V036-2`,`GR-V052-1`,`GR-V052-2` |
| protocol negative | MemTools（2026-07-23） | stream/batch 敏感性 | `STD-C023` → `STD-J045`,`STD-J046` |
| metric negative | PoisonedEvolution v2（2026-08-07） | SER 的阶段限制 | `FM-PE-C05` → `FM-PE-J06`,`FM-PE-J07` |

该取样的“广”体现在协议族和证据角色，不是把所有 benchmark 同权堆叠；“深”体现在固定任务单位、数据路径、运行边界和负面证据。仍缺共同执行，因此不产生横向赢家。

**本节证据索引** — Claims: `BEN-C01`, `BEN-C02`, `BEN-C03`, `BEN-C06`, `BEN-C07`, `BEN-C08`, `BEN-C10`, `BEN-C12`, `BEN-C13`, `BEN-C14`, `BEN-C15`, `BEN-C16`, `BEN-C21`, `BEN-C23`, `BEN-C24`, `GR-C036-1`, `GR-C036-2`, `GR-C052-1`, `GR-C052-2`, `STD-C023`, `FM-PE-C05`. Evidence: `BEN-EV01`, `BEN-EV02`, `BEN-EV03`, `BEN-EV04`, `BEN-EV05`, `BEN-EV06`, `BEN-EV11`, `BEN-EV12`, `BEN-EV13`, `BEN-EV14`, `BEN-EV15`, `BEN-EV16`, `BEN-EV19`, `BEN-EV20`, `BEN-EV23`, `BEN-EV24`, `BEN-EV25`, `BEN-EV26`, `BEN-EV27`, `BEN-EV28`, `BEN-EV29`, `BEN-EV30`, `BEN-EV31`, `BEN-EV32`, `BEN-EV41`, `BEN-EV42`, `BEN-EV45`, `BEN-EV46`, `BEN-EV47`, `BEN-EV48`, `GR-V036-1`, `GR-V036-2`, `GR-V052-1`, `GR-V052-2`, `STD-J045`, `STD-J046`, `FM-PE-J06`, `FM-PE-J07`.

## 14. 残余缺口、可逆条件与真实饱和

`SAT-CL-MM-C13` 保留十一项缺口：`GAP-CNS-01` matched backend/task/budget 的 consolidation/forgetting 复现；`02` 完整删除契约；`03` flat/hybrid/graph/bitemporal/navigation 的 matched cost 对照；`04` raw-turn/constructed ranking reversal 的多系统复现；`05` shared/team memory 动态权限与投毒；`06` 长期真实用户联合研究；`07` full-chain security；`08` 能锁定全部协议变量的 harness；`09` latent/model-native 对照；`11` coding/project memory 共同协议；`12` 全链成本。出现独立 matched reproduction 时，协议族边界、成本结论或部署门应重审。

真实饱和过程同样包含一次材料变化：

- `FM-EV-CLUSTER-MM-C13-11`：查询 `SAT11-C13-OA`, `SAT11-FOUNDATION-OA`, `SAT11-GH-C12C13`；审计 21 个唯一候选，新增 1 entity/1 high-signal；`PoisonedEvolution` 以 `FM-PE-E01` 改变“评测必须区分 artifact modification 与后续危害”的命题；`material_change=true`。
- `FM-EV-CLUSTER-MM-C13-12`：查询 `SAT12-C13-ARXIV`, `SAT12-FOUNDATION-ARXIV`, `SAT12-GH-C12C13`；审计 30 个唯一候选；0 新实体/高信号/一阶簇/立场，边界和命题未变。
- `FM-EV-CLUSTER-MM-C13-13`：查询 `SAT13-C06C12C13-12M-OA`, `SAT13-C06C12C13-OA`, `SAT13-GH-C06C12C13`；审计 19 个唯一候选；再次无物质变化。

最终以 cycle 12+13 作为连续两轮零物质变化的停止证据；范围内累计 27 targeted queries、53 deep-verified memberships。这里的“saturated”只表示当前搜索下 cluster boundary 与决策命题稳定，绝不表示 runner 已执行、十一项缺口已解决或所有 benchmark 已可比。

**本节证据索引** — Claims: `FM-PE-C01`, `FM-PE-C02`, `FM-PE-C03`, `FM-PE-C05`, `BEN-C22`, `BEN-C23`, `BEN-C25`, `GR-C035-2`, `GR-C036-2`, `GR-C052-2`. Evidence: `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J03`, `FM-PE-J04`, `FM-PE-J06`, `FM-PE-J07`, `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `BEN-EV49`, `BEN-EV50`, `GR-V035-2`, `GR-V036-2`, `GR-V052-2`. Saturation ledger IDs: `SAT-CL-MM-C13`, `FM-EV-CLUSTER-MM-C13-11`, `FM-EV-CLUSTER-MM-C13-12`, `FM-EV-CLUSTER-MM-C13-13`.



<!-- synthesis:CLY-C13 claims:BEN-C01,BEN-C03,BEN-C05,BEN-C07,BEN-C12,BEN-C16,BEN-C22,BEN-C25,FM-PE-C02,FM-PE-C03,FM-PE-C05 clusters:MM-C13 -->
