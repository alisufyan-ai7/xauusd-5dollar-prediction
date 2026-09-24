#!/usr/bin/env bash
set -euo pipefail

FROM="${1:-2026-09-01}"
TO="${2:-2026-09-02}"
OUT="${3:-data/raw/dukascopy/xauusd/m1/xauusd-${FROM}-${TO}-m1.csv}"

mkdir -p "$(dirname "$OUT")"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# dukascopy-node writes the data file into --directory. Do not redirect stdout:
# stdout contains CLI/progress text and is not the CSV payload.
npx -y dukascopy-node@1.50.0 \
  -i xauusd \
  -from "$FROM" \
  -to "$TO" \
  -t m1 \
  -p bid \
  -v \
  -utc 0 \
  -f csv \
  -dir "$TMP_DIR"

SOURCE="$(find "$TMP_DIR" -maxdepth 1 -type f -name '*.csv' -print -quit)"
if [[ -z "${SOURCE:-}" ]]; then
  echo "DOWNLOAD_FAILED: no CSV produced in $TMP_DIR" >&2
  exit 1
fi

mv "$SOURCE" "$OUT"
python3 scripts/validate_m1.py "$OUT"

echo "Saved validated sample to: $OUT"
