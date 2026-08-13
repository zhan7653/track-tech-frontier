# 技术机制主分支

六个入口沿 Memory 生命周期展开。入口页是地图；每个方向另有三篇深潜，分别解释内部机制与算法、固定版本工程数据流、以及反证与最新研究。读者不必一次读完 18 篇，可以先看入口，再沿关心的问题下钻。

| 主分支 | 入口地图 | 内部机制 | 工程 walkthrough | 反证与前沿 |
|---|---|---|---|---|
| 对象与作用域 | [对象、身份、时间与边界](01-memory-objects-and-scope.md) | [对象模型与状态语义](objects-scope/01-object-models-and-state-semantics.md) | [六种系统形状](objects-scope/03-system-walkthroughs-and-frontier.md) | [身份、双时间、共享与可移植](objects-scope/02-identity-time-and-shared-authority.md) |
| 写入与形成 | [从事件到可提交状态](02-write-and-formation.md) | [capture、分段、抽取、合并与 admission](writing-formation/01-capture-extraction-and-consolidation.md) | [五条写入管线](writing-formation/02-system-walkthroughs.md) | [信息损失、成本、投毒与研究前沿](writing-formation/03-cost-security-and-frontier.md) |
| 表示、存储与索引 | [权威层与访问投影](03-representation-storage-indexing.md) | [SQL/WAL、FTS/BM25、ANN、图和时间索引](storage-indexing/01-authoritative-state-and-index-algorithms.md) | [七种固定版本底座](storage-indexing/02-engineering-walkthroughs.md) | [多后端一致性、故障恢复与新研究](storage-indexing/03-consistency-recovery-and-frontier.md) |
| 生命周期与演化 | [修订、巩固、遗忘与恢复](04-lifecycle-and-evolution.md) | [mutation state machine 与 operator](lifecycle-evolution/01-mutation-state-machines.md) | [五种 lifecycle 实现](lifecycle-evolution/02-system-walkthroughs.md) | [派生删除、行为修复与研究前沿](lifecycle-evolution/03-deletion-repair-and-frontier.md) |
| 检索与上下文 | [从候选到可用证据](05-retrieval-and-context.md) | [query plan、过滤、召回、图导航与编译](retrieval-context/01-candidate-generation-ranking-and-navigation.md) | [六条固定版本读取链](retrieval-context/02-system-walkthroughs.md) | [LongMemEval 等基准、成本与前沿](retrieval-context/03-benchmarks-cost-and-frontier.md) |
| 使用、反馈与技能 | [从经历到行为资产](06-use-feedback-and-skills.md) | [轨迹、反思、procedure、skill 与 meta-policy](skills-use/01-experience-to-procedure-and-skill.md) | [五种工程形状与一个公开边界反例](skills-use/02-system-walkthroughs.md) | [迁移、行动、安全与最新研究](skills-use/03-transfer-safety-and-frontier.md) |

这是一条解释主线，不意味着所有系统必须实现六个独立组件。一个项目可能在多个分支出现，但每次只解剖该方向相关的数据流，不重复项目简介。[通用架构模型](../architecture.md)说明六个分支如何连接。
