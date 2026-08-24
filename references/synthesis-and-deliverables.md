# Synthesis and Deliverables

Write from the field map and deep packets, never directly from source cards. The result is a reader-first suite: evidence remains traceable, but corpus metrics, claim IDs, packets, cluster IDs, screening terms, and saturation records stay in an appendix or audit layer unless they are essential to explain uncertainty.

## Reader-facing suite

A comprehensive run produces a navigable suite under `reader/`, important mechanism reports under `reader/mechanisms/`, scenario reports under `reader/scenarios/`, selected project reports under `reader/projects/`, cross-cutting reports under `reader/cross-cutting/`, and auditable source material under `audit/` or the bundle ledger.

1. `README.md` — top-level topic/version entry, scope, evidence date, and link to the reader suite.
2. `reader/README.md` — default reading paths. Lead with the field question and what the reader will understand; do not make internal artifact navigation the primary content.
3. `reader/overview.md` — independently readable field map: why the field exists, its state objects and central problems, major mechanism branches, their relationship, current practice, 12-month movement, 90-day weak signals, maturity, consensus, disputes, and major unknowns.
4. `reader/architecture.md` — a descriptive general architecture model or architecture anatomy. Show the normal write/manage/store/retrieve/use/feedback flow, cross-cutting concerns, and variants that replace or omit modules. Never label a recommended route, default combination, or best architecture.
5. `reader/solution-landscape.md` — cross-branch solution families, how they differ, which mechanism branch each addresses, and the important tradeoffs and failure modes.
6. `reader/scenarios.md` plus `reader/scenarios/*.md` — cross-branch views for material scenarios. Explain how mechanisms are combined, replaced, or omitted under each scenario's constraints; do not repeat the branches or recommend a configuration.
7. `reader/trends.md` — current mainstream practice, substantive changes in the last 12 months, and clearly qualified 90-day signals, placed back into their technical context.
8. `reader/github-radar.md` — broad candidates grouped by mechanism branch and current signal status. Keep attention, activity, maturity, and verified adoption distinct.
9. `reader/cross-cutting/*.md` — benchmark/evaluation, security/governance, cost/reliability/observability, interoperability/integration, or other material cross-cutting analysis.
10. `reader/consensus-and-open-questions.md` — scoped consensus, counterevidence, disputes, evidence-thin questions, and unresolved problems in plain language.
11. `reader/method-and-scope.md` — discovery, screening, clustering, selection, scope, exclusions, and bias. This is the audit bridge, not required reading for a field overview.
12. `reader/human-review.md` — optional high-impact review items only after the complete reader suite exists.
13. `reader/mechanisms/<slug>.md` — a standalone reader report for every important mechanism branch.
14. `reader/projects/<owner>--<repo>.md` — a small number of real engineering analyses for selected repositories.
15. `audit/README.md` — navigation to evidence authority, ledgers, and any dated update deltas; no new technical conclusions.
16. `site/` — a rebuildable static HTML presentation generated from the completed Markdown suite. `site/index.html` is the visual entry; Markdown remains authoritative.

The suite may add topic-specific reader files. `report.md`, numbered `reports/`, or legacy `clusters/` paths may remain as compatibility surfaces for older bundles, but current reader navigation must point to the semantic `reader/` structure above.

An important branch may be a package rather than a single file. In that case, keep a reader-oriented branch entry and link focused deep pages for the internal mechanisms, fixed-version engineering, and frontier/counterevidence dimensions that the topic needs. The package as a whole must satisfy the standalone branch contract; no required technical depth may exist only in audit files.

## Main-report contract

The overview must stand alone for a technical reader who has not seen the research process. Within a short first read, that reader should be able to explain:

- why the field needs persistent or evolving state;
- what kinds of state it handles and its principal lifecycle;
- the major mechanism branches and their relationships;
- the descriptive general architecture model;
- what is mainstream, what changed in the last 12 months, and what is only a 90-day weak signal;
- maturity, costs, failure modes, consensus, disputes, and unresolved questions.

Start from the domain answer and use a plain-language-to-technical progression: concrete problem or scenario → intuitive explanation → mechanism → precise term. Present at least one reader-oriented map that relates real problems, state objects, lifecycle, mechanism branches, solution families, and cross-cutting evaluation/security/cost concerns. It must not be a corpus DAG or internal taxonomy visualization.

## Mechanism-branch report contract

Organize each important report around a problem and its solution families, not a sequence of papers or repositories. Its shape may vary by branch, but it must independently explain:

