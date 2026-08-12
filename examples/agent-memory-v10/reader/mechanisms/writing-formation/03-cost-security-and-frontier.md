# 形成失败、系统成本与研究前沿：为什么“记得更多”可能更差

写入算法的表面目标是把经历变成有用状态，真实目标却是一个长期净收益：未来任务得到的帮助，要超过形成时的信息损失、模型调用、存储增长、错误持久化、隐私与安全风险。当前许多论文只报告最终 QA 或 task success，因而无法回答复杂形成管线到底在哪一步创造价值。

## 1. 形成是一串不可逆或难逆的信息瓶颈

```text
raw stream
  ──select──> captured subset
  ──segment──> evidence units
  ──extract──> candidates
  ──merge──> canonical objects
  ──compress──> summaries/profiles/skills
  ──admit──> active state
```

每一步都可能减少信息。只要原输入或 lineage 仍在，错误可以重处理；一旦原文被删除、候选被合并、技能被执行，恢复成本显著增加。形成算法因此不只是“生成质量”，也是信息保留与可逆性策略。

## 2. 六种常见失败及其下游表现

### 2.1 Capture omission

关键事件从未进入 journal。后续系统会把它误诊为检索失败，实际上再好的 retriever 也无法找回。应测 capture recall、hook error 与未完成 session，而非只看 store size。

### 2.2 Selection bias

重要性模型偏向当前目标、显著情绪或高重复内容，忽略低频但决定性的条件。长期后果是 Memory 看似紧凑，遇到新 query distribution 时没有必要证据。

### 2.3 Extraction hallucination 与 source loss

模型把隐含猜测写成事实，或删掉否定词、时间、主体和适用条件。若候选没有 source span，系统无法区分“源中有错”与“抽取器制造”。

### 2.4 False merge / false split

false merge 会让新值覆盖无关状态；false split 产生重复 identity 和冲突候选。两者常由 candidate retrieval 和 entity resolution 共同造成，不应全部归因于 LLM。

### 2.5 Projection divergence

权威记录已写入，embedding、FTS、graph 或 summary 部分失败。检索结果依赖恰好命中的通道，更新/删除也可能只影响部分投影。

### 2.6 Error promotion

错误事实经过多次检索、反思或成功任务，被晋升为 profile、rule 或 executable skill。它从一次错误变成系统性 policy，影响范围和修复成本都扩大。

## 3. 形成成本到底花在哪里

