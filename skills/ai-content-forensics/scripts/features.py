#!/usr/bin/env python3
"""
Per-video feature extraction.

Reads:    normalized/videos/{creator}/{id}/{metadata.json,transcript.txt}
Writes:   06_packaging_features.csv  (one row per video)
          06_packaging_features.json (same data, JSON)
"""
import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NORM = ROOT / "normalized" / "videos"
TODAY = date(2026, 4, 25)

# ---- Title pattern detectors --------------------------------------------------

NUMBER_RE = re.compile(r"\b\d[\d,\.]*\b")
QUESTION_RE = re.compile(r"\?")
QUOTED_RE = re.compile(r'["“”]([^"“”]{2,})["“”]')
DASH_RE = re.compile(r"[—–] ?| - ")
PARENS_RE = re.compile(r"\([^)]+\)|\[[^\]]+\]")
EMOJI_RE = re.compile(r"[☀-➿\U0001F300-\U0001FAFF]")
ALL_CAPS_WORD_RE = re.compile(r"\b[A-Z]{3,}\b")
COLON_RE = re.compile(r":")
PIPE_RE = re.compile(r"\|")
HASHTAG_RE = re.compile(r"(?<!\w)#\w+")
PERCENT_RE = re.compile(r"\b\d+\s*%")
DOLLAR_RE = re.compile(r"\$\d")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

PAIN_TRIGGERS = {"failure","fail","mistake","wrong","worst","stop","quit","broken","scam","trap","danger","ruin"}
CURIOSITY_TRIGGERS = {"secret","hidden","truth","really","actually","unknown","mystery","surprised","strange","why","how","what"}
SPEED_TRIGGERS = {"fast","quick","speed","instant","minutes","seconds","day","overnight","30 days","60 days","week"}
STATUS_TRIGGERS = {"alpha","best","top","elite","high-status","status","power","king","master","legend","greatest"}
MONEY_TRIGGERS = {"$","money","income","revenue","mrr","arr","wealth","rich","earn","made","made $","6-figure","7-figure","million","billion"}
HEALTH_TRIGGERS = {"sleep","cortisol","testosterone","dopamine","gut","muscle","fat","fasting","ozempic","brain","pain","anxiety","depression"}
IDENTITY_TRIGGERS = {"man","woman","men","women","masculine","feminine","gen z","millennial","boomer","alpha","beta","sigma"}
FEAR_TRIGGERS = {"never","worst","crisis","collapse","apocalypse","extinction","end","trap","ruin","danger","threat","killer","dying"}
TRANSFORM_TRIGGERS = {"transform","change","life-changing","rebuild","reinvent","heal","fix","upgrade","mastered","escape"}
QUESTION_OPENERS = {"why","how","what","when","where","is","are","does","do","can","could","will","should"}

TRIGGERS = {
    "pain": PAIN_TRIGGERS, "curiosity": CURIOSITY_TRIGGERS, "speed": SPEED_TRIGGERS,
    "status": STATUS_TRIGGERS, "money": MONEY_TRIGGERS, "health": HEALTH_TRIGGERS,
    "identity": IDENTITY_TRIGGERS, "fear": FEAR_TRIGGERS, "transformation": TRANSFORM_TRIGGERS,
}

NAMED_GUEST_HINT = re.compile(r"(?:(?:^|[ -])(?:Dr\.|Dr|Prof\.?|Mr\.|Mrs\.)?\s*[A-Z][a-z]+\s+[A-Z][a-z]+)|(?:[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:on|talks|reveals))")
PIPE_GUEST = re.compile(r"\|\s*([^|]+)$")
DASH_GUEST = re.compile(r"\s[-—]\s([A-Z][^-—]+)$")


