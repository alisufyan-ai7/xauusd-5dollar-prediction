#!/usr/bin/env python3
from __future__ import annotations

import csv
import lzma
import math
import struct
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

RECORD = struct.Struct(">5if")
COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")
DECIMAL_FACTORS = {
    "XAUUSD": 1000,
    "EURUSD": 100000,
    "USDJPY": 1000,
    "GBPUSD": 100000,
    "USDCAD": 100000,
    "USDSEK": 100000,
    "USDCHF": 100000,
}

@dataclass(frozen=True)
class M1Row:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def as_tuple(self):
        return (self.timestamp, self.open, self.high, self.low, self.close, self.volume)


def _day_start_ms(day: date) -> int:
    return int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp() * 1000)


def decode_payload(payload: bytes, instrument: str, day: date) -> list[M1Row]:
    instrument = instrument.upper()
    if instrument not in DECIMAL_FACTORS:
        raise ValueError(f"unsupported instrument: {instrument}")
    if not payload:
        raise ValueError("empty payload")
    try:
        raw = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    except lzma.LZMAError as exc:
        raise ValueError("invalid LZMA-alone payload") from exc
    if not raw or len(raw) % RECORD.size:
        raise ValueError(f"decompressed length {len(raw)} is not a positive multiple of {RECORD.size}")

    factor = DECIMAL_FACTORS[instrument]
    base = _day_start_ms(day)
    rows: list[M1Row] = []
    prior_sec = -1
    for offset in range(0, len(raw), RECORD.size):
        sec, open_i, close_i, low_i, high_i, volume = RECORD.unpack_from(raw, offset)
        if sec < 0 or sec >= 86400 or sec % 60:
            raise ValueError(f"invalid M1 second offset: {sec}")
        if sec <= prior_sec:
            raise ValueError("timestamps are not strictly increasing")
        prior_sec = sec
        if min(open_i, close_i, low_i, high_i) <= 0:
            raise ValueError("nonpositive encoded price")
        if low_i > min(open_i, close_i) or high_i < max(open_i, close_i) or high_i < low_i:
            raise ValueError("OHLC invariant violation")
        if not math.isfinite(volume) or volume < 0:
            raise ValueError("invalid volume")
        row = M1Row(
            timestamp=base + sec * 1000,
            open=open_i / factor,
            high=high_i / factor,
            low=low_i / factor,
            close=close_i / factor,
            volume=float(volume),
        )
        if not all(math.isfinite(x) for x in row.as_tuple()[1:]):
            raise ValueError("nonfinite normalized value")
        rows.append(row)
    return rows


def write_csv(rows: Iterable[M1Row], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow(row.as_tuple())


def decode_file(input_path: str | Path, output_path: str | Path, instrument: str, day: date) -> int:
    rows = decode_payload(Path(input_path).read_bytes(), instrument, day)
    write_csv(rows, output_path)
    return len(rows)
