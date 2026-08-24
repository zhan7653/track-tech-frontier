# GitHub 候选雷达

**Round 01 状态：高召回候选，不是质量排名。** Stars、创建时间和单次 push 只用于发现；不表示性能、增长、采用或安全。

## Shared memory service 与 fleet control plane

- [`caura-ai/caura`](https://github.com/caura-ai/caura) — governed, scoped fleet memory 候选；需核验策略、存储、检索和 pipeline ordering。
- [`MehulG/memX`](https://github.com/MehulG/memX) — Redis/FastAPI、schema 和 pub/sub 形状；需核验真实 ACL 和并发语义。
- [`smaramwbc/statewave-multi-agent-memory`](https://github.com/smaramwbc/statewave-multi-agent-memory) — episode → compile → context 的冲突处理示例。
- [`raia-live/amfs`](https://github.com/raia-live/amfs) — 以 branch/diff/review/rollback 描述 agent memory filesystem。
- [`caura-ai/caura-long-run-fleet`](https://github.com/caura-ai/caura-long-run-fleet) — long-running fleet 集成候选。

## Blackboard、共享文件和项目状态

- [`octoryn/octopus-blackboard`](https://github.com/octoryn/octopus-blackboard) — blackboard 候选。
- [`dan-calin/shared-agent-memory`](https://github.com/dan-calin/shared-agent-memory) — 多 coding-agent 共享 project memory。
- [`microsoft/UFO`](https://github.com/microsoft/UFO) — 官方文档描述 HostAgent/AppAgent 使用持久 Blackboard。
- [`tommy0103/obelisk`](https://github.com/tommy0103/obelisk) — 可查询历史 session、subagent 与 workflow 的新项目。

## 跨 Agent 检索、同步与 handoff

- [`plur-ai/plur`](https://github.com/plur-ai/plur) — 本地、跨工具 shared memory 候选。
- [`ZenSystemAI/Zengram`](https://github.com/ZenSystemAI/Zengram) — typed shared memory 与跨机器 adapter 候选。
- [`skynetcmd/m3-memory`](https://github.com/skynetcmd/m3-memory) — agent/org/user scope、handoff inbox 与 shared tasks 候选。
- [`WeirdSky924/agent-handoff-skill`](https://github.com/WeirdSky924/agent-handoff-skill) — repository-local continuity packet，属于显式 handoff 路线。

## Runtime 与框架级深潜候选

- [`openai/openai-agents-python`](https://github.com/openai/openai-agents-python) — handoff、agent-as-tool、session、application context、sandbox 与 memory 的边界。
- [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph) — subgraph、checkpoint、store、shared state 与 multi-agent orchestration。
- [`microsoft/autogen`](https://github.com/microsoft/autogen) — team、message context、memory component 与 state save/load。
- [`microsoft/UFO`](https://github.com/microsoft/UFO) — multi-agent blackboard 的固定版本工程案例。

Round 02 会扩大候选库并完成 canonicality、node ID、commit、release、license、CI 和活动映射；Round 05 才把少量项目晋升为真正源码级工程报告。
