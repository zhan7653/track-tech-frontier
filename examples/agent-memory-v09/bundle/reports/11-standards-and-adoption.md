# Agent Memory 标准、互操作与采用追踪

**Audit cutoff:** 2026-08-10T10:07:50Z  
**Execution policy:** source and repository inspection only; no project code was run.  
**Scope:** standards status, interoperability boundaries, portability/conformance artifacts and independently auditable adoption signals.  
**Stop rule:** after every material change, continue until two consecutive successful cycles each contain real adoption, standards and product-boundary probes, add no entity/high-signal item/first-order cluster/stance, and change neither a boundary nor a published proposition.

## Bottom line

The earlier first-order conclusion survives, but the project layer was materially under-covered.

There is still no basis for describing the field as a contest among mature formal memory standards. The W3C activity is a **Community Group**; SAIHM is an **individual Internet-Draft with no RFC/standards level and stream None**; MCP is the mature adjacent protocol, whose current official extension overview includes Authorization, Apps and Tasks but no memory extension. MCP Tasks persists the lifecycle of long operations through durable handles; it does not define persistent memory semantics.

What changed is the breadth and engineering maturity of the **project-spec** layer. Five omitted 2026 repositories contain real normative or conformance assets:

- MGP: governed memory service contract, schemas, OpenAPI, adapters and a same-project compliance suite.
- Engramory: an experimental portable local file/rules discipline with host adapters and explicit scale/migration limits.
- eMEM: a signed, content-addressed fact protocol with code, SDKs, test vectors and a project-operated responder.
- OCF: a portable committed-working-context/governance bundle with schemas and fixtures, explicitly not a wire protocol.
- glatinone AMP: a v0.1.0 project draft with server/SDK/tests and successful same-project CI.

Paper and scholarly discovery also added Portable Agent Memory and Engram, plus a distinct same-name probabilistic UMP. These additions broaden the map; they do not elevate any artifact to a formal standard.

The adoption conclusion must be narrowed, not inverted. Two inspectable external signals exist:

1. Agent Memory Hall implements a bidirectional UMP adapter with tests and public CI, but the code matches an older UMP 0.1-shaped model and fails the pinned UMP 1.0 record shape by inspection.
2. An external Agent Team Kit bootstrap clones and installs tinqiao Engramory, but it is unversioned, one-maintainer and lacks conformance, CI or production-deployment evidence.

Therefore “zero external activity” is false, while “current-version independent conformance or production adoption demonstrated” remains unsupported.

## What each saturation cycle changed

| Cycle | Provider/scope | Result | Material? |
|---|---|---|---|
| 01 | W3C API, IETF Datatracker, MCP official docs | Corrected current official status; added MCP Tasks while preserving the no-memory-extension boundary | yes |
| 02 | GitHub exact canonical-URL searches for earlier candidates | Separated citations/digests/lists from implementations; held Maki for source inspection | no |
| 03 | Pinned GitHub source/tests/CI + UMP schema | Found a real external UMP-related adapter, then bounded it to UMP 0.1-shaped partial portability | yes |
| 04 | OpenAlex + paper/DOI/repository deep checks | Added PAM, Amore partial pattern adoption, Engram, and a same-name UMP collision | yes |
| 05 | Fresh GitHub repository discovery + pinned deep checks | Added MGP, Engramory, eMEM, OCF and glatinone AMP; expanded first-order project clusters | yes |
| 06 | External canonical-URL code search + file inspection | Found one real but weak external Engramory integration | yes |
| 07 | Six successful Crossref bibliographic probes | No new entity, adoption report, conformance artifact or stance | no |
| 08 | Six successful DataCite exact-title DOI probes | No new DOI entity or adoption/conformance artifact | no |
| 09 | GitHub import/signature probes + official W3C/IETF/MCP controls | Adoption, standards and product-boundary lanes all unchanged | no |
| 10 | Bing cross-provider probes + official W3C/IETF/MCP controls | No new adopter/status/product boundary; low-precision results retained | no |

Cycles 07 and 08 were successful no-material cycles, but they did not both target the adoption and product-boundary lanes, so they were not used to satisfy the final stop. Cycles 09 and 10 are the two consecutive lane-complete no-material cycles after the last material change. OpenAlex/Semantic Scholar retries that returned HTTP 429 and DuckDuckGo HTTP 202 challenge responses were not counted toward saturation.

## Strict status map

