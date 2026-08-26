# 方案全景兼容入口

本套件按六层实现组织方案，不按产品名称或数据库品牌组织。

## 全领域的方案坐标

| 位置 | TencentDB / Codex 的工程形状 | 具体前沿变化 |
|---|---|---|
| 输入 | Chat/Skill/Wiki/CodeGraph；Thread/rollout | 视觉、世界/设备状态、Computer Use 事件 |
| 形成 | L1–L3/Skill；Phase 1/2 | source-supported admission |
| 状态 | JSONL/DB/Markdown/FTS/vector/graph；SQLite/Markdown/Git | 双时间版本图 |
| 管理 | 对象/文件更新、合并和版本 | MemTxn、GEM/MemState、ForgetEval |
| 读取 | 分层注入与工具；summary + 词法下钻 | MemFlow、OpenViking、CICL |
| 反馈 | Skill version；citation usage | 多轨迹 Skill、Verifier、operation policy、Memory-design search |

详细解释见[总览](overview.md)和六层功能正文。

## 工程实现的四种外形

本套件重点展示两种组合：TencentDB 的显式对象层级与多资产工具路径，以及 Codex 的候选数据库、Markdown 工作区和词法渐进读取。完整 Codex 组件见[Codex 完整说明](codex-complete.md)。

## 当前主流和新方向怎样区分

已有固定代码路径的能力写作工程实现；近期论文和原型写作研究方向，并标明协议、代码和采用证据边界。
