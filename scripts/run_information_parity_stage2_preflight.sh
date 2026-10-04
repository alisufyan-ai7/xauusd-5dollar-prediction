#!/usr/bin/env bash
set -euo pipefail

EXPECTED_NODE="v22.23.3"
EXPECTED_NPM="10.9.9"

if [[ "$(node --version)" != "$EXPECTED_NODE" ]]; then
  echo "STAGE2_NODE_VERSION_MISMATCH:expected=$EXPECTED_NODE:actual=$(node --version)" >&2
  exit 1
fi

if [[ "$(npm --version)" != "$EXPECTED_NPM" ]]; then
  echo "STAGE2_NPM_VERSION_MISMATCH:expected=$EXPECTED_NPM:actual=$(npm --version)" >&2
  exit 1
fi

python scripts/check_information_parity_stage2_repo_contract.py
python scripts/check_information_parity_stage2_environment.py

python -m py_compile   scripts/synchronize_information_parity_m1.py   scripts/build_synthetic_dxy_stage2.py   scripts/acquire_macro_schedule_stage2.py   scripts/build_information_parity_stage2_year.py   scripts/validate_information_parity_stage2.py   scripts/build_information_parity_manifest.py   scripts/check_information_parity_stage2_environment.py   scripts/check_information_parity_stage2_repo_contract.py   tests/test_information_parity_stage2_foundation.py   tests/test_information_parity_stage2_preflight.py

python tests/test_information_parity_stage2_foundation.py
python tests/test_information_parity_stage2_preflight.py

echo "INFORMATION_PARITY_STAGE2_PREFLIGHT_ALL_PASS"
