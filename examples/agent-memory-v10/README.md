# Agent Memory frontier research — v10

**证据截止：2026-08-10｜读者版完成：2026-08-12**

v10 把 v09 的广泛语料、证据账本和工程检查转化为一套面向技术负责人和架构师的阅读套件。它首先回答 Agent Memory 在解决什么、一个系统通常怎样运转、主要技术路线如何相互关联，以及哪里仍然不确定；论文、仓库和审计记录用于支撑这些解释，而不是成为阅读入口。

v10 是对 [v09](../agent-memory-v09/README.md) 的**重编与定向补查框架**，不是一次从零开始的同规模重新发现。这个初始读者套件尚未新增可复放的定向补查记录；除非后续页面明确标出并链接新证据，近期状态、版本和工程事实仍以 v09 在 2026-08-10 冻结的证据为限。v09 完整保留，既不被覆盖，也不被改称为 v10。

## 从哪里开始

- **5 分钟：** 阅读 [读者入口](reader/README.md) 与 [领域总览](reader/overview.md)。目标是建立问题、对象、通用架构模型和主要路线的心智图。
- **30 分钟：** 接着阅读 [通用架构模型](reader/architecture.md)、[方案全景](reader/solution-landscape.md)、[近期变化](reader/trends.md) 与 [场景视图](reader/scenarios.md)。目标是看清模块如何组合、哪些路线在变化，以及场景怎样裁剪而不构成推荐。
- **专题阅读：** 从 [技术机制](reader/mechanisms/)、[重点工程案例](reader/projects/) 或 [横切议题](reader/cross-cutting/) 进入。每个专题独立说明问题、方案族、机制、比较、失败模式、证据状态与未解问题。

## 套件结构

```text
reader/                 面向读者的总览、专题、场景和工程案例
reader/mechanisms/README.md      技术机制主分支
reader/scenarios.md              跨分支的应用场景总表
reader/scenarios/README.md       四个场景专题
reader/projects/README.md        少量重点 GitHub 仓库工程案例
reader/cross-cutting/README.md   评测、安全、成本、互操作等横切问题
reader/human-review.md  少量可选的高影响人工评审事项
reader/method-and-scope.md  证据、范围与写作边界
reader/old-to-new-map.md    v10 结构与 v09 C01–C16 的映射
audit/README.md             冻结证据与账本的审计入口

../agent-memory-v09/    保留的研究底稿、账本、原始读者报告与审计材料
```

读者层只保留自然语言解释、简洁引用和必要的不确定性说明。可追溯的来源、atomic claims、evidence joins、筛选、饱和记录与验证材料通过 [v10 审计入口](audit/README.md)连接到 v09 的冻结权威；后续定向补查才在 v10 审计层追加 delta。它们都不构成阅读前提。

## 读者契约

本套件提供描述性技术分析：问题边界、方案机制、成立条件、成熟度、代价、失败模式、共识、争议与弱信号。它**不**提供技术选型建议、推荐组合、统一排行榜、默认架构或上线清单。这里的“通用架构模型”是对现有系统常见模块和数据流的解剖，不是推荐实施方案。

若需复核 v10 的重组来源和已知边界，请读 [方法与范围](reader/method-and-scope.md) 及 [v09→v10 映射](reader/old-to-new-map.md)；仅当某一判断会实质改变阅读结论时，才进入 [人工评审](reader/human-review.md)。
