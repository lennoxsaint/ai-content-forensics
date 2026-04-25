#!/usr/bin/env python3
"""
Normalize per-video raw data into the skill's expected layout.

Reads:    raw/per_video_{creator}/<id>.info.json
          raw/per_video_{creator}/<id>.{en|en-orig}.vtt
          raw/per_video_{creator}/<id>.jpg
Writes:   normalized/videos/{id}/metadata.json
          normalized/videos/{id}/transcript.txt
          normalized/videos/{id}/thumbnail.jpg
          normalized/videos/{id}/notes.md
          04_video_index.csv
          05_video_index.json
          logs/exclusions_log.md
"""
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
import sys
import csv

ROOT = Path(__file__).resolve().parent.parent
WINDOW_START = date(2024, 4, 25)
WINDOW_END = date(2026, 4, 26)  # inclusive of 25th


def parse_vtt(path: Path) -> str:
    """Convert VTT cues to plain transcript text, dedup adjacent duplicates."""
    text_lines = []
    last_line = None
    if not path.exists():
        return ""
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("WEBVTT"):
            continue
        if "-->" in s:
            continue
        if s.startswith("Kind:") or s.startswith("Language:") or s.startswith("NOTE"):
            continue
        if re.match(r"^\d+$", s):
            continue
        # Strip vtt inline tags <c.colorE5E5E5>...</c> and timestamps <00:00:01.000>
        s = re.sub(r"<[^>]+>", "", s)
        s = re.sub(r"\&[a-z]+;", " ", s)
        s = s.strip()
        if not s:
            continue
        # Dedup repeating lines (auto-subs often repeat partial cues)
        if s == last_line:
            continue
        text_lines.append(s)
        last_line = s
    return "\n".join(text_lines)


def pick_transcript(raw_dir: Path, vid: str) -> tuple[str, str | None]:
    """Prefer .en.vtt (auto-translated), fall back to .en-orig.vtt, then any *.vtt."""
    for variant in (f"{vid}.en.vtt", f"{vid}.en-US.vtt", f"{vid}.en-orig.vtt"):
        p = raw_dir / variant
        if p.exists():
            return parse_vtt(p), variant
    # last resort: any vtt for this id
    matches = list(raw_dir.glob(f"{vid}.*.vtt"))
    if matches:
        return parse_vtt(matches[0]), matches[0].name
    return "", None