- the problem, a concrete motivating situation, and the boundary;
- why a simple alternative does not cover the whole problem;
- the main solution families, how they work, and their architecture, algorithms, data flow, and engineering patterns;
- a substantive internal walkthrough of every major family: state representation, write/manage/read/use path, decision logic, concrete implementation shape, and where cost or correctness moves;
- a clear comparison of families—table or an equally legible synthesis—covering what they solve, strengths, conditions, maturity, costs, and failure modes;
- representative papers, repositories, benchmarks, and negative evidence as evidence and examples, with why they matter;
- current mainstream practice, 12-month changes, and 90-day weak signals;
- scoped consensus, counterevidence, disputes, and a qualified judgment of evidence strength and maturity;
- unresolved questions explained as: what is unknown, why it remains unknown, what understanding it limits, and what evidence is missing.

The comparison is the index to the analysis, not the analysis itself. After reading the report, a technically literate newcomer must be able to explain how several major families operate internally and what current research is changing in each. Reject a branch that only names families, gives each one a short paragraph, presents a generic lifecycle diagram without family-specific mechanics, or turns the recent frontier into a list of paper titles.

When using a branch package, reject it if the entry and child pages merely redistribute the same summary or group sources by type. A useful package separates reader jobs: the entry orients, mechanism pages reconstruct state and algorithms, engineering pages follow real component/data flows, and frontier pages connect counterevidence, costs, failures, and current experiments.

State applicability conditions descriptively. Do not tell the reader which route to select, provide a deployment path, produce an implementation checklist, or rank routes as winners.

## Scenario-view contract

Use scenarios as cross-branch explanatory lenses. For each material scenario, identify the relevant state, which mechanism modules are combined/replaced/omitted, the special constraints, and the branches where detail lives. Avoid restating every base mechanism or implying a recommended stack. Promote the scenario only when it is a distinct technical mechanism rather than a combination of existing branches.

## Project-report contract

A selected repository report is a fixed-version engineering analysis, not a quality card with extra prose. Explain:

- the mechanism route and scenario relationships it embodies, plus what differentiates it from similar projects;
- actual component relationships and the write → authoritative state → derived index → retrieve/context → update/use data flow, with inspected paths or interfaces;
- actual dependencies, backing services, protocols, adapters, deployment assumptions, and integration boundaries from pinned README, manifests, and code;
- maintenance, releases, tests, and version signals without treating attention as adoption;
- project-specific failure modes, maintenance or extension boundaries, and evidence that would reverse the analysis;
- the distinction between code-visible facts, maintainer assertions, executed results, independent integrations, and unverified risk.

Hard-fail a supposed deep dive that is only directories, manifest/workflow/test lists, generic branch risks, or a reusable validation template. If evidence is thin, publish a bounded project card or a gap instead. Do not select projects mechanically by Star count or a fixed quota.

## Evidence and synthesis

Keep atomic claims and evidence records as the audit unit. Require direct support and precise locators for core conclusions, critical numbers, current versions/status, consequential comparisons, security/adoption facts, and material limitations. Ordinary mechanism explanation may use conservative paragraph-level citations when it is reasonable and traceable.

Use synthesis records for consequential cross-source analytical judgments. Their internal markers belong in the audit layer, footnotes, or unobtrusive source machinery—not reader-facing headings, tables, or narrative. A synthesis must state the scoped proposition, independent support and opposition, assessment (`dominant`, `mixed`, `disputed`, or `evidence-thin`), conditions, limitations, confidence, minority view, unknowns, and reversal evidence. Do not count links, citations, or stars as votes.

## Benchmark synthesis

Assign a protocol fingerprint and comparability group before comparing results. Record task, dataset/version, input construction, model, prompt, retrieval/tool budget, context limit, judge, metric, runtime/hardware when relevant, and artifact version. Rank only within a compatible group. Across groups, compare coverage, assumptions, and failure modes instead of headline scores.

## Review and completion

Write the complete reader suite before preparing an optional human-review list. Reserve it for a small set of high-impact conflicts, low-confidence emerging signals, or subjective representative choices. Lack of review must not leave an empty section, suspended conclusion, or incomplete branch report.

Completion is a reader outcome, not a ledger total: a new technical reader should understand the default entry without the audit files, each important mechanism report should stand on its own, selected project reports should describe actual engineering rather than README claims, and key facts should remain traceable. File, source, project, claim, or validation counts alone cannot prove this outcome.

When HTML is generated, validate local links and inspect the entry, long mechanism pages, diagrams, wide tables, search, mobile, dark, keyboard, and print states in a real browser. A successful Markdown-to-HTML conversion alone does not establish that the presentation helps understanding.
