# MM-C10｜具身、多模态与世界状态记忆：深度报告

> 状态：final standalone cluster report；截至 2026-08-10。本文只重组 v09 已打开、已落账的来源，不新增事实，不代表代码已经运行。

## 1. 决策摘要：这里的核心不是“多存一种模态”，而是维护可行动的世界状态

MM-C10 的边界应由决策闭环定义：观察必须被定位到时间、空间、可见性与行动后果；记忆必须在后续状态变化后仍能被更新或判废；取回内容必须能改变计划。仅把图片转成文本并长期保存，或把技能库统一称为“多模态记忆”，都不足以落入这一中心边界。现有证据支持四个可组合部件：世界状态图（AriGraph）、轨迹与技能双流（XSkill）、个性语义/视觉概念与具身轨迹分离（POLAR）、固定预算压缩（MeMento）。它们解决的是不同瓶颈，当前没有证据支持单一实现统治所有任务。

面向实现的默认决策是：把“观测事实”“时态世界状态”“程序性经验/技能”“用户偏好”分开存储和治理，在规划前做按任务拼装；若部署资源受限，以固定 token 压缩作为上下文入口，但保留可回溯的原始轨迹或来源指针，避免压缩结果成为不可修复的唯一真相。这个决策是对已记录机制和失败模式的工程综合，不是任何单一来源直接声称的最佳架构。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C14`, `EXP-C15`, `EXP-C20`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `EXP-V39`, `EXP-V40`.

## 2. 边界与演化：从“记住历史”转向“维护、压缩并执行状态”

本簇包含：第一人称或环境视觉/文本观测、部分可观测下的状态累计、空间和对象关系、行动轨迹与反馈、由轨迹抽出的技能、以及这些内容对后续具身计划的作用。它不自动包含纯对话用户画像、无环境闭环的通用技能库，或只有短期视觉上下文的 VLA；只有当持久状态跨步骤或跨任务被写入、读取并影响决策时，才属于核心。

证据显示了清晰但非线性的演化。2023 年 Memory Gym 提供部分可观测、无穷任务的 RL 边界案例；2024 年 JARVIS-1 的已发布仓库仍是离线评估快照，固定且不完整的 memory 文件不能被误读成完整在线写入—索引—读取系统；2025 年 AriGraph 把 episodic 与 semantic memory 合入可更新的世界图；2026 年的 XSkill、POLAR、STALE、WorldLines 与 MeMento 分别把问题推进到视觉落地技能、长期个性化、更新后仍按旧状态行动、长时状态维护失败和固定预算压缩。MemoryVLA 的仓库元数据表明这一方向继续向 VLA/机器人操作扩散，但该仓库在本轮没有执行，不能用仓库描述替代性能验证。

因此，“更长历史”不是这条演化线的唯一方向。更关键的是把历史转成结构化状态、区分仍有效与已失效内容，并把状态落实到动作。STALE 的 400 个冲突场景/1,200 个查询中，作者报告最佳总体准确率仍为 55.2%，恰好说明“更新已入库”与“计划已适应”之间仍有断层；该数字只在其作者协议内成立。

**本节证据索引** — Claims: `BEN-C24`, `PRJ-A010`, `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C13`, `EXP-C14`, `EXP-C15`, `GR-C028-3`, `GR-C028-2`. Evidence: `BEN-EV47`, `BEN-EV48`, `PRJ-AE010-01`, `PRJ-AE010-02`, `PRJ-AE010-03`, `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `GR-V028-3`, `GR-V028-2`.

## 3. 机制地图：四类机制不是同义替代品

