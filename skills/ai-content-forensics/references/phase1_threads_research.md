# Phase 1 (Threads): Research & Corpus Building

This is the Threads-creator pathway for Phase 1. Selected when `target_platform=threads`. Mirrors the YouTube pathway (`phase1_research.md`) step for step so the downstream synthesis methodology is identical. Everything downstream depends on the quality of this research — build the case file before drawing conclusions.

## Adaptation Principle

Adapt to the actual target creator. Do not force single-post patterns onto a thread-heavy creator, or vice versa. Do not blend unlike formats (standalone statements vs numbered threads vs reply-driven commentary) into one fake law set. Classify first, segment if needed, then extract.

## Rules

1. If `input_mode=local_corpus`, use the local corpus pathway first and do not scrape live Threads unless the user explicitly promotes a recovery/export step
2. If `input_mode=live_profile`, Chrome MCP/Computer Use first (operable Day 1), Threads API second (gated on Meta app review), no silent third fallback
3. Never guess ambiguous data — verify or ask one precise question
4. Keep raw evidence separate from interpretation
5. Preserve post text verbatim (including punctuation, line breaks, emoji)
6. Save media URLs as references (download is optional)
7. Log every fallback path used in `logs/fallback_log.md`
8. Every constitution rule must trace to corpus evidence
9. Exclude pure reposts with no added commentary from pattern analysis (but keep them in corpus for reply-rate analysis)
10. Mixed-format creators: segment corpus by format family before analysis
11. If a metric is unavailable for a post, log it — do not fabricate

---

## Step 1: Creator Resolution

Resolve `target_handle` to a canonical Threads profile.

Accept: `@handle`, `handle`, full URL `https://www.threads.net/@handle`. Strip leading `@` and URL prefix before downstream use.

Verify the handle is active:
- Profile loads without 404
- At least one post within `threads_time_window_months` window
- Not a deleted/restricted/shadowbanned account

Capture profile-level signals (available through either tier):
- `followers_count` (available via API when approved; via profile-header text scrape for Chrome MCP)
- `follower_demographics` (Threads API only, when approved — `CONFIRM_BEFORE_SHIP` for non-owned profiles)
- Bio text
- `is_verified` flag
- Profile picture URL

If the handle is ambiguous or inactive, ask one precise question and wait for the user before proceeding.

---

## Step 2: Format Classification

Classify the creator along Threads-native axes before extraction:

- **Post format mix:** single-post creator (standalone statements) vs thread creator (numbered/sequential multi-post) vs mixed
- **Media profile:** text-dominant vs image-heavy vs video-heavy vs carousel-heavy
- **Origination:** original-driven vs reply-driven (high `is_quote_post` / `reposted_post` ratio)
- **Intent:** CTA-heavy (sales/funnel) vs pure-commentary vs community-building (reply-engagement-seeking)
- **Positioning:** verified-brand vs unverified-creator vs anon/niche

Create better families if the evidence demands it. The goal is to avoid analyzing single-post creators with thread-lead patterns or judging reply-driven accounts with original-post metrics.

---

## Step 3: Reference Profile (Optional)

**Only if `your_threads_handle` is provided:**

Inspect the user's Threads profile and build a reference profile covering: positioning, content pillars, post format mix, audience size and demographics (if available), packaging patterns, weaknesses. This becomes the portability filter for all findings downstream.

If `your_threads_handle` is empty, skip entirely and proceed to data collection.

---

## Step 4: Data Collection

### Local Corpus Mode (Codex Preferred)

If `input_mode=local_corpus`, read `codex_threads_local_corpus.md` and run the deterministic local corpus workflow before considering any live browser/API collection.

Required behavior:
- Ingest every supplied `corpus_files` path.
- Normalize every candidate post into the shared Threads corpus schema.
- Dedupe by URL/source ID first, then by normalized author + body hash.
- If `expected_corpus_count` is provided and the verified unique count differs, stop before making findings and write a discrepancy report.
- Use browser automation only for the final Threadify draft insertion step, not for analysis.

For the Threadify vault rerun, the preferred exact source is:

```
/Users/lennoxsaint/swipefile/vault-extract/THREADIFY VAULT EXTRACT 060426.jsonl
```

This file contains one malformed multi-line JSON record; the local corpus runner repairs it by splitting records on `{"source_id"` boundaries and escaping embedded raw newlines before JSON parsing.

### Environment Check

First, check the local environment:
- Is Chrome MCP paired to `MacBook-Pro-2.local` with device ID `19d50471-e353-4b74-b330-06ab6bdb76e7`? (Tier 1 prerequisite.)
- Does `~/.config/threads/token.json` exist? (Tier 2 readiness probe.)
- Is there a prior-run checkpoint at `logs/checkpoint.json`? Resume if present and current.

