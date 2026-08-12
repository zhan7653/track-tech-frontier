# 2026-08-13：六个机制专题的输入吸收复核

## 复核目的

本轮不是检查“论文或仓库名字有没有出现”，而是检查 v09 的主干输入是否改变了 v10 的解释。一次材料只有满足以下至少一项才算被吸收：

1. 解释一种对象、状态结构或算法步骤；
2. 重建一个固定版本系统的组件关系与数据流；
3. 提供实验条件、数字或协议边界；
4. 形成反证，限制某条强结论；
5. 改变当前研究议程或尚未解决问题的表达。

仅出现在项目表、论文清单或“代表工作包括……”句子中，不计为吸收。4,407 个去重实体用于广度地图，不会全部倾倒进读者正文；本复核重点覆盖 v09 的 73 篇论文深度卡、86 个仓库卡中被选为机制锚点的部分、16 个固定版本工程 profile，以及会改变结论的 benchmark/negative evidence。

## 复核结果概览

| 分支 | 主干输入怎样改变正文 | 固定版本工程怎样进入正文 | 反证/实验怎样限制结论 | 结果 |
|---|---|---|---|---|
| 对象与作用域 | evidence/canonical/projection 三层；事件、事实、关系、程序、共享和控制对象；双时间与 revision | MineEcho、OpenViking、Letta V1、Mem0、Sibyl、OMP 按对象/作用域/投影重建 | 双时间小样本下降、STALE、schema≠behavior、共享撤销与 conformance 缺口 | 已吸收 |
| 写入与形成 | capture→segment→extract→old-state lookup→mutation→admission→projection；raw/summary/typed/learned 五路线 | Mem0、scope-recall-hermes、Causal Memory、OpenViking、Engraphis 按真实写入链重建 | LightMem 独立复现、budget-dependent consolidation、formation cost、poisoned promotion | 已吸收 |
| 表示、存储与索引 | authoritative state 与派生索引；SQL/WAL/FTS/ANN/graph/bitemporal/tree；revision/fingerprint/watermark | Sibyl、xerj、Causal Memory、OpenViking、Engraphis、Compartment、AtomicMemory | raw baseline、post-filter dilution、dual-write/migration/delete/restore 故障矩阵 | 已吸收 |
| 生命周期与演化 | mutation state machine；amend/merge/supersede/conflict；TTL/decay；journal/recovery；learned policy | scope-recall-hermes、Engraphis、Mem0、Sibyl、Compartment 按 promotion、history、repair、journal 和密钥边界重建 | STALE 400/1,200/55.2%、ForgetEval placement、budgeted operator、PoisonedEvolution、MemSecBench | 已吸收 |
| 检索与上下文 | query plan→hard filter→BM25/ANN/graph→fusion/rerank→active loop→compiler；candidate 与 compiled budget 分离 | Causal Memory、OpenViking、Engraphis、Mem0、claude-mem、Raven 按读取链重建 | LongMemEval S/M/Oracle、MemoryAgentBench 能力拆分、Mem2Act 行动、LightMem 58.1→75.5 反证 | 已吸收 |
| 使用、反馈与技能 | trajectory→reflection→procedure→executable skill→meta-policy；形成、晋升、适用性、组合、执行、反馈 | Causal Memory、Raven、OpenViking、claude-mem、Engraphis；JARVIS-1 作为公开实现边界 | Mem2Act 2,029/400、AFTER 382/6/22、PoisonedEvolution 两流水线、STALE 行为失效 | 已吸收 |

## 逐分支复核说明

### 对象与作用域

- Generative Agents 与 MemoryBank 不再只作为历史名称：它们用于解释原始事件、派生反思/画像和后续行为使用为什么是不同层。
- AtomMem、A-MEM、AriGraph 分别落到原子粒度、动态链接和带世界状态的关系对象；GEM/MemState 用于区分 association 与 derivation/extension。
- 双时间工作进入 valid/recorded/processed time 与 as-of resolver；其负面结果用于说明“模型更清楚”不等于访问算法更准。
- 六个工程系统按对象、作用域、权威层和投影比较，而不是逐项目介绍功能。

### 写入与形成

