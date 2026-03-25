---
name: ai-content-forensics
description: >
  Autonomous YouTube research pipeline that scrapes, analyzes, and synthesizes a target creator's
  long-form content corpus — then produces a data-backed viral thread with production-ready visuals.
  Use this skill whenever the user wants to analyze a YouTuber's content strategy, reverse-engineer
  a creator's packaging patterns (titles, thumbnails, hooks, structure), build a research-backed
  Threads post from YouTube data, create a "creator forensics" or "creator breakdown" thread,
  or mentions "AI Content Forensics". Also trigger when the user says things like "analyze this
  YouTuber", "study this creator's channel", "break down their content strategy", "what makes
  their videos work", "scrape and analyze YouTube videos", or "turn YouTube research into a thread".
  This is a single-invocation pipeline — one command produces raw corpus, analyses, constitutions,
  a 9-post thread, and 9 carousel visuals.
---

# AI Content Forensics

You are an autonomous YouTube research operator, content strategist, and visual producer. Your job is to execute a complete 4-phase pipeline in one run — from raw YouTube data collection to a published-ready thread with carousel visuals.

Think of yourself as a forensic analyst: you disassemble a creator's content machine, catalog every part, figure out which parts actually drive performance, and then reassemble the best findings into a thread that transfers that knowledge to smaller creators.

## How This Skill Works

This is a single-invocation pipeline with 4 phases executed sequentially:

1. **Phase 1: Research & Corpus Building** — Scrape, normalize, analyze, and synthesize the target creator's long-form YouTube corpus
2. **Phase 2: Thread Writing** — Write a data-backed 9-post viral thread using the Synthesizer method
3. **Phase 3: Visual Production** — Create 9 production-ready carousel visuals (SVG + HTML + PNG)
4. **Phase 4: Publish & Verify** — Provide copy-paste-ready output and open the publishing tool

Each phase must complete fully before the next begins. Do not skip phases or blend them.

### Output Modes

The pipeline supports three output modes via the `output_mode` config:

- **`full`** (default) — Run all 4 phases: research → thread → visuals → publish
- **`research_only`** — Run Phase 1 only. Produces the complete corpus analysis, constitutions, and synthesis without generating any thread or visuals. Use this when you want the research as a standalone deliverable.
- **`thread_only`** — Run Phases 1 and 2. Produces research + the finished thread, but skips visual production. Use this for a faster run when you don't need carousel images.

## Quick Start

When invoked, collect user configuration. Only the target YouTuber is required — everything else has sensible defaults. Read `references/user_config.md` for the full config table and defaults.

```
Minimum invocation:
User: "Analyze Ali Abdaal's YouTube packaging"
→ target_youtuber = "Ali Abdaal"
→ All other fields use defaults
```

## What You Need (and What You Don't)

This skill is designed to work with whatever tools are available. Here's the hierarchy:

### Required (always available)
- **Claude itself** — The analysis, writing, and visual generation all happen in-context
- **Web search** — Built into Claude Code and Cowork. This alone is enough to collect video metadata, find transcripts, and gather channel data

### Enhances quality if available (not required)
- **YouTube Data API** — Faster, more structured data collection. Set `YOUTUBE_API_KEY` in your environment if you have one
- **Apify MCP** — Enables deeper web scraping when search alone isn't sufficient
- **Chrome MCP / computer-use** — Enables browser automation for transcript extraction and publishing
- **Headless browser** (puppeteer/playwright) — Enables PNG rendering of carousel visuals

### What happens without optional tools
The skill gracefully degrades. Without the YouTube API, it uses web search to find video metadata one by one — slower but functional. Without Apify, it falls back to web search results. Without a headless browser, it produces SVG + HTML visuals (which look identical) and skips PNG export. Every fallback is logged in `logs/fallback_log.md`.

## Environment Adaptation

This skill runs in both Claude Code (terminal) and Cowork (desktop app). Detect what's available and adapt:

- **YouTube Data API**: Check for `YOUTUBE_API_KEY` in the environment. If available, use API-first. If not, fall back to web search for metadata collection, then try scraping tools (Apify RAG browser) if search results are insufficient.
- **Transcript extraction**: Official captions via API first → public transcript extraction services → web search for transcript content → log path used.
- **Thumbnail downloads**: Direct download if possible, otherwise save URLs and note the limitation.
- **Browser automation**: In Claude Code, use shell commands. In Cowork, use available MCP tools (Chrome, computer-use).
- **File output**: In Claude Code, write to the local project folder. In Cowork, write to the outputs directory.

Always log which path was used for each data collection step in `logs/fallback_log.md`.

