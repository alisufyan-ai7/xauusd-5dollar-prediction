#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-data}"
RAW="$BASE/raw/dukascopy/xauusd/m1-exp002"
SYNC="$BASE/raw/dukascopy/xauusd/m1-exp002-synchronized"
LAB="$BASE/labels/exp002"
PART="$BASE/partitioned/exp002"
mkdir -p "$SYNC/bid" "$SYNC/ask" "$LAB" "$PART"

for year in $(seq 2016 2024); do
  next=$((year+1))
  bid="$RAW/bid/xauusd-${year}-01-01-${next}-01-01-m1-bid.csv"
  ask="$RAW/ask/xauusd-${year}-01-01-${next}-01-01-m1-ask.csv"
  sbid="$SYNC/bid/xauusd-${year}-01-01-${next}-01-01-m1-bid.csv"
  sask="$SYNC/ask/xauusd-${year}-01-01-${next}-01-01-m1-ask.csv"
  labels="$LAB/labels-${year}.csv"
  partitioned="$PART/partitioned-${year}.csv"

  python3 scripts/synchronize_exp002_m1.py "$bid" "$ask" "$sbid" "$sask"

  case "$year" in
    2016|2017|2018|2019|2020|2023)
      n2=$((next+1))
      nb="$SYNC/bid/xauusd-${next}-01-01-${n2}-01-01-m1-bid.csv"
      na="$SYNC/ask/xauusd-${next}-01-01-${n2}-01-01-m1-ask.csv"
      if [[ ! -f "$nb" || ! -f "$na" ]]; then
        raw_nb="$RAW/bid/xauusd-${next}-01-01-${n2}-01-01-m1-bid.csv"
        raw_na="$RAW/ask/xauusd-${next}-01-01-${n2}-01-01-m1-ask.csv"
        python3 scripts/synchronize_exp002_m1.py "$raw_nb" "$raw_na" "$nb" "$na"
      fi
      python3 scripts/label_exp002.py "$sbid" "$sask" "$labels" "$nb" "$na"
      ;;
    *)
      python3 scripts/label_exp002.py "$sbid" "$sask" "$labels"
      ;;
  esac
  python3 scripts/partition_exp001.py "$labels" "$partitioned"
done
