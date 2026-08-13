# Causal Memory：将原始会话、事实与因果边分开保存

[JingxuanC/causal-memory](https://github.com/JingxuanC/causal-memory) 是近期、规模较小但结构上有信息增益的例子。它尝试把“发生过什么”“可被召回的事实”与“某个决定带来了什么结果”放在同一 SQLite 骨架中，却不把它们混为同一记录。其关键设计是写时 gatekeeping：原始 session log 可保留以供审计，只有蒸馏后的 facts/causal edges 进入主要召回层。

**固定观察。** 提交为 [`054af36`](https://github.com/JingxuanC/causal-memory/tree/054af36507537f7b616fa41db07be483cc6e55c3)，仓库 2026-07-26 创建，2026-08-10 有 push，已观察 `v0.3.1` release；滚动 90 天有 163 commits、2 位贡献者和 9 个 open issue。Apache-2.0、CI、测试可见。30 stars 是单次快照，尤其不应被读作成熟度。

## 从日志到“为什么”的实现层次

[`store/write.rs`](https://github.com/JingxuanC/causal-memory/blob/054af36507537f7b616fa41db07be483cc6e55c3/crates/causal-memory/src/store/write.rs) 写 `session_logs`、`agent_facts`、`causal_edges`、supersede 状态和 embedding blob。`distill.rs`、`consolidate/` 与 `hippocampus/` 负责每 session 的抽取、SWR 式整合，以及图上的正/负激活；[`store/retrieve/`](https://github.com/JingxuanC/causal-memory/tree/054af36507537f7b616fa41db07be483cc6e55c3/crates/causal-memory/src/store/retrieve) 分别提供 BM25、semantic、entity hop、trace 和 RRF 融合。

1. Agent/MCP 的 session 或直接写入先落到 typed input 与 `session_logs`。
2. 每个 session 的 distill 使用一次 LLM 调用抽取 facts 和 decision→outcome edges；失败时不写 done marker，因此原日志仍可供重试。
3. 写入维护 BM25 与可选 embedding；更新某事实会先 retire 旧值再写新值。
4. 查询分别在事实和因果层取候选，`search_memory` 以 RRF（文档列出 `k=60`）汇合成回答可用的 memory lines。

固定版本的[架构文档](https://github.com/JingxuanC/causal-memory/blob/054af36507537f7b616fa41db07be483cc6e55c3/docs/architecture.md)支持这条链。它说明因果边是代码中的对象，不证明这些边在真实任务中都可靠。

## 依赖与接入范围

单文件 SQLite 由 `rusqlite` 承担；`reqwest`/`tokio` 用于 HTTP LLM/embedding；可选 `fastembed` 在本地加载 BGE-small 的 ONNX embedding。固定版本只提供 MCP stdio，README 明确 HTTP transport 尚未实现，因此网络服务接入要另加 wrapper。开启 local embedding 需要可动态加载的 ONNX Runtime 和首次模型下载；改用 HTTP endpoint 又转而依赖 endpoint/model 配置。

## 特有的错误路径

**蒸馏未完成。** LLM 或解析失败时，raw log 存在但 facts/causal recall 不完整；不写 done marker 让重试成为可能。

**语义通道退化。** ONNX 动态库、模型下载或 HTTP endpoint 出错时，semantic channel 不可用或退回 BM25；退化后的效果尚未执行验证。

**错误类比被放大。** 相似、重复或矛盾挖掘若在弱证据上建立跨任务 meta-edge，typed spreading activation 可能放大错误的 lesson transfer。这是设计结构推断出的风险，也在项目限制描述中有相应提示。

## 维护与未知

近期有提交、release、CI 和测试，但维护集中度较高；未测 PR/issue 响应、HTTP 服务形态、独立采用、线上规模或 benchmark 重放。README 分数和“测试数量”属于作者陈述，不是本研究执行结果。

**证据边界。** 本页只分析提交 `054af36` 的静态 Rust 代码、架构文档、manifest 和 2026-08-10 快照。
