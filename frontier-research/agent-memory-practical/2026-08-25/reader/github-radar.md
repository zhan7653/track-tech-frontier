# GitHub 雷达兼容入口

本报告只把能改变实现理解的仓库放入正文。入选依据是组织/项目身份、可读代码或官方文档、固定版本路径和实际机制；Star 只负责剔除明显低关注噪声。

| 项目 | 证据身份 | 正文用途 |
|---|---|---|
| [OpenAI Codex](https://github.com/openai/codex/tree/c9b19deb09c1841ce7acc33ddb96276030936a29) | OpenAI 官方仓库，固定 commit | 两阶段形成、文件化读取和反馈锚点 |
| [Microsoft Agent Framework Azure Cosmos Memory](https://github.com/microsoft/agent-framework/blob/main/python/packages/azure-cosmos-memory/README.md) | Microsoft 官方仓库，main README | cadence 抽取、分类、TTL、去重和 user/thread scope |
| [Neo4j Labs Agent Memory](https://github.com/neo4j-labs/agent-memory) | Neo4j Labs community 项目，官方仓库/README；页面复核时约 488 stars（2026-08-25） | 图状态、实体去重、reasoning trace、vector/text 检索 |
| [LangGraph Store](https://github.com/langchain-ai/langgraph/tree/f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f) | LangChain 官方仓库固定 commit | namespace/key、可选 semantic index 和 TTL |
| [Caura](https://github.com/caura-ai/caura/tree/54dd6d4f2075ca428b1f3a5a8c50114351ea4755) | 可检查固定 commit | 多租户权威 row 与派生检索面 |

Star 只用于去掉明显低关注噪声；仓库代码、文档、固定版本和维护边界才是正文证据。完整 Codex 工程路径见[Codex 完整说明](codex-complete.md)。