| 机制 | 主要状态单元 | 写入/更新重点 | 读取重点 | 最适问题 | 已知脆弱点 |
|---|---|---|---|---|---|
| 世界状态图 | 实体、关系、事件/episode | 将新观察合入 semantic + episodic 图 | 围绕当前目标检索相关子图 | 关系、空间、时态依赖 | 部分可观测、覆盖旧状态、图到计划的落差 |
| 轨迹—技能双流 | action-level experience + task-level skill | 从 rollout 累计经验并抽取技能 | 依据当前视觉上下文检索并适配 | 重复任务与程序性迁移 | 技能适配是否保留状态细节仍依任务而定 |
| 个性化多模态图 | semantic context、visual concept、embodied trajectory | 分离用户/概念状态与具体轨迹 | 按用户与当前情境组合 | 长期个性化具身交互 | 身份漂移、删除和真实长期用户验证未闭合 |
| 固定预算压缩 | preference-conditioned compressed state | 在固定 token 预算下合并长轨迹 | 把压缩态直接供决策 | 上下文/存储预算受限 | 丢失来源跨度、旧状态残留、作者基准外泛化未知 |

这张表支持“按瓶颈选机制”，不支持把四者排成单一排行榜。图方法偏向显式关系维护；双流偏向经验到技能的复用；分离式多模态图强调不同知识类型不要相互污染；压缩强调预算。它们可以串联，但串联后还必须单独测量更新、读取、规划与成本，否则无法知道增益来自哪里。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C14`, `EXP-C15`, `EXP-C21`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `EXP-V41`, `EXP-V42`.

## 4. 参考架构：分层状态面，而不是一个统一向量库

```text
视觉/文本/环境信号
        │
        ▼
[观测归一化 + 时间/可见性/来源标注]
        │
        ├──> [事件轨迹 / 原始来源指针]
        ├──> [世界状态图：实体-关系-当前/历史状态]
        ├──> [程序面：动作经验 -> 任务技能]
        └──> [个性面：用户语义 + 视觉概念]
                         │
当前目标 ──> [候选检索] ──> [冲突/时效选择] ──> [预算压缩/拼装]
                                                   │
                                                   ▼
                                             [规划与行动]
                                                   │
                                      新观察/成功/失败回写
```

架构的关键隔离点有三个。第一，原始轨迹与派生状态分开，使后续冲突能够回溯；第二，程序性技能与陈述性世界状态分开，避免“如何做”覆盖“现在是什么”；第三，压缩是读取前的预算层，而不是唯一存储层。AriGraph、XSkill、POLAR 与 MeMento 分别为这些层提供机制证据；WorldLines 和 STALE 则说明缺少时态冲突处理与行动闭环会失败。

该架构不是已执行实现。它是从不同来源中抽取的最小可组合控制面：每层都应保留 provenance、时间与版本，使 planner 可以知道“这条内容是什么、何时成立、从哪里来”。v09 未执行这些系统，也没有共同代码路径证明这些部件可无摩擦组合。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C13`, `EXP-C14`, `EXP-C15`, `PRJ-A010`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `PRJ-AE010-01`, `PRJ-AE010-02`, `PRJ-AE010-03`.

## 5. 算法与数据流：把“记忆正确”拆成五个可诊断阶段

1. **观测建档**：保存模态、时间、可见范围与动作前后关系；具身记忆的额外信息正是 observation grounding、visibility、spatial/world state 与 action consequence。
2. **状态投影**：把事件投影为当前世界状态，同时保留 episode；图方法可把 semantic 与 episodic 连接，但不能只保留最后一次覆盖值。
3. **经验抽象**：从 rollout 形成 action-level experience，再抽取 task-level skill；抽象结果与具体状态保持链接，而不是把动作模板当成世界事实。
4. **目标条件读取**：按当前任务取回世界子图、相关 episode、技能与个性上下文；对互相冲突的候选先做时效/来源选择，再进入预算压缩。
5. **行动后校验**：计划执行后，用新观察校验状态并回写；“已更新但仍按旧值行动”必须被单独记录为 policy-adaptation failure。

