#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-data}"
RAW="$BASE/raw/dukascopy/xauusd/m1-exp002"
LAB="$BASE/labels/exp002"
PART="$BASE/partitioned/exp002"
mkdir -p "$LAB" "$PART"

for year in $(seq 2016 2024); do
  next=$((year+1))
  bid="$RAW/bid/xauusd-${year}-01-01-${next}-01-01-m1-bid.csv"
  ask="$RAW/ask/xauusd-${year}-01-01-${next}-01-01-m1-ask.csv"
  labels="$LAB/labels-${year}.csv"
  partitioned="$PART/partitioned-${year}.csv"

  case "$year" in
    2016|2017|2018|2019|2020|2023)
      n2=$((next+1))
      nb="$RAW/bid/xauusd-${next}-01-01-${n2}-01-01-m1-bid.csv"
      na="$RAW/ask/xauusd-${next}-01-01-${n2}-01-01-m1-ask.csv"
      python3 scripts/label_exp002.py "$bid" "$ask" "$labels" "$nb" "$na"
      ;;
    *)
      python3 scripts/label_exp002.py "$bid" "$ask" "$labels"
      ;;
  esac
  python3 scripts/partition_exp001.py "$labels" "$partitioned"
done
