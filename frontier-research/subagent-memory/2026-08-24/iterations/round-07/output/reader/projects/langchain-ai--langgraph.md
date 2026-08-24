# LangGraph：Checkpointer、Subgraph Namespace 与跨 Thread Store

**固定版本：** [`langchain-ai/langgraph@f09cfe8`](https://github.com/langchain-ai/langgraph/tree/f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f)  
**观察：** 2026-08-24；latest release `sdk==0.4.3`；MIT。未执行测试。

## 结论

LangGraph 提供的是通用 durable state primitive，而不是一套 Subagent Memory policy。它将 Checkpointer 定义为 graph/thread 的版本化短期状态，将 Store 定义为可跨 thread 的 hierarchical namespace KV/semantic store。Subagent 持久化由 graph compile flag、thread id 和 node namespace组合决定；谁有权读写、什么应该写入和如何合并语义冲突仍由应用负责。

## 三种 Subgraph retention

[`StateGraph.compile`](https://github.com/langchain-ai/langgraph/blob/f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f/libs/langgraph/langgraph/graph/state.py#L1179)定义：

- `checkpointer=False`：不使用/不继承 checkpoint；
- `checkpointer=None`：作为 Subgraph时继承 Parent checkpointer，支持 interrupt/resume，但不同 invocation重置局部 state；
- `checkpointer=True`：拥有持久 namespace，同一 `thread_id` 跨 invocation 累积。

`thread_id` 是 checkpoint检索 key；复用表示累积，唯一值表示独立 run。测试 [`test_subgraph_persistence.py`](https://github.com/langchain-ai/langgraph/blob/f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f/libs/langgraph/tests/test_subgraph_persistence.py)固定了这些语义，并验证不同 wrapper node name 生成独立 namespace。Child显式使用自己的 thread id 时，应保留自己的 namespace而不是继承 Parent task namespace。

## Checkpoint 数据流

```text
graph state + channel versions + pending sends/writes
→ CheckpointSaver.put / put_writes
→ keyed by thread_id + checkpoint namespace
→ interrupt/resume/replay/fork
```

Checkpointer 能保留同一 superstep 的 pending writes，便于部分节点成功、一个节点失败后恢复；它不自动使 external API/tool side effect 幂等。

## Store：跨 Thread Memory

[`BaseStore`](https://github.com/langchain-ai/langgraph/blob/f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f/libs/checkpoint/langgraph/store/base/__init__.py#L708)使用 `(namespace tuple, key)` 保存 JSON object，支持 get/search/put/delete/list namespaces。semantic index默认关闭，只有配置 embedding 后才生效；TTL默认也关闭，adapter必须显式支持。

```text
namespace=(tenant/project/assistant/user/...)
key=memory id
value=JSON document
optional index fields + TTL
```

Store 可以共享给不同 thread/Subagent，但它没有内置 access policy、provenance、conflict state 或 Agent identity schema。`delete`是 put a tombstone/None 到 adapter API；底层物理语义取决于实现。

## 工程边界

- checkpoint backends：memory、SQLite、Postgres及 conformance suites；
- store backends：in-memory、SQLite/Postgres，optional vector search；
- runtime：Pregel supersteps、StateGraph reducers、interrupt；
- subgraph identity：thread id + checkpoint namespace + node path；
- long-term identity：任意 namespace tuple，由应用构造。

## 测试、维护与失败模式

仓库包含专门的 sync/async subgraph persistence、namespace isolation、checkpoint migration、pending writes和 store conformance tests。高维护活跃度与测试存在不等于应用层 Memory 安全。

项目特有失败包括：复用 thread id导致意外记忆混合；同名 stateful subgraph并行调用会争用 namespace；Store namespace未纳入 auth会越权；checkpoint state与外部 Memory store分离会产生 snapshot不一致；semantic search/TTL在adapter间能力不同。反转需要上层 runtime提供并验证统一主体、权限、commit和删除协议。
