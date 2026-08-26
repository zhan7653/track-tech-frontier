# 第 3 层：状态、存储与索引

形成后的 Memory 通常同时存在于三种状态中：可回放的原始/历史记录、当前权威正文或对象、为查找而建立的派生索引。索引命中不等于正文，当前视图也不等于完整历史；这一层的重点是把三者放对位置。

## 3.1 TencentDB：JSONL/Markdown、数据库、FTS/vector/graph、Wiki、CodeGraph

[TencentDB Agent Memory `0aff21a`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a)使用的物理原语并不神秘：文件、结构化数据库、全文/向量索引和关系图。它的工程形状来自不同 Memory 对象如何组合这些载体。

| 对象 | 原始、历史或权威正文 | 当前结构状态 | 查找投影 |
|---|---|---|---|
| L0 | `conversations/YYYY-MM-DD.jsonl` | DB 中的当前消息视图 | L0 FTS；可选 vector |
| L1 | `records/YYYY-MM-DD.jsonl` 的追加版本/恢复记录 | DB 中 current record、scope、version | L1 FTS；可选 vector |
| L2 | `scene_blocks/*.md` | 文件元信息 | 可从 Markdown 重建的 `scene_index.json` |
| L3 | `persona.md` | team+agent 当前 Persona | 无检索索引；新 Session 直接读取 |
| Skill | 不可变 version row + `SKILL.md`/supporting files | `is_head`、status、manifest、content hash | active head 的 FTS；可选 vector |
| Wiki | Markdown 页面 | Wiki/source metadata | FTS/BM25、page metadata、Wikilink edges |
| CodeGraph | 某 repo/branch/commit 的代码快照 | resource status、commit、stats | files、symbols/nodes、call/dependency edges |

### 同一条 L1 为什么有三份形态

一条 L1 “缺陷修复前建立失败测试”首先追加到 JSONL，保留来源消息、时间和版本，作为历史与恢复依据；DB current row 只表达当前可见内容；FTS/vector 则是可重建的查询入口。发生 update/merge 时，历史继续追加，新 current row 与索引被替换。因此“还能在历史里找到旧版本”和“应用查询会返回旧版本”是两回事。

### Wiki：正文、全文入口和页面关系

Wiki 的知识正文在 Markdown 页面中。每个 Wiki 的索引库保存 `page_meta`、FTS/BM25 与由 `[[Wikilink]]` 抽出的 `graph_edge`；搜索结果先返回 title/snippet/links，Agent 再按路径读页面正文。图表达页面关系，不替代页面内容；标准 Agent search 默认从 BM25 页面种子开始，也不因为库里有边就自动执行多跳图查询。

```text
wiki/concepts/jwt-authentication.md  ← 权威页面
        │ title + body
        ├─→ FTS/BM25
        └─→ [[token-revocation]] → graph_edge
```

### CodeGraph：仓库 commit 的关系投影

CodeGraph clone 指定 branch、记录 commit，再解析 files、symbols/nodes 和调用/依赖 edges。首次 `indexAll` 建立全量投影，之后 `sync` 处理变化文件。`search` 可以按名称找节点，`callers/callees/impact` 才沿关系边读取。CodeGraph 能说明“索引时这版代码的结构”，实际修改前仍需以当前 workspace source 为准。对应载体可从 [MemoryCore store](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a/MemoryCore/src/core/store)与 [Wiki index engine](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/0aff21a/MemoryKnowledge/src/engines/wiki)继续定位。

## 3.2 Codex：rollout JSONL、state/memories DB、Markdown 与 Git baseline

[Codex `c9b19deb`](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29)没有预建向量或图索引。它把原始经历、后台候选和 Agent 可读状态放在不同载体：

| 载体 | 保存什么 | 是否是新 Thread 的主要读取面 |
|---|---|---|
| rollout JSONL | user/assistant、tool call/result 与任务证据 | 否；最深层来源 |
| `state_5.sqlite` | Thread ID、source、cwd、branch、commit、updated_at、memory mode、rollout path | 否；来源发现与定位 |
| `memories_1.sqlite` | Phase 1 candidates、usage、selection，以及 Phase 1/2 jobs/watermarks | 否；形成与调度账本 |
| `memory_summary.md` | 首行 `v1` 的短导航 | 是；新 Thread 直接获得 |
| `MEMORY.md` | 跨 rollout 聚合的偏好、项目知识、流程和失败屏障 | 是；按需 search/read |
| `rollout_summaries/*.md` | 单次任务摘要和 `rollout_path` | 是；需要证据时渐进读取 |
| `skills/` | 可复用程序与配套工件 | 是；按需读取 |
| `raw_memories.md` | 被选 Phase 1 `raw_memory` 的机械物化 | 否；Phase 2 输入 |
| Git baseline | 上一次成功 Phase 2 与当前工作区之间的 diff 基线 | 否；增量形成和续跑边界 |

SQLite 中有候选不表示文件已经形成；文件已经形成也不表示当前 Agent 已经搜索并读到。Codex 的“索引”主要是生成式短导航 `memory_summary.md`、Markdown 的标题/关键词，以及查询时对普通文本做即时词法扫描。详细读取协议在第 5 层说明。

这套组合保留了一条清楚的回查链：

```text
memory_summary.md
→ MEMORY.md 中的 task group 与 Sources
→ rollout_summaries/<slug>.md
→ rollout_path 指向的原始 JSONL
```

Git baseline 也不是面向读者的逐事实历史。它让下一次 Phase 2 看见物化输入与正式文件发生了什么变化；Codex 没有为每条事实建立 stable identity 与独立 revision node。候选 schema 与文件物化分别见 [Memory migration](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/state/memory_migrations/0001_memories.sql)和 [storage.rs](https://github.com/openai/codex/blob/c9b19deb09c1841ce7acc33ddb96276030936a29/codex-rs/memories/write/src/storage.rs)。

## 3.3 双时间版本图：stable identity、immutable revision、valid time、transaction time

[A Graph-Native Bitemporal Memory Store](https://arxiv.org/abs/2607.26520)针对覆盖更新的两个问题：旧内容被抹掉，以及“事实何时成立”与“系统何时知道”被混成一个 `updated_at`。

它把一个稳定 Memory identity 连接到不可变 version nodes；每个版本保存两条闭开时间区间：

- **valid time**：内容在现实世界中何时成立；
- **transaction time**：该版本何时被数据库记录并对系统可见。

```text
MemoryIdentity: office_location
├─ HAS_VERSION → v1 "上海"
│                 valid [-∞, 7/10)
│                 transaction [7/1, 7/13)
└─ HAS_VERSION → v2 "杭州"
                  valid [7/10, +∞)
                  transaction [7/13, +∞)
```

例子中，用户 7 月 10 日搬到杭州，却到 7 月 13 日才告诉系统：

| 查询 | 时间语义 | 答案 |
|---|---|---|
| 根据当前完整证据，7 月 11 日现实中的办公室在哪里？ | valid-time historical query | 杭州 |
| Agent 在 7 月 11 日运行时，当时系统知道什么？ | transaction-time as-of query | 上海 |
| 现在在哪里？ | current query | 杭州 |

更新不覆盖 v1，而是追加 v2、关闭旧区间并移动 current view。论文原型使用 agent-local Neo4j property graph、HNSW vector index 和版本化节点；真正改变状态能力的是 stable identity 与双时间 schema，而不是“用了图数据库”。它让 current、现实历史和系统认知历史都可查询，但不自动解决 identity resolution、自然语言时间抽取或来源真伪。版本冲突如何选择、派生状态怎样修订，在第 4 层继续。
