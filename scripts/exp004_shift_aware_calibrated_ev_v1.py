#!/usr/bin/env python3
"""EXP-004 shift-aware calibrated economic value V1."""

import json,sys,math
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

import economic_value_exp003_v1 as evm
import execution_economics_exp002_v1 as exp2
import threshold_economics_exp003_v1 as th

THRESHOLDS=evm.THRESHOLDS
FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
ONE=60000
HORIZON=60*ONE

def year_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def load_train(pairs):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":
                raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True":
                continue
            x=exp2.xrow(f)
            if x is None: continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def direction_fields(direction):
    return evm.direction_fields(direction)

def fit_base_classifier(rows,X,direction,year_lt=None):
    label_col,_=direction_fields(direction)
    idx=[]
    for i,p in enumerate(rows):
        if p["coverage_complete"]!="True": continue
        if p[label_col]=="AMBIGUOUS": continue
        if year_lt is not None and year_of(int(p["decision_time_ms"]))>=year_lt: continue
        idx.append(i)
    thin=idx[::5]
    y=np.asarray([evm.CLASS_TO_INT[rows[i][label_col]] for i in thin],dtype=np.int8)
    model=HistGradientBoostingClassifier(
      loss="log_loss",learning_rate=0.05,max_iter=200,max_leaf_nodes=15,
      max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,
      early_stopping=False,random_state=1)
    model.fit(X[np.asarray(thin,dtype=int)],y)
    return model

def fit_full_regressor(rows,X,direction):
    label_col,pnl_col=direction_fields(direction)
    idx=[i for i,p in enumerate(rows)
         if p["coverage_complete"]=="True" and p[label_col]=="UNRESOLVED"]
    y=np.asarray([float(rows[i][pnl_col]) for i in idx],dtype=np.float32)
    model=HistGradientBoostingRegressor(
      loss="squared_error",learning_rate=0.05,max_iter=200,max_leaf_nodes=15,
      max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,
      early_stopping=False,random_state=1)
    model.fit(X[np.asarray(idx,dtype=int)],y)
    return model

def fit_calibrator(train_rows,train_X,direction):
    label_col,_=direction_fields(direction)
    z=[];y=[]
    for pred_year in (2017,2018,2019,2020,2021):
        m=fit_base_classifier(train_rows,train_X,direction,year_lt=pred_year)
        idx=[i for i,p in enumerate(train_rows)
             if year_of(int(p["decision_time_ms"]))==pred_year
             and p["coverage_complete"]=="True"
             and p[label_col]!="AMBIGUOUS"]
        if not idx: continue
        probs=m.predict_proba(train_X[np.asarray(idx,dtype=int)])
        z.append(np.log(np.clip(probs,1e-6,1-1e-6)))
        y.extend(evm.CLASS_TO_INT[train_rows[i][label_col]] for i in idx)
    Z=np.vstack(z)
    yy=np.asarray(y,dtype=np.int8)
    cal=LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,class_weight=None,random_state=1)
    cal.fit(Z,yy)
    return cal,int(len(yy))

def apply_calibrator(cal,probs):
    return cal.predict_proba(np.log(np.clip(probs,1e-6,1-1e-6)))

def support_reference(train_rows,train_X):
    idx=list(range(0,len(train_rows),5))
    X=train_X[np.asarray(idx,dtype=int)]
    q={
      "p01":np.quantile(X,.01,axis=0),
      "q25":np.quantile(X,.25,axis=0),
      "q75":np.quantile(X,.75,axis=0),
      "p99":np.quantile(X,.99,axis=0)
    }
    return q,int(len(X))

def support_status(ref,X):
    p01,q25,q75,p99=ref["p01"],ref["q25"],ref["q75"],ref["p99"]
    iqr=q75-q25
    low=X<p01;high=X>p99
    outside=low|high
    ex=np.zeros_like(X,dtype=np.float64)
    safe=np.where(np.abs(iqr)<1e-12,1.0,iqr)
    ex[low]=(np.broadcast_to(p01,X.shape)[low]-X[low])/np.broadcast_to(safe,X.shape)[low]
    ex[high]=(X[high]-np.broadcast_to(p99,X.shape)[high])/np.broadcast_to(safe,X.shape)[high]
    zero=(np.abs(iqr)<1e-12)
    if np.any(zero):
        ex[:,zero]=outside[:,zero].astype(float)
    count=outside.sum(axis=1)
    total=ex.sum(axis=1)
    eligible=(count<=2)&(total<=1.0)
    return eligible,count,total

