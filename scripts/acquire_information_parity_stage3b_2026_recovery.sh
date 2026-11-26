#!/usr/bin/env bash
set -euo pipefail
WORK="${1:?work directory required}"
RAW="$WORK/raw"; PRIVATE="$WORK/private"; DERIVED="$WORK/derived"; REPORTS="$WORK/reports"; MANIFESTS="$WORK/manifests"
mkdir -p "$RAW/xauusd" "$RAW/fx" "$PRIVATE" "$DERIVED" "$REPORTS" "$MANIFESTS"
trap 'rm -rf "$RAW" "$PRIVATE"' EXIT
START="2026-06-01"; END="2026-10-09"; CAP_RAW=$((350*1024*1024)); CAP_NORM=$((750*1024*1024))
WAF_CACHE="$PRIVATE/waf-token.json"

python scripts/check_information_parity_stage3b_2026_environment.py
python - <<'PY'
import importlib.util,pathlib
p=pathlib.Path("scripts/stage3b_2026_transport_recovery_preflight.py")
s=importlib.util.spec_from_file_location("gate",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.require_recovery_execution_ready(m.proposed_recovery_plan())
print("D134_RECOVERY_EXECUTION_GATE_PASS")
PY

# Same-attempt sanity request: one known weekday inside the frozen D-124 fence.
bash scripts/download_dukascopy_m1_recovery.sh xauusd bid 2026-06-01 2026-06-02   "$RAW/xauusd/xauusd-bid-sanity.csv" "$REPORTS/transport-sanity-xauusd-bid.log"   "$REPORTS/transport-sanity-xauusd-bid.json" "$WAF_CACHE" sanity
python scripts/record_stage3b_recovery_sanity.py "$RAW/xauusd/xauusd-bid-sanity.csv" "$REPORTS/transport-sanity-file.json"

# Full frozen acquisition; no model code runs until all eight inputs validate.
bash scripts/download_dukascopy_m1_recovery.sh xauusd bid "$START" "$END" "$RAW/xauusd/xauusd-bid.csv" "$REPORTS/transport-xauusd-bid.log" "$REPORTS/transport-xauusd-bid.json" "$WAF_CACHE" full
bash scripts/download_dukascopy_m1_recovery.sh xauusd ask "$START" "$END" "$RAW/xauusd/xauusd-ask.csv" "$REPORTS/transport-xauusd-ask.log" "$REPORTS/transport-xauusd-ask.json" "$WAF_CACHE" full
for inst in eurusd usdjpy gbpusd usdcad usdsek usdchf; do
  bash scripts/download_dukascopy_m1_recovery.sh "$inst" bid "$START" "$END" "$RAW/fx/$inst-bid.csv" "$REPORTS/transport-$inst-bid.log" "$REPORTS/transport-$inst-bid.json" "$WAF_CACHE" full
done

RAW_BYTES=$(du -sb "$RAW" | awk '{print $1}')
if (( RAW_BYTES > CAP_RAW )); then echo "STAGE3B_RECOVERY_RAW_BUDGET:$RAW_BYTES>$CAP_RAW" >&2; exit 2; fi
printf '{"status":"PASS","raw_bytes_including_sanity":%s,"cap":%s}\n' "$RAW_BYTES" "$CAP_RAW" > "$REPORTS/raw-budget.json"

python scripts/validate_stage3b_2026_provider_files.py "$MANIFESTS/raw-provider-manifest.json"   "XAUUSD_BID=$RAW/xauusd/xauusd-bid.csv" "XAUUSD_ASK=$RAW/xauusd/xauusd-ask.csv"   "EURUSD_BID=$RAW/fx/eurusd-bid.csv" "USDJPY_BID=$RAW/fx/usdjpy-bid.csv" "GBPUSD_BID=$RAW/fx/gbpusd-bid.csv"   "USDCAD_BID=$RAW/fx/usdcad-bid.csv" "USDSEK_BID=$RAW/fx/usdsek-bid.csv" "USDCHF_BID=$RAW/fx/usdchf-bid.csv"

python scripts/synchronize_information_parity_m1.py "$RAW/xauusd/xauusd-bid.csv" "$RAW/xauusd/xauusd-ask.csv" "$DERIVED/xauusd-synchronized.csv" > "$REPORTS/xauusd-sync.json"
python scripts/build_synthetic_dxy_stage2.py "$RAW/fx/eurusd-bid.csv" "$RAW/fx/usdjpy-bid.csv" "$RAW/fx/gbpusd-bid.csv" "$RAW/fx/usdcad-bid.csv" "$RAW/fx/usdsek-bid.csv" "$RAW/fx/usdchf-bid.csv" "$DERIVED/synthetic-dxy.csv" "$REPORTS/synthetic-dxy.json"
rm -rf "$RAW" "$PRIVATE"
trap - EXIT
printf '{"status":"PASS","raw_deleted":true,"waf_token_deleted":true}\n' > "$REPORTS/raw-release.json"

python scripts/build_information_parity_stage3b_2026.py "$DERIVED/xauusd-synchronized.csv" "$DERIVED/synthetic-dxy.csv" "$DERIVED/layer" "$REPORTS/layer-build.json"
BYTES=$(du -sb "$DERIVED" | awk '{print $1}')
if (( BYTES > CAP_NORM )); then echo "STAGE3B_NORMALIZED_BUDGET:$BYTES>$CAP_NORM" >&2; exit 2; fi
python scripts/build_information_parity_manifest.py "$MANIFESTS/normalized-manifest.json" "$DERIVED/xauusd-synchronized.csv" "$DERIVED/synthetic-dxy.csv" "$DERIVED/layer/"*.csv.gz "$REPORTS/xauusd-sync.json" "$REPORTS/synthetic-dxy.json" "$REPORTS/layer-build.json"
printf '{"status":"PASS","normalized_bytes":%s,"cap":%s}\n' "$BYTES" "$CAP_NORM" > "$REPORTS/normalized-budget.json"
echo "STAGE3B_D134_RECOVERY_ACQUISITION_BUILD_PASS"
