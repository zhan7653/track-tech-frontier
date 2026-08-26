# 第 6 层：反馈、经验与持续学习

前五层让经历成为可读 Memory；第六层才回答“使用以后，系统怎样知道什么值得保留、怎样把结果变成更好的经验、Skill 或 Memory design”。TencentDB 与 Codex 目前各闭合了一小段反馈链，主体进展来自下面这些具体论文和仓库。

## 6.1 TencentDB：轨迹 Review → Skill 版本

[TencentDB Agent Memory `0aff21a`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a)把真实 `user/assistant/tool_call/tool_result` 轨迹归档给 Review Agent。Review 通过分类、72 分门槛、`skill_list/skill_view` 查重后，选择 create/update/patch/no-op，并以 `expected_version` 形成新的不可变 Skill version。新 Session 只看到 active head。

```text
任务轨迹
→ Review：是否存在可复用能力
→ Skill v1 / v2 / v3 或 no-op
→ 后续 Session 读取 active version
```

这已经实现“执行经历 → 版本化能力 → 再复用”，但轨迹中没有稳定账本把某个 Skill 的曝光、实际采用和最终任务质量连接起来。可选 Asset Reflection 默认关闭；即使生成文字反思，固定实现也不会自动解析并据此调整资产效用。

## 6.2 Codex：citation → usage → Phase 2 selection

