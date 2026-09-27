#!/usr/bin/env python3
"""EXP-001 Execution Economics V1.

Non-sealed BID-path economic proxy. Reproduces frozen GBT V1, derives
operational VALIDATION cutoffs from all eligible feature-complete rows, and
simulates sequential DEVELOPMENT_TEST trades with frozen exit/cost rules.
"""
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
COSTS={"C0":0.00,"C10":0.10,"C20":0.20,"C30":0.30,"C50":0.50}
ONE_MINUTE_MS=60000
HORIZON_MS=60*ONE_MINUTE_MS

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
    if not xs: raise SystemExit("NO_TRAIN_ROWS")
    return np.asarray(xs,dtype=np.float32),np.asarray(ys,dtype=np.int8)

def load_partition_all(pairs,partition):
    rows=[];xs=[]
    for pp,fp in pairs:
        for p,f in iter_join(pp,fp):
            if not eligible(p,f) or p["partition"]!=partition:continue
            x=parse_x(f)
            if x is None:continue
            rows.append(p);xs.append(x)
    if not rows: raise SystemExit(f"NO_ROWS_{partition}")
    return rows,np.asarray(xs,dtype=np.float32)

def train_models(pairs):
    out={}
    for direction in ("BUY","SELL"):
        X,y=load_train_thinned(pairs,direction)
        m=HistGradientBoostingClassifier(loss="log_loss",learning_rate=0.05,max_iter=200,
            max_leaf_nodes=15,max_depth=None,min_samples_leaf=200,l2_regularization=1.0,
            max_bins=255,early_stopping=False,random_state=1)
        m.fit(X,y);out[direction]=m
    return out

def load_raw_closes(raw_files):
    closes={}
    for path in raw_files:
        with Path(path).open(encoding="utf-8",newline="") as f:
            r=csv.DictReader(f)
            for row in r:
                closes[int(row["timestamp"])]=float(row["close"])
    return closes

def year_day(ts_ms):
    d=datetime.fromtimestamp(ts_ms/1000,timezone.utc)
    return d.year,d.date().isoformat()

def trade_from_row(p,direction,expiry_closes):
    lab=p["buy_label"] if direction=="BUY" else p["sell_label"]
    ref=float(p["reference_price"])
    decision=int(p["decision_time_ms"])
    if lab=="SUCCESS":
        gross=5.0
        terminal=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_time=terminal+ONE_MINUTE_MS
    elif lab=="FAILURE":
        gross=-3.0
        terminal=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_time=terminal+ONE_MINUTE_MS
    elif lab=="AMBIGUOUS":
        gross=-3.0
        terminal=int(p["buy_terminal_bar_timestamp_ms"] if direction=="BUY" else p["sell_terminal_bar_timestamp_ms"])
        exit_time=terminal+ONE_MINUTE_MS
    elif lab=="UNRESOLVED":
        expiry_start=decision+(59*ONE_MINUTE_MS)
        if expiry_start not in expiry_closes:
            raise SystemExit(f"MISSING_EXPIRY_CLOSE_{expiry_start}")
        close=expiry_closes[expiry_start]
        gross=(close-ref) if direction=="BUY" else (ref-close)
        exit_time=decision+HORIZON_MS
    else:
        raise SystemExit(f"UNKNOWN_LABEL_{lab}")
    y,day=year_day(decision)
    return {"entry_time_ms":decision,"exit_time_ms":exit_time,"year":y,"day":day,
            "direction":direction,"label":lab,"gross":float(gross)}

def simulate(rows,buy_scores,sell_scores,buy_cut,sell_cut,mode,expiry_closes):
    trades=[];busy_until=-1
    for i,p in enumerate(rows):
        decision=int(p["decision_time_ms"])
        if decision<busy_until: continue
        b=buy_scores[i]>=buy_cut
        s=sell_scores[i]>=sell_cut
        direction=None
        if mode=="BUY_ONLY":
            if b: direction="BUY"
        elif mode=="SELL_ONLY":
            if s: direction="SELL"
        elif mode=="COMBINED":
            if b and s:
                continue
            if b: direction="BUY"
            elif s: direction="SELL"
        else:
            raise ValueError(mode)
        if direction is None: continue
        t=trade_from_row(p,direction,expiry_closes)
        trades.append(t);busy_until=t["exit_time_ms"]
    return trades

