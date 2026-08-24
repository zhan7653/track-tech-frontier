# OpenAI Codex：Thread Fork、共享 Workspace 与 Root-only Memory Formation

**固定版本：** [`openai/codex@2161ec2`](https://github.com/openai/codex/tree/2161ec272a7d6b775c9c721e6206f4fe63e383f2)  
**树：** `7472d7e85f527e57957db52acd9aa676b2725ae9`；2026-08-23 17:02Z。Apache-2.0。Windows 长路径 checkout 失败后，以短路径 no-checkout clone + `git show` 固定 blob；未运行代码。

## 结论

Codex 的 Subagent 是独立 thread，不是 Parent context 内的普通 tool worker。当前 v2 `spawn_agent` 默认 full-history fork，也支持 no-history 和 last-N-turns；所有 Agent 在当前桌面工作模式下共享目录/文件系统。Codex 本地 Memory 形成管线则显式跳过 non-root Agent。结果是一个不对称结构：Child 可以继承历史和共享工程状态，但不会独立触发 startup memory extraction；其成果主要通过消息回到 Parent，再由 root thread 的后续状态和 Memory 管线决定是否长期保留。

## Spawn 与身份

[`spawn_agent` handler](https://github.com/openai/codex/blob/2161ec272a7d6b775c9c721e6206f4fe63e383f2/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs)解析 `fork_turns`：省略/`all` 为 FullHistory，`none` 不 fork，正整数字符串为 LastNTurns。它计算 child depth，构造 canonical `AgentPath`，保存 parent thread/turn/root turn、environment selections、role/model/effort snapshot，并用 `AgentCommunication` 把任务消息触发为 Child turn。

Full-history fork 通常继承 Parent model/effort；role 或非 full fork可以应用单独模型设置。Child 仍能 spawn 自己的 Child，身份通过路径而不是显示 nickname决定。

## Shared workspace 与显式通信

内置 multi-agent usage hint 明确所有 Agent 共享 current working directory 和 filesystem，所以 worktree/锁/文件 ownership 不由 spawn 自动提供。消息、follow-up、wait 和 final delivery 是显式通信面；status notification 以结构化 `agent_path/status` 注入 Parent context。

这意味着工程状态有两个渠道：thread history fork 与共享文件。后者是权威工件但也会产生同时编辑、读到半成品和秘密共享；前者可选择 LastN/none，但不能隔离 filesystem。

## Memory 写入为何是 root-only

[`start_memories_startup_task`](https://github.com/openai/codex/blob/2161ec272a7d6b775c9c721e6206f4fe63e383f2/codex-rs/memories/write/src/start.rs)在三个条件下直接返回：ephemeral、MemoryTool disabled、`source.is_non_root_agent()`。只有 eligible root session 会做 prune、rate-limit check、Phase 1 thread extraction 与 Phase 2 consolidation。

因此 Child rollout 不会作为独立 startup candidate 被长期提炼。这避免每个探索 Agent 自动污染全局 Memory，也可能丢失只存在于 Child thread、未充分回报 Parent 的知识。

## Memory 读取与共享范围

[`MemoriesExtension`](https://github.com/openai/codex/blob/2161ec272a7d6b775c9c721e6206f4fe63e383f2/codex-rs/ext/memories/src/extension.rs)按 feature + `use_memories` 向 thread 注入 Memory developer instructions；该 contributor 本身没有 `is_non_root_agent` 判断。物理根仍是同一 `CODEX_HOME/memories`。代码可见事实是“写 startup 有 root guard，读 contributor无同样 guard”；是否每个 spawn config 最终启用读取还受 thread config/Memory mode影响，不能仅从 contributor 推出所有 Child 必然读取。

从系统形状看，Codex没有 per-Subagent memory namespace：共享长期资产以 project/cwd 等逻辑字段约束，而不是按 AgentPath 物理分库。

## Child → Parent → 长期记忆

Child `final` 立即通过通信面返回 Parent；Parent 将其综合进自己的 thread和工程工件。若该消息进入 root rollout，未来 root Memory extraction可能间接吸收 Child 结论——这是基于通信与 root-only formation 的系统推断，不是显式 `promote_subagent_memory` API。当前代码未显示一条带 evidence/schema/replay gate 的 Subagent-result→Memory commit协议。

## Guardian、Goal 与边界

Guardian处理高风险 action/approval，Goal维持跨 turn objective/accounting；它们与 Memory 是独立 extension/state machine。Guardian能控制动作，不会自动核验 Child 写入的每条长期知识；Goal持久化目标，也不等于技术事实 memory。

## 测试、维护与未知项

仓库在观察时有大量 Subagent notification、Guardian authorization、thread memory mode、memory reset 和 startup tests。固定 commit 比先前 Memory 专报的新快照更晚；本报告只分析 Subagent/Memory交界，完整本地 Memory架构另见 Agent Memory v10 的 Codex报告。

项目特有未解决问题：Child output 的 provenance/verification 在 Parent 综合中可能被压缩；共享 cwd 可能污染 sibling；root-only formation 会漏掉不回传的发现；共享 physical Memory缺少 AgentPath scope；full-history默认会放大攻击继承面。反转需要代码/测试证明单独的 Child result admission、per-Agent namespace 或默认 workspace隔离已经存在。
