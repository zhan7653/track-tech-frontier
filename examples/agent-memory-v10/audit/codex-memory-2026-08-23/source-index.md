# Codex Memory 来源索引

## 官方实现与产品资料

- [`openai/codex@c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)：固定源码树、README、workspace manifest。
- [Phase 1 extractor](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase1.rs)：rollout 过滤、抽取、redaction 和 Stage 1 输出。
- [Phase 2 consolidator](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/phase2.rs)：全局 job、内部 Agent、sandbox 和提交。
- [File storage](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/storage.rs) 与 [workspace validation](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/workspace.rs)：Markdown 工件、Git baseline、symlink 和 artifact check。
- [Memory read extension](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/ext/memories)：summary 注入、list/read/search/ad-hoc note 和路径边界。
- [MemoryStore](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/src/runtime/memories.rs) 与 [Memory DB migration](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/memory_migrations/0001_memories.sql)：候选、usage、lease、watermark 和 selection。
- [release `rust-v0.149.0`](https://github.com/openai/codex/releases/tag/rust-v0.149.0)：最新稳定发布边界。
- [OpenAI Docs — Memories](https://learn.chatgpt.com/docs/customization/memories)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、[Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)：当前公开产品语义。

以上官方实现、release 和文档属于同一 OpenAI/Codex 证据家族，不作为多个独立投票来源。

## 负面与边界资料

- [#26684 concurrent Phase 2 selection drift](https://github.com/openai/codex/issues/26684)
- [#40110 background Memory worker runaway](https://github.com/openai/codex/issues/40110)
- [#18343 scoped Memory management](https://github.com/openai/codex/issues/18343)
- [#30299 inspect/prune/delete/scope controls](https://github.com/openai/codex/issues/30299)
- [#39272 custom provider Memory support](https://github.com/openai/codex/issues/39272)

这些是当前 issue 状态和用户报告；除非与固定源码结构直接吻合，否则不视为已复现事实或发生率证据。

## 独立研究

- [Bad Memory: Evaluating Prompt Injection Risks from Memory in Agentic Systems](https://arxiv.org/abs/2607.14611)：2026-07-16 v1 预印本，合成 sandbox 中对 Codex/Claude Code 的作者实验。它支持持久 Memory 改变 prompt-injection threat model，不支持生产发生率或对当前固定提交全部防线的归因。

完整结构化来源、局限和 independence groups 见 [sources.jsonl](sources.jsonl)。
