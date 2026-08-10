# MaxFreedomPollard/Compartment：固定提交工程深潜

**Cluster:** MM-C12  
**Selection:** keep-deep — Recent creation deeply inspected; engineering surface determines keep versus watchlist.

<!-- process:method -->

## 1. 为什么看它，以及不因为什么看它

它由新近性、当前活动、工程表面或历史谱系触发深读；累计 stars 只决定优先检查，不决定技术质量。所有判断固定在下列 commit，且本轮没有安装、测试或 benchmark execution。

<!-- process:limitation -->

## 2. 版本与维护快照

| Field | Observed value |
|---|---|
| Pinned commit | 3053e289eac7438ff8f58be17eb6b66bf57ff6e3 |
| Created / pushed | 2026-07-20 / 2026-08-09 |
| Freshness bucket | newly-created-90d |
| Release | v4.5.0 / 2026-08-02T09:47:32Z |
| License | Apache-2.0 |
| Setup / CI / tests / executed | documented / present / present / not-executed |
| 90d commits / contributors | 147 / 2 |
| Single snapshot stars / forks / open issues | 701 / 3 / 3 |
| Engineering surface | strong-surface (8/8) |

这个快照只支持“截至观察时的 repository surface/activity”。单次 stars、commit 数、contributors、open issues、release 或 CI presence 都不能单独推出增长、稳定性、性能或生产采用；PR 合并时延、issue close rate 和 bus factor 本轮没有测量。

<!-- process:limitation -->

## 3. 固定提交架构

Compartment 是本地加密 vault：MCP/hooks/CLI 捕获memory，bundled BGE-small ONNX在CPU生成384-d vectors，Store只在RAM中打开SQLite（records/vec windows/FTS5/relations/audit/meta），每record text/vector加密后整个数据库image被序列化进AEAD journal；查询在解锁后用exact或可选HNSW vector+FTS5 BM25做RRF。

| Component | Responsibility | Fixed-source locator |
|---|---|---|
| capture/MCP/CLI surface | 为多agent host提供memory_store/search/get/forget/link/lock及capture hooks | `GR-S046-R` — readmes/GRC046.md Agent-native/Commands/MCP tools |
| Vault/crypto journal | Argon2id keyslots、XChaCha20-Poly1305 record/vector encryption、append-sealed journal与lock/unlock | `GR-S046-R` — readmes/GRC046.md Security/lock model |
| in-memory SQLite Store | RAM-only records、embedding windows、FTS5、relations、audit/meta CRUD与serialization | `GR-S046-T` — src/compartment/store.py; blob 1c4fefa619cbf584b4e0e6ea57881ecfcd50dae4; sha256 5433e35593379777db66169e9d418cc5242ce03c16fc3f487ecdcf1e5140fc2e |
| embedding/vector index | bundled ONNX生成vectors；<20k exact SIMD，above threshold optional usearch HNSW，长记录多window | `GR-S046-T` — docs/MEMORY.md; blob a636991cb944fc2fc482a7dec61f4dd8aadc1610; sha256 57b869b4879ad94ffa30e088b26b3f3de398a9ec0abf271b6515ea6445542dcd |

这里的 component 关系来自固定 SHA 的代码、manifest 或文档定位；它不是按顶层目录猜架构，也不把 README 的能力宣称提升为运行事实。

## 4. Write → store/index → read → action 数据流

| Step | Operation | From → to | Fixed-source locator |
|---:|---|---|---|
| 1 | hook/MCP提交turn或显式memory_store，bundled model生成多window vectors | agent host → embedder/dedup | `GR-S046-T` — docs/MEMORY.md storage flow steps 1-2 |
| 2 | 每record随机key加密text/vector并由master key wrap record key | deduped memory → encrypted record fields | `GR-S046-T` — docs/MEMORY.md steps 3-5 |
| 3 | RAM SQLite写records/vecs/FTS/audit，serialize后AEAD seal到vault journal | Vault/Store → encrypted vault file | `GR-S046-T` — store.py insert/serialize; docs/MEMORY.md |
| 4 | query embed后exact/HNSW与BM25 RRF，按namespace/filter取row并解密返回 | RAM vector/FTS indexes → MCP/CLI recall | `GR-S046-T` — docs/MEMORY.md recall; store.py fts_search/all_vectors |

## 5. 真实依赖、服务与集成约束

| Dependency / service | Role | Fixed-source locator |
|---|---|---|
| PyNaCl + argon2-cffi | XChaCha20-Poly1305与key derivation | `GR-S046-T` — pyproject.toml blob 4c8c8aa9b2391e370b3822388b0ce76d479419c3; sha256 806a04f83d2c18782d43e807d71197f15676890d2196468de2cbe46acbc3a058 |
| onnxruntime + tokenizers + numpy | bundled local embedding与exact vector math | `GR-S046-T` — pyproject.toml dependencies |
| mcp >=1,<2 + optional usearch | stdio MCP surface；>20k HNSW extra | `GR-S046-T` — pyproject.toml dependencies/optional hnsw |

**Integration constraints:**

- mcp 2.0移除了项目导入的FastMCP路径，manifest硬限制<2；升级需先port server。 (`GR-S046-T` — pyproject.toml mcp dependency comment)
- vault记录embedding model SHA256并拒绝用不匹配模型打开；模型升级要显式reindex --re-embed。 (`GR-S046-T` — docs/MEMORY.md lines 151-157)
- 所有search在RAM中进行，vault必须先unlock且容量直接影响RSS/启动重载；多process写由advisory lock串行。 (`GR-S046-R` — readmes/GRC046.md measured/one vault many agents)

## 6. 维护、Issue / PR 可见性

