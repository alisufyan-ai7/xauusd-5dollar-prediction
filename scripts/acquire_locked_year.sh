#!/usr/bin/env bash
set -euo pipefail
YEAR="${1:?year required}"
BASE="${2:-data}"
ATTEMPTS="${3:-3}"
NEXT=$((YEAR+1))
OUT="$BASE/raw/dukascopy/xauusd/m1/xauusd-${YEAR}-01-01-${NEXT}-01-01-m1.csv"
mkdir -p "$(dirname "$OUT")"

for attempt in $(seq 1 "$ATTEMPTS"); do
  echo "locked acquisition year=$YEAR attempt=$attempt/$ATTEMPTS"
  rm -f "$OUT"
  if bash scripts/download_xauusd_m1.sh "${YEAR}-01-01" "${NEXT}-01-01" "$OUT"; then
    if python3 scripts/verify_locked_year.py research/EXP-001_DATASET_LOCK.json "$YEAR" "$OUT"; then
      exit 0
    fi
  fi
  echo "attempt $attempt did not match locked dataset" >&2
done

echo "FAILED_TO_REPRODUCE_LOCKED_YEAR: $YEAR" >&2
exit 1
