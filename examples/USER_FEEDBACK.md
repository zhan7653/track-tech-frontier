# Confirmed user feedback

## 2026-08-10 — Input breadth is insufficient

The user does not consider v08 a sufficiently comprehensive technology-research input, despite its rubric score and evidence traceability.

Confirmed observations:

- The retained paper set is too small.
- The retained repository set is too small.
- The proportion and absolute number of genuinely recent works are insufficient.
- The field breadth is therefore not adequately covered; a small, highly qualified evidence set cannot by itself support a comprehensive landscape review.
- Breadth and depth are separate objectives and must be evaluated separately.
- The required order is breadth first, then depth: broadly absorb and map the field before selecting the highest-quality or most consequential items for deep reading and verification.

Design correction for any future iteration:

1. Treat broad discovery as its own first-class phase, optimized primarily for recall and recent-work coverage.
2. Preserve a substantially larger discovered corpus of papers, repositories, benchmarks, products and weak signals before applying deep evidence gates.
3. Separate at least three populations in the artifacts and evaluation: discovered, screened/mapped, and deeply verified.
4. Use the broad corpus to establish taxonomy, clusters, temporal evolution and missing areas; do not infer the field map only from the deeply verified shortlist.
5. Apply strict paper↔code, source-quality and claim-level evidence checks to the selected deep-dive subset after broad coverage has been demonstrated.
6. Evaluate freshness independently from general source quality, so a historically strong but insufficiently current corpus cannot pass as a frontier survey.
7. Do not treat v08's 94/100 rubric result as overriding this feedback. v08 demonstrates precision, provenance and report-control quality; it does not yet demonstrate sufficient discovery breadth for a comprehensive survey.

Exact numeric breadth/freshness thresholds remain intentionally unset until they are designed and tested; they must not be invented from this feedback alone.

## 2026-08-10 — Output is collection-oriented, not research synthesis

The user rejects v08 as a final research-report solution. Passing the old rubric does not constitute user acceptance.

Confirmed problems:

1. The report reads like a sequence of paper, repository and product introductions. This is a workflow failure, not merely a writing-style issue: the system collected and verified items but did not perform enough analysis or synthesis.
2. The previously inspected research repositories were not operationalized at the level that matters. The implementation borrowed bounded search, provenance and validation controls, but failed to deliver their multi-perspective expansion, recursive gap filling, research decomposition and synthesis quality. Component-level comparison was incorrectly treated as parity with their research output.
3. A proper result should resemble a high-quality survey in its reasoning structure, without becoming paper-centric:
   - derive a field tree or graph from broad evidence;
   - cluster what the field is currently doing into coherent blocks;
   - explain what problem, architecture, implementation pattern and tradeoff define each block;
   - identify weighted consensus, disagreement, maturity, negative evidence and open questions;
   - connect the blocks into a historical and causal technical trajectory.
4. Breadth and depth must become separate deliverables:
   - breadth: map a large corpus, discover clusters and explain what the community is doing;
   - depth: within every important cluster, select high-quality papers and repositories for substantial standalone analysis.
5. GitHub must be a first-class engineering evidence lane, not an appendix to papers. The workflow must actively track newly created and recently accelerated high-star repositories, releases, maintenance and implementation patterns. Old foundational repositories and current trend repositories must be separated.
6. Stars are not proof of technical quality, performance or production adoption, but recent star growth and repository activity are necessary discovery and trend signals. They must trigger investigation rather than directly support conclusions.
7. The task objective is the best possible report and strong tracking of the newest trends. Cost minimization is not a goal. The workflow may use many stages, repeated searches, multiple specialized analyses and multiple output files.
8. A single compact report is the wrong output container. Expected artifacts may include a broad landscape, taxonomy/tree, timeline, consensus and controversy synthesis, repository radar, benchmark map, per-cluster deep reports, project deep dives and an executive decision report.
9. Evidence correctness remains necessary but is not the primary definition of success. A fully cited list of introductions is still a poor research report.

Required correction in future design:

- Replace the early three-pass/source-budget optimization with staged saturation criteria based on field clusters, recent windows and unresolved perspectives.
- Add genuine synthesis stages after collection: clustering, taxonomy induction, consensus weighting, contradiction analysis, causal/temporal storyline construction and cross-cluster comparison.
- Use supervisor/worker or equivalent decomposition for parallel breadth discovery and independent per-cluster deep research.
- Evaluate output synthesis, insight, structure, consensus quality, trend sensitivity and engineering usefulness separately from citation/provenance correctness.
- Compare future output directly with the report behavior of the inspected research systems, not merely with their component checklist.

Until these corrections are implemented and re-evaluated, v08 is a precision/provenance baseline, not the accepted final solution.
