# 第 1 层：输入

Agent Memory 的第一层只回答一个问题：**后续形成长期状态时，系统实际收到了什么？** 对 TencentDB 与 Codex 来说，主干都是带顺序的交互—执行轨迹：`user input → assistant response → tool call → tool result`。四类事件的证据角色不同：用户输入主要表达意图、约束与纠正；Assistant 回复可能只是建议；tool call 只证明尝试；tool result 才记录环境返回的观察或执行结果。

事件还必须带上能定位其含义的元数据，例如 user/team/agent、thread/session/task、时间，以及 Coding Agent 中的 cwd、branch、commit。没有这些条件，同一句“先跑回归”无法判断属于哪个项目、哪一版代码或哪次任务。

## 1.1 TencentDB：Chat、Skill、Wiki、CodeGraph 的实际输入

[TencentDB Agent Memory 固定提交 `0aff21a`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a)并没有把所有输入汇入同一条日志。Chat、Skill、Wiki 与 CodeGraph 各自接收与其对象相匹配的原料。

| 输入链 | 实际输入 | 同时携带的定位信息 | 交给下一层的形态 |
|---|---|---|---|
| Chat L0 | 本轮新增的 `user`、`assistant` 消息 | team、user、agent、session，必要时带 task 与时间 | 逐消息 L0 记录与 `accepted_ids` |
| Skill | `user`、`assistant`、`tool_call`、`tool_result` 的完整规范化轨迹 | space、user、team、agent、session | 按 Session 隔离的轨迹 Buffer/Archive |
| Wiki | 上传的 `.md`、`.txt` 文档，以及 Wiki purpose、extraction schema | team、source、source SHA | 等待显式 ingest 的原文 source |
| CodeGraph | `repo_url`、branch、repo name | team/user/agent/task；clone 后再确定 commit | 待解析的仓库快照 |

### Chat 与 Skill 为什么要分两条链

Chat L0 保存真正发生的消息，不在这一层提炼经验。标准路径会去掉 system、工具轨迹以及已经注入过的 memory/persona/scene 块，避免把控制内容或旧记忆再次当作新对话学习。一次调用可能是：

```json
{
  "team_id": "team-alpha",
  "user_id": "user-alan",
  "agent_id": "coding-agent",
  "session_id": "session-001",
  "messages": [
    {"role": "user", "content": "修 bug 前先写能稳定失败的复现测试"},
    {"role": "assistant", "content": "收到，我会先复现再修改"}
  ]
}
```

输出是一条消息一条记录；`accepted_ids` 只说明消息已进入 L0，不表示已经形成 L1 Memory。

Skill 输入则必须保留执行证据。例如一次 refresh token 修复的原始轨迹是：

```text
user        修复登出后 refresh token 仍有效的问题
assistant   我先定位认证链路并建立失败测试
tool_call   运行 refresh token 测试
tool_result 并发刷新用例失败
tool_call   修改 revocation store
tool_result patch applied
tool_call   运行 refresh 与 auth 回归
tool_result all passed
assistant   已修复；多实例使用共享撤销状态
```

这条轨迹能够回答“做了什么、哪里失败、怎样验证”；只保存首尾对话则无法形成可复用 Skill。两条链的输出分别进入第 2 层的 L1 抽取和 Skill Review。

### Wiki 与 CodeGraph 是非对话输入

Wiki 的起点是文档，而不是 Chat transcript。source SHA 让 ingest 能判断原文是否真的变化；purpose 与 extraction schema 则告诉生成阶段哪些页面和关系有价值。CodeGraph 的起点是仓库地址与 branch，clone 得到 commit 后再确定性解析文件、符号和调用边。一个保存文档知识，一个保存代码结构投影；它们不应被概括成“另一种聊天记忆”。

## 1.2 Codex：Thread / rollout 事件与项目元数据

