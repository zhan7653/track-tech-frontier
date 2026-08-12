---
name: track-tech-frontier
description: Build a comprehensive, current, reader-first technology-frontier research suite from papers, GitHub, benchmarks, and other primary evidence. Use for state-of-the-art reviews, technology landscapes, emerging-trend tracking, repository radars, benchmark maps, or updates to an earlier research snapshot; do not use for a quick single-fact lookup.
---

# Track Tech Frontier

Produce an evidence-backed **reader-facing explanation of a field**, not an inventory of sources or an audit ledger. The default reader is technically literate but new to the specialty. Its first reading should explain the real problem, the field's major mechanisms, how systems work, meaningful differences, recent movement, and unresolved uncertainty without requiring internal IDs or research-process knowledge.

## Choose the run mode

- Use **snapshot** by default for a current field map.
- Use **update** when an earlier bundle exists; preserve the earlier bundle, refresh the current frontier, and rewrite affected reader material plus a dated delta.
- Use **rapid** only when the user explicitly requests a smaller result. State every relaxed breadth, freshness, depth, or deliverable condition; do not call it comprehensive.

Use the `comprehensive` profile for snapshot and update runs. Cost or runtime is not a stopping condition unless the user sets one.

Read these references before acting:

- [research-architecture.md](references/research-architecture.md) for corpus levels, field mapping, mechanism branches, and stopping;
- [breadth-and-trends.md](references/breadth-and-trends.md) for broad paper/GitHub discovery and current windows;
- [search-routing.md](references/search-routing.md) for lane routing;
- [source-and-evidence.md](references/source-and-evidence.md) for deep evidence and high-risk facts;
- [synthesis-and-deliverables.md](references/synthesis-and-deliverables.md) before clustering and drafting;
- [evaluation-gates.md](references/evaluation-gates.md) before declaring completion;
- [reference-research-behaviors.md](references/reference-research-behaviors.md) for behavioral comparison;
- [update-mode.md](references/update-mode.md) for an update.

## Initialize research state before discovery

Resolve this Skill directory and initialize schema 2.0 before the first pilot query:

```text
python <skill-dir>/scripts/research_bundle.py init --root <bundle-dir> --topic "<topic>" --as-of YYYY-MM-DD --profile comprehensive
```

For an update, also pass `--mode update --previous <prior-bundle>`. Read the generated `schema.json` and populate its exact fields. Preserve live results and research state as they are produced; do not reconstruct provenance after writing.

## Run the research program

### 1. Freeze the reader contract and run a pilot

Record the user's topic, audience, scope, named alternatives, time boundary, and non-negotiable questions. Define the reader's level and the default entry point. Do not infer a request for a recommendation, a ranking, a preferred architecture, deployment guidance, or an implementation checklist.

Run a small multi-lane pilot to estimate field scale and reveal candidate mechanism branches. Declare calibrated breadth, freshness, deep-selection, saturation, and deliverable targets in `research_plan.json`; these guide research but never substitute for reader comprehension.

### 2. Discover broadly, then map the field

Search independent paper, GitHub, benchmark, standards/product, adoption, and negative-evidence routes where relevant. Focus on current practice, the rolling 12-month frontier, and the rolling 90-day weak-signal window. Include older work only when it is necessary to explain a current route; do not create mandatory historical or foundational quotas.

Keep exact queries, source snapshots, dates, and screening rationale. Separate discovered, mapped, and deep-verified entities. Discovery metadata and weak signals guide follow-up but cannot support reader-facing technical conclusions.

Derive the reader map from the broad mapped corpus. Organize it as:

```text
technology mechanisms (primary deep branches)
→ application scenarios (cross-branch views)
→ selected GitHub engineering cases
```

Mechanism branches describe the system lifecycle: objects/scope; writing and extraction; representation, storage, and indexing; updating, consolidation, conflicts, and forgetting; retrieval/ranking/context construction; and use, feedback, or learned skills. Merge, split, or rename branches for technical coherence. Treat evaluation, security/privacy/permissions, cost/reliability/observability, and interoperability/integration as cross-cutting concerns. Cover adjacent technologies only as boundaries or alternatives unless they truly perform the field's core lifecycle role.

