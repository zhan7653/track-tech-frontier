# 上下文继承：从“复制历史”到显式委派契约

## 问题与边界

委派不是把一段 prompt 交给另一个模型这么简单。Parent 持有用户指令、计划、工具结果、秘密、工作区和权限；Child 只需要其中与局部任务有关的部分。继承设计需要同时定义**内容视图**、**资源能力**、**更新时序**和**回传接口**。本页只研究一次 spawn/handoff 的边界；Child 自己跨多次调用保留多久见[局部持久化](../local-persistence/01-runtime-lifetimes.md)。

## 方案族及内部流程

### 全历史/同一运行继承

Handoff runtime 可以让新 Agent 接管当前 run，并继续读取原消息序列。数据流最短：

```text
parent messages + tool items
→ switch active instructions/Agent
→ child continues the same history
→ child output remains in the same run/session
```

优点是没有额外摘要器，也较少丢失背景。问题是 Parent 推断、用户秘密、无关日志和旧工具结果都可能进入 Child；历史本身没有说明哪些字段是权威状态、哪些只是讨论。即使 runtime 支持 input filter，过滤器仍要承担完整性与泄漏的双重责任。

### 结构化 delegation packet

Parent 先构造一个显式对象，例如：

```json
{
  "objective": "核验支付重试逻辑",
  "acceptance": ["定位调用点", "给出失败证据"],
  "facts": [{"value": "base=abc123", "source": "git"}],
  "artifacts": ["src/retry.ts"],
  "permissions": {"read": ["repo"], "write": []},
  "unknowns": ["生产配置是否相同"]
}
```

packet 将“任务描述”和“已有状态”分开，并能保留来源、未知项与完成标准。生成可以由规则、模型或二者组合：规则适合字段和权限，模型适合从长历史提炼开放问题。主要失败是压缩时把推断写成事实、删掉反方、或只传完成目标却不传验证条件。

### 预声明返回契约与下行隔离

[AGENTSYS](https://arxiv.org/abs/2602.07398)把每次不可信工具调用放入短命 worker。Parent 在看到工具输出前声明 typed intent；raw output 只进入 worker，worker 返回 JSON，Parent 只接纳符合接口的结构化值。worker 可以递归调用工具，但新的调用再产生 Child；validator 只看用户目标和精简调用 trace，不接触 raw output。

```text
parent chooses tool + typed intent
→ raw output enters isolated worker
→ worker extracts declared fields
→ syntax/schema/validator gate
→ accepted value enters parent context
→ worker context discarded
```

这条路线把“不必要信息不进入 Parent”作为安全机制，而不是等污染进入长历史后再检测。它仍有边界：字符串字段可以携带攻击文本，schema 只能限制形状，validator/重试自身也会增加模型调用与拒绝风险。

### Capability-scoped spawn

[When Child Inherits](https://arxiv.org/abs/2605.08460)把 spawn 描述为能力传播：Child 可能继承 memory、filesystem、credentials、tools、termination authority 和资源配额。其四类问题是无限制记忆继承、缺少资源访问控制、spawn 后异步状态分叉，以及越权终止其他 Agent。

因此资源边界要独立于文本 packet：Parent 可以给 Child 只读仓库、单独 worktree、有限网络、临时 credential、只读 memory view 和不能终止 sibling 的 capability。仅提示“不要访问秘密”不是能力控制。

### Snapshot 与 revision-aware 同步

Child 可以拿静态 snapshot，也可以订阅 Parent/Team 状态。静态 snapshot 可重放、易调试，但长任务会读取旧状态；实时共享减少陈旧，却引入 race 和非确定性。revision-aware 路线让 delegation packet 携带 base revision，回流时比较 current revision：若 Parent 状态已经改变，则 rebase、重算或标记冲突，而不是静默覆盖。

## 方案比较

| 方案 | 状态充分性 | 隔离 | 并发 | 主要成本 |
|---|---|---|---|---|
| 全历史 | 高但过宽 | 弱 | 顺序 run 较简单 | token 与泄漏 |
| 结构化 packet | 可控 | 中 | 需版本字段 | 提炼与遗漏 |
| 隔离 worker + typed return | 返回面最窄 | 强 | worker tree 复杂 | validator/重试 |
| Capability-scoped spawn | 文本与资源同时隔离 | 强 | 需 registry/PDP/PEP | 控制面 |
| Revision-aware snapshot | 可重放且检测陈旧 | 中到强 | 显式 rebase/conflict | 版本管理 |

## 成本与失败模式

- 过窄 packet 会让 Child 重新探索或给出表面答案；
- 过宽继承会重复处理攻击文本，并让 Child 混淆 Parent 的假设与事实；
- schema-valid 不代表语义正确；
- Parent 的权限模式可能覆盖 Child 的较严格设置；
- snapshot 的安全性不能证明 spawn 后仍然新鲜；
- delegation summary 若没有来源，后续无法执行撤销与权限传播。

## 当前研究在改变什么

前沿从“怎样写一个好的 Subagent prompt”转向四个可验证对象：最小充分 packet、能力继承图、base revision 与 typed return。尚缺统一实验同时测量 Child 完成率、额外探索、秘密泄漏、攻击继承和状态陈旧；不同 runtime 的 handoff、agent-as-tool、sandbox 与 worktree 也还没有可比协议。


## 证据账本绑定

现实 runtime 已把历史、普通 state、application context、workspace 和能力暴露为不同继承面；因此“Child 拿到一段摘要”不能替代完整的委派边界，当前也没有跨框架统一的最小充分继承协议。
<!-- synthesis:SY-C01 claims:R5-C001,R5-C003,R5-C007,R4-C019 clusters:SM-C01 -->
