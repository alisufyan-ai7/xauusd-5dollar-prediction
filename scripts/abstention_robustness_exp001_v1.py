#!/usr/bin/env python3
"""EXP-001 fixed-policy abstention robustness V1."""
import csv,json,math,sys
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

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
SHARES=(0.10,0.05,0.025,0.01)

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

def load_train_thinned_and_rv(pairs,direction):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];rvs=[];idx=0
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"]!="TRAIN":continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            rvs.append(float(f["rv_60m"]))
            if idx%5==0:
                xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
            idx+=1
    return np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8),np.asarray(rvs,dtype=np.float64)

def load_partition(pairs,direction,partition):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];ts=[];sessions=[];rvs=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"]!=partition:continue
            lab=p[col]
            if lab=="AMBIGUOUS":continue
            x=parse_x(f)
            if x is None:continue
            xs.append(x);ys.append(1 if lab=="SUCCESS" else 0)
            ts.append(int(p["timestamp"]));sessions.append(f["session_utc"]);rvs.append(float(f["rv_60m"]))
    return (np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8),
            np.asarray(ts,dtype=np.int64),np.asarray(sessions,dtype=object),np.asarray(rvs,dtype=np.float64))

def dt_parts(ts_ms):
    d=datetime.fromtimestamp(int(ts_ms)/1000,timezone.utc)
    return d.year,((d.month-1)//3)+1,d.date().isoformat()

def basic_metrics(y,sel):
    n_all=len(y); n=int(sel.sum())
    base=float(y.mean()) if n_all else None
    sr=float(y[sel].mean()) if n else None
    return {"selected_n":n,"opportunity_share":float(n/n_all) if n_all else None,
            "selected_success_rate":sr,"unconditional_success_rate":base,
            "lift":float(sr/base) if n and base and base>0 else None}

def stratified(y,sel,groups,ordered):
    out={}
    for g in ordered:
        m=groups==g
        out[str(g)]=basic_metrics(y[m],sel[m]) if m.any() else {
            "selected_n":0,"opportunity_share":None,"selected_success_rate":None,
            "unconditional_success_rate":None,"lift":None}
    return out

def daily_bootstrap(y,sel,days,reps=1000,seed=1):
    uniq=np.unique(days)
    su=[];sn=[];uu=[];un=[]
    for d in uniq:
        m=days==d
        s=m&sel
        su.append(int(y[s].sum()));sn.append(int(s.sum()))
        uu.append(int(y[m].sum()));un.append(int(m.sum()))
    su=np.asarray(su);sn=np.asarray(sn);uu=np.asarray(uu);un=np.asarray(un)
    rng=np.random.default_rng(seed)
    rates=[];lifts=[]
    k=len(uniq)
    for _ in range(reps):
        idx=rng.integers(0,k,size=k)
        sN=sn[idx].sum(); uN=un[idx].sum()
        if sN==0 or uN==0: continue
        sr=su[idx].sum()/sN; ur=uu[idx].sum()/uN
        rates.append(sr)
        if ur>0:lifts.append(sr/ur)
    q=lambda a:[float(np.quantile(a,0.025)),float(np.quantile(a,0.975))] if len(a) else [None,None]
    return {"block":"UTC_day","replicates":reps,"success_rate_95pct":q(np.asarray(rates)),
            "lift_95pct":q(np.asarray(lifts))}

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: abstention_robustness_exp001_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    result={"status":"PASS","experiment":"EXP-001_ABSTENTION_ROBUSTNESS_V1",
            "final_oos":"NOT_ACCESSED","directions":{}}
    for direction in ("BUY","SELL"):
        Xtr,ytr,train_rv=load_train_thinned_and_rv(pairs,direction)
        q33,q67=np.quantile(train_rv,[1/3,2/3])
        model=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,
            max_leaf_nodes=15,max_depth=None,min_samples_leaf=200,l2_regularization=1.0,
            max_bins=255,early_stopping=False,random_state=1)
        model.fit(Xtr,ytr)
        Xv,yv,tv,sv,rvv=load_partition(pairs,direction,"VALIDATION")
        Xd,yd,td,sd,rvd=load_partition(pairs,direction,"DEVELOPMENT_TEST")
        pv=model.predict_proba(Xv)[:,1]
        pd=model.predict_proba(Xd)[:,1]
        years=np.empty(len(td),dtype=np.int16);quarters=np.empty(len(td),dtype=object);days=np.empty(len(td),dtype=object)
        for i,t in enumerate(td):
            y,q,day=dt_parts(t);years[i]=y;quarters[i]=f"{y}-Q{q}";days[i]=day
        vol=np.where(rvd<=q33,"LOW",np.where(rvd<=q67,"MID","HIGH"))
        policies={}
        for share in SHARES:
            cut=float(np.quantile(pv,1-share))
            sel=pd>=cut
            time_year=stratified(yd,sel,years,[2023,2024])
            qlabels=[f"{y}-Q{q}" for y in (2023,2024) for q in range(1,5)]
            time_quarter=stratified(yd,sel,quarters,qlabels)
            sessions=stratified(yd,sel,sd,["ASIA","EUROPE","US","LATE"])
            vols=stratified(yd,sel,vol,["LOW","MID","HIGH"])
            boot=daily_bootstrap(yd,sel,days)
            def above(d):
                vals=[v for v in d.values() if v["selected_success_rate"] is not None and v["unconditional_success_rate"] is not None]
                return all(v["selected_success_rate"]>v["unconditional_success_rate"] for v in vals) if vals else False
            qvals=[v for v in time_quarter.values() if v["selected_success_rate"] is not None]
            qabove=sum(v["selected_success_rate"]>v["unconditional_success_rate"] for v in qvals)
            policies[f"top_{share:g}"]={
                "validation_raw_score_cutoff":cut,
                "development_overall":basic_metrics(yd,sel),
                "by_year":time_year,"by_quarter":time_quarter,
                "by_session":sessions,"by_volatility_regime":vols,
                "bootstrap":boot,
                "stability_flags":{
                    "all_years_above_unconditional":above(time_year),
                    "at_least_6_of_8_quarters_above_unconditional":qabove>=6,
                    "all_sessions_above_unconditional":above(sessions),
                    "all_volatility_regimes_above_unconditional":above(vols),
                    "bootstrap_lift_ci_lower_gt_1":boot["lift_95pct"][0] is not None and boot["lift_95pct"][0]>1
                }
            }
        result["directions"][direction]={
            "train_rows_used":int(len(ytr)),
            "train_rv60_tertiles":{"q33":float(q33),"q67":float(q67)},
            "policies":policies
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
