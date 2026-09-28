#!/usr/bin/env python3
"""Build EXP-006 causal path-state features on top of EXP-005/EXP-002 features."""

import csv,math,sys
from pathlib import Path

WINDOWS=(5,15,30,60,120,240)
PATH_FEATURES=[]
for w in WINDOWS:
    PATH_FEATURES += [
        f"path_efficiency_{w}m",
        f"sign_change_rate_{w}m",
        f"jump_concentration_{w}m",
        f"time_since_high_{w}m",
        f"time_since_low_{w}m",
        f"synthetic_body_range_ratio_{w}m",
    ]

def rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def safe_div(a,b):
    return a/b if b and math.isfinite(b) else 0.0

def sign(x,eps=1e-12):
    return 1 if x>eps else (-1 if x<-eps else 0)

def main(argv):
    if len(argv)!=4:
        raise SystemExit("usage: augment_features_exp006_path.py <bid.csv> <base48_features.csv> <out.csv>")
    bid=rows(argv[1]);base=rows(argv[2])
    if len(bid)!=len(base): raise SystemExit("ROW_COUNT_MISMATCH")
    if not bid:
        raise SystemExit("EMPTY_INPUT")

    ts=[];op=[];hi=[];lo=[];cl=[]
    for i,(b,f) in enumerate(zip(bid,base)):
        if b["timestamp"]!=f["timestamp"]:
            raise SystemExit(f"TIMESTAMP_MISMATCH:{i}")
        ts.append(int(b["timestamp"]))
        op.append(float(b["open"]));hi.append(float(b["high"]))
        lo.append(float(b["low"]));cl.append(float(b["close"]))

    one=[0.0]*len(cl)
    contiguous=[False]*len(cl)
    for i in range(1,len(cl)):
        contiguous[i]=(ts[i]-ts[i-1]==60000)
        if contiguous[i]: one[i]=cl[i]-cl[i-1]

    out=Path(argv[3]);out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(base[0].keys())+PATH_FEATURES+["feature_version_exp006"]
    with out.open("w",encoding="utf-8",newline="") as fo:
        wr=csv.DictWriter(fo,fieldnames=fields);wr.writeheader()
        for i,f in enumerate(base):
            vals=dict(f)
            vals["feature_version_exp006"]="EXP006_PATH84_V1"
            complete=(f.get("feature_complete")=="True" and i>=240 and
                      all(contiguous[k] for k in range(i-239,i+1)))
            if complete:
                for w in WINDOWS:
                    returns=one[i-w+1:i+1]
                    abs_sum=sum(abs(x) for x in returns)
                    vals[f"path_efficiency_{w}m"]=safe_div(abs(cl[i]-cl[i-w]),abs_sum)

                    nz=[sign(x) for x in returns if sign(x)!=0]
                    changes=sum(1 for a,b in zip(nz,nz[1:]) if a!=b)
                    vals[f"sign_change_rate_{w}m"]=safe_div(changes,max(0,len(nz)-1))

                    vals[f"jump_concentration_{w}m"]=safe_div(max((abs(x) for x in returns),default=0.0),abs_sum)

                    hs=hi[i-w+1:i+1];ls=lo[i-w+1:i+1]
                    maxh=max(hs);minl=min(ls)
                    last_hi=max(j for j,v in enumerate(hs) if v==maxh)
                    last_lo=max(j for j,v in enumerate(ls) if v==minl)
                    vals[f"time_since_high_{w}m"]=w-1-last_hi
                    vals[f"time_since_low_{w}m"]=w-1-last_lo

                    syn_open=op[i-w+1]
                    syn_range=maxh-minl
                    vals[f"synthetic_body_range_ratio_{w}m"]=safe_div(abs(cl[i]-syn_open),syn_range)
            else:
                vals["feature_complete"]="False"
                for k in PATH_FEATURES: vals[k]=""
            wr.writerow(vals)
    print(f"EXP006_PATH_FEATURES_PASS rows={len(base)} output={out} extras={len(PATH_FEATURES)}")

if __name__=="__main__":
    main(sys.argv)
