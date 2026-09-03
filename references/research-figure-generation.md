# Research Figure Generation

Use generated figures only when they make an architecture, mechanism, state transition, or feedback loop materially easier to understand. A generated raster is a reader-facing explanation layer, not an evidence source and never the only carrier of a technical conclusion.

This workflow adapts the source-first figure-contract ideas from [`paper-framework-figure-studio-pro` v3.2.15f](https://github.com/c-narcissus/paper-framework-figure-studio-pro/tree/77557418b4ca8c24fa8961206bf9b8f7f6d030e1) to Track Tech Frontier. It intentionally omits that project's fixed candidate counts, heavy checkpoint machinery, raster-only rule, and terminal human-only boundary.

## Choose the right visual route

- Use Mermaid/SVG, a table, or ordinary HTML/CSS when exact labels, quantities, topology, or accessible relationships are the primary value.
- Use image generation for a visual architecture overview, mechanism cutaway, system map, conceptual pipeline, or learning loop where composition and visual analogy improve first-glance understanding.
- Use both when useful: the generated figure supplies the visual overview, while nearby prose or a code-native diagram preserves exact relationships.
- Skip the figure when it would only decorate a page or repeat an already clear paragraph, table, or diagram.

Do not use generated images for benchmark plots, exact numeric charts, source-code listings, dense equations, or diagrams whose correctness depends on many tiny labels.

## Hard user-alignment gate

Before calling `imagegen` for any new research figure, present a text-only visual alignment sheet and wait for explicit user approval. Do not generate a draft merely to make the discussion concrete. Silence, partial feedback, “roughly”, or approval of the topic is not approval of the visual plan.

The alignment sheet must show:

- the single visual thesis;
- the actual geometry and spatial hierarchy, including a small ASCII wireframe when shape matters;
- the relative area or visual weight of every major region;
- the information carried by each region;
- a hard symbol/icon budget per region and why each symbol is necessary;
- every connector, its direction, endpoints, and semantic meaning;
- the exact visible-text whitelist;
- palette and surface style;
- explicit forbidden structures, symbols, and decorative elements.

Ask the user to correct or explicitly confirm this sheet. Record the confirmed result in `figure-spec.json` under:

```json
{
  "alignment": {
    "status": "approved",
    "confirmed_by": "user",
    "approved_summary": "...",
    "geometry": "...",
    "information_density": "...",
    "symbol_budget": "...",
    "connector_plan": "...",
    "visible_text_plan": "..."
  }
}
```

`scripts/compile_figure_prompt.py` must reject any specification without this explicit approval record. A user rejection resets the status to `rejected` or `pending`, blocks further image generation, and disqualifies the rejected raster as a positive reference unless the user later says otherwise.

## Keep a small figure inventory

Before generating anything, list the proposed figures and keep only the high-value set. For each figure record:

- target page and intended placement;
- the one reader question it answers;
- why prose, a table, or the existing diagram is insufficient;
- whether it is an overview, architecture, mechanism, state, retrieval, or feedback figure;
- which exact source files and sections constrain it.

Do not impose one image per page. A compact reader suite often needs one visual anchor plus a few mechanism figures.

## Compile a semantic contract

Create a machine-readable specification before writing the image prompt. Store it under `<suite>/work/figures/<figure-id>/figure-spec.json` when the figure will be retained. The specification must separate internal node/edge IDs from visible labels, list evidence for every required entity and direction, and explicitly list forbidden edges.

Compile and validate it before image generation:

```text
python <skill-dir>/scripts/compile_figure_prompt.py \
  --spec <suite>/work/figures/<figure-id>/figure-spec.json \
  --output <suite>/work/figures/<figure-id>/prompt.md
```

Use `--check` when only validation is needed. A required edge that also appears in `forbidden_edges`, an unknown endpoint, duplicate relation, or visible label missing from the whitelist is a hard failure. Do not hand-write around a failed contract.

The specification should contain the equivalent of:

```text
figure_id:
target_page:
reader_question:
source_anchors:
required_entities:
required_relationships:
relationship_directions:
feedback_or_version_loops:
visible_text_whitelist:
caption_only_information:
forbidden_entities_or_edges:
known_ambiguities:
```

Every required entity and connector must follow from the reader source or a recorded, conservative inference. Do not add an arrow because it creates a smoother-looking pipeline. Distinguish data flow, control flow, temporal succession, dependency, feedback, and comparison; do not let one line style silently represent several meanings.

Keep transferred values, versions, weights, thresholds, or states on connectors, ports, compact tags, or the caption when possible. Do not promote every artifact into a peer module box. If repeated actors share one process, prefer compact actor markers over duplicated full pipelines.

## Compile a visual contract

Write the accepted generation prompt to `<suite>/work/figures/<figure-id>/prompt.md`. Specify:

- canvas and aspect ratio;
- one primary reading direction and 3–6 visual anchors;
- dominant mechanism region and subordinate context regions;
- module hierarchy, connector families, and any callout boundary;
- a short visible-text whitelist, ideally labels of 2–5 words;
- palette semantics that match the destination site;
- information intentionally delegated to the caption or surrounding prose;
- negative constraints covering unsupported text, edges, visual effects, and layout failures.

For Chinese figures, minimize embedded prose. Prefer numbered anchors, short Chinese labels, icons, and a nearby HTML legend. Do not embed a large title when the page already supplies one.

Avoid generic AI aesthetics: blue-purple gradients without meaning, neon glow, glass panels, glossy spheres, decorative photos, floating fragments, excessive shadows, and rainbow color assignment. Require restrained contrast, grayscale-readable structure, and color redundancy through shape or line style.

Before fixing the visual contract, inspect only the relevant local atlas boards under `assets/figure-studio/`:

- `framework-figure-subtypes.png` to choose the figure's reader job;
- `visual-grammar-layout.png` to choose one dominant layout grammar;
- `visual-communication-styles.png` to choose the rendering surface.

Use the boards as design vocabulary, not as technical evidence. Select a named lens and record why it serves the reader question; do not mix several panels merely to look novel.

## Generate and converge

When the runtime provides the `imagegen` skill/tool, use it for generated raster figures and follow its image-generation instructions. If it is unavailable, preserve the approved brief and report the missing capability; do not disguise a programmatic renderer as an AI-generated illustration.

- Generate high-impact or style-defining figures as separate candidates, normally two substantially different compositions.
- Keep one candidate per image-generation call so its prompt and artifact remain unambiguous.
- Use stable IDs such as `C01`, `C02`, and `F01`; do not infer identity from display order.
- Use a selected candidate as a reference for refinement when the image route supports reference images.
- Keep rejected candidates in the suite's ignored `tmp/` area unless the user explicitly wants them retained.

Do not run a fixed candidate quota when a single bounded revision is enough. Stop expanding candidates once a direction clearly satisfies the semantic and visual contracts.

## Review the actual raster

Inspect every candidate with an image viewer. Review visible output, not only its prompt.

Check:

- missing, invented, reversed, or falsely relayed relationships;
- broken Chinese, symbols, numbers, filenames, or equations;
- core mechanisms replaced by empty boxes, bullets, or decorative icons;
- repeated workflow lanes, ambiguous line styles, and unanchored arrows;
- excessive density, empty regions, weak reading order, or a subordinate inset dominating the figure;
- contrast, small-screen legibility, dark-theme fit, and print behavior;
- whether the caption would have to repair a misleading image.

Reject a visually attractive candidate when its semantics are wrong. If text or connector fidelity still fails after bounded revisions, fall back to a code-native diagram or a text-sparse illustration with an exact HTML legend.

## Publish without making HTML authoritative

Place the accepted asset at `<suite>/reader/assets/figures/<figure-id>.<png|webp|avif>` and reference it from the authoritative Markdown. Use concise alt text that states the figure's purpose, plus a nearby caption that explains its boundaries and any non-obvious line/color semantics.

Keep the precise technical explanation in prose, tables, or an accessible code-native diagram. Never make hover state, color alone, or generated microtext the only place where a conclusion appears.

Rebuild the static site through `scripts/render_reader_html.py`; do not hand-edit generated HTML. Verify the accepted figure at desktop and mobile widths, in light and dark themes, and in print. Confirm that the build manifest includes the copied asset and that local link validation still passes.

## Example request

```text
Use $track-tech-frontier to add a source-grounded Agent Memory architecture figure to the reader suite. Read the overview and six layer chapters, propose only the high-value figure inventory, generate two candidates for the style-defining overview figure, inspect their visible semantics, then integrate the accepted raster through Markdown and rebuild the validated HTML site.
```

## Provenance boundary

This repository borrows workflow ideas, not upstream code or visual assets. The inspected upstream package declares MIT No Attribution, but no upstream files are required at runtime here. If future work vendors an upstream script, template, icon, or sample, record its exact commit, license, and modifications separately before committing it.
