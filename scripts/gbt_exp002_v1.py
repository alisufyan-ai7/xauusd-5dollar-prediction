#!/usr/bin/env python3
"""EXP-002 fixed GBT V1 on executable-side labels."""

import csv,json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss

BASE_FEATURES=[
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
SPREAD_FEATURES=[
"spread_close_1m","spread_mean_5m","spread_mean_15m","spread_mean_60m",
"spread_max_15m","spread_max_60m","spread_ratio_1m_to_60m","spread_percentile_240m"
]
FEATURES=BASE_FEATURES+SPREAD_FEATURES
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

def xrow(f):
    vals=[]
    try:
        for k in FEATURES:
            v=float(f[k])
            if not math.isfinite(v):return None
            vals.append(v)
    except Exception:return None
    return vals

def fit_rows(pairs,direction):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];idx=0
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True":continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=xrow(f)
            if x is None:continue
            if idx%5==0:
                xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
            idx+=1
    return np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8)

def score_rows(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True":continue
            x=xrow(f)
            if x is None:continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def metrics(rows,prob,direction,cutoffs=None):
    col="buy_label" if direction=="BUY" else "sell_label"
    usable=np.asarray([p["coverage_complete"]=="True" and p[col]!="AMBIGUOUS" for p in rows])
    y=np.asarray([1 if p[col]=="SUCCESS" else 0 for p in rows],dtype=np.int8)
    yu=y[usable];pu=prob[usable]
    labs=Counter(p[col] for p in rows if p["coverage_complete"]=="True")
    out={
      "scored_rows":len(rows),"evaluation_rows":int(usable.sum()),
      "label_counts_complete":dict(labs),
      "base_success_rate":float(yu.mean()) if len(yu) else None,
      "roc_auc":float(roc_auc_score(yu,pu)) if len(np.unique(yu))==2 else None,
      "pr_auc":float(average_precision_score(yu,pu)) if yu.sum()>0 else None,
      "brier":float(brier_score_loss(yu,pu)) if len(yu) else None,
      "log_loss":float(log_loss(yu,np.clip(pu,1e-12,1-1e-12),labels=[0,1])) if len(yu) else None,
      "probability_quantiles":{str(q):float(np.quantile(prob,q)) for q in (0.5,0.75,0.9,0.95,0.975,0.99)}
    }
    if cutoffs is not None:
        bands={}
        for key,cut in cutoffs.items():
            sel=(prob>=cut)&usable;n=int(sel.sum())
            bands[key]={"n":n,"share_of_scored":float((prob>=cut).mean()),
                        "success_rate":float(y[sel].mean()) if n else None}
        out["fixed_validation_bands"]=bands
    return out

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: gbt_exp002_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    result={"status":"PASS","experiment":"EXP-002_GBT_V1","final_oos":"NOT_ACCESSED","features":FEATURES,"directions":{}}
    for direction in ("BUY","SELL"):
        X,y=fit_rows(pairs,direction)
        model=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,
            max_leaf_nodes=15,max_depth=None,min_samples_leaf=200,l2_regularization=1.0,
            max_bins=255,early_stopping=False,random_state=1)
        model.fit(X,y)
        vr,Xv=score_rows(pairs,"VALIDATION")
        dr,Xd=score_rows(pairs,"DEVELOPMENT_TEST")
        pv=model.predict_proba(Xv)[:,1];pd=model.predict_proba(Xd)[:,1]
        cuts={f"top_{s:g}":float(np.quantile(pv,1-s)) for s in SHARES}
        result["directions"][direction]={
            "train_rows_used":int(len(y)),
            "validation_cutoffs":cuts,
            "VALIDATION":metrics(vr,pv,direction,cuts),
            "DEVELOPMENT_TEST":metrics(dr,pd,direction,cuts)
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
