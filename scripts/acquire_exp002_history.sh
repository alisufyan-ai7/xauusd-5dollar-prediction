#!/usr/bin/env bash
set -euo pipefail

START_YEAR="${1:-2016}"
END_YEAR="${2:-2024}"
BASE="${3:-data}"

ROOT="$BASE/raw/dukascopy/xauusd/m1-exp002"
mkdir -p "$ROOT/bid" "$ROOT/ask" "$BASE/manifests"

files=()
for year in $(seq "$START_YEAR" "$END_YEAR"); do
  next=$((year+1))
  from="${year}-01-01"
  to="${next}-01-01"
  for side in bid ask; do
    out="$ROOT/$side/xauusd-${from}-${to}-m1-${side}.csv"
    echo "=== EXP-002 acquiring $side $year ==="
    bash scripts/download_xauusd_m1_side.sh "$side" "$from" "$to" "$out"
    files+=("$out")
  done
done

python3 scripts/build_manifest.py "$BASE/manifests/exp002-bidask-m1-manifest.json" "${files[@]}"
echo "Manifest: $BASE/manifests/exp002-bidask-m1-manifest.json"
