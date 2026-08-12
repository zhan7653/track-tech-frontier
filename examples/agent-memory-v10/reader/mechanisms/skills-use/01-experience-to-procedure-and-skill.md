# 从经历到程序和技能：可复用行为究竟怎样形成

“Agent 从经验中学习”可能只是把失败反思塞回下一轮 prompt，也可能意味着生成带参数和依赖的 workflow，甚至维护一套会自动更新的可执行技能库。它们在对象、算法和风险上完全不同。要看清这一分支，需要追踪一条经验从原始轨迹到候选规则、再到晋升、检索和实际行动的完整链路。

## 1. 五级复用对象

### 1.1 Episode / trajectory

最保守的持久对象是原始或轻度结构化轨迹：任务、环境、观察、动作、工具参数、结果、错误和人工反馈。它不声称哪一步可泛化，只在相似任务中作为 demonstration 或证据。

优点是来源完整、可重新分析；代价是 token 大、噪声多，失败和成功步骤混在一起。检索必须同时考虑任务、环境版本和 outcome，不能只匹配描述相似度。

### 1.2 Reflection / lesson

反思把一条或多条轨迹解释成语言规则，例如“生成 SQL 前先检查目标表 schema”。Reflexion 的经典循环是：

```text
attempt → evaluator feedback → verbal reflection
       → episodic buffer → next attempt
```

模型权重不变，后续任务将反思与当前观察一起输入。反思易实现，却常缺适用条件和反例；如果 evaluator 错，错误解释也会变成持久记忆。

### 1.3 Instruction / playbook

流程提炼将多个 episode 对齐，抽出参数、稳定步骤、分支和恢复逻辑：

```text
Procedure {
  goal_pattern,
  preconditions,
  inputs,
  ordered_steps,
  branch_conditions,
  expected_observations,
  recovery_steps,
  source_episodes,
  environment_fingerprint,
  validation_state
}
```

MemP 区分逐步 instruction 与高层 script，并为构建、检索和更新分别设计机制。相比自由反思，这一层更易校验和复用；但 distillation 会遗漏长尾分支，尤其容易把“常见路径”写成“唯一正确路径”。

### 1.4 Executable skill

可执行技能是代码、工具模板或 workflow，通常还需要 manifest：入口、参数 schema、依赖、工具/API 版本、资源需求、允许的副作用和测试。Voyager 将 Minecraft 中验证成功的代码放入 skill library，再用描述 embedding 检索和组合。

代码能测试、组合和复用，也把 memory 直接推近真实副作用。技能被召回只表示“候选行为匹配”，不能继承文件、网络、凭据、支付或部署权限；当前 principal 仍需在 action time 重新授权。

### 1.5 Meta-skill / memory policy

元技能不直接解决业务任务，而是决定如何形成和管理其他记忆：何时提炼、合并、遗忘、重新检索或晋升。MemSkill 让 controller 选择 memory-operation skill，executor 构造记忆，designer 根据 hard cases 修改 skill set；MemCon 则把 retrieve/consolidate/forget/no-op 变成在线 policy action。

这类系统可能适应不同任务，却最难归因。最终成功可能来自原始模型、检索、技能内容或控制策略；错误删除/晋升的反事实又可能很晚才出现。

## 2. 形成算法：从轨迹集合得到候选程序

一个较完整的离线/后台形成流程包含：

```text
trajectory normalization
  → outcome and segment labeling
  → task/environment clustering
  → step alignment
  → invariant / branch extraction
  → counterexample check
  → procedure or skill candidate
  → sandbox / replay validation
  → promotion state
```

### 2.1 轨迹规范化

把不同 Agent 或工具的记录转换成统一 event schema：observation、action、arguments、result、error、timestamp、principal、tool version。否则同一动作在不同日志中无法对齐，模型只能从自然语言猜测。

### 2.2 分段与 credit assignment

长任务被切成 goal/subgoal/attempt segment。系统要判断哪些动作对 outcome 有贡献，哪些只是伴随行为。最简单方法是按工具调用和错误边界切段；更复杂方法使用 evaluator、counterfactual replay 或 outcome model。只保留成功轨迹会丢掉“为什么另一条路失败”的边界。

### 2.3 聚类和对齐

按任务意图、状态特征和环境版本聚类，再用 sequence alignment 或 LLM 对齐步骤。稳定出现的步骤成为 backbone，不同分支成为 condition。聚类过宽会混合不同任务；过窄则无法发现可复用规律。

### 2.4 抽象和参数化

