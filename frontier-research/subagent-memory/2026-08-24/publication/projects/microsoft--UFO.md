# Microsoft UFO：Host/App Agent 共享 Blackboard 的真实代码边界

**固定版本：** [`microsoft/UFO@96983c7`](https://github.com/microsoft/UFO/tree/96983c73ed09e884a5f1d7ff8936c953b234b684)  
**观察：** 2026-08-24；release `v3.0.8`；MIT。未执行 GUI/runtime测试。

## 结论

UFO实现了清晰的两层 memory：每个 Agent有 step-wise短期 `Memory`，Host与其 AppAgent通过同一个 `Blackboard`对象共享 questions、requests、trajectories和screenshots。当前代码是内存 list + 全量 prompt序列化，没有检索、权限、版本或冲突处理。文档称 Blackboard可 file-backed跨 session，但在固定代码中只找到显式 `to/from_dict`和 questions JSONL preload，未找到通用自动持久化调用；因此该能力保留为文档声明而非代码事实。

## 组件与对象

[`MemoryItem`](https://github.com/microsoft/UFO/blob/96983c73ed09e884a5f1d7ff8936c953b234b684/ufo/agents/memory/memory.py)是动态字段对象，`Memory`只是按 step append/filter/delete的 list。它用于 Agent execution trace。

[`Blackboard`](https://github.com/microsoft/UFO/blob/96983c73ed09e884a5f1d7ff8936c953b234b684/ufo/agents/memory/blackboard.py)内部四个 `Memory`：

- questions：用户问答；
- requests：历史请求；
- trajectories：按配置 `history_keys`选择的 action/decision字段；
- screenshots：metadata、path、base64 image。

HostAgent构造一个 Blackboard；AppAgent虽有 fallback实例，但其 `blackboard` property在绑定 Host后返回 `host.blackboard`。共享来自对象引用，不是分布式 database。

## 写入与读取

Host/App processor的 memory update strategy将当前 step打成 `MemoryItem`，再选取 history keys追加到 Blackboard；AppAgent可按模型决定保存 screenshot。

```text
step context / parsed response / action result
→ agent MemoryItem
→ select configured history keys
→ host.blackboard.trajectories.append
→ optional screenshot base64 append
→ blackboard_to_prompt dumps all questions/requests/trajectories/images
→ next Host/App model call
```

`blackboard_to_prompt`没有 top-k、time filter或token budget；所有 list被 `json.dumps`，所有 screenshots逐个进入 prompt。历史增长与图片体积直接进入 context成本。

## 状态与持久化边界

代码提供 `blackboard_to_dict/json` 与 `blackboard_from_dict`，但仓库内未找到除定义外的调用。`load_questions`可从配置 JSONL预载 QA。因而当前可确认的是 session内共享与可手工序列化；文档中的“file-backed persistence”缺少本次固定代码的自动保存/加载路径。

## 并发、权限与失败

Blackboard没有 lock、version、writer id、scope或 status。Host/App在一个 Python process顺序运行时通常足够；若并行写，list append顺序由 runtime调度决定。`add_data`遇到不支持类型只打印 warning；processor update异常也多记录 warning，不阻止继续运行。

`MemoryItem._memory_attributes`在基础类是 class-level mutable list，动态字段会成为同类所有实例的可序列化字段集合；缺失值可能以 `None`进入后来 item。这是灵活 schema的代价。

## 依赖、测试与维护

依赖 UFO Host/App Agent state machine、GUI automation、prompt processors与截图文件。仓库有 state machine unit/integration tests，Blackboard本身未见专门 concurrency/persistence test。当前 release与 commit都在 2026-08-10，工程活跃。

项目特有失败：全量 prompt膨胀、base64 screenshot成本、无 scope/permission、无 conflict、文档/代码 persistence差距、并行顺序不可审计。反转需要固定版本展示自动持久化、bounded retrieval或同步控制的实际调用路径。
