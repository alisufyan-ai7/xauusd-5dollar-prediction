#!/usr/bin/env bash
set -euo pipefail
WORK="${1:?work directory required}"
RAW="$WORK/raw"; DERIVED="$WORK/derived"; REPORTS="$WORK/reports"; MANIFESTS="$WORK/manifests"
mkdir -p "$RAW/xauusd" "$RAW/fx" "$DERIVED" "$REPORTS" "$MANIFESTS"
START="2026-06-01"; END="2026-10-09"; CAP_NORM=$((750*1024*1024))
python scripts/check_information_parity_stage3b_2026_environment.py
python - <<'PY'
import importlib.util,pathlib
p=pathlib.Path("scripts/stage3b_2026_execution_preflight.py")
s=importlib.util.spec_from_file_location("gate",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.require_owner_final_approval(m.proposed_acquisition_plan())
print("D124_EXECUTION_GATE_PASS")
PY
bash scripts/download_dukascopy_m1_generic.sh xauusd bid "$START" "$END" "$RAW/xauusd/xauusd-bid.csv"
bash scripts/download_dukascopy_m1_generic.sh xauusd ask "$START" "$END" "$RAW/xauusd/xauusd-ask.csv"
for inst in eurusd usdjpy gbpusd usdcad usdsek usdchf; do
  bash scripts/download_dukascopy_m1_generic.sh "$inst" bid "$START" "$END" "$RAW/fx/$inst-bid.csv"
done
python scripts/validate_stage3b_2026_provider_files.py "$MANIFESTS/raw-provider-manifest.json"   "XAUUSD_BID=$RAW/xauusd/xauusd-bid.csv" "XAUUSD_ASK=$RAW/xauusd/xauusd-ask.csv"   "EURUSD_BID=$RAW/fx/eurusd-bid.csv" "USDJPY_BID=$RAW/fx/usdjpy-bid.csv" "GBPUSD_BID=$RAW/fx/gbpusd-bid.csv"   "USDCAD_BID=$RAW/fx/usdcad-bid.csv" "USDSEK_BID=$RAW/fx/usdsek-bid.csv" "USDCHF_BID=$RAW/fx/usdchf-bid.csv"
python scripts/synchronize_information_parity_m1.py "$RAW/xauusd/xauusd-bid.csv" "$RAW/xauusd/xauusd-ask.csv" "$DERIVED/xauusd-synchronized.csv" > "$REPORTS/xauusd-sync.json"
python scripts/build_synthetic_dxy_stage2.py "$RAW/fx/eurusd-bid.csv" "$RAW/fx/usdjpy-bid.csv" "$RAW/fx/gbpusd-bid.csv" "$RAW/fx/usdcad-bid.csv" "$RAW/fx/usdsek-bid.csv" "$RAW/fx/usdchf-bid.csv" "$DERIVED/synthetic-dxy.csv" "$REPORTS/synthetic-dxy.json"
rm -rf "$RAW"
printf '{"status":"PASS","raw_deleted":true}\n' > "$REPORTS/raw-release.json"
python scripts/build_information_parity_stage3b_2026.py "$DERIVED/xauusd-synchronized.csv" "$DERIVED/synthetic-dxy.csv" "$DERIVED/layer" "$REPORTS/layer-build.json"
BYTES=$(du -sb "$DERIVED" | awk '{print $1}')
if (( BYTES > CAP_NORM )); then echo "STAGE3B_NORMALIZED_BUDGET:$BYTES>$CAP_NORM" >&2; exit 2; fi
python scripts/build_information_parity_manifest.py "$MANIFESTS/normalized-manifest.json" "$DERIVED/xauusd-synchronized.csv" "$DERIVED/synthetic-dxy.csv" "$DERIVED/layer/"*.csv.gz "$REPORTS/xauusd-sync.json" "$REPORTS/synthetic-dxy.json" "$REPORTS/layer-build.json"
printf '{"status":"PASS","normalized_bytes":%s,"cap":%s}\n' "$BYTES" "$CAP_NORM" > "$REPORTS/normalized-budget.json"
echo "STAGE3B_BOUNDED_ACQUISITION_BUILD_PASS"
