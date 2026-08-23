# Research brief

Topic: OpenAI Codex local memory system

As of: 2026-08-23

Mode: targeted rapid update to the existing Agent Memory v10 reader suite. The user explicitly requested one Codex report rather than a full field refresh.

Reader: technically literate reader who wants to reconstruct the implementation, not a feature list.

In scope:

- the open-source local CLI/App/IDE host path in `openai/codex`;
- thread eligibility, two-stage generation, SQLite state, file artifacts, read tools, citations and retention;
- boundaries with AGENTS.md, skills, Goal, compaction, subagents, Guardian and worktrees;
- current release/main delta, security controls, GitHub issues and unresolved engineering gaps.

Out of scope:

- model weights, training recipe, hidden server prompts and complete Codex cloud backend;
- executing Codex or a live user Memory store;
- adoption, performance ranking or configuration advice;
- a full refresh of the 2026-08-10 Agent Memory corpus.