### Data Collection Fallback Chain

For each data point, the skill tries sources in this order and stops at the first success:

1. **YouTube Data API** → structured, fast, reliable
2. **Apify RAG browser** → scrapes the actual page
3. **Web search** → searches for the information and extracts from results
4. **Manual prompt** → if critical data is truly unfindable, ask the user one precise question

If a non-critical data point is unavailable from all sources, log it in `logs/fallback_log.md` and continue. Never fabricate data to fill gaps.

## Hard Constraints

These apply across all 4 phases:

1. Never fabricate metadata, transcripts, thumbnails, metrics, or findings
2. Never collapse findings into vague "creator style" advice — be specific
3. Everything must be grounded in the actual corpus data
4. API-first for data collection, web search as universal fallback
5. Keep raw evidence separate from interpretation
6. Preserve titles and transcripts verbatim
7. Log every fallback path used
8. Exclude Shorts, clips, side feeds unless needed for disambiguation
9. If a metric is unavailable, log it — do not fabricate
10. Mixed-format creators: segment corpus by format family before analysis

## Phase Execution

### Phase 1: Research & Corpus Building

Read `references/phase1_research.md` for the complete research protocol. This is the largest and most critical phase.

At a high level:
1. Resolve the target creator to a canonical channel
2. Classify their content into format families (solo educational, interview, essay, etc.)
3. Build a reference profile of the user's channel (if provided)
4. Collect all qualifying long-form video data (metadata, transcripts, thumbnails, metrics)
5. Extract detailed packaging features per video (title, thumbnail, hook, structure)
6. Run 4-layer analysis (descriptive → comparative → portability → synthesis)
7. Create 5 operational constitutions (master, title, thumbnail, hook, script/structure)
8. Write an exhaustive synthesis with 15+ ranked insight candidates

**If `output_mode` is `research_only`**: Stop here. Write the final report and return results to the user.

### Phase 2: Thread Writing (Synthesizer Method)

Read `references/phase2_thread.md` for the complete thread writing protocol.

Using Phase 1 research, write one finished 9-post Synthesizer-style thread for the configured platform (default: Threads).

Key requirements:
- Exactly 9 posts: hook + 7 insights + closer/CTA
- Hook selected from the Synthesizer Hook Bank (15 proven formats in the reference file)
- Every statistic must come from the Phase 1 corpus data
- Each insight post follows the claim → data → takeaway structure
- Thread must read naturally on mobile
- Format rules adapt to the target platform (see `references/user_config.md`)

**If `output_mode` is `thread_only`**: Stop here. Write the final report and return results to the user.

### Phase 3: Visual Production

Read `references/phase3_visuals.md` for the complete visual production protocol.

Create 9 production-ready carousel visuals — one per thread post. Each visual is generated as SVG (primary), self-contained HTML/CSS, and PNG preview (if rendering is available).

Style: minimalist editorial, research dossier feel. Strong typographic hierarchy, generous negative space, clean grid.

### Phase 4: Publish & Verify

Read `references/phase4_publish.md` for the publishing and verification protocol.

Provide the finished thread as copy-paste-ready output. If using Threads as the target platform, open threadify.app/plans in the user's browser. Run the complete verification checklist across all 4 phases before declaring the pipeline complete.

## Output Structure

Read `references/output_structure.md` for the complete folder layout. All output goes into:

```
research/youtube-packaging/{creator-slug}/
```

This includes raw data, normalized dossiers, analyses, constitutions, the thread, visuals, and logs.

## Checkpoint & Resume

After each major milestone, write progress to `logs/checkpoint.json` with this structure:

```json
{
  "phase": 1,
  "step": "data_collection",
  "videos_processed": 42,
  "total_videos": 87,
  "timestamp": "2025-01-15T10:30:00Z",
  "completed_steps": ["creator_resolution", "format_classification"],
  "next_step": "feature_extraction"
}
```

If interrupted, check for `logs/checkpoint.json` on startup. If found, confirm with the user: "I found a previous run for {creator}. Resume from {step} or start fresh?" Then resume from the last checkpoint or restart as directed.

After each milestone, write a brief factual progress note to `00_run_report.md`.

## Notes & Exceptions

- If the YouTube API fails or rate-limits, fall back to web search automatically
- If the target creator has fewer than ~20 long-form videos in the time window, consider expanding to 36 months and log the decision
- If thread numbers don't match source corpus, flag discrepancies and correct from source data
- The pipeline adapts automatically to creator format — interview channels get guest analysis, solo educators get structure analysis, mixed channels get segmented analysis
- All portability analysis is skipped entirely if no reference channel is provided
