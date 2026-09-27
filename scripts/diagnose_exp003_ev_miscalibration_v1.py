#!/usr/bin/env python3
"""EXP-003 EV miscalibration diagnosis V1.

Diagnostic only. Reproduces the frozen EXP-003 models and analyzes why
predicted EV_F10 differs from realized executable NET_F10.
FINAL_OOS 2025 access is forbidden.
"""

import json,sys,math
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

import economic_value_exp003_v1 as evm
import execution_economics_exp002_v1 as exp2
import threshold_economics_exp003_v1 as th

PROB_BINS=[i/10 for i in range(11)]

def year_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def train_reference(pairs):
    xs=[];idx=0
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":
                raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or f["feature_complete"]!="True":
                continue
            x=exp2.xrow(f)
            if x is None: continue
            if idx%5==0: xs.append(x)
            idx+=1
    return np.asarray(xs,dtype=np.float32)

def predict_components(clf,reg,X):
    probs=clf.predict_proba(X)
    pred_u=np.clip(reg.predict(X),-3.0,5.0)
    ev_gross=5*probs[:,0]-3*probs[:,1]+probs[:,2]*pred_u
    return probs,pred_u,ev_gross,ev_gross-0.10

def realized_arrays(rows,direction):
    lab_col,pnl_col=evm.direction_fields(direction)
    labels=[];gross=[];complete=[]
    for p in rows:
        ok=p["coverage_complete"]=="True"
        complete.append(ok)
        lab=p[lab_col]
        labels.append(lab)
        if not ok:
            gross.append(np.nan)
        elif lab=="SUCCESS":
            gross.append(5.0)
        elif lab in ("FAILURE","AMBIGUOUS"):
            gross.append(-3.0)
        elif lab=="UNRESOLVED":
            gross.append(float(p[pnl_col]))
        else:
            gross.append(np.nan)
    return np.asarray(labels,dtype=object),np.asarray(gross,float),np.asarray(complete,bool)

def threshold_mask(ev,name,val):
    return ev>0 if name=="T0" else ev>=val

def summarize_population(rows,direction,probs,pred_u,ev_gross,ev_f10,mask):
    labels,gross,complete=realized_arrays(rows,direction)
    m=np.asarray(mask,bool)&complete&np.isfinite(gross)
    n=int(m.sum())
    if not n:return {"n":0}
    labs=labels[m];g=gross[m];p=probs[m];pu=pred_u[m]
    c=Counter(labs.tolist())
    unresolved=(labs=="UNRESOLVED")
    realized_u=float(np.mean(g[unresolved])) if unresolved.any() else None
    pred_u_mean=float(np.mean(pu))
    ps,pf,pu_prob=[float(np.mean(p[:,i])) for i in range(3)]
    rs=c["SUCCESS"]/n;rf=c["FAILURE"]/n;ru=c["UNRESOLVED"]/n;ra=c["AMBIGUOUS"]/n
    model_ev=float(np.mean(ev_gross[m]))
    actual_class_ev=5*rs-3*rf-3*ra+ru*pred_u_mean
    actual_u_ev=5*ps-3*pf+pu_prob*(realized_u if realized_u is not None else 0.0)
    full_ev=5*rs-3*rf-3*ra+ru*(realized_u if realized_u is not None else 0.0)
    realized_net=g-0.10
    err=ev_f10[m]-realized_net
    return {
      "n":n,
      "predicted":{
        "p_success":ps,"p_failure":pf,"p_unresolved":pu_prob,
        "unresolved_pnl_mean":pred_u_mean,
        "ev_gross_mean":model_ev,
        "ev_f10_mean":float(np.mean(ev_f10[m]))
      },
      "realized":{
        "success_share":rs,"failure_share":rf,"unresolved_share":ru,"ambiguous_share":ra,
        "unresolved_pnl_mean":realized_u,
        "gross_mean":float(np.mean(g)),
        "net_f10_mean":float(np.mean(realized_net))
      },
      "errors":{
        "p_success":ps-rs,"p_failure":pf-rf,"p_unresolved":pu_prob-ru,
        "unresolved_pnl":None if realized_u is None else pred_u_mean-realized_u,
        "ev_f10_calibration":float(np.mean(ev_f10[m])-np.mean(realized_net))
      },
      "counterfactual_ev_gross":{
        "MODEL_EV":model_ev,
        "ACTUAL_CLASS_RATES_EV":float(actual_class_ev),
        "ACTUAL_UNRESOLVED_PNL_EV":float(actual_u_ev),
        "FULL_COMPONENT_REALIZED_EV":float(full_ev)
      },
      "ev_error":{
        "mean":float(np.mean(err)),"median":float(np.median(err)),
        "p10":float(np.quantile(err,.10)),"p25":float(np.quantile(err,.25)),
        "p75":float(np.quantile(err,.75)),"p90":float(np.quantile(err,.90)),
        "mae":float(np.mean(np.abs(err))),"rmse":float(np.sqrt(np.mean(err**2)))
      },
      "ev_error_by_outcome":{
        k:{
          "n":int(np.sum(labs==k)),
          "mean":float(np.mean(err[labs==k])) if np.any(labs==k) else None,
          "median":float(np.median(err[labs==k])) if np.any(labs==k) else None
        } for k in ("SUCCESS","FAILURE","UNRESOLVED","AMBIGUOUS")
      }
    }

