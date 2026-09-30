#!/usr/bin/env python3
"""TRAIN-only Root-Reset V5 Badar A+ source-fidelity experiment."""

import json
import math
import sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import root_reset_v4_badar_core as v4


def frozen_ref(side, states, confirm_t):
    s = v4.lookup_row(states, confirm_t)
    if s is None:
        return None
    ref = float(s["swing_high"] if side == "BUY" else s["swing_low"])
    return ref if math.isfinite(ref) else None


def first_one_close_mss(side, confirm_t, expire_t, bars, states):
    ref = frozen_ref(side, states, confirm_t)
    if ref is None:
        return None
    p0 = bars.index.searchsorted(confirm_t, side="right")
    p1 = bars.index.searchsorted(expire_t, side="right")
    cl = bars["close"].to_numpy(float)
    for j in range(p0, p1):
        ok = cl[j] > ref if side == "BUY" else cl[j] < ref
        if ok:
            return {"time": bars.index[j], "j": int(j), "ref": ref}
    return None


def first_mss_with_fvg(side, confirm_t, expire_t, bars, states, timeframe):
    ref = frozen_ref(side, states, confirm_t)
    if ref is None:
        return None
    p0 = bars.index.searchsorted(confirm_t, side="right")
    p1 = bars.index.searchsorted(expire_t, side="right")
    cl = bars["close"].to_numpy(float)
    hi = bars["high"].to_numpy(float)
    lo = bars["low"].to_numpy(float)

    for j in range(p0, p1):
        ok = cl[j] > ref if side == "BUY" else cl[j] < ref
        if not ok:
            continue

        chosen = None
        for k in (j, j - 1, j - 2):
            if k < 2 or bars.index[k] <= confirm_t:
                continue
            if side == "BUY" and hi[k - 2] < lo[k]:
                chosen = (k, float(hi[k - 2]), float(lo[k]))
                break
            if side == "SELL" and lo[k - 2] > hi[k]:
                chosen = (k, float(hi[k]), float(lo[k - 2]))
                break

        if chosen is None:
            continue

        k, lower, upper = chosen
        return {
            "time": bars.index[j],
            "j": int(j),
            "k": int(k),
            "ref": ref,
            "lower": lower,
            "upper": upper,
            "timeframe": timeframe,
        }
    return None


def select_trigger(m5_trigger, m3_trigger):
    if m5_trigger is None:
        return m3_trigger
    if m3_trigger is None:
        return m5_trigger
    if m5_trigger["time"] < m3_trigger["time"]:
        return m5_trigger
    if m3_trigger["time"] < m5_trigger["time"]:
        return m3_trigger
    return m5_trigger


def prior_utc_day(bid, tok):
    pday = (tok - pd.Timedelta(days=1)).floor("D")
    z = bid.loc[(bid.index >= pday) & (bid.index < pday + pd.Timedelta(days=1))]
    if z.empty:
        return None
    return {"high": float(z["high"].max()), "low": float(z["low"].min())}


def final_target_candidates(side, entry, prevday, sth1, sth4, t):
    out = []
    if prevday is not None:
        px = float(prevday["high"] if side == "BUY" else prevday["low"])
        if (side == "BUY" and px > entry) or (side == "SELL" and px < entry):
            out.append(("PREV_DAY", px))

    s1 = v4.lookup_row(sth1, t)
    if s1 is not None:
        px = float(s1["swing_high"] if side == "BUY" else s1["swing_low"])
        if math.isfinite(px) and ((side == "BUY" and px > entry) or (side == "SELL" and px < entry)):
            out.append(("H1_SWING", px))

    s4 = v4.lookup_row(sth4, t)
    if s4 is not None:
        px = float(s4["swing_high"] if side == "BUY" else s4["swing_low"])
        if math.isfinite(px) and ((side == "BUY" and px > entry) or (side == "SELL" and px < entry)):
            out.append(("H4_SWING", px))

    dedup = {}
    for fam, px in out:
        key = round(px, 8)
        if key not in dedup:
            dedup[key] = (fam, px)
        elif fam == "H4_SWING":
            dedup[key] = (fam, px)
    return list(dedup.values())


def distance(side, entry, target):
    return (target - entry) if side == "BUY" else (entry - target)


