# Changelog

## 1.1.0 — 2026-04-25

Per-video full-axis analysis, rate-limit handling, thumbnail vision, and watcher pattern.

### Added
- **Per-Video Full-Axis Analysis (mandatory)**: Every video that survives the inclusion filter is now analyzed across all five axes — thumbnail, title, full transcript, description, metadata/metrics — before entering the corpus. No partial entries.
- **API Rate-Limit Strategy**: Canonical rate-limit-safe yt-dlp invocation with `--sleep-requests 4`, `--sleep-interval 2 --max-sleep-interval 8`, `--retries 3`, `--extractor-retries 3`, and `--download-archive` for full resumability across kills, rate-limit cooldowns, and session restarts. Wrapped as `scripts/youtube_collect.sh`.
- **Mandatory thumbnail vision pass**: Gemini Vision (`gemini-2.5-pro` with `gemini-2.5-flash` fallback) runs over every collected thumbnail. Idempotent — skips thumbnails that already have `vision.json`. Produces structured per-thumbnail vision JSON + aggregated `analyses/vision_aggregate.{csv,json}`. Thumbnail constitution rules are now data-backed instead of inferential.
- **Watcher pattern for long-running collection**: `scripts/watcher.sh` polls the collection log every 60s and fires `scripts/auto_refresh.sh` exactly once when the FINISHED marker appears. Auto-refresh runs the entire pipeline (normalize → features → analyze → vision → auto-update) and writes the Second Brain log to both daily files. Standard for collections >300 videos or full 24-month windows.
- **Auto-binding of artifacts to source data**: `scripts/auto_update_artifacts.py` is now the only writer for numeric claims in `thread/final_thread.md`, `visuals/_assets.json`, and `publish/copy_paste.md`. All values are re-derived from `analyses/_stats.json` — hand-typed numbers in any visible artifact are forbidden.
- **10 new pipeline scripts** ship with the skill: `normalize.py`, `features.py`, `analyze.py`, `vision_analyze.py`, `visuals.py`, `auto_update_artifacts.py`, `run_pipeline.sh`, `auto_refresh.sh`, `watcher.sh`, `youtube_collect.sh`.
- **`references/03_render_fallbacks.md`**: Documents the PNG render priority chain — `rsvg-convert` (preferred) → headless browser → Chrome MCP → SVG-only. Includes detection logic and quality assurance checks.

### Changed
- **Cross-reference layer is default-on**: previously "Layer 3 — Portability (ONLY if `your_channel_handle` provided)". Now runs automatically; the only way to skip is for the operator to explicitly pass `your_channel_handle: ""` (empty string). Each portability finding now requires a `corpus_citation` field with row ids — never written without source attribution.
- **Hard Constraints expanded** from 10 to 13 — codified the per-video-full-axis rule, the visuals-data-binding rule, and the rate-limit-safe-yt-dlp rule.
- **Output Modes clarified**: `research_only` and `thread_only` both still include the vision pass and cross-reference layer — those are not optional add-ons.

### Why
The Apr 25 2026 forensics run on Chris Williamson surfaced five gaps: silent rate-limiting after ~340 videos out of 2,140, missing thumbnail vision, numeric drift between thread/visuals, no completion-watcher pattern, conditional cross-reference. All five are now first-class skill behaviors that hold every time the skill runs, on every platform that hosts it.

## 1.0.0 — 2026-03-25

Initial public release.

### Features
- Full 4-phase pipeline: research, thread writing, visual production, publishing
- 3 output modes: `full`, `research_only`, `thread_only`
- Multi-platform thread support: Threads (default), X, LinkedIn, Bluesky
- Zero-config operation — works with just web search, no API keys required
- YouTube Data API support for faster data collection when available
- Graceful degradation with full fallback logging
- Checkpoint and resume for interrupted runs
- 5 operational constitutions (master, title, thumbnail, hook, structure)
- 15-format Synthesizer Hook Bank for thread writing
- 9 carousel visuals in SVG + HTML (PNG if rendering available)
- Portability analysis when reference channel provided
