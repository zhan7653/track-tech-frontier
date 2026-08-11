# Breadth Discovery and Trend Tracking

Use this reference during discovery, mapping, and freshness analysis. Prefer official APIs and primary indexes; save exact requests and dated snapshots because live results drift.

## Paper discovery

Use several independent routes rather than one search engine:

1. recent survey/taxonomy seeds and their original references;
2. scholarly metadata or semantic indexes for broad keyword and topic retrieval;
3. arXiv or domain preprint indexes sorted by submission and update date;
4. official proceedings, DOI registries, and venue programs;
5. backward references and forward citations from high-value seeds;
6. benchmark, dataset, author, lab, and organization searches;
7. explicit recent-window and adversarial query families.

For each result occurrence, preserve provider, exact query or URL, rank, page/cursor, UTC observation time, raw identifier, title, dates, and available abstract/metadata. Recommended canonical keys are normalized DOI, arXiv ID without version, then stable index ID; use normalized title + first author + year only as a flagged possible duplicate.

Treat surveys and index metadata as map inputs. Reopen original papers or proceedings for deep evidence. Record first publication and latest revision separately.

## GitHub discovery

Search aliases, paper titles and identifiers, benchmark names, authors/organizations, repository topics, README text, and predecessor names. Run separate query families for:

- newly created repositories in recent windows;
- recently pushed or released repositories;
- high-attention repositories regardless of age;
- paper-linked and benchmark-linked implementations;
- competing engineering approaches and adjacent terminology;
- archived, deprecated, security, and failure signals.

Use the GitHub repository node ID as the stable identity when available. Preserve owner/name aliases after rename or transfer. Save every query and snapshot time. If a result window is capped, partition it into non-overlapping created/pushed date buckets and then by stars or language.

Keep discovery and enrichment separate. A broad GitHub search should remain one search request per page; do not turn it into an N+1 crawl by resolving the default-branch commit, releases, contributors, and CI for every hit. Enrich those fields only after mapping has established relevance, then perform the full repository card on the deep subset. Unknown activity fields stay unknown—they are never encoded as zero.

For mapped repositories, collect at least current stars, forks, created time, pushed time, latest release time, default-branch commit, license, archival/fork state, primary language, setup, tests/CI, and paper/project linkage when available. For deep repositories, also inspect meaningful contributor activity, issues/PRs relevant to maturity, architecture/code layout, dependencies, release cadence, and downstream deployment evidence.

Never infer star velocity from a single cumulative count. Calculate velocity or acceleration only from multiple dated snapshots. Record the formula, observation IDs, window, missing intervals, and `signal_only=true`.

## Time windows

Always include explicit date-window discovery. A full frontier run normally inspects:

- the rolling 90-day weak-signal window;
- the rolling 12-month frontier window;
- the preceding 12–24 months;
- foundational work before those windows.

Adjust the windows when the field moves more slowly or the user specifies another horizon, but record the choice before the breadth phase. Report unknown dates in denominators rather than silently dropping them.

Provider metadata can be future-dated, incomplete, or internally inconsistent. Quarantine post-cutoff publication metadata in an explicit future/invalid bucket and screen it separately; never count it as current or recent evidence. Preserve failed, rate-limited, malformed, and superseded queries with their exact request and limitation so the apparent recall is not overstated.

## Screening and promotion

Screen in two steps:

1. **Map promotion:** verify identity, relevance, date, item type, cluster membership, and why the item changes the map or fills a lane.
2. **Deep promotion:** select for cluster importance, technical centrality, recent momentum, decision impact, evidence quality, independent contradiction, benchmark role, or implementation relevance.

Do not use a single quality score to collapse distinct dimensions. Preserve publication status, source directness, recency, reproducibility, code/data availability, independence, engineering maturity, and adoption separately.

## Recall and saturation proxies

Open-world recall cannot be proven from one result set. Use auditable proxies:

- overlap and unique yield across independent providers/query families;
- new first-order clusters per discovery cycle;
- new important entities and new opposing stances per cycle;
- unresolved high-attention or recent entities;
- unmapped and bridge-item rates;
- aggregate coverage across lanes, time windows, and important clusters, plus material blind spots;
- citation and repository-link closure around decisive seeds.

Require a human or model mapper to inspect the highest-signal excluded, deferred, unmapped, and collision candidates, using stratified samples for the long tail. Do not manufacture exclusions to satisfy a ratio.

## Freshness interpretation

Report freshness independently from general quality:

- absolute and proportional recent paper counts by cluster;
- new and recently active repository counts by cluster;
- latest deeply verified evidence date per important cluster;
- material trend signals investigated and unresolved;
- current product/release/standard status checked as of the run date.

Foundational evidence cannot compensate for a stale frontier window. Conversely, a new preprint or high-growth repository is a signal, not a mature conclusion.
