#!/usr/bin/env bash
set -euo pipefail

INSTRUMENT="${1:?instrument id required}"
SIDE="${2:?side bid|ask required}"
FROM="${3:?from YYYY-MM-DD required}"
TO="${4:?to YYYY-MM-DD required}"
OUT="${5:?output csv required}"

if [[ "$SIDE" != "bid" && "$SIDE" != "ask" ]]; then
  echo "side must be bid or ask" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT")"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

npx -y dukascopy-node@1.50.0 \
  -i "$INSTRUMENT" \
  -from "$FROM" \
  -to "$TO" \
  -t m1 \
  -p "$SIDE" \
  -v \
  -utc 0 \
  -f csv \
  -dir "$TMP_DIR"

SOURCE="$(find "$TMP_DIR" -maxdepth 1 -type f -name '*.csv' -print -quit)"
if [[ -z "${SOURCE:-}" ]]; then
  echo "DOWNLOAD_FAILED:$INSTRUMENT:$SIDE:$FROM:$TO" >&2
  exit 1
fi

mv "$SOURCE" "$OUT"
python3 scripts/validate_m1.py "$OUT"
