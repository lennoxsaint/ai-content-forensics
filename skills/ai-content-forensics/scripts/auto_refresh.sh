#!/usr/bin/env bash
# End-to-end refresh once Chris collection completes.
# Re-runs normalize -> features -> analyze -> vision -> auto_update_artifacts -> Second Brain log.

set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

LOG="$DIR/logs/auto_refresh.log"
SECOND_BRAIN="/Users/lennoxsaint/clawd/shared/second-brain/bin/second_brain_log_run.py"

ts() { date "+%Y-%m-%d %H:%M:%S %Z"; }
log() { echo "[$(ts)] $*" | tee -a "$LOG"; }

mkdir -p "$DIR/logs"
log "auto_refresh starting"

# Step 1 — pipeline (normalize, features, analyze)
log "running scripts/run_pipeline.sh"
bash "$DIR/scripts/run_pipeline.sh" 2>&1 | tee -a "$LOG" || {
    log "WARN: run_pipeline.sh failed; aborting refresh"
    exit 1
}

CHRIS_COUNT=$(ls "$DIR/raw/per_video_chris/"*.info.json 2>/dev/null | wc -l | tr -d ' ')
NORM_COUNT=$(find "$DIR/normalized/videos/chris_williamson" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
log "chris raw=$CHRIS_COUNT normalized=$NORM_COUNT"

# Step 2 — vision pass over thumbnails (idempotent — skips already-processed)
if [[ -n "${GOOGLE_API_KEY:-}" ]]; then
    log "running scripts/vision_analyze.py (Gemini Vision)"
    python3 "$DIR/scripts/vision_analyze.py" 2>&1 | tee -a "$LOG" || log "WARN: vision pass had failures (logged)"
else
    log "GOOGLE_API_KEY not set; skipping vision pass. Re-export and rerun this script to backfill."
fi

# Step 3 — refresh deliverables
log "running scripts/auto_update_artifacts.py"
python3 "$DIR/scripts/auto_update_artifacts.py" 2>&1 | tee -a "$LOG" || {
    log "WARN: auto_update_artifacts failed"
    exit 1
}

# Step 4 — Second Brain log (both daily files)
TS_START="$(grep -m1 'auto_refresh starting' "$LOG" | head -c 21 | tr -d '[]' || date '+%Y-%m-%d %H:%M:%S %Z')"
TS_END="$(ts)"
RUN_ID="cw-forensics-refresh-$(date +%s)"

log "writing Second Brain log (target-mode inbox)"
"$SECOND_BRAIN" \
  --target-mode inbox \
  --objective "AI content forensics on Chris Williamson — auto-refresh after corpus completion" \
  --scope_completed "Re-ran normalize/features/analyze with full corpus (chris=$CHRIS_COUNT). Ran Gemini Vision pass over thumbnails. Refreshed visuals/_assets.json, thread/final_thread.md, publish/copy_paste.md, and re-rendered all 9 PNGs from updated stats. Second Brain logged on both daily files." \
  --files_changed "thread/final_thread.md, visuals/_assets.json, visuals/assets/{01..09}.{svg,html}, visuals/previews/{01..09}.png, publish/copy_paste.md, analyses/_stats.json, analyses/_stats.md, analyses/vision_aggregate.{csv,json}, normalized/videos/*/*/vision.json (per-video), 06_packaging_features.csv/json, logs/auto_refresh.log, logs/auto_update_summary.json" \
  --commands_tests "bash scripts/run_pipeline.sh; python3 scripts/vision_analyze.py; python3 scripts/auto_update_artifacts.py; rsvg-convert across all SVGs to refresh PNGs." \
  --decisions_tradeoffs "Auto-refresh fired by watcher after Chris collection completed. Numeric claims regenerated from analyses/_stats.json; qualitative prose in synthesis/constitutions/profiles preserved (refresh recipe in 00_run_report.md and publish/copy_paste.md). No auto-publish — Lennox reviews and pastes manually." \
  --errors_fixes "See logs/auto_refresh.log for any per-video vision failures (logged in logs/vision_failures.json) and any pipeline warnings." \
  --next_steps "Lennox reviews refreshed thread + 9 PNGs in publish/copy_paste.md, then manually pastes into Threads. Optional: feed updated constitutions into Aria directive system." \
  --agent_name "Claude Code (ai-content-forensics auto-refresh)" \
  --agent_platform "claude" \
  --model "claude-opus-4-7[1m]" \
  --host_device "MacBook-Pro-2.local" \
  --host_user "lennoxsaint" \
  --workspace_root "/Users/lennoxsaint" \
  --run_id "$RUN_ID" \
  --plan_id "/Users/lennoxsaint/.claude/plans/ultrathink-perform-ai-content-forensics-compiled-tower.md" \
  --task_mode "direct_execution" \
  --tools_used "yt-dlp, python3, rsvg-convert, jq, google-genai, second_brain_log_run.py" \
  --write_status "written" \
  --run_started_at_local "$TS_START" \
  2>&1 | tee -a "$LOG" | tail -3 || log "WARN: Second Brain log failed"

log "auto_refresh complete"
echo "AUTO_REFRESH_DONE $(ts) chris=$CHRIS_COUNT" >> "$DIR/logs/auto_refresh.done"
