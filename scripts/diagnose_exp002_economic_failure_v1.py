#!/usr/bin/env python3
"""EXP-002 economic failure diagnosis V1.

Descriptive only. Reproduces frozen EXP-002 models/cutoffs and explains why
classification ranking does not translate into positive executable expectancy.
FINAL_OOS 2025 is forbidden.
"""

import csv,json,math,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

import execution_economics_exp002_v1 as econ

SHARES=(0.10,0.05,0.025,0.01)

def load_rows_features(pairs,partition):
    rows=[]; feats=[]; xs=[]
    for pp,fp in pairs:
        for p,f in econ.iter_join(pp,fp):
            if p["partition"]=="FINAL_OOS":
                raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
            if p["partition"]!=partition or p["partition_boundary_eligible"]!="True" or f["feature_complete"]!="True":
                continue
            x=econ.xrow(f)
            if x is None: continue
            rows.append(p);feats.append(f);xs.append(x)
    return rows,feats,np.asarray(xs,dtype=np.float32)

def direction_fields(direction):
    if direction=="BUY":
        return "buy_label","buy_expiry_pnl"
    return "sell_label","sell_expiry_pnl"

def gross_from_row(p,direction):
    lab,exp=direction_fields(direction)
    v=p[lab]
    if p["coverage_complete"]!="True": return None
    if v=="SUCCESS": return 5.0
    if v in ("FAILURE","AMBIGUOUS"): return -3.0
    if v=="UNRESOLVED": return float(p[exp])
    return None

def outcome_summary(rows,mask,direction):
    lab,exp=direction_fields(direction)
    labels=[];gross=[];unres=[]
    for i,m in enumerate(mask):
        if not m: continue
        p=rows[i]
        if p["coverage_complete"]!="True": continue
        g=gross_from_row(p,direction)
        if g is None: continue
        labels.append(p[lab]);gross.append(g)
        if p[lab]=="UNRESOLVED":unres.append(float(p[exp]))
    c=Counter(labels);n=len(labels)
    def q(a,v): return None if not a else float(np.quantile(np.asarray(a,float),v))
    return {
      "n":n,
      "label_counts":dict(c),
      "label_shares":{k:(c[k]/n if n else None) for k in ("SUCCESS","FAILURE","UNRESOLVED","AMBIGUOUS")},
      "mean_gross":float(np.mean(gross)) if gross else None,
      "median_gross":float(np.median(gross)) if gross else None,
      "unresolved_mean":float(np.mean(unres)) if unres else None,
      "unresolved_median":float(np.median(unres)) if unres else None,
      "unresolved_p10":q(unres,.10),"unresolved_p25":q(unres,.25),
      "unresolved_p75":q(unres,.75),"unresolved_p90":q(unres,.90),
      "ev_identity": (
        5*(c["SUCCESS"]/n) - 3*(c["FAILURE"]/n) - 3*(c["AMBIGUOUS"]/n)
        + (c["UNRESOLVED"]/n)*(float(np.mean(unres)) if unres else 0.0)
      ) if n else None
    }

def quarter_of(ms):
    d=datetime.fromtimestamp(ms/1000,tz=timezone.utc)
    return f"{d.year}-Q{(d.month-1)//3+1}"

def session_of(f): return f["session_utc"]

def vol_bin(f):
    x=float(f["rv60_percentile_240m"])
    if x<=.33:return "LOW"
    if x<=.67:return "MID"
    return "HIGH"

def spread_bin(f):
    x=float(f["spread_percentile_240m"])
    if x<=.25:return "Q1"
    if x<=.50:return "Q2"
    if x<=.75:return "Q3"
    return "Q4"

def group_summary(rows,feats,mask,direction,grouper):
    buckets=defaultdict(lambda:[False]*len(rows))
    keys=[]
    for i,m in enumerate(mask):
        if not m:continue
        k=grouper(rows[i],feats[i])
        if k not in buckets: keys.append(k)
        buckets[k][i]=True
    return {k:outcome_summary(rows,buckets[k],direction) for k in keys}

def decile_masks(scores):
    # deterministic empirical deciles from DEVELOPMENT_TEST scores.
    qs=[float(np.quantile(scores,q)) for q in np.linspace(0,1,11)]
    out={}
    for j in range(10):
        lo,hi=qs[j],qs[j+1]
        if j==0: m=(scores>=lo)&(scores<=hi)
        else: m=(scores>lo)&(scores<=hi)
        out[f"D{j+1}"]=(m,{"lo":lo,"hi":hi})
    return out

def top10_slices(scores,cut):
    idx=np.where(scores>=cut)[0]
    vals=scores[idx]
    if not len(vals): return {}
    qs=[float(np.quantile(vals,q)) for q in np.linspace(0,1,11)]
    out={}
    for j in range(10):
        lo,hi=qs[j],qs[j+1]
        if j==0:m=(scores>=cut)&(scores>=lo)&(scores<=hi)
        else:m=(scores>=cut)&(scores>lo)&(scores<=hi)
        out[f"T10_S{j+1}"]=(m,{"lo":lo,"hi":hi})
    return out

