# Agent Memory frontier research — v09

这是 `track-tech-frontier` Skill 的完整公开示例，研究截止日期为 **2026-08-10**。

它不是论文或仓库简介集合，而是从广度语料出发，经过字段映射、重要分支深挖、跨来源综合与独立审计后形成的多文件研究套件。

## 快照规模

- 4,407 个 canonical entities：2,510 papers、1,846 repositories，以及标准、产品和其他来源。
- 292 条可回放 queries，7,634 条 discovery rows。
- 14 个重要技术 clusters，16 个 fixed-commit repository deep dives。
- 385 个 sources、464 个 atomic claims、773 条 evidence joins、83 个 syntheses。
- 45 个最终 reader deliverables。

这些数字描述的是最终冻结快照；`discovered`、`mapped` 和 `deep-verified` 的证据含义并不相同，详见 [输入审计](bundle/reports/12-input-audit.md) 与 [方法和限制](bundle/reports/09-method-and-limitations.md)。

## 阅读顺序

1. [研究套件入口](bundle/reports/README.md)
2. [执行结论](bundle/reports/01-executive-decision.md)
3. [字段树](bundle/reports/02-field-tree.md)
4. [架构全景](bundle/reports/03-landscape-synthesis.md)
5. [共识与争议](bundle/reports/05-consensus-controversies.md)
6. [GitHub 趋势雷达](bundle/reports/06-github-trend-radar.md)
7. [技术分支深挖](bundle/clusters/) 与 [仓库深挖](bundle/projects/)

专题入口包括 [历史和因果](bundle/reports/04-history-and-causality.md)、[Benchmark map](bundle/reports/07-benchmark-map.md)、[安全与失败](bundle/reports/08-security-and-failure.md)、[标准与采用](bundle/reports/11-standards-and-adoption.md)。

## Git 内与 Release 内分别有什么

Git 内包含：

- 全部最终读者报告；
- 14 个 cluster deep dives 与 16 个 repository deep dives；
- 最终结构化 ledgers、manifest、审计和验证记录；
- 报告本地链接所需的关键 mapping、deep packet 与 trend packet 文件。

GitHub Release `agent-memory-v09` 的完整归档还包含：

- `bundle/raw` 原始抓取快照；
- 全部 discovery、mapping、gap-fill、saturation follow-up 和 synthesis 工作目录；
- 所有中间 proposal、raw response、hash、验证脚本与运行记录；
- v09 当时冻结的 Skill 快照。

这样普通阅读和 clone 保持轻量，而需要复查完整研究过程时仍可下载全部归档。

## 质量边界

- 仓库质量卡基于固定 commit、文档、manifest、tree、CI 表面与公开维护信号；未把“存在 CI”写成测试已通过。
- 没有实际执行第三方仓库的安装、迁移、恢复或 benchmark。
- stars、README 声称和单次公开快照不作为增长、性能、成熟度或生产采用证据。
- 对缺少独立采用、删除传播、跨租户隔离或统一成本基准的部分，报告保留有界结论和证据空白。

见 [独立评审](review.md)、[完成度审计](COMPLETION_AUDIT.md) 和 [最终完整性记录](final-integrity.json)。
