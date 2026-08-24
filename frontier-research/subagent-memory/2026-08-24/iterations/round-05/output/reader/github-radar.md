# GitHub 雷达：广度候选与固定版本深潜

**Round 05 状态：广度候选不是质量排名；下表 10 个项目已经固定版本深潜。** 当前已发现 2,000+ 个去重 repository entity，并对 131 个高信号或 gap-directed 仓库完成 map-stage 筛选。Stars、创建时间和单次 push 只用于发现；不表示性能、增长、采用或安全。

## 固定版本与 90 天维护快照

| 仓库 | 固定 commit | 最近 release | 90 天 commits / contributors | 工程定位 | 深潜 |
|---|---|---:|---:|---|---|
| openai/codex | `2161ec2` | 2026-08-22 | 2,846 / 197 | Child thread fork、共享 workspace、root-only memory formation | [报告](projects/openai--codex.md) |
| openai/openai-agents-python | `2334679` | 2026-08-19 | 585 / 98 | Handoff、agent-as-tool、sandbox memory layout | [报告](projects/openai--openai-agents-python.md) |
| langchain-ai/deepagents | `23b83ad` | 2026-08-20 | 1,459 / 46 | 临时 child message context、shared backend、state 回流 | [报告](projects/langchain-ai--deepagents.md) |
| langchain-ai/langgraph | `f09cfe8` | 2026-08-19 | 163 / 18 | Checkpointer、subgraph namespace、cross-thread Store | [报告](projects/langchain-ai--langgraph.md) |
| caura-ai/caura | `54dd6d4` | 2026-08-23 | 509 / 12 | 多租户 fleet memory control plane | [报告](projects/caura-ai--caura.md) |
| microsoft/UFO | `96983c7` | 2026-08-10 | 24 / 2 | Host/App in-process Blackboard | [报告](projects/microsoft--UFO.md) |
| smaramwbc/statewave-multi-agent-memory | `7f16415` | 无 | 31 / 3 | 外部 episode→compile→context runtime 的 demo | [报告](projects/smaramwbc--statewave-multi-agent-memory.md) |
| kimdanny/matm | `2fb906b` | 无 | 1 / 1 | population trajectory retrieval/LTR | [报告](projects/kimdanny--matm.md) |
| microsoft/autogen | `027ecf0` | 2025-09-30 | 0 / 0 | context、Memory component 与 Team snapshot | [报告](projects/microsoft--autogen.md) |
| MehulG/memX | `86aeffe` | 无 | 0 / 0 | Redis LWW typed state 与进程内 notification | [报告](projects/MehulG--memX.md) |

这里的 commit/contributor 是指定 2026-05-27 至 2026-08-24 inclusive UTC 窗口的测量；release 为观察时最新发布日期。单次快照能说明维护活动和新鲜度，不能计算 star growth、项目质量或行业采用。

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

上述 10 项已经核对 canonical node、commit、release、license、CI/测试存在和活动，并形成源码级工程报告。其余 radar 名称仍只是 map-stage 候选，不等于代表性或质量结论。
