# 程序性记忆工程 walkthrough：从 session、轨迹和资源到可复用行为

开源仓库很少实现同一种“技能记忆”。有的只捕获编码 session，有的把 decision→outcome 写入因果图，有的同时管理 resource、memory 和 skill，有的提供完整 agent host，有的只发布离线评估快照。下面沿形成、检索、执行和反馈边界重建五个固定版本实现。

## 1. Causal Memory：将 decision→outcome 变成可检索 lesson

固定版本 `054af36507537f7b616fa41db07be483cc6e55c3` 先将 session 写入 raw log，distill 以每 session 一次模型调用提取 fact 与 causal edge，完成后才写 done marker。读取可以从事实、因果、实体和 trace route 找候选，再做 RRF 和 spreading activation。

在程序性语义上，它保存的不是可执行函数，而是“某决策在某上下文导致某结果”的结构化经验：

```text
session log
  → decision/action + context + outcome
  → causal edge / lesson
  → similar task or entity activation
  → prompt-visible memory line
```

这种做法比自由反思保留更多 outcome relation，却仍由模型/规则决定 causal edge。弱相似产生的 meta-edge 会让错误 lesson 跨任务传播；README 也把 lesson transfer 列为限制。distill 失败时 raw log 可重试，使“捕获成功”和“技能/lesson 已形成”成为不同状态。[v10 项目工程报告](../../projects/jingxuanc--causal-memory.md)

## 2. Raven：Agent host、memory backend 和 skill forge 分离

固定版本 `14b7419245b816782b0435385d238f9f18ac090f` 的 Raven 是 terminal agent harness。AgentLoop 在 turn 前通过 `MemoryBackend` recall，在 turn 后 store/feedback；`skill_forge` 又把 memory hits、本地技能和 Hub 候选统一为 `ScoredSkill`，做 cross-source fusion/gating。

```text
turn / outcome
  → backend.store + feedback
  → later backend.recall
  ┐
  ├─ local skill files
  └─ Hub skill candidates
       → skill_forge fusion/gating → host context/action candidate
```

这一架构明确区分“持久经验后端”和“技能来源”，但真正 EverOS 抽取/搜索逻辑位于精确 pin 的依赖，不完全在 Raven commit 内。若 backend factory/import 失败，host 退化为 no-backend，Agent 仍运行；若 userId/agentId track 错配，经验存在却取不回。技能融合也不自动证明当前 effect 被授权。[v10 项目工程报告](../../projects/evermind-ai--raven.md)

## 3. OpenViking：resource、memory 和 skill 进入统一资产树

固定版本 `7f6085a2f95c8a79ec4eb82f973cae57628341a9` 把三类对象放在 `viking://` 虚拟文件系统。Session commit 归档消息，并按 schema/policy 抽取 self、peer 与 experience memory；Parser/TreeBuilder/SemanticQueue 又为资源和技能生成 L0/L1/L2 表示。读取通过 IntentAnalyzer、hierarchical retrieval 和 rerank 找到 URI，再加载具体层级。

它展示的是**统一可寻址资产面**：procedure/skill 可以与文档、经验共享层级检索和 provenance，但对象类型仍不同。异步语义队列让写入和可召回之间存在窗口；peer routing policy 错误会把经验写入错误主体空间；AGFS 与 vector index 分裂会让技能文件存在却无法发现。

仓库表面能说明资产、队列和读取如何连接，未提供足够证据证明自动生成的技能经过 sandbox、effect analysis 或生产晋升流程。[v10 项目工程报告](../../projects/volcengine--openviking.md)

## 4. claude-mem：会话观察是程序性记忆的原料，不是技能本身

固定版本 `4702c337d85aa12e8ab7f845264a78885676261f` 用 host lifecycle hooks 捕获 prompt、tool use、Stop 和 SessionEnd。Worker 将有效模型输出写为 observations/session summary，SQLite 保存权威记录，Chroma 提供语义检索；后续 session 通过 MCP 搜索、timeline 和 ID 展开获取上下文。

