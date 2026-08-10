# Agent Memory 2026：执行结论

**As of:** 2026-08-10

这份执行稿从簇级 deep packets 和跨来源 synthesis ledger 反向生成，不新增来源事实。完整输入、边界与失败门见[方法与限制](09-method-and-limitations.md)。

<!-- process:method -->

## 九个决策判断

### 1. 把 Memory 当作六段可审计状态链

可部署的 external Agent Memory 更适合被建模为六段链：typed/provenanced data plane → multi-index candidate access → scoped/time-aware ranking → budgeted context compilation → explicit mutation/transaction control → action-time authorization；任何一层丢失 scope、version 或 provenance，后层不能可靠补回。
<!-- synthesis:CNS-S09 claims:FND-C17,FND-C21,FND-C23,REP-C12,REP-C14,REP-C22,EXP-C18,EXP-C19,EXP-C20,OPS-C01,OPS-C07,OPS-C12,OPS-C14,OPS-C16,OPS-C24,OPS-C27,BEN-C25 clusters:MM-C01,MM-C02,MM-C03,MM-C04,MM-C05,MM-C07,MM-C08,MM-C11,MM-C12 -->

**条件：** 适用于 external、persistent、mutable、multi-session 或 action-bearing memory；静态只读问答可裁剪 mutation 与 action authorization，但仍应记录 retrieval budget。

**限制：** 没有一个已执行仓库在本包中验证了全部六层；层间接口和成本尚无标准。

**推翻条件：** 若端到端独立测试证明缺少 version/scope/provenance 的简化链在 correction、tenant isolation、rollback、security 与 action success 上同样可靠且显著更低成本，则允许裁剪对应层。

### 2. 核心是生命周期控制，不只是存储与检索

对于跨会话、可变且会影响后续行动的 Agent Memory，核心工程边界是完整 lifecycle/control，而不是单独的 store 或 retrieval；固定历史、只读问答是条件外的较小问题。
<!-- synthesis:CNS-S01 claims:FND-C03,FND-C05,FND-C11,FND-C14,FND-C17,FND-C21,FND-C23,BEN-C03,BEN-C05,BEN-C06,BEN-C16,OPS-C07,OPS-C27,REP-C06 clusters:MM-C01,MM-C02,MM-C04,MM-C05,MM-C07,MM-C13 -->

**条件：** 仅适用于需要跨 session 持久化、更新、冲突处理、遗忘/删除、恢复或行动授权的系统；不外推到一次性检索、静态语料问答或纯上下文缓存。

**限制：** 缺少同一 backend、同一模型、同一预算下 passive store 与完整 lifecycle-control 的独立端到端对照；多项 2026 机制为作者预印本。

**推翻条件：** 若跨多个 backend 的独立匹配实验表明 passive/raw-history 基线在更新、冲突、忘却、恢复、行动成功和成本上持续等同或优于显式 lifecycle-control，则把判断降为 mixed，并将控制面改为按需选件。

### 3. 结构化表示有条件优于 flat top-k

关系、时间、版本和冲突密集的任务通常需要超越 flat similarity top-k 的表示与访问路径，但现有证据不支持 graph、bitemporal 或 constructed memory 对所有任务普遍更优。
<!-- synthesis:CNS-S02 claims:REP-C01,REP-C02,REP-C03,REP-C05,REP-C06,REP-C10,REP-C11,REP-C14,REP-C16,REP-C22,FND-C09 clusters:MM-C02,MM-C03,MM-C04,MM-C07,MM-C13 -->

**条件：** 当问题显式要求 entity relation、as-of、history、supersession、conflict 或跨事件导航时成立；若任务是局部事实问答且 raw evidence 可直接检索，则 flat/hybrid baseline 仍可能更好。

**限制：** 多数近期机制是 2026 预印本；仓库未执行；时间过滤位置、graph maintenance、candidate budget 与 reader model 不一致。

