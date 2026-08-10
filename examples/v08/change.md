# v08 historical acceptance decision — superseded

> Superseded by direct user review on 2026-08-10. v08 passed the old evidence/provenance rubric but is not the accepted final solution. Its discovery breadth, recency, clustering, synthesis, GitHub trend tracking and per-cluster depth are insufficient. See `..\USER_FEEDBACK.md`.

## Outcome

v08 is the accepted final forward test: **94/100, H1–H5 all pass**. No v09 was started because the objective was to iterate until the Skill could reliably retrieve high-quality papers and repositories and produce a deep, broad, evidence-backed report; the frozen rubric and hard gates now confirm that outcome.

## Changes from v07

- Split or narrowed the v07 compound claims and required each report claim to have an exact statement, marker, evidence join and clause-level semantic audit.
- Added `executions.jsonl`; repository setup/tests may be marked executed only when a successful matching command record exists. v08 performed no repository execution, so all thirteen repository cards honestly remain documented/present/missing.
- Added paper evidence roles and separate dataset sources. The survey is T2, and LongMemEval, MemoryAgentBench and Mem2ActBench each have explicit paper↔repo↔dataset chains.
- Added the missing canonical `HUST-AI-HYZ/MemoryAgentBench` and `Cantaloupe-M/Mem2ActBench` repositories with pinned commits, license, setup, CI and release status.
- Strengthened the full-profile candidate funnel: all three passes retain excluded/deferred candidates, and the landscape report uses a common comparison table.
- Saved the complete normal/strict validation transcript, counts and hashes in `validation.txt`.
- Rechecked the v07 factual regressions: MEXTRA uses 30 attacking prompts and 200 records per agent, with EHRAgent 50/55 and RAP 26/27 extracted/retrieved counts; LongMemEval S/M are scale conditions and Oracle supplies evidence sessions; current Google/AWS/Microsoft/LangGraph/LangMem status is sourced from first-party materials.

## Frozen result

- Three research passes only: Map 6, Focus 8, Verify 6; no fourth pass.
- 16 requirements, 20 queries, 69 candidates, 45 sources, 19 papers, 13 repositories, 0 executions, 16 coverage records, 66 claims, 177 evidence joins and 66 semantic checks.
- Candidate funnel: 53 retained, 11 excluded, 5 deferred.
- Normal validation: exit 0, `OK: bundle is valid`.
- Strict validation: exit 0, `OK: bundle is valid`.
- `report.md` and `output.md` are byte-identical, 21,101 bytes, SHA-256 `98C898A7A2980C2333631A2D48E25EDD00E6E175EB72897C490743AD56E35F34`.
- Independent review: 94/100, H1–H5 pass; review SHA-256 `0679CC95A48FF6DAB2E96A22EED7A407997F13ED7A6148BD25307D27BAC876E8`.

## Remaining honest limits

- No repository was installed or executed; documentation and CI presence are not runtime reproducibility.
- Several high-risk claims have only one independent source group because only the original paper, canonical repository or official product owner directly supports the scoped statement.
- There is no unified public benchmark for derived deletion, cross-tenant access control, storage growth, failure recovery and full-lifecycle cost.
- No third-party production case in the bounded search disclosed deploy version, traffic scale and failure data together.

These are retained advisories and update targets, not reasons to invent evidence or continue an otherwise accepted iteration.
