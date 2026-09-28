#!/usr/bin/env python3
"""EXP-005 downside-first direct economic model V1."""

import json,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error,roc_auc_score,average_precision_score,brier_score_loss

import economic_value_exp003_v1 as evm
import execution_economics_exp002_v1 as exp2

ONE=60000
HORIZON=60*ONE
FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
THRESHOLDS={"T0":0.00,"T25":0.25,"T50":0.50,"T75":0.75}
ARMS=("A_DIRECT_ONLY","B_DIRECT_EF_Q50","C_DIRECT_EF_Q25","D_DIRECT_EF_Q10")

def year_of(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year
def date_of(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def fields(direction):
    if direction=="BUY":
        return "buy_label","buy_expiry_pnl","buy_terminal_bar_timestamp_ms"
    return "sell_label","sell_expiry_pnl","sell_terminal_bar_timestamp_ms"

def realized_gross(p,direction):
    lab,pnl,_=fields(direction)
    if p["coverage_complete"]!="True": return None
    v=p[lab]
    if v=="SUCCESS": return 5.0
    if v=="FAILURE": return -3.0
    if v=="UNRESOLVED": return float(p[pnl])
    if v=="AMBIGUOUS": return -3.0
    return None

def early_failure(p,direction):
    lab,_,term=fields(direction)
    if p["coverage_complete"]!="True" or p[lab]!="FAILURE": return 0
    entry=int(p["decision_time_ms"])
    exit_ms=int(p[term])+ONE
    return int((exit_ms-entry)<=5*ONE)

def load_partition(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS": raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True": continue
            x=exp2.xrow(f)
            if x is None: continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def fit_models(pairs,direction):
    xs=[];yr=[];yc=[];idx=0
    lab,_,_=fields(direction)
    for pp,fp in pairs:
        for p,f in exp2.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS": raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True": continue
            if p[lab]=="AMBIGUOUS": continue
            x=exp2.xrow(f)
            if x is None: continue
            if idx%5==0:
                xs.append(x);yr.append(realized_gross(p,direction));yc.append(early_failure(p,direction))
            idx+=1
    X=np.asarray(xs,dtype=np.float32)
    reg=HistGradientBoostingRegressor(loss="squared_error",learning_rate=.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    reg.fit(X,np.asarray(yr,dtype=np.float32))
    clf=HistGradientBoostingClassifier(loss="log_loss",learning_rate=.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    clf.fit(X,np.asarray(yc,dtype=np.int8))
    return reg,clf,len(yr),int(np.sum(yc))

def predict(reg,clf,X):
    gross=np.clip(reg.predict(X),-3.0,5.0)
    net=gross-.10
    ef=clf.predict_proba(X)[:,1]
    return gross,net,ef

def fixed_band(v):
    if v<=-.50:return "LE_NEG50"
    if v<=0:return "NEG50_TO_0"
    if v<.25:return "0_TO_25"
    if v<.50:return "25_TO_50"
    if v<.75:return "50_TO_75"
    return "GE_75"

def predictive_metrics(rows,direction,pred_gross,pred_net,ef):
    labels=np.asarray([realized_gross(p,direction) for p in rows],dtype=float)
    valid=np.isfinite(labels)
    y=labels[valid];pg=pred_gross[valid];pn=pred_net[valid]
    efr=np.asarray([early_failure(p,direction) for p in rows],dtype=int)[valid]
    efv=ef[valid]
    corr=float(np.corrcoef(pg,y)[0,1]) if len(y)>1 and np.std(pg)>0 and np.std(y)>0 else None
    bands={}
    for name in ("LE_NEG50","NEG50_TO_0","0_TO_25","25_TO_50","50_TO_75","GE_75"):
        m=np.asarray([fixed_band(x)==name for x in pn])
        bands[name]={"n":int(m.sum()),"predicted_gross_mean":float(np.mean(pg[m])) if m.any() else None,
                     "realized_gross_mean":float(np.mean(y[m])) if m.any() else None}
    qs=np.quantile(pn,np.linspace(0,1,11));decs={}
    for i in range(10):
        m=(pn>=qs[i])&((pn<=qs[i+1]) if i==9 else (pn<qs[i+1]))
        decs[f"D{i+1}"]={"n":int(m.sum()),"predicted_net_mean":float(np.mean(pn[m])) if m.any() else None,
                         "realized_net_mean":float(np.mean(y[m]-.10)) if m.any() else None}
    risk_q=np.quantile(efv,np.linspace(0,1,11));risk_dec={}
    for i in range(10):
        m=(efv>=risk_q[i])&((efv<=risk_q[i+1]) if i==9 else (efv<risk_q[i+1]))
        risk_dec[f"D{i+1}"]={"n":int(m.sum()),"predicted_risk_mean":float(np.mean(efv[m])) if m.any() else None,
                             "realized_early_failure_rate":float(np.mean(efr[m])) if m.any() else None}
    return {
      "n":int(len(y)),
      "regression":{"mae":float(mean_absolute_error(y,pg)),"rmse":float(mean_squared_error(y,pg)**.5),
                    "predicted_gross_mean":float(np.mean(pg)),"realized_gross_mean":float(np.mean(y)),
                    "pearson":corr,"score_deciles":decs,"fixed_net_bands":bands},
      "early_failure":{"base_rate":float(np.mean(efr)),
                       "roc_auc":float(roc_auc_score(efr,efv)) if len(np.unique(efr))>1 else None,
                       "pr_auc":float(average_precision_score(efr,efv)) if len(np.unique(efr))>1 else None,
                       "brier":float(brier_score_loss(efr,efv)),"risk_deciles":risk_dec}
    }

def qualifies(score,t,name):
    return score>0 if name=="T0" else score>=t

def risk_ok(arm,risk,cuts):
    if arm=="A_DIRECT_ONLY": return True
    if arm=="B_DIRECT_EF_Q50": return risk<=cuts["Q50"]
    if arm=="C_DIRECT_EF_Q25": return risk<=cuts["Q25"]
    if arm=="D_DIRECT_EF_Q10": return risk<=cuts["Q10"]
    return False

def choose(mode,bscore,sscore,brisk,srisk,t,name,arm,bcuts,scuts):
    b=qualifies(bscore,t,name) and risk_ok(arm,brisk,bcuts)
    s=qualifies(sscore,t,name) and risk_ok(arm,srisk,scuts)
    if mode=="BUY_ONLY": return "BUY" if b else None
    if mode=="SELL_ONLY": return "SELL" if s else None
    if not b and not s:return None
    if b and not s:return "BUY"
    if s and not b:return "SELL"
    if abs(bscore-sscore)<.25:return None
    return "BUY" if bscore>sscore else "SELL"

def trade_from_row(p,direction):
    lab,pnl,term=fields(direction)
    if p["coverage_complete"]!="True":return None
    v=p[lab];entry=int(p["decision_time_ms"])
    if v=="SUCCESS":
        gross=5.0;exit_ms=int(p[term])+ONE
    elif v in ("FAILURE","AMBIGUOUS"):
        gross=-3.0;exit_ms=int(p[term])+ONE
    elif v=="UNRESOLVED":
        gross=float(p[pnl]);exit_ms=entry+HORIZON
    else:return None
    return {"entry_time_ms":entry,"exit_time_ms":exit_ms,"direction":direction,"label":v,
            "gross":gross,"early_failure":early_failure(p,direction)}

def simulate(rows,bscore,sscore,brisk,srisk,t,name,arm,mode,bcuts,scuts):
    raw=0;busy=-1;trades=[]
    for i,p in enumerate(rows):
        d=choose(mode,bscore[i],sscore[i],brisk[i],srisk[i],t,name,arm,bcuts,scuts)
        if d is not None:raw+=1
        ts=int(p["decision_time_ms"])
        if d is None or ts<busy:continue
        tr=trade_from_row(p,d)
        if tr is None:continue
        trades.append(tr);busy=tr["exit_time_ms"]
    return raw,trades

def subset(trades,year=None,quarter=None):
    out=[]
    for x in trades:
        if year is not None and year_of(x["entry_time_ms"])!=year:continue
        if quarter is not None and quarter_of(x["entry_time_ms"])!=quarter:continue
        out.append(x)
    return out

def stats(trades,friction,calendar_days):
    if not trades:return {"trades":0}
    gross=np.asarray([x["gross"] for x in trades],float);net=gross-friction
    pos=net[net>0].sum();neg=-net[net<0].sum();c=Counter(x["label"] for x in trades)
    holds=np.asarray([(x["exit_time_ms"]-x["entry_time_ms"])/60000 for x in trades],float)
    active=len({date_of(x["entry_time_ms"]) for x in trades})
    cum=peak=dd=0.0
    for v in net:cum+=v;peak=max(peak,cum);dd=max(dd,peak-cum)
    return {"trades":len(trades),"label_counts":dict(c),"early_failure_count":int(sum(x["early_failure"] for x in trades)),
      "early_failure_share":float(np.mean([x["early_failure"] for x in trades])),
      "mean_gross":float(gross.mean()),"median_gross":float(np.median(gross)),
      "mean_net":float(net.mean()),"median_net":float(np.median(net)),
      "profit_factor":float(pos/neg) if neg>0 else None,"cumulative_net":float(net.sum()),"max_drawdown":float(dd),
      "active_days":active,"trades_per_active_day":float(len(trades)/active) if active else None,
      "trades_per_calendar_day":float(len(trades)/calendar_days),
      "holding_p25":float(np.quantile(holds,.25)),"holding_median":float(np.median(holds)),
      "holding_p75":float(np.quantile(holds,.75)),"holding_p90":float(np.quantile(holds,.90))}

def bootstrap(trades,reps=2000,seed=5):
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
    ci=bootstrap(trades);qp=[];total=0
    for y in (2023,2024):
      for q in range(1,5):
        pnl=sum(x["gross"]-.10 for x in subset(trades,quarter=f"{y}-Q{q}"));qp.append(pnl)
        if pnl>0:total+=pnl
    maxshare=max([x/total for x in qp if x>0],default=0.0) if total>0 else None
    passed=(allm.get("trades",0)>=250 and m23.get("trades",0)>=75 and m24.get("trades",0)>=75 and
            m23.get("mean_net",0)>0 and m24.get("mean_net",0)>0 and (allm.get("profit_factor") or 0)>1 and
            ci[0] is not None and ci[0]>0 and maxshare is not None and maxshare<=.40)
    return {"passed":bool(passed),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":maxshare}

def eval_economics(rows,bscore,sscore,brisk,srisk,bcuts,scuts):
    res={}
    for arm in ARMS:
      res[arm]={}
      for name,t in THRESHOLDS.items():
        res[arm][name]={}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
          raw,trades=simulate(rows,bscore,sscore,brisk,srisk,t,name,arm,mode,bcuts,scuts)
          e={"raw_qualifying":raw,"executed_trades":len(trades),
             "suppression_ratio":float(1-len(trades)/raw) if raw else None,"frictions":{}}
          for fn,fr in FRICTIONS.items():
            e["frictions"][fn]={"ALL":stats(trades,fr,731),"2023":stats(subset(trades,2023),fr,365),
              "2024":stats(subset(trades,2024),fr,366),
              "quarters":{f"{y}-Q{q}":stats(subset(trades,quarter=f"{y}-Q{q}"),fr,92) for y in (2023,2024) for q in range(1,5)}}
          e["advancement"]=advancement(trades)
          res[arm][name][mode]=e
    return res

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:raise SystemExit("usage: exp005_downside_first_direct_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    models={}
    for d in ("BUY","SELL"):models[d]=fit_models(pairs,d)
    vr,Xv=load_partition(pairs,"VALIDATION");dr,Xd=load_partition(pairs,"DEVELOPMENT_TEST")
    scores={}
    result={"status":"PASS","experiment":"EXP-005_DOWNSIDE_FIRST_DIRECT_V1","final_oos":"NOT_ACCESSED","directions":{}}
    cuts={}
    for d in ("BUY","SELL"):
      reg,clf,n,ne=models[d]
      vg,vn,vef=predict(reg,clf,Xv);dg,dn,defr=predict(reg,clf,Xd)
      c={"Q50":float(np.quantile(vef,.50)),"Q25":float(np.quantile(vef,.25)),"Q10":float(np.quantile(vef,.10))}
      cuts[d]=c
      result["directions"][d]={"train_rows":n,"train_early_failures":ne,"validation_risk_cutoffs":c,
        "VALIDATION":predictive_metrics(vr,d,vg,vn,vef),
        "DEVELOPMENT_TEST":predictive_metrics(dr,d,dg,dn,defr),
        "DEVELOPMENT_TEST_2023":predictive_metrics([p for p in dr if year_of(int(p["decision_time_ms"]))==2023],d,
          dg[np.asarray([year_of(int(p["decision_time_ms"]))==2023 for p in dr])],
          dn[np.asarray([year_of(int(p["decision_time_ms"]))==2023 for p in dr])],
          defr[np.asarray([year_of(int(p["decision_time_ms"]))==2023 for p in dr])]),
        "DEVELOPMENT_TEST_2024":predictive_metrics([p for p in dr if year_of(int(p["decision_time_ms"]))==2024],d,
          dg[np.asarray([year_of(int(p["decision_time_ms"]))==2024 for p in dr])],
          dn[np.asarray([year_of(int(p["decision_time_ms"]))==2024 for p in dr])],
          defr[np.asarray([year_of(int(p["decision_time_ms"]))==2024 for p in dr])])}
      scores[d]=(dn,defr)
    result["economics"]=eval_economics(dr,scores["BUY"][0],scores["SELL"][0],scores["BUY"][1],scores["SELL"][1],cuts["BUY"],cuts["SELL"])
    passing=[]
    for arm,a in result["economics"].items():
      for thn,modes in a.items():
        for mode,v in modes.items():
          if v["advancement"]["passed"]:passing.append({"arm":arm,"threshold":thn,"mode":mode})
    result["passing_policies"]=passing
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