这条链能保存“改了哪些文件、执行过哪些工具、结果是什么”，为后续 procedure extraction 提供原料。但固定版本的主要可见工件仍是观察和摘要，不应仅因仓库有 `skills` 目录就外推为自动验证的技能供应链。Worker fail-open 时 Agent 继续而 capture 缺失；pending parser rejection 会延迟 observation materialization；SQLite/Chroma 分裂又影响后续发现。

它的价值在于展现 coding trajectory capture 与渐进披露，边界则是没有独立证明从这些轨迹形成、测试、晋升并授权执行技能。[v10 项目工程报告](../../projects/thedotmack--claude-mem.md)

## 5. Engraphis：decision、code graph、history 与 receipt 同库

固定版本 `128fe0515b842923df871a777eaacc3327f40513` 的 `MemoryEngine` 组合 store、embedding、vector、conflict/retention/graph policy。SQLite 同时保存 memory、bi-temporal history、layered graph/code link 和 hashed receipt；代码索引按 content hash 增量更新 symbol/edge。

对于 Coding Agent，这意味着一次做法可以关联 repository/session、code symbol、历史 revision 和 outcome，再由 lexical/vector/graph/code route 检索。它更接近“项目经验/决策图”，而不是完整 executable skill runtime。Prompt eligibility/review gate 会使对象存在却不进入 context，embedding fingerprint 改变则禁止 persistent vector recall。

要把这类 memory 推进为程序性技能，还需要显式 procedure schema、dependency/effect、sandbox validation 和 deprecation；当前固定版本主要证明了经验与代码结构能在统一可追踪数据面上被保存和检索。[v10 项目工程报告](../../projects/coding-dev-tools--engraphis.md)

## 6. JARVIS-1：论文系统与公开仓库边界的反例

固定版本 `aa9bd97debee045cb35b37564c71dee4c465b9ad` 是 Minecraft embodied-agent 的离线评估快照。公开的 `assets/memory.json` 是不完整 fixed memory；README 明确 multimodal descriptor/retrieval、`learning.py` 与 online growing-memory learning 未发布。`EpisodeStorage` 能保存 frames、actions、attention embeddings 和 metadata，却没有证据表明这些轨迹在该 SHA 被索引回 growing memory。

因此它展示 planner→controller→trajectory capture 的一部分，而不能用来证明完整“在线经验→技能演化”实现。这个边界很重要：论文描述、仓库目录、固定 asset 和真正运行时数据流是四种证据，不能互相替代。其 gym/mineclip/minedojo/JDK/Malmo 依赖冲突也说明具身技能复现包含环境栈，而不只是 memory 代码。[v09 固定版本报告](../../../../agent-memory-v09/bundle/projects/craftjarvis-jarvis-1.md)

## 7. 比较这些工程形状

| 系统 | 原始经验 | 派生工件 | 读取/使用 | 明确边界 |
|---|---|---|---|---|
| Causal Memory | session logs | fact、causal edge、lesson | RRF + activation 进入 prompt | 不是可执行 skill；meta-edge 可误联 |
| Raven | turn/session + feedback | backend memory + 多源 skill candidate | host context/skill forge | 依赖包承载核心逻辑；权限另算 |
| OpenViking | messages/resources | self/peer/experience memory、skill asset | hierarchical URI retrieval | 自动验证/晋升证据不足 |
| claude-mem | coding prompt/tool/session | observations、summaries | search→timeline→展开 | 原料不等于已验证技能 |
| Engraphis | memory/code/history | decision/graph/code-linked context | multi-route context pack | 缺完整 executable skill lifecycle |
| JARVIS-1 | embodied trajectory files | fixed incomplete memory | offline planner | online growing-memory 未发布 |

这组实现说明，当前开源工程更常见的是“捕获经验并使其可检索”，少数开始统一 skill asset 或融合 skill source；从多轨迹抽象程序、验证、晋升、受权执行和弃用的完整流水线仍罕见。

继续看[迁移、安全与最新研究](03-transfer-safety-and-frontier.md)。
