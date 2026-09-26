#!/usr/bin/env bash
set -euo pipefail

START_YEAR="${1:-2016}"
END_YEAR="${2:-2025}"
BASE="${3:-data}"

if (( START_YEAR < 2003 || END_YEAR < START_YEAR )); then
  echo "invalid year range" >&2
  exit 2
fi

RAW_DIR="$BASE/raw/dukascopy/xauusd/m1"
MANIFEST="$BASE/manifests/exp001-history-manifest.json"
mkdir -p "$RAW_DIR" "$(dirname "$MANIFEST")"

files=()

for year in $(seq "$START_YEAR" "$END_YEAR"); do
  from="${year}-01-01"
  to="$((year+1))-01-01"
  out="$RAW_DIR/xauusd-${from}-${to}-m1.csv"

  echo "=== acquiring $year ==="
  bash scripts/download_xauusd_m1.sh "$from" "$to" "$out"
  files+=("$out")
done

python3 scripts/build_manifest.py "$MANIFEST" "${files[@]}"
echo "Manifest: $MANIFEST"
