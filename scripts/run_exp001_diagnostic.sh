#!/usr/bin/env bash
set -euo pipefail

FROM="${1:-2026-08-01}"
TO="${2:-2026-09-01}"
BASE="${3:-data}"

RAW="$BASE/raw/dukascopy/xauusd/m1/xauusd-${FROM}-${TO}-m1.csv"
LABELS="$BASE/results/exp001-${FROM}-${TO}-labels.csv"
REPORT="$BASE/results/exp001-${FROM}-${TO}-diagnostic.json"

bash scripts/download_xauusd_m1.sh "$FROM" "$TO" "$RAW"
python3 scripts/label_exp001.py "$RAW" "$LABELS"
python3 scripts/diagnose_exp001.py "$RAW" "$LABELS" "$REPORT"

echo "Diagnostic report: $REPORT"
