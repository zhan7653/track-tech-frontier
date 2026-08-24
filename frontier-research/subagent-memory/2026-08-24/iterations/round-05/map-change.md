# Round 05 技术地图变化

一级八分支仍不变，但工程代码让原来过于抽象的“共享/持久化”被拆成可定位的边界：

- OpenAI Agents SDK：handoff history、application context、session、sandbox snapshot、memory layout 是不同状态面；
- Codex：Child thread 可继承历史并共享 workspace，但 startup memory formation root-only；
- LangGraph：checkpointer 的 thread/namespace durability 与 Store 的跨 thread namespace 是不同层；
- Deep Agents：message history stateless 不等于 custom state、permissions 或 backend stateless；
- AutoGen：Agent context、external Memory 与 Team snapshot 不构成原子快照；
- UFO：共享 Blackboard 是 session 内对象引用和全量 prompt，而不是有治理的数据库；
- Caura：write mode、identity/scope、dedup、contradiction 和 lifecycle 分布在多服务路径；
- Statewave demo、MATM、memX 分别界定外部 compiler、population retrieval 与 LWW typed state 的能力边界。

因此“有没有 Memory”不再作为比较单位；比较单位改为继承、局部保留、共享权威、候选提交、冲突、检索、回流和清理各自由哪个组件承担。
