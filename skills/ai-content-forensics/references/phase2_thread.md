# Phase 2: Thread Writing (Synthesizer Method)

Using the completed Phase 1 research corpus, write one finished, copy-paste-ready Synthesizer-style thread for the configured `platform_name` (default: Threads).

## What Is a Synthesizer Thread?

A Synthesizer thread is an authority-building distillation. Its job is to:

- Compress complex research into clear lessons
- Borrow or transfer authority without sounding derivative
- Save the reader time
- Make the reader feel they got the best parts without doing all the digging
- Turn dense research into simple, useful, portable insights

The thread should feel like: "I did the heavy lifting. Here are the few things that actually matter. You can use this even if you're much smaller than the source creator."

---

## Context Rules

Use all available context from the Phase 1 research data — research documents, analyses, synthesis reports, corpus summaries, creator profiles, portability findings, pattern breakdowns, quotes, constitutions, evidence files.

Do not mention source document names or file names in the output thread.

If `reference_creator_name` and `reference_creator_context` are provided:
- Keep relevance for an audience similar to the reference creator
- Treat these as audience-fit guidance, not mandatory text to include
- Only mention them in the thread if it clearly improves relevance or the CTA

---

## Thread Structure

Output exactly 9 posts:
- **Post 1** = hook
- **Posts 2-8** = exactly 7 distinct insights
- **Post 9** = final closer / CTA

Separate each post with a line that contains only the em dash character: **—**

Do not return notes, commentary, analysis, appendices, explanations, or labels like "Post 1". The final output must be clean and ready to paste directly into the platform.

---

## Platform Adaptation

Before writing, check `platform_name` from the config and apply the matching format rules from `references/user_config.md`. Key adaptations:

- **Character limits**: Threads (500), X (280), LinkedIn (3000), Bluesky (300). Every post must fit within the platform limit.
- **Takeaway label**: Uses `takeaway_label` from config (auto-adapts to platform if left at default).
- **Tone**: LinkedIn allows slightly more professional register. All others: conversational, sharp, evidence-led.
- **CTA format**: Adapt the closer to feel native on the target platform.

If the platform is X or Bluesky (tight character limits), compress insight posts more aggressively. Lead with the number, cut supporting sentences to 1-2, keep takeaways to one short line.

---

## Hook Selection System

Before writing the thread, silently do this:

1. Review all available context from the Phase 1 research
2. Score each hook format in the Synthesizer Hook Bank (below) on:
   - Evidence fit
   - Specificity
   - Curiosity / tension
   - Portability to smaller creators
   - Mobile clarity
   - Whether the hook earns the rest of the thread
3. Draft 3 candidate hooks using the top-scoring formats
4. Silently choose the strongest one
5. Use only the final winning hook in the output

### Hook Priorities
- Prefer hooks that foreground real proof
- Prefer hooks with exact numbers when the data supports it
- Prefer hooks that imply compression, curation, or distillation
- Prefer hooks that make the thread feel worth reading even to people who don't care about the source creator
- If the data is belief-breaking, you may choose a belief-dismantling hook
- If the data is more tactical than narrative, prefer clarity over drama
- Never force fake hype or fake vulnerability
- Never use a hook that sounds like generic "content about content"
- Never close the loop too early

### Hook Rules
The final hook must:
- Feel native to the platform
- Clearly signal that real research was done
- Create curiosity without sounding like lazy clickbait
- Act as a practical shortcut for the reader
- Fit the available evidence
- Stay concise enough to work on mobile
- Use sentence case or natural platform-native casing

Default priority: Proof → Promise → Plan

If the data strongly supports a belief-dismantling angle, you may instead use: Hyper-credible proof → Pain/false-belief agitation → Transformative plan

---

## Synthesizer Hook Bank (15 Formats)

### 1. Source achievement + research investment
"[Source creator] has [big result].

I wanted to know why.

So I spent [time / money / effort] studying [source].

Here are [number] lessons smaller creators can steal:"

### 2. Research distillation
"I dug through [corpus / body of work / dataset] to find the patterns that actually matter.

Here are [number] lessons worth stealing:"

### 3. Authority transfer
"[Source creator] is one of the best in the world at [thing].

I studied the patterns behind it.

Here are [number] takeaways that matter for smaller creators:"

### 4. Surprising data point
"[Surprising number or result].

That sent me down the rabbit hole.

Here are [number] lessons the data made obvious:"

### 5. Pattern extraction
"I kept seeing the same pattern show up again and again in this research.

Here are the [number] patterns I would steal first:"

### 6. Counterintuitive synthesis
"Most people look at [source creator / corpus] and copy the wrong thing.

The data points somewhere else.

Here are [number] lessons I would actually take:"

### 7. Research shortcut
"I went through the research so you do not have to.

Here are [number] lessons that are simple, portable, and worth using:"

### 8. Big result, small creator angle
"[Source creator] got [big result].

That does not mean smaller creators should copy everything.

Here are [number] things worth stealing anyway:"

### 9. Myth correction
"This research killed [common belief] for me.

Here are [number] lessons that changed my mind:"

### 10. Question-driven inquiry
"I had one question going into this research:

[Question].

Here are the [number] answers that kept showing up:"

### 11. Insight compression
"I pulled the best ideas out of a much bigger body of work.

Here are [number] insights that survived the cut:"

### 12. Data-backed rethink
"The obvious lesson from this research is wrong.

The better lesson is more useful.

Here are [number] takeaways I would keep:"

