#!/usr/bin/env bash
set -euo pipefail
YEAR="${1:?year required}"
BASE="${2:-data}"
NEXT=$((YEAR+1))
OUT="$BASE/raw/dukascopy/xauusd/m1/xauusd-${YEAR}-01-01-${NEXT}-01-01-m1.csv"
python3 scripts/reconstruct_locked_year.py "$YEAR" "$OUT" research/EXP-001_DATASET_LOCK.json
