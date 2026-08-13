# Open Memory Protocol：可交换对象不等于完整互操作

[SMJAI/open-memory-protocol](https://github.com/SMJAI/open-memory-protocol) 是协议草案加 reference server，不是成熟的通用 Memory engine。它最有价值的地方是让“迁移的是什么”变得可检查：一份 JSON schema 描述 memory 对象，Express server 与浏览器、Claude MCP、CLI adapter 把不同宿主映射到这个对象。但固定实现也揭示了协议和功能实现之间不可自动跨越的距离。

**固定观察。** 提交为 [`2f91247`](https://github.com/SMJAI/open-memory-protocol/tree/2f91247accde20feab9718790aa8a06c077e32bd)。仓库 2026-06-29 创建、最近 push 为 2026-07-02；未观察到 release，滚动 90 天为 31 commits、1 位贡献者、1 个 open issue。安装说明、CI、测试路径可见；API 快照许可证识别为 `NOASSERTION`，而 package 声明 Apache-2.0，发布/复用前应以实际 LICENSE 再核对。73 stars 不证明协议被采用。

## schema、server 与 adapter 实际各做什么

[`memory.schema.json`](https://github.com/SMJAI/open-memory-protocol/blob/2f91247accde20feab9718790aa8a06c077e32bd/spec/v1/memory.schema.json) 约束 `id/content/type/source/tags/namespace/time/embedding/metadata` 等对象字段。Express reference server 有 memories、conversations、extract、compress、handoff 路由。[`sqlite.ts`](https://github.com/SMJAI/open-memory-protocol/blob/2f91247accde20feab9718790aa8a06c077e32bd/packages/server/src/storage/sqlite.ts) 用 node:sqlite 保存 conversations 和 memories，并以 FTS5 trigger 索引 content/tags；adapter 则把浏览器、Claude MCP 和 CLI 的输入映射到同一 server/schema。

真实数据流很直接：adapter/HTTP caller 发送通过 schema 的 payload；route 构造 ID/timestamp 并调用 `SQLiteStorage.create`；写入 memories 后由 FTS trigger 更新 `memories_fts`；`search` 将 query token 变为 quoted-term OR 的 FTS 表达式，以 type/namespace 过滤后返回对象。

关键事实是：schema 允许保存 `embedding`，但固定提交的 reference `search` 不读取 embedding。因此它不是 semantic vector retrieval engine；一个实现者若加向量索引，还要自行定义索引与对象的同步语义。

## 接入与部署限制

[`packages/server/package.json`](https://github.com/SMJAI/open-memory-protocol/blob/2f91247accde20feab9718790aa8a06c077e32bd/packages/server/package.json) 要求 Node 22.5+ 的 `node:sqlite`，并使用 Express 4.18、Zod 3.22 和 SQLite FTS5。schema 还限制 content 长度、tag 格式/数量、ID pattern，并以 `additionalProperties: false` 拒绝不兼容 payload。这有利于明确交换对象，却会直接影响已有宿主的导入兼容。

更重要的是，`source.user_id` 和 `namespace` 是数据字段，不是 server 可见的组织级授权系统。SQLiteStorage 的 list/search filter 没有展示 row-level tenant enforcement；把 namespace 当成安全边界是错误用法。

## 哪些失败不是协议名称能解决的

- 调用方写 embedding 并假定会得到语义检索，会落入“对象支持 ≠ reference engine 支持”的错配，实际只得到 FTS OR 搜索。
- 若部署者把 `user_id`/namespace 当作访问控制而没有额外 auth/行级约束，多租户 list/search 存在跨用户暴露风险；这是根据静态 server 表面作出的推断。
- 写入 `expires_at` 并不自动保证过期对象不再出现：当前检查未看到统一的 list/search 过滤或后台清理承诺。

## 维护与未知

它可以证明一个规范化对象、reference CRUD/FTS 和若干 adapter 存在，不能证明存在独立兼容实现、无损 round-trip、共享撤销语义或协议生态共识。PR/issue 响应、认证加固、过期清理、第三方采用都未核实。

**证据边界。** 本页是提交 `2f91247` 的静态 schema/server/manifest 检查及 2026-08-10 快照；没有运行两套实现的导入导出或多租户部署。
