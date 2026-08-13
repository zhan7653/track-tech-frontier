# Engraphis：单一 SQLite 权威库与可重建检索层

[Coding-Dev-Tools/engraphis](https://github.com/Coding-Dev-Tools/engraphis) 把多个常被拆散的机制收进本地实现：记忆记录、FTS、双时间历史、图/代码链接和内容无关 receipt 都在一个 SQLite 文件中；向量索引则是可替换的 companion。它说明“本地优先”不等于只有文本搜索，也不等于不处理版本、冲突和上下文预算。

**固定观察。** 检查提交为 [`128fe05`](https://github.com/Coding-Dev-Tools/engraphis/tree/128fe0515b842923df871a777eaacc3327f40513)。仓库 2026-06-30 创建，快照时最新 push 为 2026-08-10、release 为 `v1.5`；滚动 90 天有 348 次提交、4 位贡献者、0 个 open issue，且有 Apache-2.0、CI、测试。0 open issue 和 153 stars 都只是某时刻的状态，不能单独证明维护质量或增长。

## 内部关系：一个权威库，多个读出视图

[`MemoryService`](https://github.com/Coding-Dev-Tools/engraphis/blob/128fe0515b842923df871a777eaacc3327f40513/docs/ARCHITECTURE_V3.md) 将 Smart/Classic MCP、REST、dashboard、CLI 连接到同一 scope/write/recall 语义；[`MemoryEngine`](https://github.com/Coding-Dev-Tools/engraphis/blob/128fe0515b842923df871a777eaacc3327f40513/engraphis/core/engine.py) 编排写入、冲突、演化、保留、召回、context pack 与 privacy/audit。SQLite 保存 records、FTS、图、双时间历史和 receipts。默认向量后端是 NumPy exact scan；`sqlite-vec` 是可选加速。代码图会按内容 hash 增量更新 symbols 和 code edges。

这种结构的要点是：向量空间不是唯一真相。若 embedding 身份变化，系统可以禁止持久向量召回，要求重建，而不是将不同模型的向量混进同一空间。

## write → store/index → read/use

1. MCP、REST、CLI 或资源 adapter 调用 Service；Engine 校验 scope、secret 和 provenance，生成 record。
2. Engine 做 embedding、去重、冲突/演化处理后，把 memory、history、FTS、graph 和 receipt 写入同一 SQLite 文件。
3. 向量后端 upsert embedding；代码资源则更新 code graph。两者都服务于权威记录，而不是取代它。
4. 查询融合 lexical、vector、graph、code 信号，rerank 后在硬 token 预算内打包为提示上下文与证据。

上述路径来自固定提交的[架构文档](https://github.com/Coding-Dev-Tools/engraphis/blob/128fe0515b842923df871a777eaacc3327f40513/docs/ARCHITECTURE_V3.md)、`engine.py` 和相关 backend。它描述可见设计，不表示本研究已测得检索质量。

## 依赖与接入限制

核心依赖仅为 NumPy；FastAPI/Uvicorn、SentenceTransformers、MCP、sqlite-vec、tree-sitter、psycopg、SQLCipher 都通过 extras 提供。这样可以保持最小本地路径，也让不同安装组合产生不同功能表面。

持久向量空间要求可验证的 embedding fingerprint；若模型、revision 或远端身份不可固定，检索会 fail-closed 直到 rebuild。另一个具体限制是 `sqlite-vec` 与 SQLCipher 的 native SQLite 库不能安全地在同进程组合：自动配置会退回 NumPy，显式要求 `sqlite-vec` 则会报错。开源仓不含 hosted team identity/automation 服务，不能由源码存在推断托管能力。

## 具体失败模式

- embedding 指纹不匹配时，系统故意关闭持久向量召回；这是防止混合向量空间的保护，同时也使迁移必须显式完成。
- sqlite-vec 与 SQLCipher 同时加载时，性能加速和进程内加密不能同时按预期工作。
- record 可能已经存在却不满足 prompt eligibility，或调用方传错 workspace/repo/session，导致召回为空；这更像 scope/review 问题，而不必然是索引损坏。

## 维护与未知

项目有近期开源活动、release、CI 与测试，但团队规模、PR 时延、跨向量后端迁移、独立采用和 hosted 实现都没有被核实。这里可确认的是本地 engine 的代码边界，不能把 README 的自测或 hosted 描述提升为生产性能结论。

**证据边界。** 本页基于提交 `128fe05` 的静态源码、manifest、README/架构文档和 2026-08-10 快照；未运行迁移或 backend 组合。
