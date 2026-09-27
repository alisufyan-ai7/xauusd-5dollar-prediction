#!/usr/bin/env python3
"""Synchronize sparse Dukascopy BID/ASK M1 candles for EXP-002.

Use the union of observed timestamps. If exactly one side is missing, it may be
represented as a zero-volume flat candle at that side's immediately prior
observed close, but only when the resulting paired OHLC remains executable-side
consistent. Invalid stale-quote reconstructions are dropped conservatively.

Timestamps absent on both sides are never created.
"""

import csv,json,sys
from pathlib import Path

FIELDS=["timestamp","open","high","low","close","volume"]

def load(path):
    out={}
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        for row in r:
            out[int(row["timestamp"])]=row
    return out

def flat(ts,close):
    s=f"{close:.10f}".rstrip("0").rstrip(".")
    return {"timestamp":str(ts),"open":s,"high":s,"low":s,"close":s,"volume":"0"}

def pair_valid(b,a):
    return (
        float(a["open"]) >= float(b["open"]) and
        float(a["high"]) >= float(b["high"]) and
        float(a["low"]) >= float(b["low"]) and
        float(a["close"]) >= float(b["close"])
    )

def write(path,rows):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

def main(argv):
    if len(argv)!=5:
        raise SystemExit("usage: synchronize_exp002_m1.py <bid.csv> <ask.csv> <out_bid.csv> <out_ask.csv>")
    bid=load(argv[1]);ask=load(argv[2])
    times=sorted(set(bid)|set(ask))
    outb=[];outa=[]
    lastb=None;lasta=None
    fillb=filla=0
    leading_dropped=0
    invalid_fill_dropped=0

    for ts in times:
        rb=bid.get(ts);ra=ask.get(ts)

        # Update last actually observed closes independently, even if this
        # timestamp later cannot be emitted as a synchronized pair.
        if rb is not None:
            lastb=float(rb["close"])
        if ra is not None:
            lasta=float(ra["close"])

        if rb is None:
            if lastb is None:
                leading_dropped+=1
                continue
            b=flat(ts,lastb)
        else:
            b=rb

        if ra is None:
            if lasta is None:
                leading_dropped+=1
                continue
            a=flat(ts,lasta)
        else:
            a=ra

        if not pair_valid(b,a):
            if rb is not None and ra is not None:
                raise SystemExit(f"OBSERVED_PAIR_OHLC_INVERSION:{ts}")
            invalid_fill_dropped+=1
            continue

        if rb is None: fillb+=1
        if ra is None: filla+=1
        outb.append(b);outa.append(a)

    write(argv[3],outb);write(argv[4],outa)
    print(json.dumps({
        "status":"PASS","rows":len(outb),
        "bid_flat_fills":fillb,"ask_flat_fills":filla,
        "leading_unpaired_dropped":leading_dropped,
        "invalid_flat_fill_dropped":invalid_fill_dropped
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main(sys.argv)
