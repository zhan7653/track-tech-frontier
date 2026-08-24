# Round 01 输入

- 自动查询：arXiv 2 条、Crossref 2 条、GitHub Search 6 条。
- 人工 Web Pilot：论文、GitHub、Benchmark、LangGraph 与 OpenAI Agents SDK 共 9 条查询。
- 失败路线：Semantic Scholar 2 条查询在重试后仍为 HTTP 429；失败和局部 raw response 已保存。
- 输入规模：1,644 条 discovery occurrence，去重为 1,569 个 entity。
- 启发式候选：575 个，其中论文 143、仓库 432；仅用于人工 triage。
- 人工映射：28 个改变初始地图的 entity。

完整查询和 raw snapshot 位于 bundle 根 `queries.jsonl`、`discovery_results.jsonl` 与 `work/round-01/pilot/`。