def score_components(clf,cal,reg,X):
    raw=clf.predict_proba(X)
    calibrated=apply_calibrator(cal,raw)
    pu=np.clip(reg.predict(X),-3.0,5.0)
    raw_ev=5*raw[:,0]-3*raw[:,1]+raw[:,2]*pu-0.10
    cal_ev=5*calibrated[:,0]-3*calibrated[:,1]+calibrated[:,2]*pu-0.10
    return raw,calibrated,pu,raw_ev,cal_ev

def realized_arrays(rows,direction):
    label_col,pnl_col=direction_fields(direction)
    labels=[];gross=[];complete=[]
    for p in rows:
        ok=p["coverage_complete"]=="True"
        complete.append(ok);lab=p[label_col];labels.append(lab)
        if not ok:gross.append(np.nan)
        elif lab=="SUCCESS":gross.append(5.0)
        elif lab in ("FAILURE","AMBIGUOUS"):gross.append(-3.0)
        elif lab=="UNRESOLVED":gross.append(float(p[pnl_col]))
        else:gross.append(np.nan)
    return np.asarray(labels,dtype=object),np.asarray(gross,float),np.asarray(complete,bool)

def calibration_metrics(rows,direction,probs,ev):
    labels,gross,complete=realized_arrays(rows,direction)
    usable=complete&(labels!="AMBIGUOUS")&np.isfinite(gross)
    y=np.asarray([evm.CLASS_TO_INT[x] for x in labels[usable]],dtype=np.int8)
    pp=probs[usable]
    brier={}
    for i,name in enumerate(evm.CLASSES):
        t=(y==i).astype(float);brier[name]=float(np.mean((pp[:,i]-t)**2))
    class_pred={name:float(np.mean(pp[:,i])) for i,name in enumerate(evm.CLASSES)}
    class_real={name:float(np.mean(labels[usable]==name)) for name in evm.CLASSES}
    bins={}
    for i,name in enumerate(evm.CLASSES):
        arr=[];pv=probs[:,i]
        for j in range(10):
            lo=j/10;hi=(j+1)/10
            m=complete&(pv>=lo)&((pv<hi) if j<9 else (pv<=hi))
            arr.append({
              "lo":lo,"hi":hi,"n":int(m.sum()),
              "predicted_mean":float(np.mean(pv[m])) if m.any() else None,
              "realized_frequency":float(np.mean(labels[m]==name)) if m.any() else None
            })
        bins[name]=arr
    rm=complete&np.isfinite(gross)
    return {
      "multiclass_log_loss":float(log_loss(y,pp,labels=[0,1,2])),
      "brier_by_class":brier,
      "predicted_class_means":class_pred,
      "realized_class_shares":class_real,
      "mean_predicted_ev_f10":float(np.mean(ev[rm])),
      "mean_realized_net_f10":float(np.mean(gross[rm]-0.10)),
      "ev_calibration_gap":float(np.mean(ev[rm])-np.mean(gross[rm]-0.10)),
      "probability_bins":bins
    }

def qualifies(v,t,name):
    return v>0 if name=="T0" else v>=t

def choose(mode,bev,sev,t,name,bok=True,sok=True):
    b=bok and qualifies(bev,t,name);s=sok and qualifies(sev,t,name)
    if mode=="BUY_ONLY":return "BUY" if b else None
    if mode=="SELL_ONLY":return "SELL" if s else None
    if not b and not s:return None
    if b and not s:return "BUY"
    if s and not b:return "SELL"
    if abs(bev-sev)<0.25:return None
    return "BUY" if bev>sev else "SELL"

def trade_from_row(p,direction):
    return th.trade_from_row(p,direction)