**推翻条件：** 若公开、可复现、预算与 reader 对齐的对照显示 flat retrieval 在 temporal/conflict/relational tasks 上持续匹配结构化方案且维护成本更低，则撤销“通常需要超越 flat”的判断；若结构化方案在多 backend 上稳定领先，提升为 dominant。

### 4. 写入、合并与遗忘不存在通吃策略

Selective write、consolidation 与 forgetting 能在特定预算和任务流下降低上下文成本、减少噪声或覆盖更多证据，但也会造成 answer-relevant detail 丢失、错误删除、旧依赖残留和不可见的行为漂移；不存在无条件最优操作符。
<!-- synthesis:CNS-S03 claims:FND-C06,FND-C14,FND-C16,FND-C19,FND-C20,FND-C21,FND-C22,REP-C03,REP-C05,REP-C06,EXP-C13,EXP-C15,BEN-C05,BEN-C06 clusters:MM-C05,MM-C07,MM-C08,MM-C10,MM-C13 -->

**条件：** 操作符必须按 token/storage/latency 预算、query distribution、可恢复性、删除语义和状态有效期选择；不可逆 delete/overwrite 需受事务与回滚约束。

**限制：** 没有统一协议同时测 detail retention、action success、privacy deletion、rollback completeness 与长期成本；MeMento、MemCon、ForgetEval 等结果仍为作者协议。

**推翻条件：** 若多系统 matched-budget 复现发现某一 consolidate/forget 策略在细节保留、行动、删除、恢复和成本上跨任务稳定占优，则将 disputed 收窄；若 raw retention 持续占优，则停止默认压缩。

### 5. 个性化收益与隐私、漂移共同增长

Personalization 的可用性依赖持续 user/identity state，但 profile 越丰富、持续越久，privacy extraction、跨域泄露、fabricated profile、identity drift、stale premise 与 sycophancy 的风险面也越大；净效用尚无通用结论。
<!-- synthesis:CNS-S04 claims:FND-C05,REP-C07,REP-C13,REP-C14,EXP-C12,EXP-C13,EXP-C19,OPS-C03,OPS-C14,OPS-C15,OPS-C16,OPS-C18,OPS-C19 clusters:MM-C08,MM-C10,MM-C12,MM-C13 -->

**条件：** 适用于跨 session 个性化、身份连续性或 preference-conditioned action；必须保留 principal scope、valid time、来源、同意、纠正、删除和下游依赖。

**限制：** 缺少长期真实用户研究和 matched no-profile baseline；vendor 文档不是隔离或删除传播证明；STALE 与 POLAR/MeMento 协议不同。

**推翻条件：** 若长期独立研究在明确同意、纠正与删除协议下显示丰富 profile 稳定提升行为且不增加 extraction、stale、cross-scope 或 sycophancy failure，则上调净效用；反之若最小 profile 同样有效，应收缩持久化。

### 6. 共享记忆的复用收益尚未独立验证

Shared memory 可以扩大经验复用和协作可见性，但只有把 principal、private/shared scope、provenance、dynamic policy、revocation 与 conflict 作为一等状态时才构成可治理的组织记忆；其协调收益与污染、authority 和 isolation 风险尚未被共同验证。
<!-- synthesis:CNS-S05 claims:EXP-C05,EXP-C06,EXP-C18,EXP-C22,BEN-C11,BEN-C13,OPS-C10,OPS-C11,OPS-C19,OPS-C26,OPS-C27 clusters:MM-C06,MM-C08,MM-C11,MM-C12,MM-C13 -->

**条件：** 仅在任务确需跨 agent/team/tenant 复用时成立；默认不能把用户 profile、local world state 或未验证 procedure 放进全局池。

**限制：** 没有同一任务、同一 trust boundary 下 flat pool、scoped memory 与无共享 baseline 的独立对照；多数仓库未执行。

**推翻条件：** 若独立部署测试显示 flat global store 在动态权限、撤销、冲突和 poisoning 下与 scoped/provenance design 同样安全且协调更好，则降低 control-plane 要求；若隔离故障普遍出现，则默认禁用跨 tenant 共享。

