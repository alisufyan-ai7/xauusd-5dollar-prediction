#!/usr/bin/env python3
"""EXP-002 sequential execution economics V1."""

import csv,json,math,sys
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

BASE_FEATURES=[
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
SPREAD_FEATURES=[
"spread_close_1m","spread_mean_5m","spread_mean_15m","spread_mean_60m",
"spread_max_15m","spread_max_60m","spread_ratio_1m_to_60m","spread_percentile_240m"
]
FEATURES=BASE_FEATURES+SPREAD_FEATURES
SHARES=(0.10,0.05,0.025,0.01)
FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
ONE=60000
HORIZON=60*ONE

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

def xrow(f):
    vals=[]
    try:
        for k in FEATURES:
            v=float(f[k])
            if not math.isfinite(v):return None
            vals.append(v)
    except Exception:return None
    return vals

def fit_model(pairs,direction):
    col="buy_label" if direction=="BUY" else "sell_label"
    xs=[];ys=[];idx=0
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!="TRAIN" or p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True":continue
            if p[col]=="AMBIGUOUS":continue
            x=xrow(f)
            if x is None:continue
            if idx%5==0:
                xs.append(x);ys.append(1 if p[col]=="SUCCESS" else 0)
            idx+=1
    m=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,max_leaf_nodes=15,
        max_depth=None,min_samples_leaf=200,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    m.fit(np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8))
    return m

def load_rows(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True":continue
            x=xrow(f)
            if x is None:continue
            rows.append(p);xs.append(x)
    return rows,np.asarray(xs,dtype=np.float32)

def date_of(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def year_of(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

def trade_from_row(p,direction):
    lab=p["buy_label"] if direction=="BUY" else p["sell_label"]
    if p["coverage_complete"]!="True": return None,"INCOMPLETE_COVERAGE"
    if lab=="SUCCESS":
        gross=5.0
        term=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_ms=term+ONE
    elif lab in ("FAILURE","AMBIGUOUS"):
        gross=-3.0
        term=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_ms=term+ONE
    elif lab=="UNRESOLVED":
        gross=float(p["buy_expiry_pnl"] if direction=="BUY" else p["sell_expiry_pnl"])
        exit_ms=int(p["decision_time_ms"])+HORIZON
    else:
        return None,"UNKNOWN_LABEL"
    entry_ms=int(p["decision_time_ms"])
    return {"entry_time_ms":entry_ms,"exit_time_ms":exit_ms,"direction":direction,"label":lab,"gross":float(gross)},None

def choose(mode,b,s):
    if mode=="BUY_ONLY": return "BUY" if b else None
    if mode=="SELL_ONLY": return "SELL" if s else None
    if b and s:return None
    if b:return "BUY"
    if s:return "SELL"
    return None

def simulate(rows,bp,sp,bcut,scut,mode):
    trades=[];busy=-1;unavail=0;reasons=defaultdict(int)
    for i,p in enumerate(rows):
        d=int(p["decision_time_ms"])
        if d<busy:continue
        direction=choose(mode,bp[i]>=bcut,sp[i]>=scut)
        if direction is None:continue
        t,err=trade_from_row(p,direction)
        if t is None:
            unavail+=1;reasons[err]+=1;continue
        trades.append(t);busy=t["exit_time_ms"]
    return trades,unavail,dict(reasons)

def mdd(vals):
    cum=peak=dd=0.0
    for v in vals:
        cum+=v;peak=max(peak,cum);dd=max(dd,peak-cum)
    return float(dd)

def metrics(trades,friction,calendar_days):
    if not trades:return {"trades":0}
    gross=np.asarray([t["gross"] for t in trades],float);net=gross-friction
    lc=defaultdict(int)
    for t in trades:lc[t["label"]]+=1
    pos=net[net>0].sum();neg=-net[net<0].sum()
    active=len({date_of(t["entry_time_ms"]) for t in trades})
    return {
      "trades":len(trades),"label_counts":dict(lc),
      "avg_gross":float(gross.mean()),"median_gross":float(np.median(gross)),
      "avg_net":float(net.mean()),"median_net":float(np.median(net)),
      "expectancy_R":float(net.mean()/3.0),"win_rate_net_positive":float((net>0).mean()),
      "profit_factor":float(pos/neg) if neg>0 else None,
      "cumulative_net":float(net.sum()),"max_drawdown":mdd(net),
      "active_trading_days":active,
      "avg_trades_per_active_day":float(len(trades)/active) if active else None,
      "avg_trades_per_calendar_day":float(len(trades)/calendar_days)
    }

def bootstrap(trades,friction,reps=1000,seed=1):
    by=defaultdict(list)
    for t in trades:by[date_of(t["entry_time_ms"])].append(t["gross"]-friction)
    days=sorted(by)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);means=[];k=len(days)
    for _ in range(reps):
        vals=[]
        for idx in rng.integers(0,k,size=k):vals.extend(by[days[idx]])
        means.append(float(np.mean(vals)))
    return [float(np.quantile(means,.025)),float(np.quantile(means,.975))]

def subset(trades,year): return [t for t in trades if year_of(t["entry_time_ms"])==year]

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:raise SystemExit("usage: execution_economics_exp002_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))
    bm=fit_model(pairs,"BUY");sm=fit_model(pairs,"SELL")
    vr,Xv=load_rows(pairs,"VALIDATION");dr,Xd=load_rows(pairs,"DEVELOPMENT_TEST")
    vb=bm.predict_proba(Xv)[:,1];vs=sm.predict_proba(Xv)[:,1]
    db=bm.predict_proba(Xd)[:,1];ds=sm.predict_proba(Xd)[:,1]
    result={"status":"PASS","experiment":"EXP-002_EXECUTION_ECONOMICS_V1","final_oos":"NOT_ACCESSED","frictions":FRICTIONS,"policies":{}}
    for share in SHARES:
        key=f"top_{share:g}";bcut=float(np.quantile(vb,1-share));scut=float(np.quantile(vs,1-share))
        pres={"buy_validation_cutoff":bcut,"sell_validation_cutoff":scut,"modes":{}}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            trades,unavail,reasons=simulate(dr,db,ds,bcut,scut,mode)
            m={}
            for fn,fr in FRICTIONS.items():
                m[fn]={
                  "ALL":metrics(trades,fr,731),
                  "2023":metrics(subset(trades,2023),fr,365),
                  "2024":metrics(subset(trades,2024),fr,366),
                  "bootstrap_avg_net_95pct":bootstrap(trades,fr)
                }
            pres["modes"][mode]={"execution_unavailable":unavail,"execution_unavailable_reasons":reasons,"results":m}
        result["policies"][key]=pres
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