- Generative Agents、MemoryBank、A-MEM、Hindsight、SimpleMem 分别解释 reflection、对象并存、动态链接、分层对象和多视图形成。
- MemTxn 将模型 proposal 与 source-supported commit 分开；MemCon 将 operation selection 变成在线 policy，同时保留受限提交边界。
- 固定版本系统被放在同一形成链上比较：旧候选如何参与 mutation、原始日志是否保留、promotion 在哪里发生、投影如何失败。
- LightMem reproduction 与 budgeted consolidation 直接否定“越结构化越好”或“固定 operator 最优”的强结论。

### 表示、存储与索引

- BM25、HNSW、IVF、RRF、PPR/spreading activation 和双时间索引都有算法步骤与适用信号，不再只是术语。
- 七个工程 profile 用于展示 single-DB、WAL/segment、AGFS+URI、Postgres/pgvector、encrypted journal 和多索引组合的不同 source-of-truth。
- revision、embedding/schema fingerprint 与 projection watermark 被明确区分，用来解释迁移和恢复。
- LightMem 与双时间小样本的负面结果限制了复杂表示的普遍收益；故障矩阵覆盖 partial commit、model migration、backup resurrection 和 scope loss。

### 生命周期与演化

- MemoryBank 的 updater 只作为显式 lifecycle 起点，不外推 transaction/delete/recovery。
- Retain or Consolidate、MemCon、MemTxn 和 ForgetEval 分别改变 operator/budget、learned selection、transaction 和 control-plane placement 的问题定义。
- 五个固定版本 walkthrough 补入 promotion/outbox、bi-temporal policy、LLM fact mutation、多存储 history、FTS rebuild、model-hash 和 AEAD journal 细节。
- STALE 将完成条件从 store correctness 推到 tool/action；删除被拆为 suppression、tombstone/revoke、projection removal、physical purge 和 behavioral repair。

### 检索与上下文

- 读取被拆成 query plan、合法集合、候选 route、融合、导航、编译和行动使用；各阶段保留独立 trace。
- 六个固定版本实现被放回同一读取链，暴露 RRF、层级 URI hydration、hard token budget、provider capability、渐进披露和 backend/identity fallback。
- LongMemEval 的 S/M 与 Oracle 含义被精确区分；MemoryAgentBench、Mem2ActBench、MemoryArena 和 STALE 保留不同任务单位。
- LightMem reproduction 证明 retriever 与 depth 足以反转表面结论，因而形成、召回和 compiled token 必须匹配。

### 使用、反馈与技能

- Reflexion、Voyager、MemP、MemSkill 与 XSkill 分别锚定 reflection、代码技能、分层程序、meta-memory policy 和多模态双层经验，不再混为“技能库”。
- 工程 walkthrough 明确区分 trajectory capture、causal lesson、统一 skill asset、skill-source fusion 和真正 executable runtime；JARVIS-1 用于说明论文系统与公开 snapshot 的实现边界。
- AFTER 的迁移维度、Mem2Act 的工具参数、PoisonedEvolution 的 inclusion/promotion 风险和 STALE 的 behavior adaptation 被串成 evidence→artifact→retrieval→execution 链。

## 有意未进入读者正文的输入

下列材料仍保留在 v09 地图与账本，但不进入深潜正文：

- 只有标题、摘要或 GitHub metadata，尚不足以解释内部机制的长尾候选；
- 普通 Agent 框架中只有一个 memory feature、却没有独立状态合同的项目；
- 与主体无关的普通 RAG、数据库、缓存或 allocator；
- README 自报排名、单次 stars、未固定依赖、没有协议指纹的性能数字；
- 与已解释机制同形、且没有增加新状态、反证或工程边界的项目。

这些排除避免把广度输入重新变成项目清单。若某个长尾材料后来提供独立复现、新 primitive、反转结果或完整固定版本工程路径，再由增量研究把它升级到专题层。

## 本轮仍保留的证据边界

- v09 没有执行第三方仓库，工程 walkthrough 是固定版本静态重建，不是安装/性能/恢复证明。
- 多数 2026 新工作是作者预印本或作者协议；独立复现集中在少数反证，不能形成统一排行榜。
- 当前仍缺同一 backend、模型、历史、候选/context/tool 预算下的跨路线实验。
- 完整派生删除、跨租户共享、并发恢复、程序晋升与真实 action harm 的端到端公开证据仍薄。

复核结果说明输入已经转化为机制、工程和反证三个层次；它不说明这些方向已经成熟，也不替代后续独立读者检查。