| Artifact | Fixed state | Correct label | What it proves | What it does not prove |
|---|---|---|---|---|
| W3C AI Agent Memory Interoperability CG | created 2026-06-03; 17 API-listed users | Community Group | Open standards-discussion venue | W3C Recommendation, implementation or adoption |
| SAIHM | `draft-saihm-memory-protocol-01`; stream None; no RFC/std level | individual Internet-Draft | Published evolving proposal | IETF standard or endorsement |
| MCP Extensions | captured 2026-08-10 | official extensions: Authorization, Apps, Tasks | Adjacent protocol evolution | canonical agent-memory semantics |
| edihasaj UMP | v1.0.0 tag `5e5970d` | versioned project spec/release | Strict portable-record schema | ecosystem standard or external v1.0 conformance |
| PAM | arXiv:2605.11032; spec v1.0 Draft; SDK 0.1.0 | paper-backed project draft | Concrete protocol design and SDK | aligned stable release or SDO governance |
| Engram | SSRN `10.2139/ssrn.6878038`; spec `350a83b` | paper-backed project draft | Governance/portability proposal and checklist | executable or independent conformance |
| MGP | protocol/release v0.1.1; `54ce6c0` | project protocol + compliance suite | Rich contract and executable same-project checks | formal standard or independent implementation |
| Engramory | release v0.7.0; `9469d79` | experimental portable discipline | Host-oriented local memory portability | wire interoperability or production adoption |
| eMEM | release v2.1.0; inspected `f853955` | project protocol + operated service | Real engineering/spec/service assets | independent adopter or live-organisation guard use |
| OCF | v0.2 Draft; `19ccdb9` | project portable context format | Governed committed-state bundle and fixtures | memory-unit or transport standard |
| glatinone AMP | RFC-AMP-001 Draft/v0.1.0; `04ff1db` | project draft + implementation | Real schema/server/SDK/tests | RFC, SDO standard or independent adoption |

## Interoperability stack after breadth correction

### 1. Governance and standards formation

W3C CG and SAIHM remain early standards-formation artifacts. The W3C API's `spec-publisher=true` says the group may publish specifications; it does not transform every linked project into W3C work or make participant count adoption. IETF fields are even more explicit: no RFC, standards level or stream.

### 2. Adjacent transport and operation lifecycle

MCP continues to provide the shared host/client/server and tool/resource surface. Tasks adds durable asynchronous operation state. That is valuable for long-running memory maintenance jobs, but the durable `taskId` is a handle to an operation; it does not constrain the stored memory's record shape, provenance, update rules or deletion semantics.

### 3. Governed service contracts

MGP is the clearest new example. Its semantic spec is declared authoritative over schemas, OpenAPI, reference behavior and compliance. It names Core, Lifecycle, Interop and ExternalService profiles and supplies adapters. This is much more than a README concept. The evidence boundary is ownership: all normative and executable artifacts remain within HKUDS/MGP, and the exact external canonical-URL query returned zero indexed hits.

### 4. Portable local disciplines

Engramory standardizes a human-auditable file/rules practice across agent hosts. Its own documentation is unusually honest about experimental status, single-project/single-writer scope and missing store version/migration. The external Agent Team Kit is a genuine integration because its bootstrap performs a clone and installs Engramory rules. It still cannot show compatibility stability because it clones the moving default branch rather than a version.

### 5. Verifiable fact protocols

eMEM treats memory as signed content-addressed facts and provides substantial wire/test/deployment machinery. The project distinguishes a running responder from organizational adoption: its README says the guard has not yet been pointed at a live organisation. That disclosure is the correct evidence boundary. Registry listings and package availability prove distribution, not independent use.

PAM's provenance path has one independent partial uptake: Amore says it clean-room implemented the content-addressed observation envelope and `prev_hash` chain. That is meaningful design transfer, but a pattern is smaller than the full `.pam` contract.

### 6. Committed working-context governance

OCF intentionally sits above memory-unit formats and below message protocols. It serializes what the agent currently holds in force and why, including qualify/receipt trails. Its reference runner and valid/invalid cases are useful project conformance assets. Artesian's reader/writer is still same-organization evidence.

### 7. Record interchange and version drift

Agent Memory Hall demonstrates why “adapter exists” and “current protocol conformance” need separate columns. The adapter is real and tested, yet its output has `body` as a string and top-level `created`, while UMP 1.0 requires `ump:"1.0"`, `body:{text}`, and `time:{created}` with strict `additionalProperties:false`. The test named round-trip checks three selected fields inside one implementation. It is neither a normative validation nor a cross-organization loss report.

## Adoption evidence matrix

