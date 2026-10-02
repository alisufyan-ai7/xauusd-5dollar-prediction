#!/usr/bin/env bash
set -euo pipefail

START_YEAR="${1:-2016}"
END_YEAR="${2:-2021}"
BASE="${3:-data}"

if (( START_YEAR < 2016 || END_YEAR > 2021 || START_YEAR > END_YEAR )); then
  echo "STAGE2_RANGE_VIOLATION: only 2016-2021 allowed" >&2
  exit 2
fi

RAW="$BASE/raw/information-parity-v1"
DERIVED="$BASE/derived/information-parity-v1"
MANIFEST="$BASE/manifests"
mkdir -p \
  "$RAW/xauusd/m1/bid" "$RAW/xauusd/m1/ask" \
  "$RAW/fx/m1/bid" \
  "$DERIVED/xauusd/m1" \
  "$MANIFEST"

FX=(eurusd usdjpy gbpusd usdcad usdsek usdchf)
raw_files=()
sync_files=()

for year in $(seq "$START_YEAR" "$END_YEAR"); do
  next=$((year+1))
  from="${year}-01-01"
  to="${next}-01-01"

  bid="$RAW/xauusd/m1/bid/xauusd-${from}-${to}-m1-bid.csv"
  ask="$RAW/xauusd/m1/ask/xauusd-${from}-${to}-m1-ask.csv"

  echo "=== Stage 2 acquiring XAUUSD BID/ASK $year ==="
  bash scripts/download_dukascopy_m1_generic.sh xauusd bid "$from" "$to" "$bid"
  bash scripts/download_dukascopy_m1_generic.sh xauusd ask "$from" "$to" "$ask"
  raw_files+=("$bid" "$ask")

  combined="$DERIVED/xauusd/m1/xauusd-${from}-${to}-m1-synchronized.csv"
  python3 scripts/synchronize_information_parity_m1.py "$bid" "$ask" "$combined"
  sync_files+=("$combined")

  for inst in "${FX[@]}"; do
    out="$RAW/fx/m1/bid/${inst}-${from}-${to}-m1-bid.csv"
    echo "=== Stage 2 acquiring $inst BID $year ==="
    bash scripts/download_dukascopy_m1_generic.sh "$inst" bid "$from" "$to" "$out"
    raw_files+=("$out")
  done
done

python3 scripts/build_manifest.py \
  "$MANIFEST/information-parity-v1-stage2-raw-market-manifest.json" \
  "${raw_files[@]}"

python3 scripts/build_manifest.py \
  "$MANIFEST/information-parity-v1-stage2-synchronized-xauusd-manifest.json" \
  "${sync_files[@]}"

echo "Stage 2 market acquisition complete: $START_YEAR-$END_YEAR"