- 2026-08-10 观察：rolling90d commits=147、unique contributors=2、open issues snapshot=3；release v4.5.0；CI/tests 存在。 (`GR-S046-O` — observations.jsonl/repositories.jsonl GRC046)
- open issues snapshot=3；PR latency、issue close-time、安全响应SLA未测。 (`GR-S046-O` — observations.jsonl GRC046)

## 7. 项目特定失败模式

| Failure mode | Trigger | Impact | Evidence / inference boundary |
|---|---|---|---|
| model hash mismatch | 更换/损坏embedding model | vault拒绝打开，需显式re-embed以避免混合空间 | GR-S046-T; inference=false |
| vault journal/auth failure | 密文截断、tamper或错误passphrase/keyfile | AEAD验证失败，memory不可用；恢复取决于journal/backup | GR-S046-R, GR-S046-T; inference=true |
| unlocked host compromise | OS/进程在vault解锁期间被完全攻陷 | RAM plaintext/master material可被读取；文档明确不能防护fully compromised OS | GR-S046-T; inference=false |
| foreign-write reload race | 多agent processes连续写且lock/reload检测失败 | 旧image覆盖新journal或暂时读stale state | GR-S046-R; inference=true |

## 8. 放回簇内后的设计判断

**本项目要回答的簇级决策：** write source、provenance、quarantine、read scope、action authorization 与 repair 是否全链连接。

**首要失败风险：** 持久投毒、间接 prompt injection、跨租户泄漏、撤销/删除未传播。

这个判断以第 3–7 节的项目特定 component、flow、dependency、constraint 与 failure records 为基础；它不把项目孤立排名，也不从 stars 或目录存在推导质量。

## 9. 采用边界与仍未知

无必需云服务、可作为个人本地vault，但本次未验证第三方生产adoption或安全审计；README latency/security表格是项目方陈述，未测。

本轮没有保留独立公开代码引用；这不证明外部采用不存在。

**Unknowns:**

- PR latency 未测
- issue close-time 未测
- 第三方security audit未知
- 独立adoption未验证
- 大vault reload/backup recovery SLO未测

## 10. 可推翻的验证计划

1. 在固定 commit 和记录的 manifest 下重放 setup/tests；失败就把 documented/present 降级为 partial/missing。
2. 重放 untrusted write→store→retrieve→tool action→repair/delete，并计 false block、latency、cost。
3. 固定 model/agent/data/budget，与无 memory、raw context 或同簇替代实现做 matched comparison；同时保存 latency、token、storage、failure 和 security trace。
4. 复核 release migration、issue/PR 维护和至少一个独立部署；没有这些证据就保持 adoption abstention。

## 11. 固定提交原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

At the 2026-08-10T05:15:41Z GitHub snapshot, MaxFreedomPollard/Compartment was created 2026-07-20, last pushed 2026-08-09, pinned at 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, had 701 cumulative stars, and had latest release v4.5.0 on 2026-08-02; the star count is one snapshot and is not growth evidence.
<!-- claim:GR-C046-1 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, the inspected engineering surface for MaxFreedomPollard/Compartment was setup=documented, CI=present, tests=present, license=Apache-2.0, and execution=not-executed; tree absence means only ‘not found in the inspected tree’, never zero implementation.
<!-- claim:GR-C046-2 -->

The repository's own GitHub metadata describes MaxFreedomPollard/Compartment as: “Encrypted, fully offline agentic memory. One click install, GUI w/ memory map, all OS and agents. Superior memory creation, storage…”
<!-- claim:GR-C046-3 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, fixed-source inspection of MaxFreedomPollard/Compartment supports this project-specific architecture reading: Compartment 是本地加密 vault：MCP/hooks/CLI 捕获memory，bundled BGE-small ONNX在CPU生成384-d vectors，Store只在RAM中打开SQLite（records/vec windows/FTS5/relations/audit/meta），每record text/vector加密后整个数据库image被序列化进AEAD journal；查询在解锁后用exact或可选HNSW vector+FTS5 BM25做RRF。 The repository was not executed in v09.
<!-- claim:PRJ-A012 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, MaxFreedomPollard/Compartment has these inspected dependencies or services: PyNaCl + argon2-cffi: XChaCha20-Poly1305与key derivation; onnxruntime + tokenizers + numpy: bundled local embedding与exact vector math; mcp >=1,<2 + optional usearch: stdio MCP surface；>20k HNSW extra. Its recorded integration constraints are: mcp 2.0移除了项目导入的FastMCP路径，manifest硬限制<2；升级需先port server。; vault记录embedding model SHA256并拒绝用不匹配模型打开；模型升级要显式reindex --re-embed。; 所有search在RAM中进行，vault必须先unlock且容量直接影响RSS/启动重载；多process写由advisory lock串行。. These are static fixed-source findings, not execution results.
<!-- claim:PRJ-I012 -->

At pinned commit 3053e289eac7438ff8f58be17eb6b66bf57ff6e3, the inspected repository tree for MaxFreedomPollard/Compartment exposed these architecture or integration locations: docs, install, integrations, packaging, skills, src, tests, tools; this is code-surface evidence and the repository was not executed in v09.
<!-- claim:PRJ-C012 -->

At the 2026-08-10T05:15:41Z GitHub/API snapshot for MaxFreedomPollard/Compartment, the inspected rolling-90d window contained 147 commits and 2 unique contributors, while open issues were 3; these are maintenance-activity signals only, and v09 did not measure pull-request latency, issue-close rate, bus factor, or production adoption.
<!-- claim:PRJ-M012 -->

<!-- synthesis:PRJ-S12 claims:GR-C046-1,GR-C046-2,GR-C046-3,PRJ-A012,PRJ-I012,PRJ-C012,PRJ-M012 clusters:MM-C12 -->

<!-- process:limitation -->
