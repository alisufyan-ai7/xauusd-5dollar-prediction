#!/usr/bin/env python3
"""Timestamp-safe EXP-001 M1 feature construction.

All features for decision row i use only rows <= i. The decision price is the
close of row i, matching EXP-001 labeling semantics.
"""
import csv, math, sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

OUT_FIELDS=[
"timestamp","decision_time_ms","reference_price","feature_complete",
"ret_1m","ret_5m","ret_15m","ret_60m",
"range_1m","body_1m","upper_wick_1m","lower_wick_1m",
"range_15m","range_60m","dist_high_15m","dist_low_15m",
"dist_high_60m","dist_low_60m","rv_15m","rv_60m",
"hour_utc","weekday_utc","session_utc"
]

def session(hour):
    if 0 <= hour < 7: return "ASIA"
    if 7 <= hour < 13: return "EUROPE"
    if 13 <= hour < 21: return "US"
    return "LATE"

def rows(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        yield from csv.DictReader(f)

def build(inp:Path,out:Path):
    data=list(rows(inp))
    out.parent.mkdir(parents=True,exist_ok=True)
    closes=[float(r["close"]) for r in data]
    highs=[float(r["high"]) for r in data]
    lows=[float(r["low"]) for r in data]
    opens=[float(r["open"]) for r in data]
    ts=[int(r["timestamp"]) for r in data]

    one_returns=[None]*len(data)
    for i in range(1,len(data)):
        if ts[i]-ts[i-1]==60000:
            one_returns[i]=closes[i]-closes[i-1]

    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=OUT_FIELDS); w.writeheader()
        for i in range(len(data)):
            dt=datetime.fromtimestamp((ts[i]+60000)/1000,tz=timezone.utc)
            complete=i>=60 and all(ts[k]-ts[k-1]==60000 for k in range(i-59,i+1))
            vals={
              "timestamp":ts[i],"decision_time_ms":ts[i]+60000,
              "reference_price":closes[i],"feature_complete":complete,
              "range_1m":highs[i]-lows[i],
              "body_1m":closes[i]-opens[i],
              "upper_wick_1m":highs[i]-max(opens[i],closes[i]),
              "lower_wick_1m":min(opens[i],closes[i])-lows[i],
              "hour_utc":dt.hour,"weekday_utc":dt.weekday(),"session_utc":session(dt.hour),
            }
            if complete:
                vals.update({
                  "ret_1m":closes[i]-closes[i-1],
                  "ret_5m":closes[i]-closes[i-5],
                  "ret_15m":closes[i]-closes[i-15],
                  "ret_60m":closes[i]-closes[i-60],
                  "range_15m":max(highs[i-14:i+1])-min(lows[i-14:i+1]),
                  "range_60m":max(highs[i-59:i+1])-min(lows[i-59:i+1]),
                  "dist_high_15m":max(highs[i-14:i+1])-closes[i],
                  "dist_low_15m":closes[i]-min(lows[i-14:i+1]),
                  "dist_high_60m":max(highs[i-59:i+1])-closes[i],
                  "dist_low_60m":closes[i]-min(lows[i-59:i+1]),
                  "rv_15m":math.sqrt(sum(x*x for x in one_returns[i-14:i+1])/15),
                  "rv_60m":math.sqrt(sum(x*x for x in one_returns[i-59:i+1])/60),
                })
            else:
                for k in ["ret_1m","ret_5m","ret_15m","ret_60m","range_15m","range_60m",
                          "dist_high_15m","dist_low_15m","dist_high_60m","dist_low_60m","rv_15m","rv_60m"]:
                    vals[k]=""
            w.writerow(vals)
    print(f"FEATURES_PASS rows={len(data)} output={out}")

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: build_features.py <raw.csv> <features.csv>")
    build(Path(sys.argv[1]),Path(sys.argv[2]))