### 13. Source quote / fact opener
"[Quote or fact from the research].

That was the line that hooked me.

Here are [number] lessons that came out of it:"

### 14. Investment proof + promise
"I spent [time / money / effort] studying this because I wanted a clear answer.

I found one.

Here are [number] takeaways you can use right away:"

### 15. Belief dismantling
"If you still think [old belief], this research will mess with your head.

Here are [number] lessons that point to a better way:"

---

## Body Post Format (Posts 2-8)

Each insight post must follow this exact structure:

**1. First line:** One sharp claim in plain text, built around the strongest number or clearest finding.

**2. Middle:** 2-3 short sentences explaining the finding with exact supporting data from the research.

**3. Ending:**
"{takeaway_label}:"
Then 1 short actionable takeaway sentence.

Example structure:

```
[Claim]

[Data sentence]
[Data sentence]

Threads takeaway:
[Action]
```

### Body Post Rules
- Every insight must use a different underlying finding
- Lead with the strongest number, ratio, percentage, multiplier, count, or contrast
- Keep the writing simple and easy to scan on mobile
- Do not use markdown bold
- Do not use bullet points
- Do not use hashtags
- Do not force emojis
- Keep each post concise enough for the platform
- Make every middle post feel worth screenshotting on its own

---

## Insight Selection

From the ranked insight list in the synthesis (Phase 1, Step 8), select exactly 7.

Each chosen insight must be:
1. Genuinely surprising, counterintuitive, or non-obvious
2. Backed by exact evidence from the data
3. Useful to smaller creators, not just the source creator
4. Strong enough to stand alone as a viral social post

### Insight Mix Rules

The 7 chosen insights must include range. Minimum mix:
- At least 2 counterintuitive findings
- At least 1 title or title-formula insight
- At least 1 hook or opening-line insight
- At least 1 structure, pacing, retention, or format insight

Do not let all 7 insights come from one category. Only include thumbnail-related insights if the research clearly supports them.

### Selection Logic (ranked priority)

1. Surprise
2. Strength and specificity of evidence
3. Usefulness for smaller creators
4. Shareability
5. Relevance to audience (if reference_creator provided)
6. Distinctness from the other selected insights

If 2 candidate insights overlap, keep the stronger one and discard the weaker one. Trust the actual data over any prior assumptions.

---

## Last Post Rules (Post 9)

The last post must be an adapted version of this pattern:

```
What you should do now:
I went through [real proof of work] for this.
The patterns are pretty clear: [3 short synthesis points].
Follow {publisher_handle} if you want more data-backed breakdowns like this.
```

Requirements:
- Mention the real work done using only evidence supported by the available data
- Do not invent counts
- Keep the 3 synthesis points short, concrete, and useful
- Make the CTA feel natural, not pushy or salesy
- Do not mention file names, appendices, or behind-the-scenes notes
- Adapt the wording naturally to the source data and final thread

If `publisher_handle` is not provided, omit the follow CTA and end with the synthesis points only.

---

## Thread Voice

**Should feel:** distilled, sharp, generous, evidence-led, mobile-friendly

**Should NOT feel:** bloated, preachy, academic, corporate, vague, worshipful, overpolished

**Use:**
- Short, clear, human sentences
- Exact numbers from the data
- 3rd-5th grade reading level except where names, precise terms, or statistics require more precision
- One idea per line when useful
- Line breaks for speed and clarity
- Simple words, concrete nouns, natural rhythm
- Natural sentence case or platform-native casing

**Avoid:**
- AI-sounding filler
- Abstract motivational wrap-up
- Stale "creator economy" phrasing
- Jargon for the sake of jargon
- Forced all-lowercase or forced Title Case

Use whatever casing feels most natural for the final thread.

---

## Hard Rules

1. Do not fabricate any number
2. Every statistic must come from the Phase 1 corpus data
3. Do not use the word "engagement"
4. Do not start an insight with "Did you know"
5. Do not start an insight with "Here's the thing"
6. Do not repeat the same finding twice in different words
7. Do not output analysis, notes, or commentary
8. Prefer exact counts, ratios, percentages, multipliers, and effect sizes
9. Keep the thread practical for creators who are much smaller than the source creator
10. Keep the final output thread-only
11. Do not mention source files, report names, or folder names
12. Do not claim the model "watched" or "read" anything unless the data clearly supports that phrasing
13. If the research does not support a dramatic claim, do not write one anyway
14. If the data is not strong enough for a hook format, pick a different one
15. The hook must earn the thread, not just bait it

---

## Quality Check

Before finalizing the thread, silently verify all of these:

- The output is exactly 9 posts
- Posts are separated only by a standalone em dash line (—)
- Posts 2-8 all include "{takeaway_label}:"
- Every chosen insight is backed by the Phase 1 data
- The hook comes from the Synthesizer Hook Bank and matches the data
- The thread reads like a Synthesizer, not a Storyteller or generic listicle
- The thread is easy to read on mobile
- The final post follows the adapted CTA pattern
- The output contains nothing except the finished thread
- Insight mix rules are satisfied (2+ counterintuitive, 1+ title, 1+ hook, 1+ structure)
- No two insights overlap
- Every post fits within the platform's character limit

---

## Thread Output

Save the clean thread to: `thread/final_thread.md`

After the thread body, create a separate file `thread/insights_audit.md` containing:
- The 7 chosen insights with the exact data point backing each
- 3-5 runner-up insights with their data points
- Brief note on why each runner-up was cut
