# 共识、争议与未解决问题

## 相对稳固的共识

- Agent Memory 的主要经验输入是带顺序的 user/assistant/tool call/tool result 轨迹，并需要 thread/task/time/project 等定位；文档、代码、视觉和设备状态是特定系统的补充输入。
- 原始证据、抽取候选、当前权威正文和派生索引应分开。TencentDB 的 JSONL/DB/Markdown/索引与 Codex 的 rollout/SQLite/Markdown/Git 都体现了这一点。
- 写入模型的输出不应天然等于真相。MemTxn 把 proposal、source-supported admission、版本选择和恢复拆开，是当前明确的研究方向。
- “内容进入上下文”必须按 Memory 类型说明：直接注入、索引导航、工具检索或来源下钻；后端 BM25/vector/graph 只是具体路径的一部分。
- citation 或使用次数只能证明可能被采用，不能证明任务结果改善。持续学习需要把 exposure、adoption、outcome、correction 和 cost 分开。

## 仍有分歧的机制

- TencentDB 的显式 L1/L2/L3/Skill 对象与 Codex 的文件级全局重写，分别移动了对象管理、可读性和语义合并成本；现有材料不足以给出统一优胜排序。
- current/history 是否应以稳定 item identity 和双时间版本表达，还是保留原始 rollout 后由文件重写处理，取决于历史查询、冲突与恢复要求。
- 检索可以由 Agent 自主使用文件工具，也可以由 MemFlow/OpenViking 这类显式 router/层级协议组织；CICL 又把选择目标从相似度改成下一步行动影响。它们尚缺同 store、同模型、同预算的全面对照。
- Skill 可以从多路径对照、并行 patch、Generator–Verifier、hard cases 或元架构搜索形成；不同方法学习的是 Experience、业务 Skill、memory operation 或整个 Memory design，不能用一个“自进化”总分替代。

## 尚未解决的问题

- TencentDB 的层级触发和 Codex 的 Phase 2 重写都没有完整显式 lineage；上游 revision 后，哪些 Scene、Persona、summary、Skill 和索引必须重算仍可能依赖生成式判断。
- 两套固定仓库都能局部移除 current 内容，却没有将 semantic forgetting 建模为统一的 supersede/release/purge、派生修复和再生成控制。
- Codex 的全局物理 Memory root 与 TencentDB 的多资产路径都要求良好的 scope 表达；跨 project、branch、version 的适用条件仍可能在抽取或文件合并中丢失。
- XSkill、Trace2Skill、CoEvoSkills、MemSkill、MemCon 与 ALMA 分别展示了反馈循环，但长期在线任务分布变化、延迟反馈和多次自我更新后的稳定性仍缺统一协议。
- Causal Memory 可以记录 decision→outcome，Omri 可以分阶段计量成本；把 Memory object、上下文片段、实际工具参数、任务结果和下一次 revision 连成一条可复现实验 trace，仍是持续评测的核心空白。

具体机制与证据见[六层总览](overview.md)及[第 4 层](04-management-evolution.md)、[第 5 层](05-retrieval-context.md)、[第 6 层](06-feedback-learning.md)。
