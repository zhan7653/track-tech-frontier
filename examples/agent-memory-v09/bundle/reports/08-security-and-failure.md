# Agent Memory 安全、治理与运行风险

## Core finding: the security boundary is a lifecycle, not a prompt filter

Persistent memory changes an untrusted observation into a durable future input. The evidence supports treating the threat as a chain:

`untrusted write → persisted/derived record → retrieval/ranking → prompt-visible state → tool/action`

AgentPoison establishes a retrieval-triggered backdoor model [OPS-C01] and reports its own three-agent results above 80% attack success at <0.1% poison rate [OPS-C02]; MINJA narrows the attacker prerequisites to interaction and observation [OPS-C04]; eTAMP extends the write path to manipulated environment observations without store access [OPS-C05]. The sleeper-memory study then evaluates the entire write/retrieve/action progression [OPS-C07]. These are distinct mechanisms, but they converge on an operational consequence: an input-side filter is not a complete memory control. <!-- synthesis:OPS-Y01 claims:OPS-C01,OPS-C02,OPS-C04,OPS-C05,OPS-C07 clusters:security-operations -->

The recent frontier attacks the assumptions inside individual controls. MAFIA explicitly targets query-only access in the presence of large benign pools and active input auditing [OPS-C10]. Salami Attack targets a different assumption: that maliciousness is legible at the level of one stored record [OPS-C11]. The 2026 MPBench study catalogs four write channels and nine structural vulnerabilities in its own taxonomy [OPS-C09]. Together they make a practical case for correlating write provenance, temporal sequence, retrieval competition, and eventual action; they do not establish a universal attack rate. <!-- synthesis:OPS-Y02 claims:OPS-C09,OPS-C10,OPS-C11 clusters:security-operations -->

## Control points and their failure modes

| Chain point | Required control | Failure mode exposed by sources | Evidence boundary |
|---|---|---|---|
| Write | Source class, tenant/authority, policy admission, quarantine | Query-only and environment-derived poisoning [OPS-C04][OPS-C05] | Attack papers, not prevalence studies |
| Store/mutate | Immutable receipt, revision, signer/authority and reversible labels | Unauthorized adaptation can be indistinguishable from tampering | MutMem attributes changes but does not prove truth [OPS-C12][OPS-C13] |
| Retrieve | Scope, purpose, freshness/conflict and privacy budget | Large pools and collusive fragments defeat simple per-record checking [OPS-C10][OPS-C11] | No common defense benchmark |
| Act | Re-authorize tool/action against current tenant, policy and provenance | A retrieved poison can turn into later agentic action [OPS-C08] | Experimental model/version scope |
| Delete/repair | Item-level deletion, retention, reindex/derived-artifact repair | Updating a stored fact need not remove stale behavioral dependence [OPS-C16][OPS-C17] | STALE is personalized-response scoped |

Provenance is necessary but insufficient: MutMem gives a concrete signed-transition pattern [OPS-C12], while StateAuditor distinguishes chronological evidence from semantic supersession [OPS-C17]. A design that can prove *who changed a weight* still needs an authority model for *who may change it* and a truth/reconciliation process for *whether it should change*. <!-- synthesis:OPS-Y03 claims:OPS-C12,OPS-C13,OPS-C16,OPS-C17 clusters:security-operations -->

Privacy is also read- and transcript-shaped, not merely encryption-at-rest. MEXTRA provides peer-reviewed evidence that black-box prompts can target private agent memory [OPS-C03]. DP-MemView instead restricts the response model to a selected public view and accounts for repeated disclosure under a stated contract [OPS-C14][OPS-C15]. This is a useful separation of raw-store access from inference through repeated responses, but it leaves raw export, logs, tool traces and out-of-contract paths as separate surfaces. <!-- synthesis:OPS-Y04 claims:OPS-C03,OPS-C14,OPS-C15 clusters:security-operations -->

## Production APIs: governance surface, not proof of safety

The official systems expose useful control-plane hooks but none is independent evidence of a fully defended pipeline. Microsoft documents item CRUD, default TTL, direct remember-or-forget, and scope-based segmentation [OPS-C18][OPS-C19]. AWS Classic documents caller-chosen `memoryId`, summarized-session memory, failure-log delivery, and deletion of stored sessions [OPS-C20][OPS-C21]. Google documents memory retrieval, revision inspection, IAM Conditions, and an endpoint-region processing statement [OPS-C22][OPS-C23]. Those are implementation boundaries that an operator can wire into governance; they do not validate isolation, deletion propagation, resistance to poisoning, or action authorization in a deployed workload. <!-- synthesis:OPS-Y05 claims:OPS-C18,OPS-C19,OPS-C20,OPS-C21,OPS-C22,OPS-C23 clusters:security-operations -->

Open implementations make the gap inspectable. Agent Memory Guard documents a write→detector→policy path and snapshot rollback [OPS-C24], source classes propagated in security events [OPS-C25], and configurable protected/immutable keys. Mem0 documents multiple memory scopes and `user_id` filtered retrieval [OPS-C26]. These are integration patterns, not measured proof that a tenant cannot cross scope or that a policy blocks adaptive poison. The packet deliberately retains no such claim.

