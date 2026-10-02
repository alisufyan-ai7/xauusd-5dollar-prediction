#!/usr/bin/env python3
"""Build one annual Information Parity V1 Stage 2 information layer.

Inputs are already-acquired/synchronized TRAIN-only market data plus a
normalized macro schedule. This script creates causal information tables only.
It never reads or creates future-return, trade-outcome, or P&L labels.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ONE_MIN = 60_000
UTC = timezone.utc
LON = ZoneInfo("Europe/London")
NY = ZoneInfo("America/New_York")
TF_RULES = {
    "m3": ("3min", 3),
    "m5": ("5min", 5),
    "m15": ("15min", 15),
    "m30": ("30min", 30),
    "h1": ("1h", 60),
    "h4": ("4h", 240),
}
STRUCT_TFS = ("m5", "m15", "h1", "h4")


def fail(msg: str):
    raise SystemExit(f"STAGE2_BUILD_FAILED:{msg}")


def load_m1(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = [
        "timestamp_ms", "decision_time_ms",
        "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume",
        "ask_open", "ask_high", "ask_low", "ask_close", "ask_volume",
        "spread_open", "spread_close", "bid_flat_fill", "ask_flat_fill",
    ]
    if list(df.columns) != required:
        fail(f"xauusd schema {list(df.columns)}")
    if df.empty:
        fail("empty xauusd m1")
    for c in ("timestamp_ms", "decision_time_ms"):
        df[c] = df[c].astype("int64")
    if not np.all(df["decision_time_ms"].to_numpy() == df["timestamp_ms"].to_numpy() + ONE_MIN):
        fail("decision time mismatch")
    if np.any(np.diff(df["timestamp_ms"].to_numpy()) <= 0):
        fail("non-increasing xauusd timestamps")
    for c in [
        "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume",
        "ask_open", "ask_high", "ask_low", "ask_close", "ask_volume",
        "spread_open", "spread_close",
    ]:
        df[c] = df[c].astype("float64")
    if (df["spread_open"] < 0).any() or (df["spread_close"] < 0).any():
        fail("negative spread")
    df["bid_flat_fill"] = df["bid_flat_fill"].astype("int8")
    df["ask_flat_fill"] = df["ask_flat_fill"].astype("int8")
    return df


def contiguous_segment_ids(ts: np.ndarray) -> np.ndarray:
    breaks = np.ones(len(ts), dtype=np.int64)
    if len(ts) > 1:
        breaks[1:] = (np.diff(ts) != ONE_MIN).astype(np.int64)
    return np.cumsum(breaks)


def add_m1_transforms(df: pd.DataFrame) -> pd.DataFrame:
    z = df.copy()
    z["volume_sum_proxy"] = z["bid_volume"] + z["ask_volume"]
    seg = pd.Series(contiguous_segment_ids(z["timestamp_ms"].to_numpy()), index=z.index)
    pos = z.groupby(seg, sort=False).cumcount()
    z["core_240m_contiguous_ready"] = (pos >= 239).astype("int8")

    for n in (5, 15, 60, 240):
        z[f"volume_mean_{n}m"] = (
            z["volume_sum_proxy"].groupby(seg, sort=False)
            .transform(lambda s, n=n: s.rolling(n, min_periods=n).mean())
        )
    z["volume_ratio_1m_to_60m"] = (
        z["volume_sum_proxy"] / z["volume_mean_60m"].replace(0, np.nan)
    )

    for n in (5, 15, 60):
        z[f"spread_mean_{n}m"] = (
            z["spread_close"].groupby(seg, sort=False)
            .transform(lambda s, n=n: s.rolling(n, min_periods=n).mean())
        )
    for n in (15, 60):
        z[f"spread_max_{n}m"] = (
            z["spread_close"].groupby(seg, sort=False)
            .transform(lambda s, n=n: s.rolling(n, min_periods=n).max())
        )
    z["spread_ratio_1m_to_60m"] = (
        z["spread_close"] / z["spread_mean_60m"].replace(0, np.nan)
    )
    return z


def resample_exact(m1: pd.DataFrame, rule: str, expected: int) -> pd.DataFrame:
    dt = pd.to_datetime(m1["timestamp_ms"], unit="ms", utc=True)
    src = pd.DataFrame({
        "open": m1["bid_open"].to_numpy(float),
        "high": m1["bid_high"].to_numpy(float),
        "low": m1["bid_low"].to_numpy(float),
        "close": m1["bid_close"].to_numpy(float),
        "volume": (m1["bid_volume"] + m1["ask_volume"]).to_numpy(float),
    }, index=dt)

    r = src.resample(rule, origin="epoch", closed="left", label="right")
    agg = r.agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"
    })
    cnt = r["close"].count()
    out = agg.loc[cnt == expected].copy()
    out["source_count"] = cnt.loc[cnt == expected].astype("int32")
    out["available_time_ms"] = (out.index.view("int64") // 1_000_000).astype("int64")

    delta = pd.to_timedelta(rule)
    out["bar_start_ms"] = (
        (out.index - delta).view("int64") // 1_000_000
    ).astype("int64")
    return out[[
        "bar_start_ms", "available_time_ms",
        "open", "high", "low", "close", "volume", "source_count"
    ]]


def build_d1(h1: pd.DataFrame) -> pd.DataFrame:
    if h1.empty:
        return pd.DataFrame(columns=[
            "bar_start_ms", "available_time_ms", "open", "high", "low", "close",
            "volume", "source_count"
        ])
    idx = pd.to_datetime(h1["available_time_ms"], unit="ms", utc=True)
    tmp = h1.copy()
    tmp.index = idx
    tmp["source_day"] = (idx - pd.Timedelta(nanoseconds=1)).dt.floor("D")
    rows = []
    for day, g in tmp.groupby("source_day", sort=True):
        if len(g) < 20:
            continue
        available = day + pd.Timedelta(days=1)
        rows.append({
            "bar_start_ms": int(day.value // 1_000_000),
            "available_time_ms": int(available.value // 1_000_000),
            "open": float(g.iloc[0]["open"]),
            "high": float(g["high"].max()),
            "low": float(g["low"].min()),
            "close": float(g.iloc[-1]["close"]),
            "volume": float(g["volume"].sum()),
            "source_count": int(len(g)),
        })
    return pd.DataFrame(rows)


def build_w1(d1: pd.DataFrame) -> pd.DataFrame:
    if d1.empty:
        return pd.DataFrame(columns=[
            "bar_start_ms", "available_time_ms", "open", "high", "low", "close",
            "volume", "source_count"
        ])
    z = d1.copy()
    day = pd.to_datetime(z["bar_start_ms"], unit="ms", utc=True)
    z["week_start"] = day - pd.to_timedelta(day.dt.weekday, unit="D")
    rows = []
    for week_start, g in z.groupby("week_start", sort=True):
        if len(g) < 4:
            continue
        available = week_start + pd.Timedelta(days=7)
        rows.append({
            "bar_start_ms": int(week_start.value // 1_000_000),
            "available_time_ms": int(available.value // 1_000_000),
            "open": float(g.iloc[0]["open"]),
            "high": float(g["high"].max()),
            "low": float(g["low"].min()),
            "close": float(g.iloc[-1]["close"]),
            "volume": float(g["volume"].sum()),
            "source_count": int(len(g)),
        })
    return pd.DataFrame(rows)


def swing_events(bars: pd.DataFrame):
    if len(bars) < 5:
        return [], []
    hi = bars["high"].to_numpy(float)
    lo = bars["low"].to_numpy(float)
    av = bars["available_time_ms"].to_numpy(np.int64)
    start = bars["bar_start_ms"].to_numpy(np.int64)
    highs = []
    lows = []
    for j in range(4, len(bars)):
        i = j - 2
        if hi[i] > hi[i - 1] and hi[i] > hi[i - 2] and hi[i] >= hi[i + 1] and hi[i] >= hi[i + 2]:
            highs.append((int(av[j]), float(hi[i]), int(start[i]), int(av[j])))
        if lo[i] < lo[i - 1] and lo[i] < lo[i - 2] and lo[i] <= lo[i + 1] and lo[i] <= lo[i + 2]:
            lows.append((int(av[j]), float(lo[i]), int(start[i]), int(av[j])))
    return highs, lows


def asof_event(decision_times: np.ndarray, events, cols):
    out = {c: np.full(len(decision_times), np.nan) for c in cols}
    if not events:
        return out
    et = np.array([e[0] for e in events], dtype=np.int64)
    pos = np.searchsorted(et, decision_times, side="right") - 1
    valid = pos >= 0
    for ci, c in enumerate(cols, start=1):
        vals = np.array([e[ci] for e in events], dtype=float)
        arr = np.full(len(decision_times), np.nan)
        arr[valid] = vals[pos[valid]]
        out[c] = arr
    return out


def build_fvg_records(bars: pd.DataFrame):
    records = {"bull": [], "bear": []}
    active = {"bull": [], "bear": []}
    if len(bars) < 3:
        return records

    hi = bars["high"].to_numpy(float)
    lo = bars["low"].to_numpy(float)
    cl = bars["close"].to_numpy(float)
    av = bars["available_time_ms"].to_numpy(np.int64)

    next_id = 0
    for k in range(len(bars)):
        now = int(av[k])

        for side in ("bull", "bear"):
            kept = []
            for ridx in active[side]:
                rec = records[side][ridx]
                invalid = (
                    cl[k] < rec["lower"] if side == "bull"
                    else cl[k] > rec["upper"]
                )
                if invalid and now > rec["created_ms"]:
                    rec["invalid_ms"] = now
                else:
                    kept.append(ridx)
            active[side] = kept

        if k >= 2 and hi[k - 2] < lo[k]:
            rec = {
                "id": next_id, "created_ms": now, "invalid_ms": None,
                "lower": float(hi[k - 2]), "upper": float(lo[k]),
            }
            next_id += 1
            records["bull"].append(rec)
            active["bull"].append(len(records["bull"]) - 1)

        if k >= 2 and lo[k - 2] > hi[k]:
            rec = {
                "id": next_id, "created_ms": now, "invalid_ms": None,
                "lower": float(hi[k]), "upper": float(lo[k - 2]),
            }
            next_id += 1
            records["bear"].append(rec)
            active["bear"].append(len(records["bear"]) - 1)

    return records


def fvg_state_for_decisions(
    decision_times: np.ndarray,
    prices: np.ndarray,
    records: list[dict],
):
    n = len(decision_times)
    lower = np.full(n, np.nan)
    upper = np.full(n, np.nan)
    signed = np.full(n, np.nan)
    created = np.full(n, np.nan)
    age = np.full(n, np.nan)
    if not records or n == 0:
        return lower, upper, signed, created, age

    events = defaultdict(lambda: {"add": [], "remove": []})
    rec_by_id = {}
    for rec in records:
        rec_by_id[rec["id"]] = rec
        events[int(rec["created_ms"])]["add"].append(rec["id"])
        if rec["invalid_ms"] is not None:
            events[int(rec["invalid_ms"])]["remove"].append(rec["id"])

    event_times = sorted(events)
    active: dict[int, dict] = {}
    cursor = 0

    def fill_segment(a: int, b: int):
        if b <= a or not active:
            return
        px = prices[a:b]
        best_abs = np.full(b - a, np.inf)
        best_signed = np.full(b - a, np.nan)
        best_lower = np.full(b - a, np.nan)
        best_upper = np.full(b - a, np.nan)
        best_created = np.full(b - a, np.nan)

        ordered = sorted(active.values(), key=lambda r: r["created_ms"])
        for rec in ordered:
            s = np.where(
                px < rec["lower"],
                rec["lower"] - px,
                np.where(px > rec["upper"], rec["upper"] - px, 0.0),
            )
            aa = np.abs(s)
            take = aa <= best_abs
            best_abs[take] = aa[take]
            best_signed[take] = s[take]
            best_lower[take] = rec["lower"]
            best_upper[take] = rec["upper"]
            best_created[take] = rec["created_ms"]

        lower[a:b] = best_lower
        upper[a:b] = best_upper
        signed[a:b] = best_signed
        created[a:b] = best_created
        age[a:b] = np.where(
            np.isfinite(best_created),
            (decision_times[a:b] - best_created) / ONE_MIN,
            np.nan,
        )

    for et in event_times:
        before = np.searchsorted(decision_times, et, side="left")
        fill_segment(cursor, before)
        cursor = before

        ev = events[et]
        for rid in ev["remove"]:
            active.pop(rid, None)
        for rid in ev["add"]:
            active[rid] = rec_by_id[rid]

    fill_segment(cursor, n)
    return lower, upper, signed, created, age


def add_structural_state(
    m1: pd.DataFrame,
    tf_tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    dtimes = m1["decision_time_ms"].to_numpy(np.int64)
    prices = m1["bid_close"].to_numpy(float)
    out = pd.DataFrame({"decision_time_ms": dtimes})

    for tf in STRUCT_TFS:
        bars = tf_tables[tf]
        sh, sl = swing_events(bars)
        hs = asof_event(
            dtimes, sh,
            ["level", "pivot_bar_start_ms", "confirmation_time_ms"]
        )
        ls = asof_event(
            dtimes, sl,
            ["level", "pivot_bar_start_ms", "confirmation_time_ms"]
        )
        for key, arr in hs.items():
            out[f"last_confirmed_swing_high_{tf}_{key}"] = arr
        for key, arr in ls.items():
            out[f"last_confirmed_swing_low_{tf}_{key}"] = arr

        fvgs = build_fvg_records(bars)
        for side in ("bull", "bear"):
            lower, upper, signed, created, age = fvg_state_for_decisions(
                dtimes, prices, fvgs[side]
            )
            base = f"nearest_active_{side}_fvg_{tf}"
            out[f"{base}_lower"] = lower
            out[f"{base}_upper"] = upper
            out[f"{base}_signed_distance"] = signed
            out[f"{base}_creation_time_ms"] = created
            out[f"{base}_age_minutes"] = age

    return out


def session_state(m1: pd.DataFrame) -> pd.DataFrame:
    ts = m1["timestamp_ms"].to_numpy(np.int64)
    dec = m1["decision_time_ms"].to_numpy(np.int64)
    hi = m1["bid_high"].to_numpy(float)
    lo = m1["bid_low"].to_numpy(float)

    labels = np.empty(len(m1), dtype=object)
    mins = np.full(len(m1), np.nan)
    asia_hi = np.full(len(m1), np.nan)
    asia_lo = np.full(len(m1), np.nan)
    lon_hi = np.full(len(m1), np.nan)
    lon_lo = np.full(len(m1), np.nan)

    utc_dates = pd.to_datetime(dec, unit="ms", utc=True).date
    start = 0
    while start < len(m1):
        d = utc_dates[start]
        end = start + 1
        while end < len(m1) and utc_dates[end] == d:
            end += 1

        utc0 = datetime.combine(d, time(0, 0), tzinfo=UTC)
        london_open = datetime.combine(d, time(8, 0), tzinfo=LON).astimezone(UTC)
        ny_open = datetime.combine(d, time(8, 0), tzinfo=NY).astimezone(UTC)

        utc0_ms = int(utc0.timestamp() * 1000)
        lon_ms = int(london_open.timestamp() * 1000)
        ny_ms = int(ny_open.timestamp() * 1000)

        ah = -np.inf
        al = np.inf
        lh = -np.inf
        ll = np.inf

        for i in range(start, end):
            # The just-completed bar may update a session range.
            if ts[i] >= utc0_ms and dec[i] <= lon_ms:
                ah = max(ah, hi[i])
                al = min(al, lo[i])
            elif ts[i] >= lon_ms and dec[i] <= ny_ms:
                lh = max(lh, hi[i])
                ll = min(ll, lo[i])

            if dec[i] < lon_ms:
                labels[i] = "ASIA"
                mins[i] = (dec[i] - utc0_ms) / ONE_MIN
            elif dec[i] < ny_ms:
                labels[i] = "LONDON"
                mins[i] = (dec[i] - lon_ms) / ONE_MIN
            else:
                labels[i] = "NEW_YORK"
                mins[i] = (dec[i] - ny_ms) / ONE_MIN

            if math.isfinite(ah):
                asia_hi[i] = ah
                asia_lo[i] = al
            if math.isfinite(lh):
                lon_hi[i] = lh
                lon_lo[i] = ll

        start = end

    return pd.DataFrame({
        "decision_time_ms": dec,
        "session_label": labels,
        "minutes_since_session_boundary": mins,
        "asia_high_known": asia_hi,
        "asia_low_known": asia_lo,
        "london_high_known": lon_hi,
        "london_low_known": lon_lo,
    })


def add_previous_day(
    structural: pd.DataFrame,
    dtimes: np.ndarray,
    d1: pd.DataFrame,
):
    structural["previous_day_high"] = np.nan
    structural["previous_day_low"] = np.nan
    structural["previous_day_open"] = np.nan
    structural["previous_day_close"] = np.nan
    if d1.empty:
        return
    av = d1["available_time_ms"].to_numpy(np.int64)
    pos = np.searchsorted(av, dtimes, side="right") - 1
    valid = pos >= 0
    for src, dst in [
        ("high", "previous_day_high"),
        ("low", "previous_day_low"),
        ("open", "previous_day_open"),
        ("close", "previous_day_close"),
    ]:
        arr = np.full(len(dtimes), np.nan)
        vals = d1[src].to_numpy(float)
        arr[valid] = vals[pos[valid]]
        structural[dst] = arr


def load_dxy(path: Path):
    d = pd.read_csv(path)
    required = [
        "dxy_bar_start_ms", "dxy_available_time_ms", "dxy_level",
        "dxy_change_1m", "dxy_change_5m", "dxy_change_15m",
        "dxy_change_60m", "dxy_change_240m",
        "dxy_rv_15m", "dxy_rv_60m", "dxy_rv_240m",
    ]
    if list(d.columns) != required:
        fail(f"dxy schema {list(d.columns)}")
    if not d.empty:
        d["dxy_available_time_ms"] = d["dxy_available_time_ms"].astype("int64")
        if np.any(np.diff(d["dxy_available_time_ms"].to_numpy()) <= 0):
            fail("non-increasing dxy availability")
    return d


def dxy_alignment(dtimes: np.ndarray, dxy: pd.DataFrame):
    available = np.zeros(len(dtimes), dtype=np.int8)
    age = np.full(len(dtimes), np.nan)
    if dxy.empty:
        return available, age
    av = dxy["dxy_available_time_ms"].to_numpy(np.int64)
    pos = np.searchsorted(av, dtimes, side="right") - 1
    valid = pos >= 0
    ages = np.full(len(dtimes), np.nan)
    ages[valid] = (dtimes[valid] - av[pos[valid]]) / ONE_MIN
    ok = valid & (ages >= 0) & (ages <= 5)
    available[ok] = 1
    age[ok] = ages[ok]
    return available, age


def load_macro_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["event_family", "scheduled_time_utc"])
    m = pd.read_csv(path)
    required = [
        "event_id", "event_family", "scheduled_time_utc", "scheduled_time_local",
        "source_timezone", "source_agency", "source_document_id_or_url",
        "release_stage", "historical_exception_flag", "normalization_version",
    ]
    if list(m.columns) != required:
        fail(f"macro schema {list(m.columns)}")
    if m.empty:
        return m
    m["scheduled_dt"] = pd.to_datetime(m["scheduled_time_utc"], utc=True)
    m["scheduled_time_ms"] = (m["scheduled_dt"].astype("int64") // 1_000_000).astype("int64")
    return m.sort_values(["scheduled_time_ms", "event_family", "event_id"]).reset_index(drop=True)


def macro_coverage_available(coverage_path: Path, year: int) -> bool:
    if not coverage_path.exists():
        return False
    o = json.loads(coverage_path.read_text(encoding="utf-8"))
    y = o.get("years", {}).get(str(year), {})
    return bool(y.get("stage2_macro_schedule_available", False))


def build_macro_state(
    dtimes: np.ndarray,
    macro: pd.DataFrame,
    schedule_available: bool,
) -> pd.DataFrame:
    out = pd.DataFrame({"decision_time_ms": dtimes})
    n = len(dtimes)
    if macro.empty:
        for c in (
            "previous_event_families", "next_event_families"
        ):
            out[c] = ""
        for c in (
            "minutes_since_previous_event", "minutes_to_next_event"
        ):
            out[c] = np.nan
        for c in (
            "events_prior_120m_count", "events_next_120m_count",
            "event_0_15m_before", "event_15_60m_before",
            "event_0_15m_after", "event_15_60m_after", "event_60_120m_after",
        ):
            out[c] = 0
        out["macro_schedule_available"] = int(schedule_available)
        return out

    grouped = (
        macro.groupby("scheduled_time_ms")["event_family"]
        .apply(lambda s: "|".join(sorted(set(map(str, s)))))
        .sort_index()
    )
    et = grouped.index.to_numpy(np.int64)
    fam = grouped.to_numpy(object)

    prev_pos = np.searchsorted(et, dtimes, side="right") - 1
    next_pos = np.searchsorted(et, dtimes, side="right")

    prev_valid = prev_pos >= 0
    next_valid = next_pos < len(et)

    prev_family = np.full(n, "", dtype=object)
    next_family = np.full(n, "", dtype=object)
    prev_mins = np.full(n, np.nan)
    next_mins = np.full(n, np.nan)

    prev_family[prev_valid] = fam[prev_pos[prev_valid]]
    next_family[next_valid] = fam[next_pos[next_valid]]
    prev_mins[prev_valid] = (dtimes[prev_valid] - et[prev_pos[prev_valid]]) / ONE_MIN
    next_mins[next_valid] = (et[next_pos[next_valid]] - dtimes[next_valid]) / ONE_MIN

    prior_left = np.searchsorted(et, dtimes - 120 * ONE_MIN, side="left")
    prior_right = np.searchsorted(et, dtimes, side="right")
    next_left = np.searchsorted(et, dtimes, side="right")
    next_right = np.searchsorted(et, dtimes + 120 * ONE_MIN, side="right")

    out["previous_event_families"] = prev_family
    out["minutes_since_previous_event"] = prev_mins
    out["next_event_families"] = next_family
    out["minutes_to_next_event"] = next_mins
    out["events_prior_120m_count"] = prior_right - prior_left
    out["events_next_120m_count"] = next_right - next_left
    out["event_0_15m_before"] = ((next_mins > 0) & (next_mins <= 15)).astype("int8")
    out["event_15_60m_before"] = ((next_mins > 15) & (next_mins <= 60)).astype("int8")
    out["event_0_15m_after"] = ((prev_mins >= 0) & (prev_mins <= 15)).astype("int8")
    out["event_15_60m_after"] = ((prev_mins > 15) & (prev_mins <= 60)).astype("int8")
    out["event_60_120m_after"] = ((prev_mins > 60) & (prev_mins <= 120)).astype("int8")
    out["macro_schedule_available"] = int(schedule_available)
    return out


def write_csv_gz(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, compression="gzip")


def json_number(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return None if not math.isfinite(float(x)) else float(x)
    return x


def main(argv: list[str]) -> None:
    if len(argv) != 8:
        raise SystemExit(
            "usage: build_information_parity_stage2_year.py "
            "<year> <xauusd-sync.csv> <dxy.csv> <macro.csv> "
            "<macro-coverage.json> <out-dir> <report.json>"
        )

    year = int(argv[1])
    if year < 2016 or year > 2021:
        fail(f"sealed year requested {year}")

    m1_path = Path(argv[2])
    dxy_path = Path(argv[3])
    macro_path = Path(argv[4])
    macro_coverage_path = Path(argv[5])
    out_dir = Path(argv[6])
    report_path = Path(argv[7])

    m1 = add_m1_transforms(load_m1(m1_path))
    dtimes = m1["decision_time_ms"].to_numpy(np.int64)

    years = pd.to_datetime(dtimes, unit="ms", utc=True).year
    if np.any(years != year):
        # A one-minute bar may close exactly at next-year midnight. The row belongs
        # to the bar-start year, so enforce by timestamp rather than decision time.
        bar_years = pd.to_datetime(m1["timestamp_ms"], unit="ms", utc=True).dt.year.to_numpy()
        if np.any(bar_years != year):
            fail("xauusd rows outside requested bar-start year")

    tf = {}
    for name, (rule, expected) in TF_RULES.items():
        tf[name] = resample_exact(m1, rule, expected)
    tf["d1"] = build_d1(tf["h1"])
    tf["w1"] = build_w1(tf["d1"])

    structural = add_structural_state(m1, tf)
    ss = session_state(m1)
    structural = structural.merge(ss, on="decision_time_ms", how="left", validate="one_to_one")
    add_previous_day(structural, dtimes, tf["d1"])

    dxy = load_dxy(dxy_path)
    dxy_available, dxy_age = dxy_alignment(dtimes, dxy)

    macro = load_macro_events(macro_path)
    schedule_available = macro_coverage_available(macro_coverage_path, year)
    macro_state = build_macro_state(dtimes, macro, schedule_available)

    dec_dt = pd.to_datetime(dtimes, unit="ms", utc=True)
    decision_index = pd.DataFrame({
        "timestamp_ms": m1["timestamp_ms"].to_numpy(np.int64),
        "decision_time_ms": dtimes,
        "year": year,
        "utc_date": dec_dt.strftime("%Y-%m-%d"),
        "ny_date": dec_dt.tz_convert("America/New_York").strftime("%Y-%m-%d"),
        "feature_ready_market": m1["core_240m_contiguous_ready"].to_numpy(np.int8),
        "dxy_available": dxy_available,
        "dxy_age_minutes": dxy_age,
        "macro_schedule_available": macro_state["macro_schedule_available"].to_numpy(np.int8),
        "market_state_version": "IPV1_STAGE2_V1",
    })

    trade = pd.DataFrame({
        "decision_time_ms": dtimes,
        "position_state": "FLAT",
        "open_position_count": 0,
        "entry_price": np.nan,
        "stop_price": np.nan,
        "target_price": np.nan,
        "minutes_in_position": 0,
        "session_realized_pnl": 0.0,
        "session_trade_count": 0,
        "consecutive_loss_count": 0,
        "risk_fraction_deployed": 0.0,
        "same_thesis_attempt_count": 0,
    })

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}

    p = out_dir / f"xauusd_m1_market_state_{year}.csv.gz"
    write_csv_gz(m1, p)
    outputs["xauusd_m1_market_state"] = str(p)

    for name, table in tf.items():
        p = out_dir / f"xauusd_{name}_{year}.csv.gz"
        write_csv_gz(table, p)
        outputs[f"xauusd_{name}"] = str(p)

    p = out_dir / f"xauusd_structural_state_{year}.csv.gz"
    write_csv_gz(structural, p)
    outputs["xauusd_structural_state"] = str(p)

    p = out_dir / f"macro_event_state_{year}.csv.gz"
    write_csv_gz(macro_state, p)
    outputs["macro_event_state"] = str(p)

    p = out_dir / f"decision_index_{year}.csv.gz"
    write_csv_gz(decision_index, p)
    outputs["decision_index"] = str(p)

    p = out_dir / f"trade_risk_state_template_{year}.csv.gz"
    write_csv_gz(trade, p)
    outputs["trade_risk_state_template"] = str(p)

    report = {
        "status": "PASS",
        "year": year,
        "scope": "TRAIN_ONLY",
        "sealed_periods_accessed": [],
        "rows": {
            "xauusd_m1_market_state": int(len(m1)),
            **{f"xauusd_{name}": int(len(table)) for name, table in tf.items()},
            "xauusd_structural_state": int(len(structural)),
            "macro_event_state": int(len(macro_state)),
            "decision_index": int(len(decision_index)),
            "trade_risk_state_template": int(len(trade)),
            "synthetic_dxy_m1": int(len(dxy)),
            "macro_event_schedule": int(len(macro)),
        },
        "coverage": {
            "feature_ready_market_share": float(decision_index["feature_ready_market"].mean()),
            "dxy_available_share": float(decision_index["dxy_available"].mean()),
            "macro_schedule_available": bool(schedule_available),
            "bid_flat_fill_rows": int(m1["bid_flat_fill"].sum()),
            "ask_flat_fill_rows": int(m1["ask_flat_fill"].sum()),
        },
        "first_timestamp_ms": int(m1.iloc[0]["timestamp_ms"]),
        "last_timestamp_ms": int(m1.iloc[-1]["timestamp_ms"]),
        "first_decision_time_ms": int(m1.iloc[0]["decision_time_ms"]),
        "last_decision_time_ms": int(m1.iloc[-1]["decision_time_ms"]),
        "outputs": outputs,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=json_number) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, default=json_number))


if __name__ == "__main__":
    main(sys.argv)
