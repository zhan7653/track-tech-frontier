# GitHub Star Growth / Momentum 有界核验

> 结论：OSSInsight 历史与 bundle 内 GitHub 当前快照在本语料上不可稳定对齐，因此不能可靠复原 59 个仓库的可比 star growth；本 packet 不做增长排名。

生成时间：`2026-08-10T13:38:36Z`。输入为 radar 的 59 个仓库和其 GitHub 单次 stars 快照；历史来源为 [OSSInsight 官方 stargazers history API](https://ossinsight.io/docs/api/stargazers-history)。

## 覆盖审计

| 项目 | 结果 |
|---|---:|
| 仓库总数 | 59 |
| usable | 1 |
| qualified（仅诊断） | 3 |
| unavailable | 55 |
| OSS/GitHub 覆盖率低于 90% | 50 |
| OSS/GitHub 覆盖率高于 110% | 0 |
| HTTP 非 200 | 0 |
| 无有效历史行 | 7 |

三个已确认的失配样本已经足以说明问题不是可忽略的小误差：

| 仓库 | OSS 最新日期 | OSS 累计 | GitHub 当前快照 | 覆盖率 | 判定 |
|---|---|---:|---:|---:|---|
| `letta-ai/letta` | 2026-08-07 | 18,250 | 24,170 | 75.5% | qualified |
| `mem0ai/mem0` | 2026-08-07 | 40,047 | 62,901 | 63.7% | unavailable |
| `Sibyl-Labs/Sibyl-Memory` | 2026-06-14 | 5 | 98 | 5.1% | unavailable |

`latest_history_date` 是 API 返回的最后一个 star 事件日期，不等于 provider ingestion watermark。真正的可用性闸门是：响应结构有效、累计序列不下降、OSS 累计值与同一语料中的 GitHub 当前快照处于 90%–110%，且目标窗口基线存在。75%–120% 只保留为 qualified 诊断；超出即 unavailable。只有 strong coverage 下才输出 `delta90`/`delta12m`。这些阈值是误差容忍带，不是统计置信区间。

由于 OSSInsight 累计的是已记录 stargazer 事件，而 GitHub 快照是当前 active stars，两者定义本就不完全相同；大幅缺口还可能包含事件数据覆盖或仓库身份连续性问题。故不能用差额倒推出真实增长，也不能把缺口填成 0。

## 可替代的 current-attention 信号

以下只回答“最近是否有工程活动/新出现”，不回答质量、采用率或受欢迎程度增长：

- 90 天内新建：19/59；12 个月内新建：39/59。
- 90 天内有 push：54/59。
- 90 天内有 release：34/59。
- 90 天 commit 计数已观测：59/59；贡献者计数已观测：59/59。未知值没有写成 0。

90 天内新建且有 push 的仓库：

`Sibyl-Labs/Sibyl-Memory`, `xerj-org/xerj`, `JingxuanC/causal-memory`, `noamschwartz/atlas-memory-demo`, `mayiwen0212/MemChain`, `VictorTaelin/OptMem`, `zjunlp/LightMem-Ego`, `memorax-ai/memorax-code`, `Coding-Dev-Tools/engraphis`, `SMJAI/open-memory-protocol`, `Brain0-ai/brain0`, `MemTensor/OmniMemEval`, `tenurehq/precisionMemBench`, `MaxFreedomPollard/Compartment`, `AML-memory/agent-memory-leaderboard`, `Health-Yang/MineEcho`, `410979729/scope-recall-hermes`, `atomicstrata/atomicmemory`, `EverMind-AI/Raven`

90 天内有 release 的仓库：

`letta-ai/letta`, `mem0ai/mem0`, `Sibyl-Labs/Sibyl-Memory`, `memvid/memvid`, `xerj-org/xerj`, `NTU-Siqiang-Group/AsterVec`, `topoteretes/cognee`, `JingxuanC/causal-memory`, `aiming-lab/SimpleMem`, `volcengine/OpenViking`, `thedotmack/claude-mem`, `zjunlp/LightMem-Ego`, `basicmachines-co/basic-memory`, `campfirein/byterover-cli`, `Coding-Dev-Tools/engraphis`, `EverMind-AI/EverOS`, `TencentCloud/TencentDB-Agent-Memory`, `OWASP/www-project-agent-memory-guard`, `Brain0-ai/brain0`, `MemPalace/mempalace`, `supermemoryai/supermemory`, `headroomlabs-ai/headroom`, `DeusData/codebase-memory-mcp`, `tinyhumansai/openhuman`, `vectorize-io/hindsight`, `NevaMind-AI/memU`, `MemTensor/MemOS`, `MaxFreedomPollard/Compartment`, `neo4j-labs/agent-memory`, `mnemox-ai/tradememory-protocol`, `activeloopai/hivemind`, `410979729/scope-recall-hermes`, `atomicstrata/atomicmemory`, `EverMind-AI/Raven`

这些集合是筛选 lane，不是排序。后续深读仍应回到固定 SHA、架构、测试/CI、维护证据和独立 adoption 证据。

## 方法边界

- 前置限制（继承上游审计，本 packet 不重复探测）：自 2026-07 起，非协作者通过 GitHub REST/GraphQL 获取 stargazer history 的尝试返回 404 或空结果，因此不能把 GitHub 自身当作本轮历史补源。
- 单次请求：`per=day`, `2025-07-01` 至 `2026-08-10`，一次覆盖 12m 与 90d；未继续追逐替代历史供应商。
- GitHub 当前 stars 沿用 bundle 已固定的观测，不重新抓取、不声称增长。
- `usable` 也只代表可以计算有界 star-event delta；不代表仓库质量或真实 adoption。
- 跨仓库增长排名固定关闭（`ranking_eligible=false`），避免不同覆盖率、unstar 语义和历史缺口制造伪精度。
- raw 响应、请求 URL、UTC 与 SHA-256 均可从 `observations.jsonl` / `manifest.json` 回放核验。

## 官方来源

- [Stargazers history API](https://ossinsight.io/docs/api/stargazers-history)
- [OSSInsight Public API](https://ossinsight.io/docs/api)
- [OSSInsight source repository](https://github.com/pingcap/ossinsight)
