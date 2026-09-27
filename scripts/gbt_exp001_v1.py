#!/usr/bin/env python3
"""EXP-001 HistGradientBoosting V1.

Uses the frozen V2 feature set. Fits on every 5th eligible TRAIN row in
chronological order; evaluates all eligible TRAIN/VALIDATION/DEVELOPMENT_TEST
rows. FINAL_OOS is forbidden.
"""
import csv,json,math,sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss

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
            try:p=next(pr)
            except StopIteration:p=None
            try:f=next(fr)
            except StopIteration:f=None
            if p is None and f is None: break
            if p is None or f is None: raise SystemExit("ROW_COUNT_MISMATCH")
            if p["timestamp"]!=f["timestamp"]: raise SystemExit("TIMESTAMP_MISMATCH")
            yield p,f

def eligible(p,f):
    if p["partition"]=="FINAL_OOS": raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
    if p["partition"] not in ALLOWED:return False
    return p["partition_boundary_eligible"]=="True" and p["coverage_complete"]=="True" and f["feature_complete"]=="True"

def parse_x(f):
    vals=[]
    try:
        for k in FEATURES:
            v=float(f[k])
            if not math.isfinite(v):return None
            vals.append(v)
    except (KeyError,ValueError,TypeError):
        return None
    return vals

def load_train_thinned(pairs,direction):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];eligible_train_index=0
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"]!="TRAIN":continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            if eligible_train_index%5==0:
                xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
            eligible_train_index+=1
    if not xs: raise SystemExit("NO_TRAIN_ROWS")
    return np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8),eligible_train_index

def iter_eval_chunks(pairs,direction):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];parts=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f):continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            xs.append(x);ys.append(1 if lab=="SUCCESS" else 0);parts.append(p["partition"])
            if len(xs)>=CHUNK:
                yield np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8),np.asarray(parts)
                xs=[];ys=[];parts=[]
    if xs:
        yield np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8),np.asarray(parts)

def calibration(y,p):
    out=[]
    for i in range(10):
        lo=i/10;hi=(i+1)/10
        m=(p>=lo)&((p<hi) if i<9 else (p<=hi))
        n=int(m.sum())
        out.append({"lo":lo,"hi":hi,"n":n,
                    "mean_pred":float(p[m].mean()) if n else None,
                    "realized":float(y[m].mean()) if n else None})
    return out

def metrics(y,p):
    pc=np.clip(p,1e-12,1-1e-12)
    d={"n":int(len(y)),"positives":int(y.sum()),"base_rate":float(y.mean()),
       "roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,
       "pr_auc":float(average_precision_score(y,p)) if y.sum()>0 else None,
       "brier":float(np.mean((p-y)**2)),
       "log_loss":float(log_loss(y,pc,labels=[0,1])),
       "probability_quantiles":{str(q):float(np.quantile(p,q)) for q in (0.5,0.75,0.9,0.95,0.99)},
       "calibration_bins":calibration(y,p),"candidate_cutoffs":{}}
    for c in CUTS:
        m=p>=c;n=int(m.sum())
        d["candidate_cutoffs"][f"{c:.2f}"]={"n":n,"share":float(n/len(y)),
            "success_rate":float(y[m].mean()) if n else None}
    return d

def evaluate(pairs,direction,model):
    raw={p:{"y":[],"p":[]} for p in ("TRAIN","VALIDATION","DEVELOPMENT_TEST")}
    val_x=[];val_y=[];val_count=0
    for X,y,parts in iter_eval_chunks(pairs,direction):
        prob=model.predict_proba(X)[:,1]
        for part in raw:
            m=parts==part
            if m.any():
                raw[part]["y"].append(y[m]);raw[part]["p"].append(prob[m])
        if val_count<50000:
            m=np.where(parts=="VALIDATION")[0]
            take=m[:max(0,50000-val_count)]
            if len(take):
                val_x.append(X[take]);val_y.append(y[take]);val_count+=len(take)
    out={}
    for part,d in raw.items():
        y=np.concatenate(d["y"]);p=np.concatenate(d["p"])
        out[part]=metrics(y,p)
    Xv=np.concatenate(val_x);yv=np.concatenate(val_y)
    imp=permutation_importance(model,Xv,yv,scoring="roc_auc",n_repeats=3,random_state=1,n_jobs=1)
    order=np.argsort(imp.importances_mean)[::-1][:15]
    top=[{"feature":FEATURES[i],"importance_mean":float(imp.importances_mean[i]),
          "importance_std":float(imp.importances_std[i])} for i in order]
    return out,top,len(yv)

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: gbt_exp001_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    result={"status":"PASS","experiment":"EXP-001_GBT_V1","final_oos":"NOT_ACCESSED",
            "train_thinning":"every_5th_eligible_train_row_chronological","features":FEATURES,"directions":{}}
    for direction in ("BUY","SELL"):
        X,y,total=load_train_thinned(pairs,direction)
        model=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,
            max_leaf_nodes=15,max_depth=None,min_samples_leaf=200,l2_regularization=1.0,
            max_bins=255,early_stopping=False,random_state=1)
        model.fit(X,y)
        ev,top,nimp=evaluate(pairs,direction,model)
        result["directions"][direction]={
            "train_eligible_before_thinning":int(total),
            "train_rows_used":int(len(y)),
            "evaluation":ev,
            "permutation_importance_validation_sample_n":int(nimp),
            "top15_permutation_importance":top
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
