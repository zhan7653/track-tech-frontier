# Deep Agents：临时模型上下文、共享 Backend 与显式 State 过滤

**固定版本：** [`langchain-ai/deepagents@23b83ad`](https://github.com/langchain-ai/deepagents/tree/23b83ad50f63d241d0069a3dc426d43b211adf2e)  
**观察：** 2026-08-24；release `deepagents==0.7.8`；MIT。未执行测试。

## 结论

Deep Agents 的 `task` tool启动 ephemeral/stateless Subagent，但“stateless”只描述其 message history。Parent 与 Child默认使用同一个 backend；除 `messages/todos/structured_response` 和标记为 private 的字段外，Parent custom state会复制给 Child，Child的非私有 state update也可回流 Parent。因此模型上下文隔离、runtime context传播、共享文件和长期 memory是四个不同面。

## Parent → Child

[`SubAgentMiddleware`](https://github.com/langchain-ai/deepagents/blob/23b83ad50f63d241d0069a3dc426d43b211adf2e/libs/deepagents/deepagents/middleware/subagents.py)生成 `task(description, subagent_type)`。tool描述明确每次 invocation stateless，只看详细 task prompt，返回一个 final report。

实际 state构造会从 `runtime.state`复制所有非 `_EXCLUDED_STATE_KEYS` 且非 `PrivateStateAttr`字段，然后把 `messages`替换成单一 Human task。Parent callbacks、metadata和 configurable context通过 LangGraph ambient config传播。若应用把 secret放在普通 custom state而没有标 private，它会进入 Child。

## Tools、permissions 与 backend

Raw SubAgent默认继承 Parent tools；可单独覆盖。Filesystem permission若缺省继承 Parent，若提供则完整替换。所有内联 Subagent的 `FilesystemMiddleware`接收与 Parent相同的 backend对象；这使 Child可通过文件协作，也意味着 context quarantine不自动隔离文件。

默认 backend是 thread-scoped `StateBackend`。`CompositeBackend`按最长 path prefix路由，例如将 `/memories/`转到 `StoreBackend`，其他 scratch file留在 StateBackend。route prefix被剥离后传给目标 backend，因此逻辑路径相同但物理 namespace由 backend factory决定。

## Child → Parent

Child完成后，middleware优先序列化 `structured_response`，否则寻找最后一个非空 AI message。返回 `Command`会把 Child非私有、非 excluded state fields一并 update到 Parent，再加入一条 ToolMessage。多个 Child同时更新带非交换 reducer的 Parent field可能冲突，应用必须定义 reducer/ownership。

## Memory Middleware

[`MemoryMiddleware`](https://github.com/langchain-ai/deepagents/blob/23b83ad50f63d241d0069a3dc426d43b211adf2e/libs/deepagents/deepagents/middleware/memory.py)按给定 AGENTS.md paths读取完整内容、去 HTML comments并注入 system fragment。prompt明确 memory可能旧、错误或非当前用户写入，并指示使用 `edit_file`及时更新、禁止凭证。

Memory本身是文件语义；持久性来自 backend。Parent `memory=`不会自动复制到自定义 Subagent middleware；但 Parent/Subagent共享 backend，Subagent可通过 filesystem tools访问相同路由。是否 always-load由每个 Agent middleware stack决定。

## 依赖、测试与失败模式

依赖 LangChain Agent middleware、LangGraph state/store、pluggable backend和 optional sandbox。仓库有 Subagent、async Subagent、memory multiturn、ContextBench、MemoryAgentBench和 permission tests。

项目特有失败：custom state未标 private会下传；默认 inherited tools/permissions可能过宽；shared backend产生并行写；Memory always-load扩大 prompt和注入面；`StoreBackend` namespace若只用 assistant id会跨用户共享；structured final只保留 Child声明的证据。反转需要上层应用的 state schema、backend namespace和 reducer证明更严格隔离。
