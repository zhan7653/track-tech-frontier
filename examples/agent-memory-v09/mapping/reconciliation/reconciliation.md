# v09 Mapping Reconciliation

物化时间：`2026-08-10T05:00:00Z`。本文件记录 broad corpus → mapped field DAG 的确定性裁决；`deep-candidate` 没有被改成 `deep-verified`。

## 决策顺序

1. Mapper `exclude` 保持 EXCLUDE。
2. Mapper `defer` 或非 exclude 的 future metadata 进入 HOLD，不参与 mapped、freshness 或 cluster count。
3. 应用 planner 的 23 条 map/deep-candidate → exclude demotion；23 条 identity/date/lineage defer 被显式确认 HOLD。
4. 最后应用独立抽查的 20 条 override；冲突时抽查裁决优先。
5. 对剩余 mapped entities 用 113 个 frozen exact aliases 归并到 16 个 canonical leaves；secondary 去重，roots 通过 DAG 继承。

## 输入锁定

- post-freshness entities：3,128；SHA-256 `db4eadf4d4f01a52ea0e75b4628910e72944a5e74c8a552e3ca76294eeb701e5`
- mapper proposals：3,128；SHA-256 `a216ee2ac95168c032fd39de0e7d99acba841fdca82d2f66a13be1de7bba4679`
- proposal/entity ID 一一对应；全部 113 个 observed natural labels 均由 exact alias table 覆盖。

## 最终 population

- mapped：**1312**（papers 689；repositories 623）
- HOLD/defer：**102**
- exclude：**1714**
- rolling 12m mapped：**1065**；rolling 90d mapped：**551**；future mapped：**0**

Planner-only 口径原为 1,318 mapped。应用 audit 后的净变化为 -6：新增排除 7、kernel-memory 转 HOLD 1、PHILIA 与 Long-Term-Memory-API 晋级 2；memanto 与 MemoryBear 只从 deep-candidate 降为 map，不改变 mapped 数。

Planner 文字稿中的 rolling 12m/90d 数为 1,068/553；用冻结的 post-hardening entity windows 逐 ID 重算后，planner-only 与 audit-final 都是 1,065/551。audit 在 recent windows 的删除与晋级净额为 0，因此这里采用可重放语料计算值，不沿用文字稿估计。

## Canonical DAG

5 个 structural roots + 16 个 leaves；C01–C14 标为 important，C15 为 model-native boundary，C16 为 integration/support view。每个 mapped entity 恰有一个 primary leaf，可有去重 secondary memberships。

| Cluster | Primary | All memberships |
|---|---:|---:|
| MM-C01 — Memory Services & Control Planes | 171 | 238 |
| MM-C02 — Agent-Memory Storage & Indexing | 31 | 55 |
| MM-C03 — Structured, Relational & Temporal Memory | 99 | 287 |
| MM-C04 — Retrieval, Ranking & Active Navigation | 25 | 90 |
| MM-C05 — Lifecycle, Consolidation & Forgetting | 116 | 378 |
| MM-C06 — Experience, Procedural Memory & Skills | 110 | 274 |
| MM-C07 — Working Context, Compression & Cost Control | 35 | 101 |
| MM-C08 — Personalization, Identity & Conversational Continuity | 81 | 210 |
| MM-C09 — Coding, Project & Environment Memory | 119 | 170 |
| MM-C10 — Embodied, Multimodal & World-State Memory | 110 | 250 |
| MM-C11 — Shared, Distributed & Portable Memory | 90 | 203 |
| MM-C12 — Security, Privacy, Integrity & Governance | 121 | 183 |
| MM-C13 — Evaluation, Benchmarks & Comparability | 117 | 284 |
| MM-C14 — Foundations, Theory & Taxonomies | 27 | 73 |
| MM-C15 — Model-Native / Parametric Memory Boundary | 24 | 36 |
| MM-C16 — Application/Framework-Embedded Memory | 36 | 36 |

`cluster_coverage.jsonl` 在本阶段只表达 mapped-corpus presence：有候选记为 `partial`，没有候选记为 `gap`；future window 一律 `not-applicable`。它不冒充 deep coverage。详细 mapped counts 在 `coverage-counts.jsonl`。

## 审计材料

- `canonical-aliases.json`：完整 exact alias 与 canonical cluster metadata。
- `planner-demotions.jsonl`：23 条 planner demotions。
- `planner-holds.jsonl`：23 条显式 identity/date/lineage HOLD。
- `audit-overrides.jsonl`：20 条最高优先级独立抽查 overrides。
- `decision-ledger.jsonl`：3,128 条逐实体裁决链。
- `coverage-counts.jsonl`：cluster × lane × window 的 mapped-corpus counts。

## 一致性

- audit_precedence_applied: `PASS`
- cluster_dag_acyclic: `PASS`
- count_conservation: `PASS`
- future_not_mapped: `PASS`
- hold_exclude_unassigned: `PASS`
- mapped_exactly_one_primary: `PASS`
- mapped_stage_events_complete: `PASS`
- no_deep_verified_stage: `PASS`
- one_screening_per_entity: `PASS`
- secondary_assignments_deduplicated: `PASS`

## Bundle output hashes

- `bundle/cluster_assignments.jsonl`: `9519d30994e29761497aa6eb25c710aa8a334027e7b1b638b8d96e02d0de4bd6`
- `bundle/cluster_coverage.jsonl`: `ec29c482b1b3409928604eb14de3ad934008547dd1f5d4a8f5b1498b2beb91fd`
- `bundle/clusters.jsonl`: `543eb9d70ac6a26b3ec8c1bbd152fdbbd3a3979ff92834defc794e527adc74e1`
- `bundle/entities.jsonl`: `02033fd86f1c35a4ac4443457fd66e4a87b3d10291ab85f8da686d5659928c99`
- `bundle/screening.jsonl`: `09a0d5b7bfb23e5aad915ac50ef4b49819f6dc79c3783be8f8350f2871755489`
- `bundle/stage_events.jsonl`: `d882a446bf041419134dbce19fbbd19bbde3c5e20b66341f7be0ca2720d31ecc`
