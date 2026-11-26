"""D-121 zero-network, zero-model preflight. NOT a downloader or model runner.

The module intentionally has no data acquisition implementation. It permits
creation/audit of an acquisition plan, and refuses permission without an
independent final owner authorization recorded as a SHA-referenced decision.
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
REQUIRED = {"scikit-learn": "1.8.0", "scipy": "1.17.0", "numpy": "2.5.3", "pandas": "3.0.6", "joblib": "1.5.3", "threadpoolctl": "3.6.0"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_local_assets(teacher: Path, features: Path, folds: Path):
    for path, expected in ((teacher, SOURCE_SHA), (features, FEATURE_SHA), (folds, FOLDS_SHA)):
        if sha256_file(path) != expected:
            raise ValueError("asset SHA-256 mismatch: " + str(path))


def inspect_environment() -> dict:
    actual = {}
    for name in REQUIRED:
        try: actual[name] = metadata.version(name)
        except metadata.PackageNotFoundError: actual[name] = None
    py = platform.python_version()
    exact = py == "3.12.14" and actual == REQUIRED
    return {"python": py, "packages": actual, "expected_python": "3.12.14", "expected_packages": REQUIRED, "exact_runtime_pass": exact}


def proposed_acquisition_plan() -> dict:
    return {"status": "DESIGN_ONLY_NOT_APPROVED", "source": "owner-attested Dukascopy licence", "window": [START, END], "symbols": list(SYMBOLS), "max_raw_bytes": CAP_RAW, "max_normalized_bytes": CAP_NORMALIZED, "max_attempts": 1, "owner_final_approval_decision_sha": None, "provider_requests_performed": 0, "raw_artifact_github_upload_allowed": False}


def require_owner_final_approval(plan: dict) -> None:
    sha = plan.get("owner_final_approval_decision_sha")
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise PermissionError("no separately committed final owner approval decision")
    if plan.get("status") != "FINAL_APPROVED" or plan.get("window") != [START, END] or plan.get("symbols") != list(SYMBOLS):
        raise PermissionError("approved plan must match the exact frozen design")
    if plan.get("max_raw_bytes") != CAP_RAW or plan.get("max_normalized_bytes") != CAP_NORMALIZED or plan.get("max_attempts") != 1:
        raise PermissionError("budget differs from approved proposal")
    # Passing this check alone still does not download: this module has no network API.


def save_plan(path: Path) -> None:
    path.write_text(json.dumps(proposed_acquisition_plan(), indent=2, sort_keys=True)+"\n", encoding="utf-8")


if __name__ == "__main__":
    print(json.dumps({"status": "SOURCE_ONLY_NO_PROVIDER", "runtime": inspect_environment(), "plan": proposed_acquisition_plan()}, indent=2, sort_keys=True))
