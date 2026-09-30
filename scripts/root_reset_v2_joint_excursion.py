#!/usr/bin/env python3
"""Root-Reset V2 joint excursion dynamic reward/risk."""

import json,sys,math
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime,timezone
import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor

import root_reset_event_driven_v1 as rr

ONE=60000
FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
GEOMS=("G50","G70","G80")
MODES=("H","B3")
QVAL={"G50":.50,"G70":.70,"G80":.80}

def year_of(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year
def date_of(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def fit_quantile(train,side,target_key,q):
    rows=[c for c in train if c["side"]==side]
    X=np.asarray([c["x"] for c in rows],dtype=np.float32)
    y=np.asarray([c[target_key] for c in rows],dtype=np.float32)
    m=HistGradientBoostingRegressor(
      loss="quantile",quantile=q,learning_rate=.05,max_iter=200,max_leaf_nodes=15,max_depth=None,
      min_samples_leaf=100,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=2)
    m.fit(X,y)
    return m

def fit_models(train):
    out={}
    for side in ("BUY","SELL"):
        out[side]={}
        for q in (.50,.70,.80):
            out[side][f"mfe_{q}"]=fit_quantile(train,side,"mfe60",q)
            out[side][f"mae_{q}"]=fit_quantile(train,side,"mae60",q)
    return out

def score(cands,models):
    for side in ("BUY","SELL"):
        rows=[c for c in cands if c["side"]==side]
        if not rows: continue
        X=np.asarray([c["x"] for c in rows],dtype=np.float32)
        md=models[side]
        preds={}
        for q in (.50,.70,.80):
            preds[f"mfe_{q}"]=np.clip(md[f"mfe_{q}"].predict(X),0,20)
            preds[f"mae_{q}"]=np.clip(md[f"mae_{q}"].predict(X),0,20)
        for i,c in enumerate(rows):
            for q in (.50,.70,.80):
                c[f"pred_mfe_{q}"]=float(preds[f"mfe_{q}"][i])
                c[f"pred_mae_{q}"]=float(preds[f"mae_{q}"][i])

def geom(c,g):
    q=QVAL[g]
    target=min(8.0,max(3.0,c[f"pred_mfe_{q}"]))
    stop=min(6.0,max(.75,c[f"pred_mae_{q}"]))
    eligible=(c["pred_mfe_0.7"]>=5.0 and
              c["pred_mae_0.5"]<=c["pred_mfe_0.5"] and
              target/stop>=1.20)
    return target,stop,eligible

def path_arrays(c):
    return c["_fav"],c["_adv"],c["_exit_close"]

def run_trade(c,g,mode):
    target,stop,eligible=geom(c,g)
    if not eligible:return None
    fav,adv,exit_close=path_arrays(c)
    be=False
    for k,(f,a) in enumerate(zip(fav,adv),1):
        if mode=="B3" and be:
            be_touch=(a>=-0.10)
            if f>=target and be_touch:return {"gross":.10,"exit_minute":k,"reason":"BE_AMBIG","target":target,"stop":stop}
            if f>=target:return {"gross":target,"exit_minute":k,"reason":"TARGET","target":target,"stop":stop}
            if be_touch:return {"gross":.10,"exit_minute":k,"reason":"BE","target":target,"stop":stop}
        else:
            if a>=stop and f>=target:return {"gross":-stop,"exit_minute":k,"reason":"STOP_AMBIG","target":target,"stop":stop}
            if a>=stop:return {"gross":-stop,"exit_minute":k,"reason":"STOP","target":target,"stop":stop}
            if f>=target:return {"gross":target,"exit_minute":k,"reason":"TARGET","target":target,"stop":stop}
            if mode=="B3" and f>=3.0:
                be=True
                if a>=-0.10:return {"gross":.10,"exit_minute":k,"reason":"BE_SAME_BAR","target":target,"stop":stop}
    return {"gross":float(exit_close),"exit_minute":60,"reason":"TIME","target":target,"stop":stop}

def enrich_paths(events,sets_by_year):
    # regenerate side paths with exact V1 semantics and retain arrays privately
    byyear=defaultdict(list)
    for c in events:byyear[c["year"]].append(c)
    for year,fs in sets_by_year.items():
        p=rr.read(fs[0]);f=rr.read(fs[1]);bid=rr.read(fs[2]);ask=rr.read(fs[3])
        ts=[int(r["timestamp"]) for r in bid]
        idxmap={int(p[i]["decision_time_ms"]):i for i in range(len(p))}
        for c in byyear.get(year,[]):
            i=idxmap[c["decision_time_ms"]]
            entry_idx=i+1
            if c["side"]=="BUY":
                entry=float(ask[entry_idx]["open"])
                fav=[float(bid[k]["high"])-entry for k in range(i+1,i+61)]
                adv=[entry-float(bid[k]["low"]) for k in range(i+1,i+61)]
                exit_close=float(bid[i+60]["close"])-entry
            else:
                entry=float(bid[entry_idx]["open"])
                fav=[entry-float(ask[k]["low"]) for k in range(i+1,i+61)]
                adv=[float(ask[k]["high"])-entry for k in range(i+1,i+61)]
                exit_close=entry-float(ask[i+60]["close"])
            c["_fav"]=fav;c["_adv"]=adv;c["_exit_close"]=float(exit_close)

def simulate(cands,g,mode):
    raw=0;busy=-1;trades=[]
    for c in sorted(cands,key=lambda z:z["decision_time_ms"]):
        target,stop,eligible=geom(c,g)
        if not eligible:continue
        raw+=1
        if c["decision_time_ms"]<busy:continue
        tr=run_trade(c,g,mode)
        if tr is None:continue
        tr.update({"entry_time_ms":c["decision_time_ms"],"side":c["side"],
                   "exit_time_ms":c["decision_time_ms"]+tr["exit_minute"]*ONE,
                   "mfe60":c["mfe60"],"mae60":c["mae60"]})
        trades.append(tr);busy=tr["exit_time_ms"]
    return raw,trades

def subset(trades,year=None,quarter=None):
    out=[]
    for t in trades:
        if year is not None and year_of(t["entry_time_ms"])!=year:continue
        if quarter is not None and quarter_of(t["entry_time_ms"])!=quarter:continue
        out.append(t)
    return out

def stats(trades,friction,days):
    if not trades:return {"trades":0}
    net=np.asarray([t["gross"]-friction for t in trades],float)
    pos=net[net>0].sum();neg=-net[net<0].sum()
    return {
      "trades":len(trades),"mean_net":float(net.mean()),
      "profit_factor":float(pos/neg) if neg>0 else None,
      "cumulative_net":float(net.sum()),
      "mean_target":float(np.mean([t["target"] for t in trades])),
      "mean_stop":float(np.mean([t["stop"] for t in trades])),
      "target_ge_5_share":float(np.mean([t["target"]>=5 for t in trades])),
      "mfe60_median":float(np.median([t["mfe60"] for t in trades])),
      "mae60_median":float(np.median([t["mae60"] for t in trades])),
      "reasons":dict(Counter(t["reason"] for t in trades))
    }

def bootstrap(trades,reps=2000,seed=10):
    by=defaultdict(list)
    for t in trades:by[date_of(t["entry_time_ms"])].append(t["gross"]-.10)
    days=sorted(by)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);vals=[];n=len(days)
    for _ in range(reps):
        s=[]
        for j in rng.integers(0,n,size=n):s.extend(by[days[j]])
        vals.append(float(np.mean(s)))
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def advance(trades):
    a=stats(trades,.10,731);y23=stats(subset(trades,2023),.10,365);y24=stats(subset(trades,2024),.10,366)
    ci=bootstrap(trades);qp=[];tot=0.0
    for y in (2023,2024):
        for q in range(1,5):
            pnl=sum(t["gross"]-.10 for t in subset(trades,quarter=f"{y}-Q{q}"));qp.append(pnl)
            if pnl>0:tot+=pnl
    share=max([v/tot for v in qp if v>0],default=0.0) if tot>0 else None
    ok=(a.get("trades",0)>=250 and y23.get("trades",0)>=75 and y24.get("trades",0)>=75 and
        y23.get("mean_net",0)>0 and y24.get("mean_net",0)>0 and (a.get("profit_factor") or 0)>1 and
        ci[0] is not None and ci[0]>0 and share is not None and share<=.40)
    return {"passed":bool(ok),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":share}

def diagnostics(rows):
    out={}
    for side in ("BUY","SELL"):
        r=[c for c in rows if c["side"]==side]
        if not r:continue
        d={}
        for key in ("mfe","mae"):
            for q in (.50,.70,.80):
                p=np.asarray([c[f"pred_{key}_{q}"] for c in r],float)
                y=np.asarray([c[f"{key}60"] for c in r],float)
                d[f"{key}_q{int(q*100)}"]={
                  "pred_mean":float(p.mean()),"realized_mean":float(y.mean()),
                  "coverage":float(np.mean(y<=p)),
                  "pearson":float(np.corrcoef(p,y)[0,1]),
                  "spearman":float(spearmanr(p,y).statistic)
                }
        out[side]=d
    return out

def main(argv):
    if len(argv)!=2+9*4:raise SystemExit("usage: root_reset_v2_joint_excursion.py <out.json> 9x <partitioned> <features> <bid> <ask>")
    out=Path(argv[1]);args=argv[2:];sets=[tuple(args[i*4:(i+1)*4]) for i in range(9)]
    setmap={y:fs for y,fs in zip(range(2016,2025),sets)}

    train=[];val=[]
    for year in range(2016,2023):
        ev=rr.generate_year(*setmap[year],year)
        for c in ev:
            if c["partition"]=="TRAIN":train.append(c)
            elif c["partition"]=="VALIDATION":val.append(c)
            elif c["partition"] in ("DEVELOPMENT_TEST","FINAL_OOS"):raise SystemExit("FORBIDDEN_EARLY_ACCESS")
    models=fit_models(train);score(val,models);enrich_paths(val,setmap)

    policies={}
    qualifiers=[]
    for g in GEOMS:
        for m in MODES:
            raw,tr=simulate(val,g,m);s=stats(tr,.10,365)
            ok=(s.get("trades",0)>=100 and s.get("mean_net",0)>0 and (s.get("profit_factor") or 0)>1 and
                s.get("target_ge_5_share",0)>=.40 and s.get("mfe60_median",0)>=4.0)
            name=f"{g}-{m}"
            policies[name]={"raw_eligible":raw,"validation_f10":s,"qualifies":bool(ok)}
            if ok:qualifiers.append((name,s))

    selected=None
    if qualifiers:
        qualifiers.sort(key=lambda z:(z[1]["mean_net"],z[1]["trades"],1 if z[0].endswith("-B3") else 0,
                                      -int(z[0][1:3])),reverse=True)
        selected=qualifiers[0][0]

    result={"status":"PASS","experiment":"ROOT_RESET_V2_JOINT_EXCURSION",
            "validation_diagnostics":diagnostics(val),"validation_policies":policies,
            "selected_policy":selected,"development_test_accessed":False,"final_oos":"NOT_ACCESSED"}

    if selected is None:
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"status":"PASS","selected_policy":None,"development_test_accessed":False,"final_oos":"NOT_ACCESSED"},indent=2));return

    dev=[]
    for year in (2023,2024):
        ev=rr.generate_year(*setmap[year],year)
        for c in ev:
            if c["partition"]=="DEVELOPMENT_TEST":dev.append(c)
            elif c["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
    score(dev,models);enrich_paths(dev,setmap)
    g,m=selected.split("-")
    raw,tr=simulate(dev,g,m)
    result["development_test_accessed"]=True
    result["development_test_diagnostics"]=diagnostics(dev)
    result["development_test"]={"raw_eligible":raw,"frictions":{},"advancement":advance(tr)}
    for fn,fr in FRICTIONS.items():
        result["development_test"]["frictions"][fn]={
          "ALL":stats(tr,fr,731),"2023":stats(subset(tr,2023),fr,365),"2024":stats(subset(tr,2024),fr,366),
          "quarters":{f"{y}-Q{q}":stats(subset(tr,quarter=f"{y}-Q{q}"),fr,92) for y in (2023,2024) for q in range(1,5)}
        }
    result["passing_policies"]=[selected] if result["development_test"]["advancement"]["passed"] else []

    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","selected_policy":selected,"passing_policies":result["passing_policies"],"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
