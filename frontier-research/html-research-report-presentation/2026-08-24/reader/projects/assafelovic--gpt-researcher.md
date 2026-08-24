# GPT Researcher：有前端不等于有阅读架构

固定提交：`5d84d2f5553e70a2765a8ff3a0d2672d60437ce8`。

## 组件与边界

Next.js 前端的 `Report.tsx` 接收完整 Markdown 字符串，调用 `markdownHelper.ts` 生成 HTML；`Sources.tsx` 把来源独立渲染为卡片或紧凑域名链接；`markdown.css` 统一正文、表格、代码和图片；页面布局提供 header、footer 与滚动按钮。

GPT Researcher 的报告组件用 remark/GFM 把一段 Markdown 转成 HTML，经 DOMPurify 净化后写入页面，来源则由独立的 Sources 组件展示。
<!-- claim:C006 -->

## 数据流

1. 研究任务产生 `answer` Markdown 与 source 列表。
2. remark + GFM 转换块和表格。
3. 链接被改写为新窗口并加入 `noopener noreferrer`。
4. DOMPurify 处理不可信报告 HTML。
5. Report 作为一个内容卡显示；Sources 在另一区域显示。

## 对本仓库的意义

安全处理值得直接吸收；单报告卡则是反例。本仓库已有多文件语义，不能把所有页面压成同一个滚动容器，也不能让来源列表脱离具体技术判断。

## 项目特有失败面

- 报告作为单个 HTML 块，没有自动页内目录和跨报告地图。
- 所有链接统一新窗口会破坏内部连续阅读。
- 来源卡显示域名，但不表达句子级支持关系。
- `dangerouslySetInnerHTML` 的安全依赖净化配置和升级。

本次只检查固定提交代码，未启动其完整前后端。
