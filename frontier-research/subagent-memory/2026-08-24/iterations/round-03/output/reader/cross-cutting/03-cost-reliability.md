# 成本、可靠性与可观测性

Subagent Memory 的成本包括 Parent 构造任务包、Child 冗余探索、共享写入、索引、通知、冲突裁决、critic、压缩、权限检查、重放和恢复。并行可降低墙钟时间，却可能增加总 token、重复检索和 merge 成本。

可靠性需要记录 agent/run/task、base version、读写集合、工具结果、提交状态和 downstream consumer。没有这些 trace，系统无法判断失败来自 Child 输入不足、共享状态陈旧、冲突被覆盖、检索漏召回，还是正确记忆被错误行动使用。