def session_intermediate(side, entry, final_target, asian, london):
    vals = []
    if side == "BUY":
        vals = [float(x) for x in (asian["high"], london["high"]) if float(x) > entry]
        if not vals:
            return None
        px = min(vals)
        return px if px < final_target else None
    vals = [float(x) for x in (asian["low"], london["low"]) if float(x) < entry]
    if not vals:
        return None
    px = max(vals)
    return px if px > final_target else None


def summarize_rows(rows):
    if not rows:
        return {"count": 0}

    good120 = [r for r in rows if r.get("p120") is not None and r.get("struct120") is not None]
    good60 = [r for r in rows if r.get("p60") is not None and r.get("struct60") is not None]
    out = {
        "count": len(good120),
        "raw_filled_rows": len(rows),
        "trigger_timeframes": {
            "M5": sum(r["trigger_tf"] == "M5" for r in rows),
            "M3": sum(r["trigger_tf"] == "M3" for r in rows),
        },
        "fill_wait_minutes": v4.summarize([r["fill_wait_minutes"] for r in rows]),
        "stop_distance": v4.summarize([r["stop_dist"] for r in rows]),
        "target_distance": v4.summarize([r["target_dist"] for r in rows]),
        "target_stop_rr": v4.summarize([r["target_stop_rr"] for r in rows]),
        "target_families": {
            fam: sum(r["target_family"] == fam for r in rows)
            for fam in ("PREV_DAY", "H1_SWING", "H4_SWING")
        },
        "intermediate_session_before_final_count": sum(r.get("intermediate_session") is not None for r in rows),
        "mfe60": v4.summarize([r["p60"]["mfe"] for r in good60]),
        "mae60": v4.summarize([r["p60"]["mae"] for r in good60]),
        "mfe120": v4.summarize([r["p120"]["mfe"] for r in good120]),
        "mae120": v4.summarize([r["p120"]["mae"] for r in good120]),
        "hit3_rate_120": float(np.mean([r["p120"]["hit3"] for r in good120])) if good120 else None,
        "hit5_rate_120": float(np.mean([r["p120"]["hit5"] for r in good120])) if good120 else None,
        "hit7_rate_120": float(np.mean([r["p120"]["hit7"] for r in good120])) if good120 else None,
        "plus5_before3_rate_120": float(np.mean([r["p120"]["plus5_before3"] for r in good120])) if good120 else None,
        "struct60": v4.stop_summary(good60, "struct60"),
        "struct120": v4.stop_summary(good120, "struct120"),
    }

    if good60:
        med_mfe = float(np.median([r["p60"]["mfe"] for r in good60]))
        med_mae = float(np.median([r["p60"]["mae"] for r in good60]))
        out["median_mfe60_to_median_mae60"] = med_mfe / max(med_mae, 1e-9)
    if good120:
        mfe = np.asarray([r["p120"]["mfe"] for r in good120], float)
        mae = np.asarray([r["p120"]["mae"] for r in good120], float)
        out["median_mfe120_to_median_mae120"] = float(np.median(mfe) / max(np.median(mae), 1e-9))
        out["year_path_edge_proxy"] = float(np.median(mfe - mae))
    return out