def max_drawdown(vals):
    cum=0.0;peak=0.0;mdd=0.0
    for v in vals:
        cum+=v;peak=max(peak,cum);mdd=max(mdd,peak-cum)
    return mdd

def metrics(trades,cost,calendar_days):
    if not trades:
        return {"trades":0}
    gross=np.asarray([t["gross"] for t in trades],dtype=float)
    net=gross-cost
    labels=defaultdict(int)
    for t in trades: labels[t["label"]]+=1
    pos=net[net>0].sum();neg=-net[net<0].sum()
    active=len(set(t["day"] for t in trades))
    return {
      "trades":int(len(trades)),
      "label_counts":dict(labels),
      "avg_gross":float(gross.mean()),
      "median_gross":float(np.median(gross)),
      "avg_net":float(net.mean()),
      "median_net":float(np.median(net)),
      "expectancy_R":float(net.mean()/3.0),
      "win_rate_net_positive":float((net>0).mean()),
      "profit_factor":float(pos/neg) if neg>0 else None,
      "cumulative_net":float(net.sum()),
      "max_drawdown":float(max_drawdown(net)),
      "active_trading_days":int(active),
      "avg_trades_per_active_day":float(len(trades)/active) if active else None,
      "avg_trades_per_calendar_day":float(len(trades)/calendar_days) if calendar_days else None
    }

def bootstrap_expectancy(trades,cost,reps=1000,seed=1):
    byday=defaultdict(list)
    for t in trades: byday[t["day"]].append(t["gross"]-cost)
    days=sorted(byday)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);means=[]
    k=len(days)
    for _ in range(reps):
        idx=rng.integers(0,k,size=k);vals=[]
        for j in idx: vals.extend(byday[days[j]])
        if vals: means.append(float(np.mean(vals)))
    return [float(np.quantile(means,0.025)),float(np.quantile(means,0.975))]

def subset_year(trades,year):
    return [t for t in trades if t["year"]==year]

def main(argv):
    if "--raw" not in argv:
        raise SystemExit("usage: execution_economics_exp001_v1.py <out.json> <partitioned.csv> <features.csv> [...] --raw <raw.csv> [...]")
    k=argv.index("--raw")
    left=argv[1:k];raw=argv[k+1:]
    if len(left)<3 or (len(left)-1)%2:
        raise SystemExit("bad partition/feature args")
    out=Path(left[0]);pairs=list(zip(left[1::2],left[2::2]))
    if not raw: raise SystemExit("NO_RAW_FILES")

    models=train_models(pairs)
    vrows,Xv=load_partition_all(pairs,"VALIDATION")
    drows,Xd=load_partition_all(pairs,"DEVELOPMENT_TEST")
    vb=models["BUY"].predict_proba(Xv)[:,1]; vs=models["SELL"].predict_proba(Xv)[:,1]
    db=models["BUY"].predict_proba(Xd)[:,1]; ds=models["SELL"].predict_proba(Xd)[:,1]
    closes=load_raw_closes(raw)

    result={"status":"PASS","experiment":"EXP-001_EXECUTION_ECONOMICS_V1",
            "final_oos":"NOT_ACCESSED","cost_model":"ALL_IN_ROUND_TRIP_PRICE_UNIT_DEDUCTION",
            "cost_scenarios":COSTS,"policies":{}}

    cal_days_all=(datetime(2024,12,31,tzinfo=timezone.utc).date()-datetime(2023,1,1,tzinfo=timezone.utc).date()).days+1
    cal_days_year={2023:365,2024:366}

    for share in SHARES:
        bcut=float(np.quantile(vb,1-share));scut=float(np.quantile(vs,1-share))
        pkey=f"top_{share:g}"
        pres={"buy_validation_cutoff":bcut,"sell_validation_cutoff":scut,"modes":{}}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            trades=simulate(drows,db,ds,bcut,scut,mode,closes)
            mres={}
            for cname,cost in COSTS.items():
                allm=metrics(trades,cost,cal_days_all)
                y23=metrics(subset_year(trades,2023),cost,cal_days_year[2023])
                y24=metrics(subset_year(trades,2024),cost,cal_days_year[2024])
                entry={"ALL":allm,"2023":y23,"2024":y24}
                if mode=="COMBINED":
                    entry["bootstrap_avg_net_95pct"]=bootstrap_expectancy(trades,cost)
                mres[cname]=entry
            pres["modes"][mode]=mres
        result["policies"][pkey]=pres

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
