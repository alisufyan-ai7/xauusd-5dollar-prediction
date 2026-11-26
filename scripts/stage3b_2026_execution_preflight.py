"""D-133 execution preflight after the single D-124 provider attempt was consumed.

No provider execution is authorized by this module. D-132 reached the first
provider request and returned a zero-byte XAUUSD BID file; all later steps
stopped. Any recovery requires a separately committed transport-recovery
decision and new pinned transport implementation.
"""
from __future__ import annotations
import hashlib
import importlib.metadata as metadata
import json
import platform
from pathlib import Path

SOURCE_SHA = "8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd"
FEATURE_SHA = "44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104"
FOLDS_SHA = "56a1c301cfebc78373793db10d7099aab9391b33e1470c869b714261ba677ec5"
START, END = "2026-06-01T00:00:00Z", "2026-10-09T00:00:00Z"
SYMBOLS = ("XAUUSD_BID", "XAUUSD_ASK", "EURUSD_BID", "USDJPY_BID", "GBPUSD_BID", "USDCAD_BID", "USDSEK_BID", "USDCHF_BID")
CAP_RAW = 350 * 1024 * 1024
CAP_NORMALIZED = 750 * 1024 * 1024
D124_AUTH = "c99ad84e4b7254d074b96df7a5f4c371ccbe01c2"
D132_EXECUTION = "707bdf424b4a810c93dc9ae7d30a07aff245582c"
ATTEMPT_CONSUMED = True
AUTHORIZED_FINAL_DECISION_SHAS = frozenset()
REQUIRED = {"scikit-learn":"1.8.0","scipy":"1.17.0","numpy":"2.5.3","pandas":"3.0.6","joblib":"1.5.3","threadpoolctl":"3.6.0"}

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_local_assets(teacher: Path, features: Path, folds: Path):
    for path, expected in ((teacher,SOURCE_SHA),(features,FEATURE_SHA),(folds,FOLDS_SHA)):
        if sha256_file(path) != expected:
            raise ValueError("asset SHA-256 mismatch: " + str(path))

def inspect_environment() -> dict:
    actual={}
    for name in REQUIRED:
        try:
            actual[name]=metadata.version(name)
        except metadata.PackageNotFoundError:
            actual[name]=None
    py=platform.python_version()
    return {"python":py,"packages":actual,"expected_python":"3.12.14","expected_packages":REQUIRED,
            "exact_runtime_pass":py=="3.12.14" and actual==REQUIRED}

def proposed_acquisition_plan() -> dict:
    return {
      "status":"ATTEMPT_CONSUMED_PROVIDER_TRANSPORT_FAILURE",
      "source":"owner-attested Dukascopy licence",
      "window":[START,END],
      "symbols":list(SYMBOLS),
      "max_raw_bytes":CAP_RAW,
      "max_normalized_bytes":CAP_NORMALIZED,
      "max_attempts":1,
      "attempts_consumed":1,
      "owner_final_approval_decision_sha":D124_AUTH,
      "consumed_execution_sha":D132_EXECUTION,
      "provider_requests_performed":1,
      "usable_provider_rows":0,
      "model_fit_performed":False,
      "raw_artifact_github_upload_allowed":False,
    }

def require_owner_final_approval(plan: dict) -> None:
    if ATTEMPT_CONSUMED:
        raise PermissionError("D124 provider attempt consumed by D132; new transport-recovery authorization required")
    raise PermissionError("no current provider execution authorization")

def save_plan(path: Path) -> None:
    path.write_text(json.dumps(proposed_acquisition_plan(),indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__ == "__main__":
    print(json.dumps({"status":"D133_ATTEMPT_CONSUMED_FAIL_CLOSED","runtime":inspect_environment(),"plan":proposed_acquisition_plan()},indent=2,sort_keys=True))
