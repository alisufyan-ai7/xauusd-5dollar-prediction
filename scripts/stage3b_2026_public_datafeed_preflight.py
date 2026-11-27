#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

START = date(2026, 6, 1)
END_EXCLUSIVE = date(2026, 10, 9)
URL_ROOT = "https://datafeed.dukascopy.com/datafeed"
ALLOWED = {
    "XAUUSD": frozenset({"BID", "ASK"}),
    "EURUSD": frozenset({"BID"}),
    "USDJPY": frozenset({"BID"}),
    "GBPUSD": frozenset({"BID"}),
    "USDCAD": frozenset({"BID"}),
    "USDSEK": frozenset({"BID"}),
    "USDCHF": frozenset({"BID"}),
}
MAX_GETS = 1050
MAX_RAW_BYTES = 350 * 1024 * 1024
MAX_NORMALIZED_BYTES = 750 * 1024 * 1024
MAX_ATTEMPTS = 1
MAX_RETRIES_AFTER_PROVIDER_FAILURE = 0
D140_PROVIDER_ENABLED = False

@dataclass(frozen=True)
class RequestSpec:
    instrument: str
    side: str
    day: date


def validate_request(spec: RequestSpec) -> None:
    instrument = spec.instrument.upper()
    side = spec.side.upper()
    if instrument not in ALLOWED:
        raise PermissionError(f"instrument not allowed: {instrument}")
    if side not in ALLOWED[instrument]:
        raise PermissionError(f"side not allowed for {instrument}: {side}")
    if not (START <= spec.day < END_EXCLUSIVE):
        raise PermissionError(f"date outside D-124 fence: {spec.day.isoformat()}")


def build_url(spec: RequestSpec) -> str:
    validate_request(spec)
    instrument = spec.instrument.upper()
    side = spec.side.upper()
    mm0 = spec.day.month - 1
    return f"{URL_ROOT}/{instrument}/{spec.day.year:04d}/{mm0:02d}/{spec.day.day:02d}/{side}_candles_min_1.bi5"


def sanity_specs() -> tuple[RequestSpec, ...]:
    d = START
    return (
        RequestSpec("XAUUSD", "BID", d),
        RequestSpec("XAUUSD", "ASK", d),
        RequestSpec("EURUSD", "BID", d),
        RequestSpec("USDJPY", "BID", d),
        RequestSpec("GBPUSD", "BID", d),
        RequestSpec("USDCAD", "BID", d),
        RequestSpec("USDSEK", "BID", d),
        RequestSpec("USDCHF", "BID", d),
    )


def full_request_count() -> int:
    days = (END_EXCLUSIVE - START).days
    return days * sum(len(sides) for sides in ALLOWED.values())


def require_provider_execution_authorized() -> None:
    if not D140_PROVIDER_ENABLED:
        raise PermissionError("D-140 provider access remains disabled pending explicit owner authorization")


def static_plan() -> dict:
    return {
        "status": "D140_PREFLIGHT_ONLY_PROVIDER_DISABLED",
        "source_representation": "DUKASCOPY_PUBLIC_DATAFEED_DIRECT_M1_V1",
        "window": [START.isoformat(), END_EXCLUSIVE.isoformat()],
        "logical_series": sum(len(v) for v in ALLOWED.values()),
        "calendar_days": (END_EXCLUSIVE - START).days,
        "sanity_gets": len(sanity_specs()),
        "full_get_opportunities": full_request_count(),
        "hard_get_cap": MAX_GETS,
        "raw_bytes_cap": MAX_RAW_BYTES,
        "normalized_bytes_cap": MAX_NORMALIZED_BYTES,
        "max_attempts": MAX_ATTEMPTS,
        "retries_after_provider_failure": MAX_RETRIES_AFTER_PROVIDER_FAILURE,
        "provider_enabled": D140_PROVIDER_ENABLED,
    }