这一数据流把错误定位为：看漏了、写错了、覆盖错了、取错了、压缩丢了、或者取对了却没行动。现有文献分别暴露了这些环节，但没有同一协议同时诊断全部五段。因此，实现时应为每段输出可检查的中间产物，而不能只看最终任务成功率。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C13`, `EXP-C14`, `EXP-C15`, `EXP-C20`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `EXP-V39`, `EXP-V40`.

## 6. 实现与集成：仓库证据只能回答“公开了什么”，不能回答“跑得怎样”

JARVIS-1 是重要的反例：固定来源检查显示其发布物是离线评估快照，`assets/memory.json` 不完整，README 明示 descriptor、retrieval、`learning.py` 与 online growing memory 未发布。依赖面包含固定的 torch/torchvision、gym/gymnasium、Malmo/JDK8 与 OpenAI API，且 README 提示版本冲突可能；这使其部署成本明显高于普通 memory library，但本轮没有运行，不能推断实际安装成功率或性能。

MemoryVLA 的固定快照有 setup 文档，但在检查树中未找到 CI 与 tests，且未执行；“未找到”不等于不存在实现。JARVIS-1 同样 setup 有文档、tests 存在、CI 在已检查树中未找到、未执行。两者都不应仅按 star 数或论文会议标签被视为工程成熟：stars 是 2026-08-10 的累计单点快照，不是增长率或采用证据。

集成验收至少要区分四层：数据接入能否保留图像/文本与环境时序；状态存储能否保留历史版本而非最后值；planner 接口能否同时接受状态、技能和压缩预算；环境层是否可重复构建。当前 ledger 只支持静态源码/README 结论，无法完成运行时验收。

**本节证据索引** — Claims: `PRJ-A010`, `PRJ-I010`, `GR-C027-1`, `GR-C027-2`, `GR-C028-1`, `GR-C028-2`. Evidence: `PRJ-AE010-01`, `PRJ-AE010-02`, `PRJ-AE010-03`, `PRJ-IE010-01`, `PRJ-IE010-02`, `GR-V027-1`, `GR-V027-2`, `GR-V028-1`, `GR-V028-2`.

## 7. 成本模型：固定 token 只是读取成本，维护世界状态还有写入与修复成本

MeMento 的作者报告提供了一个强但窄的信号：在其 DunphyBench 对照中，相对作者所称最强基线，准确率提升 7.18%、memory usage 降低 85.38%。这证明固定预算压缩值得作为候选，却不能外推到图维护、技能抽取或真实机器人运行。JARVIS-1 的依赖和环境准备则说明系统成本还包括模型运行时、Minecraft/Malmo/JDK、权重与外部 API；这些是静态集成约束，不是测得的延迟或费用。

因此 C10 的成本向量应分别记录：每步观测写入、图合并/版本化、技能抽取、候选检索、压缩、planner 调用、环境执行、失败后修复，以及持久字节/版本数。现有证据没有给出跨系统的 matched-budget 比较，不能把“memory usage”单列成总成本。报告任何性能增益时，必须同时固定候选数、检索 token、planner、任务和运行环境。

**本节证据索引** — Claims: `EXP-C15`, `PRJ-I010`, `BEN-C25`. Evidence: `EXP-V29`, `EXP-V30`, `PRJ-IE010-01`, `PRJ-IE010-02`, `BEN-EV49`, `BEN-EV50`.

## 8. 基准条件：按任务族分层，不做跨族总榜

EMemBench 从 agent 自身的文本/视觉游戏轨迹构造问题，并用游戏信号计算 ground truth，适合观测—状态记忆；Mem-Gallery 面向多模态长期对话，适合提取、适应、推理与知识管理；Memory Gym 是部分可观测 RL 的轨迹边界；STALE 与 WorldLines 更接近冲突更新和长时具身状态失败；DunphyBench/MeMento 的结果用于固定预算压缩。它们的输入、干预、agent 设定和成功标准不同，不能把数值直接并列。

一个可复核的 C10 评估应至少分四组：

| 组 | 固定条件 | 主指标 | 必须同时报告 |
|---|---|---|---|
| 观测—状态 | 相同轨迹、可见性与 ground truth | 状态/问答正确 | 写入与检索 token、状态版本数 |
| 状态—行动 | 相同环境、planner 与动作预算 | 任务成功/动作正确 | 取回正确但行动错误率 |
| 个性化冲突 | 相同用户历史与更新干预 | 最新有效状态使用 | 旧状态误用、删除/纠正结果 |
| 压缩预算 | 相同原始轨迹、token 上限与 planner | 准确/任务成功 | 压缩率、来源覆盖、延迟 |

这是一种协议设计综合；现有 claim 支持“任务族不可比较”和“应报告结果+成本向量”，但未证明某个统一 harness 已完成这些条件。

**本节证据索引** — Claims: `BEN-C10`, `BEN-C14`, `BEN-C24`, `BEN-C22`, `BEN-C25`, `EXP-C13`, `EXP-C14`, `EXP-C15`, `EXP-C21`. Evidence: `BEN-EV19`, `BEN-EV20`, `BEN-EV27`, `BEN-EV28`, `BEN-EV47`, `BEN-EV48`, `BEN-EV43`, `BEN-EV44`, `BEN-EV49`, `BEN-EV50`, `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `EXP-V41`, `EXP-V42`.

