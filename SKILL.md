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
- [research-figure-generation.md](references/research-figure-generation.md) before generating or integrating AI-created research figures;
- [html-presentation.md](references/html-presentation.md) before generating or reviewing the reader-facing HTML site;
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

For each important mechanism branch, first synthesize its solution families and their differences, then **open each major family far enough that a reader can reconstruct how it works**. Explain its state model, write/manage/read/use steps, algorithms or control decisions, concrete engineering shape, applicability conditions, shifted costs, and characteristic failures. Connect representative papers and repositories to those mechanics instead of summarizing them one by one. End with a concrete recent research agenda: name which layer current work is changing, why earlier designs are insufficient, and which missing mechanism or experiment blocks the next conclusion. A comparison table plus a few summary paragraphs is an outline, not a deep report.

Do not force a large branch into one overloaded file. When a concise branch map cannot also explain its major families at reconstructable depth, use a **branch package**: keep a readable entry map and link to focused deep dives such as internal mechanisms/algorithms, fixed-version engineering walkthroughs, and counterevidence/cost/current research. The exact split is topic-dependent; three files are not a quota. The entry must remain independently orienting, and the deep pages must answer technical questions rather than repeat the map or divide a source inventory into smaller lists.

Allocate space by importance, novelty, controversy, and engineering value; do not force a uniform template, source count, or length. However, hard-fail an important branch when its major families remain names with one-paragraph descriptions, when a generic diagram substitutes for family-specific data flows, or when “recent work is active” substitutes for explaining what current research is trying to solve.

Application scenarios are cross-branch views: explain which mechanisms are combined, replaced, or omitted and what constraints become salient. They are not recommendations. Promote a scenario to a primary mechanism branch only when it is itself a distinct technical route.

For a selected repository, inspect pinned code and documentation closely enough to explain its actual components, write/store/index/retrieve/update/use data flow, dependencies and services, interfaces and integration boundaries, maintenance signals, and project-specific failure modes. Distinguish visible code facts, maintainer assertions, execution results, and unverified risks. Run code only if the result could change a material conclusion.

### 6. Verify in layers and synthesize the reader suite

Apply strict direct evidence and precise locators to core conclusions, critical numbers, versions, comparisons, security/adoption facts, and consequential limitations. Use conservative citations and logical coherence for ordinary explanatory prose. Keep claims, evidence, screening, and saturation ledgers for traceability, but keep their IDs and process language out of reader prose.

Draft the reader suite only after mapping and deep packets exist. Lead with the field answer, not corpus counts or internal taxonomy. Use the report contract to make the main report independently readable, present a descriptive **general architecture model** rather than a recommended architecture, and give each important mechanism branch a clear solution-family comparison. Describe applicability conditions, maturity, tradeoffs, failure modes, consensus, disputes, and uncertainty without telling the reader what to choose or deploy.

When a generated figure would materially improve first-glance understanding, build a small figure inventory and follow `references/research-figure-generation.md`. Before calling an image tool, present the complete text-only visual plan and wait for explicit user approval. Keep source-grounded entities and relationships separate from visual composition, inspect the actual raster, and retain exact conclusions in Markdown or a code-native diagram. Do not add decorative images or force one figure per page.

After the Markdown reader suite is complete, generate the static HTML presentation with `scripts/render_reader_html.py`. Treat HTML as a rebuildable understanding layer: preserve Markdown as the authority; validate rewritten links and UTF-8; keep diagrams searchable and readable without interaction; and inspect the entry, a long mechanism page, a project page, search, mobile layout, dark mode, and print structure in a real browser. Do not hand-edit generated HTML.

Before reader editing is complete, perform an input-absorption review for every important branch. A selected paper, repository, benchmark, or negative result counts as absorbed only when it changes a state/algorithm explanation, a concrete engineering data flow, an experimental boundary, a qualified judgment, or the research agenda. A name in a table or bibliography does not count. Leave broad long-tail coverage in the audit/radar rather than turning it into reader inventory.

Complete the first reader-ready suite before creating an optional human-review list. Reserve that list for high-impact uncertainty, conflicting evidence, or genuinely subjective representative choices; never leave a branch as a placeholder awaiting approval.

### 7. Audit the actual result

Run the outcome gates in [evaluation-gates.md](references/evaluation-gates.md) and both deterministic validations:

```text
python <skill-dir>/scripts/research_bundle.py validate --root <bundle-dir>
python <skill-dir>/scripts/research_bundle.py validate --root <bundle-dir> --strict
python <skill-dir>/scripts/render_reader_html.py --root <bundle-dir> --output <bundle-dir>/site
python <skill-dir>/scripts/render_reader_html.py --root <bundle-dir> --output <bundle-dir>/site --check
```

Fix real errors and preserve honest advisories. A schema pass, source count, claim count, file count, or green validator alone cannot establish completion. The decisive test is whether a new technical reader can understand the field from the default entry, independently understand each important mechanism branch, and trace key claims without audit machinery interrupting the narrative.

## Deliver

Save the suite under `frontier-research/<topic-slug>/<as-of-date>/` unless the user requests another location. Return links to the HTML entry, Markdown reader entry, general architecture model, mechanism landscape, scenario views, current-trend radar, evidence/limitations material, branch reports, and selected project reports. Summarize recent-window coverage, verification status, important unresolved gaps, and any optional human-review questions.

Return in the user's language while preserving original technical and project names. Do not modify product source code or remote systems while researching.
