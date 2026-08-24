# Quarto CLI：完整科学出版能力如何分层

固定提交：`abc6a78ed68f9e8bc9d54e27851093bd687a1cb7`。

## 组件与边界

Quarto 以 Pandoc 为转换核心，在 CLI 的 render/project 层组织多文档，在 format/html 层组合 HTML 元数据、标题、数学、链接、依赖和样式，在 website/book 层处理导航、列表、搜索和交叉页面关系。Mermaid 在 core handler 进入格式相关输出。

Quarto 网站能组合层级侧栏、全文搜索、breadcrumbs、上/下一页导航和可收起两侧导航的 reader mode。
<!-- claim:C002 -->

## 数据流

1. `.qmd`/Markdown 与项目配置进入渲染命令。
2. 扩展语法、执行输出和交叉引用转成 Pandoc 结构。
3. HTML format 汇集脚本、样式、数学、图和标题元数据。
4. website/project 层建立页面顺序、侧栏、搜索和相对链接。
5. 输出静态页面；不同格式对 Mermaid 选择原生 JS、代码块或图像。

## 对本仓库的意义

值得吸收的是能力分层：内容解析、页面格式、项目导航和多格式适配彼此独立。当前仓库不需要复制 Pandoc/执行内核/主题生态，只需要它们证明的读者机制。

## 项目特有失败面

- Pandoc、Deno/Node、浏览器与扩展版本共同构成可复现输入。
- 扩展 Markdown 会把作者锁定在 Quarto 语法。
- 网站和单文档配置面较大，轻量 skill 仓库可能承担不了。
- Mermaid 的跨格式退化依赖额外浏览器工具。

本次没有运行 Quarto，也没有评估其完整无障碍结果或插件兼容矩阵。
