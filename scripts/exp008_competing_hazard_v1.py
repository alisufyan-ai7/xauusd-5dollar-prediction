#!/usr/bin/env python3
"""EXP-008 competing-hazard target-before-adverse V1."""

import json,sys,math
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

import execution_economics_exp002_v1 as exp2
import exp005_downside_first_direct_v1 as e5

CLASSES=("S_00_05","S_06_15","S_16_30","S_31_60","F_00_05","F_06_15","F_16_30","F_31_60","U_60")
CLASS_TO_INT={k:i for i,k in enumerate(CLASSES)}
ARMS=("A_HAZARD_EV","B_HAZARD_EV_EF_Q50","C_HAZARD_EV_EF_Q25","D_HAZARD_EV_EF_Q10")
THRESHOLDS={"T0":0.0,"T25":0.25,"T50":0.50,"T75":0.75}
FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
ONE=60000

def year_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

def direction_fields(direction):
    if direction=="BUY":
        return "buy_label","buy_expiry_pnl","buy_terminal_bar_timestamp_ms"
    return "sell_label","sell_expiry_pnl","sell_terminal_bar_timestamp_ms"

def xrow(f):
    vals=[]
    try:
        for k in exp2.FEATURES:
            v=float(f[k])
            if not math.isfinite(v):return None
            vals.append(v)
    except Exception:
        return None
    return vals

def hazard_class(p,direction):
    lab,_,term=direction_fields(direction)
    outcome=p[lab]
    if outcome=="UNRESOLVED":return "U_60"
    if outcome=="AMBIGUOUS":return None
    if outcome not in ("SUCCESS","FAILURE"):return None
    entry=int(p["decision_time_ms"])
    exit_ms=int(p[term])+ONE
    mins=int(round((exit_ms-entry)/ONE))
    if mins<1 or mins>60:
        raise SystemExit(f"INVALID_TERMINAL_MINUTES:{direction}:{outcome}:{mins}:{entry}")
    if mins<=5:sfx="00_05"
    elif mins<=15:sfx="06_15"
    elif mins<=30:sfx="16_30"
    else:sfx="31_60"
    return ("S_" if outcome=="SUCCESS" else "F_")+sfx

def realized_gross(p,direction):
    return e5.realized_gross(p,direction)

