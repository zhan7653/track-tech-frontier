# Subagent Memory Benchmark 协议地图

没有一个“Memory 分数”能覆盖继承、局部持久化、共享、冲突、回流、经验迁移和行动。下表只说明协议在测什么，不进行跨组排名。

| 协议 | Agent/主体结构 | 输入与任务 | Memory 干预 | 主要指标 | 不能直接推出 |
|---|---|---|---|---|---|
| GateMem | 多主体 shared assistant | 91 个长 episode、2,218 checkpoints，四领域 | authorized/unauthorized/deleted facts | utility、access control、active forgetting | 底层物理删除、task Subagent 协作效率 |
| GroupMemBench | 多方群聊 + user-bound query | threaded、speaker/persona/audience，六类问题 | 现有 memory ingestion/retrieval | accuracy、cost、storage | 工具 action、安全 commit |
| AgentLeak | coordinator-worker | 1,000 scenarios、四领域、五模型 | 七条内部/外部 channel instrumentation | channel leakage、utility | 长期 memory 正确率、所有 runtime 默认值 |
| StateFuse | replicated memory surface | 282 个 conflict-bearing MemoryAgentBench 问题 + controlled loop | conflict-preserving vs collapsed views | answer、conflict visibility、abstain/correction | 独有 accuracy 优势、permission 与 production scale |
| PatchBoard | Architect + workers + kernel | 126 ALFWorld gamefiles ×5 seeds；240 HotpotQA diagnostic | schema/patch/contracts/context slices | success、steps、tokens/success、fault contamination | 开放 schema 的所有语义正确性 |
| MAP-Graph | 四固定角色、typed lineage | 2,700 synthetic tasks/method，三领域、六组 | permission、path trust、containment、action gate | TSR、exact decision、unsafe/leak/revoke | repeated-run nondeterminism、真实 side effect、部署采用 |
| MATM | 35–37 producers、34 consumers | ALFWorld 3,553/274；WebArena 724/88 | population trajectory index + consumer ranker | success、steps、retrieval utility | malicious producer、permissions、跨环境普遍性 |
| G-Memory | AutoGen/DyLAN/MacNet teams | QA、embodied、PDDL 五 benchmark | query/insight/interaction graphs | task metric、tokens、sensitivity | scope/governance、所有 team topology |
| MemCollab | heterogeneous backbone Agents | MATH/GSM/MBPP/HumanEval，train/test 分离 | cross-model contrastive constraint bank | accuracy、efficiency | 开放工具环境、安全 transfer |
| ConMem | multiple MAS hosts | code、QA、PDDL online stream | signed card graph + coordinate/compose | task metric、candidate pruning | long-term stale skill、permission |
| TreeMem | memory-worker pipeline | PersonaMem 32K/128K/1M + long-memory QA | tree credit for builder/summarizer/retriever | QA metrics、agent ablation | peer task Subagents 的共享记忆 |
| Bad Memory | Claude Code/Codex systems | synthetic workspace、3 attack goals、4 models | pre-planted memory-file payload | ASR、persistence over sequences | payload 写入难度、生产发生率、Subagent propagation |

## 可比性组

### Governance 组

GateMem、AgentLeak、Collaborative Memory 与 MAP-Graph 都涉及权限，但对象不同：GateMem 测 requester-specific answer；AgentLeak 观察内部 channel；Collaborative Memory 模拟 policy graph；MAP-Graph 在 synthetic action decision 中联合 lineage 与 gate。它们能互相补充，不能合并成一个安全排名。

### Conflict/commit 组

StateFuse、LatticeMind、PatchBoard、MemTX 分别强调 public conflict surface、status/reconciliation、validated patch 与 staged belief transaction。只有在 state object、conflict input、resolver budget、action environment 和 repair metric 对齐时才可数值比较；当前没有这样的共同协议。

### Experience-transfer 组

MATM、G-Memory、DecentMem、MemCollab、ConMem 使用不同 Agent population、task stream、memory unit 和 compute budget。应比较机制：raw trajectory、hierarchical graph、per-agent pool、contrastive constraint、signed card，而不是把各论文最佳分数拼表。

### Runtime retention 组

公开产品提供 stateless/per-invocation/per-thread/cross-session knob，但当前选中 Benchmark 很少在同一 runtime 内系统比较这些模式。该空白直接限制了“Subagent 该不该有自己的长期记忆”的经验判断。

## 一个合格实验需要记录什么

```text
topology + identities + scope
task/dataset/version
model and decoding
delegation packet / checkpoint / memory warm-up
write, merge, retrieval and action budgets
tool environment and side-effect model
judge/metric and repeated-run protocol
security/permission/deletion conditions
artifact and code version
```

缺少这些字段时，报告只描述作者设置下的结果，不把数字推广为通用结论。
