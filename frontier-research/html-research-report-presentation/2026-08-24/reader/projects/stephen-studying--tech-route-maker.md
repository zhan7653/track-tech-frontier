# tech-route-maker：把图节点变成可审计对象

固定提交：`3c660c8c1fe75437c5f4d5ceec75261768cc3004`。

## 组件与边界

Skill 先约束领域上下文、布局与输出格式；schema 把 stage、node、edge、source 与 evidence locator 分开；validator 阻止缺证据的最终节点；renderers 从同一 JSON 生成 SVG、PPTX、Draw.io、Mermaid、HTML 与 Markdown。HTML 示例把 SVG 放在主区，把节点详情与证据放在侧栏。

## 数据流

1. 输入文件先冻结路径和哈希。
2. Agent 抽取领域对象、步骤、约束和评估。
3. `tech-route.json` 成为唯一图模型。
4. strict validator 检查节点证据、推断和未决问题。
5. HTML renderer 嵌入 SVG 与 route JSON，节点点击更新详情面板。

## 对本仓库的意义

最可迁移的思想不是其布局，而是“图、详情、证据三层来自同一模型”。当前 Markdown Mermaid 没有独立证据 schema，所以第一版只做图 + 文本摘要 + 原始定义；未来可读取研究 bundle 的结构化证据。

## 项目特有失败面

- route schema 对普通报告作者是额外工作。
- 自动布局可能把语义边简化为阶段箭头。
- 侧栏在窄屏需要重新排布，否则压缩图。
- 每个节点要求证据适合最终技术路线，不一定适合概念性总览图。

本次未运行其 renderer，结论来自固定提交的 Skill、schema、脚本和生成示例。
