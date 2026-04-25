#!/usr/bin/env python3
"""
Carousel visual generator for Phase 3.

Reads:    visuals/_assets.json   (manually curated by Phase 3 author)
Writes:   visuals/assets/*.svg
          visuals/assets/*.html
          visuals/assets/*.png   (best effort via headless Chrome if available)

Each asset entry in visuals/_assets.json:
{
  "slug": "01_hook_cover",
  "archetype": "hook_cover",
  "post_index": 1,
  "lead_number": "108,695",
  "lead_caption": "views in 24 hours",
  "headline": "i analyzed 1,997 chris williamson videos.",
  "subhead": "here are 7 packaging laws that smaller creators can steal.",
  "scope_table": [
    {"label": "videos", "value": "1,997"},
    {"label": "transcripts", "value": "1,994"},
    {"label": "thumbnails", "value": "1,997"},
    {"label": "constitutions", "value": "5"}
  ],
  "footer": "modern wisdom corpus / apr 2024 - apr 2026"
}
"""
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent.parent
VIS = ROOT / "visuals"
ASSETS = VIS / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
PNG_DIR = VIS / "previews"
PNG_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
BG = "#f7f4ee"
FG = "#111111"
ACCENT = "#8f1d1d"
NEUTRAL = "#7a7a7a"

FONT_STACK = "'Inter', 'system-ui', '-apple-system', 'Segoe UI', sans-serif"


def svg_open():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n  <rect width="100%" height="100%" fill="{BG}"/>\n'


def svg_close():
    return "</svg>\n"


