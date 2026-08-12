# Compartment：本地加密 Memory vault 的工程边界

[MaxFreedomPollard/Compartment](https://github.com/MaxFreedomPollard/Compartment) 把安全边界直接放进存储与检索路径：MCP、hooks 和 CLI 采集记忆，内置 ONNX 模型在本机生成向量，记录与向量被逐条加密，整个内存 SQLite 映像再封入 AEAD journal。它不是通用多租户服务，而是一个以本地解锁 vault 为中心的设计。

**固定观察。** 检查提交为 [`3053e28`](https://github.com/MaxFreedomPollard/Compartment/tree/3053e289eac7438ff8f58be17eb6b66bf57ff6e3)。仓库 2026-07-20 创建、2026-08-09 有 push、release 为 `v4.5.0`；滚动 90 天可见 147 commits、2 位贡献者和 3 个 open issue。Apache-2.0、CI、测试可见；701 stars 只是新项目的一次关注快照。

## 加密不是写完后才附加的一层

[`store.py`](https://github.com/MaxFreedomPollard/Compartment/blob/3053e289eac7438ff8f58be17eb6b66bf57ff6e3/src/compartment/store.py) 在 RAM 中打开 SQLite，管理 records、向量 windows、FTS5、relations、audit、meta 与序列化。项目的 [Memory 文档](https://github.com/MaxFreedomPollard/Compartment/blob/3053e289eac7438ff8f58be17eb6b66bf57ff6e3/docs/MEMORY.md) 描述由内置 BGE-small ONNX 生成 384 维向量；小规模使用 exact SIMD，超过阈值可选 usearch HNSW，长记录按多个窗口处理。Vault 层用 Argon2id 和 XChaCha20-Poly1305：每条 record 的文本/向量以随机 record key 加密，再由 master key 包装；SQLite image 最终作为 append-sealed journal 密封。

1. Hook、MCP 或 CLI 提交 turn/显式 `memory_store`，并做 embedding 与去重。
2. 文本和向量加密，记录写入 RAM SQLite 的 records、vecs、FTS 与 audit。
3. Store 序列化后封入加密 vault 文件；解锁后才可重建内存状态。
4. 查询也在解锁后的 RAM 中完成：query embedding 走 exact/HNSW 与 FTS5 BM25 的 RRF，随后按 namespace/filter 解密返回。

这使静态 vault 文件具有强封装，但检索和明文使用期的风险没有消失。

## 依赖与使用约束

[`pyproject.toml`](https://github.com/MaxFreedomPollard/Compartment/blob/3053e289eac7438ff8f58be17eb6b66bf57ff6e3/pyproject.toml) 包含 PyNaCl、argon2-cffi、onnxruntime、tokenizers、NumPy、`mcp >=1,<2`，以及可选 usearch。这个 MCP 上限是实质兼容性限制：MCP 2.0 移除了代码使用的 FastMCP 路径，升级需先改 server。

vault 记录 embedding 模型 SHA-256，模型不匹配时拒绝打开；升级模型需显式 `reindex --re-embed`。所有搜索在 RAM 中进行，因此 vault 必须先 unlock，容量影响 RSS 与启动重载；多进程写通过 advisory lock 串行化。

## 失败与安全边界

- 模型 hash 改变或损坏会阻止打开 vault，这避免混合向量空间，却把升级变成显式运维事件。
- journal 截断、篡改、错误 passphrase/keyfile 会导致 AEAD 验证失败；恢复能力依赖备份和 journal 状态，本研究未做恢复演练。
- 完全被攻陷的已解锁 OS/进程可读取 RAM 中的明文或密钥材料；项目文档明确不承诺防护这种情形。
- 多 Agent 连续写入时，若 reload/lock 检测出现竞态，可能看到旧映像覆盖新 journal 或短暂读到陈旧状态；这是基于设计的推断，未进行并发实验。

## 维护与未知

本地、无必需云服务的特征可由代码确认，但不等同于经过第三方安全审计或已验证生产使用。未测大 vault 的 reload/backup 恢复 SLO、issue/PR 响应或多进程压力；README 的安全/延迟表也只是项目方陈述。

**证据边界。** 本页基于提交 `3053e28` 的静态源码、manifest、文档及 2026-08-10 快照；没有解锁真实 vault、运行模型或审计密码学实现。
