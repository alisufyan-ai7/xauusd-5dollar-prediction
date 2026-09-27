#!/usr/bin/env python3
"""EXP-001 Execution Economics V2 using Dukascopy BID/ASK ticks."""

import csv,json,math,sys
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

import numpy as np

SHARES=(0.10,0.05,0.025,0.01)
FRICTIONS={"F0":0.00,"F05":0.05,"F10":0.10,"F20":0.20}
ONE_MINUTE_MS=60000
HORIZON_MS=60*ONE_MINUTE_MS

def day_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()

def year_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

class TickStore:
    def __init__(self,root):
        self.root=Path(root)
        self.cache={}

    def load_day(self,date_str):
        if date_str in self.cache:return self.cache[date_str]
        p=self.root/f"xauusd-ticks-{date_str}.csv"
        if not p.exists():raise SystemExit(f"MISSING_TICK_FILE:{p}")
        ts=[];ask=[];bid=[]
        with p.open(encoding="utf-8-sig",newline="") as f:
            r=csv.DictReader(f)
            for row in r:
                ts.append(int(row["timestamp"]))
                ask.append(float(row["askPrice"]))
                bid.append(float(row["bidPrice"]))
        arr=(np.asarray(ts,dtype=np.int64),np.asarray(ask,dtype=np.float64),np.asarray(bid,dtype=np.float64))
        self.cache[date_str]=arr
        # chronological processing: keep cache bounded
        if len(self.cache)>4:
            for k in sorted(self.cache)[:-4]:
                self.cache.pop(k,None)
        return arr

    def window(self,start_ms,end_ms):
        d1=day_of(start_ms);d2=day_of(end_ms)
        parts=[self.load_day(d1)]
        if d2!=d1:parts.append(self.load_day(d2))
        ts=np.concatenate([x[0] for x in parts])
        ask=np.concatenate([x[1] for x in parts])
        bid=np.concatenate([x[2] for x in parts])
        lo=np.searchsorted(ts,start_ms,side="left")
        hi=np.searchsorted(ts,end_ms,side="right")
        return ts[lo:hi],ask[lo:hi],bid[lo:hi]

def reconstruct(store,decision_ms,direction):
    expiry=decision_ms+HORIZON_MS
    ts,ask,bid=store.window(decision_ms,expiry)
    if len(ts)==0:return {"available":False,"reason":"NO_TICKS"}
    if ts[0]-decision_ms>60000:return {"available":False,"reason":"ENTRY_DELAY_GT_60S"}
    entry_ts=int(ts[0]);entry_ask=float(ask[0]);entry_bid=float(bid[0])
    entry_spread=entry_ask-entry_bid
    if direction=="BUY":
        target=entry_ask+5.0; adverse=entry_ask-3.0
        exe=bid
        hit=(exe>=target)|(exe<=adverse)
    else:
        target=entry_bid-5.0; adverse=entry_bid+3.0
        exe=ask
        hit=(exe<=target)|(exe>=adverse)

    idx=np.flatnonzero(hit)
    if len(idx):
        j=int(idx[0]);exit_ts=int(ts[j]);exit_px=float(exe[j])
        if direction=="BUY":
            gross=exit_px-entry_ask
            outcome="TARGET" if exit_px>=target else "ADVERSE"
        else:
            gross=entry_bid-exit_px
            outcome="TARGET" if exit_px<=target else "ADVERSE"
        return {"available":True,"entry_time_ms":entry_ts,"exit_time_ms":exit_ts,
                "direction":direction,"outcome":outcome,"gross":float(gross),
                "entry_spread":float(entry_spread)}

    j=np.searchsorted(ts,expiry,side="right")-1
    if j<0:return {"available":False,"reason":"NO_EXPIRY_TICK"}
    if expiry-int(ts[j])>5000:return {"available":False,"reason":"EXPIRY_TICK_STALE_GT_5S"}
    exit_px=float(bid[j] if direction=="BUY" else ask[j])
    gross=(exit_px-entry_ask) if direction=="BUY" else (entry_bid-exit_px)
    return {"available":True,"entry_time_ms":entry_ts,"exit_time_ms":expiry,
            "direction":direction,"outcome":"EXPIRY","gross":float(gross),
            "entry_spread":float(entry_spread)}

def max_drawdown(vals):
    cum=peak=mdd=0.0
    for v in vals:
        cum+=v;peak=max(peak,cum);mdd=max(mdd,peak-cum)
    return float(mdd)