| Candidate | External evidence | Independence | Version pin | Conformance | Production evidence | Verdict |
|---|---|---:|---:|---:|---:|---|
| UMP via Agent Memory Hall | converter + tests + successful CI | different repository/owner | adapter pinned; semantic target is older 0.1 shape | no UMP 1.0 validation | none | qualified partial portability |
| PAM via Amore | clean-room provenance-chain pattern | different repository/owner | pinned commit/release | no full PAM validation | none | qualified pattern adoption |
| Engramory via Agent Team Kit | clone/install bootstrap | different repository/owner | **no** upstream ref pin | none | none | weak external integration |
| OCF via Artesian | reader/writer code | same organization | pinned | same-party fixtures | none | reference implementation only |
| eMEM external URLs | lists/mirrors/trackers in inspected top ten | external mentions | n/a | none | none | attention only |
| MGP exact external URL | zero indexed hits | n/a | n/a | none | none | bounded no-evidence |
| glatinone AMP exact external URL | zero indexed hits | n/a | n/a | none | none | bounded no-evidence |

No star, fork, package, registry, README customer claim or project-operated endpoint is used here to prove adoption.

## Name collisions that now require canonical IDs

- UMP: edihasaj portable-record interchange versus Devansh Verma probabilistic identity/context research.
- AMP / RFC-AMP-001: glatinone's v0.1.0 project draft versus MemoryHub's separate project proposal, in addition to the YouTale, Smriti and PMLR AMP artifacts already mapped.
- Engramory: tinqiao's file discipline versus `vladm3105/aidoc-flow-engramory`, a separate MCP/REST memory plane.

An acronym or document label is not an entity key. Owner, canonical URL, normative document and fixed version are mandatory.

## Bounded abstention

Across the exact requests in `SAT-STD-Q001..Q058`, this audit found two weak external signals—an AMH adapter for a UMP 0.1-shaped record and an unversioned Engramory installer—but did **not** verify:

- a current-version external conformant implementation of a promoted project spec;
- an independently attributable production deployment;
- a versioned independent conformance report;
- a two-party bidirectional round-trip with a field/invariant loss report;
- an independent MemTools reproduction.

This statement is limited to public opened sources and returned/indexed results through the cutoff. It says nothing about private deployments, unindexed code, renamed/vendored implementations or work published after the snapshot.

## What would materially change the next snapshot

1. A W3C CG deliverable with a fixed profile, test vectors or public implementation report.
2. An IETF status transition reflected in Datatracker—not a project announcement.
3. Two organization-independent implementations pinned to the same normative version.
4. A public conformance artifact that records tool version, fixture hash, implementation commit and pass/fail output.
5. A two-party import/export round trip reporting preserved, transformed and lost fields plus lifecycle invariants.
6. An independently attributable deployment or package dependency pinned to a release, with operator, configuration and date.

Until then, the accurate field-level conclusion is: **formal standardization remains early; project protocols are proliferating and becoming more executable; independent current-version conformance and production adoption remain the scarce evidence.**

## 饱和补查原子证据附录

以下句子是 bundle 中的原子 claim；每条紧接其稳定 marker。

The W3C AI Agent Memory Interoperability activity is a Community Group created on 2026-06-03, not a W3C Recommendation or other formal W3C standard.
<!-- claim:SAT-STD-C001 -->

The W3C API listed 17 group participants at the cutoff; that count is participation/attention evidence and cannot establish implementation or production adoption.
<!-- claim:SAT-STD-C002 -->

draft-saihm-memory-protocol-01 remained an individual Internet-Draft record with stream None, no RFC and no standards level; it must not be called an IETF standard.
<!-- claim:SAT-STD-C003 -->

At the captured cutoff, the official MCP extensions overview listed Authorization Extensions, MCP Apps and MCP Tasks and contained no memory extension listing.
<!-- claim:SAT-STD-C004 -->

MCP Tasks defines durable asynchronous operation handles, polling, reconnect and input-required lifecycle; this does not standardize persistent memory records, retrieval, consolidation or forgetting.
<!-- claim:SAT-STD-C005 -->

Agent Memory Hall contains a real bidirectional UMP/AMH converter with file import/export, three adapter tests and successful public CI at the pinned commit.
<!-- claim:SAT-STD-C006 -->

The Agent Memory Hall converter targets an older UMP 0.1-shaped record: it emits body as a string and omits the required ump and time objects, so it is not conformant to the pinned UMP 1.0 schema.
<!-- claim:SAT-STD-C007 -->