def class_calibration(rows,direction,probs,mask=None):
    labels,_,complete=realized_arrays(rows,direction)
    base=complete if mask is None else complete&np.asarray(mask,bool)
    out={}
    for ci,name in enumerate(evm.CLASSES):
        arr=[]
        pv=probs[:,ci]
        for j in range(10):
            lo,hi=PROB_BINS[j],PROB_BINS[j+1]
            bm=(pv>=lo)&(pv<hi) if j<9 else (pv>=lo)&(pv<=hi)
            m=base&bm
            n=int(m.sum())
            arr.append({
              "lo":lo,"hi":hi,"n":n,
              "predicted_mean":float(np.mean(pv[m])) if n else None,
              "realized_frequency":float(np.mean(labels[m]==name)) if n else None
            })
        out[name]=arr
    return out

def feature_reference_stats(X):
    return {
      "p01":np.quantile(X,.01,axis=0),
      "q25":np.quantile(X,.25,axis=0),
      "median":np.quantile(X,.50,axis=0),
      "q75":np.quantile(X,.75,axis=0),
      "p99":np.quantile(X,.99,axis=0)
    }

def feature_shift(ref,X):
    med=np.quantile(X,.50,axis=0);q25=np.quantile(X,.25,axis=0);q75=np.quantile(X,.75,axis=0)
    rows=[]
    for i,name in enumerate(exp2.FEATURES):
        iqr=float(ref["q75"][i]-ref["q25"][i])
        norm=None if abs(iqr)<1e-12 else float((med[i]-ref["median"][i])/iqr)
        rows.append({
          "feature":name,
          "train_median":float(ref["median"][i]),
          "train_iqr":iqr,
          "period_median":float(med[i]),
          "period_iqr":float(q75[i]-q25[i]),
          "normalized_median_shift":norm
        })
    rows.sort(key=lambda x:abs(x["normalized_median_shift"]) if x["normalized_median_shift"] is not None else -1,reverse=True)
    return rows

def support_summary(ref,X,mask):
    m=np.asarray(mask,bool)
    if not m.any():return {"n":0}
    Z=X[m]
    low=Z<ref["p01"];high=Z>ref["p99"];outside=low|high
    features=[]
    for i,name in enumerate(exp2.FEATURES):
        features.append({
          "feature":name,
          "below_train_p01_share":float(np.mean(low[:,i])),
          "above_train_p99_share":float(np.mean(high[:,i]))
        })
    counts=outside.sum(axis=1)
    return {
      "n":int(len(Z)),
      "row_share_any_feature_outside":float(np.mean(counts>0)),
      "median_outside_feature_count":float(np.median(counts)),
      "features":features
    }

