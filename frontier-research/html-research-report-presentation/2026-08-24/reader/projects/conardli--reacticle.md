# ReActicle：受约束 HTML 文章协议的近期弱信号

固定提交：`dcfc4baf386bbc220cd1aa6274bed3b741108465`；配套 `beautiful-article` Skill 固定到 `aaf9a82f5efd73e87cc0998edc398e75bfc35901`。

## 组件与边界

ReActicle 提供 Article、Hero、Lead、Section、Summary、Aside、Table、CodeBlock、Decision、Tradeoff、Tabs、TOC、Conclusion 等语义组件，并用 `--ra-*` 主题令牌约束 Raw 自由层。Vite single-file 插件把 CSS/JS 内联为可离线 HTML。配套 Skill 把来源抽取、编辑规划、首屏验收、分节构建、终审与修复分阶段。

## 数据流

1. Skill 把来源统一为 Markdown 并记录抽取问题。
2. 规划文件决定文章类型、保留比例、主题、版式和资产。
3. Agent 用受约束 React 组件组合首屏与各节。
4. reviewer 分别检查首屏、章节和最终结果。
5. Vite 构建自包含 HTML，可选打印/PDF。

## 对本仓库的意义

语义组件、主题合同和“先做首屏再整篇”的迭代方式很有价值；但本任务不能用 80% 保留比例重编研究结论，也不应要求每个现有 Markdown 页面转为 TSX。可吸收的是模板组件与验收节奏。

## 项目特有失败面

- 每篇文章都生成 React 工程，维护成本高于确定性转换。
- Agent 编辑会产生第二份内容源，可能丢失限定语或链接。
- single-file 输出方便分享，但 56 页套件若各自内联运行时会重复体积。
- 截止观察时 ReActicle 仓库提交数很少，GitHub API 没有给出许可证标识；只适合做弱信号。

本次没有复制其代码或主题，也没有执行构建。