The AMH test called round-trip preserves only selected core fields within its own converter; it is not a schema-validation report, full-field loss analysis or two-party UMP round trip.
<!-- claim:SAT-STD-C008 -->

Portable Agent Memory is a paper-backed project protocol with a substantial draft spec and SDK, but the repository had no tag/release and exposed spec v1.0 Draft versus SDK 0.1.0; it is not an SDO standard.
<!-- claim:SAT-STD-C009 -->

Amore is independent evidence that a PAM provenance-chain idea was implemented: its NOTICE describes a clean-room content-addressed envelope/prev_hash implementation, but this is not full .pam wire-format or PAM conformance.
<!-- claim:SAT-STD-C010 -->

Engram is a paper-backed project draft whose pinned specification repository supplies a self-certification checklist but no executable conformance runner; self-certification cannot establish an independent conformant implementation.
<!-- claim:SAT-STD-C011 -->

Engram project claims about OpenClaw/Hermes writers were not corroborated by the recorded exact identifier searches, so this packet does not publish them as adoption facts.
<!-- claim:SAT-STD-C012 -->

The title Universal Memory Protocol also names a probabilistic identity/context research framework on Zenodo that is distinct from the edihasaj portable-record interchange specification.
<!-- claim:SAT-STD-C013 -->

HKUDS MGP v0.1.1 is a substantial project protocol with semantic specification, schemas, OpenAPI, reference gateway, adapters and an executable compliance suite; those same-project assets do not turn it into an SDO standard.
<!-- claim:SAT-STD-C014 -->

Engramory v0.7.0 is an explicitly experimental portable file-based memory discipline with several host adapters, not a cross-vendor wire standard; its own documentation limits it to single-project/single-writer use and lacks a store migration version.
<!-- claim:SAT-STD-C016 -->

An externally owned non-fork repository, syh5285126-ops/agent-team, really integrates tinqiao Engramory by cloning it and installing its rules/store, but the clone is unversioned and the repository supplies no conformance, CI or production-deployment report.
<!-- claim:SAT-STD-C017 -->

eMEM is a versioned project protocol with code, SDK/package and conformance assets plus a project-operated responder; project-owned deployment/registry claims are not independent adoption, and the README says its guard had not yet been pointed at a live organisation.
<!-- claim:SAT-STD-C018 -->

OCF v0.2 is a draft portable committed-working-context and governance bundle with schemas, vectors and a runner; its own scope explicitly says it is not a new wire protocol and does not define memory units.
<!-- claim:SAT-STD-C019 -->

Artesian is an inspectable OCF implementation, but it is maintained under aquifer-labs, the same organization as the OCF spec, so it is reference-implementation evidence rather than independent adoption.
<!-- claim:SAT-STD-C020 -->

glatinone's RFC-AMP-001 is a real v0.1.0 project draft with reference server, SDK, tests and successful same-project CI, but it is neither an RFC nor an independently adopted standard.
<!-- claim:SAT-STD-C021 -->

The label RFC-AMP-001 is itself ambiguous: the Red Hat AI Americas MemoryHub repository contains a distinct project proposal with the same label, not an implementation of glatinone AMP.
<!-- claim:SAT-STD-C022 -->

The 2026 project-spec layer is broader than a record/API list: it includes governed service contracts, portable local disciplines, verifiable content-addressed fact protocols and committed-working-context governance bundles.
<!-- claim:SAT-STD-C023 -->

Executable conformance assets are appearing inside project repositories, but this audit still found no current-version external conformant implementation, independent conformance report or two-party round-trip report for the promoted memory-specific project specs.
<!-- claim:SAT-STD-C024 -->

This audit did find two weaker external implementation signals—an AMH UMP 0.1-shaped adapter and an unversioned Engramory installer—so the correct conclusion is qualified partial integration, not zero external activity.
<!-- claim:SAT-STD-C025 -->

<!-- synthesis:STD-FU-S01 claims:SAT-STD-C001,SAT-STD-C002,SAT-STD-C003,SAT-STD-C004,SAT-STD-C005,SAT-STD-C006,SAT-STD-C007,SAT-STD-C008,SAT-STD-C009,SAT-STD-C010,SAT-STD-C011,SAT-STD-C012,SAT-STD-C013,SAT-STD-C014,SAT-STD-C016,SAT-STD-C017,SAT-STD-C018,SAT-STD-C019,SAT-STD-C020,SAT-STD-C021,SAT-STD-C022,SAT-STD-C023,SAT-STD-C024,SAT-STD-C025 clusters:MM-C11 -->
