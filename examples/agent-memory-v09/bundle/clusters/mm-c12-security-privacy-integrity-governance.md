# MM-C12｜安全、隐私、完整性与治理：深度报告

> 状态：final standalone cluster report；截至 2026-08-10。本文只使用 v09 已打开、已落账的来源与 claim–evidence join；不新增事实，不声称运行过代码。

## 1. 决策摘要：安全边界贯穿“写入—持久化—取回—行动—删除”，不是一个输入过滤器

MM-C12 的主要结论不是“记忆会被投毒”，而是持久记忆把一次不可信输入升级为跨会话、可重复触发的控制面。攻击可以经直接投毒、query/observation-only 注入、环境观察、分片合谋或经验晋升进入；之后还要经过持久化、取回、planner/工具执行才造成行动。隐私风险又沿反向通道出现：攻击者通过反复、适应性查询从 memory-conditioned response 中抽取信息。治理层的 CRUD、scope、TTL、签名 lineage、策略检测与审计日志只覆盖不同片段；当前没有一个独立深源验证从 poisoned-write prevention 到 tenant-scoped action authorization 的完整生产链。

所以默认控制设计必须是纵深防御：写入前标注来源与风险；写入时隔离、审核和版本化；取回时按主体/会话/agent scope 过滤；拼装时只暴露最小公共视图；高风险行动前重新授权；发现污染后回滚并修复已经传播的派生物。签名和可追溯性证明“谁以何顺序改了什么”，不能证明内容为真；删除 API 证明接口存在，也不能证明 embedding、profile、cache、backup 和已学技能都已清除。

**本节证据索引** — Claims: `OPS-C01`, `OPS-C04`, `OPS-C05`, `OPS-C07`, `OPS-C09`, `OPS-C11`, `OPS-C12`, `OPS-C13`, `OPS-C14`, `OPS-C15`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C21`, `OPS-C22`, `OPS-C24`, `OPS-C25`, `OPS-C27`, `FM-PE-C01`. Evidence: `OPS-J01`, `OPS-J04`, `OPS-J05`, `OPS-J07`, `OPS-J09`, `OPS-J11`, `OPS-J12`, `OPS-J13`, `OPS-J14`, `OPS-J15`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J21`, `OPS-J22`, `OPS-J24`, `OPS-J25`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`, `FM-PE-J01`, `FM-PE-J02`.

## 2. 边界与演化：从静态后门到多通道写入与经验晋升

本簇包括四个相互耦合的面：**完整性**（谁能改变持久状态）、**机密性**（谁能从记忆或响应中恢复什么）、**授权**（哪条记忆可驱动哪个主体的敏感行动）、**生命周期治理**（保留、修订、撤销、删除、回滚与审计）。单纯 prompt injection 若不跨越持久化边界不属于本簇核心；普通数据库 ACL 若没有 agent 的记忆读取与行动闭环，也只是外部依赖。

证据演化不是线性替代，而是攻击面逐步扩张。2024 年 AgentPoison 把后门投毒定位到长期 memory/RAG；2025 年 MEXTRA 与 MINJA 分别暴露黑盒隐私抽取和 query/observation-only 写入；2026 年 eTAMP 将入口推进到环境观察，Sleeper 把成功链拆成 write→retrieve→action，MPBench 归纳四个写入通道和九个结构漏洞，MAFIA研究 query-only + benign pool + audit，Salami 展示单片看似良性、组合后有害，MutMem 引入签名 predecessor transitions，DP-MemView把重复响应形式化为 adaptive transcript privacy，STALE则指出“存储更新、行为仍陈旧”。PoisonedEvolution 又把边界推进到经验晋升：不可信轨迹被归一化为长期可信技能。

演化的共同方向是：攻击者不必拥有 memory store 的直接写权限；防御者也不能只在单条记忆上做恶意文本分类。威胁可能跨多个良性片段、跨多次查询、跨环境与会话，并在抽象/技能化后丢掉原始不可信来源标签。

**本节证据索引** — Claims: `OPS-C01`, `OPS-C03`, `OPS-C04`, `OPS-C05`, `OPS-C07`, `OPS-C09`, `OPS-C10`, `OPS-C11`, `OPS-C12`, `OPS-C14`, `OPS-C16`, `FM-PE-C01`. Evidence: `OPS-J01`, `OPS-J03`, `OPS-J04`, `OPS-J05`, `OPS-J07`, `OPS-J09`, `OPS-J10`, `OPS-J11`, `OPS-J12`, `OPS-J14`, `OPS-J16`, `FM-PE-J01`, `FM-PE-J02`.

## 3. 机制地图：攻击链与控制链必须一一对应

| 攻击/失败机制 | 跨越的边界 | 仅靠何种控制不够 | 对应控制面 |
|---|---|---|---|
| 直接 memory/RAG 投毒 | 不可信内容 → 持久状态 | 只在读取时过滤 | 写入隔离、来源、版本、回滚 |
| query/observation/environment 注入 | 普通交互 → 隐式写入 | 只保护 store API | 入口分类、写入资格、环境来源标注 |
| sleeper chain | 写入 → 延迟取回 → 行动 | 只报告 ASR | 分段追踪与行动前再授权 |
| collusive fragments | 多个良性片段 → 联合恶意 | 单条检测器 | 组合级审计、上下文策略 |
| experience promotion | 轨迹 → 长期技能/指令 | 只扫描原始轨迹 | provenance-diversity、晋升门、派生物回滚 |
| adaptive extraction | 多轮响应 → 累积泄漏 | 单轮脱敏 | public view、累计隐私预算/响应策略 |
| stale adaptation | 已更新 store → 旧行为 | 只验证 CRUD | policy-level supersession 与行动校验 |
| logical delete gap | API 删除 → 派生状态仍存 | 只看 2xx/对象消失 | 派生物清单、重建、备份与行为修复 |

这张映射表的要点是控制覆盖而非产品打分。MutMem 的签名 lineage、OWASP Memory Guard 的 detector/policy/snapshot、DP-MemView 的公共视图、云产品的 scope/CRUD/IAM 各自提供局部机制；`OPS-C27` 明确限制了把它们拼成已验证端到端方案的冲动。

**本节证据索引** — Claims: `OPS-C01`, `OPS-C04`, `OPS-C05`, `OPS-C07`, `OPS-C09`, `OPS-C11`, `OPS-C12`, `OPS-C13`, `OPS-C14`, `OPS-C15`, `OPS-C16`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C21`, `OPS-C22`, `OPS-C24`, `OPS-C25`, `OPS-C27`, `FM-PE-C01`, `FM-PE-C04`. Evidence: `OPS-J01`, `OPS-J04`, `OPS-J05`, `OPS-J07`, `OPS-J09`, `OPS-J11`, `OPS-J12`, `OPS-J13`, `OPS-J14`, `OPS-J15`, `OPS-J16`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J21`, `OPS-J22`, `OPS-J24`, `OPS-J25`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J05`.

