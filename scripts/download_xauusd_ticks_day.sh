#!/usr/bin/env bash
set -euo pipefail

DATE="$1"
OUT="$2"
NEXT="$(python3 - "$DATE" <<'PY'
import sys,datetime as dt
d=dt.date.fromisoformat(sys.argv[1])
print((d+dt.timedelta(days=1)).isoformat())
PY
)"

mkdir -p "$(dirname "$OUT")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

npx -y dukascopy-node@1.50.0   -i xauusd   -from "$DATE"   -to "$NEXT"   -t tick   -utc 0   -f csv   -dir "$TMP"

SOURCE="$(find "$TMP" -maxdepth 1 -type f -name '*.csv' -print -quit)"
if [[ -z "${SOURCE:-}" ]]; then
  echo "DOWNLOAD_FAILED:$DATE" >&2
  exit 1
fi
mv "$SOURCE" "$OUT"
python3 scripts/validate_dukascopy_ticks.py "$OUT"
