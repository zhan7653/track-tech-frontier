# Codex 本地 Memory 定向调研审计

这是 Agent Memory v10 的一次单项目 rapid update，不是全领域增量发现。

- 读者报告：[OpenAI Codex 本地 Memory 系统](../../reader/projects/openai--codex.md)
- 固定仓库：[`openai/codex@c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)
- 最近稳定 release：[`rust-v0.149.0`](https://github.com/openai/codex/releases/tag/rust-v0.149.0)
- 官方产品边界：[OpenAI Docs — Memories](https://learn.chatgpt.com/docs/customization/memories)
- 来源索引：[source-index.md](source-index.md)
- 截止时间：2026-08-23

已检查的代码面包括 `memories/write`、`memories/read`、`ext/memories`、独立 Memory SQLite migrations、thread eligibility、Phase 2 job/selection、app-server reset、Guardian 与 feature/config 边界。没有执行仓库，也没有读取任何用户真实 Memory 文件。

证据等级：官方固定提交、官方文档和官方 release 为主要证据；GitHub issues 只作为用户报告和故障线索；`Bad Memory` 是外部预印本，结论限定于作者的合成实验。

验证文件：`sources.jsonl`、`repositories.jsonl`、`repository_observations.jsonl`、`repository_engineering_profiles.jsonl`、`claims.jsonl`、`evidence.jsonl`、`semantic_checks.jsonl` 与 `deliverables.jsonl`。
