# AI Agent Memory research contract

**As of:** 2026-08-10  
**Audience:** model, Agent, platform, and engineering leaders  
**Mode:** fresh comprehensive snapshot  
**Primary objective:** explain the complete current Agent Memory field, its recent direction, engineering reality, consensus and disagreements, and the decisions a technical team should take.

## Frozen user requirements

1. Build breadth before depth. Preserve discovered, mapped, and deep-verified populations separately.
2. Search papers and GitHub broadly enough to derive the field map from the corpus rather than from a selected bibliography.
3. Give recent work independent weight. Cover foundational history, 2024–2025, rolling 12 months, and rolling 90 days.
4. Treat GitHub as first-class engineering evidence and actively discover new/high-attention/recently active repositories.
5. Organize the output as a field tree/DAG and coherent mechanism/architecture/implementation clusters.
6. Within every important cluster, deeply analyze representative papers, repositories, benchmarks, negative evidence, and engineering tradeoffs.
7. Explain weighted consensus, disputes, maturity, open questions, and reversal conditions.
8. Build a longitudinal and causal technology trajectory without confusing chronology with causation.
9. Produce multiple substantial reader files rather than one compact report.
10. Preserve strict evidence correctness for published deep claims.
11. Make perspective expansion, recursive gap filling, supervisor/worker decomposition, compression, and final synthesis visible in the artifacts.
12. Optimize for final quality; do not stop for cost, runtime, fixed query passes, or a convenient source count.

## Initial perspectives

These perspectives seed work units and may generate derived questions after discovery:

- **Memory-system architect:** state model, lifecycle, representations, control plane, persistence, isolation, observability.
- **Agent-learning researcher:** episodic/semantic/procedural memory, reflection, skill learning, continual adaptation.
- **Retrieval researcher:** write selection, indexing, temporal/graph retrieval, reranking, adaptive read policy, grounding.
- **Benchmark designer:** task taxonomy, memory horizons, interaction, tool action, multi-agent settings, metrics and protocol comparability.
- **Repository/platform engineer:** APIs, storage backends, versioning, deployment, failure recovery, integration, tests and maintenance.
- **Security/privacy reviewer:** poisoning, extraction, sensitive persistence, multi-tenancy, deletion, access control, audit and stale/conflicting memory.
- **Cost/performance engineer:** write/read latency, token cost, storage growth, consolidation, compaction, update and recovery cost.
- **Product/adoption lead:** open-source versus managed services, maturity, independent deployment evidence, lock-in and migration.
- **Contrarian reviewer:** when long context, stateless tools, explicit state machines, BM25/vector RAG, or no memory is better.
- **Frontier scout:** recent papers, newly created or accelerating repositories, emerging benchmarks, new organizations and weak signals.

## Scope boundaries

Include memory mechanisms used by LLM-based agents, assistants, tool-using agents, embodied/web agents, and multi-agent systems when memory is a substantive system component. Include adjacent RAG, knowledge graph, reflection, skill-library, long-context, and state-management work when it clarifies a boundary or competing design.

Exclude ordinary model context, caches, generic vector databases, and generic RAG projects that do not substantively address persistent Agent Memory; preserve them only as screened boundary cases when useful.

## Completion rule

The research is comprehensive only after the v09 non-compensating gates all pass. Any unresolved breadth, freshness, important-cluster depth, synthesis, trend, or evidence gate downgrades the result rather than being averaged away.
