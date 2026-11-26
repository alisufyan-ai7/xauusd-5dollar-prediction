#!/usr/bin/env bash
set -euo pipefail
INSTRUMENT="${1:?instrument id required}"
SIDE="${2:?side bid|ask required}"
FROM="${3:?from YYYY-MM-DD required}"
TO="${4:?to YYYY-MM-DD required}"
OUT="${5:?output csv required}"
LOG="${6:?diagnostic log required}"
CLASSIFICATION="${7:?classification json required}"
WAF_CACHE="${8:?ephemeral WAF cache path required}"
MODE="${9:-full}"

VERSION="1.51.1"
if [[ "$SIDE" != "bid" && "$SIDE" != "ask" ]]; then echo "side must be bid or ask" >&2; exit 2; fi
if [[ "$MODE" != "sanity" && "$MODE" != "full" ]]; then echo "mode must be sanity or full" >&2; exit 2; fi

mkdir -p "$(dirname "$OUT")" "$(dirname "$LOG")" "$(dirname "$CLASSIFICATION")" "$(dirname "$WAF_CACHE")"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
EXTRA=()
if [[ "$MODE" == "sanity" ]]; then EXTRA+=("-re"); fi

set +e
DEBUG='dukascopy-node:cli:version,dukascopy-node:cli:nodejs,dukascopy-node:cli:urls,dukascopy-node:cli:fetcher,dukascopy-node:waf,dukascopy-node:rate-limit' npx -y "dukascopy-node@$VERSION"   -i "$INSTRUMENT" -from "$FROM" -to "$TO" -t m1 -p "$SIDE" -v -utc 0 -f csv -dir "$TMP_DIR"   -r 0 --rate-limit-retries 0 --request-interval 0   --waf-mode auto --waf-timeout 60000 --waf-token-cache-path "$WAF_CACHE"   "${EXTRA[@]}" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e

python3 scripts/classify_stage3b_transport_log.py "$LOG" "$CLASSIFICATION"
if (( RC != 0 )); then
  echo "RECOVERY_TRANSPORT_COMMAND_FAILED:$INSTRUMENT:$SIDE:$FROM:$TO:rc=$RC" >&2
  exit "$RC"
fi

SOURCE="$(find "$TMP_DIR" -maxdepth 1 -type f -name '*.csv' -print -quit)"
if [[ -z "${SOURCE:-}" || ! -s "$SOURCE" ]]; then
  echo "RECOVERY_DOWNLOAD_FAILED_EMPTY:$INSTRUMENT:$SIDE:$FROM:$TO" | tee -a "$LOG" >&2
  python3 scripts/classify_stage3b_transport_log.py "$LOG" "$CLASSIFICATION"
  exit 1
fi

mv "$SOURCE" "$OUT"
python3 scripts/validate_m1.py "$OUT"
