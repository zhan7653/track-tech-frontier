# Track Tech Frontier

`track-tech-frontier` 是一个面向技术前沿调研的 Codex Skill。它先以高召回方式收集论文、GitHub 仓库、标准、产品与反面证据，再构建领域地图、按技术机制综合方案空间，并将重要方向和少量工程项目做深，最终交付面向读者的多文件研究套件，而不是链接清单、项目简介合集或审计账本。

## 能做什么

- 广泛发现论文和 GitHub 项目，并保留可复查的查询与筛选记录。
- 按“技术机制主分支 → 应用场景视图 → 重点 GitHub 工程案例”组织读者内容。
- 区分“广度地图”和“重点深挖”，先综合方案家族，再分析代表性机制与真实实现。
- 同时追踪论文前沿与近期 GitHub 工程趋势。
- 显式整理共识、争议、反例、证据空白和未解决问题。
- 输出独立可读的总览、通用架构模型、机制报告、场景视图、GitHub radar 与项目工程报告；审计材料下沉。

## 仓库结构

```text
SKILL.md                         Skill 主入口
agents/openai.yaml               Codex 展示与默认提示
references/                      方法、证据、GitHub、综合与交付规范
scripts/                         corpus discovery、bundle 管理与测试
examples/agent-memory-v09/       Agent Memory 前沿调研最终快照
examples/agent-memory-v10/       基于 v09 重编的读者版参考实现
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

本仓库包含截至 **2026-08-10** 的 Agent Memory 研究底稿，以及 2026-08-12 完成的读者版重编。建议从 [Memory v10 读者入口](examples/agent-memory-v10/reader/README.md) 开始：

- [领域总览](examples/agent-memory-v10/reader/overview.md)
- [通用架构模型](examples/agent-memory-v10/reader/architecture.md)
- [方案全景](examples/agent-memory-v10/reader/solution-landscape.md)
- [当前主流与近期变化](examples/agent-memory-v10/reader/trends.md)
- [六个技术机制分支](examples/agent-memory-v10/reader/mechanisms/README.md)
- [四个应用场景](examples/agent-memory-v10/reader/scenarios/README.md)
- [GitHub 候选雷达](examples/agent-memory-v10/reader/github-radar.md)
- [八个重点工程案例](examples/agent-memory-v10/reader/projects/README.md)

[v09](examples/agent-memory-v09/README.md) 完整保留为广度语料、固定证据、结构化账本、旧版专题和研究过程的权威快照。v10 没有复制 278 MiB 的完整工作目录，而是通过 [审计入口](examples/agent-memory-v10/audit/README.md)连接到 v09。

Git 历史保存最终报告、结构化账本以及报告链接所需的关键过程材料。完整约 278 MiB 的研究工作目录（包含大体积 raw snapshots、全部中间产物与验证材料）作为 GitHub Release `agent-memory-v09` 的压缩附件发布，避免让普通 clone 承担实验归档体积。

## 验证

Skill 脚本仅依赖 Python 标准库。运行测试：

```powershell
python -m unittest discover -s scripts -p "test_*.py"
```

验证 Memory v10 的读者套件结构、UTF-8、相对链接、占位内容和内部审计标记：

```powershell
python scripts/validate_reader_suite.py --root examples/agent-memory-v10
```

该检查只验证读者交付的基本完整性；内容是否真正讲清领域，仍需按 `references/evaluation-gates.md` 做抽样阅读或独立读者复核，不能由绿色检查替代。

## 生成可展示的 HTML

读者套件完成并通过结构验证后，可以把现有 Markdown 直接生成一个多页、可离线打开的静态站点：

```powershell
python scripts/render_reader_html.py `
  --root examples/agent-memory-v10 `
  --output examples/agent-memory-v10/site
```

入口是 `site/index.html`。生成器保持 Markdown 为权威内容源，不执行原始 HTML，使用构建时静态搜索索引，并提供：

- 套件导航、章节地图、同组上/下一篇与专注阅读模式；
- 中文子串搜索，结果直接落到具体章节；
- 当前 `flowchart` Mermaid 子集的构建时 SVG、可点击节点、文本后备与原始源码；
- 比较表横向滚动与行聚焦、代码复制、深浅主题、移动端抽屉和打印样式；
- 隔离、类型受限的被动资源复制，带旧 manifest 保护的原子重建；
- `build-manifest.json` 输入/输出哈希，以及 UTF-8、危险 URL、本地断链、章节锚点、陈旧页面和额外文件验证。

未纳入 `reader/` 或 `audit/` 发布面的本地证据不会被写成可逃出站点根的链接；这包括套件内的 `work/` 过程材料和套件根目录之外的工作区文件。它们显示为“源工作区”文本并计入 manifest，因此独立部署不会产生指向构建机目录或未发布材料的伪链接。

再次验证已生成站点：

```powershell
python scripts/render_reader_html.py `
  --root examples/agent-memory-v10 `
  --output examples/agent-memory-v10/site `
  --check
```

支持范围和退化规则见 [`references/html-presentation.md`](references/html-presentation.md)。生成器只承诺仓库当前使用的 Markdown 子集；不支持的 Mermaid 或未来语法必须保留为可读文本并给出构建告警，不能静默丢失。

v09 快照还附带独立评审、完成度审计和最终完整性清单：

- [独立评审](examples/agent-memory-v09/review.md)
- [完成度审计](examples/agent-memory-v09/COMPLETION_AUDIT.md)
- [最终完整性记录](examples/agent-memory-v09/final-integrity.json)

## 许可

目前尚未选择开源许可证。仓库公开可见不等于自动授予复制、修改或再分发权；后续确定许可证后再补充 `LICENSE`。
