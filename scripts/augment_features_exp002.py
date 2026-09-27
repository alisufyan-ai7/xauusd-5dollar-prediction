#!/usr/bin/env python3
"""Augment frozen BID-context V2 features with causal BID/ASK spread features for EXP-002."""

import bisect,csv,math,sys
from collections import deque
from pathlib import Path

EXTRA=[
"spread_close_1m","spread_mean_5m","spread_mean_15m","spread_mean_60m",
"spread_max_15m","spread_max_60m","spread_ratio_1m_to_60m","spread_percentile_240m"
]

def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def main(argv):
    if len(argv)!=5:
        raise SystemExit("usage: augment_features_exp002.py <bid.csv> <ask.csv> <base_features.csv> <out.csv>")
    bid=rows(Path(argv[1]));ask=rows(Path(argv[2]));base=rows(Path(argv[3]))
    if not (len(bid)==len(ask)==len(base)):raise SystemExit("ROW_COUNT_MISMATCH")
    ts=[];sp=[]
    for i,(b,a,f) in enumerate(zip(bid,ask,base)):
        if b["timestamp"]!=a["timestamp"] or b["timestamp"]!=f["timestamp"]:
            raise SystemExit(f"TIMESTAMP_MISMATCH:{i}")
        t=int(b["timestamp"]);s=float(a["close"])-float(b["close"])
        if s<0 or not math.isfinite(s):raise SystemExit(f"INVALID_SPREAD:{t}")
        ts.append(t);sp.append(s)

    p=[0.0]
    for x in sp:p.append(p[-1]+x)
    pct=[None]*len(sp);q=deque();sorted_vals=[]
    for i,v in enumerate(sp):
        while q and q[0][0]<i-239:
            _,old=q.popleft();sorted_vals.pop(bisect.bisect_left(sorted_vals,old))
        bisect.insort(sorted_vals,v);q.append((i,v))
        pct[i]=bisect.bisect_right(sorted_vals,v)/len(sorted_vals)

    out=Path(argv[4]);out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(base[0].keys())+EXTRA+["feature_version_exp002"] if base else []
    with out.open("w",encoding="utf-8",newline="") as fo:
        w=csv.DictWriter(fo,fieldnames=fields);w.writeheader()
        for i,f in enumerate(base):
            causal=i>=239 and all(ts[k]-ts[k-1]==60000 for k in range(i-238,i+1))
            vals=dict(f)
            vals["feature_version_exp002"]="EXP002_V1"
            vals["spread_close_1m"]=sp[i]
            if causal:
                mean=lambda n:(p[i+1]-p[i+1-n])/n
                vals["spread_mean_5m"]=mean(5)
                vals["spread_mean_15m"]=mean(15)
                vals["spread_mean_60m"]=mean(60)
                vals["spread_max_15m"]=max(sp[i-14:i+1])
                vals["spread_max_60m"]=max(sp[i-59:i+1])
                vals["spread_ratio_1m_to_60m"]=sp[i]/vals["spread_mean_60m"] if vals["spread_mean_60m"] else 0.0
                vals["spread_percentile_240m"]=pct[i]
            else:
                for k in EXTRA[1:]:vals[k]=""
                vals["feature_complete"]="False"
            w.writerow(vals)
    print(f"EXP002_FEATURES_PASS rows={len(base)} output={out}")

if __name__=="__main__":main(sys.argv)
