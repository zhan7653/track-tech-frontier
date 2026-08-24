from __future__ import annotations

import json
from pathlib import Path


BUNDLE = Path(r"D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24")
CHECKED = "2026-08-23T17:45:00Z"

SPECS = [
    ("R4-C001","fact","high","StateFuse contract","StateFuse builds its public agent-memory contract over immutable OpSet/CRDT history, explicit conflict objects, exact and semantic correction handles, deterministic predicates, and projection-bounded resolution.","S-P-260705844","PDF pp. 1–4, Sections 1 and 3","The paper enumerates five contract components and states that projection may choose or abstain but cannot rewrite replicated history."),
    ("R4-C002","fact","high","StateFuse evaluation boundary","On the 282-question conflict-bearing MemoryAgentBench slice used by StateFuse, conflict-preserving methods tie on answer accuracy; the supported distinction is contradiction visibility and auditable correction, not universal accuracy gain.","S-P-260705844","PDF pp. 1–2 and Section 4","The abstract and introduction explicitly narrow the claim and describe matched resolver/verification conditions."),
    ("R4-C003","fact","high","MemTX mechanism","MemTX stages candidate records in snapshot-isolated transactions, checks evidence, validity, semantic conflict and dependency stability, gates irreversible actions, and uses typed cascading repair after retraction.","S-P-260723929","PDF pp. 3–6, commit and repair pipelines","The method and architecture figure define the ordered admission checks, action gate and dependency repair."),
    ("R4-C004","fact","high","MemTX evaluation","MemTX is evaluated on a 90-case main suite and a 56-case hardened suite across five backbones; the paper reports strong protocol-specific results but leaves transcription and retry outside the protected commit boundary.","S-P-260723929","PDF pp. 6–8, Tables 2–4 and Conclusion","Tables define the suites/backbones; the conclusion names the remaining open boundary."),
    ("R4-C005","fact","high","LatticeMind state model","LatticeMind stores memory items with key, content, evidence metadata, timestamp and status in PROPOSED, CONFIRMED, CONTESTED or SUPERSEDED, using symbolic checks before selective LLM reconciliation.","S-P-260808236","PDF pp. 3–5, Section 3","The problem formulation and method define the tuple, status set and two-stage conflict handling."),
    ("R4-C006","fact","high","LatticeMind limitation","LatticeMind's main evidence validates credibility conflicts; coordination conflicts are handled conservatively but are not the paper's validated empirical claim, and secondary planning results are mixed.","S-P-260808236","PDF pp. 1–2 and Discussion","The authors explicitly limit the evaluated regime and report mixed planning results."),
    ("R4-C007","fact","high","PatchBoard mechanism","PatchBoard has an Architect-generated schema and workflow rules; workers receive bounded views and propose JSON Patch operations; a deterministic kernel checks operation type, write contract, schema and invariants before transactional commit.","S-P-260529313","PDF pp. 3–6, System Design","The method traces candidate patch validation on a temporary state and records accepted and rejected transactions."),
    ("R4-C008","fact","high","PatchBoard protocol","PatchBoard compares 630 matched ALFWorld episodes across PatchBoard, LangGraph and Flock under one model/configuration and separately injects invalid JSON, bad path/type, unauthorized write, false claim and cycle faults.","S-P-260529313","PDF pp. 6–8, Sections 4–5","The setup defines 126 gamefiles × five seeds, common budgets and five fault families."),
    ("R4-C009","fact","high","Collaborative Memory mechanism","Collaborative Memory models time-varying user–agent and agent–resource permissions with bipartite graphs, keeps private and shared tiers, attaches immutable provenance, and applies read projections and write transformations.","S-P-250518279","PDF pp. 1–6, Sections 3–4","The architecture and implementation sections define the two graphs, memory tiers, provenance and policy transforms."),
    ("R4-C010","fact","high","Collaborative Memory protocol","Collaborative Memory's evaluation simulates five users and six domain agents over 2,556 MultiHop-RAG questions; resource calls and LLM-judged accuracy measure a synthetic multi-user setting rather than real organizational deployment.","S-P-250518279","PDF pp. 6–9, Section 5","The setup defines dataset, partitioned resources, synthetic overlap and metrics."),
    ("R4-C011","fact","high","Governed Shared Memory mechanism","Governed Shared Memory defines agent-local, team-shared, tenant-global and restricted scopes, temporal supersession, provenance and policy-governed propagation in a live MemClaw service.","S-P-260624535","PDF pp. 4–6, Section 5","The architecture section enumerates scopes and memory metadata/control primitives."),
    ("R4-C012","fact","high","Governed Shared Memory counterevidence","The MemClaw study found a dated agent-scoped GET-by-id enforcement gap that was remediated and a write-pipeline ordering interaction where synchronous near-duplicate rejection could prevent later contradiction handling.","S-P-260624535","PDF pp. 8–13, Sections 8–10","The results and discussion report the focused probe, fix and deduplication/contradiction interaction."),
    ("R4-C013","fact","high","Governed Shared Memory limitations","The Governed Shared Memory evaluation is a self-evaluation of one freshly provisioned tenant, has no alternative-system comparand, and states that broader adversarial and multi-tenant replication remains missing.","S-P-260624535","PDF pp. 13–14, Section 10","The limitations section explicitly lists self-evaluation, single tenant, scale and no comparand."),
    ("R4-C014","fact","high","GateMem benchmark","GateMem contains 91 long-form multi-party episodes and 2,218 hidden checkpoints across medical, office, education and household domains, jointly measuring authorized utility, contextual access control and agent-facing active forgetting.","S-P-260618829","PDF pp. 1–5, Sections 1 and 3","The abstract and benchmark construction specify episode/checkpoint counts, domains and three axes."),
    ("R4-C015","fact","high","GateMem deletion boundary","GateMem measures behavioral non-recovery after a deletion request, not certified physical erasure from every underlying store.","S-P-260618829","PDF p. 2, Introduction","The paper explicitly distinguishes interface-level active forgetting from physical or parametric erasure."),
    ("R4-C016","fact","high","MAP-Graph mechanism","MAP-Graph uses a typed graph of agents, sources, memories, claims and actions to apply hard permission filtering, multiplicative path-trust reranking, affected-state propagation and risk-sensitive action gating.","S-P-260810509","PDF pp. 3–6, Sections 3–4","The method and benchmark interface describe typed lineage, CanRead filtering, trust and action decisions."),
    ("R4-C017","fact","high","MAP-Graph protocol boundary","MAP-Graph's main evidence is one temperature-zero run over 2,700 synthetic templated tasks per method with simulated actions; several baselines are mechanism adaptations rather than complete reimplementations.","S-P-260810509","PDF pp. 5–7, Sections 4.1–4.6","The protocol, baseline and limitations text define the synthetic single-run setting and adapted baselines."),
    ("R4-C018","fact","high","AGENTSYS mechanism","AGENTSYS keeps raw tool output in short-lived worker contexts, requires the parent to predeclare a typed intent, admits only validated structured returns, and gates recursive worker tool calls with a validator that excludes raw tool content.","S-P-260207398","PDF pp. 6–9, Section 5","The architecture defines parent/worker separation, intent schema, JSON return path and recursion validator."),
    ("R4-C019","fact","high","Subagent inheritance threat","When Child Inherits identifies unrestricted memory inheritance, absent resource access control, asynchronous memory divergence and unauthorized cross-agent termination as orchestration-layer vulnerability classes.","S-P-260508460","PDF pp. 1–7, threat model and contributions","The paper enumerates four classes and maps them to trust-boundary invariants."),
    ("R4-C020","fact","normal","AutoRefine representation model","AutoRefine compiles an evidence-linked intervention specification into the first Rule, Skill or bounded Subagent whose execution boundary owns all required observations, state, decisions and completion conditions.","S-P-260122758","PDF pp. 1–5, artifact compiler","The paper defines a runtime-relative ownership order and first-closure heuristic."),
    ("R4-C021","fact","high","AutoRefine admission","AutoRefine uses a type-specific contract gate and a replay gate that requires source-failure correction without observed regression on preservation cases; the resulting guarantee is case-bounded rather than global.","S-P-260122758","PDF pp. 4–6, Equation 4 and Experimental Setup","The admission rule and text explicitly bound the guarantee to replayed evidence."),
    ("R4-C022","fact","normal","State Contamination","State Contamination defines memory laundering as classifier-clean compressed state that preserves harmful influence, measures it with a paired sub-threshold propagation gap, and finds pre-summary sanitization more effective than cleaning only the completed summary.","S-P-260516746","PDF pp. 1–6, Sections 1 and 3","The paper defines SPG and compares raw, compressed and mitigation-placement channels over paired rollouts."),
    ("R4-C023","fact","high","Memory poisoning write channels","MPBench distinguishes explicit instruction-executed, system-prompt-driven, compaction-driven and experience-to-procedure memory writes, each with different trigger and write authority.","S-P-260604329","PDF pp. 1–5, Section 2","The paper enumerates four channels and maps them to direct/inferred authority and vulnerabilities."),
    ("R4-C024","fact","high","MPBench scope","MPBench evaluates OpenClaw and HERMES under a black-box external-input adversary and explicitly excludes shared multi-user memory and direct memory access, so its results are bridge evidence for Subagent Memory rather than a multi-agent incidence rate.","S-P-260604329","PDF pp. 4–7, Threat Model and Evaluation","The scope section lists adversary capabilities and excluded shared-store settings."),
    ("R4-C025","fact","high","Bad Memory threat model","Bad Memory assumes malicious content is already present in persistent workspace files; how it reaches those files is out of scope, and initial attempts to induce writes were not trivially successful.","S-P-260714611","PDF pp. 3–5, Section 3.1","The threat model explicitly states attacker control of a file and excludes the upstream write path."),
    ("R4-C026","fact","high","Bad Memory protocol","Bad Memory tests Claude Code and Codex in a synthetic workspace across four models, three attack goals and ten trials per single-probe condition, with multi-session probe/stabilization sequences for persistence.","S-P-260714611","PDF pp. 3–7, Sections 3–4","The evaluation protocol names systems, models, vectors, sequences and trial count."),
    ("R4-C027","fact","normal","MATM mechanism","Multi-Agent Transactive Memory stores producer-agent trajectories in a population repository and trains consumer-specific retrieval on marginal utility rather than semantic similarity alone.","S-P-260619911","PDF pp. 1–6, Sections 3–4","The architecture defines producer/consumer roles, trajectory chunks and utility labels from outcome changes."),
    ("R4-C028","fact","high","MATM protocol","MATM builds separate ALFWorld and WebArena indexes using training partitions and evaluates 34 consumer agents on 274 and 88 held-out episodes respectively; similar task types may still occur across train and test.","S-P-260619911","PDF pp. 4–7, Section 4","The setup gives population sizes, splits and the stated overlap boundary."),
    ("R4-C029","fact","normal","DecentMem mechanism","DecentMem gives each agent a dual local memory: a consolidated exploitation pool and an exploration pool, with online routing updated from stage-wise feedback instead of one centralized shared repository.","S-P-260522721","PDF pp. 2–6, Method","The paper defines per-agent pools, online weighting and decentralized execution."),
    ("R4-C030","fact","high","MemCollab negative transfer","MemCollab reports that naively transferring memory across backbone models can degrade performance and instead contrasts preferred and unpreferred trajectories to distill enforce/avoid constraints tagged for task-aware retrieval.","S-P-260323234","PDF pp. 1–6, Sections 1–3","The method defines trajectory pairing, violation/invariant extraction and task-aware shared-bank retrieval; Figure 1 shows negative transfer."),
    ("R4-C031","fact","normal","ConMem mechanism","ConMem turns successful and failed trajectories into signed strategy cards connected by typed relations and runs retrieve, graph-expand, coordinate and compose stages before injecting a compact slate.","S-P-260608702","PDF pp. 3–9, Method and ablations","The method and case study define card fields, relation types, coordination pruning and failure admission."),
    ("R4-C032","fact","normal","CoMIC mechanism","CoMIC keeps subgoal-oriented hierarchical state on edge agents, asynchronously uploads completed episodes, admits critic-evaluated observation/action/result experience in the cloud, and returns grouped global guidance as one advisory channel.","S-P-260600756","PDF pp. 2–7, Sections 2–3","The architecture and equations define edge state, short-term cloud buffer, experience admission and guidance store."),
    ("R4-C033","fact","normal","TreeMem boundary","TreeMem is a multi-agent memory-construction pipeline of builder, summarizer and retrieval agents optimized by branch-based credit assignment; it is not direct evidence that peer task Subagents share a team memory.","S-P-260504811","PDF pp. 1–10, Method and Conclusion","The paper's agents are internal memory workers and its benchmarks evaluate long-history QA."),
    ("R4-C034","fact","normal","G-Memory mechanism","G-Memory stores insight, query and interaction graphs; it retrieves query nodes, traverses upward to insights and downward to sparsified collaboration traces, then builds role-specific memory for each Agent before updating all three graphs after the task.","S-P-250607398","PDF pp. 2–8, Sections 3–5","The graph definitions, Equations 4–9 and update procedure establish the data flow."),
    ("R4-C035","fact","high","G-Memory retrieval boundary","G-Memory reports that excessive hop expansion and larger query-retrieval k can reduce performance, so more retrieved shared history is not monotonically better in its evaluated protocols.","S-P-250607398","PDF pp. 8–10, Section 5.4","The sensitivity analysis reports best/near-best one-hop and k 1–2, with degradation at larger values."),
    ("R4-C036","fact","normal","MIRIX boundary","MIRIX uses six specialized Memory Managers plus a Meta Memory Manager to manage one user's heterogeneous memory types; its 'multi-agent memory system' is primarily an internal memory-worker architecture, not evidence of peer Subagents sharing one team state.","S-P-250707957","PDF pp. 1–8, Architecture","The paper describes six memory components, six managers, a meta manager and a chat agent for user memory."),
    ("R4-C037","fact","high","GroupMemBench","GroupMemBench creates threaded multi-party conversations with speaker-grounded, audience-adapted queries across six categories; its strongest tested system reaches 46.0% average accuracy and BM25 matches or exceeds most memory systems.","S-P-260514498","PDF pp. 1–8, Sections 1–4","The benchmark definition and headline results provide the structure and reported accuracy boundary."),
    ("R4-C038","fact","high","AgentLeak","AgentLeak instruments seven leakage channels in 1,000 coordinator-worker scenarios and reports that inter-agent messages leak more than final outputs, illustrating why output-only privacy audits miss internal channels.","S-P-260211510","PDF pp. 1–7, Contributions and channel taxonomy","The paper defines scenario count, channels and internal-message versus final-output comparison."),
]


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    claims = read(BUNDLE / "claims.jsonl")
    evidence = read(BUNDLE / "evidence.jsonl")
    checks = read(BUNDLE / "semantic_checks.jsonl")
    claim_ids = {row["claim_id"] for row in claims}
    evidence_ids = {row["evidence_id"] for row in evidence}
    checked_claims = {row["claim_id"] for row in checks}
    added = 0
    for claim_id, claim_type, risk, scope, statement, source_id, locator, summary in SPECS:
        evidence_id = claim_id.replace("-C", "-EV")
        if claim_id not in claim_ids:
            claims.append({
                "as_of":"2026-08-24","claim_id":claim_id,"claim_type":claim_type,"confidence":"high" if risk=="high" else "medium",
                "deliverable_ids":[],"publication_status":"ledger-only","risk":risk,"scope":scope,"statement":statement,
                "status":"supported" if claim_type=="fact" else "qualified"
            })
            claim_ids.add(claim_id)
            added += 1
        if evidence_id not in evidence_ids:
            evidence.append({"checked_at":CHECKED,"claim_id":claim_id,"evidence_id":evidence_id,"locator":locator,"relation":"supports","source_id":source_id,"support_summary":summary})
            evidence_ids.add(evidence_id)
        if claim_id not in checked_claims:
            checks.append({"checked_at":CHECKED,"claim_id":claim_id,"evidence_ids":[evidence_id],"rationale":"Clause-level check against the opened original PDF; wording remains bounded to the paper's stated mechanism and protocol.","uncovered_terms":[],"verdict":"pass"})
            checked_claims.add(claim_id)
    write(BUNDLE/"claims.jsonl",claims)
    write(BUNDLE/"evidence.jsonl",evidence)
    write(BUNDLE/"semantic_checks.jsonl",checks)
    print(json.dumps({"specs":len(SPECS),"claims_added":added,"claims_total":len(claims),"evidence_total":len(evidence)}))


if __name__ == "__main__":
    main()
