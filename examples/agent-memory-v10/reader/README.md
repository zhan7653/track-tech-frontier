# Agent Memory：读者入口

Agent Memory 研究的是：一个会跨会话、跨任务或跨执行环境行动的 Agent，怎样把过去变成可管理、可检索、可纠正且受权限约束的状态。它不等同于把聊天记录塞进向量库；真正的难题还包括该写什么、何时更新或忘记、怎样解决新旧冲突、怎样在有限上下文中取回证据，以及怎样让行动不越过状态和权限边界。

## 按时间阅读

### 5 分钟：建立地图

阅读[领域总览](overview.md)：Memory 要解决的现实问题、通用链路、主要路线，以及最近一年和最近 90 天正在变化什么。

读完应能复述：Memory 不是单一数据库；它是一条从经验进入状态、再从状态影响行动的受控链路。

### 15 分钟：看懂系统怎样运转

在总览之后阅读[通用架构模型](architecture.md)：写入、管理、存储、检索、使用、反馈与横切控制如何连接，以及不同系统会在哪些位置替换或省略模块。

### 30 分钟：理解路线和变化

在 15 分钟路径之后，阅读：

1. [方案全景](solution-landscape.md)：各主要方案家族解决的不同问题及其代价。
2. [近期变化](trends.md)：最近 12 个月与 90 天信号在既有脉络中的位置。
3. [场景视图](scenarios.md)：个人助手、Coding Agent、多 Agent 与世界状态如何组合或省略模块。
4. [共识、争议与未解问题](consensus-and-open-questions.md)：哪些结论稳固，哪些仍缺可比证据。

### 专题阅读：从问题出发

| 如果你想弄清…… | 从这里读起 |
|---|---|
| 状态是什么、归谁、何时有效 | [记忆对象与作用域](mechanisms/01-memory-objects-and-scope.md) |
| 怎样从事件形成可用记忆，并修正或遗忘 | [写入与形成](mechanisms/02-write-and-formation.md) 与 [生命周期与演化](mechanisms/04-lifecycle-and-evolution.md) |
| 怎样保存、索引、检索并编译为工作上下文 | [表示、存储与索引](mechanisms/03-representation-storage-indexing.md) 与 [检索与上下文](mechanisms/05-retrieval-and-context.md) |
| 怎样把经验变成程序、技能或项目连续性 | [使用、反馈与技能](mechanisms/06-use-feedback-and-skills.md) |
| 六个方向的算法、固定版本工程和研究前沿分别在哪 | [技术机制深潜索引](mechanisms/README.md) |
| 多主体、世界状态或可移植共享状态 | [多 Agent 共享 Memory](scenarios/03-multi-agent-shared-memory.md)、[世界状态与具身](scenarios/04-world-state-embodied-multimodal.md)及[互操作专题](cross-cutting/04-interoperability-and-integration.md) |
| 评测是否真的测到了 Memory，或安全成本如何影响链路 | [横切议题](cross-cutting/README.md) |
| 一个具体 GitHub 项目代码实际上怎样运转 | [重点工程案例](projects/README.md)；当前 Codex 见 [Codex 本地 Memory 系统](projects/openai--codex.md) |

每个专题都应可独立阅读：先给场景和问题，再解释方案族与机制，最后说明工程实现、比较、失败模式、成熟度和仍不确定之处。没有页面需要读者理解 v09 的 cluster ID、claim ID 或研究流程。

## 这不是选型手册

本报告解释不同路线在什么条件下成立、会付出什么代价、证据有多强；它不说“应该选哪一种”。场景页展示的是已有系统如何组合或裁剪模块，不是推荐参考实现。完整边界见 [方法与范围](method-and-scope.md)。

## 证据与版本

本读者层由 v09 材料重编；[v09](../../agent-memory-v09/README.md) 仍是冻结于 2026-08-10 的主要证据、输入审计和可追溯账本所在地。2026-08-12 的窄幅机制补查增加三项论文；2026-08-23 的第二个定向增量只深查 `openai/codex` 的本地 Memory 源码、官方文档和当前 issues。具体查询和来源见[v10 审计入口](../audit/README.md)。因此，正文不能被理解为对所有 2026-08-10 之后仓库、发布、标准或采用状态的全面更新。

需要核对范围与证据边界时，读 [方法与范围](method-and-scope.md)；内部分类映射已下沉到[审计目录](../audit/old-to-new-map.md)。只有少量足以改变重点或判断的事项进入 [人工评审](human-review.md)，且评审不是阅读本套件的前置条件。
