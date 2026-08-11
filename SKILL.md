---
name: track-tech-frontier
description: Build comprehensive, current technology-frontier research from a broad paper and GitHub corpus, then cluster the field, investigate trends, deeply analyze every important cluster, weigh consensus and contradictions, and deliver a multi-file evidence-backed research suite. Use for state-of-the-art reviews, technology landscapes, emerging-trend tracking, repository radars, benchmark maps, or updates to an earlier research snapshot; do not use for a quick single-fact lookup.
---

# Track Tech Frontier

Produce the best defensible research result, not the cheapest acceptable memo. Separate high-recall discovery from deep verification, and separate both from synthesis. A fully cited list of projects is not a research report.

## Choose the run mode

- Use **snapshot** by default and build the field again from broad discovery.
- Use **update** when an earlier bundle exists; re-run recent discovery, recheck mutable sources, update the field graph, and rewrite the full current synthesis plus a delta.
- Use **rapid** only when the user explicitly requests a smaller result. Disclose every relaxed breadth, depth, freshness, or deliverable gate and never call it comprehensive.

Use the `comprehensive` profile for snapshot and update runs. Cost or runtime is not a stopping condition unless the user explicitly sets one.

Read these references before acting:

- [research-architecture.md](references/research-architecture.md) for the three-level corpus, supervisor/work-unit model, clustering, deep research, and saturation;
- [breadth-and-trends.md](references/breadth-and-trends.md) for paper/GitHub recall and freshness;
- [search-routing.md](references/search-routing.md) for lane routing;
- [source-and-evidence.md](references/source-and-evidence.md) for deep evidence and quality cards;
- [synthesis-and-deliverables.md](references/synthesis-and-deliverables.md) before clustering and drafting;
- [evaluation-gates.md](references/evaluation-gates.md) before declaring completion;
- [reference-research-behaviors.md](references/reference-research-behaviors.md) for direct behavioral comparison with the inspected systems;
- [update-mode.md](references/update-mode.md) for an update.

## Initialize research state before discovery

Resolve this Skill directory and initialize schema 2.0 before the first pilot query:

```text
python <skill-dir>/scripts/research_bundle.py init --root <bundle-dir> --topic "<topic>" --as-of YYYY-MM-DD --profile comprehensive
```

For an update, also pass `--mode update --previous <prior-bundle>`. Read the generated `schema.json` and populate its exact fields. Preserve live results and research state as they are produced; do not reconstruct provenance after writing.

## Run the research program

### 1. Freeze the user contract and run a pilot

Freeze the user's goal, audience, scope, named alternatives, required decisions, and time boundary. Build aliases, predecessors, acronym collisions, and adjacent concepts. Classify the evidence ecology as research-, standards-, implementation-, product-led, or mixed.

Run a small multi-lane pilot only to estimate field scale and expose likely clusters. Then declare run-specific breadth, freshness, important-cluster, deep-selection, saturation, and deliverable targets in `research_plan.json`. These are calibration values, not universal quality claims. Do not make them artificially small to pass validation.

### 2. Create perspectives and work units

Generate multiple stakeholder and technical perspectives before finalizing the map. Create independent work units for paper recall, GitHub/release discovery, benchmarks, negative evidence, products/standards/adoption when applicable, and every important cluster. Use parallel agents or equivalent isolated branches when available.

Each work unit must return discovered items, mapped entities, cluster proposals, primary sources, exclusions, contradictions, open gaps, and follow-up queries. The supervisor merges identities and evidence, not prose summaries.

### 3. Build the discovered corpus for recall

Search multiple providers and query families across foundational, prior-frontier, rolling 12-month, and rolling 90-day windows. Keep exact query/request, provider, cursor/page, result count, UTC time, and normalized result snapshot. Preserve paper and GitHub lanes independently, plus benchmark, standards/product, adoption, and adversarial lanes when relevant.

Do not require deep source cards at this level. Discovery metadata and weak signals may enter the corpus but may not support technical conclusions.

### 4. Map, deduplicate, and cluster

Canonicalize entities, preserve aliases, and connect paper↔repository↔dataset↔benchmark↔product relations with explicit link evidence. Promote relevant entities to `mapped`, assign primary/secondary/bridge cluster memberships, and retain screening rationales.

Derive a field DAG from the mapped corpus. Iterate cluster merge/split and boundary decisions. Build the reader view as problem → mechanism/architecture → implementation pattern → evaluation/application. Keep unmapped high-signal entities visible.

### 5. Continue breadth until saturation

