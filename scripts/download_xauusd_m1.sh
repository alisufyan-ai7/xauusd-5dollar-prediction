#!/usr/bin/env bash
set -euo pipefail

FROM="${1:-2026-09-01}"
TO="${2:-2026-09-02}"
OUT="${3:-data/raw/dukascopy/xauusd/m1/xauusd-${FROM}-${TO}-m1.csv}"

mkdir -p "$(dirname "$OUT")"

npx -y dukascopy-node@1.50.0 \
  -i xauusd \
  -from "$FROM" \
  -to "$TO" \
  -t m1 \
  -f csv > "$OUT"

python3 scripts/validate_m1.py "$OUT"

echo "Saved validated sample to: $OUT"
