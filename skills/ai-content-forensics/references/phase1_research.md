# Phase 1: Research & Corpus Building

This is the largest and most critical phase. Everything downstream depends on the quality of this research. Think of it like building a case file — you need airtight evidence before you can draw conclusions.

## Adaptation Principle

Adapt to the actual target creator. Do not force interview analysis onto a solo educator, or vice versa. Do not blend unlike formats into one fake law set. Classify first, segment if needed, then extract.

## Rules

1. API first, web search second, scrape third
2. Never guess ambiguous data — verify or ask one precise question
3. Keep raw evidence separate from interpretation
4. Preserve titles and transcripts verbatim
5. Save thumbnails as files
6. Log every fallback path used
7. Every constitution rule must trace to corpus evidence
8. Exclude Shorts, clips, side feeds unless needed for disambiguation
9. Mixed-format creators: segment corpus by format family before analysis
10. If a metric is unavailable, log it — do not fabricate

---

## Step 1: Creator Resolution

Resolve `target_youtuber` to a canonical channel.

The input may be a name, handle, URL, or ambiguous string. Resolve to: canonical channel name, channel ID, main vs side feeds, format patterns.

Verify using channel page, metadata, upload behavior — not just search titles. If ambiguous, ask one precise question and wait.

## Step 2: Format Classification

Classify the creator's content into format families before extraction:

- Solo educational / tutorial
- Founder / build-in-public
- Interview / podcast
- Essay / commentary
- Documentary / explainer
- Mixed (segment corpus by family)

Create better families if the evidence demands it. The point is to avoid analyzing interview-style content with solo-educator patterns. Each family may have different packaging rules.

## Step 3: Reference Profile (Optional)

**Only if `your_channel_handle` is provided:**

Inspect the user's YouTube channel and build a reference profile covering: positioning, content pillars, formats, audience, packaging patterns, weaknesses. This becomes the portability filter for all findings.

If `your_channel_handle` is empty, skip entirely and proceed to data collection.

## Step 4: Data Collection

### Environment Check

First, check the local environment for: API credentials (`YOUTUBE_API_KEY`), extraction scripts, transcript tools, prior research from previous runs (check for existing `logs/checkpoint.json`).

### Data Collection Fallback Chain

For every data point, try these sources in order and stop at the first success:

1. **YouTube Data API** (if `YOUTUBE_API_KEY` available):
   - Channel resolution, uploads pagination
   - Per-video: ID, title, publish date, duration, thumbnail URL, description, metrics (views, likes, comments)
   - Chapter/timestamp text from descriptions

2. **Web search** (always available — this is the universal fallback):
   - Search for "{creator name} YouTube channel" to find channel metadata
   - Search for individual video titles + "YouTube" to find metadata
   - Search for "{video title} transcript" to find transcript text
   - Use web search results to extract view counts, publish dates, and other metrics from search snippets

3. **Web scraping tools** (if Apify or similar available):
   - Use Apify RAG web browser to scrape channel pages
   - Use public transcript extraction services

4. **Transcripts**: Official captions via API first → public extraction tools → web search for "{video title} transcript" → log path used.

5. **Thumbnails**: Direct download if possible, otherwise save URLs.

Log every fallback path used in `logs/fallback_log.md` with the format:
```
| Data Point | Primary Source | Fallback Used | Reason |
```

### Long-Form Definition

- Include full-length main-channel uploads
- Exclude Shorts, clips, highlights, micro-edits, repost fragments
- Use duration as primary signal (typically >5 minutes), metadata as supporting signal
- Borderline videos go in `exclusions_log.md` with reasoning

### Time Window

Apply the `time_window_months` filter (default: 24 months). Only include videos published within this window.

If the creator has fewer than ~20 qualifying videos, consider expanding to 36 months. Log this decision in `00_run_report.md`.

### Per-Video Data Points

For each qualifying video, collect:

**Raw data:**
- URL, video ID, publish date, title, duration
- Thumbnail file path + URL
- Transcript file path + full text
- Views, likes, comments count (where available)
- Description, chapter timestamps
- Host/guest/collaborator info if relevant

**Derived metrics:**
- Age in days, views per day
- Like-to-view ratio
- Title: character count, word count, structure features
- Thumbnail: text presence, composition notes
- Opening/hook pattern, time to title payoff
- Structure notes, chapter structure

---

## Step 5: Feature Extraction

For every qualifying video, extract detailed packaging features across these categories:

### Title Features
- Exact title text
- Character count, word count
- Leading token pattern (number, question, how-to, name, statement, etc.)
- Uses: numbers, contrast, quoted claim, implied promise
- Trigger categories: pain, curiosity, speed, status, money, health, identity, certainty, fear, transformation
- Title archetype (template pattern)
- Claim specificity: vague / moderate / exact

