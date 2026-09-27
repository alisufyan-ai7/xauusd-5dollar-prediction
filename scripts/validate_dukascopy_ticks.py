#!/usr/bin/env python3
"""Validate Dukascopy XAUUSD tick CSV containing ASK and BID."""

import csv,hashlib,json,math,sys
from pathlib import Path

COLS=["timestamp","askPrice","bidPrice","askVolume","bidVolume"]

def main(argv):
    if len(argv)!=2:raise SystemExit("usage: validate_dukascopy_ticks.py <ticks.csv>")
    p=Path(argv[1]);n=0;prev=None;bad_spread=0
    first=last=None
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        if r.fieldnames!=COLS:raise SystemExit(f"UNEXPECTED_COLUMNS:{r.fieldnames}")
        for row in r:
            ts=int(row["timestamp"]);ask=float(row["askPrice"]);bid=float(row["bidPrice"])
            av=float(row["askVolume"]);bv=float(row["bidVolume"])
            if prev is not None and ts<prev:raise SystemExit("NONMONOTONIC_TIMESTAMP")
            if not all(math.isfinite(x) for x in (ask,bid,av,bv)):raise SystemExit("NONFINITE")
            if ask<=0 or bid<=0 or av<0 or bv<0:raise SystemExit("INVALID_VALUE")
            if ask<bid:bad_spread+=1
            if first is None:first=ts
            last=ts;prev=ts;n+=1
    if n==0:raise SystemExit("EMPTY_TICK_FILE")
    if bad_spread:raise SystemExit(f"NEGATIVE_SPREAD_ROWS:{bad_spread}")
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps({"status":"PASS","rows":n,"first_timestamp":first,"last_timestamp":last,"sha256":h},indent=2))

if __name__=="__main__":main(sys.argv)
