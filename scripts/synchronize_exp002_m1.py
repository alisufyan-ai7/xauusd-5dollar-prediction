#!/usr/bin/env python3
"""Synchronize sparse Dukascopy BID/ASK M1 candles for EXP-002.

Dukascopy may omit a flat M1 candle independently on one price side. This
module uses the union of observed timestamps. If one side has a real bar and
the other side is missing at that same minute, the missing side is represented
as a zero-volume flat candle at its immediately prior close.

Minutes absent on BOTH sides are not created, so weekends/session closures and
true common gaps remain gaps and are still rejected by downstream exact
contiguity checks.
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

def write(path,rows):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

def main(argv):
    if len(argv)!=5:
        raise SystemExit("usage: synchronize_exp002_m1.py <bid.csv> <ask.csv> <out_bid.csv> <out_ask.csv>")
    bid=load(argv[1]);ask=load(argv[2])
    times=sorted(set(bid)|set(ask))
    outb=[];outa=[];lastb=None;lasta=None
    fillb=filla=0
    dropped=0
    for ts in times:
        b=bid.get(ts);a=ask.get(ts)
        if b is None:
            if lastb is None:
                dropped+=1
                continue
            b=flat(ts,lastb);fillb+=1
        if a is None:
            if lasta is None:
                dropped+=1
                continue
            a=flat(ts,lasta);filla+=1
        # Preserve executable-side ordering sanity.
        if float(a["close"]) < float(b["close"]):
            raise SystemExit(f"NEGATIVE_CLOSE_SPREAD:{ts}")
        outb.append(b);outa.append(a)
        lastb=float(b["close"]);lasta=float(a["close"])

    write(argv[3],outb);write(argv[4],outa)
    print(json.dumps({
        "status":"PASS","rows":len(outb),
        "bid_flat_fills":fillb,"ask_flat_fills":filla,
        "leading_unpaired_dropped":dropped
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main(sys.argv)