## Cost, latency, storage growth and observability

Security controls create compounding operational costs at every state transition: write classifiers/LLM review, immutable receipts and revisions, provenance indexes, re-embedding/retrieval filtering, audit logs, deletion propagation, and action-time reauthorization. eTAMP's author-reported eightfold stress amplification [OPS-C06] is also a reminder that operational conditions affect observed risk. No deep source here offers a cross-system, independently replicated breakdown of that cost. MutMem reports a signed-transition latency for its own system, and product/repository documents describe APIs, but those are not comparable production budgets. Treat latency, storage growth, replay/reindex time, and false-positive/false-negative burden as evaluation inputs rather than accepting headline microbenchmarks.

Minimum telemetry should join a memory ID/revision with tenant/scope, principal, source class, admission decision, policy version, content/embedding lineage, retrieval rank, prompt injection point, tool/action authorization, TTL/deletion state, and repair/rollback outcome. Without this join, a team can observe writes or actions but not prove the causal path between them.

<!-- synthesis:OPS-AUTO-01 claims:OPS-C06 clusters:MM-C12 -->

## Security regression and production evaluation

1. Test every write channel separately: direct user text, tool/web content, agent-authored consolidation, import/migration, and cross-agent/shared-memory synchronization.
2. For each, replay clean and poisoned trajectories through store, retrieval and a sensitive tool action. Measure write admission, persistence, retrieval rank, action success, recovery time, false blocks, and tenant-scope violations—not only classifier accuracy.
3. Include MAFIA-style benign dilution/auditing [OPS-C10], Salami-style collusion [OPS-C11], eTAMP environmental writes [OPS-C05], MEXTRA-style extraction [OPS-C03], and STALE update-without-behavior-change [OPS-C16].
4. Require deletion tests to include raw records, summaries, embeddings/vector indexes, revisions, caches, backups, derived profiles and evaluation traces. Current API CRUD or session deletion is not evidence of that propagation.
5. Run a cost ledger per write/retrieve/repair/action: model calls and tokens, p50/p95 latency, bytes/revisions per logical fact, index rebuild time, audit retention cost and human-review load. Hold model, corpus, retrieval budget and workload fixed before comparing systems.

<!-- synthesis:OPS-AUTO-02 claims:OPS-C03,OPS-C05,OPS-C10,OPS-C11,OPS-C16 clusters:MM-C12 -->

## Consensus, disputes, reversal criteria and decision

**Scoped consensus (dominant):** persistent memory introduces a durable write/retrieve/action security surface; independent 2024–2026 groups show backdoor, query-only injection, environmental contamination, delayed action, and extraction variants [OPS-C01][OPS-C03][OPS-C04][OPS-C05][OPS-C07].

**Dispute/evidence-thin:** no independent, protocol-comparable evidence shows that a single write firewall, provenance scheme, privacy interface, or vendor memory API closes all links in the chain. This conclusion would change with independently reproduced full-chain tests spanning adaptive poisoning, extraction, stale-state repair, scoped retrieval and sensitive action authorization [OPS-C27].

**Decision:** deploy memory as governed state. Deny promotion of untrusted content into high-authority namespaces by default; preserve source and authority provenance; retrieval must be scope/purpose/freshness aware; and sensitive actions must re-check current authorization rather than inheriting authority from a retrieved record. Instrument, red-team and cost this pipeline before expanding persistence or autonomy.

<!-- synthesis:OPS-AUTO-03 claims:OPS-C01,OPS-C03,OPS-C04,OPS-C05,OPS-C07,OPS-C27 clusters:MM-C12 -->


## Evidence promotion：从不可信轨迹到持久技能

最新补查把一条此前只作为 gap 的攻击链提升为早期作者证据：风险不只发生在 record write 或 retrieval，还发生在 trajectory 被归一化、聚合并晋升为后续 agent 信任的 procedural artifact 时。现有实验覆盖两个 skill-evolution pipeline 和 inert canary embedding；它没有验证真实有害触发、生产攻击或完整 utility-security frontier，所以这里新增的是 attack surface 与评测协议，不是所有自演化系统都会失效的结论。

## Evidence-promotion 原子证据

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

Self-evolving skill systems create an evidence-promotion security boundary because an untrusted trajectory contributor can cause repeated experience to be normalized into persistent trusted procedural instructions; the paper formalizes success as Inclusion, Evolution Attribution, and Realization.
<!-- claim:FM-PE-C01 -->

The paper's pilot provenance-diversity gate blocked 25/25 single-cluster F1 candidates in one n=30,k=3 setting while accepting one five-session diverse control, but the paper itself calls the result preliminary.
<!-- claim:FM-PE-C04 -->

The evaluated SER measures durable artifact modification, not trigger activation, harmful action execution, credential theft, exfiltration, destructive effects, or a complete utility-security frontier.
<!-- claim:FM-PE-C05 -->

<!-- synthesis:FM-SEC-S01 claims:FM-PE-C01,FM-PE-C04,FM-PE-C05 clusters:MM-C12 -->