Use cluster-specific, recent-window, citation, organization, repository-topic, benchmark, and adversarial expansions. Track information gain at field and important-cluster level: new first-order clusters, changed boundaries, important recent entities, credible new stances, and decision-changing evidence. Continue while a follow-up can materially change the map or a conclusion.

Use the cluster × lane × time-window matrix as a diagnostic for blind spots, not as a Cartesian-product quota. Report aggregate coverage and the material missing cells. Require replayable scope-level search and saturation evidence only when it protects a decision-critical conclusion, a disputed boundary, or a strong bounded-absence claim. For ordinary map completeness, an honest search log, representative sampling, and explicit blind spots are sufficient.

Never stop merely because three passes ran, a source count was reached, or deep verification is expensive.

### 6. Build the trend radar

Collect dated repository observations and recent paper/release signals. Separate foundational, established-active, new/accelerating, and watchlist items. Require at least two observations or a replayable event history before claiming growth or acceleration. Treat stars and rankings only as discovery signals.

Investigate every material signal and mark it confirmed, qualified, dismissed, or unresolved.

### 7. Deeply research every important cluster

Select a stratified deep set: foundations, current work, canonical or trend-triggered repositories, benchmark evidence, and strongest negative/contradictory work. Apply [source-and-evidence.md](references/source-and-evidence.md) only now at full strength.

For each important cluster, produce a meaningful standalone analysis, a stratified selection of high-quality evidence, and an explicit gap list. Allocate depth in proportion to importance, novelty, controversy, and decision value; do not force equal detail into every cluster. Give repository architecture, implementation, release, maintenance, integration, license, and adoption evidence the same attention as papers. Selected engineering deep dives should have reciprocal `repository_engineering_profiles.jsonl` records with fixed-version component relationships, data flow, dependencies/services, constraints, maintenance boundaries, failure modes, adoption boundary, and useful locators. Running setup or tests is optional and reserved for cases where execution can change a material judgment.

### 8. Build claims, propositions, and consensus

Register decision-critical external facts—numbers, versions, comparisons, security claims, current status, and consequential limitations—as atomic claims with precise evidence joins and semantic checks. Lower-risk descriptive facts may use paragraph-level primary citations when the wording is conservative and traceable. Then build cross-source propositions with supporting and opposing evidence, independent-group awareness, scoped assessments, minority views, unknowns, contradictions, tradeoffs, and causal/temporal relations. Consider directness, independence, publication/reproduction, comparability, recency, artifacts, negative evidence, and applicability conditions; never count links as votes.

### 9. Produce the multi-file synthesis

Follow [synthesis-and-deliverables.md](references/synthesis-and-deliverables.md). Generate field tree, landscape, timeline, consensus/controversies, GitHub radar, benchmark map, important-cluster reports, and selected repository deep dives before the executive report. Organize writing around problems, mechanisms, architectures, implementations, and decisions—not source introductions.

Allow coherent paragraphs to combine multiple audited claims. Use synthesis records and markers for analytical moves. Do not introduce source facts during drafting unless they first enter the deep evidence ledger.

### 10. Audit the actual result

Run the outcome gates from [evaluation-gates.md](references/evaluation-gates.md): breadth, freshness, field structure, selective depth, key-evidence reliability, and synthesis quality. These outcome gates are non-compensating, but optional bookkeeping does not become a hard gate by itself. Compare the output behavior with the reference research systems named in the method record: perspective expansion, gap-directed follow-up, supervisor/worker decomposition, compression, and final synthesis must be visible in the artifacts, not only claimed in a checklist.

Run and save both deterministic validations:

```text
python <skill-dir>/scripts/research_bundle.py validate --root <bundle-dir>
python <skill-dir>/scripts/research_bundle.py validate --root <bundle-dir> --strict
```

Fix every real error. Review warnings by materiality and preserve honest advisories. Validate reader-file hashes, relative links, important-cluster reports, registered source/claim references, GitHub trend calculations, and the internal consistency of any optional detailed audit records that are supplied. A schema pass proves internal consistency only; the decisive test is whether the reader suite is broad, current, analytical, technically useful, and appropriately qualified.

## Deliver

Save the complete suite under `frontier-research/<topic-slug>/<as-of-date>/` unless the user requests another location. Return links to the README, executive report, field tree, landscape, GitHub radar, benchmark map, consensus report, and cluster directory. Report all three corpus counts, important clusters, recent-window coverage, validation results, independent quality-gate results, material unresolved gaps, and artifact hashes.

Return the suite in the user's language while preserving original technical and project names. Do not modify product source code or remote systems while researching.
