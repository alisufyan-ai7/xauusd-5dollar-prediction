#!/usr/bin/env python3
"""Read-only Exness/MT5 historical tick availability probe.

This script only initializes the local MetaTrader 5 terminal, selects a symbol,
requests historical ticks, and writes local diagnostic files. It does not send,
modify, close, or inspect trading orders/positions.

Official MT5 Python functions used:
- initialize
- shutdown
- symbol_info
- symbol_select
- copy_ticks_range
- last_error
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

try:
    import MetaTrader5 as mt5
except ImportError:
    raise SystemExit(
        "MetaTrader5 package is not installed. Run: python -m pip install MetaTrader5"
    )

UTC = timezone.utc

DEFAULT_PROBES = [
    ("recent_2026", "2026-09-01T12:00:00+00:00"),
    ("jan_2025", "2025-01-15T12:00:00+00:00"),
    ("jan_2024", "2024-01-15T12:00:00+00:00"),
    ("jan_2023", "2023-01-16T12:00:00+00:00"),
    ("jan_2020", "2020-01-15T12:00:00+00:00"),
    ("jan_2016", "2016-01-15T12:00:00+00:00"),
]


@dataclass
class ProbeResult:
    label: str
    requested_from_utc: str
    requested_to_utc: str
    ticks: int
    first_tick_utc: str | None
    last_tick_utc: str | None
    valid_bid_ticks: int
    valid_ask_ticks: int
    valid_bid_ask_ticks: int
    spread_min: float | None
    spread_median: float | None
    spread_mean: float | None
    spread_p95: float | None
    spread_max: float | None
    mt5_error: list | None


def iso_from_msc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=UTC).isoformat()


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    w = pos - lo
    return xs[lo] * (1.0 - w) + xs[hi] * w


def probe(symbol: str, label: str, start: datetime, minutes: int) -> tuple[ProbeResult, list[dict]]:
    end = start + timedelta(minutes=minutes)
    ticks = mt5.copy_ticks_range(symbol, start, end, mt5.COPY_TICKS_INFO)

    if ticks is None:
        err = list(mt5.last_error())
        return ProbeResult(
            label=label,
            requested_from_utc=start.isoformat(),
            requested_to_utc=end.isoformat(),
            ticks=0,
            first_tick_utc=None,
            last_tick_utc=None,
            valid_bid_ticks=0,
            valid_ask_ticks=0,
            valid_bid_ask_ticks=0,
            spread_min=None,
            spread_median=None,
            spread_mean=None,
            spread_p95=None,
            spread_max=None,
            mt5_error=err,
        ), []

    rows = []
    spreads: list[float] = []
    valid_bid = valid_ask = valid_both = 0

    for t in ticks:
        bid = float(t["bid"])
        ask = float(t["ask"])
        if bid > 0:
            valid_bid += 1
        if ask > 0:
            valid_ask += 1
        if bid > 0 and ask > 0:
            valid_both += 1
            spreads.append(ask - bid)

        rows.append(
            {
                "time_msc": int(t["time_msc"]),
                "time_utc": iso_from_msc(int(t["time_msc"])),
                "bid": bid,
                "ask": ask,
                "spread": (ask - bid) if bid > 0 and ask > 0 else None,
                "flags": int(t["flags"]),
            }
        )

    first = rows[0]["time_utc"] if rows else None
    last = rows[-1]["time_utc"] if rows else None

    result = ProbeResult(
        label=label,
        requested_from_utc=start.isoformat(),
        requested_to_utc=end.isoformat(),
        ticks=len(rows),
        first_tick_utc=first,
        last_tick_utc=last,
        valid_bid_ticks=valid_bid,
        valid_ask_ticks=valid_ask,
        valid_bid_ask_ticks=valid_both,
        spread_min=min(spreads) if spreads else None,
        spread_median=statistics.median(spreads) if spreads else None,
        spread_mean=statistics.fmean(spreads) if spreads else None,
        spread_p95=percentile(spreads, 0.95),
        spread_max=max(spreads) if spreads else None,
        mt5_error=None,
    )
    return result, rows


def write_sample(path: Path, rows: Iterable[dict], max_rows: int = 250) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["time_msc", "time_utc", "bid", "ask", "spread", "flags"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, row in enumerate(rows):
            if i >= max_rows:
                break
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--terminal-path", default=None,
                    help="Optional full path to terminal64.exe; omit if MT5 is already discoverable.")
    ap.add_argument("--minutes", type=int, default=15,
                    help="Length of each small probe window. Default: 15.")
    ap.add_argument("--out-dir", default="exness_tick_probe")
    args = ap.parse_args()

    if args.minutes <= 0 or args.minutes > 120:
        raise SystemExit("--minutes must be between 1 and 120")

    init_ok = mt5.initialize(path=args.terminal_path) if args.terminal_path else mt5.initialize()
    if not init_ok:
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        info = mt5.symbol_info(args.symbol)
        if info is None:
            raise SystemExit(
                f"Symbol {args.symbol!r} not found in this terminal. "
                "Open Market Watch and confirm the exact Exness symbol name."
            )

        if not info.visible and not mt5.symbol_select(args.symbol, True):
            raise SystemExit(f"Could not select symbol {args.symbol!r}: {mt5.last_error()}")

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for label, start_iso in DEFAULT_PROBES:
            start = datetime.fromisoformat(start_iso).astimezone(UTC)
            result, rows = probe(args.symbol, label, start, args.minutes)
            results.append(asdict(result))
            write_sample(out_dir / f"{label}_sample.csv", rows)

        report = {
            "status": "PASS",
            "read_only": True,
            "symbol": args.symbol,
            "mt5_package_version": getattr(mt5, "__version__", None),
            "terminal_build": mt5.version(),
            "symbol_digits": int(info.digits),
            "symbol_point": float(info.point),
            "probe_minutes": args.minutes,
            "probes": results,
            "privacy_note": "Account login/number intentionally omitted.",
            "trading_note": "No order_send or trading mutation function is used by this script.",
        }

        report_path = out_dir / "exness_tick_probe_report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        print(json.dumps(report, indent=2, sort_keys=True))
        print(f"\nSaved report: {report_path.resolve()}")
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
