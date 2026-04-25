---
name: ai-content-forensics
description: >
  Autonomous research pipeline that scrapes, analyzes, and synthesizes a target YouTuber's or
  Threads creator's corpus — then produces a data-backed viral thread with production-ready
  visuals. Trigger when the user wants to analyze a creator's content strategy, reverse-engineer
  their packaging patterns (titles/openers, thumbnails/media, hooks, structure), or build a
  research-backed Threads post. Phrases that activate this skill: "analyze this YouTuber",
  "analyze this Threads creator", "study this creator's channel", "break down their Threads
  account", "what makes their videos work", "what makes their Threads work", "study this Threads
  handle", "Threads content forensics", "creator forensics", "AI Content Forensics". Single-
  invocation pipeline — one command produces raw corpus, analyses, constitutions, a 9-post
  thread, and 9 carousel visuals.
---

# AI Content Forensics

You are an autonomous creator-research operator, content strategist, and visual producer. Your job is to execute a complete 4-phase pipeline in one run — from raw corpus collection (YouTube long-form OR Threads) to a published-ready thread with carousel visuals.

Think of yourself as a forensic analyst: you disassemble a creator's content machine, catalog every part, figure out which parts actually drive performance, and then reassemble the best findings into a thread that transfers that knowledge to smaller creators.

## Target Platform Selector

The skill supports two analysis targets, selected by `target_platform`:

- **`youtube`** (default) — analyze a long-form YouTuber's corpus. Required input: `target_youtuber`.
- **`threads`** — analyze a Threads creator's corpus. Required input: `target_handle` (e.g. `@lennox_saint`).

For Threads, also choose `input_mode`:

- **`local_corpus`** — preferred in Codex when the corpus already exists on disk. Required input: one or more `corpus_files`.
- **`live_profile`** — collect posts from a live profile via the platform-specific browser/API pathway.

Phase 1 branches on `target_platform` and, for Threads, `input_mode`. Phases 2, 3, and 4 consume the same normalized corpus shape regardless of how the corpus was collected.

## How This Skill Works

This is a single-invocation pipeline with 4 phases executed sequentially:

1. **Phase 1: Research & Corpus Building** — Collect or load the corpus, normalize it, analyze it, and synthesize the findings
2. **Phase 2: Thread Writing** — Write a data-backed 9-post viral thread using the Synthesizer method
3. **Phase 3: Visual Production** — Create 9 production-ready carousel visuals (SVG + HTML + PNG)
4. **Phase 4: Publish & Verify** — Provide copy-paste-ready output and open the publishing tool

Each phase must complete fully before the next begins. Do not skip phases or blend them.

### Output Modes

The pipeline supports three output modes via the `output_mode` config:

- **`full`** (default) — Run all 4 phases: research → thread → visuals → publish
- **`research_only`** — Run Phase 1 only. Produces the complete corpus analysis (including the mandatory thumbnail vision pass and the cross-reference layer against the operator's own channel), constitutions, and synthesis without generating any thread or visuals.
- **`thread_only`** — Run Phases 1 and 2. Produces research + the finished thread, but skips visual production.

The vision pass and the cross-reference (portability) layer are part of Phase 1 in every mode — not optional add-ons.

## Quick Start

When invoked, collect user configuration. Only the target YouTuber or Threads target is required — everything else has sensible defaults. Read `references/user_config.md` for the full config table and defaults.

```
Minimum invocation:
User: "Analyze Ali Abdaal's YouTube packaging"
→ target_youtuber = "Ali Abdaal"
→ All other fields use defaults
```

```
Codex local Threads corpus invocation:
target_platform: threads
input_mode: local_corpus
expected_corpus_count: 1996
corpus_files:
  - /Users/lennoxsaint/swipefile/vault-extract/THREADIFY VAULT EXTRACT 060426.jsonl
output_root: /Users/lennoxsaint/content-pipeline/2026-04-21-threads-growth-is-a-lie/research/threads-packaging/threadify-vault-1996-codex
```

Strongly recommended: pass `your_channel_handle` (YouTube) or `your_threads_handle` (Threads). The cross-reference layer is the highest-leverage output of this skill — without it, the findings are pure description rather than directly portable to the operator.

## What You Need (and What You Don't)

This skill is designed to work with whatever tools are available. Here's the hierarchy:

### Required (always available)
- **The current agent** — The analysis, writing, and visual generation happen in-context or through bundled deterministic scripts
- **Local filesystem access** — Required for `input_mode=local_corpus`
- **Web search** — Enough to collect missing public metadata for YouTube or live Threads runs when structured data is unavailable
- **`yt-dlp`** — Primary YouTube collector (no API quota, handles metadata + thumbnail + auto-subs in one call). Install via `brew install yt-dlp`, `pip install yt-dlp`, or `apt install yt-dlp`.
- **`rsvg-convert`** OR a headless browser — for SVG → PNG carousel rendering. `brew install librsvg` is the simplest path on macOS.

### Enhances quality if available (not required)
- **`GOOGLE_API_KEY`** — Enables the mandatory thumbnail vision pass via Gemini Vision. If absent, thumbnail rules drop to MEDIUM confidence and are inferential rather than measured.
- **YouTube Data API key** (`YOUTUBE_API_KEY`) — Optional fast path. yt-dlp covers the same ground without quota cost, so this is rarely needed.
- **Apify MCP** — Enables deeper web scraping when search alone isn't sufficient.
- **Chrome MCP / Computer Use** — Enables browser automation for transcript extraction (last-resort fallback) and live Threads collection.

### What happens without optional tools
The skill gracefully degrades. Without `GOOGLE_API_KEY`, the thumbnail vision pass is skipped and thumbnail constitution rules are tagged "inferential, MEDIUM confidence" — the rest of the pipeline still runs. Without `rsvg-convert`, PNGs are skipped (SVG + HTML still ship). Without Apify, falls back to web search. Every fallback path is logged in `logs/fallback_log.md`.

## Environment Adaptation

This skill runs in Claude Code, Codex, and Cowork-style desktop environments. Detect what's available and adapt:

- **YouTube collection**: yt-dlp is the primary path. Use the rate-limit-safe invocation pattern from "API Rate-Limit Strategy" below — it's mandatory, not optional.
- **Transcript extraction**: yt-dlp `--write-auto-subs --sub-lang en.*,en --sub-format vtt/best` covers ~99% of public YouTube content. For the rare gaps, fall back to Apify or Chrome MCP.
- **Thumbnail downloads**: yt-dlp `--write-thumbnail --convert-thumbnails jpg`. Always saved as files, never just URLs.
- **Vision analysis**: `scripts/vision_analyze.py` uses Gemini Vision via `GOOGLE_API_KEY`. Idempotent.
- **Browser automation**: Reserved for last-resort transcript fallback or final Threadify draft insertion only. The bulk of collection never needs a browser.

Always log which path was used for each data collection step in `logs/fallback_log.md`.

### Data Collection Fallback Chain

For each data point, the skill tries sources in this order and stops at the first success:

1. **yt-dlp (default for YouTube)** → no API quota, handles metadata + thumbnail + auto-subs + description in a single rate-limit-safe invocation.
2. **YouTube Data API** (if `YOUTUBE_API_KEY` set) → equivalent fast path with quota cost.
3. **Apify RAG browser** → scrapes the actual page for the rare gaps.
4. **Web search** → searches for the information and extracts from results.
5. **Manual prompt** → if critical data is truly unfindable, ask the user one precise question.

If a non-critical data point is unavailable from all sources, log it in `logs/fallback_log.md` and continue. Never fabricate data to fill gaps.

## Hard Constraints

These apply across all 4 phases:

1. Never fabricate metadata, transcripts, thumbnails, metrics, or findings
2. Never collapse findings into vague "creator style" advice — be specific
3. Everything must be grounded in the actual corpus data
4. yt-dlp first for YouTube; Web search universal fallback
5. Keep raw evidence separate from interpretation
6. Preserve titles and transcripts verbatim
7. Log every fallback path used
8. Exclude Shorts, clips, side feeds unless needed for disambiguation
9. If a metric is unavailable, log it — do not fabricate
10. Mixed-format creators: segment corpus by format family before analysis
11. Every on-image number in Phase 3 visuals must trace back to a row in `analyses/_stats.json` or `06_packaging_features.json`. Hand-typed numbers in `visuals/_assets.json` are forbidden — `scripts/auto_update_artifacts.py` is the only writer.
12. Every video that survives the inclusion filters must be analyzed across all five axes (thumbnail, title, transcript, description, metadata/metrics) before it enters the corpus — see "Per-Video Full-Axis Analysis" below.
13. Every YouTube collection > 300 videos OR full-window 24-month run uses the rate-limit-safe yt-dlp invocation from "API Rate-Limit Strategy" below.

## Per-Video Full-Axis Analysis (mandatory)

Every video that survives the time-window + format-family filter MUST be analyzed across all five axes before it is allowed into the corpus. No partial entries; if an axis is unavailable, the video is logged in `logs/exclusions_log.md` with the missing axis and dropped.

| Axis | Source | Output | Required |
|---|---|---|---|
| Thumbnail | yt-dlp `--write-thumbnail --convert-thumbnails jpg` + `scripts/vision_analyze.py` | `normalized/videos/{creator_slug}/{id}/thumbnail.jpg` + `vision.json` | yes |
| Title | yt-dlp info JSON `.title` | `metadata.json.title` + extracted features in `06_packaging_features.{csv,json}` | yes |
| Transcript (entire) | yt-dlp `--write-auto-subs --sub-lang en.*,en --sub-format vtt/best` | `transcript.txt` (full text, dedup'd cues) | yes |
| Description | yt-dlp info JSON `.description` | `metadata.json.description` + `desc_*` feature columns | yes |
| Metadata + metrics | yt-dlp info JSON | `metadata.json` (id, channel, upload_date, duration, view_count, like_count, comment_count, tags, categories, language) + derived `views_per_day`, `like_to_view`, `comment_to_view` in `06_packaging_features` | yes |

The vision.json schema (Gemini Vision pass) is documented in `references/phase1_research.md` Step 5.5.

These five axes are not aspirational — they are the input to every constitution, every insight, every visual data point, and the cross-reference scoring against the operator's own channel. Skipping any axis breaks downstream analysis.

## API Rate-Limit Strategy (mandatory)

YouTube rate-limits aggressive yt-dlp sessions silently — iteration continues but downloads return "Video unavailable. This content isn't available, try again later. The current session has been rate-limited by YouTube for up to an hour." This is the most common silent-failure mode in the skill. The canonical defensive invocation:

```bash
yt-dlp \
  --skip-download \
  --write-info-json \
  --write-thumbnail \
  --write-auto-subs --sub-lang "en.*,en" --sub-format "vtt/best" \
  --convert-thumbnails jpg \
  --no-warnings --ignore-errors \
  --download-archive "{output_root}/raw/{creator_slug}_done_archive.txt" \
  --break-match-filters "upload_date >= {window_start_yyyymmdd}" \
  --sleep-requests 4 \
  --sleep-interval 2 --max-sleep-interval 8 \
  --retries 3 --extractor-retries 3 \
  --print-to-file "[%(epoch)s] DONE %(id)s | %(upload_date)s | %(duration)s | %(view_count)s | %(title).80s" \
    "{output_root}/logs/{creator_slug}_videos_collected.log" \
  -o "{output_root}/raw/per_video_{creator_slug}/%(id)s.%(ext)s" \
  "https://www.youtube.com/channel/{CHANNEL_ID}/videos"
```

Wrapped as `scripts/youtube_collect.sh` for convenience.

Key flag rationale:
- `--sleep-requests 4` — 4-second delay between web requests inside a single video pull. Stops the "rapid-fire to YouTube" pattern that triggers rate-limiting.
- `--sleep-interval 2 --max-sleep-interval 8` — random 2-8 second delay between videos.
- `--download-archive {file}` — records every successfully-completed video ID; subsequent runs skip them. Makes the entire run idempotent and resumable across kills, rate-limit cooldowns, and session restarts.
- `--break-match-filters "upload_date >= …"` — stops iterating the channel feed once we hit a video older than the window cutoff. Saves hours when the channel has 4,000+ lifetime uploads.
- `--retries 3 --extractor-retries 3` — survives transient network failures.
- Targeting `/channel/{ID}/videos` (not the bare channel URL) skips the Shorts feed and gives strict newest-first ordering.

Detection: if `{collection_log}` contains BOTH "Video unavailable" AND "rate-limited by YouTube" repeated more than ~5 times in a row, the skill MUST report rate-limit detection in `00_run_report.md`. Recovery options:
1. Kill the current run, sleep 60 minutes, restart with the same command (the `--download-archive` makes this safe).
2. If `--sleep-requests 4` is already in effect, accept the longer ETA and continue.

Gemini Vision rate limits: `scripts/vision_analyze.py` is idempotent (skips per-video `vision.json` files that already exist) and respects the API's default 1 request/second. Failures are logged to `logs/vision_failures.json`; partial results are still aggregated into `analyses/vision_aggregate.csv`.

## Watcher Pattern for long-running collection

For any YouTube collection where the in-window queue is > 300 videos OR the time window is the full 24 months, the skill installs a completion-watcher inside the run's output directory:

- `scripts/watcher.sh` — polls the collection log every 60 seconds.
- `scripts/auto_refresh.sh` — fires once when the collection's FINISHED marker appears.

The watcher detects `FINISHED CHRIS COLLECTION` (or equivalent FINISHED-marker for the run) in `logs/{creator_slug}_collection.log` and fires `auto_refresh.sh` exactly once. `auto_refresh.sh` then runs:

1. `scripts/run_pipeline.sh` (normalize → features → analyze)
2. `scripts/vision_analyze.py` (Gemini Vision over every collected thumbnail; idempotent)
3. `scripts/auto_update_artifacts.py` (re-derive numeric claims in thread/visuals/copy_paste from fresh stats)
4. SVG → HTML → PNG re-render via `scripts/visuals.py` + `rsvg-convert`
5. Second Brain log to BOTH daily files (`--target-mode inbox`)

A `logs/auto_refresh.done` flag prevents double-fire. The watcher self-terminates after firing OR after a 24-hour deadline.

Both scripts are templates that ship with the skill. Launch with:

```bash
nohup bash scripts/watcher.sh > logs/watcher.stdout 2>&1 &
disown
```

The watcher is what lets a 6-hour collection run finish unattended and still produce a fresh, fully-rebound set of deliverables when the operator returns.

## Phase Execution

### Phase 1: Research & Corpus Building

**Branch on `target_platform`:**
- If `target_platform == threads` and `input_mode == local_corpus`, read `references/codex_threads_local_corpus.md` first, then use `references/phase1_threads_research.md` only for the shared feature taxonomy.
- If `target_platform == threads` and `input_mode == live_profile`, read `references/phase1_threads_research.md`.
- Otherwise (default `youtube`), read `references/phase1_research.md`.

Both pathways run the same 8-step protocol (creator resolution → format classification → reference profile → data collection → feature extraction → 4-layer analysis → 5 constitutions → exhaustive synthesis) and output a compatible corpus shape so Phase 2 can consume either.

At a high level:
1. Resolve the target creator to a canonical channel / profile
2. Classify their content into format families
3. Build a reference profile of the user's own channel / profile (default behavior; only skip if explicitly opted out)
4. Collect all qualifying content using the rate-limit-safe yt-dlp invocation (metadata + engagement metrics + text/transcript + thumbnails)
5. Extract detailed packaging features per video or post (text + numeric features)
5.5. **Run thumbnail vision pass** via `scripts/vision_analyze.py` (mandatory if `GOOGLE_API_KEY` is set; otherwise fall back inferentially with logged confidence drop)
6. Run 4-layer analysis (descriptive → comparative → portability → synthesis)
7. Create 5 operational constitutions
8. Write an exhaustive synthesis with 15+ ranked insight candidates

**If `output_mode` is `research_only`**: Stop here. Write the final report and return results to the user.

### Phase 2: Thread Writing (Synthesizer Method)

Read `references/phase2_thread.md` for the complete thread writing protocol.

Using Phase 1 research, write one finished 9-post Synthesizer-style thread for the configured platform (default: Threads).

Key requirements:
- Exactly 9 posts: hook + 7 insights + closer/CTA
- Hook selected from the Synthesizer Hook Bank (15 proven formats in the reference file)
- Every statistic must come from the Phase 1 corpus data (verifiable in `analyses/_stats.json` or as a row id in `06_packaging_features.json`)
- Each insight post follows the claim → data → takeaway structure
- Thread must read naturally on mobile
- Format rules adapt to the target platform (see `references/user_config.md`)
- Insights MUST cross-reference the operator's own channel — the takeaway line tells the operator what to do given their specific channel context

**If `output_mode` is `thread_only`**: Stop here. Write the final report and return results to the user.

### Phase 3: Visual Production

Read `references/phase3_visuals.md` for the complete visual production protocol.

Create 9 production-ready carousel visuals — one per thread post. Each visual is generated as SVG (primary), self-contained HTML/CSS, and PNG preview (if rendering is available). All on-image numbers come from `analyses/_stats.json` via `scripts/auto_update_artifacts.py` — never hand-typed.

Style: minimalist editorial, research dossier feel. Strong typographic hierarchy, generous negative space, clean grid.

### Phase 4: Publish & Verify

Read `references/phase4_publish.md` for the publishing and verification protocol.

Provide the finished thread as copy-paste-ready output. If using Threads as the target platform, stage it in Threadify only when the user explicitly asks for browser insertion. Codex runs are draft-first: do not publish, schedule, overwrite, or send live content unless the user explicitly promotes that exact action. Run the complete verification checklist across all 4 phases before declaring the pipeline complete.

## Output Structure

Read `references/output_structure.md` for the complete folder layout. By default, output goes into:

```
research/youtube-packaging/{creator-slug}/
```

For local Threads corpus runs, respect the provided `output_root` exactly when present.

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

The yt-dlp `--download-archive` file (per-creator) is the more important resume mechanism for the collection step itself: every successfully-collected video ID is recorded there and skipped on subsequent runs.

After each milestone, write a brief factual progress note to `00_run_report.md`.

## Notes & Exceptions

- If yt-dlp is rate-limited, see "API Rate-Limit Strategy" — kill, wait, resume; the `--download-archive` flag makes this safe.
- If the target creator has fewer than ~20 long-form videos in the time window, consider expanding to 36 months and log the decision.
- If thread numbers don't match source corpus, flag discrepancies and correct from source data; `auto_update_artifacts.py` should be run before publish to catch drift automatically.
- The pipeline adapts automatically to creator format — interview channels get guest analysis, solo educators get structure analysis, mixed channels get segmented analysis.
- Cross-reference (portability) layer is default-on. It only skips if the operator explicitly opts out — pass `your_channel_handle: ""` (empty string) to suppress.
