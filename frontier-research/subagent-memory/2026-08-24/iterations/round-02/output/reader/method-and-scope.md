# 方法、范围与当前证据边界

## 独立研究与基准

本研究以 `examples/agent-memory-v10` 固定版本作为读者效果和工程深度的最低基准，但不复制其分支结构。Round 01 先运行多路线 Pilot，从输入推导七个 Subagent-specific 分支；Round 02 的 runtime 文档进一步新增 Subagent-local persistence and identity 分支。

## Round 01–02 输入

Pilot 运行 arXiv、Crossref、GitHub Search 和 web/official-domain search。Semantic Scholar 两条查询在配置重试后仍返回 HTTP 429，失败和一份局部 raw response 已保留。

Round 01 自动导入形成 1,644 条 discovery occurrence 和 1,569 个去重 entity。Round 02 再运行 38 条可重放查询，新增 5,247 次 occurrence，并补充 20 条产品、负面、adoption 和 gap-directed web 查询。当前累计为 79 条查询、6,898 次 discovery occurrence、4,292 个去重 entity，其中 2,230 篇论文、2,057 个仓库和 5 个产品文档实体；3,329 个实体落在最近 12 个月，1,565 个落在最近 90 天。

Round 02 启发式高召回 triage 标出 1,878 个候选，其中 668 篇论文、1,210 个仓库；经过高信号规则、最高分检查和两个分数带各 80 项的固定种子抽样，当前 mapped population 为 170 个实体。筛选分数只指导 map-stage 工作，不表示质量、成熟度或采用。数字只说明输入层，不证明覆盖完成。

## 证据层

- **Discovered：** 搜索发生和 provider metadata，只用于扩展与候选筛选。
- **Mapped：** 已确认身份、范围相关性和机制分支，用于技术地图。
- **Deep-verified：** 打开原始论文、固定代码或官方文档，并建立 claim/evidence 后才可支撑高风险结论。

Round 01–02 读者页主要使用保守的机制综合和明确链接，尚未把 mapped 候选全部晋升为 deep-verified。后续轮次会严格核验数字、版本、安全、采用和重要比较；一般性架构解释保持逻辑完整而不把每句话拆成审计记录。

## 时间边界

- 当前实践与必要前置材料：截至 2025-08-24；
- 最近 12 个月：2025-08-25 至 2026-08-24；
- 最近 90 天：2026-05-27 至 2026-08-24；
- 截止日后的 provider metadata 进入 future/invalid bucket。

## 范围边界

只有承担跨 Agent 状态继承、共享、提交、检索、回流或演化职责的消息、workspace、RAG、checkpoint、event log、task queue 和通用 Agent Memory 才纳入。相邻技术略写。报告不提供推荐架构和技术选型。

## 当前限制

广度查询仍有术语噪声，尤其 Crossref 的社会科学 collective memory、GitHub 的小型新项目和应用论文中偶然出现的 memory 词；Semantic Scholar 仍受 429 限制。尚未完成引用闭包、作者/组织路线、完整 Benchmark 指纹、产品 Release 检查、源码固定版本分析和独立采用调查。adoption 搜索以第一方和自述案例为主，不能支持采用率结论。当前主流与趋势判断因此仍是阶段性、限定于已映射输入的分析。
