# Material for MkDocs：静态文档的导航与检索

固定提交：`39c5171cef8394a2263a6fb81410c73e01890d8d`。

## 组件与边界

MkDocs 负责从 Markdown 构建页面与导航树，Material 主题用模板 partials 渲染嵌套 nav、页内 TOC、header 和内容区域；search 插件从生成 HTML 提取标题和正文，浏览器端完成查询。admonition、details、tabs、annotations 和 Mermaid 由 Markdown 扩展与主题样式组合。

## 数据流

1. `mkdocs.yml` 和 docs 文件决定页面与顺序。
2. Markdown 扩展产生带语义类的 HTML。
3. Jinja 模板建立跨页导航与当前页状态。
4. search 插件抽取页/节文本生成索引。
5. 静态资源在浏览器实现查询、抽屉和主题切换；offline 插件可改写为离线分发。

## 对本仓库的意义

它最直接证明“静态站点也能有好搜索和三层导航”。但本仓库已有自己的 reader 结构和验证器，直接引入 MkDocs 会增加配置、主题和扩展依赖；标准库生成器只需实现较小子集。

## 项目特有失败面

- tabs/details 内的搜索命中可能不能自动显示正确隐藏面板，官方 issue 曾专门跟踪这一类问题。
- 自定义模板覆盖可能和主题升级产生漂移。
- 离线模式与普通站点路径规则不同，需要单独验收。
- 多扩展组合可能让源 Markdown 离开 GFM 可移植子集。

本次没有运行 MkDocs，也没有把主题功能清单当作理解增益证据。
