# 身份、时间与共享权限：一条记忆在谁的世界里成立

对象模型解决“记的是什么”，作用域模型解决“它对谁、在何时、以什么权限成立”。许多实现把作用域缩成 `user_id` 或 namespace；这足以做简单过滤，却不足以表达 Agent 代用户行动、多个 Agent 协作、迟到证据修订历史、项目分支并行，以及共享内容被撤销后的传播。

本篇从四组经常混在一起的语义展开：身份角色、时间轴、版本/冲突，以及共享 authority。重点是这些语义怎样进入写入、读取和行动，而不是罗列权限字段。

## 1. 身份不是一个 ID，而是一组角色

一次记忆变化至少可能涉及五种身份：

| 角色 | 回答的问题 | 例子 |
|---|---|---|
| actor | 谁执行了写入或修订 | Agent A、用户、后台 extractor |
| subject | 这条状态描述谁或什么 | 用户 B、项目 P、文件 F |
| owner | 谁拥有或可撤销这条对象 | 个人账户、团队、组织 |
| principal | 当前谁在请求读取或行动 | Agent C 代表用户 B |
| tenant / domain | 哪个隔离与治理边界 | workspace、组织、项目环境 |

把五者压成 `user_id` 会产生典型混乱：Agent 代用户写入时，actor 与 subject 被当作同一人；团队导入个人偏好时，owner 与 tenant 混同；读取时只验证对象属于某 workspace，却没有验证当前 Agent 的用途和委托关系。

### 1.1 写入时建立身份，而不是检索后猜

较稳健的顺序是：transport/session 先给出 authenticated principal；宿主上下文确定 tenant 与当前 task/project；输入内容只能提出 subject 候选，不能自行覆盖 principal。`metadata={user_id: ...}` 若可由被保存文本任意注入，会让隔离形同虚设。

固定版本的 [Mem0 工程分析](../../projects/mem0ai--mem0.md)显示其 orchestration 从调用参数设置 user/agent/run filters，并剥离 metadata 中伪造身份；这是一个具体的边界实现。它不能证明所有 backend 都有同等隔离，因为 provider adapter、history 和 entity collection 仍可能拥有不同 scope 能力。

### 1.2 读取与行动使用不同权限

一条对象可被检索，不表示它能授权行动。读取权限决定某 principal 是否能看到证据；行动权限还取决于当前工具、目标资源、风险和委托。例如团队 Agent 可以读取“部署流程”，但不能因为流程中保存了某个命令就自动获得生产凭据。程序性对象尤其需要将 information authority 与 capability authority 分开。

## 2. 四种时间回答四个不同问题

Agent Memory 中常见的时间至少包括：

```text
occurred_at       事件何时发生
valid_from/to     一个断言在现实或业务语义中何时成立
recorded_at       系统何时得知并提交这条信息
processed_at      摘要、embedding、graph 等投影何时生成
```

同一条记录的这些时间可以不同。离线导入的会议纪要可能在周一发生、周五才记录；一次修订可能声明某政策从周三起生效；embedding 可能因队列延迟到周六才完成。只有一个 `timestamp` 时，系统无法区分“当时世界怎样”“当时系统知道什么”和“当前索引是否已经追上”。

### 2.1 双时间状态如何工作

双时间模型通常把 valid time 与 transaction/recorded time 分开。每次修订追加一个新版本：

```text
Object identity: deployment-policy

v1: value=A, valid=[2026-07-01, ∞), recorded=2026-07-01
v2: value=B, valid=[2026-07-10, ∞), recorded=2026-07-12
```

在 7 月 11 日运行的 Agent 根据当时已记录的 v1 行动；7 月 13 日查询“7 月 11 日世界实际采用什么”可能返回 v2 的 valid-time 解释，同时查询“Agent 当时能知道什么”仍返回 v1。这是 bitemporal 模型比 last-write-wins 多表达的语义。