def raw_signal_cluster(rows,mask):
    times=[int(rows[i]["decision_time_ms"]) for i,m in enumerate(mask) if m]
    times.sort()
    diffs=[(times[i]-times[i-1])/60000 for i in range(1,len(times))]
    dayc=Counter(econ.date_of(t) for t in times)
    counts=list(dayc.values())
    def share_le(x): return float(np.mean(np.asarray(diffs)<=x)) if diffs else None
    def q(v): return float(np.quantile(counts,v)) if counts else None
    return {
      "raw_signals":len(times),
      "inter_signal_share_le_1m":share_le(1),
      "inter_signal_share_le_5m":share_le(5),
      "inter_signal_share_le_15m":share_le(15),
      "inter_signal_share_le_30m":share_le(30),
      "active_days":len(dayc),
      "signals_per_active_day_p50":q(.50),
      "signals_per_active_day_p75":q(.75),
      "signals_per_active_day_p90":q(.90),
      "signals_per_active_day_p95":q(.95)
    }

def holding_summary(trades):
    if not trades:return {}
    mins=np.asarray([(t["exit_time_ms"]-t["entry_time_ms"])/60000 for t in trades],float)
    bylab=defaultdict(list);bygross=defaultdict(list)
    for t,m in zip(trades,mins):
        bylab[t["label"]].append(float(m))
        if m<=5:k="LE_5"
        elif m<=15:k="GT5_LE15"
        elif m<=30:k="GT15_LE30"
        else:k="GT30_LE60"
        bygross[k].append(t["gross"])
    return {
      "median_minutes":float(np.median(mins)),
      "p25_minutes":float(np.quantile(mins,.25)),
      "p75_minutes":float(np.quantile(mins,.75)),
      "p90_minutes":float(np.quantile(mins,.90)),
      "by_label":{k:{
          "n":len(v),"mean_minutes":float(np.mean(v)),"median_minutes":float(np.median(v))
      } for k,v in bylab.items()},
      "gross_by_holding_bin":{k:{
          "n":len(v),"mean_gross":float(np.mean(v))
      } for k,v in bygross.items()}
    }

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: diagnose_exp002_economic_failure_v1.py <out.json> <partitioned.csv> <features.csv> [...]")
    out=Path(argv[1]);pairs=list(zip(argv[2::2],argv[3::2]))

    bm=econ.fit_model(pairs,"BUY"); sm=econ.fit_model(pairs,"SELL")
    vr,vf,Xv=load_rows_features(pairs,"VALIDATION")
    dr,df,Xd=load_rows_features(pairs,"DEVELOPMENT_TEST")
    vb=bm.predict_proba(Xv)[:,1];vs=sm.predict_proba(Xv)[:,1]
    db=bm.predict_proba(Xd)[:,1];ds=sm.predict_proba(Xd)[:,1]

    cuts={}
    for share in SHARES:
        key=f"top_{share:g}"
        cuts[key]={"BUY":float(np.quantile(vb,1-share)),"SELL":float(np.quantile(vs,1-share))}

    result={"status":"PASS","experiment":"EXP-002_ECONOMIC_FAILURE_DIAGNOSIS_V1",
            "final_oos":"NOT_ACCESSED","cutoffs":cuts,"directions":{},"sequential":{}}

    for direction,scores in (("BUY",db),("SELL",ds)):
        dres={"bands":{}}
        for key,c in cuts.items():
            cut=c[direction];mask=scores>=cut
            dres["bands"][key]={
              "overall":outcome_summary(dr,mask,direction),
              "by_year":group_summary(dr,df,mask,direction,lambda p,f:str(econ.year_of(int(p["decision_time_ms"])))),
              "by_quarter":group_summary(dr,df,mask,direction,lambda p,f:quarter_of(int(p["decision_time_ms"]))),
              "by_session":group_summary(dr,df,mask,direction,lambda p,f:session_of(f)),
              "by_volatility":group_summary(dr,df,mask,direction,lambda p,f:vol_bin(f)),
              "by_spread_percentile":group_summary(dr,df,mask,direction,lambda p,f:spread_bin(f)),
              "clustering":raw_signal_cluster(dr,mask)
            }

        decs={}
        for name,(m,bounds) in decile_masks(scores).items():
            decs[name]={"bounds":bounds,"summary":outcome_summary(dr,m,direction)}
        dres["score_deciles"]=decs

        t10cut=cuts["top_0.1"][direction]
        slices={}
        for name,(m,bounds) in top10_slices(scores,t10cut).items():
            slices[name]={"bounds":bounds,"summary":outcome_summary(dr,m,direction)}
        dres["top10_score_slices"]=slices
        result["directions"][direction]=dres

    for key,c in cuts.items():
        result["sequential"][key]={}
        for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
            trades,unavail,reasons=econ.simulate(dr,db,ds,c["BUY"],c["SELL"],mode)
            # raw qualifying denominator, respecting mode semantics but before position suppression.
            raw=0
            for b,s in zip(db>=c["BUY"],ds>=c["SELL"]):
                if mode=="BUY_ONLY": raw+=int(b)
                elif mode=="SELL_ONLY": raw+=int(s)
                else: raw+=int(bool(b)^bool(s))
            result["sequential"][key][mode]={
              "raw_qualifying_signals":int(raw),
              "executed_trades":len(trades),
              "suppression_ratio":float(1-len(trades)/raw) if raw else None,
              "execution_unavailable":unavail,
              "execution_unavailable_reasons":reasons,
              "holding_time":holding_summary(trades),
              "F0":econ.metrics(trades,0.0,731),
              "F10":econ.metrics(trades,0.10,731)
            }

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","out":str(out),"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