def seq_calibration(rows,bev,sev,t,name,mode):
    trades=[];busy=-1;raw=0
    for i,p in enumerate(rows):
        d=int(p["decision_time_ms"])
        direction=th.choose(mode,bev[i],sev[i],t,name)
        if direction is not None:raw+=1
        if direction is None or d<busy:continue
        tr=th.trade_from_row(p,direction)
        if tr is None:continue
        pred=float(bev[i] if direction=="BUY" else sev[i])
        tr["predicted_ev_f10"]=pred
        trades.append(tr);busy=tr["exit_time_ms"]
    def sm(ts):
        if not ts:return {"trades":0}
        pred=np.asarray([x["predicted_ev_f10"] for x in ts],float)
        real=np.asarray([x["gross"]-.10 for x in ts],float)
        c=Counter(x["label"] for x in ts)
        return {
          "trades":len(ts),"predicted_ev_f10_mean":float(pred.mean()),
          "realized_net_f10_mean":float(real.mean()),
          "calibration_gap":float(pred.mean()-real.mean()),
          "label_counts":dict(c)
        }
    return {
      "raw_qualifying":raw,
      "ALL":sm(trades),
      "2023":sm([x for x in trades if year_of(x["entry_time_ms"])==2023]),
      "2024":sm([x for x in trades if year_of(x["entry_time_ms"])==2024])
    }

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: diagnose_exp003_ev_miscalibration_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    tref=train_reference(pairs);ref=feature_reference_stats(tref)

    bm,br,_,_=evm.fit_direction(pairs,"BUY")
    sm,sr,_,_=evm.fit_direction(pairs,"SELL")
    vr,Xv=evm.load_partition(pairs,"VALIDATION")
    dr,Xd=evm.load_partition(pairs,"DEVELOPMENT_TEST")

    result={"status":"PASS","experiment":"EXP-003_EV_MISCALIBRATION_DIAGNOSIS_V1",
            "final_oos":"NOT_ACCESSED","train_reference_rows":int(len(tref)),
            "directions":{},"feature_shift":{},"sequential":{}}

    # Feature shift is direction-independent.
    v2023=np.asarray([year_of(int(p["decision_time_ms"]))==2023 for p in dr])
    v2024=np.asarray([year_of(int(p["decision_time_ms"]))==2024 for p in dr])
    result["feature_shift"]["VALIDATION_2022"]=feature_shift(ref,Xv)
    result["feature_shift"]["DEV_2023"]=feature_shift(ref,Xd[v2023])
    result["feature_shift"]["DEV_2024"]=feature_shift(ref,Xd[v2024])

    comps={}
    for direction,clf,reg in (("BUY",bm,br),("SELL",sm,sr)):
        probs_v,pu_v,eg_v,ef_v=predict_components(clf,reg,Xv)
        probs_d,pu_d,eg_d,ef_d=predict_components(clf,reg,Xd)
        dres={"VALIDATION":{},"DEVELOPMENT_TEST":{},"class_calibration":{},"support":{}}
        populations={"ALL":np.ones(len(vr),bool)}
        for n,t in evm.THRESHOLDS.items():populations[n]=threshold_mask(ef_v,n,t)
        for n,m in populations.items():
            dres["VALIDATION"][n]=summarize_population(vr,direction,probs_v,pu_v,eg_v,ef_v,m)
        pops_d={"ALL":np.ones(len(dr),bool)}
        for n,t in evm.THRESHOLDS.items():pops_d[n]=threshold_mask(ef_d,n,t)
        for n,m in pops_d.items():
            block={"ALL":summarize_population(dr,direction,probs_d,pu_d,eg_d,ef_d,m)}
            for y in (2023,2024):
                ym=np.asarray([year_of(int(p["decision_time_ms"]))==y for p in dr])&m
                block[str(y)]=summarize_population(dr,direction,probs_d,pu_d,eg_d,ef_d,ym)
            quarters={}
            for y in (2023,2024):
                for q in range(1,5):
                    key=f"{y}-Q{q}"
                    qm=np.asarray([quarter_of(int(p["decision_time_ms"]))==key for p in dr])&m
                    quarters[key]=summarize_population(dr,direction,probs_d,pu_d,eg_d,ef_d,qm)
            block["quarters"]=quarters
            dres["DEVELOPMENT_TEST"][n]=block

        dres["class_calibration"]["VALIDATION_2022"]=class_calibration(vr,direction,probs_v)
        dres["class_calibration"]["DEV_2023"]=class_calibration(dr,direction,probs_d,v2023)
        dres["class_calibration"]["DEV_2024"]=class_calibration(dr,direction,probs_d,v2024)
        for n,t in evm.THRESHOLDS.items():
            dres["support"][n]=support_summary(ref,Xd,pops_d[n])
        result["directions"][direction]=dres
        comps[direction]=(ef_v,ef_d)

    bev_v,bev_d=comps["BUY"];sev_v,sev_d=comps["SELL"]
    for n,t in evm.THRESHOLDS.items():
        result["sequential"][n]={}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            result["sequential"][n][mode]={
              "VALIDATION":seq_calibration(vr,bev_v,sev_v,t,n,mode),
              "DEVELOPMENT_TEST":seq_calibration(dr,bev_d,sev_d,t,n,mode)
            }

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
