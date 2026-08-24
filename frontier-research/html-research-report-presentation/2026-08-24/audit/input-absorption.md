# 输入吸收检查

| 输入 | 实际改变了什么 |
|---|---|
| Quarto | 把实现拆成内容解析、格式输出、项目导航，并加入 reader mode 与跨格式 Mermaid 退化。 |
| MyST | 采用原生 `details` 的无脚本原则，并明确跨页/页内两种侧栏。 |
| MkDocs Material | 选择构建时章节索引、离线搜索、嵌套导航；加入隐藏内容搜索反例。 |
| Observable Framework | 采用静态数据/索引思路；明确运行时图表不会自动进入搜索。 |
| GPT Researcher | 加入 raw HTML/URL 安全边界；拒绝单报告卡 + 独立来源墙作为最终结构。 |
| tech-route-maker | 形成“视觉图 + 文本摘要 + 原始定义/证据”的三层图解模型。 |
| ReActicle / beautiful-article | 采用语义组件和主题令牌思想以及分版浏览器验收；拒绝 TSX 重写内容源。 |
| Idyll paper | 把可读作者层和扩展交互接口作为分离原则。 |
| EMAR paper | 把无需交互也能完整阅读设为硬退化门槛。 |
| W3C WAI | 加入 landmark、标题层级、键盘、移动阅读和焦点验收。 |
| Distill | 让引用、边注、宽图和交互服务文章节奏，而不是 dashboard 密度。 |
| 本机 power-work-report | 吸收 sticky nav、主题、打印、details、滚动状态；发现其单文件特化不能直接扩展到 56 页。 |

所有深输入都改变了架构、交互边界、失败条件或验收门槛；没有只为增加项目名称而进入正文。
