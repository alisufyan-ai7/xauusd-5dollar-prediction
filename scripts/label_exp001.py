#!/usr/bin/env python3
"""EXP-001 deterministic M1 barrier labeling.

Decision semantics
------------------
For row i:
- decision price P(t) = close of row i;
- decision time = end of row i = timestamp + 60_000 ms;
- future scanning starts at row i+1;
- at most the next 60 chronological M1 bars are eligible;
- BUY target = P + 5, BUY adverse = P - 3;
- SELL target = P - 5, SELL adverse = P + 3.

If both target and adverse barrier for the same direction are touched inside the
same M1 bar, ordering is unknowable from OHLC and the directional label is
AMBIGUOUS. It is never guessed.

Gaps in the source are allowed in the input but shorten calendar coverage:
only bars whose start timestamp is strictly before decision_time + horizon are
eligible. Thus a 60-bar count cannot silently extend beyond 60 calendar minutes.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ONE_MINUTE_MS = 60_000
DEFAULT_TARGET = 5.0
DEFAULT_ADVERSE = 3.0
DEFAULT_HORIZON_MINUTES = 60

INPUT_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
OUTPUT_COLUMNS = [
    "timestamp",
    "decision_time_ms",
    "reference_price",
    "buy_label",
    "buy_terminal_bar_offset",
    "buy_terminal_bar_timestamp_ms",
    "buy_mfe",
    "buy_mae",
    "sell_label",
    "sell_terminal_bar_offset",
    "sell_terminal_bar_timestamp_ms",
    "sell_mfe",
    "sell_mae",
    "bars_observed",
    "coverage_complete",
]


@dataclass(frozen=True)
class Bar:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


def _finite_float(value: str, field: str, row_num: int) -> float:
    try:
        out = float(value)
    except ValueError as exc:
        raise ValueError(f"row {row_num}: {field} is not numeric") from exc
    if not math.isfinite(out):
        raise ValueError(f"row {row_num}: {field} is not finite")
    return out


def load_m1(path: Path) -> list[Bar]:
    bars: list[Bar] = []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != INPUT_COLUMNS:
            raise ValueError(
                f"unexpected columns {reader.fieldnames!r}; expected {INPUT_COLUMNS!r}"
            )
        previous = None
        for row_num, row in enumerate(reader, start=2):
            try:
                ts = int(row["timestamp"])
            except ValueError as exc:
                raise ValueError(f"row {row_num}: timestamp is not integer ms") from exc
            if ts % ONE_MINUTE_MS:
                raise ValueError(f"row {row_num}: timestamp not M1 aligned")
            if previous is not None and ts <= previous:
                raise ValueError(f"row {row_num}: timestamps must be strictly increasing")
            b = Bar(
                timestamp=ts,
                open=_finite_float(row["open"], "open", row_num),
                high=_finite_float(row["high"], "high", row_num),
                low=_finite_float(row["low"], "low", row_num),
                close=_finite_float(row["close"], "close", row_num),
                volume=_finite_float(row["volume"], "volume", row_num),
            )
            if min(b.open, b.high, b.low, b.close) <= 0:
                raise ValueError(f"row {row_num}: prices must be positive")
            if b.high < max(b.open, b.close) or b.low > min(b.open, b.close) or b.high < b.low:
                raise ValueError(f"row {row_num}: invalid OHLC relationship")
            if b.volume < 0:
                raise ValueError(f"row {row_num}: negative volume")
            bars.append(b)
            previous = ts
    if not bars:
        raise ValueError("input contains no bars")
    return bars


def _direction_label(
    future: list[Bar],
    reference: float,
    direction: str,
    target_distance: float,
    adverse_distance: float,
) -> tuple[str, int | None, int | None, float, float]:
    if direction == "BUY":
        target = reference + target_distance
        adverse = reference - adverse_distance
    elif direction == "SELL":
        target = reference - target_distance
        adverse = reference + adverse_distance
    else:
        raise ValueError("direction must be BUY or SELL")

    mfe = 0.0
    mae = 0.0

    for offset, bar in enumerate(future, start=1):
        if direction == "BUY":
            favorable = max(0.0, bar.high - reference)
            adverse_exc = max(0.0, reference - bar.low)
            hit_target = bar.high >= target
            hit_adverse = bar.low <= adverse
        else:
            favorable = max(0.0, reference - bar.low)
            adverse_exc = max(0.0, bar.high - reference)
            hit_target = bar.low <= target
            hit_adverse = bar.high >= adverse

        mfe = max(mfe, favorable)
        mae = max(mae, adverse_exc)

        if hit_target and hit_adverse:
            return "AMBIGUOUS", offset, bar.timestamp, mfe, mae
        if hit_target:
            return "SUCCESS", offset, bar.timestamp, mfe, mae
        if hit_adverse:
            return "FAILURE", offset, bar.timestamp, mfe, mae

    return "UNRESOLVED", None, None, mfe, mae


def label_rows(
    bars: list[Bar],
    *,
    target_distance: float = DEFAULT_TARGET,
    adverse_distance: float = DEFAULT_ADVERSE,
    horizon_minutes: int = DEFAULT_HORIZON_MINUTES,
) -> Iterable[dict]:
    if target_distance <= 0 or adverse_distance <= 0 or horizon_minutes <= 0:
        raise ValueError("target, adverse, and horizon must be positive")

    horizon_ms = horizon_minutes * ONE_MINUTE_MS

    for i, current in enumerate(bars):
        decision_time = current.timestamp + ONE_MINUTE_MS
        horizon_end = decision_time + horizon_ms

        future: list[Bar] = []
        j = i + 1
        while j < len(bars) and bars[j].timestamp < horizon_end:
            future.append(bars[j])
            j += 1

        # Complete coverage means the source reaches the final eligible M1 bar
        # at horizon_end - 1 minute. Weekend/session gaps correctly fail this.
        expected_last_start = horizon_end - ONE_MINUTE_MS
        coverage_complete = bool(future) and future[-1].timestamp == expected_last_start

        buy = _direction_label(
            future, current.close, "BUY", target_distance, adverse_distance
        )
        sell = _direction_label(
            future, current.close, "SELL", target_distance, adverse_distance
        )

        yield {
            "timestamp": current.timestamp,
            "decision_time_ms": decision_time,
            "reference_price": current.close,
            "buy_label": buy[0],
            "buy_terminal_bar_offset": buy[1],
            "buy_terminal_bar_timestamp_ms": buy[2],
            "buy_mfe": round(buy[3], 10),
            "buy_mae": round(buy[4], 10),
            "sell_label": sell[0],
            "sell_terminal_bar_offset": sell[1],
            "sell_terminal_bar_timestamp_ms": sell[2],
            "sell_mfe": round(sell[3], 10),
            "sell_mae": round(sell[4], 10),
            "bars_observed": len(future),
            "coverage_complete": coverage_complete,
        }


def write_labels(input_path: Path, output_path: Path) -> dict:
    bars = load_m1(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {
        "buy": {"SUCCESS": 0, "FAILURE": 0, "UNRESOLVED": 0, "AMBIGUOUS": 0},
        "sell": {"SUCCESS": 0, "FAILURE": 0, "UNRESOLVED": 0, "AMBIGUOUS": 0},
    }
    rows = 0
    incomplete = 0

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in label_rows(bars):
            rows += 1
            counts["buy"][row["buy_label"]] += 1
            counts["sell"][row["sell_label"]] += 1
            if not row["coverage_complete"]:
                incomplete += 1
            writer.writerow(row)

    result = {
        "status": "PASS",
        "input": str(input_path),
        "output": str(output_path),
        "rows": rows,
        "incomplete_coverage_rows": incomplete,
        "counts": counts,
        "parameters": {
            "target_distance": DEFAULT_TARGET,
            "adverse_distance": DEFAULT_ADVERSE,
            "horizon_minutes": DEFAULT_HORIZON_MINUTES,
            "decision_price": "decision_bar_close",
            "scan_starts": "next_m1_bar",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: label_exp001.py <validated-m1.csv> <labels.csv>", file=sys.stderr)
        return 2
    write_labels(Path(argv[1]), Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
