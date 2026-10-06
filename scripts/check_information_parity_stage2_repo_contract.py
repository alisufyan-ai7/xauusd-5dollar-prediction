#!/usr/bin/env python3
"""Static repository-contract checks for Information Parity V1 Stage 2.

This is intentionally standard-library only so it can run before installing
third-party dependencies. It catches workflow/runtime/governance drift before
any CI or provider-data execution.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_LOCK = {
    "beautifulsoup4": "4.15.0",
    "certifi": "2026.7.22",
    "charset-normalizer": "3.5.2",
    "idna": "3.20",
    "numpy": "2.5.3",
    "pandas": "3.0.6",
    "python-dateutil": "2.9.0.post0",
    "requests": "2.34.2",
    "six": "1.17.0",
    "soupsieve": "2.10",
    "typing-extensions": "4.16.0",
    "urllib3": "2.8.0",
}

CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
SETUP_NODE_SHA = "49933ea5288caeca8642d1e84afbd3f7d6820020"
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"
UPLOAD_ARTIFACT_SHA = "ea165f8d65b6e75b540449e92b4886f43607fa02"


def fail(msg: str) -> None:
    raise SystemExit(f"STAGE2_REPO_CONTRACT_FAIL:{msg}")


def read(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        fail(f"missing_file:{path}")
    return p.read_text(encoding="utf-8")


def parse_lock(text: str) -> dict[str, str]:
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            fail(f"unlocked_requirement:{line}")
        name, version = line.split("==", 1)
        out[name.strip().lower()] = version.strip()
    return out


def require(text: str, needle: str, where: str) -> None:
    if needle not in text:
        fail(f"missing_contract:{where}:{needle}")


def forbid(text: str, needle: str, where: str) -> None:
    if needle in text:
        fail(f"forbidden_contract:{where}:{needle}")


def main() -> None:
    lock = parse_lock(read("requirements/information-parity-stage2.lock.txt"))
    if lock != EXPECTED_LOCK:
        fail(f"lock_mismatch:expected={EXPECTED_LOCK}:actual={lock}")

    preflight = read(".github/workflows/information-parity-stage2-preflight.yml")
    main_wf = read(".github/workflows/information-parity-stage2.yml")

    for name, text in (
        ("preflight_workflow", preflight),
        ("stage2_workflow", main_wf),
    ):
        require(text, "runs-on: ubuntu-24.04", name)
        require(text, 'node-version: "22.23.3"', name)
        require(text, 'python-version: "3.12.14"', name)
        require(
            text,
            "-r requirements/information-parity-stage2.lock.txt",
            name,
        )
        require(text, f"actions/checkout@{CHECKOUT_SHA}", name)
        require(text, f"actions/setup-node@{SETUP_NODE_SHA}", name)
        require(text, f"actions/setup-python@{SETUP_PYTHON_SHA}", name)
        forbid(text, "runs-on: ubuntu-latest", name)

    # The deterministic preflight is manual by default. During a deliberately
    # authorized CI confirmation, a push trigger is allowed only when it is
    # restricted to this isolated branch AND the single trigger file.
    require(preflight, "workflow_dispatch:", "preflight_workflow")
    forbid(preflight, "\n  pull_request:", "preflight_workflow")
    if "\n  push:" in preflight:
        require(
            preflight,
            "research/information-parity-v1-stage2-preflight",
            "preflight_workflow",
        )
        require(
            preflight,
            '".github/information-parity-stage2-preflight-trigger"',
            "preflight_workflow",
        )
    require(
        preflight,
        "bash scripts/run_information_parity_stage2_preflight.sh",
        "preflight_workflow",
    )

    # Provider-data workflow is manual-only and its action revision is pinned.
    require(main_wf, "workflow_dispatch:", "stage2_workflow")
    forbid(main_wf, "\n  push:", "stage2_workflow")
    forbid(main_wf, "\n  pull_request:", "stage2_workflow")
    require(
        main_wf,
        f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}",
        "stage2_workflow",
    )

    # Macro parser/network validation is a deliberately narrow manual gate.
    require(main_wf, "inputs.mode == 'macro-preflight'", "stage2_workflow")
    require(
        main_wf,
        "information-parity-stage2-macro-preflight",
        "stage2_workflow",
    )
    macro_section = main_wf.split("\n  macro-preflight:\n", 1)
    if len(macro_section) != 2:
        fail("missing_macro_preflight_job")
    macro_section = macro_section[1].split("\n  full-train:\n", 1)[0]
    require(
        macro_section,
        "Acquire and normalize 2016-2021 macro schedule only",
        "macro_preflight_job",
    )
    forbid(
        macro_section,
        "acquire_information_parity_stage2.sh",
        "macro_preflight_job",
    )

    # Full TRAIN orchestration must be continuous, same-snapshot, and bounded
    # strictly to the permitted 2016-2021 TRAIN interval.
    for needle in (
        "inputs.mode == 'full-train'",
        "timeout-minutes: 360",
        "verify_information_parity_stage2_full_train_inputs.py",
        "acquire_information_parity_stage2.sh 2016 2021",
        "build_synthetic_dxy_stage2_full_train.py",
        "build_information_parity_stage2_full_train.py",
        "validate_information_parity_stage2_full_train.py",
        "summarize_information_parity_stage2_full_train.py",
        "information-parity-stage2-full-train",
        "Release raw provider files after identities and DXY are frozen",
    ):
        require(main_wf, needle, "stage2_workflow")
    forbid(
        main_wf,
        "Full build intentionally blocked until smoke acceptance",
        "stage2_workflow",
    )

    full_train_section = main_wf.split("\n  full-train:\n", 1)
    if len(full_train_section) != 2:
        fail("missing_full_train_job")
    full_train_section = full_train_section[1]
    macro_gate = full_train_section.find(
        "Acquire and normalize 2016-2021 macro schedule"
    )
    market_gate = full_train_section.find(
        "Acquire one same-snapshot 2016-2021 market history"
    )
    if macro_gate < 0 or market_gate < 0 or macro_gate > market_gate:
        fail("full_train_macro_gate_must_precede_market_acquisition")

    downloader = read("scripts/download_dukascopy_m1_generic.sh")
    require(downloader, "dukascopy-node@1.50.0", "dukascopy_downloader")

    acquisition = read("scripts/acquire_information_parity_stage2.sh")
    require(
        acquisition,
        "START_YEAR < 2016 || END_YEAR > 2021",
        "stage2_acquisition",
    )
    require(
        acquisition,
        'tee "$REPORTS/xauusd-sync-${year}.json"',
        "stage2_acquisition",
    )
    require(
        acquisition,
        "build_information_parity_manifest.py",
        "stage2_acquisition",
    )

    for path in (
        "scripts/build_synthetic_dxy_stage2_full_train.py",
        "scripts/build_information_parity_stage2_full_train.py",
        "scripts/validate_information_parity_stage2_full_train.py",
        "scripts/verify_information_parity_stage2_full_train_inputs.py",
        "scripts/summarize_information_parity_stage2_full_train.py",
        "research/INFORMATION_PARITY_V1_STAGE2_FULL_TRAIN_CONTINUITY_ADDENDUM.md",
    ):
        read(path)

    macro = read("scripts/acquire_macro_schedule_stage2.py")
    require(
        macro,
        "start_year < 2016 or end_year > 2021",
        "macro_acquisition",
    )

    for needle in (
        "2021-press-fomc.htm",
        "def is_national_gdp_title",
        'suffix[0] in {",", ":", "("}',
    ):
        require(macro, needle, "macro_acquisition")

    validator = read("scripts/validate_information_parity_stage2.py")
    require(
        validator,
        "ALLOWED_YEARS = set(range(2016, 2022))",
        "stage2_validator",
    )
    require(
        validator,
        "SEALED_YEARS = {2022, 2023, 2024, 2025}",
        "stage2_validator",
    )

    test = read("tests/test_information_parity_stage2_preflight.py")
    for needle in (
        "future_return",
        "assert_session_dst",
        "assert_swing_and_fvg_causality",
        "load_bls_snapshot(2016)",
        "dxy_age_minutes",
        "xauusd_w1_2016.csv.gz",
        "Fomc2021FallbackFixture",
        "Gross Domestic Product: First Quarter 2018",
        "A.M., EDT",
    ):
        require(test, needle, "offline_preflight_test")

    print("INFORMATION_PARITY_STAGE2_REPO_CONTRACT_PASS")


if __name__ == "__main__":
    main()
