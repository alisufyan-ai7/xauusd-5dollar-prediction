#!/usr/bin/env python3
"""Generate deterministic fake market files around real frozen teacher minutes for no-provider rehearsal."""
from __future__ import annotations
import csv,math,sys
from pathlib import Path
import pandas as pd

SCHEMA=["timestamp","open","high","low","close","volume"]
BASE={"xauusd":2350.0,"eurusd":1.08,"usdjpy":150.0,"gbpusd":1.27,"usdcad":1.36,"usdsek":10.4,"usdchf":0.89}

def write(path,times,base,spread=0.0,scale=1.0):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=SCHEMA); w.writeheader()
        for i,t in enumerate(times):
            wave=math.sin((t//60000)%997/37.0)*scale
            trend=((t//60000)%131)*scale/500.0
            close=base+wave+trend+spread
            op=close-math.sin(i/13.0)*scale/20
            hi=max(op,close)+scale/30
            lo=min(op,close)-scale/30
            w.writerow({"timestamp":t,"open":f"{op:.8f}","high":f"{hi:.8f}","low":f"{lo:.8f}","close":f"{close:.8f}","volume":f"{1+(i%17)/10:.4f}"})

def main(argv):
    if len(argv)!=3: raise SystemExit("usage: generate_stage3b_2026_synthetic_market.py <teacher.csv> <raw-dir>")
    teacher=pd.read_csv(argv[1],dtype=str,keep_default_na=False)
    e=teacher[teacher.primary_task_a_eligible.str.lower()=="true"]
    times=set()
    for _,g in e.groupby("source_date"):
        a=min(pd.Timestamp(x).value//1_000_000 for x in g.interval_start_utc)
        b=max(pd.Timestamp(x).value//1_000_000 for x in g.interval_end_utc)
        start=a-360*60000
        end=b+10*60000
        times.update(range(int(start),int(end)+1,60000))
    times=sorted(times); raw=Path(argv[2])
    write(raw/"xauusd"/"xauusd-bid.csv",times,BASE["xauusd"],0,0.8)
    write(raw/"xauusd"/"xauusd-ask.csv",times,BASE["xauusd"],0.25,0.8)
    for j,inst in enumerate(("eurusd","usdjpy","gbpusd","usdcad","usdsek","usdchf")):
        scale=0.001 if BASE[inst]<2 else 0.02
        write(raw/"fx"/f"{inst}-bid.csv",times,BASE[inst],0,scale*(1+j/10))
    print(f"SYNTHETIC_STAGE3B_MARKET_ROWS_PER_SERIES={len(times)}")

if __name__=="__main__":
    main(sys.argv)
