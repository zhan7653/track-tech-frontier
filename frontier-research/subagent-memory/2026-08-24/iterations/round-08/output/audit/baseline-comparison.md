# 相对 Agent Memory v10 的基准比较

**基准：** `examples/agent-memory-v10` at `714fd00953cffe185b661143f4a9cfd70a7a1ceb`  
**当前：** Round 07 reader integration，等待最终严格发布审计

## 基准能力画像

Agent Memory v10 的主要输入继承自 v09 bundle：7,634 条 discovery occurrence、4,407 个 entity、292 条查询、21 个 cluster、73 个 deep paper card、86 个 repository card、16 个 engineering profile、385 个 source、464 个 claim、773 个 evidence join 和 45 个 manifested deliverable。其读者层提供独立总览、架构图、六个机制分支及深挖包、四个场景、四个横切报告、趋势、GitHub 雷达和项目报告。

这些数字不是新研究的机械配额。真正基准是：主报告能建立地图；重要分支能解释内部机制；GitHub 报告能跟随固定版本组件和数据流；近期变化被放回机制；关键结论可追溯。

## Round 01 对比

| 维度 | Round 01 状态 | 相对基准 |
|---|---|---|
| 独立领域地图 | 已形成两个边界、七个新分支 | 方向成立，仍需广度稳定性 |
| 输入广度 | 1,644 次发现、1,569 个 entity、四类自动/人工路线 | 低于基准，且 Semantic Scholar 受限 |
| 新鲜度 | 显式 12 个月与 90 天查询已运行 | 初步覆盖，尚未分支级核验 |
| 分支深度 | 每分支有问题、方案族和研究议程 | 明显低于基准深挖包 |
| GitHub 工程分析 | 有候选雷达，无正式 fixed-version profile | 未达基准 |
| Benchmark/安全/反证 | 已进入横切地图 | 未完成协议与独立证据对齐 |
| 可读性 | 总览和架构可独立阅读 | 初版可用，仍需独立读者回归 |
| 可追溯性 | 查询、raw snapshot、entity 和初始映射已保存 | deep claim/evidence 尚未建立 |

Round 01 不宣称达到基准。下一轮优先补广度、新近仓库、Benchmark、产品/runtime 和负面证据；后续再进入分支深潜与源码工程分析。

## Round 02 更新

输入规模已经达到与基准相近的开放候选面：6,898 次 occurrence、4,292 个实体，并显式覆盖产品/runtime、负面和 adoption 路线。独立地图因公开 runtime 文档新增“Subagent-local persistence and identity”一级分支，说明新输入确实改变了结构。

但 mapped population 仍低于基准，分支内部深度、deep-verified paper、Benchmark 协议、claim/evidence 和 fixed-version project report 尚未达到基准。因此 Round 02 只通过输入广度与地图信息增益门槛，不通过最终深度和工程质量门槛。

## Round 04 更新

42 篇代表论文完成原文级核验，八个分支均新增内部机制页，Benchmark 协议被拆成 governance、conflict/commit、experience-transfer 和 runtime-retention 等不可直接排名的比较组。论文输入已实际改变分类和正文，而不是只出现在 bibliography。

当前论文深度接近基准的读者效果，但 fixed-version GitHub engineering profile 仍为零，分支也尚缺工程组件、真实依赖、维护边界和独立反证。整体仍未达到最终基准。

## Round 05–07 更新

当前输入规模为 6,898 次 discovery occurrence、4,298 个实体、93 条查询；它略低于基准 occurrence/entity，但保持明确 12 个月/90 天窗口和 2,063 个 GitHub entity。深层输入为 42 篇 opened PDF 与 10 个固定版本仓库，少于基准的 73 paper/16 profile，但专题范围更窄，且八个一级分支各有独立机制深页。

| 维度 | 当前状态 | 相对基准判断 |
|---|---|---|
| 主地图 | 两个边界、三个权威层、八个一级机制 | 达到；为 Subagent topic 独立推导 |
| 输入广度/新鲜度 | 4,298 entities；3,329 recent-12m；1,565 recent-90d（Round 02 统计） | 接近；明确 recent 搜索与 gap 保留 |
| 论文深度 | 42 PDF、状态机/协议/限制深页 | 数量较少，专题聚焦后深度达到 |
| GitHub 工程 | 10 fixed commits、activity observations、profiles、project reports | 项目数较少，关键 runtime/service 形状已覆盖 |
| 分支读者深度 | 八个 entry + 八个 mechanism deep page | 达到并覆盖新增 local persistence 分支 |
| 横切分析 | Benchmark、安全、成本/可靠性、互操作 | 达到；从短页升级为机制综合 |
| 趋势 | 区分主流 primitive、进入工程与研究前沿 | 达到；不以 star/新建代替趋势 |
| 人工评审 | 完整报告后只评业务边界与继续深挖 | 达到用户要求 |
| 可追溯性 | 56 claims/evidence、10 synthesis；final publication 待封账 | 内容已具备，Round 08 完成双向 manifest |

结论：当前已达到“读者效果、机制深度和工程对照至少不低于基准”的实质门槛；仍不能在 Round 08 strict validator、deliverable/marker、saturation 和 regression 全部通过前宣称最终完成。