[2026 年的系统表征研究](https://arxiv.org/abs/2606.06448)将 Agent Memory 拆成 ingestion、construction、storage、retrieval、prompt assembly、generation 和 maintenance。它的重要贡献不是给出通用赢家，而是指出复杂方法常把成本从 serving 转移到 construction。

一个完整成本账本至少需要：

| 阶段 | 需要记录的量 |
|---|---|
| capture | events、raw bytes、redaction、hook latency/failure |
| segment/extract | model calls、input/output tokens、batch size、retry、candidate count |
| related-state read | candidate_k、retrieval route、tokens supplied to mutation model |
| mutation/admission | decision calls、conflict/quarantine rate、human review |
| commit/index | transaction time、write amplification、embedding/graph fan-out |
| maintenance | reprocess、reindex、repair、migration、snapshot/storage growth |
| downstream | compiled tokens、answer/action benefit、stale/error impact |

只报告“节省了 query tokens”会忽略形成阶段多次 LLM 调用；只报告写入延迟又会忽略复杂对象减少长期 prompt 的收益。应比较相同 task horizon 下的累计曲线，而不是一次 query 的单点。

## 4. Raw retain、摘要和结构化形成没有固定排名

[Retain or Consolidate?](https://arxiv.org/abs/2607.17545)把 retention 与 consolidation 的关系表达为预算条件：保留原始细节有助于未来未知问题，consolidation 在紧 token 预算下提高覆盖，却可能删掉 query-critical evidence。这个结论反对两个极端：所有内容都应提前摘要，或永远只保留 raw history。

[LightMem 独立复现](https://arxiv.org/abs/2607.29104)进一步表明，在固定 memory store 时，替换 retriever 和 candidate depth 就能显著改变结果；匹配 retrieval depth 后，raw-turn baseline 常常更强，而 constructed memory 的优势更依赖严格 answer-token budget。它没有证明所有形成算法无效，而是证明必须匹配 reader、retriever、候选和 token 预算。

公平对照至少包含：

- 同一 raw input 与同一模型；
- raw retain、summary、typed fact、graph/structured 等形成路线；
- 相同 candidate depth 和 compiled memory tokens；
- source-span/oracle recall 与 final answer/action 同时报告；
- construction + serving + maintenance 累计成本；
- update、conflict 与 delete 测试，而不只是静态 QA。

## 5. 写入是持久攻击面

被保存内容可以在数小时或数周后触发，不必在当前轮说服模型。攻击链包括：

```text
malicious / misleading input
  → capture
  → extraction or summary removes suspicious context
  → admission/promotion
  → future retrieval
  → context interpreted as instruction
  → tool action
```

写入 detector 只能拦截已知模式；provenance 说明来源，不证明内容安全；签名证明谁写入，不证明写入者未被操纵。需要 source class、quarantine、promotion gate、minimum disclosure 和 action-time authorization共同工作。

### 5.1 形成器本身会放大攻击

摘要可能把“网页中出现的恶意指令”改写成看似可信的规则；fact extractor 可能把攻击文本的陈述当成用户偏好；skill distiller 可能把一次被投毒的成功轨迹编译为可执行 procedure。形成阶段因此需要测**攻击内容怎样改变对象类型和 authority**，而不只测是否进入向量库。

### 5.2 错误经验晋升

[PoisonedEvolution](https://arxiv.org/html/2608.05563v2)把攻击推进到 self-evolving skill：恶意 trajectory 可影响之后被提炼和复用的 instruction。这类结果属于作者协议，不能直接当现实攻击概率，但它说明 promotion boundary 是独立安全检查点。

## 6. 来源支持、隐私和可删除性之间的张力

保留完整 source span 有利于审计与修正，却扩大敏感原文的保存面；只保存 hash/receipt 保护内容，却可能无法重新解释语义；使用受控 pointer 可以在需要时 hydrate，但需要权限、key lifecycle 和删除传播。

一种常见分层是：

- ledger 保存最小 receipt 与加密/受控 payload pointer；
- active object 保存任务所需字段、来源引用和 policy；
- index 只保存必要表示和 object ID；
- compiler 在当前 principal/purpose 下 hydrate 最小证据。

这仍不能自动解决“派生 summary 已泄露原始敏感信息”。删除需要枚举对象 lineage 和已经形成的 procedure/profile，而不仅是原文 pointer。

## 7. 最新研究正在修改形成链的哪一层

| 研究方向 | 正在改的层 | 旧做法不足 | 关键待证 |
|---|---|---|---|
| atomic/typed formation | segment/extract | chunk/summary 粘连多个断言 | 粒度误差与长期净收益 |
| dynamic links and dependency | extract/merge | 相似关系不能指导修订传播 | typed edge ground truth、repair |
| source-supported transaction | admission/commit | 模型输出直接写入、无法恢复 | 并发、跨后端、崩溃独立实验 |
| budget-aware operator selection | form/manage | 固定阈值不适配 query horizon | matched-budget 长期曲线 |
| learned memory control | decision policy | 手工规则难适应任务变化 | policy drift、不可逆错误、安全约束 |
| poisoning-aware promotion | admission | 检测只覆盖原始输入 | 从对象形成到未来行动的完整链 |
| trajectory database | commit/evolution | 只检查单条记录，不检查依赖状态 | state-level invariant 与 benchmark |

这些方向相互依赖：typed object 没有 transaction，更新仍可能部分提交；learned policy 没有 source/rollback，会把探索变成持久风险；安全 admission 没有 action trace，无法证明防御改变最终行为。

## 8. 评测应该怎样定位形成失败

一次完整实验可以设置多个检查点：

1. **capture oracle**：gold event 是否进入；
2. **candidate oracle**：必要 assertion/relation/procedure 是否被提出；
3. **source coverage**：候选字段是否能回到原文；
4. **mutation correctness**：ADD/MERGE/SUPERSEDE/CONFLICT 是否正确；
5. **state integrity**：current/history/lineage 是否一致；
6. **projection freshness**：各索引是否覆盖 committed revision；
7. **retrieval/context**：必要对象是否进入有限上下文；
8. **action outcome**：Agent 是否因此做对且未越权；
9. **cost/failure**：每阶段 token、latency、storage、retry、repair。

MemoryAgentBench 等 incremental benchmark 开始覆盖更新能力，MemSecBench 等安全协议开始覆盖 Write–Execute–Forget；它们仍不能替代一套共享的 formation-stage trace。不同 task/model/backend 的分数不应拼成总榜。

## 9. 当前能形成的判断

较稳固的判断是：raw evidence 与 derived state 应分层；形成器输出应视为 proposal；identity、source、scope、version 与 policy 需要在 commit 前确定；复杂管线必须记录 projection/repair 状态。

条件性判断是：typed fact、summary、graph 和 learned controller 都可能在特定 budget/task 下改善后续使用，但现有证据不支持“越早抽取、越结构化、越主动写入越好”。最薄弱的证据集中在跨后端 transaction、长期 policy learning、派生删除和 formation-to-action 安全闭环。

回到短入口：[写入与记忆形成](../02-write-and-formation.md)。对象形成后怎样演化和遗忘，见[生命周期与演化](../04-lifecycle-and-evolution.md)。
