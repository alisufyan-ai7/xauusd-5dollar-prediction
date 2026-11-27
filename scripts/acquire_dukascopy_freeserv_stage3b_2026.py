#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

import stage3b_2026_freeserv_preflight as gate

AUTHORIZED_D148_DECISION_SHAS = frozenset()
PROVIDER_EXECUTION_ENABLED = False
HTTP_TIMEOUT_SECONDS = 45

OUTPUTS = {
    ("XAU/USD", "B"): "xauusd/xauusd-bid.csv",
    ("XAU/USD", "A"): "xauusd/xauusd-ask.csv",
    ("EUR/USD", "B"): "fx/eurusd-bid.csv",
    ("USD/JPY", "B"): "fx/usdjpy-bid.csv",
    ("GBP/USD", "B"): "fx/gbpusd-bid.csv",
    ("USD/CAD", "B"): "fx/usdcad-bid.csv",
    ("USD/SEK", "B"): "fx/usdsek-bid.csv",
    ("USD/CHF", "B"): "fx/usdchf-bid.csv",
}

class AcquisitionFailure(RuntimeError):
    pass


def require_execution_authorized(authorization_sha: str) -> None:
    if authorization_sha not in AUTHORIZED_D148_DECISION_SHAS:
        raise PermissionError("D-148 authorization SHA is not allowlisted")
    if not PROVIDER_EXECUTION_ENABLED:
        raise PermissionError("D-148 provider execution is disabled")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_once(
    spec: gate.RequestSpec,
    *,
    timeout: int = HTTP_TIMEOUT_SECONDS,
    opener=urllib.request.urlopen,
) -> tuple[int, bytes]:
    url = gate.build_url(spec)
    req = urllib.request.Request(url, headers=gate.request_headers())
    try:
        with opener(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", resp.getcode()))
            return status, resp.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()
    except Exception as exc:
        raise AcquisitionFailure(
            f"transport failure without retry for {spec.instrument}/{spec.side} cursor={spec.cursor_ms}: "
            f"{type(exc).__name__}: {exc}"
        ) from exc


def decode_response(spec: gate.RequestSpec, status: int, payload: bytes) -> list[gate.CandleRow]:
    if status != 200:
        raise AcquisitionFailure(
            f"HTTP {status} for {spec.instrument}/{spec.side} cursor={spec.cursor_ms}"
        )
    if not payload:
        raise AcquisitionFailure(
            f"empty payload for {spec.instrument}/{spec.side} cursor={spec.cursor_ms}"
        )
    callback = gate.request_params(spec)["jsonp"]
    try:
        raw = gate.parse_jsonp(payload, callback)
        rows = gate.decode_candle_rows(raw)
    except Exception as exc:
        raise AcquisitionFailure(
            f"decode failure for {spec.instrument}/{spec.side} cursor={spec.cursor_ms}: {exc}"
        ) from exc
    if not rows:
        raise AcquisitionFailure(
            f"zero rows for {spec.instrument}/{spec.side} cursor={spec.cursor_ms}"
        )
    return rows


def _enforce_raw_budget(raw_bytes: int) -> None:
    if raw_bytes > gate.MAX_RAW_BYTES:
        raise AcquisitionFailure(
            f"raw payload cap exceeded: {raw_bytes}>{gate.MAX_RAW_BYTES}"
        )


def sanity_phase(fetcher: Callable[[gate.RequestSpec], tuple[int, bytes]]) -> tuple[list[dict], int, int]:
    records = []
    raw_bytes = 0
    requests = 0
    for spec in gate.sanity_specs():
        if requests >= len(gate.sanity_specs()):
            raise AcquisitionFailure("sanity request budget exceeded")
        status, payload = fetcher(spec)
        requests += 1
        raw_bytes += len(payload)
        _enforce_raw_budget(raw_bytes)
        rows = decode_response(spec, status, payload)
        inside = gate.rows_inside_fence(rows)
        if not inside:
            raise AcquisitionFailure(
                f"sanity yielded no in-fence rows for {spec.instrument}/{spec.side}"
            )
        records.append({
            "instrument": spec.instrument,
            "side": spec.side,
            "cursor_ms": spec.cursor_ms,
            "limit": spec.limit,
            "status": status,
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
            "rows": len(rows),
            "first_timestamp": rows[0].timestamp,
            "last_timestamp": rows[-1].timestamp,
        })
    if requests != 8:
        raise AcquisitionFailure(f"sanity request count mismatch: {requests}")
    return records, requests, raw_bytes


def acquire_series(
    instrument: str,
    side: str,
    output_path: Path,
    fetcher: Callable[[gate.RequestSpec], tuple[int, bytes]],
    *,
    initial_raw_bytes: int = 0,
) -> tuple[dict, int]:
    if (instrument, side) not in gate.ALLOWED:
        raise PermissionError(f"unapproved series {instrument}/{side}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cursor = gate.START_MS
    first_page = True
    requests = 0
    raw_bytes = initial_raw_bytes
    written = 0
    page_records = []
    completed = False

    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(("timestamp", "open", "high", "low", "close", "volume"))

        while requests < gate.PROPOSED_MAX_FULL_REQUESTS_PER_SERIES:
            if not (gate.START_MS <= cursor < gate.END_EXCLUSIVE_MS):
                raise AcquisitionFailure(f"cursor escaped request fence: {cursor}")
            spec = gate.RequestSpec(instrument, side, cursor, gate.MAX_PAGE_LIMIT)
            status, payload = fetcher(spec)
            requests += 1
            raw_bytes += len(payload)
            _enforce_raw_budget(raw_bytes)
            rows = decode_response(spec, status, payload)
            normalized, new_cursor = gate.normalize_page(rows, cursor, first_page=first_page)
            first_page = False
            accepted = gate.rows_inside_fence(normalized)
            for row in accepted:
                writer.writerow(row.as_tuple())
            written += len(accepted)
            page_records.append({
                "request_index": requests,
                "cursor_ms": cursor,
                "status": status,
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
                "decoded_rows": len(rows),
                "accepted_rows": len(accepted),
                "first_timestamp": rows[0].timestamp,
                "last_timestamp": rows[-1].timestamp,
            })
            if any(row.timestamp >= gate.END_EXCLUSIVE_MS for row in normalized):
                completed = True
                break
            cursor = new_cursor

    if not completed:
        raise AcquisitionFailure(
            f"series did not reach end fence within {gate.PROPOSED_MAX_FULL_REQUESTS_PER_SERIES} requests: "
            f"{instrument}/{side}"
        )
    if written <= 0:
        raise AcquisitionFailure(f"series wrote zero in-fence rows: {instrument}/{side}")
    return {
        "instrument": instrument,
        "side": side,
        "requests": requests,
        "rows": written,
        "output": str(output_path),
        "pages": page_records,
    }, raw_bytes


def normalized_size(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*.csv") if p.is_file())


def run(
    output_root: Path,
    report_path: Path,
    authorization_sha: str,
    *,
    fetcher: Callable[[gate.RequestSpec], tuple[int, bytes]] = fetch_once,
) -> dict:
    require_execution_authorized(authorization_sha)
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    sanity, total_requests, raw_bytes = sanity_phase(fetcher)
    series_reports = []
    for instrument, side, _ in gate.SERIES:
        rel = OUTPUTS[(instrument, side)]
        report, raw_bytes = acquire_series(
            instrument,
            side,
            output_root / rel,
            fetcher,
            initial_raw_bytes=raw_bytes,
        )
        total_requests += report["requests"]
        if total_requests > gate.PROPOSED_MAX_TOTAL_REQUESTS:
            raise AcquisitionFailure(
                f"total request cap exceeded: {total_requests}>{gate.PROPOSED_MAX_TOTAL_REQUESTS}"
            )
        nbytes = normalized_size(output_root)
        if nbytes > gate.MAX_NORMALIZED_BYTES:
            raise AcquisitionFailure(
                f"normalized cap exceeded: {nbytes}>{gate.MAX_NORMALIZED_BYTES}"
            )
        series_reports.append(report)

    result = {
        "status": "PASS",
        "authorization_sha": authorization_sha,
        "source_representation": gate.SOURCE_REPRESENTATION,
        "window": [gate.START_ISO, gate.END_EXCLUSIVE_ISO],
        "sanity": sanity,
        "sanity_requests": len(sanity),
        "full_requests": sum(x["requests"] for x in series_reports),
        "total_requests": total_requests,
        "request_cap": gate.PROPOSED_MAX_TOTAL_REQUESTS,
        "raw_payload_bytes": raw_bytes,
        "raw_payload_cap": gate.MAX_RAW_BYTES,
        "normalized_bytes": normalized_size(output_root),
        "normalized_cap": gate.MAX_NORMALIZED_BYTES,
        "retries": 0,
        "series": series_reports,
    }
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str]) -> None:
    if len(argv) != 4:
        raise SystemExit(
            "usage: acquire_dukascopy_freeserv_stage3b_2026.py <output-root> <report.json> <authorization-sha>"
        )
    try:
        run(Path(argv[1]), Path(argv[2]), argv[3])
    except Exception as exc:
        print(f"D148_ACQUISITION_FAILURE:{type(exc).__name__}:{exc}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main(sys.argv)
