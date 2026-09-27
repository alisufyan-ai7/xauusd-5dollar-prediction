#!/usr/bin/env bash
set -euo pipefail

SIDE="${1:?side bid|ask}"
FROM="${2:?from YYYY-MM-DD}"
TO="${3:?to YYYY-MM-DD}"
OUT="${4:?output csv}"

if [[ "$SIDE" != "bid" && "$SIDE" != "ask" ]]; then
  echo "side must be bid or ask" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT")"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

npx -y dukascopy-node@1.50.0   -i xauusd   -from "$FROM"   -to "$TO"   -t m1   -p "$SIDE"   -v   -utc 0   -f csv   -dir "$TMP_DIR"

SOURCE="$(find "$TMP_DIR" -maxdepth 1 -type f -name '*.csv' -print -quit)"
if [[ -z "${SOURCE:-}" ]]; then
  echo "DOWNLOAD_FAILED:$SIDE:$FROM:$TO" >&2
  exit 1
fi

mv "$SOURCE" "$OUT"
python3 scripts/validate_m1.py "$OUT"
