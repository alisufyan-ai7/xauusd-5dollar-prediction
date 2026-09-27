#!/usr/bin/env python3
"""EXP-001 calibration and abstention V1."""
import csv,json,math,sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
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
TOP_SHARES=(0.50,0.30,0.20,0.10,0.05,0.025,0.01)
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
    xs=[];ys=[];idx=0
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"]!="TRAIN":continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            if idx%5==0:
                xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
            idx+=1
    return np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8)

def load_partition(pairs,direction,partition):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"]!=partition:continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
    return np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8)

def logit(p):
    p=np.clip(p,1e-6,1-1e-6)
    return np.log(p/(1-p)).reshape(-1,1)

def calibration_bins(y,p):
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
    return {
      "n":int(len(y)),"positives":int(y.sum()),"base_rate":float(y.mean()),
      "roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,
      "pr_auc":float(average_precision_score(y,p)) if y.sum()>0 else None,
      "brier":float(np.mean((p-y)**2)),
      "log_loss":float(log_loss(y,pc,labels=[0,1])),
      "calibration_bins":calibration_bins(y,p)
    }

def band_report(y,raw,cal,cut):
    m=raw>=cut;n=int(m.sum())
    return {"n":n,"share":float(n/len(y)),
            "success_rate":float(y[m].mean()) if n else None,
            "mean_calibrated_probability":float(cal[m].mean()) if n else None}

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: calibration_exp001_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    result={"status":"PASS","experiment":"EXP-001_CALIBRATION_ABSTENTION_V1",
            "final_oos":"NOT_ACCESSED","features":FEATURES,"directions":{}}
    for direction in ("BUY","SELL"):
        Xtr,ytr=load_train_thinned(pairs,direction)
        gbt=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,
            max_leaf_nodes=15,max_depth=None,min_samples_leaf=200,l2_regularization=1.0,
            max_bins=255,early_stopping=False,random_state=1)
        gbt.fit(Xtr,ytr)
        Xv,yv=load_partition(pairs,direction,"VALIDATION")
        Xd,yd=load_partition(pairs,direction,"DEVELOPMENT_TEST")
        rv=gbt.predict_proba(Xv)[:,1]
        rd=gbt.predict_proba(Xd)[:,1]
        cal=LogisticRegression(C=1e6,solver="lbfgs",max_iter=1000,random_state=1)
        cal.fit(logit(rv),yv)
        cv=cal.predict_proba(logit(rv))[:,1]
        cd=cal.predict_proba(logit(rd))[:,1]
        bands={}
        monotonic_v=[];monotonic_d=[]
        for share in TOP_SHARES:
            cut=float(np.quantile(rv,1-share))
            key=f"top_{share:g}"
            vr=band_report(yv,rv,cv,cut); dr=band_report(yd,rd,cd,cut)
            bands[key]={"validation_raw_score_cutoff":cut,"VALIDATION":vr,"DEVELOPMENT_TEST":dr,
                        "success_rate_abs_difference":abs(vr["success_rate"]-dr["success_rate"]) if vr["success_rate"] is not None and dr["success_rate"] is not None else None}
            monotonic_v.append(vr["success_rate"]);monotonic_d.append(dr["success_rate"])
        def nondecreasing(vals):
            xs=[x for x in vals if x is not None]
            return all(xs[i+1]>=xs[i] for i in range(len(xs)-1))
        result["directions"][direction]={
          "train_rows_used":int(len(ytr)),
          "platt_coefficient":float(cal.coef_[0][0]),
          "platt_intercept":float(cal.intercept_[0]),
          "VALIDATION":{"raw":metrics(yv,rv),"calibrated":metrics(yv,cv)},
          "DEVELOPMENT_TEST":{"raw":metrics(yd,rd),"calibrated":metrics(yd,cd)},
          "abstention_bands":bands,
          "monotonic_success_with_selectivity":{
             "VALIDATION":nondecreasing(monotonic_v),
             "DEVELOPMENT_TEST":nondecreasing(monotonic_d)
          }
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