def title_archetype(title: str) -> str:
    t = title.strip()
    tlow = t.lower()
    if "vs" in tlow or " vs. " in tlow:
        return "vs_comparison"
    if t.endswith("?") or QUESTION_OPENERS & set(tlow.split()[:1]):
        return "question"
    if PIPE_GUEST.search(t):
        return "headline_pipe_guest"
    if DASH_GUEST.search(t):
        return "headline_dash_guest"
    if re.match(r"^\d", t):
        return "number_lead"
    if re.match(r"^(why|how|what|when|where) ", tlow):
        return "qword_lead"
    if t.isupper() or sum(1 for c in t if c.isupper()) / max(1, len(t)) > 0.5:
        return "caps_heavy"
    if "(" in t or "[" in t:
        return "headline_with_parenthetical"
    return "headline_statement"


def detect_triggers(text: str) -> list[str]:
    tl = text.lower()
    hits = []
    for cat, words in TRIGGERS.items():
        for w in words:
            if w.startswith("$"):
                if "$" in tl:
                    hits.append(cat); break
            elif " " in w:
                if w in tl:
                    hits.append(cat); break
            elif re.search(rf"\b{re.escape(w)}\b", tl):
                hits.append(cat); break
    return list(dict.fromkeys(hits))


def hook_features(transcript: str) -> dict:
    """Approximate first-15s, first-30s and full-hook features from a transcript.
    Auto-subs lack precise timestamps after our VTT cleanup, so we fall back to
    word-count proxies: ~150 wpm typical podcast/clip pace = ~2.5 wps.
    First 38 words ≈ first 15s; first 75 words ≈ first 30s.
    """
    if not transcript:
        return {"hook_15": "", "hook_30": "", "hook_words_15": 0,
                "hook_question": False, "hook_number": False,
                "hook_first_word": "", "hook_archetype": "no_transcript"}
    words = transcript.split()
    hook15 = " ".join(words[:38])
    hook30 = " ".join(words[:75])
    first = words[0].lower().strip(",.;:?!\"'") if words else ""
    archetype = "monologue"
    if "?" in hook30 and any(QUESTION_RE.search(s) for s in hook30.split(".")[:3]):
        archetype = "question_open"
    elif first in QUESTION_OPENERS:
        archetype = "question_open"
    elif first in {"so","look","listen","ok","alright"}:
        archetype = "casual_open"
    elif first in {"i","my","me"}:
        archetype = "first_person_open"
    elif first in {"you","your"}:
        archetype = "second_person_open"
    elif NUMBER_RE.search(hook15):
        archetype = "number_lead_open"
    elif first in {"the","a","an"}:
        archetype = "noun_lead_open"
    return {
        "hook_15": hook15.replace("\n", " ")[:500],
        "hook_30": hook30.replace("\n", " ")[:1000],
        "hook_words_15": len(hook15.split()),
        "hook_question": "?" in hook30,
        "hook_number": bool(NUMBER_RE.search(hook15)),
        "hook_first_word": first,
        "hook_archetype": archetype,
    }


def extract_named_guest(title: str) -> str | None:
    """Heuristic: try to grab a guest name from podcast-style titles.
    Patterns: "... | Joe Rogan", "... - Eric Weinstein", "... w/ John Smith", "Joe Rogan on ..."
    """
    m = PIPE_GUEST.search(title)
    if m:
        return m.group(1).strip()
    m = DASH_GUEST.search(title)
    if m:
        return m.group(1).strip()
    m = re.search(r"\bw/\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", title)
    if m:
        return m.group(1).strip()
    m = re.search(r"\bwith\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", title)
    if m:
        return m.group(1).strip()
    m = re.match(r"^([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:on|reveals|talks|explains|tells|breaks)", title)
    if m:
        return m.group(1).strip()
    return None


