# Track Tech Frontier

`track-tech-frontier` 是一个面向技术前沿调研的 Codex Skill。它先以高召回方式收集论文、GitHub 仓库、标准、产品与反面证据，再构建领域树、识别重要分支、做重点深挖，最终输出多文件研究套件，而不是链接清单或项目简介合集。

## 能做什么

- 广泛发现论文和 GitHub 项目，并保留可复查的查询与筛选记录。
- 按机制、架构、实现、评测、安全、成本与采用情况聚类。
- 区分“广度地图”和“重点深挖”，对每个重要分支形成独立分析。
- 同时追踪论文前沿与近期 GitHub 工程趋势。
- 显式整理共识、争议、反例、证据空白和后续验证问题。
- 生成字段树、全景分析、时间线、benchmark map、GitHub radar、cluster deep dives 和 repository deep dives。

## 仓库结构

```text
SKILL.md                         Skill 主入口
agents/openai.yaml               Codex 展示与默认提示
references/                      方法、证据、GitHub、综合与交付规范
scripts/                         corpus discovery、bundle 管理与测试
examples/agent-memory-v09/       Agent Memory 前沿调研最终快照
```

## 安装

把仓库克隆到个人 Codex skills 目录：

```powershell
git clone https://github.com/zhan7653/track-tech-frontier.git "$env:CODEX_HOME\skills\track-tech-frontier"
```

如果没有设置 `CODEX_HOME`，通常可使用：

```powershell
git clone https://github.com/zhan7653/track-tech-frontier.git "$HOME\.codex\skills\track-tech-frontier"
```

然后在 Codex 中以 `$track-tech-frontier` 调用。

## Agent Memory 调研

本仓库包含截至 **2026-08-10** 的完整可读研究快照。建议从 [Memory 研究入口](examples/agent-memory-v09/bundle/reports/README.md) 开始：

- [执行结论](examples/agent-memory-v09/bundle/reports/01-executive-decision.md)
- [字段树](examples/agent-memory-v09/bundle/reports/02-field-tree.md)
- [架构全景](examples/agent-memory-v09/bundle/reports/03-landscape-synthesis.md)
- [共识与争议](examples/agent-memory-v09/bundle/reports/05-consensus-controversies.md)
- [GitHub 趋势雷达](examples/agent-memory-v09/bundle/reports/06-github-trend-radar.md)
- [14 个技术分支深挖](examples/agent-memory-v09/bundle/clusters/)
- [16 个仓库深挖](examples/agent-memory-v09/bundle/projects/)
- [输入审计](examples/agent-memory-v09/bundle/reports/12-input-audit.md)
- [方法与限制](examples/agent-memory-v09/bundle/reports/09-method-and-limitations.md)

Git 历史保存最终报告、结构化账本以及报告链接所需的关键过程材料。完整约 278 MiB 的研究工作目录（包含大体积 raw snapshots、全部中间产物与验证材料）作为 GitHub Release `agent-memory-v09` 的压缩附件发布，避免让普通 clone 承担实验归档体积。

## 验证

Skill 脚本仅依赖 Python 标准库。运行测试：

```powershell
python -m unittest discover -s scripts -p "test_*.py"
```

Memory 快照还附带独立评审、完成度审计和最终完整性清单：

- [独立评审](examples/agent-memory-v09/review.md)
- [完成度审计](examples/agent-memory-v09/COMPLETION_AUDIT.md)
- [最终完整性记录](examples/agent-memory-v09/final-integrity.json)

## 许可

目前尚未选择开源许可证。仓库公开可见不等于自动授予复制、修改或再分发权；后续确定许可证后再补充 `LICENSE`。
