# Research Architecture

Use this architecture for every full snapshot or update. Optimize for the quality of the final research product, not for minimum runtime, token use, or source count.

## Three corpus levels

Keep these populations separate throughout the run:

1. **Discovered** — high-recall metadata and weak signals. Search results, paper metadata, repository metadata, and trend leads may enter here without deep verification. They may shape follow-up searches but cannot support technical conclusions.
2. **Mapped** — deduplicated, identity-checked entities assigned to one or more clusters with dates, roles, and screening rationales. Use this population to build the field map and measure breadth or freshness. Do not use mapped-only metadata to support high-risk claims.
3. **Deep-verified** — selected papers, repositories, benchmarks, standards, products, and negative evidence that pass the source, quality-card, claim, evidence, and semantic-audit contracts. Only this level may support reader-facing technical conclusions.

Never hide a discovered or mapped item merely because it was not selected for deep verification. Report all three population sizes and their date, lane, and cluster distributions.

## Supervisor and work units

For a full run, act as a research supervisor. Create independent work units for:

- paper recall and citation expansion;
- GitHub discovery and repository momentum;
- benchmarks and comparability;
- products, standards, or adoption when relevant;
- negative evidence, security, failure, and lock-in;
- each important field cluster;
- independent synthesis and final audit.

Use parallel agents or equivalent isolated research branches when available. Give each branch a scoped question, evidence lanes, time windows, expected artifacts, and completion signal. Require every branch to return its sources, exclusions, cluster suggestions, contradictions, and remaining gaps. Do not ask a worker merely to summarize a list of sources.

## Workflow

### 1. Freeze the user contract

Freeze only the user's goal, audience, scope, named alternatives, time boundary, and non-negotiable questions. Permit derived research questions to grow from discovery and clustering. Record every derived question with its origin and parent requirement.

Define at least four time bands when the ecology permits:

- foundational work before the current frontier window;
- established recent work;
- the current rolling 12-month frontier;
- the current rolling 90-day weak-signal window.

Declare breadth and freshness targets in `research_plan.json` after a small pilot query set reveals the field's scale. Treat targets as calibration for this run, not universal truth. Missing a declared target prevents a comprehensive claim unless the run documents credible ecosystem scarcity.

### 2. Discover broadly

Run independent paper, GitHub, benchmark, standard/product, adoption, and negative-evidence lanes across all time bands. Expand aliases, surveys, references, forward citations, author and organization pages, benchmark names, paper titles, repository topics, releases, renamed predecessors, issues, and adjacent terminology.

Preserve raw or normalized result snapshots, exact queries, provider, page/cursor, execution time, and result count. Deduplicate only after recording discovery occurrences.

Maintain a cluster × lane × time-window matrix as a diagnostic view. Use it to reveal blind spots and report aggregate coverage; do not turn every cell into a mandatory independent research project. For decision-critical gaps, disputed boundaries, or bounded-absence conclusions, attach a replayable proof connecting the actual query, screening, mapped identity or scarcity audit, and conclusion. Treat future-dated metadata as quarantine, not current coverage.

Do not stop because a bibliography looks large or a fixed pass count was reached. Stop when the field map and important-cluster conclusions have stabilized, recent signals have been investigated, and remaining material gaps are explicit.

### 3. Map the field

Normalize identities and connect paper↔repository↔dataset↔benchmark↔product relations. Cluster from the broad mapped corpus, not from the deep shortlist. Use a DAG internally and expose a readable problem → mechanism/architecture → implementation → evaluation tree.

Every important cluster card must state:

- the problem and boundary;
- its main mechanism and architecture patterns;
- implementation patterns and representative repositories;
- evaluation tasks and benchmarks;
- maturity, tradeoffs, and failure modes;
- recent changes and trend signals;
- consensus, disputes, and unknowns;
- adjacent or overlapping clusters.

Iterate merge/split decisions and preserve the rationale. Keep `bridge` and `unmapped` entities visible rather than forcing a misleading category.

### 4. Investigate trends

Separate popularity/momentum, engineering maturity, and verified adoption.

- A single GitHub snapshot can establish current stars, activity, or release state only.
- Claim star growth or acceleration only from at least two dated observations or a replayable event history.
- Use created/pushed/released windows, contributor activity, issue/PR health, and paper linkage to qualify attention signals.
- Treat stars and trend rank as investigation triggers, never as evidence of technical quality, performance, or adoption.

Every material trend signal must receive a follow-up and end as `confirmed`, `qualified`, `dismissed`, or `unresolved`.

### 5. Select and run deep research

Select a stratified deep set across the field and within decision-important clusters: foundational evidence, current work, canonical or accelerating repositories, benchmark evidence, and the strongest negative or contradictory result. Give repositories equal status with papers for implementation-led questions. Allocate effort by importance and uncertainty rather than equalizing source counts or report length.

Produce a standalone cluster report and explicit gap list. Recurse on material gaps until the cluster reaches its stop condition. A project deep dive is required for decision-critical, architecture-representative, or trend-triggered repositories, not for every repository mechanically.

### 6. Build propositions and consensus

Abstract cross-source questions into scoped propositions. Record each independent evidence group's stance, directness, publication/reproduction status, protocol comparability, recency, and limitations. Classify the result as `dominant`, `mixed`, `disputed`, or `evidence-thin`; never count links as votes.

Build longitudinal and causal relations as `precedes`, `enables`, `extends`, `replaces`, `complements`, `competes`, or `contradicts`. Distinguish verified events, source-asserted influence, report inference, and forecast. Temporal adjacency alone is not causality.

### 7. Synthesize, then write the executive report

Generate the field map, landscape, timeline, consensus, GitHub radar, benchmark map, and cluster reports before the executive report. The executive writer must synthesize those artifacts and may not introduce new facts directly from source cards.

## Saturation and stopping

Review saturation at field level and for each important cluster. Add lane-, window-, or perspective-specific records when that scope contains a material gap or supports a consequential absence claim. Continue when a new query can plausibly:

- discover a new first-order cluster or change a cluster boundary;
- close a user-required lane or recent window;
- investigate a material trend signal;
- add a credible opposing stance or independent reproduction;
- change a decision-relevant conclusion.

Stop a scope only after consecutive expansion cycles yield no material new cluster, boundary, stance, representative implementation, or conclusion change and all remaining gaps are explicit. Stop the whole run only when all important clusters have deep packets, cross-cluster conflicts are resolved or preserved, and the reader-facing artifacts agree.

Materialize expansion cycles that affect the field map, an important cluster, a high-impact proposition, or a strong bounded-absence conclusion. Each event should identify the actual queries and whether the boundary, stance, representative set, or material conclusion changed. Two consecutive targeted no-material cycles are the recommended standard for a consequential bounded-absence claim; ordinary stopping may instead use transparent yield summaries and explicit residual gaps.

Runtime or cost exhaustion may force a disclosed incomplete result; it never proves comprehensive coverage.
