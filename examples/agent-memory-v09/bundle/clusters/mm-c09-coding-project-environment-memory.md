# C09：编码、项目与环境记忆深度报告

截至 2026-08-10。本报告不是仓库清单，而是把 C09 拆成四条不同的机制路线，再用论文实验、固定提交代码面和反证判断哪些结论成立。

## 结论先行

C09 is not one storage problem: the retained evidence separates at least structural code indexes, event-sourced project judgments, passive repository instruction files, and feedback-conditioned developer policies, each with different write triggers, read paths, and evaluation units.
<!-- claim:C09-C12 -->

The positive structural-index ablation and negative repository-context-file study make the effect of coding memory conditional on representation, workload, and intervention point rather than on persistence or extra context alone.
<!-- claim:C09-C13 -->

因此，C09 的分析单位不能是“有没有 memory”：应分别问它保存的是代码结构、开发判断、提示规则还是反馈策略；何时写入；如何绑定 repo/branch/commit；何时进入上下文或阻断动作；最终用 localization、resolve、重复失败、测试结果、成本和安全门分别验收。

## 四条机制路线

| 路线 | Durable state | Write | Read / action | 最合适的验证 |
|---|---|---|---|---|
| 结构化代码索引 | symbol、call/dependency graph、embedding/index revision | code/commit 变化触发索引 | localization 后供 agent 读写文件 | 同 harness 的 index on/off，resolve、localization、cost |
| 事件溯源项目判断 | issue、attempt、fix、decision、note、fragile-file signal | 工具结果、commit、人工判断追加事件 | summary/MCP recall；pre-action warning | 重复失败率、decision consistency、action gate、跨 session |
| 仓库上下文/规则文件 | repository overview、非标准约束、命令 | 人工或 LLM 生成静态文件 | session 开始时注入 prompt | task success、token/cost、instruction compliance |
| 反馈条件策略 | match、feedback、resolution、reward/telemetry | 任务反馈与已验证 resolution | deterministic ranker；shadow/canary policy | hard-negative、decision accuracy、latency、OPE/safety gates |

## 路线一：结构化索引的因果证据与边界

The structural-index study held Claude Opus 4.7 fixed and compared index-on, the same harness with the index off, and an agentic-grep harness across SWE-PolyBench Verified and SWE-bench Pro with three seeds and a leak-audited per-task sandbox.
<!-- claim:C09-C01 -->

In the structural-index artifact's released table, index-on versus index-off was 50.4% versus 41.9% resolve and 84.5% versus 44.3% agent-targeted localization@5, while per-cell mean cost was $1.15 versus $1.19; these are author-released results for one fixed model and the stated filtered sample, not a universal coding-memory ranking.
<!-- claim:C09-C02 -->

The supercoder-eval artifact can recompute released metrics and inspect scoring logic, but it cannot rerun agent generation or independently reconstruct localization and resolve from unreleased traces, so it is not a full end-to-end reproduction package.
<!-- claim:C09-C03 -->

At pinned commit 89e4156ba11538a8be0e2343d215bdff778550ed, supercoder-eval separates released metrics, analysis, scoring, an exclusion ledger, and paper source; v09 found no CI or test directory in the inspected tree and did not execute the analysis.
<!-- claim:C09-C11 -->

这里能支持的共识是：对于需要跨文件定位的 workload，代码结构可以成为有效的 project-memory 表示；不能支持的是“任何 coding task 都应持久化全库索引”或“该仓库已完成第三方复现”。

## 路线二：把开发历史变成可治理事件

PROJECTMEM represents project history as append-only typed events for issues, attempts, fixes, decisions, and notes, deterministically projects them into compact summaries served over MCP, and adds a pre-action gate for previously failed approaches or fragile files.
<!-- claim:C09-C04 -->

PROJECTMEM's reported evaluation is a two-month author self-study over 10 projects and 207 logged events, so it supports feasibility and inspectability but does not establish a causal task-success benefit against a matched no-memory baseline.
<!-- claim:C09-C05 -->

At pinned commit 3d8e3f379913d49585ba126d090f5501de9c079d, projectmem exposes separate storage, search, summary, staleness, redaction, MCP-server, command, and test modules; v09 inspected this structure but did not execute the package or tests.
<!-- claim:C09-C10 -->