def simulate(rows,bev,sev,t,name,mode,support=None):
    raw=0;trades=[];busy=-1
    for i,p in enumerate(rows):
        ok=True if support is None else bool(support[i])
        direction=choose(mode,bev[i],sev[i],t,name,ok,ok)
        if direction is not None:raw+=1
        d=int(p["decision_time_ms"])
        if direction is None or d<busy:continue
        tr=trade_from_row(p,direction)
        if tr is None:continue
        trades.append(tr);busy=tr["exit_time_ms"]
    return raw,trades

def date_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()

def subset(trades,year=None,quarter=None):
    out=[]
    for x in trades:
        if year is not None and year_of(x["entry_time_ms"])!=year:continue
        if quarter is not None and quarter_of(x["entry_time_ms"])!=quarter:continue
        out.append(x)
    return out

def stats(trades,friction,calendar_days):
    if not trades:return {"trades":0}
    gross=np.asarray([x["gross"] for x in trades],float)
    net=gross-friction
    pos=net[net>0].sum();neg=-net[net<0].sum()
    c=Counter(x["label"] for x in trades)
    holds=np.asarray([(x["exit_time_ms"]-x["entry_time_ms"])/60000 for x in trades],float)
    active=len({date_of(x["entry_time_ms"]) for x in trades})
    cum=0;peak=0;dd=0
    for v in net:
        cum+=v;peak=max(peak,cum);dd=max(dd,peak-cum)
    return {
      "trades":len(trades),"label_counts":dict(c),
      "mean_gross":float(gross.mean()),"median_gross":float(np.median(gross)),
      "mean_net":float(net.mean()),"median_net":float(np.median(net)),
      "profit_factor":float(pos/neg) if neg>0 else None,
      "cumulative_net":float(net.sum()),"max_drawdown":float(dd),
      "active_days":active,
      "trades_per_active_day":float(len(trades)/active) if active else None,
      "trades_per_calendar_day":float(len(trades)/calendar_days),
      "holding_p25":float(np.quantile(holds,.25)),"holding_median":float(np.median(holds)),
      "holding_p75":float(np.quantile(holds,.75)),"holding_p90":float(np.quantile(holds,.90))
    }

