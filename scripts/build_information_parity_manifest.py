#!/usr/bin/env python3
"""Build a compact hash/row-count manifest for Stage 2 files.

Supports CSV, CSV.GZ, JSON and arbitrary files. It never copies raw data.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

TS_FIELDS = (
    "timestamp",
    "timestamp_ms",
    "decision_time_ms",
    "dxy_bar_start_ms",
    "dxy_available_time_ms",
    "available_time_ms",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_csv(path: Path) -> dict:
    opener = gzip.open if path.name.endswith(".gz") else open
    rows = 0
    first = None
    last = None
    fields = None
    with opener(path, "rt", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        ts_field = next((x for x in TS_FIELDS if x in fields), None)
        for row in r:
            rows += 1
            if ts_field and row.get(ts_field, "") != "":
                try:
                    ts = int(float(row[ts_field]))
                    if first is None:
                        first = ts
                    last = ts
                except ValueError:
                    pass
    return {
        "rows": rows,
        "columns": fields,
        "timestamp_field": next((x for x in TS_FIELDS if x in (fields or [])), None),
        "first_timestamp_like": first,
        "last_timestamp_like": last,
    }


def inspect(path: Path) -> dict:
    entry = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if path.name.endswith(".csv") or path.name.endswith(".csv.gz"):
        entry.update(inspect_csv(path))
    elif path.suffix == ".json":
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            entry["json_top_level_type"] = type(obj).__name__
            if isinstance(obj, dict):
                entry["json_keys"] = sorted(obj.keys())
        except Exception as e:
            entry["json_parse_error"] = str(e)
    return entry


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        raise SystemExit(
            "usage: build_information_parity_manifest.py "
            "<out.json> <file> [<file> ...]"
        )
    out = Path(argv[1])
    files = [Path(x) for x in argv[2:]]
    missing = [str(x) for x in files if not x.exists()]
    if missing:
        raise SystemExit(f"MISSING_MANIFEST_FILES:{missing}")
    entries = [inspect(p) for p in files]
    manifest = {
        "schema_version": "IPV1_FILE_MANIFEST_V1",
        "files": entries,
        "file_count": len(entries),
        "total_bytes": sum(x["bytes"] for x in entries),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