把具体路径、用户名、ID、日期替换成 typed parameters，并显式保留 schema 与 constraints。一个“复制某仓库配置”的轨迹若被粗暴抽象成“总是复制旧配置”，会在新版本中制造错误。

### 2.5 反例和适用性检查

候选 procedure 需要与失败轨迹、近似但不适用任务和环境漂移对照。支持次数不是独立性：多个 Agent 可能复制同一错误源。更可信的支持包含不同任务、版本、主体和 outcome，并保留 minority/counterexample。

## 3. 晋升不是保存动作，而是状态转换

候选工件可以经历：

```text
draft → quarantined → replayed → sandbox-validated
      → approved/shadow → active → deprecated/revoked
```

晋升条件可能包括来源多样性、最小成功/失败样本、静态检查、测试通过、允许 effect、人工 approval 或风险等级。`successful=true` 只说明一次 outcome，不足以证明跨任务复用。

可执行工件还要冻结 environment fingerprint：tool/API version、dependency lock、data/schema version、OS/runtime、权限和模型。它们变化后，工件应进入 needs-revalidation，而不是继续以历史成功率排名。

## 4. 技能检索：相似任务只是第一道门

运行时的 applicability filter 至少检查：

- principal、team、tenant 与许可证/共享范围；
- goal、input/output schema 和 required capabilities；
- tool/API/dependency/environment version；
- skill state：active、deprecated、revoked、quarantined；
- effect class 与当前授权；
- historical success/failure 和反例；
- composition conflict 与资源预算。

然后才使用 lexical/dense/graph/learned ranker。返回可按 `fit × validation × recency × trust × cost` 排序，但各 component 必须可观察。一个高相似技能若依赖旧 API，应被版本门挡住，而不是靠 reranker 的“新鲜度”碰碰运气。

## 5. 组合与执行：技能库不是 prompt 片段集合

复杂任务可能把多个技能组成 DAG：

```text
inspect_schema
      ↓
generate_migration ──► run_tests
      ↓                  ↓
backup_state ───────► apply_migration
```

组合器需要检查输入/输出类型、前置条件、资源冲突和 effect ordering。执行器为每一步建立 capability token 或 approval boundary，并记录 observation。失败后按声明的 compensation/rollback 处理；没有 rollback 的动作不能因“来自记忆”而自动重试。

自然语言 reflection 进入 prompt 与可执行技能加载到 runtime 是两条不同信任路径。前者可能诱导模型，后者可能直接产生副作用；统一叫“procedural memory”时，安全报告必须分别说明。

## 6. 反馈怎样更新工件

一次使用后至少产生四类反馈：

1. retrieval：是否选到适用技能；
2. adaptation：参数化/组合是否正确；
3. execution：每一步是否成功、为何失败；
4. outcome：任务和长期结果是否改善。

更新可以调整 applicability、增加 counterexample、修订步骤、产生新 version 或降低 promotion state。直接累加成功计数会形成 self-reinforcing loop：早期被选中的技能得到更多使用，又因更多使用排名更高。应保留 exposure/selection bias，或用 deterministic baseline、shadow/canary 与 off-policy evaluation 约束 learned residual。

## 7. 从本地复用到跨主体迁移

迁移至少有四级：

| 层级 | 变化 | 额外风险 |
|---|---|---|
| 同任务重试 | observation 变化小 | 记住测试实例、过拟合 |
| 跨任务 | goal 相似但输入不同 | 抽象错误、长尾分支 |
| 跨角色/Agent | policy 与权限变化 | 主体边界、职责和许可证 |
| 跨模型/环境 | planner、tool、schema 变化 | 行为语义漂移、不可复现 |

AFTER 的近期研究将 local improvement、cross-task、cross-role 和 cross-model transfer 分开，这比“总体成功率提高”更能判断工件到底复用了什么。视觉/具身路线还要携带观察空间、可见性、位置和动作后果，不能只把文字 instruction 复制到新环境。

## 8. 这一分支真正尚未解决的算法问题

- 如何从少量轨迹识别因果步骤，而不是高频伴随行为；
- 如何保留罕见失败分支，同时仍压缩成可用 procedure；
- 如何为自由语言规则推断可验证 precondition 和 effect；
- 如何在任务、角色、模型和工具版本变化时估计 applicability；
- 如何让 learned meta-policy 可回滚，并度量长期 regret；
- 如何在共享技能中表达来源、许可证、主体和撤销传播；
- 如何将“被写入”“被检索”“被执行”“产生副作用”四个攻击阶段分开测量。

继续看[固定版本工程 walkthrough](02-system-walkthroughs.md)以及[迁移、安全与最新研究](03-transfer-safety-and-frontier.md)。
