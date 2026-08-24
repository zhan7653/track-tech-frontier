# 长期运行 Agent Fleet

Fleet 中的 Agent 可能跨任务、主机和模型长期存在。集中式 shared memory 便于治理和复用，却会产生控制面、租户隔离和传播风险；去中心化 memory 保留 Agent 多样性，却需要目录、发现和跨 Agent 信任。

Fleet 常需要 agent/task/project/team/tenant 多层 scope、动态权限、来源链、版本、通知、撤销和运营可观测性。经验共享还要记录 producer、consumer、任务、结果和失效条件，否则成功轨迹会脱离环境传播。

Pilot 中 Governed Shared Memory、Multi-Agent Transactive Memory、DecentMem、CoMIC 与多个 fleet repository 展示了不同拓扑。它们的性能、成熟度和生产采用仍需独立证据，项目自述不能单独证明。
