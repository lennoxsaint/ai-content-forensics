#!/usr/bin/env python3
"""
Compute corpus-level statistics for the analysis layer.

Reads:    06_packaging_features.json
Writes:   analyses/_stats.json   (machine-readable)
          analyses/_stats.md     (human-readable summary)

Statistics produced:
  - Per-family counts, view distributions, like/comment ratios
  - Title feature prevalence (overall + per family)
  - Title archetype distribution
  - Hook archetype distribution
  - Top-decile vs bottom-decile feature comparison (by views_per_day)
  - Per-family top-decile vs bottom-decile
  - Guest analysis (Chris): videos with named guest vs without
  - Chris vs Lennox feature comparison (portability source)
  - Top-N exemplar videos per archetype/feature
"""
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSES = ROOT / "analyses"
ANALYSES.mkdir(parents=True, exist_ok=True)


def median(seq):
    seq = [x for x in seq if x is not None]
    return statistics.median(seq) if seq else 0


def percentiles(seq, ps=(0.1, 0.25, 0.5, 0.75, 0.9, 0.99)):
    seq = sorted(x for x in seq if x is not None)
    if not seq:
        return {f"p{int(p*100)}": 0 for p in ps}
    return {f"p{int(p*100)}": seq[min(len(seq)-1, int(len(seq)*p))] for p in ps}


def split_top_bottom(rows, key="views_per_day", decile=0.1):
    rows = sorted([r for r in rows if r.get(key) is not None],
                  key=lambda r: r[key], reverse=True)
    n = len(rows)
    cut = max(1, int(n * decile))
    return rows[:cut], rows[-cut:]


def feature_prevalence(rows, feature):
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get(feature)) / len(rows)


def feature_diff(top, bottom, feature):
    a = feature_prevalence(top, feature)
    b = feature_prevalence(bottom, feature)
    return {"top_pct": round(a, 4), "bottom_pct": round(b, 4),
            "diff": round(a - b, 4),
            "ratio": round(a / b, 2) if b > 0 else None}