## 4. 参考安全架构：记忆数据面之外必须有独立控制面

```text
用户/query/网页/工具/环境/其他 agent
                  │
                  ▼
 [来源分类 + 主体/租户/会话绑定 + 风险检测]
                  │
        ┌── 拒绝/隔离/人工审查
        ▼
 [版本化写入 + predecessor/provenance + snapshot]
        │                      │
        │                      └──> [晋升门：轨迹 -> 技能/摘要/画像]
        ▼
 [scope-filtered retrieval + selected public view]
        │
 [冲突/陈旧/组合级检查]
        │
 [planner] ──> [敏感行动再授权] ──> [工具/外部系统]
        │                  │
        └──── SecurityEvent/审计 ────┘
                         │
       [撤销/回滚/删除 + 派生物与行为依赖修复]
```

架构有两条不可合并的证据链。**数据控制链**负责来源、scope、公共视图、版本和删除；**行动控制链**负责在记忆影响敏感动作前重新检查主体、意图和当前政策。只完成前者仍可能让一条被合法写入、合法取回但语义错误的内容驱动危险行动；只完成后者则无法阻止持久污染扩散到摘要、画像或技能。

MutMem 的证据支持 signed predecessor-linked transition，但其作者明确授权/追溯不等于真值。OWASP Memory Guard 支持 detector + declarative policy + snapshot rollback 与 SecurityEvent 来源分类；云产品文档支持局部 CRUD/scope/IAM/region 能力。这里把它们组合成参考架构属于显式工程综合，不是已经被单一实现或独立部署验证的事实。

