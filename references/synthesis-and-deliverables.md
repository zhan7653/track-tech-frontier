# Synthesis and Deliverables

Use the field map and cluster deep packets as the writing inputs. Do not write the final suite directly from source cards.

## Reader-facing suite

A full run produces a navigable multi-file suite under `reports/` plus deep reports under `clusters/` and selected project reports under `projects/`:

1. `README.md` — entry point, as-of, status, reading paths, artifact navigation, IDs, and unresolved gaps; no new technical conclusions.
2. `01-executive-decision.md` — cross-cluster conclusions, important changes, decision implications, uncertainty, and next actions.
3. `02-field-tree.md` — the field DAG rendered as a readable tree/graph with definitions, boundaries, overlaps, corpus counts, and recent coverage.
4. `03-landscape-synthesis.md` — what the field is doing, organized by cluster; problem, architecture, implementation, maturity, and tradeoffs.
5. `04-history-and-causality.md` — verified events, source-asserted influence, report inferences, and forecasts kept distinct.
6. `05-consensus-controversies.md` — scoped propositions, supporting and opposing independent groups, conditions, minority views, and reversal criteria.
7. `06-github-trend-radar.md` — foundational, established-active, new/accelerating, and watchlist repositories; momentum, maturity, and adoption in separate columns.
8. `07-benchmark-map.md` — task tree, datasets/versions, memory or system setup, metrics/judges, protocol fingerprints, comparability groups, and gaps.
9. an optional topic-specific report such as security/failure, standards, or products when material;
10. `09-method-and-limitations.md` — discovery, screening, clustering, selection, execution, saturation, exclusions, and bias;
11. `10-source-index.md` — navigation only, grouped by cluster, type, date, and role;
12. one `clusters/<id>-<slug>.md` for every important cluster;
13. `projects/<owner>--<repo>.md` for decision-critical, representative, or trend-triggered repositories.

The artifact manifest may add topic-specific files. A single `report.md` may exist as a compatibility index, but it is not the only inspected output.

## Cluster report contract

Every important cluster report must answer:

- What problem does this cluster solve, and what is outside its boundary?
- What are the dominant mechanism, architecture, and implementation patterns?
- Why did these patterns emerge historically?
- Which papers, repositories, benchmarks, and products are representative, and why?
- What do high-quality sources agree on within a stated scope?
- Which results conflict, and are differences explained by task, data, model, protocol, cost, or incentives?
- What is the strongest negative result or failure mode?
- How closely do repositories implement the published ideas?
- What changed in the recent window, and which signals remain weak?
- What is known, unknown, and the next decisive test?
- What should a technical decision-maker do with this cluster?

Do not create a paragraph per source. Use sources as evidence inside an argument organized around the questions above.

## Project report contract

A selected repository report is a fixed-version engineering analysis, not a quality card with extra prose. For every project deep dive:

- pin the exact commit/release and separate repository-created, recently-pushed, and release dates;
- explain project-specific component relationships and the write → authoritative state → derived index → read/context/action data flow, naming inspected paths or interfaces;
- inspect actual dependencies, backing services, protocols, adapters, and deployment assumptions from pinned README/manifests/code—not merely manifest filenames;
- state concrete integration constraints such as runtime/database/provider requirements, migration/version boundaries, tenant/permission assumptions, or index/rebuild behavior;
- analyze maintenance evidence beyond a star snapshot: recent commits/contributors plus issue/PR/release signals when observed, with unmeasured latency, close rate, bus factor, and support boundaries left explicitly unknown;
- identify project-specific failure modes, verification steps, and the exact evidence that would reverse the engineering judgment;
- distinguish README/maintainer assertions, visible code surface, executed results, independent integrations, and production adoption;
- attach precise README/tree/manifest/code/API locators and mark any reconstructed data flow as an inspection-based inference.

Hard-fail a supposed project deep dive that is only top-level directories, manifest/workflow/test path lists, generic cluster risks, and a reusable validation template. If the evidence does not support a real deep dive, publish a bounded project card or gap instead of calling it deep.

## Synthesis blocks

Keep atomic claims as the source-level audit unit, but allow a coherent paragraph to combine them. Mark a cross-source analytical block with a stable synthesis ID and the claims it depends on, for example:

```html
<!-- synthesis:Y042 claims:C017,C031,C088 clusters:CL03 -->
```

The corresponding synthesis record must state the proposition or analytical move, a disjoint synthesis-level partition of supporting and opposing evidence IDs, their canonical independent groups, assessment (`dominant`, `mixed`, `disputed`, or `evidence-thin`), minority view, unknowns, weighting method, confidence, conditions, limitations, and reversal criteria. Claim-level `supports`/`contradicts` relations cannot be reused as synthesis stance automatically: a source may support a negative atomic claim while opposing the higher-level proposition. A paragraph may contain multiple sentence-level claim markers. Each marker still immediately follows the exact supported factual sentence, but it no longer has to be the only prose in the paragraph. Register and mark all high-risk or decision-critical source facts; lower-risk connective analysis may remain unmarked when it is conservative, traceable at paragraph level, and introduces no consequential new fact.

A `cross-source synthesis` proposition must be an actual analytical judgment and use at least two canonical evidence groups. It may not equal or embed one underlying atomic claim, contain an HTML claim marker, or masquerade a repository metadata snapshot as consensus. Use an evidence-aggregation action for a single project or single-family inspection.

Every substantive block must either:

- perform a named synthesis action and cite its underlying claims;
- contain one or more evidence-backed atomic claims;
- be a narrowly marked method, limitation, or navigation block.

Reject consecutive project-introduction paragraphs, source-by-source summaries, or prose that merely restates metadata without explaining a mechanism, pattern, comparison, conflict, or implication.

## Consensus weighting

Assess consensus at the proposition level. Consider:

- number of genuinely independent evidence groups;
- primary evidence versus survey or vendor repetition;
- peer review and publication status;
- independent reproduction and public artifacts;
- protocol relevance and comparability;
- freshness and version alignment;
- credible contradictory or negative evidence;
- applicability conditions and population boundaries.

Use `dominant`, `mixed`, `disputed`, or `evidence-thin`, with a rationale. Preserve the strongest minority view and the evidence that would reverse the assessment. Never use citation, source, or star counts as a vote by themselves.

## Benchmark synthesis

Assign a protocol fingerprint and comparability group before comparing results. At minimum record task, dataset/version, input construction, model, prompt, retrieval/tool budget, context limit, judge, metric, runtime/hardware when relevant, and artifact version. Quantitatively rank only within a compatible group. Across groups, compare coverage, assumptions, and failure modes instead of headline scores.

## Executive synthesis

Write the executive report last. Each conclusion must link to at least one cluster report and one closed synthesis/claim chain. It must state the current field-level judgment, what changed recently, what is mature, what remains disputed, and which next test or adoption action follows. The executive writer may not introduce new source facts.
