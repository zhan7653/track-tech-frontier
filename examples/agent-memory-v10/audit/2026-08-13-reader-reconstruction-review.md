# 2026-08-13：机制专题读者复述抽查

## 方法

本抽查不使用字数、来源数或章节数判断内容是否深入。对六个专题分别隐藏 v09 审计材料，只阅读 v10 入口和三篇深潜，尝试回答：

1. 能否画出至少一条端到端状态或数据流；
2. 能否解释三个以上方案/系统为什么实质不同；
3. 能否把失败定位到具体阶段，而不是笼统说“效果不好”；
4. 能否说清近期研究改的是哪一层，以及现有实验为什么还不足；
5. 是否被迫依赖内部 claim/cluster ID、仓库目录清单或人工审批。

## 抽查结果

### 对象与作用域：通过

可复述链路为 `event/receipt → canonical revisioned object → FTS/vector/graph/summary projection → scoped read/action`。可区分事件、事实/画像、关系/世界/项目、程序/技能和共享/控制对象；可解释 actor/subject/owner/principal/tenant 与 occurred/valid/recorded/processed time。MineEcho 的应用内多层状态、OpenViking 的 URI/tree、Letta V1 的 core/archive、Mem0 的 fact/history/entity、Sibyl 的 tenant SQLite、OMP 的 schema/reference behavior 不再是同形项目简介。

仍有边界：共享对象的并发、撤销和跨实现 round-trip 主要是问题定义与局部实现，没有独立完整 conformance。

### 写入与形成：通过

可复述链路为 `capture → segment/group → typed proposal → related-old retrieval → ADD/MERGE/SUPERSEDE/CONFLICT → admission → canonical commit → projection`。可解释 raw retain、summary/reflection、typed extraction、transaction admission 和 learned control 把成本与错误移到哪里；能从 Mem0、journal-first、causal distill、hierarchical semantic queue 和 MemoryEngine 的不同失败位置区分系统。

LightMem reproduction 和 budgeted consolidation 已进入结论边界，读者不会得到“越结构化越好”的错误印象。

### 表示、存储与索引：通过

可复述权威 evidence/current-history 与派生 FTS/vector/graph/cache 的不对称关系；能说明 BM25、HNSW、IVF、RRF、PPR、双时间和层级 URI 的内部作用。工程 walkthrough 覆盖 single SQLite、WAL/segment、AGFS+metadata、Postgres/pgvector、encrypted RAM vault 和多索引 engine；revision、fingerprint、watermark 三者的区别可用于解释迁移与恢复。

仍有边界：仓库均未在本轮执行，跨后端事务和故障恢复属于机制/静态工程分析，未被共同运行协议证明。

### 生命周期与演化：通过（经第二次加厚）

可复述对象从 captured/proposed/quarantined/admitted 到 active/conflicted/superseded/consolidated/hidden/purged/restored 的状态机；可区分 amend、merge、supersede、conflict、TTL、decay、release、revoke 和 purge。固定版本层能跟踪 promotion/outbox、bi-temporal policy、LLM mutation/history、FTS rebuild、encrypted journal/model-hash。派生修复页给出 typed dependency closure、watermark、故障矩阵和删除收据。

STALE、MemCon、MemTxn、ForgetEval 与 budgeted consolidation 分别约束 behavior adaptation、policy、transaction、placement 和 operator ranking，未被压成“最新工作很多”。

### 检索与上下文：通过

可复述 `query plan → pre-filter → lexical/dense/entity/graph candidates → canonical dedup → RRF/rerank/navigation → evidence compiler → answer/tool action`。能说明 HNSW/IVF、RRF/PPR、active loop 与 MMR/context compilation 的不同职责；能沿 Causal Memory、OpenViking、Engraphis、Mem0、claude-mem 和 Raven 的固定版本读取链定位 backend、identity、queue、fingerprint 和 progressive disclosure 故障。

LongMemEval S/M/Oracle、MemoryAgentBench、Mem2ActBench 与 STALE 保留不同任务单位；LightMem 复现说明 retriever/depth/token budget 会反转表面结论。

### 使用、反馈与技能：通过

可复述 `trajectory → segmentation/credit → reflection/procedure/skill candidate → replay/sandbox/promotion → applicability filtering → composition/authorization → execution/outcome → revision/deprecation`。Reflexion、Voyager、MemP、MemSkill、XSkill 不再只是论文名，而是不同持久工件与控制层；工程页区分 causal lesson、host/backend/skill forge、统一资产、coding observations 和公开 snapshot 边界。

Mem2ActBench、AFTER、PoisonedEvolution 与 STALE 把长期约束、迁移、晋升攻击和 behavior repair 接到同一供应链。仍缺的是同一轨迹、工具版本和预算下对 trajectory/reflection/procedure/code skill/meta-policy 的独立对照。

## 跨专题问题

- 入口页仍有一定内容重复，但现在承担的是可独立阅读地图；深潜页按机制、工程和前沿分工，不再重复论文/仓库简介。
- 读者正文没有内部 claim/synthesis/cluster marker；固定版本边界用自然语言表达。
- 18 篇深潜并非固定模板：对象分支将身份/时间视为独立核心；其他分支把第三篇用于反证、成本和研究前沿。结构相似用于导航，不代表每篇内容等量。
- 用户不要求选型建议，正文保持描述性，没有路线排名或默认实施架构。

## 仍未关闭的研究空白

1. 同一 backend、模型、历史和预算下，raw/typed/graph/active/skill 等路线的跨层对照；
2. 跨多存储与多 writer 的 transaction、recovery、late evidence 和 conflict；
3. 从 revoke/purge 到 summary/vector/cache/backup/skill/action 的完整修复；
4. 共享/可移植 Memory 的独立当前版本 conformance 与生产采用；
5. 从恶意写入到真实授权 action，再到 incident repair 的完整安全实验；
6. formation、maintenance、retrieval、action 和人工 review 的长期总成本。

这些空白已经在相应分支被解释为“为什么不知道、限制什么判断、需要什么实验”，没有被留给人工评审补写。