**本节证据索引** — Claims: `OPS-C12`, `OPS-C13`, `OPS-C15`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C21`, `OPS-C22`, `OPS-C23`, `OPS-C24`, `OPS-C25`, `OPS-C26`, `OPS-C27`, `FM-PE-C01`. Evidence: `OPS-J12`, `OPS-J13`, `OPS-J15`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J21`, `OPS-J22`, `OPS-J23`, `OPS-J24`, `OPS-J25`, `OPS-J26`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`, `FM-PE-J01`, `FM-PE-J02`.

## 5. 算法与数据流：用状态机记录一次记忆如何获得行动权

建议把每条外部贡献的状态建模为以下迁移，而不是直接从“文本”变成“可信记忆”：“observed → quarantined → admitted → retrieved → composed → authorized-for-action → acted → superseded/deleted”。每次迁移都记录主体、scope、predecessor、来源类和策略结果。轨迹要晋升为技能时，另走 promotion 分支，保留贡献 session/来源的关系；发现污染时，从恶意源逆向枚举所有摘要、技能、embedding/profile/cache 派生物。

这一状态机有三个算法级检查点：

1. **写入资格**：即使请求只表现为 query、observation 或环境内容，也先判定它是否有资格形成持久状态；不以“没有直接 store API 调用”作为安全证明。
2. **组合级检索检查**：Salami 类风险要求检查被共同取回的片段集合，而不只是逐条打分；MAFIA 的 query-only、benign pool 与 active audit 设置说明输入审计也应进入评测。
3. **行动再授权与后验回写**：Sleeper 的 write→retrieve→action 分解要求在 tool call 前检查；STALE 要求在状态变更后验证 planner 是否真正放弃旧策略。

DP-MemView 的 selected public view 提供了响应侧最小暴露接口，但只解决其定义的视图契约；适应性多轮泄漏仍需累计分析。该状态机没有在 v09 中实现或运行。

**本节证据索引** — Claims: `OPS-C04`, `OPS-C05`, `OPS-C07`, `OPS-C10`, `OPS-C11`, `OPS-C12`, `OPS-C14`, `OPS-C15`, `OPS-C16`, `FM-PE-C01`. Evidence: `OPS-J04`, `OPS-J05`, `OPS-J07`, `OPS-J10`, `OPS-J11`, `OPS-J12`, `OPS-J14`, `OPS-J15`, `OPS-J16`, `FM-PE-J01`, `FM-PE-J02`.

## 6. 实现与集成：现有工程覆盖三层，但没有一条已验证的生产闭环

工程证据显示了“攻击—运行时阻断—审计”三层：AgentPoison 提供 memory/knowledge-base poisoning 红队代码，OWASP Agent Memory Guard 在读写路径上描述 detector、policy、snapshot rollback 与 provenance SecurityEvent，Brain0 描述敏感读取和来源/意图审计。该组合是覆盖地图，不是互操作或效果证明。

AgentPoison 仓库在固定 commit `f859…` 上 setup 有文档、tests 存在、CI 在已检查树中未找到、MIT、未执行；其 233 stars 是 2026-08-10 的累计单点，不是增长/采用证据。OWASP 的相关 README 固定在 `425616…`，支持静态机制判断，但本轮没有运行 detector、策略或回滚。对生产系统的集成验收应分别要求：持久层适配器是否覆盖全部写入口；scope 是否在服务端强制；SecurityEvent 是否可关联到实际 retrieval/tool call；snapshot rollback 是否连带修复派生技能和行为；故障时是否 fail closed。当前 ledger 不支持回答这些运行问题。

**本节证据索引** — Claims: `GR-C-M009`, `GR-C032-1`, `GR-C032-2`, `GR-C032-3`, `OPS-C24`, `OPS-C25`, `OPS-C27`. Evidence: `GR-V-M009-01`, `GR-V-M009-02`, `GR-V-M009-03`, `GR-V032-1`, `GR-V032-2`, `GR-V032-3`, `OPS-J24`, `OPS-J25`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`.

## 7. 成本模型：安全控制要按链路计费，不能只报检测准确率

安全控制的成本至少分为：每次写入的检测/策略调用、隔离与人工审查、版本与 snapshot 存储、取回时 scope/组合检查、响应侧公共视图生成、每个敏感动作的再授权、污染后的索引重建/派生物回滚、审计保留。eTAMP 报告在其实验中环境 stress 可把攻击成功率提高最多 8 倍，说明成本评估还必须包含压力条件；不能只在低并发、单步请求上测。

