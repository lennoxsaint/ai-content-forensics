# Phase 3: Visual Production

Create 9 production-ready carousel visuals — one per thread post. Each visual is generated in three formats: SVG (primary editable format), self-contained HTML/CSS (secondary), and PNG preview (if the environment supports rendering).

---

## Visual System

### Palette
- **Background**: `visual_background` from config (default `#f7f4ee`)
- **Text**: `visual_text` from config (default `#111111`)
- **Accent**: `visual_accent` from config (default `#8f1d1d`)
- **Neutral**: muted gray (`#7a7a7a`)

### Style
Minimalist editorial. Strong typographic hierarchy. Generous negative space. Clean grid. Subtle rules and dividers. No heavy drop shadows, no clutter, no random icons.

### Feel
Research dossier / creator memo / smart Figma export.

NOT: BI dashboard, sales deck, or generic infographic.

### Canvas
1080 x 1350px (mobile-first, optimized for carousel viewing on all platforms)

### Export Formats
For each asset, generate:
1. **SVG file** (primary editable format)
2. **Self-contained HTML/CSS file** (secondary — viewable in any browser)
3. **PNG preview** (if rendering is available in the environment)

For PNG rendering:
- In Claude Code: Try puppeteer, playwright, or similar headless browser tools if available
- In Cowork: Try available rendering tools or MCP tools
- If no rendering is available, log this in `fallback_log.md` and note that PNGs can be generated manually by opening the HTML files in a browser and screenshotting at 1080x1350

---

## Data Validation (Before Any Visual)

Before generating any visual:
1. Map every on-image number to its source file and exact location in the Phase 1 research
2. If thread text and corpus conflict, corpus wins — log the discrepancy and use the correct value
3. Do not guess or approximate missing values
4. Create a data validation log (`visuals/02_data_validation.md`) before asset generation

This step is non-negotiable. Every number on every slide must be traceable.

---

## Asset Archetypes

Match each insight to the best visual form. Do not repeat the same chart type across all slides — vary the visual form.

| Archetype | Best For |
|-----------|----------|
| **Scope Table / Dossier Cover** | Hook slide. Compact corpus audit (videos analyzed, transcripts, analyses, constitutions). |
| **Split-Stat Gap Card** | Large multiplier findings (e.g., 6.28x gap). Two big numbers with a visual bridge. |
| **Sorted Bar Chart** | Rankings, category performance, bucket comparisons. |
| **Grouped Bar Chart** | Top vs bottom comparisons across 2-4 categories. |
| **Dumbbell Comparison** | Shorter vs longer, before vs after, top vs bottom paired comparisons. |
| **Template / Formula Card** | Title patterns, hook structures. Must use EXACT corpus examples only. |
| **Matrix Card** | Conditional or segmented findings. |
| **Recap / Saveable Checklist** | Closer slide. Clean summary of all 7 insights. |

---

## Asset Requirements

### Asset 1 (Hook / Cover)
- Exact hook text from the thread
- Compact corpus audit table or badge set (videos, transcripts, analyses, constitutions)
- Research cover feel, not a meme

### Assets 2-8 (Insights)
- One visual per chosen insight, in exact thread order
- The main number or divergence must be the most visually dominant element on the slide
- If the insight involves a formula or pattern, include a template card with exact corpus examples
- If it involves top vs bottom divergence, make contrast instantly legible
- If it involves a ranking, sort cleanly and highlight the key finding

### Asset 9 (Recap / Closer)
- Clean summary of all 7 insights
- Actual research scope counts from the closer
- Saveable, not promotional

### On-Image Copy Rules
- Shorter than the full post text whenever possible
- Lead with the strongest number or ratio
- Lowercase except proper nouns
- No jargon, no long paragraphs
- Must make sense as a standalone screenshot
- Include tiny source/scope line if useful (e.g., "based on 87 videos analyzed")

---

## Typography Hierarchy

Use a clear type hierarchy across all 9 assets:

- **Hero number/stat**: Largest element on the slide. Bold weight.
- **Headline/claim**: Second largest. Sets context for the number.
- **Body text**: Supporting data sentences. Smaller, regular weight.
- **Label/caption**: Smallest. Used for axis labels, source notes, scope lines.

Stick to system fonts or widely available web fonts. Recommended: Inter, system-ui, or similar clean sans-serif.

---

## SVG Generation Guidelines

When generating SVGs:
- Set viewBox to "0 0 1080 1350"
- Use embedded text (not paths) so the text remains editable
- Apply the color palette from the visual system
- Use `<rect>`, `<line>`, `<text>`, and `<g>` elements for clean, maintainable markup
- For bar charts, calculate positions mathematically based on data values
- Test that the SVG is well-formed XML

## HTML Generation Guidelines

When generating HTML files:
- Make each file completely self-contained (inline CSS, no external dependencies)
- Set the canvas to 1080x1350px with the background color
- Use CSS Grid or Flexbox for layout
- Match the SVG output exactly in design
- Include a `<meta>` viewport tag for mobile preview

---

## Supporting Documentation

Create these files in the `visuals/` directory:

### `00_visual_system.md`
Document the full visual system: palette with hex codes, type hierarchy with sizes and weights, spacing rules, chart styling rules, and any design decisions made.

### `01_asset_manifest.md`
For each of the 9 assets:
- File paths (SVG, HTML, PNG)
- Data source (which Phase 1 file and which data point)
- On-image copy (exact text that appears on the visual)
- Archetype used

### `02_data_validation.md`
For each on-image number across all 9 assets:
- The number as displayed
- The source file path
- The exact location/context in the source file
- Confirmation of accuracy

---

## Quality Check

Before finalizing visuals, verify:
- Exactly 9 visual assets created
- Post order matches thread order exactly
- Hook text on Asset 1 is the exact hook from the thread
- Recap scope counts on Asset 9 are exact
- Every on-image number is traceable to source data
- Design system is consistent across all 9 assets (same palette, same fonts, same spacing)
- Main number is visually dominant on every insight slide
- No two slides use the exact same chart type (variety required)