def main():
    rows = json.loads((ROOT / "06_packaging_features.json").read_text(encoding="utf-8"))

    by_creator = defaultdict(list)
    for r in rows:
        by_creator[r["creator_slug"]].append(r)

    stats = {"total_rows": len(rows), "creators": {}}

    BOOL_FEATURES = [
        "title_has_number", "title_has_question", "title_has_quoted",
        "title_has_parens", "title_has_dash", "title_has_pipe",
        "title_has_colon", "title_has_emoji", "title_has_caps_word",
        "title_has_hashtag", "title_has_percent", "title_has_dollar",
        "title_has_year", "hook_question", "hook_number",
        "desc_has_link", "desc_has_chapters",
    ]

    for creator, crows in by_creator.items():
        cstat = {"n": len(crows)}
        # Per-family breakdown
        families = defaultdict(list)
        for r in crows:
            families[r["format_family"]].append(r)

        cstat["family_counts"] = {f: len(v) for f, v in families.items()}
        cstat["total_views"] = sum(r["view_count"] or 0 for r in crows)
        cstat["total_likes"] = sum(r["like_count"] or 0 for r in crows)
        cstat["total_comments"] = sum(r["comment_count"] or 0 for r in crows)
        cstat["total_transcript_words"] = sum(r["transcript_words"] or 0 for r in crows)
        cstat["videos_with_transcript"] = sum(1 for r in crows if r["has_transcript"])

        # Distribution per metric
        cstat["distributions"] = {
            "view_count": percentiles([r["view_count"] for r in crows if r["view_count"]]),
            "views_per_day": percentiles([r["views_per_day"] for r in crows if r["views_per_day"]]),
            "duration_min": percentiles([r["duration_min"] for r in crows]),
            "title_chars": percentiles([r["title_chars"] for r in crows]),
            "title_words": percentiles([r["title_words"] for r in crows]),
            "transcript_words": percentiles([r["transcript_words"] for r in crows if r["transcript_words"]]),
            "like_to_view": percentiles([r["like_to_view"] for r in crows if r["like_to_view"]]),
        }

        # Title archetype distribution
        cstat["title_archetypes"] = dict(
            Counter(r["title_archetype"] for r in crows).most_common()
        )
        cstat["hook_archetypes"] = dict(
            Counter(r["hook_archetype"] for r in crows).most_common()
        )
        cstat["title_first_words"] = dict(
            Counter(r["title_first_word"] for r in crows).most_common(20)
        )
        cstat["hook_first_words"] = dict(
            Counter(r["hook_first_word"] for r in crows).most_common(20)
        )
        cstat["title_triggers_count"] = dict(
            Counter(t for r in crows for t in (r["title_triggers"].split("|") if r["title_triggers"] else [])).most_common()
        )

        # Boolean feature prevalence
        cstat["feature_prevalence"] = {
            f: round(feature_prevalence(crows, f), 4) for f in BOOL_FEATURES
        }

        # Guest analysis
        cstat["with_named_guest"] = sum(1 for r in crows if r.get("title_named_guest"))
        cstat["pct_with_guest"] = round(cstat["with_named_guest"] / len(crows), 4) if crows else 0
        cstat["top_guests"] = dict(
            Counter(r["title_named_guest"] for r in crows if r["title_named_guest"]).most_common(20)
        )

        # Top-decile vs bottom-decile (views_per_day)
        top, bottom = split_top_bottom(crows, "views_per_day", decile=0.10)
        cstat["top_decile_n"] = len(top)
        cstat["bottom_decile_n"] = len(bottom)
        cstat["top_decile_views_per_day_median"] = round(median([r["views_per_day"] for r in top]), 1)
        cstat["bottom_decile_views_per_day_median"] = round(median([r["views_per_day"] for r in bottom]), 1)
        if cstat["bottom_decile_views_per_day_median"]:
            cstat["top_vs_bottom_multiplier"] = round(
                cstat["top_decile_views_per_day_median"] /
                cstat["bottom_decile_views_per_day_median"], 1)
        else:
            cstat["top_vs_bottom_multiplier"] = None

        cstat["top_vs_bottom_features"] = {
            f: feature_diff(top, bottom, f) for f in BOOL_FEATURES
        }
        cstat["top_vs_bottom_archetypes"] = {
            "top": dict(Counter(r["title_archetype"] for r in top).most_common()),
            "bottom": dict(Counter(r["title_archetype"] for r in bottom).most_common()),
        }
        cstat["top_vs_bottom_hook"] = {
            "top": dict(Counter(r["hook_archetype"] for r in top).most_common()),
            "bottom": dict(Counter(r["hook_archetype"] for r in bottom).most_common()),
        }
        cstat["top_decile_titles"] = [
            {"id": r["id"], "title": r["title"], "views_per_day": r["views_per_day"],
             "view_count": r["view_count"], "duration_min": r["duration_min"],
             "title_archetype": r["title_archetype"], "named_guest": r.get("title_named_guest"),
             "format_family": r["format_family"]}
            for r in top
        ]
        cstat["bottom_decile_titles"] = [
            {"id": r["id"], "title": r["title"], "views_per_day": r["views_per_day"],
             "view_count": r["view_count"], "duration_min": r["duration_min"],
             "title_archetype": r["title_archetype"], "named_guest": r.get("title_named_guest"),
             "format_family": r["format_family"]}
            for r in bottom
        ]

        # Per-family top-decile features (only if family >= 20)
        cstat["per_family"] = {}
        for fam, frows in families.items():
            if len(frows) < 10:
                continue
            ftop, fbot = split_top_bottom(frows, "views_per_day", decile=0.10)
            fstat = {
                "n": len(frows),
                "median_views_per_day": round(median([r["views_per_day"] for r in frows]), 1),
                "top_n": len(ftop),
                "bottom_n": len(fbot),
                "top_median_views_per_day": round(median([r["views_per_day"] for r in ftop]), 1),
                "bottom_median_views_per_day": round(median([r["views_per_day"] for r in fbot]), 1),
                "top_archetypes": dict(Counter(r["title_archetype"] for r in ftop).most_common()),
                "top_titles": [{"id": r["id"], "title": r["title"], "views_per_day": r["views_per_day"]} for r in ftop[:10]],
                "bottom_titles": [{"id": r["id"], "title": r["title"], "views_per_day": r["views_per_day"]} for r in fbot[:10]],
                "feature_prevalence_top": {f: round(feature_prevalence(ftop, f), 4) for f in BOOL_FEATURES},
                "feature_prevalence_bottom": {f: round(feature_prevalence(fbot, f), 4) for f in BOOL_FEATURES},
            }
            cstat["per_family"][fam] = fstat

        stats["creators"][creator] = cstat

    # Cross-creator comparison (portability)
    if "chris_williamson" in stats["creators"] and "lennox_saint" in stats["creators"]:
        chris = stats["creators"]["chris_williamson"]
        lennox = stats["creators"]["lennox_saint"]
        port = {}
        for f in BOOL_FEATURES:
            port[f] = {
                "chris": chris["feature_prevalence"][f],
                "lennox": lennox["feature_prevalence"][f],
                "delta": round(chris["feature_prevalence"][f] - lennox["feature_prevalence"][f], 4),
            }
        port["title_archetypes"] = {
            "chris": chris["title_archetypes"],
            "lennox": lennox["title_archetypes"],
        }
        stats["portability_compare"] = port

    out_json = ANALYSES / "_stats.json"
    out_json.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_json}")

    # Human-readable summary
    md = []
    md.append("# Corpus Statistics — auto-generated\n")
    md.append(f"Total rows: **{stats['total_rows']}**\n")
    for creator, c in stats["creators"].items():
        md.append(f"\n## {creator}\n")
        md.append(f"- n: {c['n']}")
        md.append(f"- Family counts: {c['family_counts']}")
        md.append(f"- Total views: {c['total_views']:,}")
        md.append(f"- Median views/day: {c['distributions']['views_per_day'].get('p50',0)}")
        md.append(f"- Top vs bottom decile multiplier: {c.get('top_vs_bottom_multiplier')}x")
        md.append(f"- Top archetypes: {c['title_archetypes']}")
        md.append(f"- % with named guest: {c['pct_with_guest']*100:.1f}%")
        md.append(f"- Top guests: {list(c['top_guests'].items())[:10]}")
        md.append(f"- Title feature prevalence: {c['feature_prevalence']}")
    (ANALYSES / "_stats.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {ANALYSES/'_stats.md'}")


if __name__ == "__main__":
    main()