### Tier Selection

Two tiers only. No Tier 3.

- **Tier 1: Chrome MCP scrape** — operable Day 1. Primary path.
- **Tier 2: Threads API** — documented in full below but **NOT operable until Meta app review is approved** for `threads_basic` + `threads_profile_discovery`. When approved, Tier 2 becomes preferred (more structured, better rate, fewer UI-fragility risks).

Selection logic at runtime:

```
IF ~/.config/threads/token.json exists AND a capability probe succeeds:
  → prefer Tier 2 for metadata
  → if /insights returns 403 on non-owned posts, keep Tier 2 for metadata + fall to Tier 1 for metrics
  → on 429/5xx: fall entirely to Tier 1 for this run
ELSE:
  → Tier 1 only
IF Tier 1 fails (extension not connected, login wall unresolved after user "ready", zero posts after bounded scroll):
  → halt and surface to user; do NOT silently produce an empty corpus
Log every attempt and transition in logs/fallback_log.md
```

### Tier 1: Chrome MCP (primary, operable Day 1)

Follows the pattern proven in `~/.claude/skills/ghostwrite_thread/SKILL.md`.

**Pairing lock (mandatory before any Chrome MCP call):**
1. Call `mcp__claude-in-chrome__tabs_context_mcp({createIfEmpty: true})`.
2. Verify `hostname == MacBook-Pro-2.local`.
3. Read `~/.claude.json` — require `chromeExtension.pairedDeviceId == 19d50471-e353-4b74-b330-06ab6bdb76e7` and `chromeExtension.pairedDeviceName == MacBook-Pro-2 Chrome`.
4. If extension not connected or device mismatch, STOP and report the exact CLAUDE.md error message. Do NOT proceed.

**Navigation + login-wall:**
1. `mcp__claude-in-chrome__tabs_create_mcp` → store `tabId`.
2. `mcp__claude-in-chrome__navigate` → `https://www.threads.net/@{handle}`.
3. Detect login wall via `mcp__claude-in-chrome__read_page`. If a sign-in CTA dominates, halt with the exact prompt:
   > "I couldn't access your authenticated Threads session automatically. Please open Threads in Chrome on this MacBook and reply 'ready'."
4. Resume only when the user replies `ready`. If still blocked after resume, halt and ask the user to re-authenticate in Chrome directly.

**Bounded scroll (3-condition stop, from ghostwrite_thread):**
Stop when ANY of:
- Oldest visible post is older than `threads_time_window_months` (default 12), OR
- `threads_post_count` posts collected (default 200), OR
- No new posts load after 3 consecutive scroll attempts.

**Per-post extraction:**
- Prefer `mcp__claude-in-chrome__javascript_tool` with DOM selectors for reliable, structured extraction of `post_url`, `post_id`, `timestamp_relative`, `likes_count`, `replies_count`, `reposts_count`, `text`, `is_quote_post`, `is_original`, `media_type`.
- Fallback: `mcp__claude-in-chrome__get_page_text` + regex (swipefile-hunter pattern) if `javascript_tool` selectors break due to DOM changes.

**Failure modes that halt the pipeline (no Tier 3 fallback):**
- Chrome extension not connected OR pairing mismatch → halt with CLAUDE.md error message.
- Login wall persists after user "ready" → halt; ask user to re-auth.
- Zero posts extracted after bounded scroll → halt and surface as a data-quality issue. Do NOT produce an empty corpus and proceed.

### Tier 2: Threads API (documented, gated on Meta app review)

Ships as reference documentation. Not operable until `threads_profile_discovery` is approved.

**Setup prerequisites:**
- Meta developer account at https://developers.facebook.com
- App created with the Threads product enabled
- Permissions requested: `threads_basic`, `threads_profile_discovery` (`CONFIRM_BEFORE_SHIP`: exact scope string — verify against the scopes doc before coding)
- App review submitted and approved (multi-week)
- Long-lived user token stored at `~/.config/threads/token.json`
- Token refresh handled per Threads API docs

**Endpoints:**

| Purpose | Path | Notes |
|---|---|---|
| List any public creator's posts by handle | `GET /profile_posts?username={handle}` | Requires `threads_basic` + `threads_profile_discovery`. No consent from target creator needed. |
| Single post detail | `GET /{threads-media-id}` | Token required. |
| Per-post insights | `GET /{threads-media-id}/insights` | `threads_manage_insights`. `CONFIRM_BEFORE_SHIP`: may be author-scoped only. If 403 on non-owned posts, metrics fall to Tier 1. |
| User-level insights | `GET /{threads-user-id}/threads_insights` | Token must belong to that user. Not useful for target-creator analysis. |
| Keyword search | `GET /keyword_search` | `CONFIRM_BEFORE_SHIP`: endpoint path not fully confirmed from primary docs. |

