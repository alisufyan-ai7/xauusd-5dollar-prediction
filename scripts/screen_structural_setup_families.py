#!/usr/bin/env python3
"""TRAIN-only structural setup family screening for Root-Reset V3."""

import csv,json,math,sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import numpy as np

import root_reset_event_driven_v1 as rr

ONE=60000
COOLDOWN=15
FAMILIES=("A_BREAKOUT_RETEST","B_SWEEP_RECLAIM","C_IMPULSE_PULLBACK")

def read(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def year_of(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc).year

def first_hit(vals,level):
    for i,v in enumerate(vals,1):
        if v>=level:return i
    return None

def first_before(fav,adv,flevel,alevel):
    for i,(f,a) in enumerate(zip(fav,adv),1):
        if f>=flevel and a>=alevel:
            return False  # conservative same-bar ambiguity
        if f>=flevel:return True
        if a>=alevel:return False
    return False

def build_candidate(i,side,bid,ask,atr,family):
    n=len(bid)
    if i+60>=n:return None
    ts=[int(r["timestamp"]) for r in bid]
    if any(ts[k]-ts[k-1]!=ONE for k in range(i+1,i+61)):return None
    if atr[i] is None:return None

    if side=="BUY":
        entry=float(ask[i+1]["open"])
        fav30=[float(bid[k]["high"])-entry for k in range(i+1,i+31)]
        adv30=[entry-float(bid[k]["low"]) for k in range(i+1,i+31)]
        fav60=[float(bid[k]["high"])-entry for k in range(i+1,i+61)]
        adv60=[entry-float(bid[k]["low"]) for k in range(i+1,i+61)]
    else:
        entry=float(bid[i+1]["open"])
        fav30=[entry-float(ask[k]["low"]) for k in range(i+1,i+31)]
        adv30=[float(ask[k]["high"])-entry for k in range(i+1,i+31)]
        fav60=[entry-float(ask[k]["low"]) for k in range(i+1,i+61)]
        adv60=[float(ask[k]["high"])-entry for k in range(i+1,i+61)]

    mfe30=max(0.0,max(fav30));mae30=max(0.0,max(adv30))
    mfe60=max(0.0,max(fav60));mae60=max(0.0,max(adv60))
    t3=first_hit(fav60,3.0);t5=first_hit(fav60,5.0);t7=first_hit(fav60,7.0);tm3=first_hit(adv60,3.0)
    decision=ts[i]+ONE
    return {
      "family":family,"side":side,"decision_time_ms":decision,"year":year_of(decision),
      "mfe30":mfe30,"mae30":mae30,"mfe60":mfe60,"mae60":mae60,
      "hit3":int(mfe60>=3.0),"hit5":int(mfe60>=5.0),"hit7":int(mfe60>=7.0),
      "plus3_before_minus3":int(first_before(fav60,adv60,3.0,3.0)),
      "plus5_before_minus3":int(first_before(fav60,adv60,5.0,3.0)),
      "time_plus3":t3,"time_plus5":t5,"time_minus3":tm3
    }

def screen_year(bidp,askp,year):
    bid=read(bidp);ask=read(askp)
    if len(bid)!=len(ask):raise SystemExit(f"ROW_COUNT_MISMATCH:{year}")
    n=len(bid)
    ts=[int(r["timestamp"]) for r in bid]
    for i,(b,a) in enumerate(zip(bid,ask)):
        if b["timestamp"]!=a["timestamp"]:raise SystemExit(f"TS_MISMATCH:{year}:{i}")

    op=[float(r["open"]) for r in bid];hi=[float(r["high"]) for r in bid]
    lo=[float(r["low"]) for r in bid];cl=[float(r["close"]) for r in bid]
    atr=rr.precompute_atr15(ts,op,hi,lo,cl)

    out={f:[] for f in FAMILIES}
    cooldown={f:-1 for f in FAMILIES}

    # pending state per direction for A and C
    A={"BUY":None,"SELL":None}
    C={"BUY":None,"SELL":None}

    for i in range(60,n-60):
        if i>0 and ts[i]-ts[i-1]!=ONE:
            A={"BUY":None,"SELL":None};C={"BUY":None,"SELL":None}
            continue
        a=atr[i]
        if a is None or a<=0:continue
        decision=ts[i]+ONE

        # ----- Family A pending evaluation -----
        for side in ("BUY","SELL"):
            st=A[side]
            if st is not None:
                age=i-st["break_i"]
                if age>10:
                    A[side]=None
                else:
                    lvl=st["level"];sa=st["atr"]
                    if side=="BUY":
                        if cl[i] < lvl-.25*sa:
                            A[side]=None
                        elif lo[i] <= lvl+.15*sa and cl[i] >= lvl+.10*sa:
                            if decision>=cooldown["A_BREAKOUT_RETEST"]:
                                cand=build_candidate(i,"BUY",bid,ask,atr,"A_BREAKOUT_RETEST")
                                if cand:
                                    out["A_BREAKOUT_RETEST"].append(cand)
                                    cooldown["A_BREAKOUT_RETEST"]=decision+COOLDOWN*ONE
                            A[side]=None
                    else:
                        if cl[i] > lvl+.25*sa:
                            A[side]=None
                        elif hi[i] >= lvl-.15*sa and cl[i] <= lvl-.10*sa:
                            if decision>=cooldown["A_BREAKOUT_RETEST"]:
                                cand=build_candidate(i,"SELL",bid,ask,atr,"A_BREAKOUT_RETEST")
                                if cand:
                                    out["A_BREAKOUT_RETEST"].append(cand)
                                    cooldown["A_BREAKOUT_RETEST"]=decision+COOLDOWN*ONE
                            A[side]=None

        # start new A states only if direction free
        prior_hi=max(hi[i-60:i]);prior_lo=min(lo[i-60:i])
        if A["BUY"] is None and cl[i] > prior_hi+.10*a and op[i] <= prior_hi:
            A["BUY"]={"break_i":i,"level":prior_hi,"atr":a}
        if A["SELL"] is None and cl[i] < prior_lo-.10*a and op[i] >= prior_lo:
            A["SELL"]={"break_i":i,"level":prior_lo,"atr":a}

        # ----- Family B sweep-reclaim -----
        if decision>=cooldown["B_SWEEP_RECLAIM"]:
            side=None
            if lo[i] < prior_lo-.10*a and cl[i] > prior_lo+.05*a and cl[i] > op[i]:
                side="BUY"
            elif hi[i] > prior_hi+.10*a and cl[i] < prior_hi-.05*a and cl[i] < op[i]:
                side="SELL"
            if side:
                cand=build_candidate(i,side,bid,ask,atr,"B_SWEEP_RECLAIM")
                if cand:
                    out["B_SWEEP_RECLAIM"].append(cand)
                    cooldown["B_SWEEP_RECLAIM"]=decision+COOLDOWN*ONE

        # ----- Family C pending evaluation -----
        for side in ("BUY","SELL"):
            st=C[side]
            if st is not None:
                age=i-st["impulse_i"]
                if age>10:
                    C[side]=None
                else:
                    amp=st["amp"];end=st["end"]
                    if side=="BUY":
                        retr=(end-cl[i])/amp
                    else:
                        retr=(cl[i]-end)/amp
                    if retr>.60:
                        C[side]=None
                    else:
                        if .25<=retr<=.50:
                            st["pullback_seen"]=True
                        if st.get("pullback_seen") and i>st["impulse_i"]:
                            confirm=(cl[i]>hi[i-1]) if side=="BUY" else (cl[i]<lo[i-1])
                            if confirm:
                                if decision>=cooldown["C_IMPULSE_PULLBACK"]:
                                    cand=build_candidate(i,side,bid,ask,atr,"C_IMPULSE_PULLBACK")
                                    if cand:
                                        out["C_IMPULSE_PULLBACK"].append(cand)
                                        cooldown["C_IMPULSE_PULLBACK"]=decision+COOLDOWN*ONE
                                C[side]=None

        # start new C impulse if no pending same direction
        net=cl[i]-cl[i-15]
        path=sum(abs(cl[k]-cl[k-1]) for k in range(i-14,i+1))
        eff=abs(net)/max(path,1e-6)
        if abs(net)>=1.50*a and eff>=.65:
            side="BUY" if net>0 else "SELL"
            if C[side] is None:
                C[side]={"impulse_i":i,"amp":abs(net),"end":cl[i],"pullback_seen":False}

    return out

def medtime(rows,key):
    vals=[r[key] for r in rows if r[key] is not None]
    return float(np.median(vals)) if vals else None

def summarize(rows):
    if not rows:return {"candidates":0}
    mfe30=np.asarray([r["mfe30"] for r in rows],float);mae30=np.asarray([r["mae30"] for r in rows],float)
    mfe60=np.asarray([r["mfe60"] for r in rows],float);mae60=np.asarray([r["mae60"] for r in rows],float)
    return {
      "candidates":len(rows),
      "buy_count":sum(r["side"]=="BUY" for r in rows),
      "sell_count":sum(r["side"]=="SELL" for r in rows),
      "median_mfe30":float(np.median(mfe30)),"median_mae30":float(np.median(mae30)),
      "median_mfe60":float(np.median(mfe60)),"median_mae60":float(np.median(mae60)),
      "mean_mfe60":float(np.mean(mfe60)),"mean_mae60":float(np.mean(mae60)),
      "median_event_mfe_to_mae_floor_010":float(np.median(mfe60/np.maximum(mae60,.10))),
      "median_mfe_to_median_mae":float(np.median(mfe60)/max(np.median(mae60),1e-9)),
      "hit3_rate":float(np.mean([r["hit3"] for r in rows])),
      "hit5_rate":float(np.mean([r["hit5"] for r in rows])),
      "hit7_rate":float(np.mean([r["hit7"] for r in rows])),
      "plus3_before_minus3_rate":float(np.mean([r["plus3_before_minus3"] for r in rows])),
      "plus5_before_minus3_rate":float(np.mean([r["plus5_before_minus3"] for r in rows])),
      "median_time_plus3":medtime(rows,"time_plus3"),
      "median_time_plus5":medtime(rows,"time_plus5"),
      "median_time_minus3":medtime(rows,"time_minus3"),
      "year_path_edge":float(np.median(mfe60-mae60))
    }

def family_eval(rows):
    overall=summarize(rows)
    yearly={}
    edges=[]
    counts=[]
    for y in range(2016,2022):
        yr=[r for r in rows if r["year"]==y]
        s=summarize(yr);yearly[str(y)]=s
        counts.append(s.get("candidates",0))
        if s.get("candidates",0)>0:edges.append(s["year_path_edge"])
        else:edges.append(float("-inf"))
    positive_years=sum(e>0 for e in edges)
    eligible=(
      overall.get("candidates",0)>=600 and
      all(c>=60 for c in counts) and
      positive_years>=4 and
      float(np.median(edges))>0 and
      overall.get("median_mfe_to_median_mae",0)>=1.10
    )
    return {
      "overall":overall,"yearly":yearly,
      "positive_edge_years":positive_years,
      "minimum_year_path_edge":float(min(edges)),
      "median_year_path_edge":float(np.median(edges)),
      "eligible":bool(eligible)
    }

def main(argv):
    if len(argv)!=1+6*2:
        raise SystemExit("usage: screen_structural_setup_families.py 6x <bid.csv> <ask.csv>")
    args=argv[1:]
    allrows={f:[] for f in FAMILIES}
    for j,year in enumerate(range(2016,2022)):
        bidp,askp=args[j*2:(j+1)*2]
        yr=screen_year(bidp,askp,year)
        for f in FAMILIES:allrows[f].extend(yr[f])

    result={"status":"PASS","screening":"ROOT_RESET_V3_SETUP_FAMILIES","years":"2016-2021",
            "validation_accessed":False,"development_test_accessed":False,"final_oos":"NOT_ACCESSED",
            "families":{}}
    elig=[]
    for f in FAMILIES:
        e=family_eval(allrows[f]);result["families"][f]=e
        if e["eligible"]:elig.append(f)

    selected=None
    if len(elig)==1:selected=elig[0]
    elif len(elig)>1:
        def key(f):
            e=result["families"][f]
            return (e["minimum_year_path_edge"],e["median_year_path_edge"],
                    e["overall"]["plus5_before_minus3_rate"],e["overall"]["candidates"])
        selected=max(elig,key=key)
    result["selected_family"]=selected

    out=Path("data/reports/root-reset-v3/setup-family-screening.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","selected_family":selected,
                      "validation_accessed":False,"development_test_accessed":False,
                      "final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