### Thumbnail Features
- Local file path
- Face present (yes/no), face count, emotion level (high/med/low)
- Text on image (transcribe if present)
- Contrast level, color intensity, background simplicity
- Focal point clarity
- Screenshot/UI/diagram usage
- Visual metaphor usage
- Thumbnail archetype

### Hook Features
- Exact opening lines (first 3-5 sentences from transcript)
- First 15-second and 30-second summary
- Time to first high-stakes statement
- Time to first concrete promise or payoff
- Whether opening validates title/thumbnail promise quickly
- Hook archetype
- Title-thumbnail-hook alignment assessment

### Structure Features
- High-level section map
- Intro structure (story-led, proof-led, direct, question-led)
- Who speaks first (for multi-speaker content)
- Story precedes teaching? Proof precedes teaching?
- Pacing notes, topic transition patterns
- Emotional turn points
- Practical takeaway density (high/med/low)
- CTA placement (early/mid/late/end), CTA style
- Ending structure

### Conditional Modules

Enable per format family:

**Interview/podcast module:**
- Guest name, category, fame/authority signals
- How much packaging depends on guest reputation
- Cold open type (guest clip, host monologue, stats, etc.)
- When guest authority is established in the video
- Question sequencing logic, tension escalation
- Thumbnail: host face, guest face, or both dominant

**Solo education module:**
- Title framing: problem, promise, blueprint, myth-bust, teardown, case study
- Opening: proof, result, tension, mistake, objection, outcome
- Examples arrive before theory?
- Structure: step-by-step, framework, teardown, story-led, comparative
- Thumbnail: tool UI, before/after, result framing, creator face

**Founder/build-in-public module:**
- Title: stakes, numbers, runway, revenue, failure, experiment
- Opening: tension, scoreboard, decision point, setback, reveal
- Narrative vs tactical lesson alternation
- Thumbnail: numbers, stakes, dashboards, personal reaction

---

## Step 6: Analysis (4 Layers)

### Layer 1 — Descriptive
What patterns repeat in titles, thumbnails, hooks, structures? If multiple format families exist, what differs by family?

### Layer 2 — Comparative
Compare top-performing vs bottom-performing videos using available metrics. Normalize by age where possible. Identify patterns disproportionately present in top performers. State correlation, not causality.

### Layer 3 — Portability (ONLY if `your_channel_handle` provided)

For each discovered pattern, score:
- `evidence_strength` (strong/moderate/weak)
- `prevalence_in_corpus` (percentage of videos)
- `effect_size_if_measurable`
- `portability_to_user_channel` (high/medium/low)
- `dependence_on`: guest fame, creator brand equity, production scale, timing/news cycle
- `risk_of_false_transfer`
- `recommendation`: adopt / test / ignore

Create three buckets:
- **A. Portable now** for user's channel
- **B. Conditional** — worth testing
- **C. Creator-specific artifacts** — do not blindly copy

If no reference channel provided, skip Layer 3 entirely.

### Layer 4 — Synthesis
Convert strongest findings into operational constitutions. Prefer actionable rules over vague commentary.

---

## Step 7: Constitutions

Create 5 constitutions, each containing:

1. **Master packaging constitution** — overview + cross-cutting rules
2. **Title constitution**
3. **Thumbnail constitution**
4. **Hook / opening constitution**
5. **Script and structure constitution**

Each constitution must include:
- **Purpose**: what it governs
- **Non-negotiable rules**: hard rules with strong evidence
- **Strong patterns**: common but not universal
- **Conditional rules**: when to use which pattern
- **Anti-patterns**: what to avoid
- **Evidence base**: reference actual videos and data behind each rule
- **Portability notes** (only if reference channel provided)
- **Confidence labels**: mark each rule high / medium / low confidence

Write these as operational law, not fluffy commentary. Another creator or agent should be able to follow them mechanically.

---

## Step 8: Exhaustive Synthesis

Create a comprehensive synthesis document covering:

1. Corpus scope and method
2. Target creator profile and classification
3. Reference channel profile (if provided)
4. Format-family breakdown (if applicable)
5. Strongest title laws
6. Strongest thumbnail laws
7. Strongest hook / opening laws
8. Strongest script / structure laws
9. Top vs bottom performer comparisons with effect sizes
10. Portable laws (if reference channel provided)
11. Contradictions and outliers
12. Recommended experiments
13. **RANKED LIST**: minimum 15 screenshot-worthy insight candidates, scored by:
    - Surprise
    - Specificity
    - Actionability
    - Shareability

Clearly separate: raw evidence → interpreted patterns → portable laws → creator-specific artifacts.

This ranked insight list is the direct input for Phase 2 thread writing.
