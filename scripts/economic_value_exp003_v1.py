#!/usr/bin/env python3
"""EXP-003 economic-value model V1.

Frozen before empirical results. Reuses EXP-002 features and executable labels.
2025 FINAL_OOS access is forbidden.
"""

import csv,json,math,sys
from pathlib import Path
from collections import Counter
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import log_loss, mean_absolute_error, mean_squared_error

import execution_economics_exp002_v1 as exp2

CLASSES=("SUCCESS","FAILURE","UNRESOLVED")
CLASS_TO_INT={k:i for i,k in enumerate(CLASSES)}
THRESHOLDS={"T0":0.00,"T25":0.25,"T50":0.50,"T75":0.75}
F10=0.10

def direction_fields(direction):
    if direction=="BUY":
        return "buy_label","buy_expiry_pnl"
    return "sell_label","sell_expiry_pnl"

def fit_direction(pairs,direction):
    label_col,pnl_col=direction_fields(direction)
    xc=[];yc=[];xr=[];yr=[]
    idx=0
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":
                raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True":
                continue
            lab=p[label_col]
            if lab=="AMBIGUOUS":
                continue
            x=exp2.xrow(f)
            if x is None:
                continue
            if idx%5==0:
                xc.append(x);yc.append(CLASS_TO_INT[lab])
            idx+=1
            if lab=="UNRESOLVED":
                xr.append(x);yr.append(float(p[pnl_col]))

    clf=HistGradientBoostingClassifier(
        loss="log_loss",learning_rate=0.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,
        early_stopping=False,random_state=1)
    clf.fit(np.asarray(xc,dtype=np.float32),np.asarray(yc,dtype=np.int8))

    reg=HistGradientBoostingRegressor(
        loss="squared_error",learning_rate=0.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,
        early_stopping=False,random_state=1)
    reg.fit(np.asarray(xr,dtype=np.float32),np.asarray(yr,dtype=np.float32))
    return clf,reg,len(yc),len(yr)

def load_partition(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":
                raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True":
                continue
            x=exp2.xrow(f)
            if x is None:
                continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def realized_gross(p,direction):
    label_col,pnl_col=direction_fields(direction)
    if p["coverage_complete"]!="True":
        return None
    lab=p[label_col]
    if lab=="SUCCESS": return 5.0
    if lab in ("FAILURE","AMBIGUOUS"): return -3.0
    if lab=="UNRESOLVED": return float(p[pnl_col])
    return None

def brier_multiclass(y,probs):
    out={}
    for i,name in enumerate(CLASSES):
        target=(y==i).astype(float)
        out[name]=float(np.mean((probs[:,i]-target)**2))
    return out

def decile_report(values,rows,direction):
    out={}
    qs=[float(np.quantile(values,q)) for q in np.linspace(0,1,11)]
    label_col,_=direction_fields(direction)
    for j in range(10):
        lo,hi=qs[j],qs[j+1]
        if j==0: mask=(values>=lo)&(values<=hi)
        else: mask=(values>lo)&(values<=hi)
        idx=np.where(mask)[0]
        gs=[];labs=[]
        for i in idx:
            g=realized_gross(rows[i],direction)
            if g is None: continue
            gs.append(g);labs.append(rows[i][label_col])
        c=Counter(labs);n=len(gs)
        out[f"D{j+1}"]={
            "lo":lo,"hi":hi,"n":n,
            "mean_gross":float(np.mean(gs)) if gs else None,
            "mean_net_f10":float(np.mean(np.asarray(gs)-F10)) if gs else None,
            "label_shares":{k:(c[k]/n if n else None) for k in CLASSES+("AMBIGUOUS",)}
        }
    return out

def evaluate(clf,reg,rows,X,direction):
    label_col,pnl_col=direction_fields(direction)
    probs=clf.predict_proba(X)
    # sklearn class ordering is numeric 0,1,2 because fit labels are ints.
    pred_u=np.clip(reg.predict(X),-3.0,5.0)
    ev_gross=5*probs[:,0]-3*probs[:,1]+probs[:,2]*pred_u
    ev_f10=ev_gross-F10

    eval_idx=[]
    y=[]
    unresolved_idx=[]
    unresolved_y=[]
    for i,p in enumerate(rows):
        if p["coverage_complete"]!="True": continue
        lab=p[label_col]
        if lab=="AMBIGUOUS": continue
        eval_idx.append(i);y.append(CLASS_TO_INT[lab])
        if lab=="UNRESOLVED":
            unresolved_idx.append(i);unresolved_y.append(float(p[pnl_col]))
    y=np.asarray(y,dtype=np.int8)
    pe=probs[np.asarray(eval_idx,dtype=int)]

    unresolved_metrics={}
    if unresolved_idx:
        yp=np.asarray([pred_u[i] for i in unresolved_idx],float)
        yt=np.asarray(unresolved_y,float)
        unresolved_metrics={
            "n":len(yt),
            "mae":float(mean_absolute_error(yt,yp)),
            "rmse":float(mean_squared_error(yt,yp)**0.5),
            "mean_pred":float(np.mean(yp)),
            "mean_realized":float(np.mean(yt))
        }

    return {
        "scored_rows":len(rows),
        "evaluation_rows":len(eval_idx),
        "multiclass_log_loss":float(log_loss(y,pe,labels=[0,1,2])) if len(y) else None,
        "brier_by_class":brier_multiclass(y,pe) if len(y) else {},
        "unresolved_regression":unresolved_metrics,
        "ev_f10_quantiles":{str(q):float(np.quantile(ev_f10,q)) for q in (0.1,0.25,0.5,0.75,0.9,0.95,0.975,0.99)},
        "ev_f10_deciles":decile_report(ev_f10,rows,direction),
        "threshold_counts":{k:int(np.sum(ev_f10>=v)) if v>0 else int(np.sum(ev_f10>0)) for k,v in THRESHOLDS.items()}
    }

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: economic_value_exp003_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    result={
        "status":"PASS",
        "experiment":"EXP-003_ECONOMIC_VALUE_V1",
        "final_oos":"NOT_ACCESSED",
        "thresholds":THRESHOLDS,
        "directions":{}
    }
    for direction in ("BUY","SELL"):
        clf,reg,nc,nr=fit_direction(pairs,direction)
        vr,Xv=load_partition(pairs,"VALIDATION")
        dr,Xd=load_partition(pairs,"DEVELOPMENT_TEST")
        result["directions"][direction]={
            "train_classifier_rows":nc,
            "train_unresolved_regression_rows":nr,
            "VALIDATION":evaluate(clf,reg,vr,Xv,direction),
            "DEVELOPMENT_TEST":evaluate(clf,reg,dr,Xd,direction)
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