这一支最重要的架构观点不是“再做一个向量库”，而是把 source event、derived summary 和 action gate 分开：Git/测试结果仍是当前事实，事件日志保存为什么这样做和什么已经失败，summary 只是可重建投影，action 前再按当前 commit/worktree/permission 复核。

## 路线三：反证——更多上下文本身不是记忆收益

The AGENTS.md study reports that repository context files did not generally improve task success and increased inference cost by more than 20% on average across its tested agents, models, generated files, and developer-committed files.
<!-- claim:C09-C06 -->

The AGENTS.md authors conclude that context files are useful for non-standard coding practices but that performance claims require evaluation and human-written files should avoid unnecessary requirements; this is a boundary on passive context injection, not a refutation of all structured project memory.
<!-- claim:C09-C07 -->

这条反证迫使 C09 把“被保存”与“在正确时刻、以正确粒度、影响正确动作”分开。静态 overview、结构索引、失败历史和 policy memory 不能放在同一个 leaderboard 里，也不能用 context 长度代替收益。

## 路线四：反馈策略与安全门

RL Developer Memory keeps a deterministic ranker deployed, logs retrieval and feedback decisions, and permits a contextual-bandit residual policy to influence canary behavior only through conservative off-policy-evaluation and review gates.
<!-- claim:C09-C08 -->

In RL Developer Memory's same-commit 200-case author benchmark, deterministic control and the full shadow/OPE configuration both report 80.0% expected-decision accuracy and 100.0% hard-negative suppression; the paper also reports unsupported active learned-policy deployment and official-client MCP interoperability, a live latency regression, and 40 residual non-RL failures.
<!-- claim:C09-C09 -->

该结果不支持“learned memory 已胜出”；更稳妥的工程结论是先把 deterministic decision、feedback lineage、review/OPE gate 和 rollback 做成真值面，再让学习策略在 shadow/canary 中证明增量收益。

## C09 参考架构

```text
repo / branch / worktree / commit / tool outcome
            │
            ├─ authoritative receipts: Git objects, tests, issue/tool events
            ├─ project judgment ledger: attempt/fix/decision/reason/supersession
            ├─ derived projections: symbol graph, semantic index, summaries
            └─ policy state: feedback, gate decision, reviewer/OPE trace
                              │
hard scope + commit watermark ─┴─> retrieve / localize / compile context
                                      │
current permission + pre-action gate ─┴─> edit / command / tool action
                                                      │
                                             result and test receipt
```

必须保留的工程不变量：每个记忆对象绑定 repository identity 与 branch/worktree/commit 或有效期；derived index 暴露 commit watermark；decision 有 supersession 而非静默覆盖；secret/credential 默认不写；action 使用前重验当前权限与事实；任何 benchmark 同时报 localization、resolve/action、tokens/cost、stale hit、错误注入与 recovery。

## 当前 GitHub 工程面

v09 的固定提交雷达覆盖三类近期实现：Basic Memory/ByteRover/Memorax 更偏跨会话项目知识与工作方式；Engraphis/Codebase Memory MCP 更偏代码图、版本历史和检索接口；Claude-Mem/Headroom 等相邻项目更偏会话观察与上下文压缩。它们说明工程供给活跃，但 stars、README、CI presence、公开引用都不是性能或生产采用证据；每个项目的固定提交、模块、依赖、维护和验证边界在独立 project deep dive 中展开。

## 尚未闭合的证据

- 尚无一个公开协议同时比较结构索引、事件日志、静态上下文文件和反馈策略。
- 没有执行本 packet 的仓库，因此不能把 documented setup 或 tests present 升级成可运行性结论。
- branch/worktree 并发、secret capture、index invalidation、decision conflict 与 purge/derived deletion 仍缺统一实测。
- PROJECTMEM 和 RL Developer Memory 的主要效果证据来自作者；structural-index artifact 也不是完整生成重放。
- 截止本轮，工程热度可作为 inspect trigger，但不能替代 matched ablation、独立复现或生产证据。



<!-- synthesis:CLY-C09 claims:C09-C01,C09-C02,C09-C04,C09-C05,C09-C06,C09-C07,C09-C08,C09-C09,C09-C12,C09-C13 clusters:MM-C09 -->
