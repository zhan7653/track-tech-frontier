# Research Architecture

## Purpose and populations

Optimize a full snapshot or update for the quality of the finished reader suite. Keep three populations separate:

1. **Discovered** — high-recall metadata and weak signals that guide searching but cannot support technical conclusions.
2. **Mapped** — deduplicated, identity-checked entities with dates, roles, branch memberships, and screening rationale. Use these to map the field and describe coverage.
3. **Deep-verified** — selected papers, repositories, benchmarks, standards, products, and negative evidence with the evidence required for reader-facing conclusions.

Do not hide a discovered or mapped item merely because it was not deeply verified. Keep the three populations in the audit layer; reader prose should use only the degree of process detail needed to interpret uncertainty.

## Reader-first field structure

Build a readable field map before drafting. Its primary branches are technical mechanisms, not source types, product categories, or application names:

```text
mechanism branches
→ scenario views that cross those branches
→ selected repository engineering cases
```

Use the following lifecycle as a starting point, not a fixed taxonomy:

```text
memory objects and scope
→ writing, extraction, and formation
→ representation, storage, and indexing
→ updating, consolidation, conflict handling, and forgetting
→ retrieval, ranking, and context construction
→ use, feedback, and experience/skill learning
```

Security, privacy, authorization, governance, evaluation, cost, reliability, observability, interoperability, and integration cut across the lifecycle. Merge, split, or rename branches only when the resulting mechanism is coherent. State each branch's inclusion, exclusion, relationships, implementation patterns, solution families, maturity, tradeoffs, failure modes, and evidence gaps.

Use scenarios—such as personal assistants, coding agents, multi-agent systems, world-state systems, and embodied or multimodal systems—to show how mechanisms combine, replace, or disappear under different constraints. Do not repeat the mechanism explanation or convert a scenario view into advice. Make it a primary branch only if it introduces an independent technical route.

Long context, ordinary RAG, parameter memory, continual learning, checkpoints, and workflow state are adjacent by default. Mention them as boundaries or alternatives; include them in the subject only when they perform the field's core cross-session state, lifecycle, retrieval/use, or evolution role.

## Workflow

### 1. Freeze the research and reader contract

Record the user goal, intended reader, scope, named alternatives, time boundary, and non-negotiable questions. Let research questions evolve from the map. Record their origin and parent requirement.

Prioritize current practice, the rolling 12-month frontier, and the rolling 90-day weak-signal window. Add older work only when it is necessary to explain a present route, claim, or contrast. Do not require a foundations section or a historical quota.

After a small multi-lane pilot, declare calibrated breadth, freshness, importance, deep-selection, saturation, and deliverable targets in `research_plan.json`. They are planning signals, not proof that the reader outcome is complete.

### 2. Discover broadly and map carefully

Run independent paper, GitHub, benchmark, product/standard, adoption, and negative-evidence routes as the topic warrants. Preserve exact queries, pages/cursors, snapshots, timestamps, and result counts before deduplicating.

Connect paper ↔ repository ↔ dataset ↔ benchmark ↔ product relations. Map from the broad mapped corpus rather than a deep shortlist. Keep bridge and high-signal unmapped entities visible. Maintain a branch × lane × time-window matrix only to diagnose blind spots; do not make every cell an independent quota.

### 3. Investigate current signals

Separate attention/momentum, engineering maturity, and verified adoption. A single repository observation can establish only an observed state, not growth. End each material trend signal as `confirmed`, `qualified`, `dismissed`, or `unresolved` after follow-up.

### 4. Deepen branches, scenarios, and projects

Start each important mechanism branch with a solution-family synthesis, then select evidence that clarifies the mechanisms, comparisons, current movement, counterevidence, and open questions. Allocate effort by importance, novelty, controversy, and engineering value rather than equal source counts or lengths.

Use a branch package when one page would force the overview and the implementation detail to compete. A common shape is a short entry map plus separate mechanism/algorithm, engineering, and frontier/counterevidence reports, but the split follows the topic rather than a fixed file count. Cross-link the package so a reader can orient from the entry and then reconstruct the system in the deep pages. Splitting an inventory into several files is not depth.

Use a broad GitHub candidate radar followed by only a few genuine project reports. A project report requires a fixed-version inspection of component relationships, lifecycle data flow, dependencies/services, interfaces, integration and deployment constraints, maintenance boundaries, failure modes, and the distinction between code-visible facts, maintainer claims, executed results, and unknown risks. A directory list or README summary is a bounded project card, not a deep dive.

### 5. Build descriptive propositions

Assess scoped propositions using independent evidence groups, directness, publication/reproduction status, protocol comparability, recency, artifacts, negative evidence, and applicability conditions. Classify them as `dominant`, `mixed`, `disputed`, or `evidence-thin`. Keep verified events, source-asserted influence, report inferences, and forecasts distinct.

Describe what a route solves, the conditions in which it holds, maturity, cost, failure modes, consensus, disputes, and weak signals. Do not turn those descriptions into a ranking, a preferred configuration, deployment instructions, or an implementation checklist.

## Saturation and stopping

Continue a scope while a credible follow-up could reveal a first-order branch, change a material boundary, identify a representative current implementation, add an independent opposing stance, or alter a qualified conclusion. Materialize expansion cycles affecting the map, an important branch, a high-impact proposition, or a consequential bounded-absence claim.

Stop ordinary discovery when the map and important branch conclusions stabilize and remaining gaps are explicit. For a consequential absence claim or disputed scope, use repeated targeted no-material cycles and preserve their query evidence. Cost or runtime can force a clearly marked incomplete result; it never proves coverage.

## Writing order and review

Write the independently readable main report and complete branch and project reports from the map and deep packets. Only then produce an optional, small human-review list for high-impact uncertainty, evidence conflict, or genuinely subjective representative choices. A branch without human review still needs a complete, qualified first-version conclusion.

Before final reader editing, compare the important branch inputs against the actual prose. Treat a paper, repository, benchmark, or negative result as absorbed only when it changes a mechanism explanation, engineering walkthrough, experimental boundary, judgment, or research agenda. Preserve unabsorbed long-tail items in the map/audit rather than padding reader pages with names.
