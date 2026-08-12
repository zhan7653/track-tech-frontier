# v09 → v10 结构映射

v10 不按 v09 的 cluster 编号向读者组织内容，而是按“技术机制 → 应用场景 → 重点工程案例”组织。这样做不会丢弃 v09 的范围：每个新页面都能回溯到一个或多个 v09 C01–C16，以及相应的证据和项目材料。v09 的原始字段树与完整边界见 [v09 field tree](../../agent-memory-v09/bundle/reports/02-field-tree.md)。

## 新读者结构与旧分类

| v10 读者层 | 主要问题 | v09 来源 | 处理方式 |
|---|---|---|---|
| 总览与通用架构模型 | 状态怎样从经验进入行动链路 | C01、C02、C03、C04、C05、C07、C12、C13、C14 | 跨簇综合；不把旧 DAG 或内部 ID搬入正文 |
| 对象、作用域与表示 | 记忆保存什么、属于谁、何时有效 | C03、C08、C10、C11、C14；边界 C15 | 合并关系/时间、身份、世界和共享状态的语义 |
| 写入、生命周期与演化 | 如何形成、更新、巩固、冲突处理、遗忘与撤销 | C01、C05、C08、C12 | 以 mutation/control 问题重组，而非按服务或论文分段 |
| 存储、检索与上下文构造 | 如何保存、索引、取回并压缩为有限上下文 | C01、C02、C03、C04、C07 | 把 substrate、检索与 working context 的不同职责并列解释 |
| 经验、技能与任务记忆 | 如何从轨迹、反馈、项目状态形成可复用经验 | C06、C09；关联 C05、C07 | 保留技能和 Coding/环境状态的不同对象与实现边界 |
| 共享、世界与多模态状态 | 如何处理多主体、可移植、具身与世界模型状态 | C10、C11；关联 C03、C12 | 按 authority、同步与部分可观测性展开 |
| 场景视图 | 个人助手、Coding、多 Agent、世界状态如何裁剪机制 | C08、C09、C10、C11；支持视图 C16 | 跨分支组合说明；不构成新 taxonomy 或推荐 |
| 评测与可比性 | 是否真正衡量到了记忆及其副作用 | C13；关联 C04、C05、C06、C07、C10、C12 | 横切主题，不作为“某一种 memory” |
| 安全、隐私、治理与可靠性 | 谁能写、读、撤销和相信状态 | C12；关联 C01、C05、C08、C11 | 横切主题，贯穿 write→store→retrieve→act |
| 成本、可观测性与工程集成 | 上下文预算、运行边界、服务与互操作 | C01、C02、C07、C11；支持视图 C16 | 横切主题；不把一般框架 feature list 当作 Memory 主体 |
| 理论与相邻边界 | 术语、模型原生状态、RAG/长上下文等边界 | C14；边界 C15、C16 | 提供最小必要解释，不设独立历史主体章节 |
| 重点 GitHub 工程案例 | 代码中哪些模块真实存在、如何流动 | v09 16 个 project deep dives，主要关联 C01–C12 | 少量项目按机制/场景挂靠；不按 stars 或固定数量扩充 |

## C01–C16 的去向

| v09 cluster | v10 去向 |
|---|---|
| C01 Memory Services & Control Planes | 通用架构、写入生命周期、存储检索、工程集成 |
| C02 Agent-Memory Storage & Indexing | 存储、索引与工程集成 |
| C03 Structured / Relational / Temporal | 对象作用域表示；存储检索；共享/世界状态 |
| C04 Retrieval / Ranking / Navigation | 存储、检索与上下文构造；评测 |
| C05 Lifecycle / Consolidation / Forgetting | 写入、生命周期与演化；安全治理；评测 |
| C06 Experience / Procedures / Skills | 经验、技能与任务记忆 |
| C07 Working Context / Compression / Cost | 存储检索与上下文构造；成本横切 |
| C08 Personalization / Identity / Continuity | 对象作用域表示；个人助手场景；生命周期 |
| C09 Coding / Project / Environment | 经验、技能与任务记忆；Coding Agent 场景；工程案例 |
| C10 Embodied / Multimodal / World State | 共享、世界与多模态状态；相关场景 |
| C11 Shared / Distributed / Portable | 共享、世界与多模态状态；多 Agent 场景；互操作 |
| C12 Security / Privacy / Integrity / Governance | 安全、隐私、治理与可靠性横切页 |
| C13 Evaluation / Benchmarks / Comparability | 评测与可比性横切页；总览的证据限定 |
| C14 Foundations / Theory / Taxonomies | 总览中的定义与边界；理论与相邻边界 |
| C15 Model-Native / Parametric Boundary | 仅在边界说明中保留，防止与外部 Memory 混同 |
| C16 Application / Framework Support View | 场景和工程集成的支持性视图，不作为机制主分支 |

映射是多对多的：例如 C03 同时影响表示、存储、检索、共享和世界状态；C12、C13 横切整个链路。它不表示 v10 对 v09 重新计数，也不表示一个 v09 项只可属于一个 v10 页面。要追溯原始成员、筛选和证据，仍应回到 v09 的 [cluster reports](../../agent-memory-v09/bundle/clusters/) 与 [audit materials](../../agent-memory-v09/bundle/reports/12-input-audit.md)。
