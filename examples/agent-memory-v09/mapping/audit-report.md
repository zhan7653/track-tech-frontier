# v09 mapping audit

Audit date: 2026-08-10  
Seed: `v09-mapping-audit-20260810`  
Role: independent read-only audit of the six mapper proposal files before canonical reconciliation.

## Scope and sample

The audit first verified structural conservation: 3,128 packet entities produced exactly 3,128 proposals; packet and proposal hashes matched their manifests; IDs, enums, and required fields were valid.

The judgment sample contained 120 entities, stratified across `(paper|repository) × (map|deep-candidate|exclude|defer)`, 15 per stratum. It contained 60 papers and 60 repositories; 30 examples of each decision; and 25 foundational, 32 2024–2025, 31 rolling-12-month, 26 rolling-90-day, and 6 future-metadata examples. All six mappers were represented. Separate full inspections covered the top 30 repositories by snapshot stars, the 30 newest deep-paper candidates, the 30 newest deep-repository candidates, all 99 `W_FUTURE_METADATA` records, and normalized-title/cluster conflicts.

## Pre-reconciliation gate result

- G1 breadth: partial. The population was ample, but `deep-candidate` remained a metadata-screening decision rather than source verification.
- G2 freshness/trend: partial. Time windows and future quarantine existed, but release evidence, creation versus activity, and longitudinal trend observations were incomplete.
- G3 field map: fail before reconciliation. Six mappers produced 115 unreconciled primary labels, and defer records were counted inconsistently in substantive clusters.

These are pre-reconciliation findings. They do not describe the later canonical DAG after overrides and alias reconciliation.

## Error patterns found

The equal-decision sample contained eight clear false inclusions among 60 map/deep samples (13.3%). This is a risk observation for the stratified sample, not a population estimate. The recurring causes were:

1. ordinary KV-cache, attention, serving, or hardware optimization treated as semantic Agent Memory;
2. human/neuroscience or generic continual-learning work without an Agent Memory bridge;
3. generic vector databases, RAG systems, frameworks, and applications promoted because memory appeared in a feature list;
4. high snapshot stars or recent creation/push causing a promotion beyond what title and description supported;
5. repository metadata being used to infer mechanisms such as versioning, auditing, or tiered memory that were not visible in the packet;
6. `defer` entities retaining substantive cluster labels, thereby contaminating cluster counts.

All 99 future-metadata records remained excluded or deferred (63/36); none was promoted. However, future metadata and all other defers had to be removed from mapped/freshness/cluster counts.

## Required reconciliation policy

The audit required decision-first processing:

1. `exclude` stays outside the DAG;
2. `defer` and `W_FUTURE_METADATA` go to an unresolved hold and do not contribute to map, freshness, or cluster counts;
3. explicit entity overrides precede alias mapping;
4. generic KV/serving, generic databases/RAG, human memory, and feature-list applications default to exclusion unless an Agent Memory persistence/lifecycle/control mechanism is explicit;
5. stars, recent creation, and recent push remain inspection signals, not evidence of growth, quality, maturity, or adoption;
6. service/control plane, storage/index, structured/temporal representation, lifecycle, application support, and model-native boundaries remain separate rather than being collapsed into “memory infrastructure.”

The independent audit supplied 20 priority overrides. The canonical materializer also applied the broader planner override set and recorded the final decision for every affected entity in `reconciliation/audit-overrides.jsonl`; that ledger, rather than this prose, is authoritative for the post-reconciliation corpus.

## Limitations

The audit judged metadata screening, not the truth of paper or repository claims. It did not execute repositories, validate benchmark results, infer adoption, or turn snapshot popularity into a time series. Deep verification and synthesis therefore remain separate downstream stages.

