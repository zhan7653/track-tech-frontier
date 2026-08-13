# 2026-08-12：机制分支深度补查

## 为什么补查

v10 第一版的总览已能建立领域地图，但六个机制分支对各方案族的内部工作方式解释不足。本轮以 v09 深证据为主体重写，仅做一次窄幅新近性复核，检查截至 2026-08-12 是否有会明显增强机制解释或改变一级路线的新论文。

## 查询范围

2026-08-12 通过公开 Web/arXiv 检索执行了四类精确范围：

- `site:arxiv.org agent memory August 2026 long-term memory agents`
- `site:arxiv.org agent memory retrieval consolidation August 2026`
- `site:github.com agent memory created August 2026 GitHub`
- `site:arxiv.org agent memory procedural skills memory August 2026`

这是编辑阶段的定向 gap check，不是重新运行 v09 的全量 paper/GitHub discovery。GitHub 结果没有发现会改变六个一级机制分支的项目，因此没有新增项目深潜或趋势排名。

## 新纳入的机制证据

| 来源 | 为什么纳入 | 影响的读者分支 | 使用边界 |
|---|---|---|---|
| [Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads](https://arxiv.org/abs/2606.06448) | 将 memory execution 拆为 ingestion、construction、storage、retrieval、prompt assembly、generation、maintenance，并对十类系统做分阶段成本表征 | 写入形成、存储索引、检索上下文 | 2026-06-04 预印本；结果依赖作者的系统适配、模型、硬件与协议，不据其表格做通用排名 |
| [Is Agent Memory a Database? Rethinking Data Foundations for Long-Term AI Agent Memory](https://arxiv.org/abs/2605.26252) | 将正确性提升到 state trajectory，并提出 content/structure/policy、state-level operators 与 MemState 原型 | 对象作用域、写入形成、存储索引、生命周期 | 2026-05-25 vision/prototype 预印本；结构性论点与原型不等于成熟引擎或行业共识 |
| [Managing Procedural Memory in LLM Agents: Control, Adaptation, and Evaluation](https://arxiv.org/abs/2606.23127) | 用 AFTER 把程序性技能的 local、cross-task、cross-role、cross-model transfer 分开 | 使用反馈与技能 | 2026-06-22 预印本；数值仅限作者的 382-task、六角色、22-skill 协议，不外推为生产收益 |

## 结论变化

一级技术地图没有变化。三项证据分别加深了三个既有判断：复杂 Memory 会把成本从查询搬到 construction；长期正确性需要检查状态轨迹而非单条记录；程序性记忆要以迁移和适用性而非原任务重试来评测。它们未改变对成熟度的保守判断，也未形成产品或仓库推荐。
