#!/usr/bin/env python3
"""EXP-006 BASE48 vs PATH84 representation A/B test."""

import csv,json,math,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor

import execution_economics_exp002_v1 as exp2
import exp005_downside_first_direct_v1 as e5
from augment_features_exp006_path import PATH_FEATURES

REPRESENTATIONS={
    "REP_A_BASE48":exp2.FEATURES,
    "REP_B_PATH84":exp2.FEATURES+PATH_FEATURES,
}

def xrow(f,features):
    vals=[]
    try:
        for k in features:
            v=float(f[k])
            if not math.isfinite(v): return None
            vals.append(v)
    except Exception:
        return None
    return vals

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

def fit_models(pairs,direction,features):
    xs=[];yr=[];yc=[];idx=0
    lab,_,_=e5.fields(direction)
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS": raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True": continue
            if p[lab]=="AMBIGUOUS": continue
            x=xrow(f,features)
            if x is None: continue
            if idx%5==0:
                xs.append(x);yr.append(e5.realized_gross(p,direction));yc.append(e5.early_failure(p,direction))
            idx+=1
    X=np.asarray(xs,dtype=np.float32)
    reg=HistGradientBoostingRegressor(loss="squared_error",learning_rate=.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    reg.fit(X,np.asarray(yr,dtype=np.float32))
    clf=HistGradientBoostingClassifier(loss="log_loss",learning_rate=.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    clf.fit(X,np.asarray(yc,dtype=np.int8))
    return reg,clf,len(yr),int(np.sum(yc))

def load_partition(pairs,partition,features):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS": raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True": continue
            x=xrow(f,features)
            if x is None: continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def bootstrap_seed6(trades,reps=2000,seed=6):
    by=defaultdict(list)
    for x in trades:by[e5.date_of(x["entry_time_ms"])].append(x["gross"]-.10)
    days=sorted(by)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);vals=[];n=len(days)
    for _ in range(reps):
        sample=[]
        for j in rng.integers(0,n,size=n):sample.extend(by[days[j]])
        vals.append(float(np.mean(sample)))
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: exp006_causal_path_state_v1.py <out.json> <partitioned.csv> <path84_features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))

    # Freeze EXP-006 bootstrap seed while reusing EXP-005 economics.
    e5.bootstrap=bootstrap_seed6

    result={"status":"PASS","experiment":"EXP-006_CAUSAL_PATH_STATE_V1","final_oos":"NOT_ACCESSED","representations":{}}
    passing=[]

    for rep,features in REPRESENTATIONS.items():
        vr,Xv=load_partition(pairs,"VALIDATION",features)
        dr,Xd=load_partition(pairs,"DEVELOPMENT_TEST",features)
        repout={"feature_count":len(features),"directions":{}}
        scores={};cuts={}
        for d in ("BUY","SELL"):
            reg,clf,n,ne=fit_models(pairs,d,features)
            vg,vn,vef=e5.predict(reg,clf,Xv)
            dg,dn,defr=e5.predict(reg,clf,Xd)
            c={"Q50":float(np.quantile(vef,.50)),"Q25":float(np.quantile(vef,.25)),"Q10":float(np.quantile(vef,.10))}
            cuts[d]=c
            mask23=np.asarray([e5.year_of(int(p["decision_time_ms"]))==2023 for p in dr])
            mask24=np.asarray([e5.year_of(int(p["decision_time_ms"]))==2024 for p in dr])
            repout["directions"][d]={
              "train_rows":n,"train_early_failures":ne,"validation_risk_cutoffs":c,
              "VALIDATION":e5.predictive_metrics(vr,d,vg,vn,vef),
              "DEVELOPMENT_TEST":e5.predictive_metrics(dr,d,dg,dn,defr),
              "DEVELOPMENT_TEST_2023":e5.predictive_metrics([p for i,p in enumerate(dr) if mask23[i]],d,dg[mask23],dn[mask23],defr[mask23]),
              "DEVELOPMENT_TEST_2024":e5.predictive_metrics([p for i,p in enumerate(dr) if mask24[i]],d,dg[mask24],dn[mask24],defr[mask24]),
            }
            scores[d]=(dn,defr)
        repout["economics"]=e5.eval_economics(dr,scores["BUY"][0],scores["SELL"][0],scores["BUY"][1],scores["SELL"][1],cuts["BUY"],cuts["SELL"])
        result["representations"][rep]=repout

        if rep=="REP_B_PATH84":
            for arm,a in repout["economics"].items():
                for thn,modes in a.items():
                    for mode,v in modes.items():
                        if v["advancement"]["passed"]:
                            passing.append({"representation":rep,"arm":arm,"threshold":thn,"mode":mode})

    result["passing_policies"]=passing

    # compact representation deltas
    delta={}
    for d in ("BUY","SELL"):
        a=result["representations"]["REP_A_BASE48"]["directions"][d]["DEVELOPMENT_TEST"]
        b=result["representations"]["REP_B_PATH84"]["directions"][d]["DEVELOPMENT_TEST"]
        delta[d]={
          "direct_pearson_delta":b["regression"]["pearson"]-a["regression"]["pearson"],
          "early_failure_roc_auc_delta":b["early_failure"]["roc_auc"]-a["early_failure"]["roc_auc"],
          "early_failure_pr_auc_delta":b["early_failure"]["pr_auc"]-a["early_failure"]["pr_auc"],
        }
    result["representation_delta"]=delta

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
