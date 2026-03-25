# Changelog

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
