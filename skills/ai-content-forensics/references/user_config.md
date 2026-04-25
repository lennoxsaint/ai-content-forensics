# User Configuration

When invoked, collect these inputs from the user. The required field depends on `target_platform`: for YouTube (default) it's `target_youtuber`; for Threads it's `target_handle`. Everything else has sensible defaults.

## Configuration Table

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `target_platform` | no | youtube | Analysis target platform. Supported: `youtube` \| `threads`. Selects the Phase 1 data-collection pathway |
| `input_mode` | no | live_profile | Threads-only input mode. Supported: `local_corpus` \| `live_profile`. Use `local_corpus` when a Threadify vault/export already exists on disk |
| `target_youtuber` | conditional | — | The YouTuber to analyze (name, handle, or URL). Required when `target_platform=youtube` |
| `target_handle` | conditional | — | The Threads creator to analyze (e.g. `@lennox_saint` or `lennox_saint`). Required when `target_platform=threads` and `input_mode=live_profile` |
| `corpus_files` | conditional | none | One or more local corpus files. Required when `target_platform=threads` and `input_mode=local_corpus` |
| `expected_corpus_count` | no | none | Optional hard gate for local corpus runs. If provided, stop when the verified deduped count differs |
| `output_root` | no | derived from target | Optional absolute output directory. Use this for project-tied reruns |
| `output_mode` | no | full | Pipeline scope: `full` (all 4 phases), `research_only` (Phase 1 only), or `thread_only` (Phases 1-2 only) |
| `your_channel_handle` | no | none | Your YouTube channel for portability comparison (YouTube pathway only) |
| `your_threads_handle` | no | none | Your Threads handle for portability comparison (Threads pathway only) |
| `publisher_handle` | no | none | Your handle for the CTA (e.g. @lennox_saint) |
| `platform_name` | no | Threads | Output platform for the generated thread. Supported: `Threads`, `X`, `LinkedIn`, `Bluesky`. Independent of `target_platform` |
| `reference_creator_name` | no | none | A creator whose audience is similar to yours (for audience-fit filtering) |
| `reference_creator_context` | no | none | Niche, audience, offer, voice, or positioning notes about the reference creator |
| `takeaway_label` | no | Threads takeaway | Label used at the end of each insight post. Auto-adapts to platform_name if left at default |
| `time_window_months` | no | 24 | Months of content to analyze (YouTube default) |
| `threads_time_window_months` | no | 12 | Months of posts to analyze (Threads pathway — shorter because Threads cycles faster) |
| `threads_post_count` | no | 200 | Max Threads posts to ingest into the corpus (bounded-scroll ceiling) |
| `visual_background` | no | #f7f4ee | Background color for visuals |
| `visual_accent` | no | #8f1d1d | Accent color for visuals |
| `visual_text` | no | #111111 | Text color for visuals |

## How to Collect

Ask the user conversationally. First establish the target platform, then collect the required field for that pathway, then offer the optional settings.

**YouTube pathway (default):**
```
"Which YouTuber do you want to analyze?"

Then:
"A few optional settings before I start:
- Your YouTube channel handle (for portability comparison)?
- Your Threads/X/LinkedIn handle (for the CTA in the final thread)?
- Output mode: full pipeline, research only, or thread only?
- Any custom time window or visual colors?

Or I can just use the defaults and get started."
```

**Threads pathway:**
```
"Which Threads creator do you want to analyze? (Give me their handle, e.g. @lennox_saint)"

Then:
"A few optional settings before I start:
- Your Threads handle (for portability comparison)?
- Output mode: full pipeline, research only, or thread only?
- Time window (default: last 12 months)?
- Post count cap (default: 200)?

Or I can just use the defaults and get started."
```

**Threads local corpus pathway (Codex preferred when a vault/export exists):**
```
"Which local corpus file should I analyze?"

Then:
"Do you want a hard expected-count gate, and where should I write the output?"
```

If the user supplies the corpus path, expected count, and output root in the prompt, do not ask again. Run the local corpus gate first.

If the user just gives a YouTuber name or Threads handle and says "go", use all defaults and start immediately.

## Invocation Examples

```
# YouTube (default — no target_platform needed)
target_youtuber: "Luna"
platform_name: "Threads"
publisher_handle: "@lennox_saint"

# Threads
target_platform: "threads"
target_handle: "@lennox_saint"
platform_name: "Threads"
publisher_handle: "@lennox_saint"
threads_post_count: 200
threads_time_window_months: 12

# Threads local corpus
target_platform: "threads"
input_mode: "local_corpus"
corpus_files:
  - "/Users/lennoxsaint/swipefile/vault-extract/THREADIFY VAULT EXTRACT 060426.jsonl"
expected_corpus_count: 1996
output_root: "/Users/lennoxsaint/content-pipeline/2026-04-21-threads-growth-is-a-lie/research/threads-packaging/threadify-vault-1996-codex"
output_mode: "full"
```

## Platform-Specific Format Rules

When `platform_name` is set, adapt the thread output:

### Threads (default)
- 500 character limit per post
- No hashtags in body posts (optional 1-2 in closer)
- Natural sentence case
- `takeaway_label` default: "Threads takeaway"
- Publishing tool: https://www.threadify.app/plans
- Canvas size: 1080x1350px (carousel optimized)

### X (Twitter)
- 280 character limit per post
- Tighter copy required — compress insight posts
- `takeaway_label` default: "Takeaway"
- No publishing tool auto-opened
- Canvas size: 1080x1350px

### LinkedIn
- 3000 character limit per post
- Can expand insight explanations slightly
- More professional tone acceptable
- `takeaway_label` default: "Key insight"
- No publishing tool auto-opened
- Canvas size: 1080x1350px

### Bluesky
- 300 character limit per post
- Similar constraints to X
- `takeaway_label` default: "Takeaway"
- No publishing tool auto-opened
- Canvas size: 1080x1350px

## Hook Format Selection

The hook format for the thread is selected automatically from a bank of 15 proven Synthesizer-style hooks (see `phase2_thread.md`). No manual template selection is needed from the user.

## Automatic Defaults

If `takeaway_label` is left at default and `platform_name` is changed from Threads, the takeaway label auto-adapts to the platform default listed above. If the user explicitly sets `takeaway_label`, that value is used regardless of platform.

If `publisher_handle` is provided without a platform prefix (e.g., `lennox_saint` instead of `@lennox_saint`), prepend `@` automatically.
