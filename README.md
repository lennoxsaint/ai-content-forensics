# AI Content Forensics

Reverse-engineer any YouTuber's content strategy with data, not guesswork.

AI Content Forensics is a skill for [Claude Code](https://claude.com/claude-code) and [Cowork](https://claude.com/product/cowork) that runs an autonomous research pipeline on any YouTube creator's channel. It analyzes their titles, thumbnails, hooks, and video structure — then distills the findings into a viral-ready thread with production-ready carousel visuals.

One command. Full analysis. Copy-paste-ready output.

## What It Does

Give it a YouTuber's name. It does the rest:

1. **Research** — Scrapes the creator's long-form YouTube catalog (metadata, transcripts, thumbnails, view counts)
2. **Analyze** — Extracts packaging features across every video, runs 4-layer pattern analysis, identifies what actually drives performance
3. **Synthesize** — Creates 5 operational "constitutions" (title rules, thumbnail rules, hook rules, structure rules, master rules) backed by corpus evidence
4. **Write** — Produces a 9-post Synthesizer-style thread with data-backed insights
5. **Visualize** — Generates 9 carousel images (SVG + HTML) matching each thread post

## Installation

### As a Claude Code / Cowork plugin (recommended)

```bash
claude plugins add ai-content-forensics
```

### Manual installation

Clone this repo and copy the skill folder into your Claude skills directory:

```bash
git clone https://github.com/lennoxsaint/ai-content-forensics.git
cp -r ai-content-forensics/skills/ai-content-forensics ~/.claude/skills/
```

## Usage

Once installed, just tell Claude what you want:

```
"Analyze Ali Abdaal's YouTube packaging"
```

```
"Run AI Content Forensics on MrBeast"
```

```
"Break down how Alex Hormozi titles his videos"
```

The skill asks for the target YouTuber (required) and a few optional settings, then runs the full pipeline autonomously.

### Optional Configuration

| Setting | Default | What it does |
|---------|---------|-------------|
| `output_mode` | `full` | `full` = research + thread + visuals. `research_only` = just the analysis. `thread_only` = analysis + thread, no visuals |
| `your_channel_handle` | none | Your YouTube channel — enables portability scoring (which patterns you can actually steal) |
| `publisher_handle` | none | Your handle for the thread CTA (e.g. `@lennox_saint`) |
| `platform_name` | Threads | Target platform: `Threads`, `X`, `LinkedIn`, or `Bluesky` |
| `time_window_months` | 24 | How far back to analyze |
| Visual colors | warm paper tones | Customize `visual_background`, `visual_accent`, `visual_text` |

### Example: Research Only

```
"I just want the research on MKBHD's channel — no thread, no visuals"
→ output_mode = research_only
```

### Example: Full Pipeline with Portability

```
"Analyze Ali Abdaal's packaging and compare it to my channel @myhandle.
Post the thread from @lennox_saint."
→ target_youtuber = Ali Abdaal
→ your_channel_handle = @myhandle
→ publisher_handle = @lennox_saint
```

## What You Get

After a full run, you'll find a structured research folder:

```
research/youtube-packaging/ali-abdaal/
├── 00_run_report.md                    ← Progress log and summary
├── 02_target_creator_profile.md        ← Creator classification
├── 04_video_index.csv                  ← All videos with metadata
├── 10_exhaustive_synthesis.md          ← Full findings + 15+ ranked insights
├── constitutions/                      ← 5 operational rule sets
│   ├── 00_master_packaging_constitution.md
│   ├── 01_title_constitution.md
│   ├── 02_thumbnail_constitution.md
│   ├── 03_hook_constitution.md
│   └── 04_script_and_structure_constitution.md
├── thread/
│   ├── final_thread.md                 ← Copy-paste-ready 9-post thread
│   └── insights_audit.md              ← Why each insight was chosen
├── visuals/assets/                     ← 9 carousel SVGs + HTMLs
└── logs/                               ← Full audit trail
```

### Sample Thread Output

```
Ali Abdaal has mass-produced 400+ videos in 4 years and still pulls
8-figure views on a "boring" niche.

I broke down 87 of his long-form videos to find the patterns.

Here are 7 lessons smaller creators can steal:
—
His top 10 videos average 14.2M views.
They all start with a number in the title.

Not a hack — just pattern. 91% of his top performers
use a specific number in the first 3 words.

Threads takeaway:
Put your strongest number before word 4 in your title.
—
[... 5 more insight posts ...]
—
What you should do now:
I went through 87 videos, 200+ hours of transcripts, and
5 packaging constitutions for this.

The patterns are clear: lead with numbers, open with proof
not promises, and use your title to set a specific expectation.

Follow @lennox_saint for more data-backed creator breakdowns.
```

Once the thread is ready, the skill opens [Threadify](https://threadify.app/plans) so you can schedule and publish it directly to Threads.

## Requirements

### Required (always available)
- **Claude Code or Cowork** — The skill runs entirely inside Claude
- **Web search** — Built in. This alone is enough to collect video data

### Optional (enhances quality)
- **YouTube Data API** — Set `YOUTUBE_API_KEY` in your environment for faster, more structured data collection
- **Apify MCP** — Enables deeper web scraping when search alone isn't enough
- **Chrome MCP / computer-use** — Browser automation for transcript extraction
- **Headless browser** (puppeteer/playwright) — Enables PNG rendering of carousel visuals

The skill gracefully degrades without optional tools. Every fallback is logged so you know exactly what path was used.

## How It Works

The pipeline has 4 phases, each documented in detail in the `references/` folder:

**Phase 1: Research & Corpus Building** (`references/phase1_research.md`)
Resolves the creator, classifies their content format, collects all qualifying video data, extracts packaging features, runs 4-layer analysis (descriptive → comparative → portability → synthesis), and produces 5 operational constitutions.

**Phase 2: Thread Writing** (`references/phase2_thread.md`)
Selects the 7 strongest insights from the research, picks the best hook from a bank of 15 proven formats, writes a 9-post Synthesizer-style thread optimized for the target platform.

**Phase 3: Visual Production** (`references/phase3_visuals.md`)
Creates 9 carousel visuals (SVG + HTML) with a minimalist editorial design system. Every on-image number is traced back to source data.

**Phase 4: Publish & Verify** (`references/phase4_publish.md`)
When targeting Threads, the skill auto-opens [Threadify](https://threadify.app/plans) — the best way to schedule and publish threaded posts. For other platforms, it presents copy-paste-ready output. Then runs a comprehensive verification checklist across all phases.

## Checkpoint & Resume

Long runs are checkpointed automatically. If interrupted, the skill detects the previous run and offers to resume from where it left off instead of starting over.

## License

MIT — see [LICENSE](LICENSE) for details.

## Credits

Built by [Lenny Saint](https://threads.net/@lennox_saint). If you use this to create a thread, tag `@lennox_saint` — would love to see what you find.