## 9. 失败与负面证据：取回成功不等于决策成功

负面证据集中在三条链路。其一，WorldLines 把困难定位为 partial observability、world state 被覆盖、以及 memory 到 plan 的转换。其二，STALE 表明存储更新后，响应仍可能围绕旧值制定计划，并在其作者设置中留下明显准确率缺口。其三，压缩虽能降低内存预算，但现有结果仅来自作者特定对照，没有跨系统复现，也没有证明来源跨度和冲突信息不会在压缩中丢失。

工程端还有更基础的负面边界：JARVIS-1 发布包缺失完整在线记忆路径；MemoryVLA 在检查树中未找到 CI/tests 且未执行。这些不能证明系统无效，却足以阻止把 README 功能描述升级为“已验证工程能力”。任何上线决策都必须把静态可见、可安装、可运行、可复现和可运营分开。

**本节证据索引** — Claims: `EXP-C13`, `EXP-C14`, `EXP-C15`, `PRJ-A010`, `GR-C027-2`, `GR-C028-2`. Evidence: `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `PRJ-AE010-01`, `PRJ-AE010-02`, `PRJ-AE010-03`, `GR-V027-2`, `GR-V028-2`.

## 10. 替代方案与取舍

- **只保留原始多模态历史**：来源最完整，但读取预算会随轨迹增长；现有证据没有给出其跨任务成本上界。适合作为审计底座，不宜直接成为 planner 唯一输入。
- **只保留压缩态**：可控制 token，但一旦冲突或错误被压缩，缺少原始来源会妨碍修复。MeMento 仅支持特定作者对照中的收益。
- **只保留世界图**：适合关系和当前状态，但容易把不确定观察硬化为事实，也可能覆盖历史状态；WorldLines 的失败模式要求版本化 episode 回链。
- **只保留技能库**：对重复动作有利，却可能把“如何做”与“当前世界是什么”混淆；XSkill 的双流本身就是分离经验与技能的证据。
- **推荐的混合方案**：原始/事件层负责可追溯，世界图负责显式状态，技能层负责程序复用，压缩层负责读取预算；其代价是写放大、同步与修复复杂度，尚无共同实验证明端到端最优。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C14`, `EXP-C15`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`.

## 11. 共识、少数路线与仍未决的问题

**强共识（多类来源交叉支持）**：具身/多模态记忆必须表示可见性、空间/世界状态和行动后果；长期效果不能只由静态问答衡量；检索正确与行动正确是两个阶段；跨 procedural、personalized-conflict、embodied-state 协议不能做统一排行榜。

**正在形成的共识**：世界状态与 episode 应同时存在；程序性技能与状态事实应分层；预算压缩应在 matched protocol 下测量。这里的“共识”是本语料中机制趋同，不是社区投票结果。

**少数/竞争路线**：显式图、双流技能、个性化图与固定预算压缩分别把不同对象设为中心。现有证据不足以断言哪一条是通用赢家；尤其缺少同环境、同 planner、同 token/动作预算下的直接对照。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C13`, `EXP-C14`, `EXP-C15`, `EXP-C20`, `EXP-C21`, `BEN-C22`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `EXP-V39`, `EXP-V40`, `EXP-V41`, `EXP-V42`, `BEN-EV43`, `BEN-EV44`.

