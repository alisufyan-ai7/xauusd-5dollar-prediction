#!/usr/bin/env python3
"""EXP-003 sequential threshold economics V1."""

import json,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

import economic_value_exp003_v1 as evm
import execution_economics_exp002_v1 as exp2

FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
ONE=60000
HORIZON=60*ONE

def score_direction(clf,reg,X):
    p=clf.predict_proba(X)
    u=np.clip(reg.predict(X),-3.0,5.0)
    return 5*p[:,0]-3*p[:,1]+p[:,2]*u-0.10

def qualifies(v,t,name):
    return v>0.0 if name=="T0" else v>=t

def choose(mode,buy_ev,sell_ev,t,name):
    b=qualifies(buy_ev,t,name); s=qualifies(sell_ev,t,name)
    if mode=="BUY_ONLY": return "BUY" if b else None
    if mode=="SELL_ONLY": return "SELL" if s else None
    if not b and not s:return None
    if b and not s:return "BUY"
    if s and not b:return "SELL"
    if abs(buy_ev-sell_ev)<0.25:return None
    return "BUY" if buy_ev>sell_ev else "SELL"

def trade_from_row(p,direction):
    lab_col,pnl_col=evm.direction_fields(direction)
    if p["coverage_complete"]!="True":return None
    lab=p[lab_col]
    entry=int(p["decision_time_ms"])
    if lab=="SUCCESS":
        gross=5.0
        term=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_ms=term+ONE
    elif lab in ("FAILURE","AMBIGUOUS"):
        gross=-3.0
        term=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_ms=term+ONE
    elif lab=="UNRESOLVED":
        gross=float(p[pnl_col]);exit_ms=entry+HORIZON
    else:return None
    return {"entry_time_ms":entry,"exit_time_ms":exit_ms,"direction":direction,"label":lab,"gross":gross}

def simulate(rows,buy_ev,sell_ev,t,name,mode):
    raw=0;trades=[];busy=-1
    for i,p in enumerate(rows):
        d=int(p["decision_time_ms"])
        direction=choose(mode,buy_ev[i],sell_ev[i],t,name)
        if direction is not None:raw+=1
        if d<busy or direction is None:continue
        tr=trade_from_row(p,direction)
        if tr is None:continue
        trades.append(tr);busy=tr["exit_time_ms"]
    return raw,trades

def date_of(ms):return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def year_of(ms):return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year
def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def mdd(vals):
    cum=peak=dd=0.0
    for v in vals:
        cum+=v;peak=max(peak,cum);dd=max(dd,peak-cum)
    return float(dd)

def stats(trades,friction,calendar_days):
    if not trades:return {"trades":0}
    net=np.asarray([x["gross"]-friction for x in trades],float)
    gross=np.asarray([x["gross"] for x in trades],float)
    pos=net[net>0].sum();neg=-net[net<0].sum()
    c=Counter(x["label"] for x in trades)
    holds=np.asarray([(x["exit_time_ms"]-x["entry_time_ms"])/60000 for x in trades],float)
    active=len({date_of(x["entry_time_ms"]) for x in trades})
    return {
      "trades":len(trades),"label_counts":dict(c),
      "mean_gross":float(gross.mean()),"median_gross":float(np.median(gross)),
      "mean_net":float(net.mean()),"median_net":float(np.median(net)),
      "profit_factor":float(pos/neg) if neg>0 else None,
      "cumulative_net":float(net.sum()),"max_drawdown":mdd(net),
      "active_days":active,
      "trades_per_active_day":float(len(trades)/active) if active else None,
      "trades_per_calendar_day":float(len(trades)/calendar_days),
      "holding_p25":float(np.quantile(holds,.25)),"holding_median":float(np.median(holds)),
      "holding_p75":float(np.quantile(holds,.75)),"holding_p90":float(np.quantile(holds,.90))
    }

def subset(trades,year=None,quarter=None):
    out=[]
    for x in trades:
        if year is not None and year_of(x["entry_time_ms"])!=year:continue
        if quarter is not None and quarter_of(x["entry_time_ms"])!=quarter:continue
        out.append(x)
    return out

def bootstrap(trades,friction=0.10,reps=2000,seed=3):
    by=defaultdict(list)
    for x in trades:by[date_of(x["entry_time_ms"])].append(x["gross"]-friction)
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
    q={}
    total_positive=0.0
    for y in (2023,2024):
      for qi in range(1,5):
        key=f"{y}-Q{qi}";ts=subset(trades,quarter=key)
        pnl=sum(x["gross"]-.10 for x in ts);q[key]=pnl
        if pnl>0:total_positive+=pnl
    max_share=max([(v/total_positive) for v in q.values() if v>0],default=0.0) if total_positive>0 else None
    passed=(
      allm.get("trades",0)>=250 and
      m23.get("trades",0)>=75 and m24.get("trades",0)>=75 and
      m23.get("mean_net",0)>0 and m24.get("mean_net",0)>0 and
      (allm.get("profit_factor") or 0)>1 and
      ci[0] is not None and ci[0]>0 and
      max_share is not None and max_share<=0.40
    )
    return {"passed":bool(passed),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":max_share}

def evaluate_partition(rows,X,bm,br,sm,sr,partition_name):
    bev=score_direction(bm,br,X);sev=score_direction(sm,sr,X)
    result={}
    days=365 if partition_name=="VALIDATION" else 731
    for name,t in evm.THRESHOLDS.items():
        result[name]={}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            raw,trades=simulate(rows,bev,sev,t,name,mode)
            entry={"raw_qualifying":raw,"executed_trades":len(trades),
                   "suppression_ratio":float(1-len(trades)/raw) if raw else None,
                   "frictions":{}}
            for fn,fr in FRICTIONS.items():
                entry["frictions"][fn]={
                  "ALL":stats(trades,fr,days),
                  "2023":stats(subset(trades,2023),fr,365) if partition_name=="DEVELOPMENT_TEST" else None,
                  "2024":stats(subset(trades,2024),fr,366) if partition_name=="DEVELOPMENT_TEST" else None,
                  "quarters":{f"{y}-Q{q}":stats(subset(trades,quarter=f"{y}-Q{q}"),fr,92)
                              for y in ((2023,2024) if partition_name=="DEVELOPMENT_TEST" else ())
                              for q in range(1,5)}
                }
            if partition_name=="DEVELOPMENT_TEST":
                entry["advancement"]=advancement(trades)
            result[name][mode]=entry
    return result

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:raise SystemExit("usage: threshold_economics_exp003_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    bm,br,_,_=evm.fit_direction(pairs,"BUY");sm,sr,_,_=evm.fit_direction(pairs,"SELL")
    vr,Xv=evm.load_partition(pairs,"VALIDATION")
    dr,Xd=evm.load_partition(pairs,"DEVELOPMENT_TEST")
    res={"status":"PASS","experiment":"EXP-003_THRESHOLD_ECONOMICS_V1","final_oos":"NOT_ACCESSED",
         "thresholds":evm.THRESHOLDS,
         "VALIDATION":evaluate_partition(vr,Xv,bm,br,sm,sr,"VALIDATION"),
         "DEVELOPMENT_TEST":evaluate_partition(dr,Xd,bm,br,sm,sr,"DEVELOPMENT_TEST")}
    passing=[]
    for th,modes in res["DEVELOPMENT_TEST"].items():
        for mode,v in modes.items():
            if v["advancement"]["passed"]:passing.append({"threshold":th,"mode":mode})
    res["passing_policies"]=passing
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
