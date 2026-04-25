#!/usr/bin/env bash
# Watcher: polls every 60s for the FINISHED CHRIS COLLECTION marker.
# When the marker appears, fires auto_refresh.sh exactly once and exits.
# Safe to launch with nohup. Self-terminates after a single trigger or on a 24h timeout.

set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$DIR/logs/watcher.log"
COLLECTION_LOG="$DIR/logs/chris_collection.log"
DONE_FLAG="$DIR/logs/auto_refresh.done"
mkdir -p "$DIR/logs"

ts() { date "+%Y-%m-%d %H:%M:%S %Z"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

if [[ -f "$DONE_FLAG" ]]; then
    log "auto_refresh.done already exists; nothing to do; exiting."
    exit 0
fi

log "watcher started; polling $COLLECTION_LOG every 60s for FINISHED CHRIS COLLECTION marker"

DEADLINE=$(( $(date +%s) + 24*60*60 ))   # 24h hard timeout

while true; do
    if [[ -f "$COLLECTION_LOG" ]] && grep -q "FINISHED CHRIS COLLECTION" "$COLLECTION_LOG"; then
        log "marker FOUND. firing auto_refresh.sh"
        nohup bash "$DIR/scripts/auto_refresh.sh" >> "$DIR/logs/auto_refresh.log" 2>&1 &
        log "auto_refresh launched (pid $!); watcher exiting."
        exit 0
    fi
    if (( $(date +%s) > DEADLINE )); then
        log "watcher 24h deadline reached without marker; exiting"
        exit 0
    fi
    sleep 60
done
