# Reader HTML Presentation Contract

Generate HTML only after the Markdown reader suite is complete. HTML is a derived understanding and distribution layer; it never becomes a second authority for technical conclusions.

## Default build

```text
python <skill-dir>/scripts/render_reader_html.py --root <suite-dir> --output <suite-dir>/site
python <skill-dir>/scripts/render_reader_html.py --root <suite-dir> --output <suite-dir>/site --check
```

The output is a static multi-page site whose default entry is `site/index.html`. It must work from a normal static server and remain readable when opened from local files. Shared CSS, JavaScript, and the search index live under `site/assets/`; `build-manifest.json` records UTF-8 byte hashes without embedding an absolute local source path.

## Reader jobs

The presentation must help a technically literate newcomer do four jobs:

1. **Orient:** see the field question, reading routes, mechanism map, and current/uncertain boundaries before browsing files.
2. **Locate:** move across the suite, within one page, or directly from a search result to a section.
3. **Reconstruct:** follow state/data flow, compare solution families, and inspect code or diagrams without losing the prose argument.
4. **Verify:** reach nearby sources, project versions, limitations, and audit material without internal process IDs dominating the narrative.

Use landing cards only for orientation, prose for causal explanation, tables for repeated exact comparisons, diagrams for relationships, and details for supplementary material. Do not turn every paragraph into a card or every report into a dashboard.

## Supported source contract

The standard-library renderer supports the subset currently used by the repository's reader suites:

- one H1 plus nested headings;
- paragraphs, emphasis, inline code, links, images, blockquotes, ordered/unordered lists, and horizontal rules;
- GFM-style pipe tables;
- fenced or four-space-indented `text`, `json`, and other code blocks;
- the observed Mermaid `flowchart` subset: directions, ordinary nodes, chained/compound edges, dotted labeled edges, and simple subgraphs.

This is not a claim of full CommonMark, GFM, or Mermaid compatibility. An unsupported construct must remain visible as escaped source or a readable fallback and create a build warning. Never guess a diagram that the parser cannot reconstruct.

## Security and integrity

- Escape raw HTML from Markdown. Do not execute script, event-handler, iframe, or style input.
- Allow only `http`, `https`, `mailto`, page anchors, and resolved relative links.
- Resolve Markdown links against source files before rewriting them to output HTML.
- Copy only passive, allowlisted assets into `site/assets/source/`; never let source-linked files overwrite pages or renderer assets. Local paths outside the suite root become explicit non-clickable “source workspace” references and are counted in the manifest, so a standalone site never contains links that escape its root.
- Fail the build on broken generated local links, invalid UTF-8, replacement characters, missing entry pages, output collisions, or dangerous generated URL schemes.
- Keep search result rendering escaped even though the search index was generated locally.
- Do not infer evidence relations, confidence, or freshness in the presentation layer.

## Diagram contract

Every rendered technical diagram keeps three representations:

1. accessible SVG for the visual relationship;
2. a text list of objects and connections for search, screen readers, and checking;
3. the original Mermaid source for editing and fallback.

Long diagrams may scroll horizontally at a readable node size. Do not shrink an entire long chain until labels become unreadable. Clicking or focusing a node may reveal a short explanation, but no unique conclusion may exist only in that interaction.

## Browser acceptance

Inspect at least:

- the default entry and reading-path cards;
- one long mechanism report with several heading levels;
- one wide comparison table;
- every Mermaid shape family present in the suite;
- a project report and nearby external/source links;
- full-suite search using Chinese and an original project name;
- desktop around 1440×900, mobile around 390×844, dark mode, keyboard focus, reduced-motion behavior, and print structure.

Use at least four visible iterations for a new presentation system: structure, hierarchy, comprehension interactions, then resilience/polish. Fix the issues found in each pass before moving to the next. A green link checker cannot replace browser reading.

## Output boundaries

- Do not add a service, database, analytics, remote fonts, or CDN dependency to the default output.
- Do not rewrite or summarize source prose during rendering.
- Do not hand-edit generated HTML; change the source Markdown, renderer, or shared assets and rebuild.
- Rebuild through a validated staging directory and replace only an output carrying this renderer's manifest. `--check` must compare source/output hashes and file sets so deleted Markdown cannot leave stale published HTML.
- Keep audit navigation available but visually subordinate to the default reader path.
