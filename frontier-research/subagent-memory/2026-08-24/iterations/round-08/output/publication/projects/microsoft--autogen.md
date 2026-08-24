# AutoGen：Agent Model Context、外部 Memory 与 Team Snapshot 的分离

**固定版本：** [`microsoft/autogen@027ecf0`](https://github.com/microsoft/autogen/tree/027ecf0a379bcc1d09956d46d12d44a3ad9cee14)  
**观察：** 2026-08-24；latest Python release `python-v0.7.5`（2025-09-30）；CC-BY-4.0。默认分支最后 commit在 2026-04；未执行测试。

## 结论

AutoGen把三类状态分开：`ChatCompletionContext`是 Agent内部消息状态；`Memory`是外部 component，在每次 inference前自行检索并修改 model context；Team snapshot按 participant name保存所有 Agent与 manager state。Assistant `save_state()`只保存 model context，不包含外部 Memory backend内容，所以恢复 Team不等于恢复共享 Memory的一致快照。

## Agent 数据流

[`AssistantAgent.on_messages_stream`](https://github.com/microsoft/autogen/blob/027ecf0a379bcc1d09956d46d12d44a3ad9cee14/python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py#L900)执行：incoming/handoff messages写入 model context → 依次调用每个 Memory的 `update_context()` → LLM inference → assistant/tool results继续写 context。HandoffMessage还能把其 `context` items直接加入接收 Agent。

[`Memory` protocol](https://github.com/microsoft/autogen/blob/027ecf0a379bcc1d09956d46d12d44a3ad9cee14/python/packages/autogen-core/src/autogen_core/memory/_base_memory.py#L60)只规定 `update_context/query/add/clear/close`和 MIME/metadata；存储、检索、scope、排序、权限和去重完全由实现决定。多个 Memory按序修改同一 context，顺序会影响最终 prompt。

## Local persistence

Assistant Agent在多次 `on_messages` 调用间保留 model context。`save_state()`导出 `AssistantAgentState.llm_context`，`load_state()`覆盖它；`reset()`只 clear model context。外部 Redis/Chroma/Mem0/ListMemory不在这个 payload中，它们有自己的 lifecycle。

## Team snapshot

[`BaseGroupChat.save_state()`](https://github.com/microsoft/autogen/blob/027ecf0a379bcc1d09956d46d12d44a3ad9cee14/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py#L748)通过 runtime保存每个 participant和 group manager，并用 Agent name作为 key以便跨 runtime portable。manager state可含 message thread/current turn/previous speaker，Magentic-One还含 task/facts/plan/stall count。

代码警告 running team上调用 save可能得到 inconsistent state；load时要求所有 name存在且 team不得 running。Agent改名、重复 name或不同 team结构都会影响恢复。远程 Agent通过 runtime save/load，仍不保证它依赖的外部 database在同一时间点冻结。

## 依赖与集成

- AgentChat teams/group managers；
- Core runtime/message topics；
- model context variants（unbounded/buffered/token-limited）；
- Memory implementations（Redis、Chroma、Mem0、canvas等）；
- handoff/team tools；
- external state persistence由应用负责。

## 测试、维护与失败模式

仓库有 agent/team state、model context、Memory protocol和多个 backend tests。当前 default branch较观察日不算新，最新 Python release也早于多项 2026 runtime文档，报告不把历史 Star解释为当前采用。

项目特有失败：Memory backend未随 Team snapshot保存；running save不一致；name-key portability可能碰撞；多个 Memory顺序改变 context；外部 Memory可把相同内容重复注入长 context；Handoff context可能绕过普通消息筛选。反转需要应用层 transaction或 snapshot protocol将 team state、Memory store与外部 side effect绑定。
