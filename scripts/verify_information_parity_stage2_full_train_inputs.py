#!/usr/bin/env python3
"""Verify static full-TRAIN prerequisites before provider acquisition.

This runs before any expensive 2016-2021 market download. It intentionally
checks only repository-controlled prerequisites, especially BLS schedule
snapshots needed when BLS blocks GitHub Actions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
YEARS = tuple(range(2016, 2022))
FAMILIES = ("CPI", "NFP", "JOLTS")

FIELDS = [
    "event_id",
    "event_family",
    "scheduled_time_utc",
    "scheduled_time_local",
    "source_timezone",
    "source_agency",
    "source_document_id_or_url",
    "release_stage",
    "historical_exception_flag",
    "normalization_version",
]


def fail(msg: str):
    raise SystemExit(f"STAGE2_FULL_INPUT_FAIL:{msg}")


def inspect_snapshot(path: Path, year: int) -> dict:
    if not path.exists():
        fail(f"missing_bls_snapshot:{year}:{path}")

    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if r.fieldnames != FIELDS:
            fail(f"bls_snapshot_schema:{year}:{r.fieldnames}")
        rows = list(r)

    seen_ids = set()
    seen_family_time = set()
    counts = {family: 0 for family in FAMILIES}
    official_prefix = f"https://www.bls.gov/schedule/{year}/"

    for row in rows:
        eid = row["event_id"]
        if not eid or eid in seen_ids:
            fail(f"bls_snapshot_event_id:{year}:{eid}")
        seen_ids.add(eid)

        fam = row["event_family"]
        if fam not in counts:
            fail(f"bls_snapshot_family:{year}:{fam}")
        if row["source_agency"] != "BLS":
            fail(f"bls_snapshot_agency:{year}:{row['source_agency']}")
        if row["source_timezone"] != "America/New_York":
            fail(f"bls_snapshot_timezone:{year}:{row['source_timezone']}")
        if not row["source_document_id_or_url"].startswith(official_prefix):
            fail(
                f"bls_snapshot_source:{year}:"
                f"{row['source_document_id_or_url']}"
            )

        local = datetime.fromisoformat(row["scheduled_time_local"])
        utc = datetime.fromisoformat(row["scheduled_time_utc"])
        if local.tzinfo is None or utc.tzinfo is None:
            fail(f"bls_snapshot_naive_time:{year}:{eid}")
        if local.astimezone(ET).year != year:
            fail(f"bls_snapshot_local_year:{year}:{eid}")
        if local.astimezone(timezone.utc) != utc.astimezone(timezone.utc):
            fail(f"bls_snapshot_utc_mismatch:{year}:{eid}")

        stage = row.get("release_stage", "")
        source = row["source_document_id_or_url"]
        token = (
            f"BLS|{fam}|{utc.astimezone(timezone.utc).isoformat()}|"
            f"{stage}|{source}"
        )
        expected_id = hashlib.sha256(token.encode()).hexdigest()[:20]
        if eid != expected_id:
            fail(
                f"bls_snapshot_event_id_hash:{year}:{eid}:"
                f"expected={expected_id}"
            )

        key = (fam, utc.astimezone(timezone.utc))
        if key in seen_family_time:
            fail(f"bls_snapshot_duplicate_family_time:{year}:{fam}:{utc}")
        seen_family_time.add(key)
        counts[fam] += 1

    for fam, count in counts.items():
        if count < 11:
            fail(f"bls_snapshot_count:{year}:{fam}:{count}")

    return {
        "path": str(path),
        "rows": len(rows),
        "counts": counts,
        "official_source_prefix": official_prefix,
    }


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        raise SystemExit(
            "usage: verify_information_parity_stage2_full_train_inputs.py "
            "<report.json>"
        )

    report_path = Path(argv[1])
    snapshots = {}
    for year in YEARS:
        path = Path(
            f"research/reference/information-parity-v1/"
            f"bls-schedule-{year}.csv"
        )
        snapshots[str(year)] = inspect_snapshot(path, year)

    report = {
        "status": "PASS",
        "schema_version": "IPV1_STAGE2_FULL_INPUTS_V1",
        "years": list(YEARS),
        "bls_snapshots": snapshots,
        "sealed_xauusd_periods_accessed": [],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