def text_el(x, y, text, size=48, weight=400, color=FG, anchor="start", letter_spacing=0):
    safe = (text.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;"))
    return (
        f'  <text x="{x}" y="{y}" font-family="{FONT_STACK}" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}" '
        f'text-anchor="{anchor}" letter-spacing="{letter_spacing}">{safe}</text>\n'
    )


def rule(y, x1=80, x2=W-80, color=NEUTRAL, w=1):
    return f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="{w}"/>\n'


def wrap_text_lines(text, max_chars):
    return textwrap.wrap(text, width=max_chars, break_long_words=False)


# ------- Archetype renderers --------------------------------------------------

def render_hook_cover(a: dict) -> tuple[str, str]:
    headline = a.get("headline", "")
    subhead = a.get("subhead", "")
    lead_num = a.get("lead_number", "")
    lead_cap = a.get("lead_caption", "")
    scope = a.get("scope_table", [])
    footer = a.get("footer", "")

    s = svg_open()
    # corpus dossier label
    s += text_el(80, 110, "CORPUS FORENSICS", size=22, weight=600, color=ACCENT, letter_spacing=4)
    s += rule(140, 80, 280, NEUTRAL, 2)
    # headline
    head_lines = wrap_text_lines(headline, 24)
    y = 220
    for line in head_lines[:3]:
        s += text_el(80, y, line, size=82, weight=700)
        y += 96
    # subhead
    sub_lines = wrap_text_lines(subhead, 38)
    y += 30
    for line in sub_lines[:3]:
        s += text_el(80, y, line, size=44, weight=400, color=NEUTRAL)
        y += 56
    # scope table - one row per item, label-left value-right (avoids cramped 4-column horizontal)
    if scope:
        y += 60
        s += rule(y, 80, W-80, FG, 1)
        y += 60
        for item in scope:
            s += text_el(80, y, item["label"], size=32, weight=400, color=NEUTRAL,
                         anchor="start", letter_spacing=1)
            s += text_el(W-80, y, item["value"], size=56, weight=700, anchor="end",
                         color=FG)
            y += 70
            s += rule(y - 30, 80, W-80, NEUTRAL, 1)
        y += 20
    # lead number (optional, if no scope)
    if lead_num and not scope:
        y += 60
        s += text_el(W/2, y+20, lead_num, size=200, weight=800, anchor="middle", color=ACCENT)
        s += text_el(W/2, y+90, lead_cap, size=32, weight=400, anchor="middle", color=NEUTRAL)
    # footer
    s += text_el(80, H-80, footer, size=22, weight=400, color=NEUTRAL, letter_spacing=2)
    s += svg_close()
    h = wrap_html(s)
    return s, h


def render_split_stat(a: dict) -> tuple[str, str]:
    """Two big stats with vs/contrast in middle."""
    headline = a.get("headline", "")
    subhead = a.get("subhead", "")
    a_label = a.get("a_label", "top decile")
    a_value = a.get("a_value", "")
    b_label = a.get("b_label", "bottom decile")
    b_value = a.get("b_value", "")
    multiplier = a.get("multiplier", "")
    footer = a.get("footer", "")

    s = svg_open()
    # post number badge
    s += text_el(80, 110, f"INSIGHT {a.get('post_index','')}", size=22, weight=600,
                 color=ACCENT, letter_spacing=4)
    s += rule(140, 80, 280, NEUTRAL, 2)
    # headline
    head_lines = wrap_text_lines(headline, 26)
    y = 220
    for line in head_lines[:3]:
        s += text_el(80, y, line, size=68, weight=700)
        y += 82
    y += 30
    # Stack vertically: a_value, then label below, then multiplier rule, then b_value, then label
    # Top accent value
    s += text_el(W/2, y + 130, a_value, size=160, weight=800,
                 anchor="middle", color=ACCENT)
    s += text_el(W/2, y + 200, a_label, size=28, weight=500,
                 anchor="middle", color=NEUTRAL, letter_spacing=2)
    # Multiplier band
    mid_y = y + 270
    s += rule(mid_y, 80, W/2 - 80, NEUTRAL, 1)
    s += text_el(W/2, mid_y + 14, multiplier, size=56, weight=700,
                 anchor="middle", color=FG)
    s += rule(mid_y, W/2 + 80, W-80, NEUTRAL, 1)
    # Bottom neutral value
    s += text_el(W/2, mid_y + 170, b_value, size=160, weight=800,
                 anchor="middle", color=NEUTRAL)
    s += text_el(W/2, mid_y + 240, b_label, size=28, weight=500,
                 anchor="middle", color=NEUTRAL, letter_spacing=2)
    y = mid_y + 290
    s += rule(y, 80, W-80, NEUTRAL, 1)
    y += 50
    sub_lines = wrap_text_lines(subhead, 40)
    for line in sub_lines[:5]:
        s += text_el(80, y, line, size=32, weight=400)
        y += 42
    s += text_el(80, H-80, footer, size=22, weight=400, color=NEUTRAL, letter_spacing=2)
    s += svg_close()
    return s, wrap_html(s)


def render_bar_chart(a: dict) -> tuple[str, str]:
    """Sorted bar chart for rankings (top archetypes etc)."""
    headline = a.get("headline", "")
    subhead = a.get("subhead", "")
    bars = a.get("bars", [])  # list of {label, value, highlight?}
    footer = a.get("footer", "")

    s = svg_open()
    s += text_el(80, 110, f"INSIGHT {a.get('post_index','')}", size=22, weight=600,
                 color=ACCENT, letter_spacing=4)
    s += rule(140, 80, 280, NEUTRAL, 2)
    head_lines = wrap_text_lines(headline, 26)
    y = 220
    for line in head_lines[:3]:
        s += text_el(80, y, line, size=68, weight=700)
        y += 82
    y += 40
    # chart
    if bars:
        max_v = max(b["value"] for b in bars)
        chart_x = 380
        chart_w = W - 80 - chart_x
        bar_h = 50
        gap = 30
        for i, b in enumerate(bars):
            by = y + i*(bar_h+gap)
            color = ACCENT if b.get("highlight") else FG
            s += text_el(chart_x - 20, by + bar_h*0.7, b["label"], size=28, weight=500,
                         anchor="end")
            bar_len = chart_w * (b["value"] / max_v)
            s += f'  <rect x="{chart_x}" y="{by}" width="{bar_len}" height="{bar_h}" fill="{color}"/>\n'
            label = b.get("value_label", str(b["value"]))
            s += text_el(chart_x + bar_len + 12, by + bar_h*0.7, label, size=26,
                         weight=600, color=color)
        y += len(bars)*(bar_h+gap) + 40
    s += rule(y, 80, W-80, NEUTRAL, 1)
    y += 40
    sub_lines = wrap_text_lines(subhead, 40)
    for line in sub_lines[:5]:
        s += text_el(80, y, line, size=30, weight=400)
        y += 40
    s += text_el(80, H-80, footer, size=22, weight=400, color=NEUTRAL, letter_spacing=2)
    s += svg_close()
    return s, wrap_html(s)


def render_template_card(a: dict) -> tuple[str, str]:
    """Title formula / template card with 3-5 corpus exemplars."""
    headline = a.get("headline", "")
    subhead = a.get("subhead", "")
    formula = a.get("formula", "")
    examples = a.get("examples", [])
    footer = a.get("footer", "")

    s = svg_open()
    s += text_el(80, 110, f"INSIGHT {a.get('post_index','')}", size=22, weight=600,
                 color=ACCENT, letter_spacing=4)
    s += rule(140, 80, 280, NEUTRAL, 2)
    head_lines = wrap_text_lines(headline, 26)
    y = 220
    for line in head_lines[:3]:
        s += text_el(80, y, line, size=68, weight=700)
        y += 82
    y += 30
    # formula card
    s += f'  <rect x="80" y="{y}" width="{W-160}" height="120" fill="white" stroke="{FG}" stroke-width="2"/>\n'
    s += text_el(W/2, y+50, "formula", size=20, weight=500, color=NEUTRAL,
                 anchor="middle", letter_spacing=4)
    s += text_el(W/2, y+95, formula, size=44, weight=700, anchor="middle", color=ACCENT)
    y += 160
    # examples
    s += text_el(80, y, "exact corpus examples:", size=24, weight=600,
                 color=NEUTRAL, letter_spacing=2)
    y += 40
    for i, ex in enumerate(examples[:5]):
        s += f'  <rect x="80" y="{y}" width="6" height="60" fill="{ACCENT}"/>\n'
        ex_lines = wrap_text_lines(ex, 60)
        for j, ln in enumerate(ex_lines[:2]):
            s += text_el(110, y + 26 + j*30, ln, size=24, weight=500)
        y += 80
    s += rule(y, 80, W-80, NEUTRAL, 1)
    y += 30
    sub_lines = wrap_text_lines(subhead, 40)
    for line in sub_lines[:3]:
        s += text_el(80, y+20, line, size=26, weight=400, color=NEUTRAL)
        y += 36
    s += text_el(80, H-80, footer, size=22, weight=400, color=NEUTRAL, letter_spacing=2)
    s += svg_close()
    return s, wrap_html(s)


def render_recap_closer(a: dict) -> tuple[str, str]:
    headline = a.get("headline", "")
    cta = a.get("cta", "")
    items = a.get("items", [])
    footer = a.get("footer", "")
    publisher = a.get("publisher", "")

    s = svg_open()
    s += text_el(80, 110, "RECAP", size=22, weight=600, color=ACCENT, letter_spacing=4)
    s += rule(140, 80, 280, NEUTRAL, 2)
    head_lines = wrap_text_lines(headline, 28)
    y = 220
    for line in head_lines[:2]:
        s += text_el(80, y, line, size=72, weight=700)
        y += 86
    y += 40
    for i, it in enumerate(items[:7]):
        # checkbox
        s += f'  <rect x="80" y="{y-30}" width="36" height="36" fill="none" stroke="{FG}" stroke-width="2"/>\n'
        s += text_el(98, y-3, "✓", size=30, weight=700, anchor="middle", color=ACCENT)
        # text
        ln = wrap_text_lines(it, 44)
        for j, l in enumerate(ln[:2]):
            s += text_el(140, y + j*36, l, size=30, weight=500)
        y += max(60, len(ln)*36 + 20)
    y = max(y, H - 250)
    s += rule(y, 80, W-80, NEUTRAL, 1)
    y += 50
    s += text_el(80, y, cta, size=32, weight=500)
    if publisher:
        s += text_el(80, y+50, publisher, size=42, weight=700, color=ACCENT)
    s += text_el(80, H-80, footer, size=22, weight=400, color=NEUTRAL, letter_spacing=2)
    s += svg_close()
    return s, wrap_html(s)


def wrap_html(svg_str: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
  <title>visual</title>
  <style>
    html,body {{ margin:0; padding:0; background:#222; }}
    .frame {{ display:flex; align-items:center; justify-content:center; min-height:100vh; }}
    svg {{ display:block; max-width:100%; height:auto; box-shadow:0 8px 30px rgba(0,0,0,0.3); }}
  </style>
</head>
<body><div class=\"frame\">{svg_str}</div></body>
</html>
"""


RENDERERS = {
    "hook_cover": render_hook_cover,
    "split_stat": render_split_stat,
    "bar_chart": render_bar_chart,
    "template_card": render_template_card,
    "recap_closer": render_recap_closer,
}


def main():
    spec_path = VIS / "_assets.json"
    if not spec_path.exists():
        print(f"Need {spec_path} (Phase 3 author writes this).")
        return
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for asset in spec:
        slug = asset["slug"]
        archetype = asset["archetype"]
        renderer = RENDERERS.get(archetype)
        if not renderer:
            print(f"WARN unknown archetype {archetype} for {slug}, skipping")
            continue
        svg, html = renderer(asset)
        (ASSETS / f"{slug}.svg").write_text(svg, encoding="utf-8")
        (ASSETS / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"wrote {slug}.svg + {slug}.html")


if __name__ == "__main__":
    main()
