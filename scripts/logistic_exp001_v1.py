#!/usr/bin/env python3
"""EXP-001 logistic regression V1.

Memory-bounded chronological training/evaluation on TRAIN, VALIDATION and
DEVELOPMENT_TEST only. FINAL_OOS is forbidden.
"""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, log_loss
from sklearn.preprocessing import StandardScaler

ALLOWED={"TRAIN","VALIDATION","DEVELOPMENT_TEST"}
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
CUTS=(0.20,0.30,0.40,0.50,0.60)
CHUNK=20000

def iter_join(partitioned,features):
    with Path(partitioned).open(encoding="utf-8",newline="") as pf, Path(features).open(encoding="utf-8",newline="") as ff:
        pr=csv.DictReader(pf); fr=csv.DictReader(ff)
        while True:
            try: p=next(pr)
            except StopIteration: p=None
            try: f=next(fr)
            except StopIteration: f=None
            if p is None and f is None: break
            if p is None or f is None: raise SystemExit("ROW_COUNT_MISMATCH")
            if p["timestamp"]!=f["timestamp"]: raise SystemExit("TIMESTAMP_MISMATCH")
            yield p,f

def eligible(p,f):
    if p["partition"]=="FINAL_OOS": raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
    if p["partition"] not in ALLOWED: return False
    return p["partition_boundary_eligible"]=="True" and p["coverage_complete"]=="True" and f["feature_complete"]=="True"

def parse_x(f):
    vals=[]
    try:
        for k in FEATURES:
            v=float(f[k])
            if not math.isfinite(v): return None
            vals.append(v)
    except (KeyError,ValueError,TypeError):
        return None
    return vals

def iter_chunks(pairs,direction,partitions):
    label_col="buy_label" if direction=="BUY" else "sell_label"
    xs=[]; ys=[]; ps=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"] not in partitions: continue
            lab=p[label_col]
            if lab=="AMBIGUOUS": continue
            x=parse_x(f)
            if x is None: continue
            xs.append(x); ys.append(1 if lab=="SUCCESS" else 0); ps.append(p["partition"])
            if len(xs)>=CHUNK:
                yield np.asarray(xs,dtype=np.float64),np.asarray(ys,dtype=np.int8),ps
                xs=[];ys=[];ps=[]
    if xs:
        yield np.asarray(xs,dtype=np.float64),np.asarray(ys,dtype=np.int8),ps

def fit_direction(pairs,direction):
    scaler=StandardScaler()
    n=0
    for X,y,_ in iter_chunks(pairs,direction,{"TRAIN"}):
        scaler.partial_fit(X); n+=len(y)
    if n==0: raise SystemExit(f"NO_TRAIN_ROWS_{direction}")

    clf=SGDClassifier(loss="log_loss",penalty="l2",alpha=1e-4,fit_intercept=True,
                      learning_rate="constant",eta0=0.03,shuffle=False,random_state=1,
                      average=False)
    first=True
    for epoch in range(1,5):
        clf.set_params(eta0=0.03/math.sqrt(epoch))
        for X,y,_ in iter_chunks(pairs,direction,{"TRAIN"}):
            Xs=scaler.transform(X)
            if first:
                clf.partial_fit(Xs,y,classes=np.array([0,1],dtype=np.int8)); first=False
            else:
                clf.partial_fit(Xs,y)
    return scaler,clf

def calibration(y,p):
    out=[]
    edges=np.linspace(0,1,11)
    for i in range(10):
        lo,hi=float(edges[i]),float(edges[i+1])
        mask=(p>=lo)&((p<hi) if i<9 else (p<=hi))
        n=int(mask.sum())
        out.append({"lo":lo,"hi":hi,"n":n,
                    "mean_pred":float(p[mask].mean()) if n else None,
                    "realized":float(y[mask].mean()) if n else None})
    return out

def evaluate_direction(pairs,direction,scaler,clf):
    store={p:{"y":[],"prob":[]} for p in ("TRAIN","VALIDATION","DEVELOPMENT_TEST")}
    for X,y,parts in iter_chunks(pairs,direction,set(store)):
        prob=clf.predict_proba(scaler.transform(X))[:,1]
        parts=np.asarray(parts)
        for part in store:
            m=parts==part
            if m.any():
                store[part]["y"].append(y[m]); store[part]["prob"].append(prob[m])

    report={}
    for part,d in store.items():
        if not d["y"]: continue
        y=np.concatenate(d["y"]); p=np.concatenate(d["prob"])
        eps=1e-12; pc=np.clip(p,eps,1-eps)
        row={
          "n":int(len(y)),"positives":int(y.sum()),"base_rate":float(y.mean()),
          "roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,
          "pr_auc":float(average_precision_score(y,p)) if y.sum()>0 else None,
          "brier":float(np.mean((p-y)**2)),
          "log_loss":float(log_loss(y,pc,labels=[0,1])),
          "probability_quantiles":{str(q):float(np.quantile(p,q)) for q in (0.5,0.75,0.9,0.95,0.99)},
          "calibration_bins":calibration(y,p),
          "candidate_cutoffs":{}
        }
        for c in CUTS:
            m=p>=c; n=int(m.sum())
            row["candidate_cutoffs"][f"{c:.2f}"]={
                "n":n,"share":float(n/len(y)),
                "success_rate":float(y[m].mean()) if n else None
            }
        report[part]=row
    return report

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: logistic_exp001_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]); pairs=list(zip(argv[2::2],argv[3::2]))
    result={"status":"PASS","experiment":"EXP-001_LOGISTIC_V1","final_oos":"NOT_ACCESSED",
            "features":FEATURES,"directions":{}}
    for direction in ("BUY","SELL"):
        scaler,clf=fit_direction(pairs,direction)
        result["directions"][direction]={
          "coef":[float(x) for x in clf.coef_[0]],
          "intercept":float(clf.intercept_[0]),
          "scaler_mean":[float(x) for x in scaler.mean_],
          "scaler_scale":[float(x) for x in scaler.scale_],
          "evaluation":evaluate_direction(pairs,direction,scaler,clf)
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__": main(sys.argv)
