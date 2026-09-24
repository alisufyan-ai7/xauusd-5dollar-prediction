#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-data}"
RAW_DIR="$BASE/raw/dukascopy/xauusd/m1"
LABEL_DIR="$BASE/labels/exp001"
PART_DIR="$BASE/partitioned/exp001"
REPORT_DIR="$BASE/reports/exp001"
mkdir -p "$LABEL_DIR" "$PART_DIR" "$REPORT_DIR"

for year in $(seq 2016 2025); do
  next=$((year+1))
  raw="$RAW_DIR/xauusd-${year}-01-01-${next}-01-01-m1.csv"
  labels="$LABEL_DIR/labels-${year}.csv"
  partitioned="$PART_DIR/partitioned-${year}.csv"

  if [[ ! -f "$raw" ]]; then
    echo "MISSING_REQUIRED_RAW_YEAR: $raw" >&2
    exit 1
  fi

  python3 scripts/label_exp001.py "$raw" "$labels"
  python3 scripts/partition_exp001.py "$labels" "$partitioned"
done

python3 scripts/summarize_partitions.py "$REPORT_DIR/partition-summary.json" "$PART_DIR"/partitioned-*.csv
echo "Partition summary: $REPORT_DIR/partition-summary.json"