Base URL: `https://graph.threads.net/v1.0/`

**Fields returned by `/profile_posts`** (confirmed from https://developers.facebook.com/docs/threads/retrieve-and-discover-posts/retrieve-posts/):
`id, media_product_type, media_type, media_url, permalink, owner, username, text, timestamp, shortcode, thumbnail_url, children, is_quote_post, quoted_post, reposted_post, alt_text, link_attachment_url, gif_url, poll_attachment, topic_tag, is_spoiler_media, text_entities, text_attachment, is_verified, profile_picture_url`.

**Insights metrics** (per post): `views, likes, replies, reposts, quotes, shares`. No `saves` metric exists — `CONFIRM_BEFORE_SHIP`: any analysis that assumes YouTube-parity "saves" must be omitted.

**Pseudocode:**

```
GET /profile_posts?username={handle}&limit=100&fields=id,text,timestamp,media_type,permalink,is_quote_post,reposted_post,text_entities
→ paginate until threads_post_count reached OR posts older than threads_time_window_months
Capability probe: fetch 1 post's insights first.
For each post id (if insights probe succeeded):
  GET /{id}/insights?metric=views,likes,replies,reposts,quotes,shares
  if 401/403 → fall to Tier 1 for metrics, keep Tier 2 for metadata
  if 429/5xx → fall entirely to Tier 1 for the run
```

**Fallback triggers:** 401 (token), 403 (scope or ownership), 429 (rate), 5xx (service).

**Rate limits** (confirmed from https://developers.facebook.com/docs/threads/overview):
- Profile discovery / reads: 1,000 requests per user per 24h rolling.
- Keyword search: 500 queries per 7-day rolling.
- Publishing (unused here): 250 posts per user per 24h. `CONFIRM_BEFORE_SHIP`: exact insights quota formula not in scraped text.

**Explicit gate note:** Tier 2 is NOT operable until Meta app review is approved. Until then, the skill runs on Tier 1 Chrome MCP. When Tier 2 becomes operable, update the selection logic block in this file — no other file needs to change.

### Capability Matrix

What each tier can deliver (no Tier 3 per architecture decision):

| Field | Tier 1 Chrome MCP | Tier 2 Threads API (when approved) |
|---|---|---|
| text | yes | yes |
| timestamp | yes (relative — needs normalization) | yes (ISO 8601) |
| media_type | yes (visual inference) | yes |
| likes | yes (rendered) | yes (insights) if not author-scoped |
| replies | yes (rendered) | yes (insights) if not author-scoped |
| reposts | yes (rendered) | yes (insights) if not author-scoped |
| quotes | partial (reply indicator only) | yes (insights) if not author-scoped |
| views | no (not shown publicly) | yes (insights) if not author-scoped |
| saves | no | no (metric does not exist) |
| shares | no | yes (insights) if not author-scoped |

### Logging Format

Log every data-collection attempt, fallback, and tier transition in `logs/fallback_log.md`:

```
[2026-04-20T14:02:11+08:00] threads tier=1 url=https://www.threads.net/@lennox_saint status=ok scrolled=12 posts=200 action=continue
[2026-04-20T14:15:03+08:00] threads tier=2 endpoint=/profile_posts?username=lennox_saint status=200 posts=100 action=continue
[2026-04-20T14:15:14+08:00] threads tier=2 endpoint=/<media_id>/insights status=403 reason=scope_or_ownership action=fallthrough_tier1_for_metrics
```

Format matches the YouTube pathway's logging convention for consistency.

### Time Window

Apply `threads_time_window_months` (default 12). Only include posts published within this window. Threads cycles faster than YouTube, so 12 months is the default vs 24 for YouTube.

If the creator has fewer than ~40 qualifying posts in window, consider expanding to 18 or 24 months. Log this decision in `00_run_report.md`.

### Post Inclusion Rules

- Include original posts, thread leads, thread continuations, and original carousels/images/videos.
- Pure reposts (where `reposted_post` is set and `text` is empty) go into a separate track — counted for frequency analysis but excluded from pattern/feature analysis.
- Quote posts (`is_quote_post=true`) are included with full feature extraction; they count as original commentary.
- Replies to OTHER creators (not to own thread) go in `exclusions_log.md` with reasoning, unless the creator is reply-driven (per Step 2 classification), in which case include them.

---

## Step 5: Feature Extraction

For every qualifying post, extract these features. This is the Threads equivalent of the YouTube title/thumbnail/hook/structure extraction.

### Corpus Schema Parity

| YouTube schema | Threads equivalent |
|---|---|
| URL | `permalink` |
| video ID | `id` |
| publish date | `timestamp` (ISO 8601 after normalization) |
| title (first impression) | `text` first line / `hook_opener` |
| duration | word count of `text` |
| thumbnail URL + analysis | `media_url` / `thumbnail_url` + media type |
| transcript full text | `text` (full body) |
| views, likes, comments | `views, likes, replies, reposts, quotes, shares` |
| title trigger categories | opener trigger categories (same 10-category taxonomy) |
| hook/opening analysis | opener + first-line analysis (same taxonomy) |
| structure: section map, intro, pacing | post type, is_original, is_quote_post, thread position, CTA presence, question presence, trigger-word density |

### Opener Features (parallel to YouTube title features)

- `hook_opener`: literal first 140 chars of `text` (matches Threads' own reading-preview ceiling)
- Character count, word count of the opener
- Leading token pattern (number, question, how-to, statement, claim, name, etc.)
- Uses: numbers, contrast, quoted claim, implied promise
- Trigger categories: pain, curiosity, speed, status, money, health, identity, certainty, fear, transformation (same 10 categories as YouTube for cross-platform consistency)
- Opener archetype (template pattern: "X beats Y", "Unpopular opinion:", "Thread 🧵", etc.)
- Claim specificity: vague / moderate / exact

### Media Features (parallel to thumbnail features)

- `has_media`: bool
- `media_type`: `text_only | image | video | carousel | reply | quote | repost`
- Carousel slide count (if `children` array is present)
- Alt text presence and text (from `alt_text`)

Note: Threads does not expose per-post face/contrast/focal analysis through either tier. These YouTube-specific visual features are omitted from the Threads corpus. Replaced by the simpler `has_media` flag.

### Hook / First-Line Features

- Exact first line (everything before the first line break or sentence boundary)
- First 30-word summary of the post
- Time-to-payoff: for thread leads, how many posts in does the main promise land (1-of-N style)
- Does the opener validate the media promise (if any) quickly?
- Hook archetype (shared with the opener archetype; may collapse these into one field if overlap is consistent)

### Post-Structure Features

- `post_type` (see enum above)
- `thread_position`: `standalone | thread_lead | thread_continuation` (heuristic: detect `1/`, `🧵`, `part 1`, or sequential text patterns)
- `is_original`: bool (true unless `reposted_post` is set)
- `cta_presence`: detect CTA phrasing (`follow`, `dm me`, `link in bio`, `@mention`, `check out`, full URL)
- `cta_style`: soft (conversational) / explicit (imperative) / link (bare URL)
- `question_presence`: ends with `?` OR contains engagement-prompt pattern (e.g., "agree?", "what would you add?")
- `trigger_density`: count of trigger-words per 100 words (same 10 categories as openers)
- Word count, sentence count, paragraph count
- Emoji count and emoji-per-word ratio
- Line-break density

### Engagement Derived Metrics

- Age in days, likes-per-day
- Likes-to-replies ratio (signal of conversation vs approval)
- Likes-to-reposts ratio (signal of virality vs personal resonance)
- If views available (Tier 2 only): likes-to-views, replies-to-views

### Conditional Modules

Enable per format family from Step 2:

**Thread-creator module:**
- Average thread length
- Opener-to-reveal length (words between hook and main payoff)
- Sequential-signal style: `1/N`, `🧵`, implicit, mixed
- Thread-lead-only likes vs full-thread likes distribution (where measurable)

**Single-post creator module:**
- Opener-density (how much work the first line does)
- Standalone-claim archetypes (contrarian take, reframe, data point, declarative, question)

**Reply-driven module:**
- Quote-vs-original ratio
- Which creators they engage with most
- Reply-thread length when replying to own posts

**CTA-heavy module:**
- CTA frequency (percentage of posts with CTA)
- CTA position: opener / body / closer
- CTA phrasing archetypes

---

## Step 6: Analysis (4 Layers)

Identical methodology to the YouTube pathway — the synthesis stays consistent across platforms.

### Layer 1 — Descriptive
What patterns repeat in openers, media use, CTAs, thread structures? If multiple format families exist from Step 2, what differs by family?

### Layer 2 — Comparative

Top 10% vs bottom 25% splits by engagement (primary metric: likes-per-day; secondary: replies-per-day). Normalize by post age where possible.

Length buckets for Threads:
- `≤60 words` (micro-post)
- `61-150` (standard)
- `151-300` (medium)
- `301-500` (long-form, Threads character ceiling)

Measure lift on:
- Hook opener archetypes
- Trigger categories
- CTA presence vs absence
- Question presence vs absence
- Media presence vs absence
- Post-type (thread_lead vs standalone)

State correlation, not causality. Flag confounds (e.g., verified creators have inherent visibility advantage).

### Layer 3 — Portability (only if `your_threads_handle` provided)

Same scoring schema as YouTube pathway:
- `evidence_strength` (strong/moderate/weak)
- `prevalence_in_corpus` (percentage of posts)
- `effect_size_if_measurable`
- `portability_to_user_profile` (high/medium/low)
- `dependence_on`: verified-blue-tick, existing audience, niche, controversy appetite
- `risk_of_false_transfer`
- `recommendation`: adopt / test / ignore

Three buckets:
- **A. Portable now** for user's profile
- **B. Conditional** — worth testing
- **C. Creator-specific artifacts** — do not blindly copy

If no reference handle provided, skip Layer 3 entirely.

### Layer 4 — Synthesis

Convert strongest findings into operational constitutions. Prefer actionable rules over vague commentary.

---

## Step 7: Constitutions

Create 5 constitutions, each containing the same structure as the YouTube pathway (purpose, non-negotiable rules, strong patterns, conditional rules, anti-patterns, evidence base, portability notes, confidence labels).

Threads constitutions (parallel to YouTube's 5):

1. **Master packaging constitution (Threads)** — overview + cross-cutting rules.
2. **Opener constitution** — parallel to YouTube's title constitution. Governs the first 140 chars.
3. **Post-structure constitution** — parallel to YouTube's script/structure. Governs word count, thread length, sequencing signals, question placement.
4. **Media-use constitution** — parallel to YouTube's thumbnail. Governs when to attach image/video/carousel vs text-only.
5. **CTA-and-engagement constitution** — Threads-native, replaces YouTube's intro-style constitution. Governs when and how to invite follows, replies, link clicks.

Write these as operational law, not fluffy commentary. Another creator or agent should be able to follow them mechanically.

---

## Step 8: Exhaustive Synthesis

Create a comprehensive synthesis document covering:

1. Corpus scope and method (which tier, how many posts, time window)
2. Target creator profile and classification (from Step 2)
3. Reference profile (if provided)
4. Format-family breakdown (if applicable)
5. Strongest opener laws
6. Strongest media-use laws
7. Strongest post-structure laws
8. Strongest CTA-and-engagement laws
9. Top vs bottom performer comparisons with effect sizes
10. Portable laws (if reference handle provided)
11. Contradictions and outliers
12. Recommended experiments
13. **RANKED LIST**: minimum 15 screenshot-worthy insight candidates, scored by:
    - Surprise
    - Specificity
    - Actionability
    - Shareability

Clearly separate: raw evidence → interpreted patterns → portable laws → creator-specific artifacts.

This ranked insight list is the direct input for Phase 2 thread writing. Phase 2 is platform-agnostic and consumes the same insight shape regardless of whether the analysis came from YouTube or Threads.

---

## Sources

Threads API documentation and platform behavior cited from (accessed 2026-04-20):

- https://developers.facebook.com/docs/threads/overview
- https://developers.facebook.com/docs/threads/get-started/
- https://developers.facebook.com/docs/threads/get-started/get-access-tokens-and-permissions/
- https://developers.facebook.com/docs/threads/retrieve-and-discover-posts/retrieve-posts/
- https://developers.facebook.com/docs/threads/insights/
- https://developers.facebook.com/docs/threads/changelog/
- https://www.postman.com/meta/threads/documentation/dht3nzz/threads-api

Chrome MCP patterns borrowed from:
- `~/.claude/skills/ghostwrite_thread/SKILL.md` — bounded scroll + login wall pattern
- `~/.claude/skills/swipefile-hunter/SKILL.md` — Threads URL conventions
- `~/.claude/CLAUDE.md` — Chrome MCP pairing-lock policy

CONFIRM_BEFORE_SHIP items (must be verified before first real Tier 2 run):
1. Exact `threads_profile_discovery` scope string.
2. Whether `/insights` on non-owned public posts is permitted or author-scoped. Likely restricted.
3. `keyword_search` endpoint path and exact permissions.
4. Rate-limit quota formula for insights reads beyond the documented ceilings.
5. Confirmation that `saves` metric truly does not exist — not just unobserved.