## 12. 工程决策矩阵

| 决策情境 | 首选设计 | 必做验证 | 当前证据限制 |
|---|---|---|---|
| 状态关系/时间冲突主导 | 版本化世界图 + episode 回链 | 冲突注入、旧值误用、图到行动 | 主要是论文机制与作者协议 |
| 重复任务/技能迁移主导 | 经验—技能双流 | 视觉情境适配、错误技能撤回 | 未有共同长期部署对照 |
| 长期用户具身交互 | 个性语义/视觉概念与轨迹分离 | consent/correction/delete、身份漂移 | 缺长期真实用户 matched baseline |
| token/存储受限 | 原始留存 + 读取时固定预算压缩 | 来源跨度、冲突保真、成本向量 | 压缩收益为特定作者结果 |
| 采购现成仓库 | 先 pinned install/run，再谈能力 | 环境构建、tests/CI、版本/许可证 | v09 仅静态检查且未运行 |

禁止性决策：不因 GitHub stars、会议标签或 README 描述直接选择；不把 JARVIS-1 固定 memory 文件当成完整在线系统；不跨基准族平均分数；不把一次取回正确视为行动闭环已解决。

**本节证据索引** — Claims: `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C13`, `EXP-C15`, `PRJ-A010`, `PRJ-I010`, `GR-C027-1`, `GR-C028-1`, `BEN-C22`, `BEN-C25`. Evidence: `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V25`, `EXP-V26`, `EXP-V29`, `EXP-V30`, `PRJ-AE010-01`, `PRJ-AE010-02`, `PRJ-AE010-03`, `PRJ-IE010-01`, `PRJ-IE010-02`, `GR-V027-1`, `GR-V028-1`, `BEN-EV43`, `BEN-EV44`, `BEN-EV49`, `BEN-EV50`.

## 13. 分层深选：为什么是这些来源

深选不是按数量或 stars 排名，而是覆盖不同机制、时间窗、载体和反证角色。全部为已打开 T1。

| 层 | 代表来源（日期/版本） | 角色 | 对应 claim → evidence |
|---|---|---|---|
| foundation/boundary | Memory Gym（2023-09-29） | 部分可观测轨迹边界 | `BEN-C24` → `BEN-EV47`, `BEN-EV48` |
| 2024 工程基线 | JARVIS-1 pinned `aa9bd…`（2024-04-08） | 离线发布物与依赖负边界 | `PRJ-A010`, `PRJ-I010` → `PRJ-AE010-01..03`, `PRJ-IE010-01..02` |
| 2025 结构机制 | AriGraph（2025-05-15） | semantic + episodic 世界图 | `EXP-C08` → `EXP-V15`, `EXP-V16` |
| rolling-12m 机制 | XSkill（2026-07-01） | 经验—技能双流 | `EXP-C11` → `EXP-V21`, `EXP-V22` |
| rolling-12m 机制 | POLAR（2026-05-25） | 个性/视觉概念/轨迹分离 | `EXP-C12` → `EXP-V23`, `EXP-V24` |
| rolling-90d 反证 | STALE（2026-05-07） | 更新与行动脱节 | `EXP-C13` → `EXP-V25`, `EXP-V26` |
| rolling-90d 反证 | WorldLines（2026-06-17） | 部分可观测、覆盖、规划失败 | `EXP-C14` → `EXP-V27`, `EXP-V28` |
| rolling-90d 成本 | MeMento/DunphyBench（2026-08-02） | 固定预算压缩 | `EXP-C15` → `EXP-V29`, `EXP-V30` |
| rolling-90d 仓库 | MemoryVLA pinned `d732…`（2026-06-13） | VLA 工程雷达、未执行边界 | `GR-C028-1..3` → `GR-V028-1..3` |
| benchmark | EMemBench（2026-01-23）、Mem-Gallery（2026-01-07） | 状态轨迹与多模态对话协议 | `BEN-C10`, `BEN-C14` → `BEN-EV19`,`BEN-EV20`,`BEN-EV27`,`BEN-EV28` |

