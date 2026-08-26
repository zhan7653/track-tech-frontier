# 六层实现地图

六层链路把真实输入、首次形成、持久状态、后续管理、当前读取和结果反馈分开。TencentDB 与 Codex 是工程锚点；每个前沿案例只出现在它实际改变的层。

| 层 | TencentDB | Codex | 前沿案例 | 入口 |
|---|---|---|---|---|
| 1 输入 | Chat、Skill、Wiki、CodeGraph | Thread/rollout + 项目元数据 | 视觉观察、WorldLines、Computer History | [01](../01-input.md) |
| 2 写入与形成 | L0→L1→L2→L3；Skill Review | Phase 1 → Phase 2 | MemTxn admission | [02](../02-write-formation.md) |
| 3 状态、存储与索引 | JSONL/Markdown/DB/FTS/vector/graph | rollout/state/memories DB/Markdown/Git | 双时间版本图 | [03](../03-state-storage-indexing.md) |
| 4 管理与演化 | L1/L2/L3/Skill update/version | Phase 2 文件级重写 | MemTxn、GEM/MemState、ForgetEval | [04](../04-management-evolution.md) |
| 5 读取与上下文 | L3 直注；L2/L1/L0/Skill/Knowledge 分路径读取 | summary 直注；词法 search/read；来源下钻 | MemFlow、OpenViking、CICL | [05](../05-retrieval-context.md) |
| 6 反馈与学习 | 轨迹 Review→Skill version | citation→usage→selection | XSkill、Trace2Skill、CoEvoSkills、MemSkill、MemCon、AFTER、ALMA、Causal Memory/Omri | [06](../06-feedback-learning.md) |

主循环为：

```text
input → formation → persistent state
                     ↕ management
                  retrieval/context → feedback/learning
                         ↑                    │
                         └──── 新对象/策略 ──┘
```
