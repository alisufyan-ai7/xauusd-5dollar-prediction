#!/usr/bin/env python3
"""Root-cause reset V1: event-driven opportunity + dynamic trade management.

2025 FINAL_OOS is forbidden.
"""

import csv,json,math,sys
from collections import deque,defaultdict,Counter
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss

import execution_economics_exp002_v1 as exp2

ONE=60000
HORIZON=60
CUSUM_H=1.0
COOLDOWN=5
STOP_RR_MIN=1.5
MAX_STOP=5.0/STOP_RR_MIN
OPP_THRESHOLDS=(0.50,0.60,0.70,0.80)
POLICIES=("M0_HOLD_TO_5","M1_BE_AT_3","M2_TAKE_3")
FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}

def read(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def year_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

def date_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()

def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def xrow(f):
    try:
        x=[float(f[k]) for k in exp2.FEATURES]
    except Exception:
        return None
    if not all(math.isfinite(v) for v in x):return None
    return x

def precompute_atr15(ts,op,hi,lo,cl):
    n=len(ts);atr=[None]*n
    block_trs=deque(maxlen=4)
    prev_ts=None
    for i in range(n):
        if i>0 and ts[i]-ts[i-1]!=ONE:
            block_trs.clear()
        decision=ts[i]+ONE
        if decision%(15*ONE)==0 and i>=15:
            contiguous=all(ts[k]-ts[k-1]==ONE for k in range(i-13,i+1)) and ts[i-14]-ts[i-15]==ONE
            if contiguous:
                bh=max(hi[i-14:i+1]);bl=min(lo[i-14:i+1]);prev=cl[i-15]
                tr=max(bh-bl,abs(bh-prev),abs(bl-prev))
                if math.isfinite(tr) and tr>0:block_trs.append(tr)
            else:
                block_trs.clear()
        if len(block_trs)==4:
            atr[i]=float(sum(block_trs)/4)
    return atr

def first_time(vals,level):
    for k,v in enumerate(vals,1):
        if v>=level:return k
    return None

def management_path(direction,entry,stop_dist,fav,adv,exit_close,policy):
    """Return gross pnl and exit minute. Conservative same-bar ordering."""
    be_active=False
    be_gross=.10
    for k,(f,a) in enumerate(zip(fav,adv),1):
        if policy=="M2_TAKE_3":
            if a>=stop_dist and f>=3.0:return -stop_dist,k,"STOP_AMBIG"
            if a>=stop_dist:return -stop_dist,k,"STOP"
            if f>=3.0:return 3.0,k,"TP3"
            continue

        # M0 / M1
        active_stop=be_gross if (policy=="M1_BE_AT_3" and be_active) else -stop_dist
        if policy=="M1_BE_AT_3" and be_active:
            # adverse excursion from entry >= -0.10 means price reached the protected stop.
            # adv is nonnegative adverse distance, so protected profitable stop is represented
            # via executable liquidation relative to entry; same-bar high/low ambiguity is conservative.
            if f>=5.0 and a>=0.0:
                # If bar reaches +5, TP is certain only if protected stop is not also reachable
                # after activation. Since any bar low can be below entry, use side-specific OHLC
                # already encoded via adv: if any adverse excursion exists, same-bar ordering unknown.
                # Conservatively allow TP5 only when no adverse move from entry in the bar.
                if a<=1e-12:return 5.0,k,"TP5"
                return .10,k,"BE_AMBIG"
            if a>=0.0:
                return .10,k,"BE"
        else:
            if a>=stop_dist and f>=5.0:return -stop_dist,k,"STOP_AMBIG"
            if a>=stop_dist:return -stop_dist,k,"STOP"
            if f>=5.0:return 5.0,k,"TP5"
            if policy=="M1_BE_AT_3" and f>=3.0:
                be_active=True
                # if same bar also traded adversely from entry, conservatively assume BE is hit after activation
                if a>0:return .10,k,"BE_SAME_BAR"

    return exit_close,60,"TIME"

def candidate_from_index(i,side,p,f,bid,ask,atr,year):
    n=len(bid)
    if i<15 or i+HORIZON>=n:return None
    if p[i]["partition_boundary_eligible"]!="True" or f[i].get("feature_complete")!="True":return None
    part=p[i]["partition"]
    if part=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
    if p[i+HORIZON]["partition"]!=part:return None
    if any(int(bid[k]["timestamp"])-int(bid[k-1]["timestamp"])!=ONE for k in range(i+1,i+HORIZON+1)):return None
    x=xrow(f[i])
    if x is None or atr[i] is None:return None

    entry_idx=i+1
    if side=="BUY":
        entry=float(ask[entry_idx]["open"])
        future_hi=[float(bid[k]["high"]) for k in range(i+1,i+HORIZON+1)]
        future_lo=[float(bid[k]["low"]) for k in range(i+1,i+HORIZON+1)]
        fav=[h-entry for h in future_hi]
        adv=[entry-l for l in future_lo]
        structure=entry-min(float(bid[k]["low"]) for k in range(i-14,i+1))
        exit_close=float(bid[i+HORIZON]["close"])-entry
    else:
        entry=float(bid[entry_idx]["open"])
        future_lo=[float(ask[k]["low"]) for k in range(i+1,i+HORIZON+1)]
        future_hi=[float(ask[k]["high"]) for k in range(i+1,i+HORIZON+1)]
        fav=[entry-l for l in future_lo]
        adv=[h-entry for h in future_hi]
        structure=max(float(ask[k]["high"]) for k in range(i-14,i+1))-entry
        exit_close=entry-float(ask[i+HORIZON]["close"])

    a=float(atr[i])
    structure_stop=structure+.25*a
    volatility_stop=1.5*a
    stop=max(structure_stop,volatility_stop)
    admissible=bool(stop>0 and stop<=MAX_STOP)

    mfe=max(fav);mae=max(adv)
    t3=first_time(fav,3.0);t5=first_time(fav,5.0);t7=first_time(fav,7.0)
    early_damage=0
    if admissible:
        reached_plus1=False
        for k in range(5):
            fs=fav[k]>=1.0
            ss=adv[k]>=stop
            if ss and fs:
                early_damage=1;break
            if ss and not reached_plus1:
                early_damage=1;break
            if fs:
                reached_plus1=True;break

    management={}
    if admissible:
        for pol in POLICIES:
            g,m,reason=management_path(side,entry,stop,fav,adv,exit_close,pol)
            management[pol]={"gross":float(g),"exit_minute":int(m),"reason":reason}

    return {
      "year":year,"partition":part,"decision_time_ms":int(p[i]["decision_time_ms"]),
      "side":side,"x":x,"atr15_proxy":a,"structure_stop":float(structure_stop),
      "volatility_stop":float(volatility_stop),"initial_stop":float(stop),
      "stop_admissible":admissible,"mfe60":float(mfe),"mae60":float(mae),
      "opportunity5":int(mfe>=5.0),"early_damage":int(early_damage),
      "time_to_mfe3":t3,"time_to_mfe5":t5,"time_to_mfe7":t7,
      "management":management
    }

def generate_year(pp,fp,bidp,askp,year):
    p=read(pp);f=read(fp);bid=read(bidp);ask=read(askp)
    if not(len(p)==len(f)==len(bid)==len(ask)):raise SystemExit("ROW_COUNT_MISMATCH")
    n=len(p)
    ts=[int(r["timestamp"]) for r in bid]
    for i in range(n):
        t=str(ts[i])
        if p[i]["timestamp"]!=t or f[i]["timestamp"]!=t or ask[i]["timestamp"]!=t:
            raise SystemExit(f"TIMESTAMP_MISMATCH:{year}:{i}")
    op=[float(r["open"]) for r in bid];hi=[float(r["high"]) for r in bid]
    lo=[float(r["low"]) for r in bid];cl=[float(r["close"]) for r in bid]
    atr=precompute_atr15(ts,op,hi,lo,cl)

    events=[];pos=0.0;neg=0.0;cool_until=-1
    for i in range(1,n):
        if ts[i]-ts[i-1]!=ONE or atr[i] is None:
            pos=neg=0.0;continue
        decision=int(p[i]["decision_time_ms"])
        if decision<cool_until:
            pos=neg=0.0;continue
        z=(cl[i]-cl[i-1])/max(atr[i],1e-6)
        pos=max(0.0,pos+z);neg=min(0.0,neg+z)
        side=None
        if pos>=CUSUM_H:side="BUY"
        elif neg<=-CUSUM_H:side="SELL"
        if side:
            cand=candidate_from_index(i,side,p,f,bid,ask,atr,year)
            if cand is not None:events.append(cand)
            pos=neg=0.0;cool_until=decision+COOLDOWN*ONE
    return events

def fit_models(train,side):
    rows=[c for c in train if c["side"]==side]
    X=np.asarray([c["x"] for c in rows],dtype=np.float32)
    y=np.asarray([c["opportunity5"] for c in rows],dtype=np.int8)
    yd=np.asarray([c["early_damage"] for c in rows],dtype=np.int8)
    if len(np.unique(y))<2 or len(np.unique(yd))<2:raise SystemExit(f"CLASS_MISSING:{side}")
    opp=HistGradientBoostingClassifier(loss="log_loss",learning_rate=.05,max_iter=200,max_leaf_nodes=15,
      max_depth=None,min_samples_leaf=100,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    risk=HistGradientBoostingClassifier(loss="log_loss",learning_rate=.05,max_iter=200,max_leaf_nodes=15,
      max_depth=None,min_samples_leaf=100,l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=1)
    opp.fit(X,y);risk.fit(X,yd)
    return opp,risk

def score(cands,models):
    for side in ("BUY","SELL"):
        rows=[c for c in cands if c["side"]==side]
        if not rows:continue
        X=np.asarray([c["x"] for c in rows],dtype=np.float32)
        opp,risk=models[side]
        po=opp.predict_proba(X)[:,1];pr=risk.predict_proba(X)[:,1]
        for c,a,b in zip(rows,po,pr):
            c["p_opportunity5"]=float(a);c["p_early_damage"]=float(b)

def risk_cutoffs(validation):
    out={}
    for side in ("BUY","SELL"):
        vals=[c["p_early_damage"] for c in validation if c["side"]==side and c["stop_admissible"]]
        if not vals:raise SystemExit(f"NO_VALIDATION_RISK_ROWS:{side}")
        out[side]=float(np.quantile(vals,.50))
    return out

def eligible(c,threshold,cuts):
    return c["stop_admissible"] and c["p_opportunity5"]>=threshold and c["p_early_damage"]<=cuts[c["side"]]

def simulate(cands,threshold,cuts,policy):
    trades=[];busy=-1;raw=0
    for c in sorted(cands,key=lambda z:z["decision_time_ms"]):
        if not eligible(c,threshold,cuts):continue
        raw+=1
        if c["decision_time_ms"]<busy:continue
        m=c["management"][policy]
        exit_ms=c["decision_time_ms"]+m["exit_minute"]*ONE
        trades.append({
          "entry_time_ms":c["decision_time_ms"],"exit_time_ms":exit_ms,
          "side":c["side"],"gross":m["gross"],"reason":m["reason"],
          "initial_stop":c["initial_stop"],"mfe60":c["mfe60"],"mae60":c["mae60"]
        })
        busy=exit_ms
    return raw,trades

def stats(trades,friction,calendar_days):
    if not trades:return {"trades":0}
    g=np.asarray([t["gross"] for t in trades],float);net=g-friction
    pos=net[net>0].sum();neg=-net[net<0].sum();reasons=Counter(t["reason"] for t in trades)
    active=len({date_of(t["entry_time_ms"]) for t in trades})
    cum=peak=dd=0.0
    for v in net:
        cum+=v;peak=max(peak,cum);dd=max(dd,peak-cum)
    return {
      "trades":len(trades),"mean_gross":float(g.mean()),"mean_net":float(net.mean()),
      "profit_factor":float(pos/neg) if neg>0 else None,"cumulative_net":float(net.sum()),
      "max_drawdown":float(dd),"active_days":active,
      "trades_per_active_day":float(len(trades)/active) if active else None,
      "trades_per_calendar_day":float(len(trades)/calendar_days),
      "reasons":dict(reasons),
      "initial_stop_median":float(np.median([t["initial_stop"] for t in trades])),
      "initial_stop_p90":float(np.quantile([t["initial_stop"] for t in trades],.90)),
      "mfe60_median":float(np.median([t["mfe60"] for t in trades])),
      "mae60_median":float(np.median([t["mae60"] for t in trades])),
    }

def subset(trades,year=None,quarter=None):
    out=[]
    for t in trades:
        if year is not None and year_of(t["entry_time_ms"])!=year:continue
        if quarter is not None and quarter_of(t["entry_time_ms"])!=quarter:continue
        out.append(t)
    return out

def bootstrap(trades,reps=2000,seed=9):
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

def advancement(trades):
    a=stats(trades,.10,731);y23=stats(subset(trades,2023),.10,365);y24=stats(subset(trades,2024),.10,366)
    ci=bootstrap(trades)
    qp=[];tot=0.0
    for y in (2023,2024):
        for q in range(1,5):
            pnl=sum(t["gross"]-.10 for t in subset(trades,quarter=f"{y}-Q{q}"));qp.append(pnl)
            if pnl>0:tot+=pnl
    share=max([v/tot for v in qp if v>0],default=0.0) if tot>0 else None
    passed=(a.get("trades",0)>=250 and y23.get("trades",0)>=75 and y24.get("trades",0)>=75 and
            y23.get("mean_net",0)>0 and y24.get("mean_net",0)>0 and (a.get("profit_factor") or 0)>1 and
            ci[0] is not None and ci[0]>0 and share is not None and share<=.40)
    return {"passed":bool(passed),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":share}

def diagnostics(cands):
    out={}
    for side in ("BUY","SELL"):
        r=[c for c in cands if c["side"]==side]
        if not r:continue
        y=np.asarray([c["opportunity5"] for c in r]);p=np.asarray([c["p_opportunity5"] for c in r])
        yd=np.asarray([c["early_damage"] for c in r]);pr=np.asarray([c["p_early_damage"] for c in r])
        out[side]={
          "events":len(r),"stop_admissible":int(sum(c["stop_admissible"] for c in r)),
          "opportunity5_rate":float(y.mean()),"opp_brier":float(np.mean((p-y)**2)),
          "opp_roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))>1 else None,
          "opp_pr_auc":float(average_precision_score(y,p)) if len(np.unique(y))>1 else None,
          "early_damage_rate":float(yd.mean()),"risk_brier":float(np.mean((pr-yd)**2)),
          "risk_roc_auc":float(roc_auc_score(yd,pr)) if len(np.unique(yd))>1 else None,
          "risk_pr_auc":float(average_precision_score(yd,pr)) if len(np.unique(yd))>1 else None,
          "initial_stop_quantiles":{str(q):float(np.quantile([c["initial_stop"] for c in r],q)) for q in (.1,.5,.9)},
          "mfe60_quantiles":{str(q):float(np.quantile([c["mfe60"] for c in r],q)) for q in (.1,.5,.9)},
          "mae60_quantiles":{str(q):float(np.quantile([c["mae60"] for c in r],q)) for q in (.1,.5,.9)},
        }
    return out

def main(argv):
    if len(argv)!=2+9*4:
        raise SystemExit("usage: root_reset_event_driven_v1.py <out.json> 9x <partitioned> <features> <bid> <ask>")
    out=Path(argv[1]);args=argv[2:]
    sets=[]
    for j in range(9):
        sets.append(tuple(args[j*4:(j+1)*4]))

    # TRAIN + VALIDATION only first.
    train=[];validation=[]
    for year,fs in zip(range(2016,2023),sets[:7]):
        ev=generate_year(*fs,year)
        for c in ev:
            if c["partition"]=="TRAIN":train.append(c)
            elif c["partition"]=="VALIDATION":validation.append(c)
            elif c["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")

    models={side:fit_models(train,side) for side in ("BUY","SELL")}
    score(validation,models)
    cuts=risk_cutoffs(validation)

    threshold_report={}
    selected=None
    for th in OPP_THRESHOLDS:
        raw,tr=simulate(validation,th,cuts,"M0_HOLD_TO_5")
        s=stats(tr,.10,365)
        threshold_report[str(th)]={"raw_qualifying":raw,"stats_f10":s}
        if selected is None and s.get("trades",0)>=100 and s.get("mean_net",0)>0:
            selected=th

    result={
      "status":"PASS","experiment":"ROOT_CAUSE_RESET_EVENT_DRIVEN_V1",
      "final_oos":"NOT_ACCESSED","train_events":len(train),"validation_events":len(validation),
      "validation_diagnostics":diagnostics(validation),"risk_q50":cuts,
      "threshold_selection":threshold_report,"selected_opportunity_threshold":selected,
    }

    if selected is None:
        result["development_test_accessed"]=False
        result["passing_policies"]=[]
        result["stop_reason"]="NO_VALIDATION_THRESHOLD_QUALIFIED"
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"status":"PASS","selected_threshold":None,"development_test_accessed":False,"final_oos":"NOT_ACCESSED"},indent=2))
        return

    # Only now access 2023-2024.
    dev=[]
    for year,fs in zip((2023,2024),sets[7:9]):
        ev=generate_year(*fs,year)
        for c in ev:
            if c["partition"]=="DEVELOPMENT_TEST":dev.append(c)
            elif c["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
    score(dev,models)
    result["development_test_accessed"]=True
    result["development_test_events"]=len(dev)
    result["development_test_diagnostics"]=diagnostics(dev)
    result["policies"]={}
    passing=[]
    for pol in POLICIES:
        raw,tr=simulate(dev,selected,cuts,pol)
        d={"raw_qualifying":raw,"executed_trades":len(tr),
           "suppression_ratio":float(1-len(tr)/raw) if raw else None,"frictions":{}}
        for fn,fr in FRICTIONS.items():
            d["frictions"][fn]={
              "ALL":stats(tr,fr,731),
              "2023":stats(subset(tr,2023),fr,365),
              "2024":stats(subset(tr,2024),fr,366),
              "quarters":{f"{y}-Q{q}":stats(subset(tr,quarter=f"{y}-Q{q}"),fr,92)
                          for y in (2023,2024) for q in range(1,5)}
            }
        d["advancement"]=advancement(tr)
        if d["advancement"]["passed"]:passing.append(pol)
        result["policies"][pol]=d
    result["passing_policies"]=passing

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","selected_threshold":selected,"passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
