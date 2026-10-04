#!/usr/bin/env python3
"""Fail fast if the Stage 2 runtime drifts from the frozen accepted-smoke env."""

from __future__ import annotations

import importlib.metadata
import platform
import sys
from pathlib import Path


LOCK = Path("requirements/information-parity-stage2.lock.txt")
EXPECTED_PYTHON = "3.12.14"


def parse_lock(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise SystemExit(f"UNPINNED_REQUIREMENT:{line}")
        name, version = line.split("==", 1)
        out[name.strip().lower()] = version.strip()
    return out


def main() -> None:
    if platform.python_version() != EXPECTED_PYTHON:
        raise SystemExit(
            "STAGE2_PYTHON_VERSION_MISMATCH:"
            f"expected={EXPECTED_PYTHON}:actual={platform.python_version()}"
        )

    expected = parse_lock(LOCK)
    mismatches = []
    for name, version in expected.items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            mismatches.append((name, version, "MISSING"))
            continue
        if actual != version:
            mismatches.append((name, version, actual))

    if mismatches:
        lines = [
            f"{name}:expected={want}:actual={actual}"
            for name, want, actual in mismatches
        ]
        raise SystemExit("STAGE2_ENVIRONMENT_DRIFT\n" + "\n".join(lines))

    print("INFORMATION_PARITY_STAGE2_ENVIRONMENT_PASS")
    print(f"python={platform.python_version()}")
    for name in sorted(expected):
        print(f"{name}={expected[name]}")


if __name__ == "__main__":
    main()
