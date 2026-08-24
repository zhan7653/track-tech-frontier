# Statewave Multi-Agent Memory Demo：外部 Runtime 的 Episode→Compile→Context 集成

**固定版本：** [`smaramwbc/statewave-multi-agent-memory@7f16415`](https://github.com/smaramwbc/statewave-multi-agent-memory/tree/7f16415176f7a8cc5ead659a7e8ee09fa031ce76)  
**观察：** 2026-08-24；无 GitHub release；Apache-2.0。该仓库是 demo/client，非 Statewave runtime源码；未执行外部服务。

## 结论

项目清楚展示三个 API：append raw episode、compile subject、retrieve token-bounded context。但 conflict extraction、Jaccard/supersession和 ranking实际位于外部 `statewave-client`连接的服务，不在本仓库。因此本报告能深入分析集成与并发边界，不能把 README算法主张当作本仓库代码实现。

## 组件与数据流

```text
three analyst tasks
→ deterministic candidate builder from local source JSON
→ Statewave create_episode(subject, metadata.memory_candidates)
→ compile_memories_wait(subject)
→ list/search memories and compute before/after diff
→ SSE memory_update to browser
→ get_context(subject, question, max_tokens)
→ synthesis Agent receives assembled_context
```

`AsyncStatewaveClient`是 SDK薄封装；`statewave_tools.py`提供同步 `remember/compile/recall`。`server.py`用FastAPI启动 analyst并通过 SSE广播；synthesis只看到 external runtime返回的 active context。

## 并发真实边界

[`agents/analyst.py`](https://github.com/smaramwbc/statewave-multi-agent-memory/blob/7f16415176f7a8cc5ead659a7e8ee09fa031ce76/agents/analyst.py#L112)显式用一个 `asyncio.Lock`串行化 `post → compile → diff`。代码注释说明 compile会处理该 subject全部 uncompiled episodes；若两个 Agent race，可能 double-compile并产生 duplicate memories/diffs。

这与 README“compile idempotent”的概括存在张力：demo本身仍需要应用级 lock。该 lock只在单进程内有效，跨 process/host需要 runtime transaction/idempotency提供保证，本仓库无法验证。

## Conflict demo 与来源

三份 source JSON故意构造 Stripe旧/新价格；candidate builder是 deterministic，不调用 LLM。README描述 external compiler用词重叠/Jaccard阈值和时间顺序 supersede旧值；runtime实现不可见。`get_memory_diff`只根据 before ids和 after status分类 new/superseded/unchanged，不验证 supersession理由。

## 依赖、测试与维护

依赖外部 Statewave API/SDK、FastAPI、OpenAI-compatible synthesis、SSE和前端。仓库 tests只覆盖 candidate construction与 diff分类，未覆盖真实 compile、auth、network retry和跨进程 race；无 release，最近 push在 2026-08-17。

项目特有失败：external service不可审计；single-process lock；固定 subject使所有 analyst共享一个 namespace；compiled active context可能隐藏 losing claim，只能通过 timeline审计；synthesis信任 assembled context；README与代码 extraction方式不同。反转需要打开同版本 runtime/server源码或执行 external API的并发和conflict测试。
