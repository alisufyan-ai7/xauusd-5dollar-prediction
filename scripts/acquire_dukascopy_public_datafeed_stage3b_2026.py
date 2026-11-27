#!/usr/bin/env python3
"""D-144 one-attempt credential-free Dukascopy direct-M1 acquisition.

Transport only. Scientific scope is frozen by D-124/D-140. No retries, no
alternate host/source, and the D-146 one-time attempt is consumed after a TLS connection reset on the first sanity request; provider execution is now fail-closed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import timedelta
from pathlib import Path

import decode_dukascopy_datafeed_m1 as decoder
import stage3b_2026_public_datafeed_preflight as gate

D144_AUTHORIZATION_SHA = "eb05ac27af18f68232d86a9148597aa565688709"
AUTHORIZED_D140_DECISION_SHAS = frozenset()
SOURCE_REPRESENTATION = "DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1"
PROVIDER_EXECUTION_ENABLED = False
USER_AGENT = "xauusd-stage3b-d140/1.0"

SERIES = (
    ("XAUUSD", "BID", "xauusd/xauusd-bid.csv"),
    ("XAUUSD", "ASK", "xauusd/xauusd-ask.csv"),
    ("EURUSD", "BID", "fx/eurusd-bid.csv"),
    ("USDJPY", "BID", "fx/usdjpy-bid.csv"),
    ("GBPUSD", "BID", "fx/gbpusd-bid.csv"),
    ("USDCAD", "BID", "fx/usdcad-bid.csv"),
    ("USDSEK", "BID", "fx/usdsek-bid.csv"),
    ("USDCHF", "BID", "fx/usdchf-bid.csv"),
)

class AcquisitionFailure(RuntimeError):
    pass


def require_execution_authorized(auth_sha: str = D144_AUTHORIZATION_SHA) -> None:
    if auth_sha not in AUTHORIZED_D140_DECISION_SHAS:
        raise PermissionError("D-140 authorization SHA not allowlisted")
    if not PROVIDER_EXECUTION_ENABLED:
        raise PermissionError("D-140/D-144 attempt consumed by D-146; no rerun authorized")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_once(url: str, timeout: int = 45, opener=urllib.request.urlopen) -> tuple[int, bytes]:
    if not url.startswith(gate.URL_ROOT + "/"):
        raise PermissionError("alternate host/source forbidden")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with opener(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", resp.getcode()))
            body = resp.read()
            return status, body
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()
    except Exception as exc:
        raise AcquisitionFailure(f"network error without retry for {url}: {type(exc).__name__}: {exc}") from exc


def iter_full_specs():
    d = gate.START
    while d < gate.END_EXCLUSIVE:
        for instrument, side, _ in SERIES:
            yield gate.RequestSpec(instrument, side, d)
        d += timedelta(days=1)


def output_path(raw_root: Path, instrument: str, side: str) -> Path:
    key = (instrument.upper(), side.upper())
    for i, s, rel in SERIES:
        if (i, s) == key:
            return raw_root / rel
    raise PermissionError(f"unapproved series: {instrument}/{side}")


def run(raw_root: Path, report_path: Path) -> dict:
    require_execution_authorized()
    raw_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    get_count = 0
    raw_bytes = 0
    status_counts = Counter()
    sanity_records = []
    missing = []
    per_series_rows = Counter()

    # Phase 1: exactly eight June 1 sanity GETs. Any failure consumes/stops attempt.
    for spec in gate.sanity_specs():
        gate.validate_request(spec)
        if get_count >= gate.MAX_GETS:
            raise AcquisitionFailure("GET cap before sanity completion")
        url = gate.build_url(spec)
        status, payload = fetch_once(url)
        get_count += 1; raw_bytes += len(payload); status_counts[str(status)] += 1
        if raw_bytes > gate.MAX_RAW_BYTES:
            raise AcquisitionFailure("raw byte cap exceeded during sanity")
        if status != 200 or not payload:
            raise AcquisitionFailure(f"sanity failed {spec.instrument}/{spec.side}: HTTP {status}, bytes={len(payload)}")
        try:
            rows = decoder.decode_payload(payload, spec.instrument, spec.day)
        except Exception as exc:
            raise AcquisitionFailure(f"sanity decode failed {spec.instrument}/{spec.side}: {exc}") from exc
        if not rows:
            raise AcquisitionFailure(f"sanity decoded zero rows {spec.instrument}/{spec.side}")
        sanity_records.append({"instrument":spec.instrument,"side":spec.side,"day":spec.day.isoformat(),"url":url,"http_status":status,"bytes":len(payload),"sha256":sha256_bytes(payload),"rows":len(rows)})
    if get_count != 8:
        raise AcquisitionFailure(f"sanity GET count mismatch: {get_count}")

    handles = {}; writers = {}
    try:
        for instrument, side, rel in SERIES:
            path = raw_root / rel; path.parent.mkdir(parents=True, exist_ok=True)
            fh = path.open("w", encoding="utf-8", newline="")
            writer = csv.writer(fh, lineterminator="\n"); writer.writerow(decoder.COLUMNS)
            handles[(instrument,side)] = fh; writers[(instrument,side)] = writer

        # Phase 2: all 1,040 frozen daily opportunities. No retry.
        full_gets = 0
        for spec in iter_full_specs():
            gate.validate_request(spec)
            if get_count >= gate.MAX_GETS:
                raise AcquisitionFailure(f"GET cap exceeded before {spec}")
            url = gate.build_url(spec)
            status, payload = fetch_once(url)
            get_count += 1; full_gets += 1; raw_bytes += len(payload); status_counts[str(status)] += 1
            if raw_bytes > gate.MAX_RAW_BYTES:
                raise AcquisitionFailure("raw byte cap exceeded")
            if status in (403, 429) or status >= 500:
                raise AcquisitionFailure(f"provider failure without retry: HTTP {status} for {url}")
            if status != 200 or not payload:
                missing.append({"instrument":spec.instrument,"side":spec.side,"day":spec.day.isoformat(),"url":url,"http_status":status,"bytes":len(payload)})
                continue
            try:
                rows = decoder.decode_payload(payload, spec.instrument, spec.day)
            except Exception as exc:
                raise AcquisitionFailure(f"invalid nonempty payload for {url}: {exc}") from exc
            w = writers[(spec.instrument, spec.side)]
            for row in rows:
                w.writerow(row.as_tuple())
            per_series_rows[f"{spec.instrument}_{spec.side}"] += len(rows)
        if full_gets != gate.full_request_count():
            raise AcquisitionFailure(f"full GET count mismatch: {full_gets}")
    finally:
        for fh in handles.values(): fh.close()

    if get_count != 8 + gate.full_request_count():
        raise AcquisitionFailure(f"total GET count mismatch: {get_count}")
    if get_count > gate.MAX_GETS:
        raise AcquisitionFailure(f"GET cap exceeded: {get_count}")

    report = {
        "status":"PASS",
        "authorization_sha":D144_AUTHORIZATION_SHA,
        "source_representation":SOURCE_REPRESENTATION,
        "provider_host":"datafeed.dukascopy.com",
        "window":[gate.START.isoformat(),gate.END_EXCLUSIVE.isoformat()],
        "sanity_gets":8,
        "full_gets":gate.full_request_count(),
        "total_gets":get_count,
        "hard_get_cap":gate.MAX_GETS,
        "raw_payload_bytes":raw_bytes,
        "raw_payload_cap":gate.MAX_RAW_BYTES,
        "retries":0,
        "alternate_host_or_source_used":False,
        "status_counts":dict(sorted(status_counts.items())),
        "sanity":sanity_records,
        "missing_objects":missing,
        "missing_object_count":len(missing),
        "rows_by_series":dict(sorted(per_series_rows.items())),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("sanity","missing_objects")}, indent=2, sort_keys=True))
    return report


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: acquire_dukascopy_public_datafeed_stage3b_2026.py <raw-root> <report.json>")
    try:
        run(Path(argv[1]), Path(argv[2]))
    except Exception as exc:
        print(f"D140_ACQUISITION_FAILURE:{type(exc).__name__}:{exc}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main(sys.argv)
