# Incremental mapping workspace

This directory contains the deterministic Q0057–Q0074 screening and mapping
increment over the 1,191 entities that had no baseline screening record.

Files:

- `materialize_incremental_mapping.py` — frozen classifier, manual boundary
  overrides, canonical C01–C16 assignment, materializer, and byte-level checker.
- `proposals.jsonl` — one metadata-level `map`, `defer`, or `exclude` decision
  for every incremental entity, with reason and inspection scope.
- `summary.json` — exact counts, query-level information gain, invariants, and
  hashes for the five modified bundle files.
- `review.md` — readable query-by-query mechanism, boundary, saturation, and
  recent-repository audit.

Reproduce without writing:

```powershell
$env:PYTHONUTF8='1'
python .\materialize_incremental_mapping.py --check
```

`--preview` rewrites only the three generated artifacts. `--apply` also writes
the five authorized mapping files under `bundle/`. The script refuses a first
apply if frozen discovery inputs or the pre-increment mapping hashes changed.

This operation is taxonomy mapping only. It never creates deep sources, never
promotes an entity to `deep-verified`, and never treats GitHub stars or push
dates as relevance, quality, maturity, or adoption evidence.