### 3. Continue breadth until the map is useful and stable

Use gap-directed expansion by mechanism branch, time window, citation, organization, repository topic, benchmark, and adversarial route. Treat the cluster × lane × time-window matrix as a blind-spot diagnostic, not a quota.

Stop expansion only when further likely searches no longer create a first-order mechanism branch, change a material boundary, uncover a representative current implementation, or alter a qualified conclusion. Make material gaps and weak signals visible. Do not claim exhaustive recall.

### 4. Build the current-trend and GitHub radar

Put new work back into its mechanism branch rather than isolating it as a list of news. Describe current practice, substantiate recent 12-month changes, and label recent 90-day items as weak signals until evidence supports more. Treat stars, rankings, or a single snapshot only as attention/discovery signals; require dated observations for growth claims.

Use two GitHub layers: a broad candidate radar for coverage and recency, followed by a small, information-rich set of genuine engineering deep dives. Select deep dives for distinctive architecture, implementation relevance, current activity, or counterexample value—not a fixed count or star rank.

### 5. Deeply research important mechanism branches and projects

For each important mechanism branch, first synthesize its solution families and their differences, then deepen the evidence that makes the comparison useful. Explain the problem and boundary, how each family works, architecture/algorithm/data flow, important papers and implementations, maturity, costs, failure modes, consensus, counterevidence, and unresolved questions. Allocate space by importance, novelty, controversy, and engineering value; do not force a uniform template or source count.

Application scenarios are cross-branch views: explain which mechanisms are combined, replaced, or omitted and what constraints become salient. They are not recommendations. Promote a scenario to a primary mechanism branch only when it is itself a distinct technical route.

For a selected repository, inspect pinned code and documentation closely enough to explain its actual components, write/store/index/retrieve/update/use data flow, dependencies and services, interfaces and integration boundaries, maintenance signals, and project-specific failure modes. Distinguish visible code facts, maintainer assertions, execution results, and unverified risks. Run code only if the result could change a material conclusion.

### 6. Verify in layers and synthesize the reader suite

Apply strict direct evidence and precise locators to core conclusions, critical numbers, versions, comparisons, security/adoption facts, and consequential limitations. Use conservative citations and logical coherence for ordinary explanatory prose. Keep claims, evidence, screening, and saturation ledgers for traceability, but keep their IDs and process language out of reader prose.

Draft the reader suite only after mapping and deep packets exist. Lead with the field answer, not corpus counts or internal taxonomy. Use the report contract to make the main report independently readable, present a descriptive **general architecture model** rather than a recommended architecture, and give each important mechanism branch a clear solution-family comparison. Describe applicability conditions, maturity, tradeoffs, failure modes, consensus, disputes, and uncertainty without telling the reader what to choose or deploy.

Complete the first reader-ready suite before creating an optional human-review list. Reserve that list for high-impact uncertainty, conflicting evidence, or genuinely subjective representative choices; never leave a branch as a placeholder awaiting approval.

### 7. Audit the actual result

Run the outcome gates in [evaluation-gates.md](references/evaluation-gates.md) and both deterministic validations:

```text
python <skill-dir>/scripts/research_bundle.py validate --root <bundle-dir>
python <skill-dir>/scripts/research_bundle.py validate --root <bundle-dir> --strict
```

Fix real errors and preserve honest advisories. A schema pass, source count, claim count, file count, or green validator alone cannot establish completion. The decisive test is whether a new technical reader can understand the field from the default entry, independently understand each important mechanism branch, and trace key claims without audit machinery interrupting the narrative.

## Deliver

Save the suite under `frontier-research/<topic-slug>/<as-of-date>/` unless the user requests another location. Return links to the reader entry, general architecture model, mechanism landscape, scenario views, current-trend radar, evidence/limitations material, branch reports, and selected project reports. Summarize recent-window coverage, verification status, important unresolved gaps, and any optional human-review questions.

Return in the user's language while preserving original technical and project names. Do not modify product source code or remote systems while researching.