def main(argv):
    if len(argv) != 1 + 6 * 2:
        raise SystemExit("usage: root_reset_v5_badar_source_fidelity.py 6x <bid.csv> <ask.csv>")

    bids = []
    asks = []
    for i in range(6):
        bid, ask = v4.load_pair(argv[1 + i * 2], argv[2 + i * 2])
        bids.append(bid)
        asks.append(ask)

    bid = pd.concat(bids).sort_index()
    ask = pd.concat(asks).sort_index()
    if bid.index.has_duplicates or ask.index.has_duplicates:
        raise SystemExit("DUPLICATE_TIMESTAMP")

    ts = bid["timestamp"].to_numpy(np.int64)
    bhi = bid["high"].to_numpy(float)
    blo = bid["low"].to_numpy(float)

    m3 = v4.resample_exact(bid, "3min", 3)
    m5 = v4.resample_exact(bid, "5min", 5)
    m15 = v4.resample_exact(bid, "15min", 15)
    h1 = v4.resample_exact(bid, "1h", 60)
    h4 = v4.resample_exact(bid, "4h", 240)
    d1 = v4.build_d1_from_h1(h1)
    ask15 = v4.resample_exact(ask, "15min", 15)

    st3 = v4.structure_state(m3)
    st5 = v4.structure_state(m5)
    sth1 = v4.structure_state(h1)
    sth4 = v4.structure_state(h4)
    std1 = v4.structure_state(d1)
    fvgs = v4.build_h1_fvgs(h1)

    funnel = defaultdict(int)
    yearly_funnel = defaultdict(lambda: defaultdict(int))
    rows = []

    first_date = pd.Timestamp(bid.index.min()).tz_convert(v4.NY).date()
    last_date = pd.Timestamp(bid.index.max()).tz_convert(v4.NY).date()
    d = first_date

    while d <= last_date:
        if d.year < 2016 or d.year > 2021:
            d += timedelta(days=1)
            continue

        tokyo, lon, nyopen, ex0, ex1, cap = v4.session_bounds(d)
        tok = pd.Timestamp(tokyo)
        lon_t = pd.Timestamp(lon)
        ny_t = pd.Timestamp(nyopen)
        ex0t = pd.Timestamp(ex0)
        ex1t = pd.Timestamp(ex1)
        capt = pd.Timestamp(cap)

        asian = v4.range_stats(ts, bhi, blo, v4.ts_ms(tok), v4.ts_ms(lon_t))
        london = v4.range_stats(ts, bhi, blo, v4.ts_ms(lon_t), v4.ts_ms(ny_t))
        if asian is None or london is None:
            d += timedelta(days=1)
            continue

        funnel["ny_dates_observed"] += 1
        yearly_funnel[d.year]["ny_dates_observed"] += 1

        day15 = m15.loc[(m15.index > ex0t) & (m15.index <= ex1t)]
        if day15.empty:
            d += timedelta(days=1)
            continue

        prevday = prior_utc_day(bid, tok)

        for side in ("BUY", "SELL"):
            filled_for_side = False
            blocked_until = ex0t
            dir_day_counted = False

            for t, bar in day15.iterrows():
                if filled_for_side or t < blocked_until or v4.is_news_time(t):
                    continue

                s1 = v4.lookup_row(sth1, t)
                s4 = v4.lookup_row(sth4, t)
                sd = v4.lookup_row(std1, t)
                if s1 is None or s4 is None or sd is None:
                    continue

                h1s = int(s1["state"])
                h4s = int(s4["state"])
                d1s = int(sd["state"])
                eligible = (h1s == 1 and h4s != -1 and d1s != -1) if side == "BUY" else (
                    h1s == -1 and h4s != 1 and d1s != 1
                )
                if not eligible:
                    continue

                if not dir_day_counted:
                    funnel["directionally_eligible_session_days"] += 1
                    yearly_funnel[d.year]["directionally_eligible_session_days"] += 1
                    dir_day_counted = True

                p = m15.index.get_loc(t)
                if p < 4:
                    continue
                prev = m15.iloc[p - 4 : p]
                trs = []
                prev_close = None
                for ii, rr in prev.iterrows():
                    if prev_close is None:
                        prev_pos = m15.index.get_loc(ii) - 1
                        if prev_pos < 0:
                            break
                        prev_close = float(m15.iloc[prev_pos]["close"])
                    tr = max(
                        float(rr["high"] - rr["low"]),
                        abs(float(rr["high"]) - prev_close),
                        abs(float(rr["low"]) - prev_close),
                    )
                    trs.append(tr)
                    prev_close = float(rr["close"])
                if len(trs) != 4:
                    continue
                atr15 = float(np.mean(trs))
                if not math.isfinite(atr15) or atr15 <= 0:
                    continue
                buf = 0.05 * atr15

                levels = (asian["low"], london["low"]) if side == "BUY" else (asian["high"], london["high"])
                if side == "BUY":
                    pierced = [x for x in levels if float(bar["low"]) < x - buf]
                else:
                    pierced = [x for x in levels if float(bar["high"]) > x + buf]
                if not pierced:
                    continue

                funnel["m15_liquidity_sweeps"] += 1
                yearly_funnel[d.year]["m15_liquidity_sweeps"] += 1
                level = min(pierced) if side == "BUY" else max(pierced)

                h1fvg = v4.active_fvg(fvgs, side, t, float(bar["low"]), float(bar["high"]))
                if h1fvg is None:
                    continue

                funnel["sweeps_overlapping_h1_fvg"] += 1
                yearly_funnel[d.year]["sweeps_overlapping_h1_fvg"] += 1

                closeback = float(bar["close"]) > level if side == "BUY" else float(bar["close"]) < level
                if not closeback:
                    continue

                funnel["m15_closeback_confirmations"] += 1
                yearly_funnel[d.year]["m15_closeback_confirmations"] += 1

                pending_end = min(t + pd.Timedelta(minutes=30), ex1t)

                m5_mss = first_one_close_mss(side, t, pending_end, m5, st5)
                m3_mss = first_one_close_mss(side, t, pending_end, m3, st3)
                if m5_mss is not None:
                    funnel["m5_one_close_mss"] += 1
                    yearly_funnel[d.year]["m5_one_close_mss"] += 1
                if m3_mss is not None:
                    funnel["m3_one_close_mss"] += 1
                    yearly_funnel[d.year]["m3_one_close_mss"] += 1

                m5_trigger = first_mss_with_fvg(side, t, pending_end, m5, st5, "M5")
                m3_trigger = first_mss_with_fvg(side, t, pending_end, m3, st3, "M3")
                trigger = select_trigger(m5_trigger, m3_trigger)

                if trigger is None:
                    blocked_until = pending_end
                    continue

                funnel["mss_with_displacement_fvg_trigger"] += 1
                yearly_funnel[d.year]["mss_with_displacement_fvg_trigger"] += 1
                tfkey = "selected_m5_trigger" if trigger["timeframe"] == "M5" else "selected_m3_trigger"
                funnel[tfkey] += 1
                yearly_funnel[d.year][tfkey] += 1

                entry = float(trigger["upper"] if side == "BUY" else trigger["lower"])

                if side == "BUY":
                    stop = float(bar["low"]) - buf
                else:
                    a15 = ask15.loc[t] if t in ask15.index else None
                    if a15 is None:
                        blocked_until = pending_end
                        continue
                    stop = float(a15["high"]) + buf

                stop_dist = (entry - stop) if side == "BUY" else (stop - entry)
                if not math.isfinite(stop_dist) or stop_dist <= 0:
                    blocked_until = pending_end
                    continue

                funnel["valid_structural_stop"] += 1
                yearly_funnel[d.year]["valid_structural_stop"] += 1

                candidates = final_target_candidates(side, entry, prevday, sth1, sth4, trigger["time"])
                if not candidates:
                    blocked_until = pending_end
                    continue

                funnel["valid_final_htf_target"] += 1
                yearly_funnel[d.year]["valid_final_htf_target"] += 1

                ge5 = []
                for fam, px in candidates:
                    dist = distance(side, entry, px)
                    if dist >= 5.0:
                        ge5.append((dist, fam, px))
                if not ge5:
                    blocked_until = pending_end
                    continue

                funnel["target_distance_ge_5"] += 1
                yearly_funnel[d.year]["target_distance_ge_5"] += 1

                qual = [x for x in ge5 if x[0] / stop_dist >= 3.0]
                if not qual:
                    blocked_until = pending_end
                    continue

                qual.sort(key=lambda x: x[0])
                target_dist, target_family, target = qual[0]
                target_rr = target_dist / stop_dist

                funnel["target_stop_rr_ge_3"] += 1
                yearly_funnel[d.year]["target_stop_rr_ge_3"] += 1

                intermediate = session_intermediate(side, entry, target, asian, london)
                if intermediate is not None:
                    funnel["intermediate_session_before_final"] += 1
                    yearly_funnel[d.year]["intermediate_session_before_final"] += 1

                order_end = min(trigger["time"] + pd.Timedelta(minutes=30), ex1t)
                funnel["proximal_limit_orders_placed"] += 1
                yearly_funnel[d.year]["proximal_limit_orders_placed"] += 1

                fill = v4.first_limit_fill(side, entry, bid, ask, trigger["time"], order_end)
                if fill is None:
                    blocked_until = order_end
                    continue

                funnel["proximal_limit_orders_filled"] += 1
                yearly_funnel[d.year]["proximal_limit_orders_filled"] += 1
                filled_for_side = True

                h60 = min(fill + pd.Timedelta(minutes=60), capt)
                h120 = min(fill + pd.Timedelta(minutes=120), capt)
                p60 = v4.path_metrics(side, entry, fill, bid, ask, h60)
                p120 = v4.path_metrics(side, entry, fill, bid, ask, h120)
                struct60 = v4.outcome_for_stop(side, entry, target, stop, fill, bid, ask, h60)
                struct120 = v4.outcome_for_stop(side, entry, target, stop, fill, bid, ask, h120)

                if p120 is None or struct120 is None:
                    funnel["invalid_postfill_path"] += 1
                    yearly_funnel[d.year]["invalid_postfill_path"] += 1

                rows.append(
                    {
                        "date": d.isoformat(),
                        "year": d.year,
                        "side": side,
                        "m15_confirm_time": t.isoformat(),
                        "trigger_time": trigger["time"].isoformat(),
                        "trigger_tf": trigger["timeframe"],
                        "entry": entry,
                        "fill_time": fill.isoformat(),
                        "fill_wait_minutes": float((fill - trigger["time"]).total_seconds() / 60.0),
                        "stop": stop,
                        "stop_dist": float(stop_dist),
                        "target": float(target),
                        "target_family": target_family,
                        "target_dist": float(target_dist),
                        "target_stop_rr": float(target_rr),
                        "intermediate_session": None if intermediate is None else float(intermediate),
                        "m15_liquidity_level": float(level),
                        "atr15": float(atr15),
                        "h1_fvg_lower": float(h1fvg[2]),
                        "h1_fvg_upper": float(h1fvg[3]),
                        "execution_fvg_lower": float(trigger["lower"]),
                        "execution_fvg_upper": float(trigger["upper"]),
                        "p60": p60,
                        "p120": p120,
                        "struct60": struct60,
                        "struct120": struct120,
                    }
                )

        d += timedelta(days=1)

    report = {
        "status": "PASS",
        "experiment": "ROOT_RESET_V5_BADAR_SOURCE_FIDELITY",
        "scope": "TRAIN_2016_2021_ONLY",
        "validation_accessed": False,
        "development_test_accessed": False,
        "final_oos": "NOT_ACCESSED",
        "funnel": dict(funnel),
        "yearly_funnel": {str(y): dict(v) for y, v in yearly_funnel.items()},
        "overall": summarize_rows(rows),
        "by_side": {},
        "by_year": {},
    }

    for side in ("BUY", "SELL"):
        report["by_side"][side] = summarize_rows([r for r in rows if r["side"] == side])
    for y in range(2016, 2022):
        report["by_year"][str(y)] = summarize_rows([r for r in rows if r["year"] == y])

    overall = report["overall"]
    counts = [report["by_year"][str(y)].get("count", 0) for y in range(2016, 2022)]
    edges = [report["by_year"][str(y)].get("year_path_edge_proxy") for y in range(2016, 2022)]
    valid_edges = [x for x in edges if x is not None]

    entry_pass = bool(
        overall.get("count", 0) >= 180
        and all(c >= 20 for c in counts)
        and (overall.get("median_mfe120_to_median_mae120") or 0) >= 1.10
        and len(valid_edges) == 6
        and float(np.median(valid_edges)) > 0
        and sum(x > 0 for x in valid_edges) >= 4
        and (overall.get("plus5_before3_rate_120") or 0) >= 0.35
    )

    s = overall.get("struct120", {"n": 0})
    yearly_net = [
        report["by_year"][str(y)].get("struct120", {}).get("mean_net_f10_r")
        for y in range(2016, 2022)
    ]
    valid_net = [x for x in yearly_net if x is not None]
    stop_pass = bool(
        s.get("n", 0) > 0
        and (s.get("mean_net_f10_r") or 0) > 0
        and (s.get("profit_factor") or 0) > 1
        and len(valid_net) == 6
        and sum(x > 0 for x in valid_net) >= 4
        and min(valid_net) >= -0.35
    )

    report["advancement"] = {
        "entry_population_pass": entry_pass,
        "structural_stop_pass": stop_pass,
        "eligible_for_future_2022_preregistration": bool(entry_pass and stop_pass),
    }

    out = Path("data/reports/root-reset-v5/source-fidelity-train.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "PASS",
                "filled_rows": len(rows),
                "economic_rows": report["overall"].get("count", 0),
                "advancement": report["advancement"],
                "validation_accessed": False,
                "development_test_accessed": False,
                "final_oos": "NOT_ACCESSED",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main(sys.argv)