def extract_features(meta: dict, transcript: str) -> dict:
    title = meta.get("title") or ""
    desc = meta.get("description") or ""
    duration = meta.get("duration") or 0
    views = meta.get("view_count") or 0
    likes = meta.get("like_count") or 0
    comments = meta.get("comment_count") or 0
    upload = meta.get("upload_date")
    try:
        upload_d = date.fromisoformat(upload)
        age = max(1, (TODAY - upload_d).days)
    except Exception:
        age = None

    out = {
        "creator": meta.get("uploader") or meta.get("channel"),
        "id": meta.get("id"),
        "url": meta.get("url"),
        "title": title,
        "upload_date": upload,
        "age_days": age,
        "duration_s": duration,
        "duration_min": round(duration/60, 1) if duration else 0,
        "view_count": views,
        "like_count": likes,
        "comment_count": comments,
        "views_per_day": round(views/age, 1) if age and views else 0,
        "like_to_view": round(likes/views, 5) if views else 0,
        "comment_to_view": round(comments/views, 6) if views else 0,
        # Title features
        "title_chars": len(title),
        "title_words": len(title.split()),
        "title_has_number": bool(NUMBER_RE.search(title)),
        "title_has_question": bool(QUESTION_RE.search(title)),
        "title_has_quoted": bool(QUOTED_RE.search(title)),
        "title_has_parens": bool(PARENS_RE.search(title)),
        "title_has_dash": bool(DASH_RE.search(title)),
        "title_has_pipe": bool(PIPE_RE.search(title)),
        "title_has_colon": bool(COLON_RE.search(title)),
        "title_has_emoji": bool(EMOJI_RE.search(title)),
        "title_has_caps_word": bool(ALL_CAPS_WORD_RE.search(title)),
        "title_has_hashtag": bool(HASHTAG_RE.search(title)),
        "title_has_percent": bool(PERCENT_RE.search(title)),
        "title_has_dollar": bool(DOLLAR_RE.search(title)),
        "title_has_year": bool(YEAR_RE.search(title)),
        "title_archetype": title_archetype(title),
        "title_triggers": "|".join(detect_triggers(title)),
        "title_first_word": (title.split() or [""])[0].lower(),
        "title_named_guest": extract_named_guest(title),
        # Description features
        "desc_chars": len(desc),
        "desc_words": len(desc.split()),
        "desc_has_link": "http" in desc.lower(),
        "desc_has_chapters": bool(re.search(r"^\d{1,2}:\d{2}", desc, re.M)),
        # Tags
        "tags_count": len(meta.get("tags") or []),
        "tags": "|".join((meta.get("tags") or [])[:10]),
        # Format-family classification
        "format_family": (
            "long_form" if duration >= 1800 else
            "clip" if duration >= 60 else
            "short"
        ),
        # Transcript availability
        "transcript_words": len(transcript.split()) if transcript else 0,
        "has_transcript": bool(transcript),
    }
    out.update(hook_features(transcript))
    return out


def main():
    rows = []
    for creator_dir in sorted(NORM.iterdir()):
        if not creator_dir.is_dir():
            continue
        for vd in sorted(creator_dir.iterdir()):
            if not vd.is_dir():
                continue
            meta_path = vd / "metadata.json"
            if not meta_path.exists():
                continue
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            transcript = ""
            t_path = vd / "transcript.txt"
            if t_path.exists():
                transcript = t_path.read_text(encoding="utf-8")
            row = extract_features(meta, transcript)
            row["creator_slug"] = creator_dir.name
            rows.append(row)

    rows.sort(key=lambda r: (r["creator_slug"], -(r.get("view_count") or 0)))

    csv_path = ROOT / "06_packaging_features.csv"
    json_path = ROOT / "06_packaging_features.json"
    if rows:
        cols = list(rows[0].keys())
        with csv_path.open("w", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                # Strip newlines from str fields for CSV safety
                cleaned = {k: (v.replace("\n", " ") if isinstance(v, str) else v) for k,v in r.items()}
                w.writerow(cleaned)
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {len(rows)} rows.")
    else:
        print("No rows to write.")


if __name__ == "__main__":
    main()
