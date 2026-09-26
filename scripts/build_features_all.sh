#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-data}"
RAW_DIR="$BASE/raw/dukascopy/xauusd/m1"
PART_DIR="$BASE/partitioned/exp001"
FEAT_DIR="$BASE/features/exp001"
mkdir -p "$FEAT_DIR"

for year in $(seq 2016 2024); do
  next=$((year+1))
  raw="$RAW_DIR/xauusd-${year}-01-01-${next}-01-01-m1.csv"
  part="$PART_DIR/partitioned-${year}.csv"
  feat="$FEAT_DIR/features-${year}.csv"
  [[ -f "$raw" ]] || { echo "missing raw $raw" >&2; exit 1; }
  [[ -f "$part" ]] || { echo "missing partitioned $part" >&2; exit 1; }
  python3 scripts/build_features.py "$raw" "$feat"
done

echo "FEATURE_BUILD_ALL_PASS"
