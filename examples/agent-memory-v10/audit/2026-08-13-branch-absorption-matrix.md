# 2026-08-13：六个机制分支的输入吸收矩阵

## 为什么需要这张矩阵

v09 已形成一套很大的研究输入：4,407 个去重实体、73 篇深论文卡、86 个仓库卡、385 个实际打开来源、373 条已发布结论、14 个机制簇深度报告和 16 个固定版本工程剖面。v10 第一阶段虽然把总览改成了读者结构，但六个机制分支对这些材料压缩过度；许多重要路线只被点名，部分工程剖面完全没有进入自然语言解释。

本矩阵用于约束第二阶段重编。它不是“每个名字都必须出现在正文”的配额，而是区分三种用途：

- **主干材料**：改变分支分类、机制解释或前沿判断，必须进入对应深潜；
- **代表实例**：用来解剖一种具体算法或工程形状，选择性详写；
- **边界/反证**：限制普遍性、暴露失败或说明评测不可比，必须在相关判断附近出现；
- **长尾地图**：只用于证明广度或提供后续线索，不应倾倒进读者正文。

## 六分支吸收计划

| 读者分支 | 必须吸收的 v09 深度簇 | 主干论文/机制 | 固定版本工程实例 | 关键反证与评测 | 第二阶段专题页 |
|---|---|---|---|---|---|
| 对象与作用域 | C03、C08、C10、C11、C14；横切 C12 | Generative Agents、MemoryBank、AtomMem、A-MEM、AriGraph、bitemporal store、GEM/MemState | MineEcho、OpenViking、Letta V1、Mem0、Sibyl、Open Memory Protocol | STALE、身份/时间漂移、共享状态撤销、对象粒度错误 | 对象模型；身份/时间/共享语义；系统与前沿 |
| 写入与形成 | C01、C05、C08、C12、C14 | observation/reflection、fact extraction、typed mutation、MemTxn、MemCon、Hindsight、SimpleMem | Mem0、Causal Memory、scope-recall-hermes、OpenViking、Engraphis | write poisoning、摘要信息损失、construction cost、来源支持不足 | 形成算法；系统 walkthrough；失败与研究前沿 |
| 表示、存储与索引 | C01、C02、C03、C07；关联 C09/C11 | raw/typed state、BM25/ANN/hybrid、graph、bitemporal、multi-tier、trajectory database | Sibyl、xerj、Causal Memory、OpenViking、Engraphis、AtomicMemory、Compartment | LightMem 独立复现、dual-write 漂移、embedding/schema migration、恢复缺口 | 底座与索引；工程 walkthrough；一致性/成本前沿 |
| 生命周期与演化 | C01、C05、C08、C12 | update/supersede/merge、consolidation、forget/release/purge、journal/recovery、learned control | scope-recall-hermes、Engraphis、Mem0、Sibyl、Compartment | Retain or Consolidate、ForgetEval、STALE、派生物删除、策略误操作 | 操作与状态机；系统 walkthrough；修复与研究前沿 |
| 检索与上下文 | C03、C04、C07、C13 | lexical/vector/hybrid、PPR/graph navigation、temporal filtering、active retrieval、context compilation | Causal Memory、OpenViking、Engraphis、Mem0、claude-mem、Raven | LongMemEval、MemoryAgentBench、LightMem 复现、candidate/compiled budget 混杂 | 检索算法；系统 walkthrough；评测/成本前沿 |
| 使用、反馈与技能 | C06、C09、C10、C12、C13 | Reflexion、Voyager、trajectory distillation、MemSkill、XSkill、AFTER、meta-memory policy | Causal Memory、Raven、claude-mem、OpenViking、Engraphis | Mem2ActBench、PoisonedEvolution、STALE、错误经验自强化与迁移失败 | 经验到技能；系统 walkthrough；安全/迁移前沿 |

## 代表性并不等于全收录

每个专题采用“机制锚点 + 工程锚点 + 反证锚点”的组合。论文用于解释算法、实验与概念边界；仓库用于解释固定版本中的组件、依赖、数据流和失败表面；benchmark 和负面证据用于限制结论。一个项目同时出现在多个分支时，只解释该分支真正关心的部分，不重复完整项目简介。

下列材料默认不进入六分支正文：仅有 metadata 的长尾候选、普通 Agent 框架的一项 memory feature、无法核验的 README 排名、单次 stars 快照、与核心生命周期无关的普通 RAG/数据库/上下文缓存，以及没有改变当前机制分类的同形项目。它们继续保留在 v09 地图与 GitHub 雷达中。

## 三轮产出与验收

1. **Round A — 机制展开**：为六个分支分别建立方案内部、代表系统、前沿与反证三篇深潜；把 state、algorithm、data flow 和 control decision 写清。
2. **Round B — 输入回填**：逐项检查本矩阵的主干论文、工程剖面和反证是否真正影响文字，而非只出现名字；补实验条件、版本边界和失败链。
3. **Round C — 读者编辑**：重写六篇入口，去掉重复、审计语言和堆名词；让读者可以从短地图逐层进入细节。

完成不能由新增文件数或字节数证明。最终逐篇回答三个问题：读者能否画出至少几种方案的内部数据流；能否解释代表系统为什么实质不同；能否说出近期研究正在改哪一个机制以及什么证据仍缺失。
