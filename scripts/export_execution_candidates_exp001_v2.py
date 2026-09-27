#!/usr/bin/env python3
"""Export EXP-001 V2 operational execution candidates without future-label conditioning."""

import csv,json,math,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

FEATURES=[
"ret_5m","ret_15m","ret_30m","ret_60m","ret_120m","ret_240m",
"rv_15m","rv_60m","rv_120m","rv_240m","tr_mean_60m",
"rv_short_long_ratio","compression_expansion_ratio","rv60_percentile_240m",
"recent_5dollar_range_frequency_240m","range_position_60m","range_position_240m",
"slope_15m","slope_60m","slope_240m","trend_persistence_15m",
"trend_persistence_60m","trend_persistence_240m",
"directional_agreement_m5_m15_h1_h4","body_range_ratio_1m",
"close_location_1m","wick_asymmetry_1m","impulse_15m","pullback_depth_15m",
"impulse_pullback_ratio_15m","return_acceleration_5v15",
"directional_consistency_5m","directional_consistency_15m",
"directional_consistency_30m","current_day_range_position",
"distance_round_5","distance_round_10","minutes_to_session_transition",
"europe_us_overlap","session_rv_60m"
]
SHARES=(0.10,0.05,0.025,0.01)

def iter_join(pp,fp):
    with Path(pp).open(encoding="utf-8",newline="") as pf, Path(fp).open(encoding="utf-8",newline="") as ff:
        pr=csv.DictReader(pf);fr=csv.DictReader(ff)
        while True:
            try:p=next(pr)
            except StopIteration:p=None
            try:f=next(fr)
            except StopIteration:f=None
            if p is None and f is None:break
            if p is None or f is None:raise SystemExit("ROW_COUNT_MISMATCH")
            if p["timestamp"]!=f["timestamp"]:raise SystemExit("TIMESTAMP_MISMATCH")
            yield p,f

def parse_x(f):
    out=[]
    try:
        for k in FEATURES:
            v=float(f[k])
            if not math.isfinite(v):return None
            out.append(v)
    except Exception:
        return None
    return out

def train_eligible(p,f):
    return (p["partition"]=="TRAIN" and p["partition_boundary_eligible"]=="True"
            and p["coverage_complete"]=="True" and f["feature_complete"]=="True")

def score_eligible(p,f,partition):
    return (p["partition"]==partition and p["partition_boundary_eligible"]=="True"
            and f["feature_complete"]=="True")

def train_model(pairs,direction):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];idx=0
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not train_eligible(p,f):continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            if idx%5==0:
                xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
            idx+=1
    m=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,
        max_leaf_nodes=15,max_depth=None,min_samples_leaf=200,l2_regularization=1.0,
        max_bins=255,early_stopping=False,random_state=1)
    m.fit(np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8))
    return m

def load_partition(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not score_eligible(p,f,partition):continue
            x=parse_x(f)
            if x is None:continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def utc_date(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date()

def main(argv):
    if len(argv)<6 or (len(argv)-4)%2:
        raise SystemExit("usage: export_execution_candidates_exp001_v2.py <candidates.csv> <cutoffs.json> <dates.txt> <partitioned.csv> <features.csv> [...]")
    cand=Path(argv[1]);cut=Path(argv[2]);dates=Path(argv[3]);pairs=list(zip(argv[4::2],argv[5::2]))

    bm=train_model(pairs,"BUY");sm=train_model(pairs,"SELL")
    vr,Xv=load_partition(pairs,"VALIDATION")
    dr,Xd=load_partition(pairs,"DEVELOPMENT_TEST")
    vb=bm.predict_proba(Xv)[:,1];vs=sm.predict_proba(Xv)[:,1]
    db=bm.predict_proba(Xd)[:,1];ds=sm.predict_proba(Xd)[:,1]

    cuts={}
    for s in SHARES:
        cuts[f"top_{s:g}"]={"buy":float(np.quantile(vb,1-s)),"sell":float(np.quantile(vs,1-s))}
    top10=cuts["top_0.1"]
    keep=(db>=top10["buy"]) | (ds>=top10["sell"])

    cand.parent.mkdir(parents=True,exist_ok=True)
    fields=["timestamp","decision_time_ms","reference_price","partition","buy_score","sell_score"]
    required=set()
    with cand.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for i,m in enumerate(keep):
            if not m:continue
            p=dr[i];decision=int(p["decision_time_ms"])
            w.writerow({
                "timestamp":p["timestamp"],"decision_time_ms":decision,
                "reference_price":p["reference_price"],"partition":p["partition"],
                "buy_score":f"{db[i]:.17g}","sell_score":f"{ds[i]:.17g}"
            })
            d=utc_date(decision);required.add(d.isoformat())
            expiry=datetime.fromtimestamp((decision+60*60000)/1000,tz=timezone.utc).date()
            required.add(expiry.isoformat())

    cut.parent.mkdir(parents=True,exist_ok=True)
    cut.write_text(json.dumps({
        "status":"PASS","final_oos":"NOT_ACCESSED",
        "validation_rows_scored":len(vr),"development_rows_scored":len(dr),
        "candidate_rows":int(keep.sum()),"cutoffs":cuts
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")
    dates.parent.mkdir(parents=True,exist_ok=True)
    dates.write_text("\n".join(sorted(required))+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","candidate_rows":int(keep.sum()),"required_tick_dates":len(required),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
