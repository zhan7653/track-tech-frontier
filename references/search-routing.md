# Search Routing and Coverage

Route discovery by the field's evidence ecology. Use [breadth-and-trends.md](breadth-and-trends.md) for corpus and freshness details.

## Evidence ecologies

- **Research-led:** prioritize scholarly metadata, recent preprints, official proceedings, original papers, benchmarks, datasets, citations, and author-linked code.
- **Standards-led:** prioritize normative specifications, proposals, charters, conformance suites, design repositories, issues, release phases, and independent implementation status.
- **Implementation-led:** prioritize canonical repositories, code architecture, docs, releases, commits, issues/PRs, tests, dependencies, integration evidence, and adjacent implementations.
- **Product-led:** prioritize official release notes/docs for current capability, then independent measurements, adoption, incidents, security, lock-in, migration, and alternatives.
- **Mixed:** run each applicable lane independently before synthesis. Do not let the easiest-to-search lane stand in for the field.

## Coverage grid

Build a live diagnostic grid across:

```text
important cluster × evidence lane × time window × perspective
```

Freeze the user's contract before discovery. Add derived research questions and gap records as the map evolves. Use the grid to expose skew, stale areas, and missing evidence lanes; judge overall completeness from field-level breadth, important-cluster coverage, and the materiality of remaining gaps. Exact cell-level proof is reserved for consequential gaps, disputed boundaries, and bounded-absence conclusions. An umbrella category does not automatically cover all members.

## Query stages

Queries are not limited to a fixed number of passes. Label each exact query with one stage:

- `pilot` — estimate ecology and expose aliases/clusters;
- `discover` — high-recall paper, GitHub, benchmark, product, or standard search;
- `map` — resolve identity, links, aliases, and cluster boundaries;
- `gap-fill` — close a named lane, time-window, perspective, or cluster gap;
- `deep-focus` — open original evidence for a selected deep packet;
- `verify` — confirm freshness, version, canonical identity, high-risk support, or contradiction;
- `adversarial` — search limitations, failures, critique, security, deprecation, lock-in, contamination, or negative results;
- `refresh` — recheck mutable sources in update mode.

Record iteration, parent query IDs, target lanes/windows/clusters, linked gap, exact request, UTC time, result count or limitation, and information-gain note.

## Paper lane

Run broad topic/alias searches, recent-window searches, survey/taxonomy seed expansion, venue and author searches, backward/forward citations, benchmark and dataset searches, and reproduction/critique searches. Reopen original papers or proceedings before deep use. Preserve publication status, revisions, data/code links, experiment conditions, and limitations.

## GitHub lane

Run aliases, topics, paper titles/IDs, benchmark names, author/organization, created-window, pushed-window, release, high-attention, and deprecated/archived searches. Partition capped result sets by time and attention bands. Verify canonical owner and stable node identity before mapping. For deep items, inspect the exact commit, architecture, setup, tests/CI, license, releases, maintenance, issues/PRs, paper relation, and independent adoption.

Implementation-led repositories need not have a paper. Record canonicality separately from optional paper affiliation.

## Benchmark lane

Search benchmark papers, dataset cards, harness repositories, revisions, contamination, replication, task coverage, and competing baselines. Create protocol fingerprints and comparability groups before preserving numerical results.

## Standards, product, and adoption lanes

Search normative/specification indexes, phases, changelogs, compatibility tables, release notes, security advisories, migration/deprecation notices, independent deployments, incidents, and alternatives. Treat dynamic tables and docs as dated evidence.

## Negative and contrarian lane

Run multiple adversarial families, not a single token query. Include failure, limitation, critique, replication, benchmark caveat, contamination, security, privacy, poisoning, stale data, deletion, lock-in, abandonment, and cost. Preserve contradictory sources and investigate whether differences follow from versions, protocols, or conditions.

## Saturation review

After every material expansion cycle, update field- and cluster-level coverage and note which lanes, windows, or perspectives changed. Continue if the cycle discovers a first-order cluster, changes a boundary, adds a high-signal recent entity, introduces a credible new stance, reveals a canonical artifact, or changes a decision conclusion. Stop when likely remaining gains are non-material for the report and material gaps are explicit.
