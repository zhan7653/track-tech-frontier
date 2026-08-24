# 方法、范围与当前证据边界

## 独立研究与基准

本研究以 `examples/agent-memory-v10` 固定版本作为读者效果和工程深度的最低基准，但不复制其分支结构。Round 01 先运行多路线 Pilot，从输入推导七个 Subagent-specific 分支；Round 02 的 runtime 文档进一步新增 Subagent-local persistence and identity 分支。

## Round 01–07 输入与吸收

Pilot 运行 arXiv、Crossref、GitHub Search 和 web/official-domain search。Semantic Scholar 两条查询在配置重试后仍返回 HTTP 429，失败和一份局部 raw response 已保留。

Round 01 自动导入形成 1,644 条 discovery occurrence 和 1,569 个去重 entity。Round 02 再运行 38 条可重放查询，新增 5,247 次 occurrence，并补充 20 条产品、负面、adoption 和 gap-directed web 查询。当前累计为 79 条查询、6,898 次 discovery occurrence、4,292 个去重 entity，其中 2,230 篇论文、2,057 个仓库和 5 个产品文档实体；3,329 个实体落在最近 12 个月，1,565 个落在最近 90 天。

Round 02 启发式高召回 triage 标出 1,878 个候选，其中 668 篇论文、1,210 个仓库；经过高信号规则、最高分检查和两个分数带各 80 项的固定种子抽样，当前 mapped population 为 170 个实体。筛选分数只指导 map-stage 工作，不表示质量、成熟度或采用。数字只说明输入层，不证明覆盖完成。

Round 03 建立分支 × lane × 时间窗口诊断矩阵，对继承、局部持久化和 population experience 等较稀疏分支做 gap-directed manual mapping。当前 mapped population 为 201 个实体：65 篇论文、131 个仓库、5 个产品文档；474 条 assignment 允许实体跨分支但不把同一证据重复计算为独立支持。四条 recent negative-transfer 查询没有填平 C06 最近 90 天负面证据格，该缺口保持公开。

Deep selection 先按“能改变机制解释、实验边界或工程数据流”选择材料，不按固定数量、Stars 或单一分数。选择清单位于审计工作区，后续只有真正打开原始论文或固定代码的实体才会晋升 deep-verified。

Round 04 下载并哈希 42 篇代表论文 PDF，使用 `pypdf` 完整抽取全部页面，逐分支检查方法、状态结构、实验、消融和限制。42 个 paper entity 已晋升 deep-verified，并形成 42 个 source 与 paper card、38 个原子 claim/evidence/semantic check。原始 PDF 保留在 Git 忽略的本地 `tmp/pdfs`；Bundle 保存 arXiv URL、版本、SHA-256、页数和抽取文本，避免把大体积二进制工作目录提交到仓库。

深核验触发了分类修正：MIRIX、MAPLE 和 TreeMem 的 multi-agent 主要是内部 memory worker pipeline，不能作为 Parent/Sibling 共享记忆的直接证据。它们被保留为 bridge；StateFuse、MemTX、PatchBoard、AGENTSYS、MATM、G-Memory 等则改变了分支内部的状态机、commit、检索和迁移解释。

Round 05 又固定并读取 10 个代表仓库：OpenAI Agents SDK、Codex、LangGraph、Deep Agents、AutoGen、UFO、Caura、Statewave demo、MATM 与 memX。每个项目绑定 commit、GitHub rolling-90-day observation、repository card、engineering profile 和独立读者报告；9 个完成本地 clone，Codex 以短路径 no-checkout clone + `git show` 检查。没有执行多服务 stack、Benchmark 或 tests，因此代码存在、维护活动和线上效果严格分开。

Round 06–07 将 42 篇论文事实与 10 个仓库事实合成为 8 个机制判断和 2 个横切判断，扩写安全、评价、成本、互操作，并让主报告、分支、场景、项目和来源索引互相链接。当前 Bundle 有 4,298 个 entity、207 个 mapped/deep entity、52 个 deep-verified source、93 条查询、56 个原子 claim/evidence 和 10 个 synthesis。

## 证据层

- **Discovered：** 搜索发生和 provider metadata，只用于扩展与候选筛选。
- **Mapped：** 已确认身份、范围相关性和机制分支，用于技术地图。
- **Deep-verified：** 打开原始论文、固定代码或官方文档，并建立 claim/evidence 后才可支撑高风险结论。

读者页只把打开原文/固定代码和跨来源综合用于重要判断；mapped 候选继续作为雷达，不因高星或新建自动晋升。一般性架构解释保持逻辑完整，不把每句话拆成审计记录；关键 synthesis 在最终 publication 副本中与 ledger 双向绑定。

## 时间边界

- 当前实践与必要前置材料：截至 2025-08-24；
- 最近 12 个月：2025-08-25 至 2026-08-24；
- 最近 90 天：2026-05-27 至 2026-08-24；
- 截止日后的 provider metadata 进入 future/invalid bucket。

## 范围边界

只有承担跨 Agent 状态继承、共享、提交、检索、回流或演化职责的消息、workspace、RAG、checkpoint、event log、task queue 和通用 Agent Memory 才纳入。相邻技术略写。报告不提供推荐架构和技术选型。

## 当前限制

广度查询仍有术语噪声，尤其 Crossref 的社会科学 collective memory、GitHub 小型新项目和应用论文中偶然出现的 memory 词；Semantic Scholar 仍受 429 限制。没有完成穷尽引用闭包、所有项目 Issue/PR 审计、独立部署复现或独立采用率调查。adoption 搜索以第一方和自述案例为主；单次 GitHub snapshot 不能计算增长。结论限定于截至 2026-08-24 的公开原始材料与固定版本代码。