此选择刻意包含作者论文、固定仓库、基准与负面发现；它仍缺独立运行复现，因此“来源分层”不能被误写为“证据完全独立”。

**本节证据索引** — Claims: `BEN-C24`, `PRJ-A010`, `PRJ-I010`, `EXP-C08`, `EXP-C11`, `EXP-C12`, `EXP-C13`, `EXP-C14`, `EXP-C15`, `GR-C028-1`, `GR-C028-2`, `GR-C028-3`, `BEN-C10`, `BEN-C14`. Evidence: `BEN-EV47`, `BEN-EV48`, `PRJ-AE010-01`, `PRJ-AE010-02`, `PRJ-AE010-03`, `PRJ-IE010-01`, `PRJ-IE010-02`, `EXP-V15`, `EXP-V16`, `EXP-V21`, `EXP-V22`, `EXP-V23`, `EXP-V24`, `EXP-V25`, `EXP-V26`, `EXP-V27`, `EXP-V28`, `EXP-V29`, `EXP-V30`, `GR-V028-1`, `GR-V028-2`, `GR-V028-3`, `BEN-EV19`, `BEN-EV20`, `BEN-EV27`, `BEN-EV28`.

## 14. 缺口、可逆条件与真实饱和

仍开放两项直接缺口。`GAP-CNS-06`：缺少长期真实用户、matched no-profile baseline，以及 consent/correction/delete intervention 与 identity drift、sycophancy、extraction 的联合研究。`GAP-CNS-08`：现有 harness candidates 尚未证明能固定 dataset/model/agent wrapper/retrieval-token-tool budget/seed/judge，同时保留协议族标签并重跑 action/security families。若其中任一获得独立、matched、可运行证据，本稿的默认架构或基准决策都应重审。

饱和声明只表示**边界/命题停止变化**，不表示证据完备。真实终止轮为：

- `FM-EV-CLUSTER-MM-C10-11`：查询 `SAT11-C10-OA`, `SAT11-FOUNDATION-OA`, `SAT11-GH-C10C11`；审计 21 个唯一候选；0 新实体、0 新高信号、0 新一阶簇、0 新立场；boundary/proposition/material 均为 false。
- `FM-EV-CLUSTER-MM-C10-12`：查询 `SAT12-C10-ARXIV`, `SAT12-FOUNDATION-ARXIV`, `SAT12-GH-C10C11`；审计 28 个唯一候选；同样无物质变化。

据 `SAT-CL-MM-C10`，最终范围内共有 10 条 targeted queries、13 个 deep-verified memberships，残余缺口保留为上述两个 ID。停止的理由是连续两轮没有新增一阶叶子或改变决策命题；并非认为仓库已执行、长期用户证据已取得，或各机制已经做过 matched comparison。

**本节证据索引** — Claims: `EXP-C20`, `EXP-C21`, `BEN-C22`, `BEN-C23`, `GR-C027-2`, `GR-C028-2`. Evidence: `EXP-V39`, `EXP-V40`, `EXP-V41`, `EXP-V42`, `BEN-EV43`, `BEN-EV44`, `BEN-EV45`, `BEN-EV46`, `GR-V027-2`, `GR-V028-2`. Saturation ledger IDs: `SAT-CL-MM-C10`, `FM-EV-CLUSTER-MM-C10-11`, `FM-EV-CLUSTER-MM-C10-12`.



<!-- synthesis:CLY-C10 claims:EXP-C11,EXP-C12,EXP-C14,EXP-C20,EXP-C21 clusters:MM-C10 -->
