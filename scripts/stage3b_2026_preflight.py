#!/usr/bin/env python3
"""No-provider Stage 3B 2026 protocol guards. Standard-library-only.

All inputs to these functions must be fixtures or already-frozen source-only
metadata. This module intentionally provides no network/acquisition code.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

UTC = timezone.utc
FENCE_START = datetime(2026, 6, 1, tzinfo=UTC)
TEACHER_START = datetime(2026, 7, 6, tzinfo=UTC)
FENCE_END = datetime(2026, 10, 9, tzinfo=UTC)
QUARANTINE_END = datetime(2026, 12, 1, tzinfo=UTC)
SHADOW_END = datetime(2027, 1, 1, tzinfo=UTC)
RAW_MAX_BYTES = 350 * 1024**2
NORMALIZED_MAX_BYTES = 750 * 1024**2
SYMBOLS = frozenset({"XAUUSD_BID", "XAUUSD_ASK", "EURUSD_BID", "USDJPY_BID", "GBPUSD_BID", "USDCAD_BID", "USDSEK_BID", "USDCHF_BID"})


def parse_utc(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset() != timedelta(0):
        raise ValueError("UTC timestamp required")
    return d


def check_market_request(symbol: str, start: str, end: str) -> None:
    a, b = parse_utc(start), parse_utc(end)
    if symbol not in SYMBOLS:
        raise ValueError("unapproved symbol")
    if not (FENCE_START <= a < b <= FENCE_END):
        raise ValueError("2026 market request outside approved proposal fence")


def check_market_row(symbol: str, timestamp: str) -> None:
    a = parse_utc(timestamp)
    check_market_request(symbol, a.isoformat(), (a + timedelta(microseconds=1)).isoformat())


def check_budget(raw_bytes: int, normalized_bytes: int, attempts: int) -> None:
    if not (0 <= raw_bytes <= RAW_MAX_BYTES and 0 <= normalized_bytes <= NORMALIZED_MAX_BYTES and attempts <= 1 and attempts >= 0):
        raise ValueError("data/acquisition budget exceeded")


def read_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [x["name"] for x in data["features"]]
    if len(names) != len(set(names)):
        raise ValueError("duplicate feature")
    if data["status"] != "PREFLIGHT_DESIGN_NO_PROVIDER" or not data["features"]:
        raise ValueError("unsupported feature contract")
    forbidden = ("trade", "risk", "future", "pnl", "profit", "event_id", "stream", "source_date", "timestamp_ms", "decision_time_ms", "pivot_bar_start", "confirmation_time", "creation_time_ms")
    for f in data["features"]:
        if f["arm"] not in ("GOLD", "FULL_ONLY"):
            raise ValueError("unknown feature arm")
        if any(s in f["name"].lower() for s in forbidden):
            raise ValueError("forbidden predictor")
        if f["source_table"] not in ("xauusd_m1_market_state", "xauusd_structural_state", "xauusd_timeframes", "decision_index", "synthetic_dxy_m1", "macro_event_state"):
            raise ValueError("unknown source")
    return data


def feature_columns(contract: dict, arm: str) -> tuple[str, ...]:
    if arm not in ("GOLD", "FULL"):
        raise ValueError("unknown arm")
    return tuple(f["name"] for f in contract["features"] if f["arm"] == "GOLD" or arm == "FULL")


def expand_event(event: dict) -> list[tuple[datetime, float]]:
    if event.get("primary_task_a_eligible") != "true":
        return []
    a, b = parse_utc(event["interval_start_utc"]), parse_utc(event["interval_end_utc"])
    if a.second or b.second or a.microsecond or b.microsecond:
        raise ValueError("minute grid only")
    k = int((b - a).total_seconds() / 60) + 1
    if k < 1 or k > 5 or k != int(event["interval_width_minutes"]):
        raise ValueError("interval outside source-only cap")
    return [(a + timedelta(minutes=i), 1 / k) for i in range(k)]


def align_causal(minute: datetime, state_times: list[datetime]) -> datetime | None:
    candidates = [t for t in state_times if t <= minute]
    return max(candidates) if candidates else None


def pool_event(probabilities: list[float]) -> float:
    if not probabilities or any(not 0 <= p <= 1 for p in probabilities):
        raise ValueError("invalid prediction probabilities")
    return sum(probabilities) / len(probabilities)


def lodo(events: list[dict]) -> list[tuple[str, list[str], list[str]]]:
    seen = {x["event_id"] for x in events}
    if len(seen) != len(events):
        raise ValueError("duplicate event ID")
    dates = sorted({e["source_date"] for e in events})
    folds = []
    for date in dates:
        test = [e["event_id"] for e in events if e["source_date"] == date]
        train = [e["event_id"] for e in events if e["source_date"] != date]
        if set(test) & set(train) or len(test) + len(train) != len(events):
            raise AssertionError("date-fold leakage")
        folds.append((date, train, test))
    return folds


def class_normalized_mass(events: list[dict], positive_label: str = "ACT") -> dict[str, float]:
    groups = defaultdict(list)
    for e in events:
        if e.get("primary_task_a_eligible") != "true":
            continue
        group = "ACT" if e["event_type"].startswith("COMMIT_") else "P3"
        groups[group].append(e["event_id"])
    if not groups["ACT"] or not groups["P3"]:
        raise ValueError("both classes required")
    return {event_id: .5 / len(items) for items in groups.values() for event_id in items}


def validate_source_manifest(events: list[dict], expected_sha: str | None = None, csv_bytes: bytes | None = None) -> dict:
    if expected_sha and hashlib.sha256(csv_bytes or b"").hexdigest() != expected_sha:
        raise ValueError("frozen teacher SHA-256 mismatch")
    if len({e["event_id"] for e in events}) != len(events):
        raise ValueError("duplicate event")
    eligible = [e for e in events if e["primary_task_a_eligible"] == "true"]
    for e in eligible:
        if not (TEACHER_START <= parse_utc(e["interval_start_utc"]) < FENCE_END):
            raise ValueError("teacher date outside bounded window")
        if len(expand_event(e)) != int(e["interval_width_minutes"]):
            raise ValueError("invalid interval")
    act = [e for e in eligible if e["event_type"].startswith("COMMIT_")]
    p3 = [e for e in eligible if e["event_type"] in ("HARD_REJECT", "DEFER_WAIT")]
    dates_a, dates_n = {e["source_date"] for e in act}, {e["source_date"] for e in p3}
    if not (len(act) == 107 and len(p3) == 143 and len(dates_a) == 39 and len(dates_a & dates_n) == 39):
        raise ValueError("frozen source counts mismatch")
    return {"eligible_act": len(act), "eligible_p3": len(p3), "source_dates": len(dates_a), "paired_dates": len(dates_a & dates_n)}


def audit_feature_parity(gold_rows: list[str], full_rows: list[str]) -> None:
    if gold_rows != full_rows or len(gold_rows) != len(set(gold_rows)):
        raise ValueError("GOLD/FULL row or order mismatch")


def require_calendar_provenance(item: dict, decision_time: str) -> None:
    d = parse_utc(decision_time)
    announced = parse_utc(item["document_published_utc"])
    if announced > d:
        raise ValueError("calendar date not shown publicly known by decision")
    if item["event_family"] not in {"CLAIMS", "CPI", "NFP", "JOLTS", "GDP", "FOMC"}:
        raise ValueError("unapproved calendar family")
    if not item.get("archive_url") or not item.get("historical_schedule_verified", False):
        raise ValueError("unverified historical calendar")


if __name__ == "__main__":
    raise SystemExit("Import only: no acquisition or model execution supported")