当前没有共同协议同时给出上述成本与安全收益。PoisonedEvolution 的 pilot provenance-diversity gate 在一个 `n=30,k=3` 设置中拦截 25/25 单簇 F1 候选并接受一个五 session 多样性对照，但论文本身称其为 preliminary；它不能直接成为通用阈值。产品 API 的 CRUD/scope/IAM 文档也不提供这些控制在统一 workload 下的延迟、模型调用或人工负担。

所以采购或架构评审应报告安全—效用向量：阻断率/漏报、正常任务影响、写/读/行动延迟、额外 model calls/tokens、持久字节/版本、回滚时间、人工审查量；没有 matched workload 时不做总成本排名。

**本节证据索引** — Claims: `OPS-C06`, `FM-PE-C04`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C22`, `OPS-C24`, `OPS-C27`. Evidence: `OPS-J06`, `FM-PE-J05`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J22`, `OPS-J24`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`.

## 8. 基准条件：把每个攻击成功数字绑定到它实际测量的阶段

AgentPoison 作者在三个 agent 的实验中报告平均 ASR 超过 80%、投毒率低于 0.1%、正常性能影响低于 1%；Sleeper 作者报告在“成功取回”的评估条件下，60–89% 产生攻击者意图动作；PoisonedEvolution 在 SkillClaw 的 10% attacker support 下报告 546/600（91.0%）SER，在结构不同的 Trace2Skill 上报告 369/600（61.5%）SER。它们不能直接比较：ASR、conditional action rate 与 SER 的分母、阶段和系统不同；SER 只测持久 artifact modification，不测 trigger、实际有害行动、凭证盗窃、外泄或破坏。

MemSecBench 提供 Write–Execute–Forget 协议，包含 310 cases、48 contexts 和 24-configuration matrix，是更接近生命周期的协议候选；但仍不能替代 adaptive extraction、collusive fragments、environmental injection 与 tenant authorization 的 full-chain 验证。

最低可比条件应固定：攻击支持比例/污染预算、写入口、benign pool、检索成功定义、planner/model、工具权限、会话跨度、删除/修复步骤、压力条件和正常任务基线；分别报告 inclusion、retrieval、action、harm、extraction 与 repair，不把它们折成一个“安全分”。

**本节证据索引** — Claims: `OPS-C02`, `OPS-C07`, `OPS-C08`, `FM-PE-C02`, `FM-PE-C03`, `FM-PE-C05`, `BEN-C16`, `OPS-C27`. Evidence: `OPS-J02`, `OPS-J07`, `OPS-J08`, `FM-PE-J03`, `FM-PE-J04`, `FM-PE-J06`, `FM-PE-J07`, `BEN-EV31`, `BEN-EV32`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`.

## 9. 失败与负面证据：局部控制经常被错误升级为完整保证

- **授权 ≠ 真值**：MutMem 可以让修改可签名、可追溯，但其作者明确否认这能证明内容真实。
- **store 更新 ≠ 行为更新**：STALE 描述 implicit policy adaptation gap；需要验证 planner 的实际行为而非只读回对象。
- **单条良性 ≠ 组合良性**：Salami 的威胁模型否定逐条检测就足够。
- **没有 API 写权限 ≠ 不可投毒**：MINJA/eTAMP 分别从 query/observation 和环境观察进入。
- **SER ≠ 完整危害**：PoisonedEvolution 指标不包含 trigger/action/harm 等后续阶段。
- **CRUD/TTL/scope ≠ end-to-end governance**：产品文档证明局部接口，未独立验证污染预防到 tenant-scoped action authorization 的完整链。
- **代码公开 ≠ 防御有效**：AgentPoison/OWASP/Brain0 的工程表面可检查，但本轮未运行。

这些负面边界共同要求证据升级门：文档能力只能支持“接口/机制存在”；固定源码只能支持“实现面可见”；执行后才能谈可运行；独立 matched benchmark 才能谈比较；真实多租户部署才可能支持生产保证。