[Codex `c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)要求 Agent 使用 Local Memory 后在最终回答附文件行与 rollout IDs。citation parser 验证 ID，并让对应 Stage 1 candidate 的 `usage_count += 1`、`last_usage = now`；Phase 2 以后按使用与新鲜度选择候选。

```text
Memory 片段被回答引用
→ citation 指向 rollout IDs
→ usage_count / last_usage 更新
→ 下次 Phase 2 更可能选择这些来源
```

这闭合的是 citation-driven retention，不是效果学习：citation 证明 Agent 声称采用了来源，不证明任务成功，也不记录内容被展示却未采用的 exposure。

## 6.3 XSkill：Experience Bank、Skill Library、多路径与 cross-rollout critique

[XSkill](https://arxiv.org/abs/2603.12056)把一次成功轨迹拆成两种不同学习产物：Experience 是 action-level 的“触发条件 → 建议动作”；Skill 是 task-level 的结构化 workflow 与工具模板。它们分别进入 JSON Experience Bank 与 Markdown Skill Library。

```text
Experience e = (condition, recommended action, embedding)

Skill k = (
  metadata: name / description / version,
  workflow sequence,
  reusable tool templates
)
```

### 同一任务主动运行多条路径

在 accumulation phase，同一训练任务由执行模型独立运行多次；论文主设置使用 N=4 rollouts。每条路径保留任务图片、视觉中间状态、文本推理、工具调用/结果和最终 outcome。知识管理 MLLM 先做 visually grounded summary：它不只写“调用了旋转工具”，还记录倒置图像这一视觉证据为何触发旋转、旋转后的观察怎样改变后续判断。

随后 cross-rollout critique 横向比较成功与失败路径：哪些动作在成功路径稳定出现，哪些只是偶然步骤，哪些失败由错误工具选择或遗漏视觉条件造成。Critique 输出 Experience 的 `add/modify` 操作；成功轨迹同时贡献 Skill fragments。Experience 在提交前按 cosine similarity 合并近似项，容量超限时再移除冗余/低质量项；Skill fragments 则与全局 Skill 文档分层合并、去重和抽象。

```text
同一视觉任务
├─ rollout A：未旋转图像 → 识别失败
├─ rollout B：旋转后裁剪 → 成功
├─ rollout C：只增强对比度 → 仍失败
└─ rollout D：旋转 + 裁剪 + 识别 → 成功
       ↓ visually grounded summaries
       ↓ cross-rollout critique
Experience：检测到方向异常时，先校正方向再做局部识别
Skill：视觉检查 → 方向判断 → 变换 → ROI 裁剪 → 验证
```

Inference phase 先把新任务分解为多个技术子目标，分别检索 Experience；再根据当前图片重写触发条件与动作，丢掉明显不适用项。Skill adaptor 剪去无关工作流、把重写后的 Experience 嵌入步骤，并把结果作为非强制参考注入执行模型。实际使用过的 Experience/Skill 形成 usage history，下一轮 accumulation 又以它为 critique 参考。XSkill 的持续学习因此发生在外部双流知识库，而不是模型参数中。

## 6.4 Trace2Skill：轨迹池、并行 patch、层次化 Skill 合并与迁移

[Trace2Skill](https://arxiv.org/abs/2603.25158)不在推理时检索许多零散经验，而是先用大规模轨迹池把经验编译成一个可直接加载的 Skill directory：根 `SKILL.md` 保存广泛程序，`references/`、scripts 或 assets 保存低频细节和确定性工具。

它的三阶段管线是：

1. 冻结的 ReAct Agent 使用初始 Skill 跑 evolution tasks，收集 query、推理/工具历史、最终输出和 binary correctness；轨迹分成 success 与 failure pools。
2. 大量 analyst sub-agents 并行处理单条轨迹。Success analyst 从成功路径抽取可复用行为；Error analyst 可以检查 trace 和 artifacts、与 ground truth 对照并验证候选修复。无法解释因果失败的轨迹不产生 patch。
3. 所有 trajectory-local patches 进入层次化 many-to-one merge。每层最多合并一批 patch，去重、解冲突并保留不重叠洞见，直到得到一个 consolidated patch；最后转成 diff-style edits，拒绝不存在文件、搁置行区间冲突并验证 Skill 格式。

```text
frozen agent + initial skill
→ labeled trajectory pool
→ success/error analysts 并行提出 patches
→ patch pool
→ merge tree：局部补丁 → 中间补丁 → consolidated patch
→ portable SKILL.md + references/scripts/assets
```

层次化合并的学习单位不是“最相似的一条历史”，而是多条独立 patch 中反复出现的错误、workaround 和标准操作。普遍模式留在 `SKILL.md`；task-specific quirks 下沉到按需 reference。形成后的 Skill 直接用于 inference，不需要再次检索每条轨迹。

论文同时区分 Skill deepening 与 creation：前者从人工 Skill 开始补强，后者从模型参数知识生成的弱草稿开始。迁移实验再把 author model 与 user model 分开，检查 Skill 是否能跨模型规模、模型家族和 OOD table-QA 任务使用。于是反馈链的输出不只是“原任务变好”，还包括一份可以在不同执行 Agent 上复用的程序工件。

## 6.5 EvoSkills / CoEvoSkills：Generator–Verifier 迭代晋升

[CoEvoSkills](https://arxiv.org/abs/2604.01687)面对的是多文件 Skill package：单次生成很容易留下覆盖缺口和逻辑错误，因此用 Skill Generator、独立 Surrogate Verifier 与 Ground-Truth Oracle 组成共同演化循环。

Skill Generator 从任务说明、可见背景资料和通用 skill-creator meta-skill 出发，产生第一个 package。执行该版本后，Surrogate Verifier 在独立 LLM session 中只看到任务输入、输出 artifacts 与自己维护的测试脚本；它看不到 Generator reasoning、Skill source 或隐藏 oracle tests。Verifier 生成确定性 assertions，返回逐项失败、根因和可操作修订建议。

```text
Skill S(i)
→ 在工作环境执行，产生 artifacts y(i)
→ Surrogate Verifier 跑 V(j)
   ├─ fail：固定测试集，diagnostics → Generator 修订 S(i+1)
   └─ pass：在新环境重新执行 → Ground-Truth Oracle
              ├─ pass：晋升/结束
              └─ fail：只回传 pass/fail bit，Verifier 自主加难 V(j+1)
```

Surrogate 通过而 Oracle 失败时，系统不泄露隐藏测试内容；Verifier 必须根据可观察输入与当前 artifacts 扩展测试。每次 Oracle 评估都在 fresh environment 重跑，系统保存 best Skill snapshot，达到完美结果提前结束。

论文的 exoplanet transit 案例展示了产物怎样演化：早期 BLS 方案先被 surrogate 捕获格式与逻辑 bug；surrogate 全过后 Oracle 仍指出精度不足；多轮反馈最终让 Skill 从 BLS 切换到 TLS，并加入两阶段精度与 alias 检查。Generator 与 Verifier 都在演化：一个修 Skill，一个修“怎样验证 Skill”。

## 6.6 MemSkill：controller、executor、designer 与 hard-case evolution

[MemSkill](https://arxiv.org/abs/2602.02474)学习的不是业务 Skill，而是“如何从交互轨迹构造和修订 Memory”的 memory skills。它明确分开两个 store：每条 trace 自己的 memory bank，以及跨 trace 共享的 skill bank。Skill bank 从 Insert、Update、Delete、Skip 四个基本 operation 起步。

### Controller 与 Executor 先学习怎样使用现有 Skill

长 trace 按 token 切成连续 spans。对每个 span，controller 同时看当前文本与该 trace 已检索的现有 memories，从不断变化的 skill bank 选 Top-K。LLM executor 一次应用这些 Skill，更新 trace-specific memory bank。完成后的 Memory 再回答 memory-dependent training queries，任务 reward 用于优化 controller 的 selection policy。

### Designer 从反复失败处改变 Skill bank

回答错误或不完整的 query 连同 used memories、prediction、reference、reward 与 failure count 进入滑动 hard-case buffer。Designer 对 cases 聚类，在每个 cluster 中优先选择低 reward、反复失败的代表项，然后分两步更新：先分析缺失或错误的 memory behavior，再提出对现有 Skill 的具体 edit 或新增 Skill。

```text
trace spans
→ controller 选 memory skills
→ executor 构造/修订 trace memory
→ query evaluation + reward
→ hard-case buffer
→ cluster + difficulty selection
→ designer：behavior diagnosis → edit/new skill
→ 新 skill bank → 下一轮 controller/executor
```

系统保存最佳 skill-bank snapshot；更新导致性能下降时 rollback，连续不提升则 early stop。新增 Skill 后短暂提高其探索概率，让 controller 真正试用并学习效用。MemSkill 的闭环同时优化“选哪些 operation”和“operation 本身怎样写”，而不只是不断往 Memory 追加文本。

## 6.7 MemCon：任务反馈驱动的 Memory 操作策略

[MemCon](https://arxiv.org/abs/2607.13591)不替换底层 store，而是在任意 memory backend 的 `retrieve/store` 外包一层轻量 controller。它把每次 Memory 操作建模为 Memory MDP 的 action：

```text
Retrieve(top_k, insight_k, hop)
PlanInject
Re-Retrieve(alternative query)
Consolidate
Forget
NoOp
```

状态同时描述 task progress 与 memory status：goal type、step phase、是否 stuck、已访问位置，以及 store size、是否存在成功计划、当前 learning phase。实现把状态离散成几百个 key，用 tabular contextual bandit 和 UCB 在 action value 与探索奖励间选择；初始化 priors 让 Retrieve/PlanInject 较早被尝试，Forget/NoOp 较保守。

每个任务结束后，环境给出 success/failure 和效率奖励。系统用 reverse-discounted Monte Carlo return 更新本次访问过的 `(state, action)`；越接近最终结果的 Memory 决策得到越强 credit。Q-table 定期持久化，所以策略跨任务流积累。

一个 stuck Agent 连续重复同一动作时，state 中 `is_stuck=true`；policy 可以从普通 Retrieve 切到 Re-Retrieve，用“alternative approach”改写 query，避免再次读到相同 top-k。遇到相同 goal type 时，PlanInject 可以加载过去成功轨迹抽象出的对象无关动作模板。Consolidate/Forget 只在 backend 真正提供 maintenance hook 时执行，否则静默 no-op；这避免把论文 action name 误写成所有后端都有的能力。

MemCon 从任务级二值结果学习“何时、取什么、取多少、何时不取”，且 controller lookup 不增加 LLM 调用。它的持续学习对象是操作策略，不是 Memory 正文。

## 6.8 AFTER：跨任务、角色、模型的程序性经验迁移

[AFTER](https://arxiv.org/abs/2606.23127)是一套专门测 procedural memory 是否真正可迁移的 benchmark，而不是另一个 Skill 生成器。它包含 382 个现实 workplace tasks、六种专业角色与 22 类 procedural skills，并为每个 role-skill cell 建立 train/validation/test splits。

评测依次区分四件事：静态 Skill 是否改善本地任务；一次 refinement 是否有效；从 narrow traces 与 diverse traces 演化的 Skill 有何不同；Skill 换 task、role 或 model 后是否仍有效。每次执行 trace 都链接到使用的 Skill version；operator 修改后产生 child version，未采用候选保留为 inactive branch，named snapshot 固定一次评测的 active versions。

```text
source tasks / roles / models 的执行 traces
→ skill refinement/evolution
→ version lineage + active snapshot
→ held-out task test
→ cross-role test
→ cross-model test
→ transfer matrix：general / specialized / regressed
```

论文结果说明“在原角色上变好”不能代替迁移证据。多模型来源的多样 traces 形成的 Skill 在作者 cross-model protocol 中达到 73.1% test accuracy，高于单一来源；但同一个 PDF Skill 从 Project Manager 迁到 Data Scientist，或反向迁移，会因工作目的不同而损失 4.8–7.5 个点。输出因此应包括适用角色和迁移结果，而不是只给一个累计成功次数。

AFTER 将持续学习的验收从“文件生成了”推进到“离开原任务后还是否有用”，并揭示程序经验会自然形成 specialization。

## 6.9 ALMA：Meta Agent 搜索 Memory design

[ALMA](https://arxiv.org/abs/2602.07755)把学习对象再提升一层：不是改一条 Memory、一个 Skill 或一个 controller action，而是搜索由可执行 Python 表达的完整 Memory design，包括 schema、抽取、更新和检索机制。

Memory design archive 从一组抽象类模板开始。每轮 Meta Agent 从 archive 采样旧 design，读取其 source code、成功率，以及从成功/失败 execution logs 分层抽样出的少量代表记录；随后反思、提出 plan，并实现一个新 design。trial run 用少量 collection/deployment tasks 检查实现，runtime error 时最多进行三轮 reflection/debug。

```text
archive：design code + score + sampled logs + sample count
→ sample parent designs
→ Meta Agent：reflect → propose → implement code
→ trial run / debug
→ Memory Collection：general_update(trajectory)
→ Deployment：general_retrieve(task)
→ success、cost、interaction logs
→ 新 design 加回 archive
```

正式 evaluation 把任务分为 Memory Collection 与 Deployment 两段；固定 Agent 使用 `general_update` 写入经验，再用 `general_retrieve` 取回。新 design 的表现与 end-to-end cost、retrieved-context tokens 一起记录。Archive sampling 同时考虑相对无 Memory baseline 的收益和某个 design 已被采样的次数，避免永远只沿当前最优分支贪心搜索。

最终产物是一棵可追溯的 Memory-design lineage：中等分数的 schema/normalization/strategy-switching 设计也可能成为后来更优设计的 stepping stone。论文在 ALFWorld、TextWorld、Baba Is AI 与 MiniHack 等顺序决策域评估该搜索过程；它说明 Memory 架构本身可以由任务结果驱动演化。

## 6.10 Causal Memory、Omri 与相关基准：结果归因、成本和持续评测

### Causal Memory：把 decision → outcome 保存成可检索关系

[Causal Memory 固定提交 `054af36`](https://github.com/JingxuanC/causal-memory/tree/054af36507537f7b616fa41db07be483cc6e55c3)先保存 raw session logs，再以每 Session 一次 distill 抽取 atomic facts 与 decision→outcome causal edges；失败时不写 done marker，原日志仍可重试。读取分别从 BM25/optional embedding、causal、entity 与 trace route 取候选，用 RRF 汇合并可做 typed spreading activation。

```text
session log
→ context + decision/action + outcome
→ fact / causal edge / lesson
→ BM25 + semantic + entity/trace + causal activation
→ 后续任务的 prompt-visible memory lines
```

这使系统能问“哪个决定在什么条件下导致了什么结果”，而不只找相似文本。它保存的是结构化 lesson，不是可执行 Skill；causal edge 仍由 distillation 生成，弱相似建立的跨任务 meta-edge 可能放大错误类比。要做效果归因，还需把召回的 edge、实际行动与新 outcome 再连接起来。

### Omri：把 Memory 成本按 construction / retrieval / generation 计量

[Agent Memory: Characterization and System Implications](https://arxiv.org/abs/2606.06448)建立 phase-aware profiling harness，在同一 monotonic timeline 上记录 API 与硬件 telemetry，把 token、模型调用、延迟、utilization 和 energy 分到 construction、retrieval、generation 三阶段。这样可以看见“短 Prompt”是否只是把成本搬到后台抽取和巩固。

论文还测 construction scheduling 的 freshness–latency trade-off：异步构造减少前台写延迟，却可能让下一 Session 查询尚未提交的新状态；不同系统的 per-session construction time 在作者测试中跨越多个数量级。持续学习因此不能只优化成功率，还要记录后台积压、写到可见的延迟、每次再检索和重建成本。

### 相关基准各自测闭环的一段

| 基准 | 具体观察对象 | 对持续学习的作用 |
|---|---|---|
| [MemoryAgentBench](https://arxiv.org/abs/2507.05257) | accurate retrieval、test-time learning、long-range understanding、selective forgetting | 区分“读到”与“新规则改变旧状态” |
| [Mem2ActBench](https://arxiv.org/abs/2601.19935) | 历史约束是否改变工具选择与参数 | 把 Memory 使用连接到实际 action |
| [SkillsBench](https://arxiv.org/abs/2602.12670) | 多文件 Skill package 在专业任务中的表现 | 检查 Skill 内容与执行结果，而非文件是否存在 |
| [ForgetEval](https://arxiv.org/abs/2606.15903) | supersede/release/purge 及 control-plane placement | 检查状态变化是否覆盖 canonicalization 与 intent-aware mutation |
| AFTER | local、cross-task、cross-role、cross-model transfer | 检查经验是否过拟合形成环境 |

这些结果不能压成一个“Memory 分数”。一套持续评测应把同一条链逐段记录：

```text
memory/skill version
→ 是否曝光、读取、采用
→ 进入了哪次计划或工具参数
→ task outcome / 用户纠正
→ token、延迟、重试与维护成本
→ 下一版 Memory、Skill、policy 或 design
```

只有这条可追溯链建立以后，系统才能区分“常被引用”“确实改善结果”“只在原环境有效”和“收益低于维护成本”。本层各案例分别补充了 Experience/Skill 形成、验证晋升、操作策略、迁移、架构搜索、结果关系和系统成本中的一段。
