# Subagent Memory 方案空间

方案差异首先来自**状态拓扑和提交权**，而不是向量库或图数据库的选择。

## 全领域的方案坐标

可以用四条轴定位一个方案：Child 看到全历史还是受控视图；状态是 Child 私有还是团队共享；写入立即生效还是先候选/提交；长期经验集中保存还是分散在 Agent population。下表把常见组合放在同一坐标中。

| 方案族 | Parent → Child | Child → Team | 并发/冲突 | 适用条件 | 典型失败 |
|---|---|---|---|---|---|
| 全历史继承 | 复制 transcript 或 session | 返回文本并继续同一历史 | 通常由 orchestration 顺序隐式处理 | 单 run、低并发、主体边界简单 | 秘密和攻击载荷继承、上下文膨胀、旧状态传播 |
| 结构化 handoff packet | 筛选目标、约束、工件和已知状态 | 结构化结果或 handoff 文件 | Parent 串行合并 | 明确 manager-specialist 关系 | 压缩遗漏、Parent 瓶颈、跨 sibling 发现弱 |
| 命名 Subagent 局部记忆 | 按 invocation/thread/project/user 加载自身状态 | 更新自身 memory/checkpoint，未必发布团队 | 依赖 namespace 与 writer policy | 重复调用同一角色、长期 specialist | 跨任务污染、同名并发、残留状态、删除不完全 |
| 共享 blackboard/workspace | 所有 Agent 读取共同状态或文件 | 直接写、patch 或发布工件 | 需要版本、锁、schema 或角色规则 | 协作对象结构明确、需要任务中同步 | last-write-wins、污染、非确定重放 |
| 集中式 shared memory service | 按 scope 检索或订阅 | API 写入候选/记录 | 中央控制面处理版本、冲突和策略 | 跨机器、跨框架、fleet 或多租户 | 控制面复杂、能力漂移、共享面过宽 |
| 去中心化/Transactive Memory | Child 保留私有状态，通过目录发现他人知识 | 发布轨迹、索引或能力摘要 | 消费者选择和局部更新 | Agent 异构、隐私或多样性重要 | 目录陈旧、信任传递、重复与全局一致性弱 |
| Transactional belief state | 读取 snapshot 与已提交信念 | stage → validate → commit/reject | 显式 transaction、conflict 和 repair | 写入会驱动高风险行动 | 延迟和实现成本、validator 自身错误 |

这些方案可以组合。一个系统可以使用 handoff packet 启动隔离 Child，用 shared workspace 交换工件，再把最终事实写入 governed service；也可以让 Agent 私有保留完整轨迹，只向 transactive index 发布可检索摘要。

## 工程实现的四种外形

工程上最常见的是四种外形：runtime 内的 history/state/checkpoint；共享 workspace/backend；独立 memory service；population trajectory/skill index。Codex、LangGraph/Deep Agents、Caura/memX、MATM 分别提供了固定版本对照。它们可以组合，但身份、snapshot 和 commit 语义需要显式 adapter。

## 当前主流和新方向怎样区分

主流是 Parent 编排、消息/ToolMessage 回流、shared file/backend、thread checkpoint 和应用自定义 namespace。正在进入工程的是 layout/project memory、多租户 scope、background consolidation、contradiction/lifecycle。较新的研究方向是 conflict-preserving contract、belief transaction、派生权限、negative-transfer-aware experience 和 risk-gated action；“新”不等于成熟或更适合低风险任务。

## 方案的真正比较轴

- **权威性：** 任意 Agent 写入是否立即可行动，还是先成为候选？
- **视图构造：** Child 看到全历史、摘要、任务包、共享 workspace 还是按权限检索的 evidence packet？
- **同步：** snapshot、轮询、通知、事件流还是同步共享对象？
- **冲突语义：** 覆盖、保留多版本、显式 conflict set、裁决或 transaction abort？
- **来源：** 能否追溯到 Agent、任务、工具、输入、时间与派生链？
- **退出语义：** Child 销毁后，scratch、工件、失败和经验分别怎样处理？
- **行动耦合：** 召回内容是否需要在当前权限和风险下重新验证？

后续分支报告不会给出统一赢家，而会说明这些轴在什么条件下改变成本、正确性和失败形态。