**本节证据索引** — Claims: `OPS-C04`, `OPS-C05`, `OPS-C11`, `OPS-C13`, `OPS-C16`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C21`, `OPS-C22`, `OPS-C27`, `FM-PE-C05`, `GR-C032-2`, `GR-C-M009`. Evidence: `OPS-J04`, `OPS-J05`, `OPS-J11`, `OPS-J13`, `OPS-J16`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J21`, `OPS-J22`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`, `FM-PE-J06`, `FM-PE-J07`, `GR-V032-2`, `GR-V-M009-01`, `GR-V-M009-02`, `GR-V-M009-03`.

## 10. 替代方案与取舍

| 方案 | 能解决 | 不能单独解决 | 适用判断 |
|---|---|---|---|
| 写入 detector/policy | 已知单条恶意或规则违规 | query-only 语义、合谋片段、后续行动 | 必要但非充分的第一道门 |
| signed provenance/lineage | 身份、顺序、追溯、回滚定位 | 内容真假、合法主体被诱导 | 作为完整性账本，不作为 truth oracle |
| scope/IAM | 用户/会话/agent/租户隔离 | scope 内污染、planner 越权行动 | 与行动授权分层部署 |
| selected public view | 降低响应模型直接接触原始记忆 | 非响应通道、无限多轮累计泄漏 | 适合机密数据读取面 |
| snapshot rollback | 恢复特定存储版本 | 已传播到技能/画像/cache 的污染 | 必须配派生物依赖图 |
| provenance-diversity gate | 降低单一攻击簇晋升 | 协同攻击与通用阈值 | 目前只可作实验性晋升门 |

推荐不是选择其中一个，而是按威胁模型组合，并保持每层可单独关闭、度量和回滚。证据不足时，敏感工具调用应假设记忆内容仍不可信，即使其写入、签名和取回全部“合法”。

**本节证据索引** — Claims: `OPS-C10`, `OPS-C11`, `OPS-C12`, `OPS-C13`, `OPS-C14`, `OPS-C15`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C21`, `OPS-C22`, `OPS-C24`, `OPS-C25`, `FM-PE-C04`. Evidence: `OPS-J10`, `OPS-J11`, `OPS-J12`, `OPS-J13`, `OPS-J14`, `OPS-J15`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J21`, `OPS-J22`, `OPS-J24`, `OPS-J25`, `FM-PE-J05`.

## 11. 共识、少数路线与矛盾

**强共识**：持久化改变了威胁的时间尺度；攻击入口不局限于直接 store write；应把 write、retrieve、action 和 repair 分段；来源/版本/审计是必要基础；任何敏感行动都不能只因“来自 memory”而被信任。

**正在形成的共识**：控制应覆盖组合片段、经验晋升和适应性多轮泄漏；逻辑删除必须扩展到派生物和行为依赖。这里的“共识”只是本语料的多来源趋同。

**少数/竞争路线**：cryptographic lineage 强调可验证转换，DP-MemView 强调响应视图与累计隐私，Memory Guard 强调 detector/policy/snapshot，产品平台强调 CRUD/scope/IAM。它们并不矛盾，但解决对象不同。真正矛盾来自证据升级：产品文档常能证明 API 边界，却不能独立证明 full-chain security；攻击论文的高成功率也不能直接代表生产风险概率。

**本节证据索引** — Claims: `OPS-C01`, `OPS-C04`, `OPS-C05`, `OPS-C07`, `OPS-C09`, `OPS-C11`, `OPS-C12`, `OPS-C13`, `OPS-C14`, `OPS-C15`, `OPS-C18`, `OPS-C19`, `OPS-C22`, `OPS-C24`, `OPS-C27`, `FM-PE-C01`, `FM-PE-C05`. Evidence: `OPS-J01`, `OPS-J04`, `OPS-J05`, `OPS-J07`, `OPS-J09`, `OPS-J11`, `OPS-J12`, `OPS-J13`, `OPS-J14`, `OPS-J15`, `OPS-J18`, `OPS-J19`, `OPS-J22`, `OPS-J24`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J06`, `FM-PE-J07`.

## 12. 决策门与可执行要求

