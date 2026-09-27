#!/usr/bin/env python3
import subprocess
import sys

subprocess.run(
    [sys.executable, "scripts/validate_m1.py", "tests/fixtures/xauusd_m1_valid.csv"],
    check=True,
)
print("smoke validation passed")
