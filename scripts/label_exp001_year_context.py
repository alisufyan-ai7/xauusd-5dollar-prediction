#!/usr/bin/env python3
"""Label one EXP-001 year with optional next-year context.

The output contains labels only for rows originating in the primary year.
Next-year bars are used solely as forward context for the 60-minute horizon.
"""
import csv,json,sys
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("label_exp001",ROOT/"scripts"/"label_exp001.py")
m=importlib.util.module_from_spec(spec)
sys.modules["label_exp001"]=m
spec.loader.exec_module(m)

def main(argv):
    if len(argv) not in (3,4):
        raise SystemExit("usage: label_exp001_year_context.py <primary.csv> <labels.csv> [next.csv]")
    primary=Path(argv[1]);out=Path(argv[2])
    bars=m.load_m1(primary)
    primary_n=len(bars)
    if len(argv)==4:
        nxt=m.load_m1(Path(argv[3]))
        if nxt:
            cutoff=bars[-1].timestamp+(m.DEFAULT_HORIZON_MINUTES+1)*m.ONE_MINUTE_MS
            bars.extend([b for b in nxt if b.timestamp<cutoff])
    out.parent.mkdir(parents=True,exist_ok=True)
    counts={"buy":{"SUCCESS":0,"FAILURE":0,"UNRESOLVED":0,"AMBIGUOUS":0},
            "sell":{"SUCCESS":0,"FAILURE":0,"UNRESOLVED":0,"AMBIGUOUS":0}}
    incomplete=0
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=m.OUTPUT_COLUMNS);w.writeheader()
        for i,row in enumerate(m.label_rows(bars)):
            if i>=primary_n: break
            counts["buy"][row["buy_label"]]+=1
            counts["sell"][row["sell_label"]]+=1
            if not row["coverage_complete"]: incomplete+=1
            w.writerow(row)
    print(json.dumps({"status":"PASS","primary_rows":primary_n,
        "context_rows":len(bars)-primary_n,"incomplete_coverage_rows":incomplete,
        "counts":counts},indent=2,sort_keys=True))

if __name__=="__main__": main(sys.argv)