### 7. 单一 leaderboard 不代表总体能力

Agent Memory 排名对 horizon、history construction、write/update/forget protocol、retriever、k/token/tool budget、model/judge 以及是否要求 action-use 高度敏感；单一 leaderboard 不能代表整体能力。
<!-- synthesis:CNS-S06 claims:BEN-C01,BEN-C02,BEN-C03,BEN-C05,BEN-C07,BEN-C12,BEN-C16,BEN-C22,BEN-C25,REP-C05,REP-C06,REP-C17,REP-C18,EXP-C21,FND-C13 clusters:MM-C04,MM-C05,MM-C07,MM-C08,MM-C10,MM-C11,MM-C12,MM-C13 -->

**条件：** 所有跨系统数字比较必须共享 protocol fingerprint；跨 family 只能比较覆盖、假设和 failure mode，不能合并总分。

**限制：** 本次未执行统一 harness；部分 benchmark runner 或 artifact 仍未确认完整；judge/annotation sensitivity 未独立审计。

**推翻条件：** 只有预注册、公开、同模型同数据同预算的多 family rerun 显示排名对 protocol 变化稳定，才允许把单一排行榜作为总体能力近似。

### 8. 安全必须覆盖 write → retrieve → act 全链

Persistent memory 是跨时间的 write→store/mutate→retrieve→prompt→action 攻击与隐私链；输入过滤或单条记录检查不能覆盖 query-only、environmental、sleeper、collusive、extraction 与 stale-dependency failure。
<!-- synthesis:CNS-S11 claims:OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C09,OPS-C10,OPS-C11,OPS-C14,OPS-C16,OPS-C27,REP-C07,EXP-C18,BEN-C16 clusters:MM-C05,MM-C08,MM-C11,MM-C12,MM-C13 -->

**条件：** 适用于任何会把不可信观察或 derived summary 持久化并在未来影响 prompt/tool/action 的系统。

**限制：** 攻击发生率与生产 prevalence 未被证明；没有共同防御 benchmark 或独立 vendor head-to-head。

**推翻条件：** 若独立全链测试跨多 backend 证明单一 write filter 在 adaptive query、environmental、collusive、extraction、stale repair 和 sensitive action 上均充分，才收窄多层控制要求。

### 9. GitHub 是工程一手证据，但不是采用证明

GitHub 与官方产品文档是判断真实架构、integration surface、migration、tests/CI、license、release 和治理 API 的一等证据；但 README、目录或 workflow 存在本身不证明执行成功、比较性能、安全、采用或生产成熟度。
<!-- synthesis:CNS-S12 claims:FND-C04,FND-C10,FND-C12,REP-C10,REP-C11,REP-C12,REP-C13,REP-C14,REP-C15,REP-C19,EXP-C22,OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C24,OPS-C25,OPS-C26,OPS-C27,BEN-C18,BEN-C19,BEN-C20,BEN-C21,BEN-C23 clusters:MM-C01,MM-C02,MM-C03,MM-C04,MM-C06,MM-C09,MM-C11,MM-C12,MM-C13,MM-C16 -->

**条件：** 结论只覆盖 inspected commit/page 的可见实现表面；动态状态需按 as-of 重查。

**限制：** 七包没有隔离安装/测试、release cadence time series、downstream deployment 样本或统一维护健康审计。

**推翻条件：** 具体仓库只有在 pinned execution、tests、release/maintenance history、independent integration/adoption 和 failure evidence 补齐后，才可升级成熟度；本方法边界本身不因某个项目成功而撤销。

## 阅读路线

- 5 分钟：本页。
- 30 分钟：[字段树](02-field-tree.md) → [架构全景](03-landscape-synthesis.md) → [共识与争议](05-consensus-controversies.md) → [GitHub 雷达](06-github-trend-radar.md)。
- 专家：进入 `../clusters/` 的 14 个主簇和 `../projects/` 的固定提交项目深潜。
