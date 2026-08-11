# Source and Evidence Contract

Use the generated `schema.json` as the exact field and enum authority. This reference defines the semantic boundaries that the records must preserve.

## Separate corpus metadata from evidence

- A **discovery result** records a search occurrence. It may contain metadata, a snippet, or a weak signal and never supports a technical conclusion.
- An **entity** is the deduplicated paper, repository, benchmark, dataset, product, standard, or other item. `discovered` and `mapped` entities may remain metadata-only.
- A **source** is material actually used in the deep evidence ledger. Only `deep-verified` entities may link to sources that support published claims.

Do not force a discovered item to have a source, paper card, repository card, or claim. Do not drop it from the field map merely because it was not deeply verified.

## Source fitness

Rank evidence by fitness for the exact claim:

1. **T1 primary:** original paper/proceedings, official standard/doc/release/code/issue, first-party dataset, or direct measurement.
2. **T2 authoritative synthesis:** rigorous survey, reputable independent benchmark, or expert analysis with transparent method.
3. **T3 discovery context:** engineering blog, quality journalism, maintainer interview, or community discussion.
4. **T4 lead only:** snippets, generated summaries, SEO pages, unsourced lists, and reposts.

A survey remains T2 for its synthesis. A repository establishes what its inspected code/docs/release contain; it does not by itself prove correctness, performance, adoption, or production readiness. A paper result applies only to its named setup.

Record authority and access separately. `opened` means the exact evidence location was read. `metadata-only`, `blocked`, and `unverified` cannot be the sole support for a published high-risk claim.

## Identity and time

Use canonical URLs and stable identifiers. Normalize paper identity by DOI, arXiv ID without version, then stable provider ID; flag title-based matches for review. Use GitHub node ID when available and preserve rename/transfer aliases. Treat paper↔code, repository↔organization, and repository↔product relations as verified only with explicit link evidence.

Record every operation with the actual UTC clock. The research cutoff is not an execution timestamp. Preserve first publication, latest revision, repository creation, push, release, and observation times separately.

## Paper deep cards

For every deep paper, record identifier, title/authors/year, publication or preprint status, venue/revision and precise status locator, evidence role, task, dataset/version, baselines, model/configuration, metric, limitations, code/data relations, and what was checked when no artifact was found.

Register datasets as dataset entities/sources rather than using a repository ID as a dataset. A preprint is primary evidence for what its authors report, but its status and lack of independent reproduction remain visible.

## Repository deep cards

Separate canonicality from optional paper affiliation. An implementation-led canonical repository may have no paper.

Record stable node identity, owner/repository, aliases, pinned commit, release, created/pushed dates, license, archival/fork state, setup, tests/CI, meaningful maintenance evidence, architecture/code layout, dependencies/integration constraints, and independent adoption evidence. Mark unknowns honestly.

For selected project deep dives, materialize a reciprocal `repository_engineering_profiles.jsonl` record that binds the project to opened fixed-version sources and explains its meaningful components, write/store/index/read-or-action flow, actual dependencies or services, integration constraints, maintenance boundary, project-specific failure modes, adoption boundary, and unknowns. Use enough located detail to support the engineering judgment; fixed cardinalities are guidance, not a substitute for understanding the project.

Execution is optional. Use `executed` only when setup or tests actually ran successfully in the present environment and an execution record saves exact command, environment, timestamps, exit code, and bounded output summary. Reading instructions is `documented`; seeing workflows/tests is `present`. Do not run a repository merely to satisfy a process field—run it when the result can resolve a material architecture, compatibility, reproducibility, or performance question.

Stars, forks, trending rank, or vendor customer names never fill adoption evidence.

## Repository observations and trends

Save dated snapshots with current stars, forks, created/pushed/release state, default-branch commit, and available activity fields. A growth or acceleration metric requires at least two matching observations, its formula/window, completeness note, and `signal_only=true`. It may trigger a deep dive but cannot directly support quality, performance, or adoption claims.

## Atomic claims and evidence joins

Separate facts, comparisons, inferences, and forecasts. Mark explicit numbers, dates, versions, publication/repository status, comparisons, performance, consequential limitations, security, current status, license, setup, tests, and adoption as high risk. Low-risk background descriptions and clearly labeled analytical interpretations need not become one ledger row per clause.

For each claim/source relationship, record a precise locator, bounded support summary, relation (`supports`, `partial`, or `contradicts`), and check time. Numerical support summaries state what the value counts, unit, denominator, setup, and baseline. `evidence.jsonl` remains the single claim↔source authority.

A published high-risk claim requires an opened T1 direct-support join with a precise locator. A source supporting only part of a sentence requires the claim to be split or qualified. Preserve contradictory sources; do not silently choose the convenient side.

A normal-risk inference may synthesize several `partial` joins when its wording is explicitly limited to the inspected corpus, version, or report classification and its semantic audit passes. This exception never applies to numbers, current status, performance, security outcomes, adoption, or a universal absence claim.

Research logs may support only bounded inferences about what this run found. They never prove an external fact or universal absence.

## Publication and semantic audit

Claims may be `published`, `ledger-only`, or `superseded`. Only published claims must appear in reader deliverables. Unsupported or unresolved claims remain ledger-only.

Before publication, perform a clause-level semantic audit for registered high-risk and decision-critical claims. Verify that the exact factual sentence is fully supported, list the evidence IDs used, and record uncovered terms. For lower-risk prose, use conservative wording, paragraph-level citations, and sampled review. `revise` means split or narrow and repeat; `drop` keeps it out. A self-check is an auditable judgment surface, not ground truth; use independent review for consequential work.

Allow the same registered claim in multiple deliverables. Every marked occurrence must preserve its sentence-level marker and evidence semantics. Unmarked analytical prose may not introduce unsupported high-risk facts.

## Syntheses, propositions, and stances

Use synthesis records for analytical moves across claims: consensus, disagreement, trajectory, tradeoff, causal link, and open question. Record the dependent claims/evidence, a disjoint synthesis-level supporting/opposing evidence partition, canonical independent groups, assessment, minority view, unknowns, weighting method, conditions, confidence, limitations, and reversal criteria.

An evidence group is independent only when it does not inherit the same underlying experiment or announcement. Mirrors, reposts, a vendor README, and its launch blog remain one group.

All views of the same repository node—API observation, README, tree, manifest, release, and companion project card—remain one group. A reciprocal paper/repository/dataset family is also one group unless independent authorship or evaluation is explicitly established. Never treat different URL shapes or source-row IDs as independent votes.

## Coverage without false joins

Coverage may list relevant claim and evidence IDs. Derive sources through the evidence table; never require every listed claim to join every listed source. For a missing-evidence conclusion, preserve the exact search scope, research-log source, bounded inference claim, and gap.

## Execution and mutation safety

Research is read-only unless the user separately authorizes executing repositories. Never mutate remote systems. If running a project is justified and safe, isolate it, pin inputs, record commands, and keep observed results separate from author claims.
