#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode, urlsplit

SOURCE_REPRESENTATION = "DUKASCOPY_FREESERV_CHART_JSON3_M1_V1"
BASE_URL = "https://freeserv.dukascopy.com/2.0/index.php"
REFERER = (
    "https://freeserv.dukascopy.com/2.0/?path=chart/index&showUI=true&showTabs=true"
    "&showParameterToolbar=true&showOfferSide=true&allowInstrumentChange=true"
    "&allowPeriodChange=true&allowOfferSideChange=true&presentationType=candle"
    "&timezone=0&live=true"
)
START_ISO = "2026-06-01T00:00:00Z"
END_EXCLUSIVE_ISO = "2026-10-09T00:00:00Z"
START_MS = int(datetime(2026, 6, 1, tzinfo=timezone.utc).timestamp() * 1000)
END_EXCLUSIVE_MS = int(datetime(2026, 10, 9, tzinfo=timezone.utc).timestamp() * 1000)
INTERVAL = "1MIN"
TIME_DIRECTION = "N"
MAX_PAGE_LIMIT = 30_000
SANITY_LIMIT = 2
PROPOSED_MAX_TOTAL_REQUESTS = 96
PROPOSED_MAX_FULL_REQUESTS_PER_SERIES = 11
MAX_RAW_BYTES = 350 * 1024 * 1024
MAX_NORMALIZED_BYTES = 750 * 1024 * 1024
MAX_RETRIES_AFTER_PROVIDER_FAILURE = 0
PROVIDER_EXECUTION_ENABLED = False

SERIES = (
    ("XAU/USD", "B", "XAUUSD_BID"),
    ("XAU/USD", "A", "XAUUSD_ASK"),
    ("EUR/USD", "B", "EURUSD_BID"),
    ("USD/JPY", "B", "USDJPY_BID"),
    ("GBP/USD", "B", "GBPUSD_BID"),
    ("USD/CAD", "B", "USDCAD_BID"),
    ("USD/SEK", "B", "USDSEK_BID"),
    ("USD/CHF", "B", "USDCHF_BID"),
)
ALLOWED = frozenset((i, s) for i, s, _ in SERIES)

@dataclass(frozen=True)
class RequestSpec:
    instrument: str
    side: str
    cursor_ms: int
    limit: int

@dataclass(frozen=True)
class CandleRow:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def as_tuple(self):
        return (self.timestamp, self.open, self.high, self.low, self.close, self.volume)


def require_provider_execution_authorized() -> None:
    if not PROVIDER_EXECUTION_ENABLED:
        raise PermissionError("D-148 provider access is not authorized")


def _callback_for(spec: RequestSpec) -> str:
    material = f"{spec.instrument}|{spec.side}|{spec.cursor_ms}|{spec.limit}".encode("utf-8")
    return "_callbacks____" + hashlib.sha256(material).hexdigest()[:9]


def validate_request(spec: RequestSpec) -> None:
    if (spec.instrument, spec.side) not in ALLOWED:
        raise PermissionError(f"unapproved instrument/side: {spec.instrument}/{spec.side}")
    if not (START_MS <= spec.cursor_ms < END_EXCLUSIVE_MS):
        raise PermissionError(f"cursor outside D-124 fence: {spec.cursor_ms}")
    if not (1 <= spec.limit <= MAX_PAGE_LIMIT):
        raise PermissionError(f"limit outside frozen range: {spec.limit}")


def request_params(spec: RequestSpec) -> dict[str, str]:
    validate_request(spec)
    return {
        "path": "chart/json3",
        "splits": "true",
        "stocks": "true",
        "time_direction": TIME_DIRECTION,
        "jsonp": _callback_for(spec),
        "last_update": str(spec.cursor_ms),
        "offer_side": spec.side,
        "instrument": spec.instrument,
        "interval": INTERVAL,
        "limit": str(spec.limit),
    }


def build_url(spec: RequestSpec) -> str:
    params = request_params(spec)
    url = BASE_URL + "?" + urlencode(params)
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc != "freeserv.dukascopy.com" or parts.path != "/2.0/index.php":
        raise PermissionError("unexpected FREESERV URL identity")
    return url


def request_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (D148 deterministic preflight; no-provider until authorized)",
        "Host": "freeserv.dukascopy.com",
        "Referer": REFERER,
        "Accept": "*/*",
    }