def load_train(pairs):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True":
                continue
            x=xrow(f)
            if x is None:continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def load_partition(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True":
                continue
            x=xrow(f)
            if x is None:continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def fit_base(rows,X,direction,year_lt=None):
    idx=[];yy=[]
    for i,p in enumerate(rows):
        if year_lt is not None and year_of(int(p["decision_time_ms"]))>=year_lt:continue
        c=hazard_class(p,direction)
        if c is None:continue
        idx.append(i);yy.append(CLASS_TO_INT[c])
    thin=idx[::5]
    y=np.asarray([CLASS_TO_INT[hazard_class(rows[i],direction)] for i in thin],dtype=np.int8)
    if set(y.tolist())!=set(range(9)):
        raise SystemExit(f"MISSING_HAZARD_CLASS:{direction}:{year_lt}:{sorted(set(y.tolist()))}")
    m=HistGradientBoostingClassifier(
      loss="log_loss",learning_rate=.05,max_iter=200,max_leaf_nodes=15,max_depth=None,
      min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    m.fit(X[np.asarray(thin,dtype=int)],y)
    return m

def fit_calibrator(rows,X,direction):
    zz=[];yy=[]
    for pred_year in (2017,2018,2019,2020,2021):
        m=fit_base(rows,X,direction,year_lt=pred_year)
        idx=[i for i,p in enumerate(rows)
             if year_of(int(p["decision_time_ms"]))==pred_year and hazard_class(p,direction) is not None]
        probs=m.predict_proba(X[np.asarray(idx,dtype=int)])
        if probs.shape[1]!=9:raise SystemExit("BASE_PROBABILITY_DIMENSION_MISMATCH")
        zz.append(np.log(np.clip(probs,1e-6,1-1e-6)))
        yy.extend(CLASS_TO_INT[hazard_class(rows[i],direction)] for i in idx)
    Z=np.vstack(zz);y=np.asarray(yy,dtype=np.int8)
    if set(y.tolist())!=set(range(9)):raise SystemExit("CALIBRATOR_CLASS_MISSING")
    cal=LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,class_weight=None,random_state=1)
    cal.fit(Z,y)
    return cal,int(len(y))

def fit_unresolved(rows,X,direction):
    idx=[];targets=[]
    _,pnl,_=direction_fields(direction)
    for i,p in enumerate(rows):
        if hazard_class(p,direction)=="U_60":
            idx.append(i);targets.append(float(p[pnl]))
    idx=idx[::5];targets=np.asarray(targets[::5],dtype=np.float32)
    m=HistGradientBoostingRegressor(
      loss="squared_error",learning_rate=.05,max_iter=200,max_leaf_nodes=15,max_depth=None,
      min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    m.fit(X[np.asarray(idx,dtype=int)],targets)
    return m,int(len(idx))

def calibrated_probs(base,cal,X):
    p=base.predict_proba(X)
    return cal.predict_proba(np.log(np.clip(p,1e-6,1-1e-6)))

def score(base,cal,ureg,X):
    p=calibrated_probs(base,cal,X)
    pu=np.clip(ureg.predict(X),-3.0,5.0)
    ps=p[:,:4].sum(axis=1)
    pf=p[:,4:8].sum(axis=1)
    pun=p[:,8]
    pef=p[:,4]
    ev=5*ps-3*pf+pun*pu-.10
    return p,pu,ps,pf,pun,pef,ev

def diagnostic(rows,direction,p,ps,pf,pun,pef,ev):
    cls=np.asarray([CLASS_TO_INT[hazard_class(x,direction)] if hazard_class(x,direction) is not None else -1 for x in rows])
    ok=cls>=0
    yy=cls[ok];pp=p[ok]
    one=np.eye(9)[yy]
    brier=float(np.mean(np.sum((pp-one)**2,axis=1)))
    realized=np.asarray([realized_gross(x,direction) for x in rows],dtype=float)
    realized_net=realized-.10
    class_stats={}
    for i,name in enumerate(CLASSES):
        class_stats[name]={
          "predicted_share":float(np.mean(pp[:,i])),
          "realized_share":float(np.mean(yy==i))
        }
    actual_success=np.isin(cls,[0,1,2,3])
    actual_failure=np.isin(cls,[4,5,6,7])
    actual_unres=cls==8
    actual_ef=cls==4
    qs=np.quantile(ev,np.linspace(0,1,11));decs={}
    for i in range(10):
        m=(ev>=qs[i])&((ev<=qs[i+1]) if i==9 else (ev<qs[i+1]))
        decs[f"D{i+1}"]={"n":int(m.sum()),"predicted_ev_mean":float(np.mean(ev[m])) if m.any() else None,
                         "realized_net_mean":float(np.mean(realized_net[m])) if m.any() else None}
    bands={}
    for name,t in THRESHOLDS.items():
        m=(ev>0) if name=="T0" else (ev>=t)
        bands[name]={"n":int(m.sum()),"predicted_ev_mean":float(np.mean(ev[m])) if m.any() else None,
                     "realized_net_mean":float(np.mean(realized_net[m])) if m.any() else None}
    return {
      "multiclass_log_loss":float(log_loss(yy,pp,labels=list(range(9)))),
      "macro_brier":brier,
      "classes":class_stats,
      "aggregate":{
        "predicted_success":float(np.mean(ps)),"realized_success":float(np.mean(actual_success)),
        "predicted_failure":float(np.mean(pf)),"realized_failure":float(np.mean(actual_failure)),
        "predicted_unresolved":float(np.mean(pun)),"realized_unresolved":float(np.mean(actual_unres)),
        "predicted_early_failure":float(np.mean(pef)),"realized_early_failure":float(np.mean(actual_ef)),
      },
      "mean_predicted_ev_f10":float(np.mean(ev)),
      "mean_realized_net_f10":float(np.mean(realized_net)),
      "ev_calibration_gap":float(np.mean(ev)-np.mean(realized_net)),
      "ev_deciles":decs,
      "ev_threshold_rows":bands
    }

def qualifies(v,t,name):
    return v>0 if name=="T0" else v>=t

def risk_ok(arm,r,cuts):
    if arm=="A_HAZARD_EV":return True
    if arm=="B_HAZARD_EV_EF_Q50":return r<=cuts["Q50"]
    if arm=="C_HAZARD_EV_EF_Q25":return r<=cuts["Q25"]
    if arm=="D_HAZARD_EV_EF_Q10":return r<=cuts["Q10"]
    return False

def choose(mode,bev,sev,br,sr,t,name,arm,bc,sc):
    b=qualifies(bev,t,name) and risk_ok(arm,br,bc)
    s=qualifies(sev,t,name) and risk_ok(arm,sr,sc)
    if mode=="BUY_ONLY":return "BUY" if b else None
    if mode=="SELL_ONLY":return "SELL" if s else None
    if not b and not s:return None
    if b and not s:return "BUY"
    if s and not b:return "SELL"
    if abs(bev-sev)<.25:return None
    return "BUY" if bev>sev else "SELL"

def simulate(rows,bev,sev,br,sr,t,name,arm,mode,bc,sc):
    raw=0;busy=-1;trades=[]
    for i,p in enumerate(rows):
        d=choose(mode,bev[i],sev[i],br[i],sr[i],t,name,arm,bc,sc)
        if d is not None:raw+=1
        ts=int(p["decision_time_ms"])
        if d is None or ts<busy:continue
        tr=e5.trade_from_row(p,d)
        if tr is None:continue
        trades.append(tr);busy=tr["exit_time_ms"]
    return raw,trades

def bootstrap(trades,reps=2000,seed=8):
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

def advancement(trades):
    allm=e5.stats(trades,.10,731);m23=e5.stats(e5.subset(trades,2023),.10,365);m24=e5.stats(e5.subset(trades,2024),.10,366)
    ci=bootstrap(trades);qp=[];total=0.0
    for y in (2023,2024):
        for q in range(1,5):
            pnl=sum(x["gross"]-.10 for x in e5.subset(trades,quarter=f"{y}-Q{q}"));qp.append(pnl)
            if pnl>0:total+=pnl
    maxshare=max([x/total for x in qp if x>0],default=0.0) if total>0 else None
    passed=(allm.get("trades",0)>=250 and m23.get("trades",0)>=75 and m24.get("trades",0)>=75 and
            m23.get("mean_net",0)>0 and m24.get("mean_net",0)>0 and (allm.get("profit_factor") or 0)>1 and
            ci[0] is not None and ci[0]>0 and maxshare is not None and maxshare<=.40)
    return {"passed":bool(passed),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":maxshare}

def eval_econ(rows,bev,sev,br,sr,bc,sc):
    out={}
    for arm in ARMS:
        out[arm]={}
        for name,t in THRESHOLDS.items():
            out[arm][name]={}
            for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
                raw,trades=simulate(rows,bev,sev,br,sr,t,name,arm,mode,bc,sc)
                e={"raw_qualifying":raw,"executed_trades":len(trades),
                   "suppression_ratio":float(1-len(trades)/raw) if raw else None,"frictions":{}}
                for fn,fr in FRICTIONS.items():
                    e["frictions"][fn]={
                      "ALL":e5.stats(trades,fr,731),
                      "2023":e5.stats(e5.subset(trades,2023),fr,365),
                      "2024":e5.stats(e5.subset(trades,2024),fr,366),
                      "quarters":{f"{y}-Q{q}":e5.stats(e5.subset(trades,quarter=f"{y}-Q{q}"),fr,92)
                                  for y in (2023,2024) for q in range(1,5)}
                    }
                e["advancement"]=advancement(trades)
                out[arm][name][mode]=e
    return out

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: exp008_competing_hazard_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    train_rows,train_X=load_train(pairs)
    vr,Xv=load_partition(pairs,"VALIDATION")
    dr,Xd=load_partition(pairs,"DEVELOPMENT_TEST")
    result={"status":"PASS","experiment":"EXP-008_COMPETING_HAZARD_V1","final_oos":"NOT_ACCESSED","directions":{}}
    scored={};cuts={}

    for d in ("BUY","SELL"):
        cal,caln=fit_calibrator(train_rows,train_X,d)
        base=fit_base(train_rows,train_X,d)
        ureg,un=fit_unresolved(train_rows,train_X,d)
        vp,vup,vps,vpf,vpun,vpef,vev=score(base,cal,ureg,Xv)
        dp,dup,dps,dpf,dpun,dpef,dev=score(base,cal,ureg,Xd)
        c={"Q50":float(np.quantile(vpef,.50)),"Q25":float(np.quantile(vpef,.25)),"Q10":float(np.quantile(vpef,.10))}
        cuts[d]=c
        mask23=np.asarray([year_of(int(p["decision_time_ms"]))==2023 for p in dr])
        mask24=np.asarray([year_of(int(p["decision_time_ms"]))==2024 for p in dr])
        result["directions"][d]={
          "calibration_rows":caln,"unresolved_train_rows":un,"validation_early_failure_cutoffs":c,
          "VALIDATION":diagnostic(vr,d,vp,vps,vpf,vpun,vpef,vev),
          "DEVELOPMENT_TEST":diagnostic(dr,d,dp,dps,dpf,dpun,dpef,dev),
          "DEVELOPMENT_TEST_2023":diagnostic([p for i,p in enumerate(dr) if mask23[i]],d,dp[mask23],dps[mask23],dpf[mask23],dpun[mask23],dpef[mask23],dev[mask23]),
          "DEVELOPMENT_TEST_2024":diagnostic([p for i,p in enumerate(dr) if mask24[i]],d,dp[mask24],dps[mask24],dpf[mask24],dpun[mask24],dpef[mask24],dev[mask24])
        }
        scored[d]=(dev,dpef)

    result["economics"]=eval_econ(dr,scored["BUY"][0],scored["SELL"][0],scored["BUY"][1],scored["SELL"][1],cuts["BUY"],cuts["SELL"])
    passing=[]
    for arm,a in result["economics"].items():
        for th,modes in a.items():
            for mode,v in modes.items():
                if v["advancement"]["passed"]:passing.append({"arm":arm,"threshold":th,"mode":mode})
    result["passing_policies"]=passing

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
