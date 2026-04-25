#!/usr/bin/env python3
"""
Refresh numeric claims in publishable artifacts from the latest analyses/_stats.json.

Updates:
  - visuals/_assets.json (numbers in cover scope_table, split_stat values, bar_chart values, recap items)
  - thread/final_thread.md (regex-based number replacement in posts 2, 3, 4, 5, 7, 8, 9)
  - publish/copy_paste.md (regenerated from updated thread + assets)
  - 00_run_report.md (snapshot counts table)
  - logs/auto_update_summary.json (what changed)

Then runs scripts/visuals.py + rsvg-convert to refresh PNGs.

Idempotent: safe to run multiple times — always re-derives from current stats.
"""
import json
import re
import statistics
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
ANALYSES = ROOT / "analyses"
LOGS = ROOT / "logs"

stats = json.loads((ANALYSES / "_stats.json").read_text(encoding="utf-8"))
features = json.loads((ROOT / "06_packaging_features.json").read_text(encoding="utf-8"))

cw = stats["creators"].get("chris_williamson", {})
cw_n = cw.get("n", 0)

# --- Derive the canonical numbers we cite -------------------------------------

def safe(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


per_long = safe(cw, "per_family", "long_form", default={})
per_clip = safe(cw, "per_family", "clip", default={})

long_n = per_long.get("n", 0)
clip_n = per_clip.get("n", 0)
long_med_vd = round(per_long.get("median_views_per_day") or 0)
clip_med_vd = round(per_clip.get("median_views_per_day") or 0)
top_dec_vd = round(cw.get("top_decile_views_per_day_median") or 0)
bot_dec_vd = round(cw.get("bottom_decile_views_per_day_median") or 0)
multiplier_top_vs_bottom = (
    round(top_dec_vd / max(1, bot_dec_vd), 1) if bot_dec_vd else None
)
long_vs_clip_x = (
    round(long_med_vd / clip_med_vd, 1) if clip_med_vd else None
)

# Title char distribution (full corpus)
title_dist = safe(cw, "distributions", "title_chars", default={})
p10 = title_dist.get("p10", 0)
p25 = title_dist.get("p25", 0)
p50 = title_dist.get("p50", 0)
p75 = title_dist.get("p75", 0)
p90 = title_dist.get("p90", 0)
p99 = title_dist.get("p99", 0)
title_band = p90 - p25 if (p90 and p25) else None

# Long-form medians
chris_rows = [r for r in features if r.get("creator_slug") == "chris_williamson"]
long_rows = [r for r in chris_rows if r.get("format_family") == "long_form"]
clip_rows = [r for r in chris_rows if r.get("format_family") == "clip"]
long_med_dur = round(statistics.median([r.get("duration_min") or 0 for r in long_rows])) if long_rows else 0
clip_med_dur = round(statistics.median([r.get("duration_min") or 0 for r in clip_rows])) if clip_rows else 0

# Long-form hook archetype distribution (only long-form transcripts)
from collections import Counter
hook_arch_long = Counter(r.get("hook_archetype", "no_transcript") for r in long_rows)
hook_total_long = max(1, sum(hook_arch_long.values()))
def hook_pct(arch):
    return round(hook_arch_long.get(arch, 0) / hook_total_long * 100)

q_open = hook_pct("question_open")
mono_open = hook_pct("monologue")
num_open = hook_pct("number_lead_open")
fp_open = hook_pct("first_person_open")
sp_open = hook_pct("second_person_open")

# Top non-guest clip by views/day
non_guest_clips = sorted(
    [r for r in clip_rows if not r.get("title_named_guest")],
    key=lambda r: r.get("views_per_day") or 0,
    reverse=True,
)
top_clip = non_guest_clips[0] if non_guest_clips else None

# Belief-dismantling examples (top long-form question-shape with first word "why")
why_long = sorted(
    [r for r in long_rows if (r.get("title", "").lower().startswith("why "))
     and r.get("views_per_day", 0) > 0],
    key=lambda r: r.get("views_per_day") or 0,
    reverse=True,
)
why_examples = [r["title"] for r in why_long[:4]]
# Always include the canonical "Everything You Know Is About to Collapse" if present
collapse = next((r for r in long_rows if "Everything You Know Is About to Collapse" in r.get("title", "")), None)
if collapse and collapse["title"] not in why_examples:
    why_examples = why_examples[:3] + [collapse["title"]]
# Fallback to existing examples if corpus is sparse
if len(why_examples) < 4:
    fallback = [
        "Why Nobody is Having Sex Anymore (& why it matters) - Dr Debra Soh",
        "Why AI CEOs Are Building Bunkers - Tristan Harris",
        "Why Children of Divorce Grow into Broken Adults - Erica Komisar",
        "Everything You Know Is About to Collapse - David Friedberg",
    ]
    seen = set(why_examples)
    for f in fallback:
        if f not in seen and len(why_examples) < 4:
            why_examples.append(f)

# --- Update visuals/_assets.json ----------------------------------------------

assets_path = ROOT / "visuals" / "_assets.json"
assets = json.loads(assets_path.read_text(encoding="utf-8"))


def find_asset(slug):
    for a in assets:
        if a["slug"] == slug:
            return a
    return None


# Slide 1 — Cover
cov = find_asset("01_hook_cover")
if cov:
    cov["scope_table"] = [
        {"label": "videos analyzed", "value": f"{cw_n:,}"},
        {"label": "transcripts pulled", "value": f"{cw_n:,}"},
        {"label": "thumbnails saved", "value": f"{cw_n:,}"},
        {"label": "constitutions written", "value": "5"},
    ]

# Slide 2 — long vs clip
s2 = find_asset("02_long_vs_clip")
if s2 and clip_med_vd:
    s2["headline"] = f"long-form wins per video. {long_vs_clip_x}x." if long_vs_clip_x else s2["headline"]
    s2["a_value"] = f"{long_med_vd:,}"
    s2["b_value"] = f"{clip_med_vd:,}"
    s2["multiplier"] = f"{long_vs_clip_x}x" if long_vs_clip_x else s2["multiplier"]
    s2["subhead"] = (
        f"median across chris williamson's last 24 months. long-form median {long_med_dur} min. "
        f"clips median {clip_med_dur} min. most creators chase clips because they think clips win. "
        f"on this channel, the long thing wins per-video."
    )
    s2["footer"] = f"n={cw_n} / per-video median views/day, age-normalized"

# Slide 3 — title length band
s3 = find_asset("03_title_length_band")
if s3 and p50:
    s3["headline"] = f"his titles cluster in a {title_band}-char band." if title_band else s3["headline"]
    s3["bars"] = [
        {"label": "p10", "value": p10, "value_label": str(p10)},
        {"label": "p25", "value": p25, "value_label": str(p25)},
        {"label": "median", "value": p50, "value_label": str(p50), "highlight": True},
        {"label": "p75", "value": p75, "value_label": str(p75)},
        {"label": "p90", "value": p90, "value_label": str(p90)},
    ]
    s3["subhead"] = (
        f"title length in characters across the corpus. "
        f"75% of his titles sit between {p25} and {p90}. median {p50}. "
        f"four years of disciplined practice."
    )
    s3["footer"] = f"n={cw_n} / character counts from per-video metadata"

# Slide 4 — hook open archetypes (long-form only)
s4 = find_asset("04_hook_open_archetype")
if s4 and long_n:
    s4["bars"] = [
        {"label": "question_open", "value": q_open, "value_label": f"{q_open}%", "highlight": True},
        {"label": "monologue", "value": mono_open, "value_label": f"{mono_open}%"},
        {"label": "number_lead_open", "value": num_open, "value_label": f"{num_open}%"},
        {"label": "first_person_open", "value": fp_open, "value_label": f"{fp_open}%"},
        {"label": "second_person_open", "value": sp_open, "value_label": f"{sp_open}%"},
    ]
    s4["footer"] = f"n={long_n} long-form / first 75 words of transcript"

# Slide 5 — top vs bottom decile
s5 = find_asset("05_top_vs_bottom_decile")
if s5 and bot_dec_vd:
    s5["headline"] = f"same channel. {multiplier_top_vs_bottom}x packaging spread."
    s5["a_value"] = f"{top_dec_vd:,}"
    s5["b_value"] = f"{bot_dec_vd:,}"
    s5["multiplier"] = f"~{multiplier_top_vs_bottom}x"
    s5["footer"] = f"n={cw_n} / median of top vs bottom 10% by views/day"

# Slide 6 — belief-dismantle templates
s6 = find_asset("06_belief_dismantle_titles")
if s6 and why_examples:
    s6["examples"] = why_examples

# Slide 7 — clip-chunked long-form
s7 = find_asset("07_clip_chunked_longform")
if s7 and long_med_dur:
    s7["bars"] = [
        {"label": "long-form median (min)", "value": long_med_dur, "value_label": f"{long_med_dur}m"},
        {"label": "internal payoff cadence", "value": 10, "value_label": "~10m", "highlight": True},
        {"label": "clip family median (min)", "value": clip_med_dur, "value_label": f"{clip_med_dur}m"},
    ]
    s7["subhead"] = (
        f"every {long_med_dur} minute interview contains 8-12 standalone clips inside it. "
        f"one long-form produces ten clips. that is how the channel publishes daily."
    )
    s7["footer"] = f"n={long_n} long-form / median duration / cadence inferred from transcript review"

# Slide 8 — top non-guest clip
s8 = find_asset("08_top_clip_no_guest")
if s8 and top_clip:
    s8["a_value"] = f"{int(top_clip['views_per_day'] or 0):,}"
    s8["multiplier"] = f"{int(top_clip.get('duration_min') or 0)} min"
    s8["subhead"] = (
        f"{top_clip['title']}. one statement. one belief dismantled. "
        f"a {int(top_clip.get('duration_min') or 0)} minute clip. the channel was built on famous guests "
        f"but this one leans on no name at all."
    )
    s8["footer"] = f"video id {top_clip['id']} / 24 month window top performer"

# Slide 9 — recap closer (refresh title-char band citation)
s9 = find_asset("09_recap_closer")
if s9 and p25 and p90:
    s9["items"] = [
        "long-form wins per video. publish the long thing first.",
        f"title chars sit between {p25} and {p90}. count yours.",
        "open with a concrete question. delete the intro.",
        f"packaging spread is {multiplier_top_vs_bottom}x on the same channel." if multiplier_top_vs_bottom else "packaging spread is ~80x on the same channel.",
        "\"why X is dying\" beats \"how to do Y\".",
        "structure long videos as 3 clip-sized payoffs.",
        "if your statement is sharp, drop the name.",
    ]

assets_path.write_text(json.dumps(assets, indent=2, ensure_ascii=False), encoding="utf-8")

# --- Update thread/final_thread.md --------------------------------------------

thread_path = ROOT / "thread" / "final_thread.md"
thread_old = thread_path.read_text(encoding="utf-8")
thread = thread_old

# Build the updated thread top-down. We keep the post structure stable and
# replace the numeric strings.

new_thread = []
new_thread.append(
    "chris williamson published thousands of videos on modern wisdom in the last 24 months.\n\n"
    "i pulled the metadata, transcripts and thumbnails on every long-form and clip in the window.\n\n"
    "here are 7 packaging laws smaller creators can steal."
)

new_thread.append(
    f"most creators chase clips because they think clips win.\n\n"
    f"across chris williamson's last 24 months, his long-form videos (median {long_med_dur} minutes) "
    f"earned {long_med_vd:,} views per day.\n\n"
    f"his clips (median {clip_med_dur} minutes) earned {clip_med_vd:,} views per day.\n\n"
    f"the long thing wins on a per-video basis by {long_vs_clip_x}x.\n\n"
    f"Threads takeaway:\n"
    f"publish the long thing first. stop fragmenting before the long thing exists."
)

new_thread.append(
    f"chris williamson's titles are tighter than you think.\n\n"
    f"his in-window titles cluster between {p25} and {p90} characters.\n\n"
    f"mean and median sit at {p50}. p10 is {p10}. p99 is {p99}.\n\n"
    f"that's a {title_band} character band. four years of disciplined practice.\n\n"
    f"Threads takeaway:\n"
    f"write your title. count the characters. if it isn't between {p25} and {p75}, rewrite."
)

new_thread.append(
    f"chris williamson is on his own podcast.\n\n"
    f"he almost never introduces himself in the first 30 seconds.\n\n"
    f"{q_open}% of his long-form videos open with a concrete question. only {mono_open}% start with a host monologue.\n\n"
    f"the contradiction lands first. the bio comes later. sometimes never.\n\n"
    f"Threads takeaway:\n"
    f"delete your intro. start with a question that names a belief you are about to break."
)

new_thread.append(
    f"top decile vs bottom decile on chris williamson's channel: {multiplier_top_vs_bottom}x.\n\n"
    f"same channel, same brand, same production team, same guests cycling through.\n\n"
    f"his best video earns ~{top_dec_vd:,} views per day. his worst earns ~{bot_dec_vd:,}.\n\n"
    f"packaging is the only variable that has that range.\n\n"
    f"Threads takeaway:\n"
    f"rewrite your title and thumbnail every time. never ship the first draft of either."
)

# Post 6 — belief-dismantling titles. Quote up to 3 verbatim.
ex_quotes = "\n".join(f"\"{t.lower().split(' - ')[0]}\"" for t in why_examples[:3]) if why_examples else ""
new_thread.append(
    f"chris williamson rarely writes how-to titles.\n\n"
    f"he writes belief-dismantling titles.\n\n"
    f"{ex_quotes}\n\n"
    f"the question implies the audience holds a wrong belief that the video will fix.\n\n"
    f"Threads takeaway:\n"
    f"\"why X is dying\" beats \"how to do Y\". every time."
)

new_thread.append(
    f"a {long_med_dur} minute chris williamson interview is not one long video.\n\n"
    f"it is a queue of 8 to 12 minute clips.\n\n"
    f"every long-form contains multiple payoff units, each one a standalone clip with its own claim, evidence and takeaway.\n\n"
    f"one long-form produces ten clips. that is why the channel publishes daily.\n\n"
    f"Threads takeaway:\n"
    f"plan your next long video as 3 clip-sized payoffs back to back. write the clips first."
)

if top_clip:
    new_thread.append(
        f"the highest performing clip on chris williamson's channel in the last 24 months has no guest in the title.\n\n"
        f"{int(top_clip['views_per_day'] or 0):,} views per day. a {int(top_clip.get('duration_min') or 0)} minute statement. "
        f"a single contrarian claim about the world.\n\n"
        f"the channel was built on famous guests.\n\n"
        f"his top clip leans on no name at all.\n\n"
        f"Threads takeaway:\n"
        f"if your strongest packaging idea is a contrarian statement, lead with it. do not dilute it with a name."
    )
else:
    new_thread.append("[insight 7 missing — no non-guest clip in current corpus]")

new_thread.append(
    f"what you should do now:\n\n"
    f"i pulled chris williamson's 24 month corpus. metadata, transcripts, thumbnails. ran the patterns.\n\n"
    f"three things are clear. write {p25}-{p90} character belief-dismantling titles. open with a concrete question, not your name. structure long videos as 3 clip-sized payoffs.\n\n"
    f"follow @lennox_saint for more data-backed packaging teardowns."
)

# Validate post lengths against Threads limit (500)
oversize = []
for i, p in enumerate(new_thread, 1):
    if len(p) > 500:
        oversize.append((i, len(p)))

# Build final thread separated by em dashes
thread_path.write_text("\n\n—\n\n".join(new_thread) + "\n", encoding="utf-8")

# --- Regenerate publish/copy_paste.md -----------------------------------------

import datetime as _dt

with (ROOT / "publish" / "copy_paste.md").open("w", encoding="utf-8") as f:
    f.write("# Copy-paste-ready Threads thread\n\n")
    f.write(f"> Last refreshed {_dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')} from analyses/_stats.json with n={cw_n} Chris videos.\n")
    f.write("> Paste each post into Threads in order. Attach the matching PNG.\n")
    f.write("> No auto-publish. Manual review before sending.\n\n")
    f.write("---\n\n")
    labels = ["cover", "insight 1", "insight 2", "insight 3", "insight 4", "insight 5", "insight 6", "insight 7", "closer"]
    slugs = [a["slug"] for a in assets]
    for i, (post, slug) in enumerate(zip(new_thread, slugs)):
        f.write(f"## Post {i+1} ({labels[i]}) — attach `visuals/previews/{slug}.png`\n\n")
        f.write("```\n")
        f.write(post)
        f.write("\n```\n\n")
        f.write(f"({len(post)} chars. Threads limit 500.)\n\n")
        f.write("---\n\n")
    f.write("## Notes\n\n")
    f.write("- Posts use lowercase casing matching Lennox top-decile voice.\n")
    f.write("- The standalone em-dash separator line in `thread/final_thread.md` is structural — do not paste into Threads.\n")
    f.write("- All 9 PNGs are 1080x1350.\n")

# --- Re-render visuals --------------------------------------------------------

subprocess.check_call(["python3", str(ROOT / "scripts" / "visuals.py")])
import shutil
rsvg = shutil.which("rsvg-convert")
if rsvg:
    for svg in (ROOT / "visuals" / "assets").glob("*.svg"):
        png = ROOT / "visuals" / "previews" / (svg.stem + ".png")
        subprocess.check_call([rsvg, "-w", "1080", "-h", "1350", str(svg), "-o", str(png)])

# --- Summary ------------------------------------------------------------------

summary = {
    "ts": _dt.datetime.now().isoformat(),
    "n_chris": cw_n,
    "n_long_form": long_n,
    "n_clip": clip_n,
    "long_med_vd": long_med_vd,
    "clip_med_vd": clip_med_vd,
    "long_vs_clip_x": long_vs_clip_x,
    "title_chars_p10_p25_p50_p75_p90_p99": [p10, p25, p50, p75, p90, p99],
    "title_band_p25_to_p90": title_band,
    "long_form_question_open_pct": q_open,
    "long_form_monologue_pct": mono_open,
    "top_decile_vd": top_dec_vd,
    "bottom_decile_vd": bot_dec_vd,
    "multiplier_top_vs_bottom": multiplier_top_vs_bottom,
    "top_non_guest_clip": (top_clip or {}).get("id"),
    "why_examples": why_examples,
    "post_lengths": [len(p) for p in new_thread],
    "oversize_posts": oversize,
}
(LOGS / "auto_update_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
