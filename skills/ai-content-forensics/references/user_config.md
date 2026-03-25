# User Configuration

When invoked, collect these inputs from the user. Only `target_youtuber` is required — everything else has sensible defaults.

## Configuration Table

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `target_youtuber` | **yes** | — | The YouTuber to analyze (name, handle, or URL) |
| `output_mode` | no | full | Pipeline scope: `full` (all 4 phases), `research_only` (Phase 1 only), or `thread_only` (Phases 1-2 only) |
| `your_channel_handle` | no | none | Your YouTube channel for portability comparison |
| `publisher_handle` | no | none | Your handle for the CTA (e.g. @lennox_saint) |
| `platform_name` | no | Threads | Target platform for the thread. Supported: `Threads`, `X`, `LinkedIn`, `Bluesky` |
| `reference_creator_name` | no | none | A creator whose audience is similar to yours (for audience-fit filtering) |
| `reference_creator_context` | no | none | Niche, audience, offer, voice, or positioning notes about the reference creator |
| `takeaway_label` | no | Threads takeaway | Label used at the end of each insight post (e.g. "Threads takeaway:"). Auto-adapts to platform_name if left at default |
| `time_window_months` | no | 24 | Months of content to analyze |
| `visual_background` | no | #f7f4ee | Background color for visuals |
| `visual_accent` | no | #8f1d1d | Accent color for visuals |
| `visual_text` | no | #111111 | Text color for visuals |

## How to Collect

Ask the user conversationally. Start with the required field, then offer the optional ones as a group:

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

If the user just gives a YouTuber name and says "go", use all defaults and start immediately.

## Platform-Specific Format Rules

When `platform_name` is set, adapt the thread output:

### Threads (default)
- 500 character limit per post
- No hashtags in body posts (optional 1-2 in closer)
- Natural sentence case
- `takeaway_label` default: "Threads takeaway"
- Publishing tool: threadify.app/plans
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
