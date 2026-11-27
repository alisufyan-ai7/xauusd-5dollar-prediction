#!/usr/bin/env bash
set -euo pipefail
WORK="${1:?work directory required}"
RAW="$WORK/raw"; DERIVED="$WORK/derived"; REPORTS="$WORK/reports"; MANIFESTS="$WORK/manifests"
mkdir -p "$RAW/xauusd" "$RAW/fx" "$DERIVED" "$REPORTS" "$MANIFESTS"
CAP_NORM=$((750*1024*1024))

check_intermediate_budget() {
  local bytes
  bytes=$(du -sb "$RAW" "$DERIVED" 2>/dev/null | awk '{s+=$1} END{print s+0}')
  if (( bytes > CAP_NORM )); then
    echo "STAGE3B_D140_NORMALIZED_INTERMEDIATE_BUDGET:${bytes}>${CAP_NORM}" >&2
    exit 2
  fi
  printf '{"status":"PASS","normalized_intermediate_bytes":%s,"cap":%s}\n' "$bytes" "$CAP_NORM" > "$REPORTS/normalized-intermediate-budget.json"
}

python scripts/check_information_parity_stage3b_2026_environment.py
python scripts/acquire_dukascopy_public_datafeed_stage3b_2026.py "$RAW" "$REPORTS/public-datafeed-acquisition.json"

python scripts/validate_stage3b_2026_provider_files.py "$MANIFESTS/raw-provider-manifest.json" \
  "XAUUSD_BID=$RAW/xauusd/xauusd-bid.csv" "XAUUSD_ASK=$RAW/xauusd/xauusd-ask.csv" \
  "EURUSD_BID=$RAW/fx/eurusd-bid.csv" "USDJPY_BID=$RAW/fx/usdjpy-bid.csv" "GBPUSD_BID=$RAW/fx/gbpusd-bid.csv" \
  "USDCAD_BID=$RAW/fx/usdcad-bid.csv" "USDSEK_BID=$RAW/fx/usdsek-bid.csv" "USDCHF_BID=$RAW/fx/usdchf-bid.csv"
check_intermediate_budget

python scripts/synchronize_information_parity_m1.py "$RAW/xauusd/xauusd-bid.csv" "$RAW/xauusd/xauusd-ask.csv" "$DERIVED/xauusd-synchronized.csv" > "$REPORTS/xauusd-sync.json"
python scripts/build_synthetic_dxy_stage2.py "$RAW/fx/eurusd-bid.csv" "$RAW/fx/usdjpy-bid.csv" "$RAW/fx/gbpusd-bid.csv" "$RAW/fx/usdcad-bid.csv" "$RAW/fx/usdsek-bid.csv" "$RAW/fx/usdchf-bid.csv" "$DERIVED/synthetic-dxy.csv" "$REPORTS/synthetic-dxy.json"
check_intermediate_budget

rm -rf "$RAW"
printf '{"status":"PASS","provider_csv_deleted":true}\n' > "$REPORTS/raw-release.json"
python scripts/build_information_parity_stage3b_2026.py "$DERIVED/xauusd-synchronized.csv" "$DERIVED/synthetic-dxy.csv" "$DERIVED/layer" "$REPORTS/layer-build.json"
BYTES=$(du -sb "$DERIVED" | awk '{print $1}')
if (( BYTES > CAP_NORM )); then echo "STAGE3B_D140_NORMALIZED_BUDGET:${BYTES}>${CAP_NORM}" >&2; exit 2; fi
python scripts/build_information_parity_manifest.py "$MANIFESTS/normalized-manifest.json" "$DERIVED/xauusd-synchronized.csv" "$DERIVED/synthetic-dxy.csv" "$DERIVED/layer/"*.csv.gz "$REPORTS/xauusd-sync.json" "$REPORTS/synthetic-dxy.json" "$REPORTS/layer-build.json"
printf '{"status":"PASS","normalized_bytes":%s,"cap":%s}\n' "$BYTES" "$CAP_NORM" > "$REPORTS/normalized-budget.json"
echo "STAGE3B_D140_BOUNDED_ACQUISITION_BUILD_PASS"
