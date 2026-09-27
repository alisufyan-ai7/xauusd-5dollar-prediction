#!/usr/bin/env python3
"""EXP-002 executable-side M1 labeling from synchronized BID and ASK candles."""

from __future__ import annotations
import csv,sys,json
from dataclasses import dataclass
from pathlib import Path

ONE=60000
H=60
TARGET=5.0
ADVERSE=3.0

@dataclass(frozen=True)
class Bar:
    timestamp:int
    open:float
    high:float
    low:float
    close:float

def load(path:Path):
    out=[]
    with path.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        for x in r:
            out.append(Bar(int(x["timestamp"]),float(x["open"]),float(x["high"]),float(x["low"]),float(x["close"])))
    return out

def sync(bid,ask):
    if len(bid)!=len(ask): raise SystemExit("BID_ASK_ROW_COUNT_MISMATCH")
    for i,(b,a) in enumerate(zip(bid,ask)):
        if b.timestamp!=a.timestamp: raise SystemExit(f"BID_ASK_TIMESTAMP_MISMATCH:{i}")
        if a.open < b.open or a.high < b.high or a.low < b.low or a.close < b.close:
            # Dukascopy OHLC sides should not invert. Treat as invalid snapshot.
            raise SystemExit(f"NEGATIVE_SPREAD_OHLC:{b.timestamp}")

def scan(bid,ask,i,direction):
    decision=bid[i].timestamp+ONE
    start=i+1
    end=start+H
    if end>len(bid): return ("UNRESOLVED","",False,"",None,None,None)
    expected=[decision+k*ONE for k in range(H)]
    actual=[bid[j].timestamp for j in range(start,end)]
    actual2=[ask[j].timestamp for j in range(start,end)]
    complete=(actual==expected and actual2==expected)
    if not complete: return ("UNRESOLVED","",False,"",None,None,None)

    if direction=="BUY":
        entry=ask[start].open
        target=entry+TARGET; adverse=entry-ADVERSE
    else:
        entry=bid[start].open
        target=entry-TARGET; adverse=entry+ADVERSE

    label="UNRESOLVED";terminal=""
    for j in range(start,end):
        if direction=="BUY":
            t=bid[j].high>=target
            a=bid[j].low<=adverse
        else:
            t=ask[j].low<=target
            a=ask[j].high>=adverse
        if t and a:
            label="AMBIGUOUS";terminal=bid[j].timestamp;break
        if t:
            label="SUCCESS";terminal=bid[j].timestamp;break
        if a:
            label="FAILURE";terminal=bid[j].timestamp;break

    expiry_bid=bid[end-1].close
    expiry_ask=ask[end-1].close
    expiry_pnl=(expiry_bid-entry) if direction=="BUY" else (entry-expiry_ask)
    return (label,terminal,True,entry,target,adverse,expiry_pnl)

FIELDS=[
"timestamp","decision_time_ms","coverage_complete",
"buy_entry_ask","buy_target_bid","buy_adverse_bid","buy_label","buy_terminal_bar_timestamp_ms","buy_expiry_pnl",
"sell_entry_bid","sell_target_ask","sell_adverse_ask","sell_label","sell_terminal_bar_timestamp_ms","sell_expiry_pnl"
]

def main(argv):
    if len(argv) not in (4,6):
        raise SystemExit("usage: label_exp002.py <bid.csv> <ask.csv> <out.csv> [next_bid.csv next_ask.csv]")
    bid=load(Path(argv[1])); ask=load(Path(argv[2])); primary=len(bid)
    sync(bid,ask)
    if len(argv)==6:
        nb=load(Path(argv[4]));na=load(Path(argv[5]));sync(nb,na)
        if nb:
            cutoff=bid[-1].timestamp+(H+1)*ONE
            for b,a in zip(nb,na):
                if b.timestamp<cutoff:
                    bid.append(b);ask.append(a)
    out=Path(argv[3]);out.parent.mkdir(parents=True,exist_ok=True)
    counts={d:{k:0 for k in ("SUCCESS","FAILURE","UNRESOLVED","AMBIGUOUS")} for d in ("BUY","SELL")}
    incomplete=0
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader()
        for i in range(primary):
            b=scan(bid,ask,i,"BUY");s=scan(bid,ask,i,"SELL")
            complete=bool(b[2] and s[2])
            if not complete:incomplete+=1
            counts["BUY"][b[0]]+=1;counts["SELL"][s[0]]+=1
            w.writerow({
                "timestamp":bid[i].timestamp,
                "decision_time_ms":bid[i].timestamp+ONE,
                "coverage_complete":complete,
                "buy_entry_ask":"" if b[3] is None else b[3],
                "buy_target_bid":"" if b[4] is None else b[4],
                "buy_adverse_bid":"" if b[5] is None else b[5],
                "buy_label":b[0],"buy_terminal_bar_timestamp_ms":b[1],
                "buy_expiry_pnl":"" if b[6] is None else b[6],
                "sell_entry_bid":"" if s[3] is None else s[3],
                "sell_target_ask":"" if s[4] is None else s[4],
                "sell_adverse_ask":"" if s[5] is None else s[5],
                "sell_label":s[0],"sell_terminal_bar_timestamp_ms":s[1],
                "sell_expiry_pnl":"" if s[6] is None else s[6],
            })
    print(json.dumps({"status":"PASS","rows":primary,"incomplete":incomplete,"counts":counts},indent=2,sort_keys=True))

if __name__=="__main__":
    main(sys.argv)