def metrics(trades,friction,calendar_days):
    if not trades:return {"trades":0}
    gross=np.asarray([t["gross"] for t in trades],dtype=float)
    net=gross-friction
    oc=defaultdict(int)
    for t in trades:oc[t["outcome"]]+=1
    pos=net[net>0].sum();neg=-net[net<0].sum()
    spreads=np.asarray([t["entry_spread"] for t in trades],dtype=float)
    active=len(set(day_of(t["entry_time_ms"]) for t in trades))
    return {
        "trades":int(len(trades)),
        "outcomes":dict(oc),
        "avg_gross":float(gross.mean()),"median_gross":float(np.median(gross)),
        "avg_net":float(net.mean()),"median_net":float(np.median(net)),
        "expectancy_R":float(net.mean()/3.0),
        "win_rate_net_positive":float((net>0).mean()),
        "profit_factor":float(pos/neg) if neg>0 else None,
        "cumulative_net":float(net.sum()),
        "max_drawdown":max_drawdown(net),
        "active_trading_days":int(active),
        "avg_trades_per_active_day":float(len(trades)/active) if active else None,
        "avg_trades_per_calendar_day":float(len(trades)/calendar_days),
        "entry_spread_mean":float(spreads.mean()),
        "entry_spread_median":float(np.median(spreads)),
        "entry_spread_p95":float(np.quantile(spreads,0.95))
    }

def bootstrap(trades,friction,reps=1000,seed=1):
    by=defaultdict(list)
    for t in trades:by[day_of(t["entry_time_ms"])].append(t["gross"]-friction)
    days=sorted(by)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);means=[];k=len(days)
    for _ in range(reps):
        picks=rng.integers(0,k,size=k);vals=[]
        for i in picks:vals.extend(by[days[i]])
        means.append(float(np.mean(vals)))
    return [float(np.quantile(means,.025)),float(np.quantile(means,.975))]

def subset(trades,year):
    return [t for t in trades if year_of(t["entry_time_ms"])==year]

def choose_direction(mode,bq,sq):
    if mode=="BUY_ONLY":return "BUY" if bq else None
    if mode=="SELL_ONLY":return "SELL" if sq else None
    if bq and sq:return None
    if bq:return "BUY"
    if sq:return "SELL"
    return None

def main(argv):
    if len(argv)!=5:
        raise SystemExit("usage: execution_economics_exp001_v2.py <candidates.csv> <cutoffs.json> <tick_dir> <out.json>")
    cand_path,cut_path,tick_dir,out_path=map(Path,argv[1:])
    cuts=json.loads(cut_path.read_text())["cutoffs"]
    candidates=[]
    with cand_path.open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            candidates.append({
                "decision":int(r["decision_time_ms"]),
                "buy":float(r["buy_score"]),"sell":float(r["sell_score"])
            })
    candidates.sort(key=lambda x:x["decision"])

    engines={}
    for s in SHARES:
        pk=f"top_{s:g}"
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            engines[(pk,mode)]={"busy_until":-1,"trades":[],"unavailable":0,"reasons":defaultdict(int)}

    store=TickStore(tick_dir)
    outcome_cache={}

    for row in candidates:
        d=row["decision"]
        for s in SHARES:
            pk=f"top_{s:g}";cut=cuts[pk]
            bq=row["buy"]>=cut["buy"];sq=row["sell"]>=cut["sell"]
            for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
                e=engines[(pk,mode)]
                if d<e["busy_until"]:continue
                direction=choose_direction(mode,bq,sq)
                if direction is None:continue
                key=(d,direction)
                if key not in outcome_cache:
                    outcome_cache[key]=reconstruct(store,d,direction)
                t=outcome_cache[key]
                if not t["available"]:
                    e["unavailable"]+=1;e["reasons"][t["reason"]]+=1
                    continue
                e["trades"].append(t)
                e["busy_until"]=t["exit_time_ms"]

    result={"status":"PASS","experiment":"EXP-001_EXECUTION_ECONOMICS_V2",
            "final_oos":"NOT_ACCESSED","frictions":FRICTIONS,"policies":{}}
    cal_all=731;cal_year={2023:365,2024:366}

    for s in SHARES:
        pk=f"top_{s:g}";result["policies"][pk]={"modes":{}}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            e=engines[(pk,mode)];tr=e["trades"];modes={}
            for fname,fr in FRICTIONS.items():
                modes[fname]={
                    "ALL":metrics(tr,fr,cal_all),
                    "2023":metrics(subset(tr,2023),fr,cal_year[2023]),
                    "2024":metrics(subset(tr,2024),fr,cal_year[2024]),
                    "bootstrap_avg_net_95pct":bootstrap(tr,fr)
                }
            result["policies"][pk]["modes"][mode]={
                "execution_unavailable":int(e["unavailable"]),
                "execution_unavailable_reasons":dict(e["reasons"]),
                "results":modes
            }

    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","out":str(out_path),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
