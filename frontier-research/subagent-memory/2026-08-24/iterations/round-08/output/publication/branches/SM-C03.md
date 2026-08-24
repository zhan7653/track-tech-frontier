# 共享协作底座：黑板、结构化状态、日志与服务

## 问题与权威状态

多个 Agent 需要共同看到进展，但“共同看到”可以指完全不同的对象：消息、当前值、append-only 事件、文件、patch、trajectory 或编译后的 active memory。底座的首要问题是**哪个对象是权威状态**，索引和摘要只是访问面还是也能直接改写事实。

## 方案族及内部流程

### 自然语言黑板

Agent 将计划、发现和结果追加到共同文本区，其他 Agent 读取并继续。表达自由、接入简单，适合早期协作；但重复、冲突、部分完成和权限通常交给模型自行解释。黑板有内容不等于 Agent 会检索它，也不等于最新一条就是正确值。

### Typed key/value 或 JSON state

共享对象有 schema、key、timestamp、writer 和 status。Agent 可以 update 某字段，订阅 key 变化，或读取 bounded view。`memX` 等工程候选代表 REST/WebSocket/pub-sub 形状。Last-write-wins 可保证确定性，却会隐藏语义冲突；schema 只能保证结构，不保证事实支持。

### Validated patch blackboard

[PatchBoard](https://arxiv.org/abs/2605.29313)让 Architect 生成 task schema 和 role write contract，worker 只看到 context slice，并返回 JSON Patch。kernel 在临时副本上检查 operation、path、schema 和 invariant，通过后事务提交；拒绝也进入 log 但不污染 committed state。scheduler 只消费 committed event。

其 ALFWorld 作者实验显示 shared blackboard 本身不是全部收益：plain/structured blackboard 控制仍低于完整 PatchBoard；去掉 patch/schema interface 或 context slicing 是最大消融之一。另一方面，false claim 是独立 fault 类，提醒 structural validity 不等于 semantic truth。

### Append-only episode log + compiler

Agent 先追加不可变 observation/episode，另一个 compiler 去重、抽取、解决冲突并产生 active view：

```text
episodes (authoritative evidence log)
→ compile/admit/supersede
→ active typed memories
→ search/context projection
```

这保留重放和重新解释能力，也把 write-to-visible latency、compiler version、重复执行和 recovery 变成系统职责。Statewave 是待固定版本核验的工程候选。

### Shared files / Git-like artifacts

文件适合代码、研究笔记和 human review。路径天然提供 namespace，Git 提供 branch/diff/history；但并行 Agent 仍需 worktree、merge、lock 或 single writer。一个 Markdown “handoff” 可以是明确 packet，也可能退化为无人维护的全局状态堆。

### Memory service / control plane

独立服务统一 API、MCP、credential、scope、search、provenance、notification 和 lifecycle。它能跨机器/框架连接 fleet，代价是控制面、数据库、队列、异步 enrichment、迁移和所有 handler 的权限一致性。Governed Shared Memory 暴露的 GET/search 与 dedup/contradiction ordering 正是此形状的特有风险。

## 方案比较

| 底座 | 权威对象 | 并发语义 | 重放 | 主要风险 |
|---|---|---|---|---|
| 文本黑板 | 文本/消息 | 隐式 | 弱 | 冲突和检索全交给模型 |
| Typed state | 当前对象 | LWW/CAS/lock | 中 | 结构正确、语义错误 |
| Validated patch | committed state + log | transaction | 强 | schema/validator 成本 |
| Episode+compiler | immutable episode | append + async compile | 强 | 延迟和双层一致性 |
| Files/Git | artifact history | branch/merge | 强 | 路径权限与 merge 冲突 |
| Control plane | versioned records | 服务策略 | 取决于日志 | 多 path 能力漂移 |

## 当前研究在改变什么

前沿正在把 blackboard 从“共享一段上下文”升级为带验证、来源和 commit 状态的协作数据库，同时重新发现 event sourcing、patch、CRDT 和 Git 的语义。尚缺跨底座的统一 object model，以及真实系统中 crash recovery、消息重复、partial commit 和长期 schema migration 的独立证据。


## 证据账本绑定

共享底座已经覆盖对象引用、文件/Backend、checkpoint/store、Redis 当前值和多服务数据库，但这些实现对权威状态、历史、通知和恢复的语义不同，不能用“shared memory”一个标签互换。
<!-- synthesis:SY-C03 claims:R5-C008,R5-C011,R5-C014,R5-C017 clusters:SM-C03 -->