def parse_jsonp(payload: bytes | str, callback: str) -> list:
    text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    prefix = callback + "("
    suffix = ");"
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise ValueError("JSONP callback wrapper mismatch")
    inner = text[len(prefix):-len(suffix)]
    try:
        obj = json.loads(inner)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSONP JSON payload") from exc
    if not isinstance(obj, list):
        raise ValueError("JSONP payload must be a list")
    return obj


def decode_candle_rows(raw_rows: list) -> list[CandleRow]:
    out: list[CandleRow] = []
    prior = None
    for raw in raw_rows:
        if not isinstance(raw, list) or len(raw) not in (6, 7):
            raise ValueError("unexpected chart row shape")
        if len(raw) == 7 and raw[6] is not None:
            raise ValueError("unexpected non-null trailing chart field")
        ts, o, h, l, c, v = raw[:6]
        if isinstance(ts, bool) or not isinstance(ts, int):
            raise ValueError("timestamp must be integer epoch milliseconds")
        vals = (o, h, l, c, v)
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in vals):
            raise ValueError("OHLCV values must be numeric")
        o, h, l, c, v = map(float, vals)
        if not all(math.isfinite(x) for x in (o, h, l, c, v)):
            raise ValueError("non-finite OHLCV")
        if min(o, h, l, c) <= 0:
            raise ValueError("nonpositive price")
        if l > min(o, c) or h < max(o, c) or h < l:
            raise ValueError("OHLC invariant violation")
        if v < 0:
            raise ValueError("negative volume")
        if prior is not None and ts <= prior:
            raise ValueError("timestamps are not strictly increasing")
        prior = ts
        out.append(CandleRow(ts, o, h, l, c, v))
    return out


def normalize_page(rows: list[CandleRow], cursor_ms: int, *, first_page: bool) -> tuple[list[CandleRow], int]:
    if not rows:
        return [], cursor_ms
    if rows[0].timestamp < cursor_ms:
        raise ValueError("page begins before requested cursor")
    work = list(rows)
    if not first_page and work and work[0].timestamp == cursor_ms:
        work = work[1:]
    if not work:
        raise ValueError("cursor did not advance")
    if work[0].timestamp <= cursor_ms and not first_page:
        raise ValueError("cursor did not advance")
    new_cursor = work[-1].timestamp
    if new_cursor <= cursor_ms:
        raise ValueError("cursor did not advance")
    return work, new_cursor


def rows_inside_fence(rows: list[CandleRow]) -> list[CandleRow]:
    accepted = []
    for row in rows:
        if row.timestamp < START_MS:
            raise PermissionError("provider row before authorized start")
        if row.timestamp >= END_EXCLUSIVE_MS:
            continue
        accepted.append(row)
    return accepted


def sanity_specs() -> tuple[RequestSpec, ...]:
    return tuple(RequestSpec(i, s, START_MS, SANITY_LIMIT) for i, s, _ in SERIES)


def static_plan() -> dict:
    calendar_days = (END_EXCLUSIVE_MS - START_MS) // 86_400_000
    theoretical_slots_per_series = calendar_days * 1440
    theoretical_full_pages_per_series = (theoretical_slots_per_series + MAX_PAGE_LIMIT - 1) // MAX_PAGE_LIMIT
    return {
        "status": "D148_PREFLIGHT_ONLY_PROVIDER_DISABLED",
        "source_representation": SOURCE_REPRESENTATION,
        "endpoint": BASE_URL,
        "interval": INTERVAL,
        "window": [START_ISO, END_EXCLUSIVE_ISO],
        "logical_series": len(SERIES),
        "sanity_requests": len(sanity_specs()),
        "sanity_limit": SANITY_LIMIT,
        "full_page_limit": MAX_PAGE_LIMIT,
        "calendar_days": calendar_days,
        "theoretical_calendar_slots_per_series": theoretical_slots_per_series,
        "theoretical_full_pages_per_series_if_pages_fill": theoretical_full_pages_per_series,
        "proposed_max_full_requests_per_series": PROPOSED_MAX_FULL_REQUESTS_PER_SERIES,
        "proposed_max_total_requests": PROPOSED_MAX_TOTAL_REQUESTS,
        "raw_bytes_cap": MAX_RAW_BYTES,
        "normalized_bytes_cap": MAX_NORMALIZED_BYTES,
        "retries_after_provider_failure": MAX_RETRIES_AFTER_PROVIDER_FAILURE,
        "provider_enabled": PROVIDER_EXECUTION_ENABLED,
    }
