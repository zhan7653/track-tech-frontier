# 人工评审清单：完整报告之后该判断什么

这份清单不是要求人重新检查所有方向。主报告、八个分支、42 篇论文深读和 10 个工程深潜已经先给出完整地图与默认判断；人工评审只负责决定哪些判断影响实际采用，或哪些专题值得继续深挖。

## 第一层：范围是否贴近实际问题

- 实际 Subagent 是一次性 tool worker、同 thread specialist、长期命名角色，还是跨机器 fleet？
- 需要共享的是代码/文档工件、当前任务状态、可争议事实，还是可复用 trajectory/skill？
- 是否存在多用户、租户、秘密、外部 side effect 或动态权限？
- 出错后只需重新回答，还是必须撤销/补偿已经执行的动作？

若只是低风险单 run 分解，structured task/result + Parent merge 可能已足够；并发主体、长期 retention、高风险行动或多租户才会让 conflict/provenance/control plane 成为优先事项。

## 第二层：确认报告中的关键判断

| 判断 | 默认结论 | 人工评审要看什么 |
|---|---|---|
| Child 是否应 full-history | 不应作为无条件默认 | 任务充分性、秘密与陈旧状态的真实比例 |
| Child 是否应长期记忆 | 按 thread/layout/project 明确绑定 | 跨任务复用收益与污染/清理责任 |
| 是否直接共享 store | 共享 primitive 不等于团队信念 | 权威对象、writer、history、conflict、scope |
| 是否需要 transaction | 只对高风险/并发 belief 有明显价值 | 错误 commit 的代价与可接受 latency |
| 是否共享 trajectory/skill | 需要 consumer/condition/negative transfer | 模型/工具版本差异和 producer trust |
| 是否需要 action gate | 召回内容不能自动授权 | 具体 side effect、当前主体与补偿路径 |

## 第三层：选择后续深挖

只有出现以下情况才继续研究某个分支：

- 报告中的默认结论与实际 runtime/config 明显不同；
- 需要比较两个候选项目的部署、API、fault behavior 或许可证；
- 某个 preprint 机制会直接改变架构决策，值得独立复现；
- 业务有报告未覆盖的 identity、scope、deletion 或 side-effect 约束；
- 90 天弱信号中出现与当前技术栈直接相关的新版本/仓库。

## 评审记录模板

```text
decision/question:
affected mechanism or project:
current report judgment:
business/runtime condition that changes it:
extra evidence or experiment needed:
owner and deadline:
reversal condition:
```

建议把评审结论写成明确的“采用/不采用/继续验证”决定，而不是给所有分支再做一次主观打分。