1. **任何内容进入长期 store 前**：要求来源类、主体、scope、写入理由、版本 predecessor；无法归属的内容隔离。
2. **任何轨迹晋升为摘要/技能/画像前**：保留贡献来源，进行多 session/来源审查；当前 provenance-diversity 数字只能作为试验配置。
3. **任何 retrieval 进入 planner 前**：服务端 scope 过滤、冲突/陈旧检查、最小公共视图；记录实际取回集合以支持组合审计。
4. **任何敏感 tool action 前**：按当前主体和政策再授权，不继承 memory 的信任等级。
5. **任何 delete/rollback 完成前**：枚举原对象、revisions、embedding、profile、cache、摘要、技能、backup 与行为依赖；未验证的部分显式标为 residual。
6. **任何安全宣称发布前**：区分作者结果、静态仓库、实际执行、独立复现与生产部署；不把 ASR、conditional action rate、SER 或 benchmark lifecycle score 混为一个数。

**本节证据索引** — Claims: `OPS-C07`, `OPS-C11`, `OPS-C12`, `OPS-C13`, `OPS-C15`, `OPS-C16`, `OPS-C18`, `OPS-C19`, `OPS-C20`, `OPS-C21`, `OPS-C22`, `OPS-C24`, `OPS-C25`, `FM-PE-C01`, `FM-PE-C04`, `FM-PE-C05`, `BEN-C16`. Evidence: `OPS-J07`, `OPS-J11`, `OPS-J12`, `OPS-J13`, `OPS-J15`, `OPS-J16`, `OPS-J18`, `OPS-J19`, `OPS-J20`, `OPS-J21`, `OPS-J22`, `OPS-J24`, `OPS-J25`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J05`, `FM-PE-J06`, `FM-PE-J07`, `BEN-EV31`, `BEN-EV32`.

## 13. 分层深选：覆盖入口、持久化、隐私、治理、实现与反证

全部选自已打开 T1；分层的目标是机制覆盖与反证，不是“论文越新越好”。

| 层 | 代表来源（日期/版本） | 选择原因 | claim → evidence |
|---|---|---|---|
| foundation attack | AgentPoison（2024-07-17） | memory/RAG 后门与作者结果基线 | `OPS-C01`,`OPS-C02` → `OPS-J01`,`OPS-J02` |
| privacy | MEXTRA（ACL 2025） | 黑盒私密信息抽取 | `OPS-C03` → `OPS-J03` |
| indirect write | MINJA（2025-03-05）、eTAMP（2026-04-07） | query/observation 与环境入口 | `OPS-C04..06` → `OPS-J04..06` |
| lifecycle | Sleeper（2026-05-14）、MemSecBench（2026-07-29） | write→retrieve→action 与 Write–Execute–Forget | `OPS-C07`,`OPS-C08`,`BEN-C16` → `OPS-J07`,`OPS-J08`,`BEN-EV31`,`BEN-EV32` |
| frontier attacks | MAFIA（2026-08-04）、Salami（2026-08-03） | query-only audit 与组合片段 | `OPS-C10`,`OPS-C11` → `OPS-J10`,`OPS-J11` |
| integrity/privacy control | MutMem（2026-08-03）、DP-MemView（2026-08-04） | signed lineage 与 adaptive transcript privacy | `OPS-C12..15` → `OPS-J12..15` |
| behavior negative | STALE（2026-08-03） | store 更新但行为陈旧 | `OPS-C16`,`OPS-C17` → `OPS-J16`,`OPS-J17` |
| engineering control | OWASP Memory Guard pinned `425616…`（2026-08-10） | detector/policy/snapshot/audit 表面 | `OPS-C24`,`OPS-C25`,`GR-C-M009` → `OPS-J24`,`OPS-J25`,`GR-V-M009-02` |
| promotion frontier | PoisonedEvolution v2（2026-08-07） | 轨迹→技能的证据晋升边界 | `FM-PE-C01..05` → `FM-PE-J01..07` |

独立性限制：许多数值是作者报告；仓库与论文可能同一组织；产品文档是能力边界而非独立安全验证。分层确保了观点覆盖，不能把来源数量当作生产置信度。

**本节证据索引** — Claims: `OPS-C01`, `OPS-C02`, `OPS-C03`, `OPS-C04`, `OPS-C05`, `OPS-C06`, `OPS-C07`, `OPS-C08`, `OPS-C10`, `OPS-C11`, `OPS-C12`, `OPS-C13`, `OPS-C14`, `OPS-C15`, `OPS-C16`, `OPS-C17`, `OPS-C24`, `OPS-C25`, `GR-C-M009`, `BEN-C16`, `FM-PE-C01`, `FM-PE-C02`, `FM-PE-C03`, `FM-PE-C04`, `FM-PE-C05`. Evidence: `OPS-J01`, `OPS-J02`, `OPS-J03`, `OPS-J04`, `OPS-J05`, `OPS-J06`, `OPS-J07`, `OPS-J08`, `OPS-J10`, `OPS-J11`, `OPS-J12`, `OPS-J13`, `OPS-J14`, `OPS-J15`, `OPS-J16`, `OPS-J17`, `OPS-J24`, `OPS-J25`, `GR-V-M009-01`, `GR-V-M009-02`, `GR-V-M009-03`, `BEN-EV31`, `BEN-EV32`, `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J03`, `FM-PE-J04`, `FM-PE-J05`, `FM-PE-J06`, `FM-PE-J07`.

## 14. 残余缺口、可逆条件与真实饱和

`SAT-CL-MM-C12` 保留九个开放缺口：`GAP-CNS-02` end-to-end 删除契约；`GAP-CNS-05` shared/team memory 的动态权限、撤销、投毒与跨租户验证；`GAP-CNS-06` 长期真实用户的隐私/纠正/删除联合研究；`GAP-CNS-07` adaptive poisoning 到 action authorization/deletion repair 的 full-chain 协议；`GAP-CNS-08` 可固定完整协议变量的 harness；`GAP-CNS-09` model-native/latent memory 的安全与可删性对照；`GAP-CNS-10` pinned install/test 与独立下游部署；`GAP-CNS-11` coding/project memory 的隔离、secret、失效与演化协议；`GAP-CNS-12` 全链成本。任一项出现独立、matched、可运行证据，都可能改变本稿控制优先级。

真实饱和过程包含一次重要变化，不能只报最后“两轮没变化”：

- `FM-EV-CLUSTER-MM-C12-11`：查询 `SAT11-C12-OA`, `SAT11-FOUNDATION-OA`, `SAT11-GH-C12C13`；审计 21 个唯一候选，新增 1 entity/1 high-signal，`PoisonedEvolution` 以 `FM-PE-E01` 并入并改变“经验晋升”命题；`material_change=true`。
- `FM-EV-CLUSTER-MM-C12-12`：查询 `SAT12-C12-ARXIV`, `SAT12-FOUNDATION-ARXIV`, `SAT12-GH-C12C13`；审计 30 个唯一候选；无新实体/高信号/一阶簇/立场，边界与命题均未变。
- `FM-EV-CLUSTER-MM-C12-13`：查询 `SAT13-C06C12C13-12M-OA`, `SAT13-C06C12C13-OA`, `SAT13-GH-C06C12C13`；审计 19 个唯一候选；再次无物质变化。

最终以 cycle 12+13 作为连续两轮零物质变化的停止证据；范围内累计 36 targeted queries、31 deep-verified memberships。饱和仅说明当前搜索下边界/决策命题稳定，不等于九个缺口已经解决，也不等于任何仓库经过运行验证。

**本节证据索引** — Claims: `FM-PE-C01`, `FM-PE-C02`, `FM-PE-C03`, `FM-PE-C04`, `FM-PE-C05`, `OPS-C27`, `GR-C032-2`, `BEN-C16`. Evidence: `FM-PE-J01`, `FM-PE-J02`, `FM-PE-J03`, `FM-PE-J04`, `FM-PE-J05`, `FM-PE-J06`, `FM-PE-J07`, `OPS-J27`, `OPS-J28`, `OPS-J29`, `OPS-J30`, `OPS-J31`, `OPS-J32`, `OPS-J33`, `OPS-J34`, `OPS-J35`, `OPS-J36`, `OPS-J37`, `OPS-J38`, `OPS-J39`, `OPS-J40`, `OPS-J41`, `OPS-J42`, `OPS-J43`, `OPS-J44`, `OPS-J45`, `GR-V032-2`, `BEN-EV31`, `BEN-EV32`. Saturation ledger IDs: `SAT-CL-MM-C12`, `FM-EV-CLUSTER-MM-C12-11`, `FM-EV-CLUSTER-MM-C12-12`, `FM-EV-CLUSTER-MM-C12-13`.



<!-- synthesis:CLY-C12 claims:OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C10,OPS-C11,OPS-C14,OPS-C16,OPS-C24,OPS-C25,FM-PE-C01,FM-PE-C04,FM-PE-C05 clusters:MM-C12 -->