def bootstrap(trades,reps=2000,seed=4):
    by=defaultdict(list)
    for x in trades:by[date_of(x["entry_time_ms"])].append(x["gross"]-.10)
    days=sorted(by)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);vals=[];n=len(days)
    for _ in range(reps):
        sample=[]
        for j in rng.integers(0,n,size=n):sample.extend(by[days[j]])
        vals.append(float(np.mean(sample)))
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def advancement(trades):
    allm=stats(trades,.10,731);m23=stats(subset(trades,2023),.10,365);m24=stats(subset(trades,2024),.10,366)
    ci=bootstrap(trades)
    q={};total_pos=0.0
    for y in (2023,2024):
      for qi in range(1,5):
        key=f"{y}-Q{qi}";pnl=sum(x["gross"]-.10 for x in subset(trades,quarter=key))
        q[key]=pnl
        if pnl>0:total_pos+=pnl
    max_share=max([v/total_pos for v in q.values() if v>0],default=0.0) if total_pos>0 else None
    passed=(
      allm.get("trades",0)>=250 and m23.get("trades",0)>=75 and m24.get("trades",0)>=75 and
      m23.get("mean_net",0)>0 and m24.get("mean_net",0)>0 and
      (allm.get("profit_factor") or 0)>1 and ci[0] is not None and ci[0]>0 and
      max_share is not None and max_share<=0.40
    )
    return {"passed":bool(passed),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":max_share}

def eval_arm(rows,bev,sev,support,arm_name,partition):
    result={};days=365 if partition=="VALIDATION" else 731
    for name,t in THRESHOLDS.items():
        result[name]={}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            raw,trades=simulate(rows,bev,sev,t,name,mode,support)
            e={"raw_qualifying":raw,"executed_trades":len(trades),
               "suppression_ratio":float(1-len(trades)/raw) if raw else None,
               "frictions":{}}
            for fn,fr in FRICTIONS.items():
                e["frictions"][fn]={
                  "ALL":stats(trades,fr,days),
                  "2023":stats(subset(trades,2023),fr,365) if partition=="DEVELOPMENT_TEST" else None,
                  "2024":stats(subset(trades,2024),fr,366) if partition=="DEVELOPMENT_TEST" else None,
                  "quarters":{f"{y}-Q{q}":stats(subset(trades,quarter=f"{y}-Q{q}"),fr,92)
                              for y in ((2023,2024) if partition=="DEVELOPMENT_TEST" else ())
                              for q in range(1,5)}
                }
            if partition=="DEVELOPMENT_TEST" and arm_name in ("B_CAL_EV","C_CAL_EV_SUPPORT"):
                e["advancement"]=advancement(trades)
            result[name][mode]=e
    return result

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: exp004_shift_aware_calibrated_ev_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    train_rows,train_X=load_train(pairs)
    support_ref,support_ref_n=support_reference(train_rows,train_X)

    models={}
    for direction in ("BUY","SELL"):
        cal,cal_n=fit_calibrator(train_rows,train_X,direction)
        clf=fit_base_classifier(train_rows,train_X,direction,year_lt=None)
        reg=fit_full_regressor(train_rows,train_X,direction)
        models[direction]=(clf,cal,reg,cal_n)

    vr,Xv=evm.load_partition(pairs,"VALIDATION")
    dr,Xd=evm.load_partition(pairs,"DEVELOPMENT_TEST")

    v_support,v_count,v_ex=support_status(support_ref,Xv)
    d_support,d_count,d_ex=support_status(support_ref,Xd)

    parts={}
    scored={}
    for part,rows,X,support,count,ex in (
        ("VALIDATION",vr,Xv,v_support,v_count,v_ex),
        ("DEVELOPMENT_TEST",dr,Xd,d_support,d_count,d_ex)):
        parts[part]={
          "support":{
            "eligible_share":float(np.mean(support)),
            "rejected_share":float(np.mean(~support)),
            "outside_count_quantiles":{str(q):float(np.quantile(count,q)) for q in (.5,.75,.9,.95,.99)},
            "total_exceedance_quantiles":{str(q):float(np.quantile(ex,q)) for q in (.5,.75,.9,.95,.99)}
          },
          "directions":{}
        }
        scored[part]={}
        for direction in ("BUY","SELL"):
            clf,cal,reg,cal_n=models[direction]
            raw,calp,pu,raw_ev,cal_ev=score_components(clf,cal,reg,X)
            parts[part]["directions"][direction]={
              "calibration_rows":cal_n,
              "RAW_EV":calibration_metrics(rows,direction,raw,raw_ev),
              "CAL_EV":calibration_metrics(rows,direction,calp,cal_ev)
            }
            scored[part][direction]=(raw_ev,cal_ev)

    result={
      "status":"PASS","experiment":"EXP-004_SHIFT_AWARE_CALIBRATED_EV_V1",
      "final_oos":"NOT_ACCESSED","support_reference_rows":support_ref_n,
      "calibration_diagnostics":parts,
      "economics":{}
    }

    for part,rows,support in (("VALIDATION",vr,v_support),("DEVELOPMENT_TEST",dr,d_support)):
        bev_raw,bev_cal=scored[part]["BUY"];sev_raw,sev_cal=scored[part]["SELL"]
        result["economics"][part]={
          "A_RAW_EV":eval_arm(rows,bev_raw,sev_raw,None,"A_RAW_EV",part),
          "B_CAL_EV":eval_arm(rows,bev_cal,sev_cal,None,"B_CAL_EV",part),
          "C_CAL_EV_SUPPORT":eval_arm(rows,bev_cal,sev_cal,support,"C_CAL_EV_SUPPORT",part)
        }

    passing=[]
    for arm in ("B_CAL_EV","C_CAL_EV_SUPPORT"):
        for thname,modes in result["economics"]["DEVELOPMENT_TEST"][arm].items():
            for mode,v in modes.items():
                if v.get("advancement",{}).get("passed"):
                    passing.append({"arm":arm,"threshold":thname,"mode":mode})
    result["passing_policies"]=passing

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
