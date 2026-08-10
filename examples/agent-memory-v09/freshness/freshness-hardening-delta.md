# Freshness hardening delta

As of: 2026-08-10

The first compiler treated a coarse year/month interval as recent when it merely overlapped a rolling window. The hardened compiler now requires the coarse interval to fall wholly inside a recent window and not extend beyond the as-of date. Repository entity freshness remains based on creation date; recent push/activity is reported separately.

## Corpus effect

| Measure | Before | After |
|---|---:|---:|
| Unique entities | 3,128 | 3,128 |
| Paper entities | 1,685 | 1,685 |
| Repository entities | 1,443 | 1,443 |
| Entities in rolling 12 months | 2,024 | 1,881 |
| Entities in rolling 90 days | 997 | 896 |
| Papers in rolling 12 months | 1,079 | 936 |
| Papers in rolling 90 days | 791 | 690 |
| Repositories created in rolling 12 months | 945 | 945 |
| Repositories created in rolling 90 days | 206 | 206 |
| Future-metadata quarantine | 99 | 99 |

The hardening changed only time-window assignments for 147 entities; entity IDs, query count (56), discovery occurrence count (5,415), paper count, and repository count were conserved.

Separately, 1,267 repositories had a push in the rolling 12-month activity window and 966 had a push in the rolling 90-day activity window. These activity counts are not treated as repository creation or star-growth claims.

## Reproducibility

- Pre-hardening entity snapshot: `entities-pre-hardening.jsonl` — SHA-256 `f658eb642451d8ee94dc1491f39a64066b81f80721381aa01242d679effbf3ab`.
- Post-hardening entity snapshot: `entities-post-hardening.jsonl` — SHA-256 `db4eadf4d4f01a52ea0e75b4628910e72944a5e74c8a552e3ca76294eeb701e5`.
- Recompiled query and discovery ledgers were byte-identical to the originals.
- Full compiler summaries: `../discovery-compile-dry-run-v2.json` and `../discovery-compile-summary-v2.json`.