def normalize_creator(creator: str, raw_dir: Path, out_dir: Path, video_index: list,
                      exclusions: list, in_window_only: bool = True) -> dict:
    """Normalize one creator's per-video data."""
    info_jsons = sorted(raw_dir.glob("*.info.json"))
    counts = {"total": 0, "in_window": 0, "out_of_window": 0,
              "missing_transcript": 0, "missing_thumbnail": 0,
              "shorts_excluded": 0}

    for ij in info_jsons:
        # Skip channel/playlist info JSONs (24-char channel ID is the filename root)
        try:
            data = json.loads(ij.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Channel info JSONs lack an `id` field shaped like a video
        vid = data.get("id")
        if not vid or len(vid) != 11:  # YouTube video IDs are 11 chars
            continue
        counts["total"] += 1

        upload_date_str = data.get("upload_date", "") or ""
        try:
            upload_date = datetime.strptime(upload_date_str, "%Y%m%d").date()
        except (ValueError, TypeError):
            upload_date = None

        in_window = (upload_date is not None and
                     WINDOW_START <= upload_date < WINDOW_END)

        if upload_date is None:
            exclusions.append({"creator": creator, "video_id": vid,
                               "title": data.get("title", ""),
                               "reason": "no upload_date"})
            continue
        if not in_window:
            counts["out_of_window"] += 1
            if in_window_only:
                exclusions.append({"creator": creator, "video_id": vid,
                                   "upload_date": upload_date.isoformat(),
                                   "title": data.get("title", ""),
                                   "reason": f"outside 24mo window ({WINDOW_START} - {WINDOW_END})"})
                continue
        else:
            counts["in_window"] += 1

        duration = data.get("duration") or 0
        is_short = duration and duration < 60
        if is_short:
            counts["shorts_excluded"] += 1
            exclusions.append({"creator": creator, "video_id": vid,
                               "duration": duration,
                               "title": data.get("title", ""),
                               "reason": "Short (<60s)"})
            continue

        # Build per-video folder
        vfolder = out_dir / vid
        vfolder.mkdir(parents=True, exist_ok=True)

        # Pick best transcript
        transcript, transcript_src = pick_transcript(raw_dir, vid)
        if transcript:
            (vfolder / "transcript.txt").write_text(transcript, encoding="utf-8")
        else:
            counts["missing_transcript"] += 1

        # Copy thumbnail
        thumb_src = raw_dir / f"{vid}.jpg"
        if thumb_src.exists():
            shutil.copy2(thumb_src, vfolder / "thumbnail.jpg")
        else:
            counts["missing_thumbnail"] += 1

        # Distill metadata into a smaller normalized json
        meta = {
            "id": vid,
            "title": data.get("title", ""),
            "channel": data.get("channel", ""),
            "channel_id": data.get("channel_id", ""),
            "uploader": data.get("uploader", ""),
            "upload_date": upload_date.isoformat(),
            "timestamp": data.get("timestamp"),
            "duration": duration,
            "view_count": data.get("view_count"),
            "like_count": data.get("like_count"),
            "comment_count": data.get("comment_count"),
            "description": data.get("description", ""),
            "tags": data.get("tags") or [],
            "categories": data.get("categories") or [],
            "language": data.get("language"),
            "thumbnail_url": data.get("thumbnail"),
            "transcript_path": "transcript.txt" if transcript else None,
            "transcript_source": transcript_src,
            "transcript_word_count": len(transcript.split()) if transcript else 0,
            "thumbnail_path": "thumbnail.jpg" if thumb_src.exists() else None,
            "raw_info_path": str(ij.relative_to(ROOT)),
            "url": f"https://www.youtube.com/watch?v={vid}",
        }
        (vfolder / "metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Light per-video notes scaffold
        notes = (
            f"# {meta['title']}\n\n"
            f"- ID: `{vid}` ({meta['url']})\n"
            f"- Uploaded: {meta['upload_date']}\n"
            f"- Duration: {meta['duration']}s\n"
            f"- Views: {meta['view_count']}, Likes: {meta['like_count']}, Comments: {meta['comment_count']}\n"
            f"- Transcript: {'yes' if transcript else 'NO'} "
            f"(source: {transcript_src})\n"
            f"- Thumbnail: {'yes' if thumb_src.exists() else 'NO'}\n"
        )
        (vfolder / "notes.md").write_text(notes, encoding="utf-8")

        # Add to flat index
        video_index.append({
            "creator": creator,
            "id": vid,
            "title": meta["title"],
            "upload_date": meta["upload_date"],
            "duration": duration,
            "view_count": meta["view_count"],
            "like_count": meta["like_count"],
            "comment_count": meta["comment_count"],
            "transcript_words": meta["transcript_word_count"],
            "url": meta["url"],
        })
    return counts


def main():
    creators = [
        ("chris_williamson", ROOT / "raw" / "per_video_chris", True),
        ("lennox_saint",     ROOT / "raw" / "per_video_lennox", True),
    ]
    out_videos = ROOT / "normalized" / "videos"
    out_videos.mkdir(parents=True, exist_ok=True)
    logs_dir = ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    video_index = []
    exclusions = []
    summary = {}

    for creator, raw_dir, in_window in creators:
        if not raw_dir.exists():
            print(f"Skipping {creator} — no raw dir", file=sys.stderr)
            continue
        creator_out = out_videos / creator
        creator_out.mkdir(parents=True, exist_ok=True)
        counts = normalize_creator(creator, raw_dir, creator_out,
                                   video_index, exclusions, in_window)
        summary[creator] = counts
        print(f"{creator}: {counts}", file=sys.stderr)

    # Write flat index files
    idx_csv = ROOT / "04_video_index.csv"
    idx_json = ROOT / "05_video_index.json"
    if video_index:
        cols = list(video_index[0].keys())
        with idx_csv.open("w", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(video_index)
        idx_json.write_text(json.dumps(video_index, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    # Write exclusion log
    excl_log = ROOT / "logs" / "exclusions_log.md"
    with excl_log.open("w", encoding="utf-8") as f:
        f.write("# Excluded videos\n\n| Creator | Video ID | Upload Date | Title | Reason |\n|---|---|---|---|---|\n")
        for e in exclusions:
            f.write(f"| {e.get('creator')} | `{e.get('video_id')}` | {e.get('upload_date','-')} | "
                    f"{(e.get('title','') or '').replace('|','/')[:100]} | {e.get('reason')} |\n")

    # Write run-report fragment
    rr = ROOT / "logs" / "normalize_summary.json"
    rr.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
