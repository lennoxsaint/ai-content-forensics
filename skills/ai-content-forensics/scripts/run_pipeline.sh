#!/usr/bin/env bash
# Re-runnable analysis pipeline. Safe to run while collection is in progress —
# operates only on what's been collected so far.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[$(date)] === Normalize ==="
python3 scripts/normalize.py

echo "[$(date)] === Features ==="
python3 scripts/features.py

echo "[$(date)] === Analyze ==="
python3 scripts/analyze.py

echo "[$(date)] === Done. Counts: ==="
echo "  videos in normalized/: $(find normalized/videos -mindepth 2 -maxdepth 2 -type d | wc -l)"
echo "  rows in 06_packaging_features.csv: $(($(wc -l < 06_packaging_features.csv) - 1))"
