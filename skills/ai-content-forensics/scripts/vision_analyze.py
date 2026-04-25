#!/usr/bin/env python3
"""
Run Gemini Vision over every collected thumbnail in normalized/videos/ and
emit structured per-video vision JSON + a flat aggregated CSV.

Reads:    normalized/videos/{creator_slug}/{video_id}/thumbnail.jpg
Writes:   normalized/videos/{creator_slug}/{video_id}/vision.json
          analyses/vision_aggregate.csv
          analyses/vision_aggregate.json

Skips videos that already have vision.json (idempotent — safe to re-run).

Schema per vision.json:
{
  "video_id": "...",
  "title": "...",
  "model": "gemini-2.5-pro",
  "face_count": int,
  "host_face_present": bool,
  "guest_face_present": bool,
  "faces_total_emotion": "neutral|surprised|angry|amused|stern|smiling|other",
  "expression_intensity": "high|medium|low",
  "text_overlay_present": bool,
  "text_overlay_words": [str, ...],
  "text_overlay_word_count": int,
  "text_overlay_dominant_color": "hex",
  "background_color_dominant": "hex",
  "background_simplicity": "minimal|busy",
  "focal_point_clarity": "high|medium|low",
  "primary_concept_object": "free-text short label",
  "modern_wisdom_brand_mark_visible": bool,
  "single_dominant_subject": bool,
  "mobile_legibility_220x125": "high|medium|low",
  "interpretation_notes": "1-3 sentences"
}
"""
import csv
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NORM = ROOT / "normalized" / "videos"
ANALYSES = ROOT / "analyses"
LOGS = ROOT / "logs"
ANALYSES.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

VISION_LOG = LOGS / "vision_analyze.log"

# Lazy import — only required if we actually run
try:
    from google import genai
    from google.genai import types
except ImportError as e:
    print("google-genai not installed:", e, file=sys.stderr)
    sys.exit(2)


PROMPT_TEMPLATE = """You are a YouTube thumbnail forensics analyst. Analyze the attached thumbnail image and return a single JSON object matching this schema EXACTLY (no preamble, no markdown):

{
  "face_count": <integer 0-N>,
  "host_face_present": <bool — Chris Williamson is the host; if creator is not Chris, mark false>,
  "guest_face_present": <bool — interview guest visible alongside or instead of host>,
  "faces_total_emotion": "<one of: neutral, surprised, angry, amused, stern, smiling, intense, sad, other>",
  "expression_intensity": "<high | medium | low>",
  "text_overlay_present": <bool>,
  "text_overlay_words": [<word strings, exact text, in reading order>],
  "text_overlay_word_count": <integer>,
  "text_overlay_dominant_color": "<6-digit hex like #FFFFFF>",
  "background_color_dominant": "<hex>",
  "background_simplicity": "<minimal | busy>",
  "focal_point_clarity": "<high | medium | low>",
  "primary_concept_object": "<short label of the dominant non-face element if any, e.g. 'graph', 'phone', 'plate of food', 'chess piece', 'none'>",
  "modern_wisdom_brand_mark_visible": <bool>,
  "single_dominant_subject": <bool — would a viewer see ONE clear subject in 0.3 seconds at thumbnail size>,
  "mobile_legibility_220x125": "<high | medium | low — at small sizes, can the viewer parse the dominant subject and text>",
  "interpretation_notes": "<1-3 sentences plain text describing the thumbnail's packaging strategy in this single image>"
}

Context: video title is "{title}". Creator is "{creator}". Return only the JSON object."""


def analyze_one(client, image_path: Path, title: str, creator: str, model_name: str):
    image_bytes = image_path.read_bytes()
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        types.Part.from_text(text=PROMPT_TEMPLATE.format(title=title, creator=creator)),
    ]
    resp = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    return resp.text


def log(msg: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    with VISION_LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line.rstrip())


def main():
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log("ERROR: GOOGLE_API_KEY not set; cannot run vision pass.")
        sys.exit(2)

    # Use the strongest available vision model. gemini-2.5-pro is generally available;
    # the system memo says image GENERATION uses gemini-3.1-flash-image-preview but for
    # vision UNDERSTANDING we use a different model.
    model_candidates = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-1.5-pro",
    ]
    client = genai.Client(api_key=api_key)
    model_name = None
    for cand in model_candidates:
        try:
            client.models.get(model=cand)
            model_name = cand
            break
        except Exception:
            continue
    if not model_name:
        # Don't pre-validate; just try gemini-2.5-pro and let the call decide
        model_name = "gemini-2.5-pro"
    log(f"Using vision model: {model_name}")

    # Iterate every per-video folder under both creators
    rows = []
    failures = []
    processed = 0
    skipped = 0
    for creator_dir in sorted(NORM.iterdir()):
        if not creator_dir.is_dir():
            continue
        for vd in sorted(creator_dir.iterdir()):
            if not vd.is_dir():
                continue
            meta_path = vd / "metadata.json"
            thumb_path = vd / "thumbnail.jpg"
            vision_path = vd / "vision.json"
            if not (meta_path.exists() and thumb_path.exists()):
                continue
            if vision_path.exists():
                # idempotent — re-use existing
                try:
                    rows.append(json.loads(vision_path.read_text(encoding="utf-8")))
                except Exception:
                    pass
                skipped += 1
                continue
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            title = meta.get("title", "")
            creator = meta.get("channel", creator_dir.name)
            try:
                raw = analyze_one(client, thumb_path, title, creator, model_name)
                # Some models still wrap JSON in code fences; strip if present.
                cleaned = raw.strip().strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:].strip()
                payload = json.loads(cleaned)
                payload["video_id"] = meta.get("id")
                payload["title"] = title
                payload["model"] = model_name
                payload["creator_slug"] = creator_dir.name
                vision_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                rows.append(payload)
                processed += 1
                if processed % 25 == 0:
                    log(f"vision pass: {processed} done, {len(failures)} failed")
            except Exception as e:
                failures.append({"video_id": meta.get("id"), "error": str(e)[:200]})
                log(f"vision FAIL {meta.get('id')}: {str(e)[:200]}")
                # avoid hammering on failures
                time.sleep(0.5)

    # Write aggregates
    if rows:
        cols = sorted({k for r in rows for k in r.keys()})
        # Force a stable ordering with key columns first
        priority = ["video_id", "creator_slug", "title", "model"]
        cols = priority + [c for c in cols if c not in priority]
        agg_csv = ANALYSES / "vision_aggregate.csv"
        with agg_csv.open("w", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                cleaned = {}
                for k in cols:
                    v = r.get(k)
                    if isinstance(v, (list, dict)):
                        v = json.dumps(v, ensure_ascii=False)
                    cleaned[k] = v
                w.writerow(cleaned)
        agg_json = ANALYSES / "vision_aggregate.json"
        agg_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"vision pass complete: processed={processed}, skipped_existing={skipped}, failures={len(failures)}, total_rows_in_aggregate={len(rows)}")
    if failures:
        (LOGS / "vision_failures.json").write_text(
            json.dumps(failures, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
