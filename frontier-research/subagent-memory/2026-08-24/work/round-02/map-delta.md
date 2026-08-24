# Round 02 地图变化

Round 02 的 5,247 条新增 occurrence 把总实体扩展到 4,285。广度候选在原七分支均有覆盖，没有出现需要推翻 Parent→Child / Child→Team 两边界的证据。

但是，Claude Code、LangGraph、OpenAI Agents SDK Sandbox Memory 和 Deep Agents 的官方/项目文档共同暴露了一个原地图没有独立表达的问题：**命名 Subagent 自身的状态保留期和身份绑定**。

因此新增 `SM-C08 Subagent-Local Persistence and Identity`。它与三个相邻分支的边界是：

- `SM-C01` 研究一次 spawn 时 Parent 向 Child 传什么；
- `SM-C08` 研究 Child 自己跨 invocation/thread/session/project/user 保留什么；
- `SM-C02` 研究多个主体间谁能看和修改哪些状态；
- `SM-C05` 研究 Child 的局部状态何时提交回 Parent/Team。

新增分支是 Round 02 的实质结构变化，不是重命名或文件拆分。
