"""Offline-only science/governance guardrails for D-120.

No provider API, no network, no model fitting. Calendar evidence must be
individually dated. Historical unknowns are missing, not retroactively known.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import re

UTC = timezone.utc
FENCE_START = datetime(2026,6,1,tzinfo=UTC)
TEACHER_START = datetime(2026,7,6,tzinfo=UTC)
FENCE_END = datetime(2026,10,9,tzinfo=UTC)
PROTECTED_END = datetime(2027,1,1,tzinfo=UTC)
SYMBOLS = frozenset({"XAUUSD_BID","XAUUSD_ASK", "EURUSD_BID", "USDJPY_BID", "GBPUSD_BID", "USDCAD_BID", "USDSEK_BID", "USDCHF_BID"})
FAMILIES = frozenset({"CPI","NFP","JOLTS","FOMC","GDP","CLAIMS"})


def utc(s: str) -> datetime:
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() != timedelta(0):
        raise ValueError("not absolute UTC")
    return dt


def market_request(symbol: str, start: str, end: str, *, owner_final_approval: bool = False) -> None:
    """Fail closed even on in-scope requests until *later* explicit approval."""
    a, b = utc(start), utc(end)
    if symbol not in SYMBOLS or not (FENCE_START <= a < b <= FENCE_END):
        raise ValueError("symbol/date outside proposal")
    if not owner_final_approval:
        raise PermissionError("D-088 closed: final execution approval absent")


def causal_calendar_entry(entry: dict, minute_start: str) -> dict | None:
    """Evidence-based schedule; absence of archived publication => missing.

    Do not use a post-release news article as evidence of a previously
    scheduled future event. No actual/forecast/previous fields accepted.
    """
    now = utc(minute_start)
    if entry.get("family") not in FAMILIES:
        raise ValueError("non-frozen family")
    if any(k in entry for k in ("actual", "forecast", "previous", "surprise", "revision", "outcome")):
        raise ValueError("post-release fields prohibited")
    if not entry.get("source_url"):
        return None
    published = entry.get("published_at_utc")
    if published is None:
        return None
    publication = utc(published)
    release = utc(entry["release_at_utc"])
    if publication > now:
        return None
    if not entry.get("pre_release_schedule_evidence"):
        return None
    updated = entry.get("superseded_at_utc")
    if updated is not None and now >= utc(updated):
        return None
    return {"family": entry["family"], "release_at_utc": release.isoformat(), "source_url": entry["source_url"]}


def convert_et(year: int, month: int, day: int, hour: int, minute: int) -> str:
    dt = datetime(year,month,day,hour,minute,tzinfo=ZoneInfo("America/New_York"))
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def accepted_cold_start(minute_start: str, source_start: str = "2026-06-01T00:00:00Z") -> bool:
    """Explicitly declares a bounded *different initialization* to Stage 2.

    Does not assert the original six-year continuous-state representation.
    Every old swing/FVG is unknown on the first source minute. Only
    independently observed in-window state may be carried forward.
    """
    start = utc(source_start)
    moment = utc(minute_start)
    if start != FENCE_START or moment < TEACHER_START or moment >= FENCE_END:
        raise ValueError("source cold-start boundary changed")
    return True


def fail_on_new_source_window(requested_start: str, requested_end: str) -> None:
    if utc(requested_start) != FENCE_START or utc(requested_end) != FENCE_END:
        raise ValueError("new source bounds require new preregistration")


def allowlisted_columns(features: list[dict]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Selected 92 GOLD + 63 FULL-only; reject timestamps/outcomes/metadata."""
    names = [f["name"] for f in features]
    if len(names) != len(set(names)):
        raise ValueError("duplicate feature")
    if any(not re.match(r"^(xauusd_m1_market_state|xauusd_structural_state|xauusd_(?:m3|m5|m15|m30|h1|h4|d1|w1)|synthetic_dxy_m1|macro_event_state|decision_index)\.[a-z0-9_]+$", n) for n in names):
        raise ValueError("unexpected source/column name")
    if any(any(word in n.lower() for word in ("future", "return_outcome", "trade_risk", "teacher", "profit", "pnl", "event_id", "stream", "timestamp_ms", "decision_time_ms", "pivot_bar_start", "confirmation_time", "creation_time_ms")) for n in names):
        raise ValueError("leakage predictor")
    gold = tuple(f["name"] for f in features if f["arm"]=="GOLD")
    only_full = tuple(f["name"] for f in features if f["arm"]=="FULL_ONLY")
    if len(gold)!=92 or len(only_full)!=63:
        raise ValueError("unexpected frozen source-derived feature counts")
    return gold, gold+only_full