[图原生双时间 Memory](https://arxiv.org/abs/2607.26520)用稳定 identity、版本化 content、valid time 与 transaction time表达这一差别。它提供了清晰模型，但作者的小规模实验同时出现某些更新任务改善和 temporal reasoning 下降，说明后过滤、候选深度和读者模型仍会影响结果；双时间语义清晰不等于任意实现都更准。

### 2.2 投影时间为何也重要

权威状态已提交 v2，而向量或图索引仍在 v1，会出现“数据库正确、检索过时”。index watermark 应表明投影覆盖到哪个 revision；读取可以等待、回退到权威查询或标记结果不完整。没有 watermark 时，零结果无法区分对象不存在、scope 被拒绝、索引尚未构建或 embedding 失败。

## 3. 版本、替代和冲突不是同一种变化

### 3.1 五种常见关系

| 关系 | 含义 | current view 如何处理 |
|---|---|---|
| amend | 同一对象补充不冲突字段 | 合并成新 revision，保留前驱 |
| supersede | 新值明确取代旧值 | 新值 current，旧值进入 history |
| contradict | 两个来源互不相容，尚未解决 | current 可为空或并列冲突 |
| branch | 两个 scope/项目分支各自有效 | 按 scope 选择，不互相覆盖 |
| retract/revoke | 内容或权限被撤回 | 停止可见/可用，并触发派生修复 |

传统 upsert 只能方便地表达 supersede，而且经常不保留旧值；但 Agent 需要知道冲突是否已解决、某版本在哪个 scope 有效，以及撤回是否只是停止召回还是要求物理清除。

### 3.2 冲突解析是可观察操作

冲突解析可能由来源优先级、明确用户确认、时间有效性、领域规则或模型判断完成。无论使用哪种机制，结果都应留下 `decision / actor / reason / source set / previous current / new current`。否则一次模型选择会变成无痕覆盖，后续无法区分“新证据修订”与“错误抽取覆盖”。

### 3.3 迟到证据会改变历史而不一定改变现在

迟到事件可能补齐过去某段 history，却不改变 current。例如系统今天导入一份上月的旧配置文件；若只按 recorded_at 排序，它会成为“最新”值。有效时间与版本关系使系统可以把它插入历史，同时保持当前版本不变。

## 4. 共享 Memory 的三种一致性模型

### 4.1 私有对象 + 共享视图

原对象继续由个人或 Agent 拥有，共享层保存 policy 和 view pointer。读取时根据 principal、purpose 和字段级规则生成最小披露视图。优势是撤销较清楚；代价是共享结果依赖源对象可用性和动态 policy。

### 4.2 复制到共享空间

对象在分享时形成新 identity 或 fork，之后可独立修订。这适合 handoff 或发布知识，但撤销原对象并不会自动删除共享副本；系统需要明确 copy 的许可、provenance 和后续责任。

### 4.3 共同修订 canonical object

多个 actor 更新同一对象，需要 revision、conflict 和 authority 模型。简单 last-write-wins 可能丢掉并发更新；CRDT/merge 可以保留结构变化，却不能自动判断语义冲突。共享事实、项目决策和 procedure 对 merge 的含义也不相同。

这三种模型不能由一个 `shared=true` 字段代替。当前协议草案和项目 schema 多能表示对象与 namespace，却较少提供经过验证的多写者冲突、撤销、派生删除和语义 round-trip。

## 5. 可移植性不只是 JSON 能否解析

要把一条 Memory 从系统 A 移到系统 B，至少存在四个层次：

1. **syntactic**：字段可解析；
2. **structural**：对象、关系、时间和版本没有丢失；
3. **behavioral**：update、forget、retrieve 后得到相同可观察语义；
4. **governance**：owner、purpose、consent、revocation 和审计边界仍成立。

项目级 AMP/OMP/UMP 往往先解决前两层；W3C Community Group 与 individual Internet-Draft 代表标准形成活动，但不能被写成已经有正式 Recommendation/RFC。MCP 提供 tools/resources/prompts 等上下文交换原语，durable task 也不是 Agent Memory 的对象/生命周期语义。

固定版本的 [Open Memory Protocol](../../projects/smjai--open-memory-protocol.md)包含 memory schema、Express routes、SQLite/FTS5 reference server 和多个 adapter。它证明一种 exchange shape 可以落成代码；embedding 字段虽可保存，实际搜索只使用 FTS OR，因此“schema 中有 embedding”不等于 reference implementation 已实现语义向量检索，更不等于跨实现一致性。

## 6. 撤销与删除为何穿过所有作用域层

撤销一条共享事实至少要处理：

```text
canonical object
  ├─ current/profile view
  ├─ summary
  ├─ embedding / FTS / graph edge
  ├─ exported or copied object
  ├─ compiled prompt / cache
  └─ derived procedure or past action
```

停止 canonical object 的读取只解决第一步。可重建投影可以按 revision 失效；已复制对象需要另一套 revoke/recall 语义；过去行动无法被数据库删除，只能通过补偿、修复和未来授权防止继续使用。因而“删除成功”至少要区分逻辑不可见、索引清除、物理清除、备份过期和行为修复。

## 7. 作用域错误怎样在链路中传播

| 起点 | 隐蔽传播方式 | 最终表现 |
|---|---|---|
| actor/subject 混淆 | 抽取事实归到错误 profile | 另一个用户收到个性化内容 |
| valid/recorded time 混淆 | 迟到旧事实成为 current | Agent 执行过期流程 |
| namespace 当作授权 | 检索只按 team filter | 低权限 Agent 读取敏感共享状态 |
| revoke 只改主表 | embedding/cache 仍有旧副本 | 已撤销内容继续进入 prompt |
| branch identity 丢失 | 项目事实跨分支合并 | Coding Agent 在错误版本修改代码 |
| copy 与 view 未区分 | 原对象撤回不影响副本 | 共享系统仍合法返回旧内容 |

[STALE](https://arxiv.org/abs/2605.06527)所代表的负面方向指出：状态更新与 Agent 行为更新之间存在能力缺口。其意义不只是“模型会忘记”，而是系统需要观察 revision 是否穿过检索、上下文和行动。

## 8. 当前前沿正在补什么

近期工作的关注点已从 namespace filter 走向更完整的状态语义：双时间用于分开历史和认知时间；transaction/journal 用于恢复一致 revision；shared/portable 研究尝试让 identity、scope 和 revocation 跨实现；trajectory database 试图把 dependency 和 policy 变成可检查状态。

仍缺四类决定性证据：

- 多写者、迟到证据和冲突同时出现时的统一 benchmark；
- schema round-trip 之外的 operation/conformance tests；
- 删除与撤销穿过摘要、索引、备份和技能的完整追踪；
- action-time 实验，验证纠正是否真正停止旧行为。

因此当前最稳妥的领域判断是：identity/time/authority 已经成为设计共识，但具体跨后端语义、协议成熟度和净成本仍处于早期。继续阅读[代表系统与前沿](03-system-walkthroughs-and-frontier.md)，看这些语义在现有系统中分别被实现到什么程度。
