#!/usr/bin/env bash
# Rate-limit-safe yt-dlp collector for AI Content Forensics.
#
# Usage:
#   bash scripts/youtube_collect.sh \
#     --channel-id UCIaH-gZIVC432YRjNVvnyCA \
#     --window-start 20240425 \
#     --creator-slug chris_williamson \
#     [--output-root "$PWD"] \
#     [--include-streams]
#
# Effects:
#   - writes raw/per_video_{creator_slug}/{id}.{info.json,jpg,en*.vtt}
#   - writes raw/{creator_slug}_done_archive.txt (resumable)
#   - writes logs/{creator_slug}_collection.log
#   - writes "FINISHED CHRIS COLLECTION"-style marker on clean exit
#
# Resumability: re-running the same command skips videos already in the
# download archive — safe to kill, wait out a YouTube rate-limit, and resume.

set -euo pipefail

# ---- arg parse ---------------------------------------------------------------

CHANNEL_ID=""
WINDOW_START=""
CREATOR_SLUG=""
OUTPUT_ROOT="$PWD"
INCLUDE_STREAMS=0
SLEEP_REQUESTS=4
SLEEP_INTERVAL_MIN=2
SLEEP_INTERVAL_MAX=8

while [[ $# -gt 0 ]]; do
    case "$1" in
        --channel-id) CHANNEL_ID="$2"; shift 2 ;;
        --window-start) WINDOW_START="$2"; shift 2 ;;
        --creator-slug) CREATOR_SLUG="$2"; shift 2 ;;
        --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
        --include-streams) INCLUDE_STREAMS=1; shift ;;
        --sleep-requests) SLEEP_REQUESTS="$2"; shift 2 ;;
        --sleep-interval-min) SLEEP_INTERVAL_MIN="$2"; shift 2 ;;
        --sleep-interval-max) SLEEP_INTERVAL_MAX="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,18p' "$0"
            exit 0
            ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

[[ -n "$CHANNEL_ID" ]]    || { echo "ERR: --channel-id required" >&2; exit 2; }
[[ -n "$WINDOW_START" ]]  || { echo "ERR: --window-start YYYYMMDD required" >&2; exit 2; }
[[ -n "$CREATOR_SLUG" ]]  || { echo "ERR: --creator-slug required" >&2; exit 2; }

mkdir -p "$OUTPUT_ROOT/raw/per_video_$CREATOR_SLUG" "$OUTPUT_ROOT/logs"

ARCHIVE="$OUTPUT_ROOT/raw/${CREATOR_SLUG}_done_archive.txt"
COLLECTION_LOG="$OUTPUT_ROOT/logs/${CREATOR_SLUG}_collection.log"
COLLECTED_LOG="$OUTPUT_ROOT/logs/${CREATOR_SLUG}_videos_collected.log"

# Marker uses the slug for distinguishability across creators.
START_MARKER="STARTED ${CREATOR_SLUG^^} COLLECTION"
DONE_MARKER="FINISHED ${CREATOR_SLUG^^} COLLECTION"

ts() { date "+%Y-%m-%d %H:%M:%S %Z"; }
echo "[$(ts)] $START_MARKER" >> "$COLLECTION_LOG"

run_ytdlp() {
    local url="$1"
    yt-dlp \
        --skip-download \
        --write-info-json \
        --write-thumbnail \
        --write-auto-subs \
        --sub-lang "en.*,en" \
        --sub-format "vtt/best" \
        --convert-thumbnails jpg \
        --no-warnings \
        --ignore-errors \
        --download-archive "$ARCHIVE" \
        --break-match-filters "upload_date >= $WINDOW_START" \
        --sleep-requests "$SLEEP_REQUESTS" \
        --sleep-interval "$SLEEP_INTERVAL_MIN" \
        --max-sleep-interval "$SLEEP_INTERVAL_MAX" \
        --retries 3 \
        --extractor-retries 3 \
        --print-to-file "[%(epoch)s] DONE %(id)s | %(upload_date)s | %(duration)s | %(view_count)s | %(title).80s" "$COLLECTED_LOG" \
        -o "$OUTPUT_ROOT/raw/per_video_$CREATOR_SLUG/%(id)s.%(ext)s" \
        "$url" \
        >> "$COLLECTION_LOG" 2>&1 || {
            echo "[$(ts)] yt-dlp returned non-zero on $url (continuing)" >> "$COLLECTION_LOG"
        }
}

run_ytdlp "https://www.youtube.com/channel/$CHANNEL_ID/videos"

if [[ "$INCLUDE_STREAMS" == "1" ]]; then
    echo "[$(ts)] STARTED ${CREATOR_SLUG^^} STREAMS" >> "$COLLECTION_LOG"
    run_ytdlp "https://www.youtube.com/channel/$CHANNEL_ID/streams" || true
fi

echo "[$(ts)] $DONE_MARKER" >> "$COLLECTION_LOG"

# Quick post-run summary
COLLECTED=$(ls "$OUTPUT_ROOT/raw/per_video_$CREATOR_SLUG/"*.info.json 2>/dev/null | wc -l | tr -d ' ')
RATE_LIMITED=$(grep -c "rate-limited by YouTube" "$COLLECTION_LOG" 2>/dev/null || echo 0)
echo "[$(ts)] summary: collected=$COLLECTED rate_limit_hits=$RATE_LIMITED" >> "$COLLECTION_LOG"

if [[ "$RATE_LIMITED" -gt 5 ]]; then
    echo "[$(ts)] WARN: $RATE_LIMITED rate-limit messages observed. Consider sleeping 60min and re-running with same args (--download-archive will skip already-collected videos)." >> "$COLLECTION_LOG"
fi