[Codex 固定提交 `c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)中，一次任务的持久原料是 Thread 对应的 rollout JSONL。它按发生顺序保留消息、工具调用与结果；Thread DB 则保存找到这条 rollout 所需的项目和生命周期信息。

```text
Thread / rollout
├─ user message
├─ assistant message
├─ tool call
├─ tool result
├─ root thread 中回流的 Agent 通信
└─ 运行控制事件与元数据

Thread metadata
├─ thread_id / source / rollout_path
├─ cwd / git branch / git commit
├─ created_at / updated_at / archived
└─ memory_mode
```

一条说明性记录可以写成：

```jsonl
{"type":"session_meta","thread_id":"th-42","cwd":"/repo/auth-service"}
{"type":"turn_context","git_branch":"fix/token-revoke","git_sha":"8c4a1d9"}
{"type":"message","role":"user","text":"先复现 refresh token 撤销失效"}
{"type":"tool_call","name":"exec","args":"pytest tests/test_refresh.py"}
{"type":"tool_result","call_id":"call-17","text":"1 failed, 8 passed"}
{"type":"message","role":"assistant","text":"跨实例需要共享 revocation store"}
```

rollout 保存的是原始事件序列，不是已经整理好的 Memory。它也可能包含 SessionMeta、TurnContext、WorldState、Compacted marker 或 developer 内容；第 2 层 Phase 1 会从中选择 user/assistant、tool call/result 和 root-thread Agent 通信，过滤运行控制记录、developer message 与完整 AGENTS/Skill 注入，并进行 secret redaction 和长度预算。换言之，第一层保存的事件集合比真正送入抽取模型的集合更宽。

项目元数据不是装饰。若过去结论是“本地 Map 可用”，cwd、branch 与 commit 能说明它发生在哪个仓库和版本；没有这些条件，Phase 2 很容易把一次旧分支经验写成全局规则。Thread/rollout 的输出在第 2 层变成 Phase 1 的单任务候选，同时继续作为可回查的原始证据。

## 1.3 前沿输入案例：视觉观察、世界/设备状态与 Computer Use 事件流

近期系统没有替换对话—工具主干，而是增加了三种无法只靠文字回复还原的原始 payload。

### 视觉观察进入执行轨迹

[XSkill](https://arxiv.org/abs/2603.12056)把任务图片、工具调用、中间输出和文本推理交错保存。知识管理模型不只看到“调用了 rotate”，还要看到“图像倒置”这一视觉状态如何触发旋转，以及旋转后观察怎样改变下一步。于是输入单元更接近：

```text
image observation
→ reasoning / tool call
→ transformed image / tool result
→ next decision
→ task outcome
```

这些视觉状态在第 6 层会通过多路径对照形成 Experience 与 Skill；在第一层，它们仍只是带时间顺序的原始观察和动作证据。

### 世界、对象或设备状态与动作反馈

[WorldLines](https://arxiv.org/abs/2606.18847)的长时家庭轨迹同时包含 dialogue、action、execution feedback、object/device state change。比如“用户说关灯”只是意图，`switch_off(lamp)` 是动作，设备状态从 `on` 变成 `off` 才是结果；稍后另一个观察又可能表明灯被重新打开。论文的 ObsMem 进一步保存 observer/visibility 和 action-native state trail，使系统能区分直接观察、他人报告和动作后的状态。

这类输入随后可形成当前世界状态及历史版本；若只保留自然语言摘要，“现在是什么”和“曾经发生过什么”会被压成同一句话。

### Computer Use / Computer History 的跨应用操作流

[OpenAI Computer History](https://learn.chatgpt.com/docs/customization/computer-history)从用户允许的应用与网站建立 interaction-event stream。事件可以包括 click、typing、keyboard shortcut、app switch，以及 macOS accessibility 暴露的文字和上下文；系统周期性把事件形成文本摘要和本地 Markdown Memory。它明确不把 screenshot、microphone input 或 system audio 写入 history。

```text
9:00  打开任务列表并检查状态
9:10  在文档中比较项目反馈
9:20  更新 launch plan 与说明
      ↓
“Prepared a launch update” 活动摘要
+ 可供用户确认的 Skill/automation 建议
```

这里新增的不是一轮 Agent 对话，而是用户在电脑上的行为流。它的输出仍要经过形成阶段，才会变成可回顾的时间线、Memory 文件或可复用 workflow。

下一层从这些原始输入继续：哪些片段值得保存，模型与确定性程序怎样把它们形成 L1/L2/L3、文件化 Memory 或 Skill。
