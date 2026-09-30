#!/usr/bin/env python3
"""Validation-only excursion calibration diagnosis for Root-Reset V2."""

import json,sys,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr

import root_reset_event_driven_v1 as rr
import root_reset_v2_joint_excursion as v2

QS=(.01,.05,.10,.25,.50,.75,.90,.95,.99,1.0)

def qdict(vals):
    a=np.asarray(vals,float)
    return {str(q):float(np.quantile(a,q)) for q in QS}

def safe_ratio(a,b):
    if b is None or abs(b)<1e-12:return None
    return float(a/b)

def decile_report(pred,real):
    pred=np.asarray(pred,float);real=np.asarray(real,float)
    edges=np.quantile(pred,np.linspace(0,1,11))
    out={}
    ratios=[]
    for i in range(10):
        lo,hi=edges[i],edges[i+1]
        mask=(pred>=lo)&((pred<=hi) if i==9 else (pred<hi))
        p=pred[mask];r=real[mask]
        if len(p)==0:
            out[f"D{i+1}"]={"n":0};continue
        pm=float(np.mean(p));pmed=float(np.median(p))
        rm=float(np.mean(r));rmed=float(np.median(r))
        ratio_med=safe_ratio(rmed,pmed)
        if ratio_med is not None:ratios.append(ratio_med)
        out[f"D{i+1}"]={
          "n":int(len(p)),
          "predicted_mean":pm,"predicted_median":pmed,
          "realized_mean":rm,"realized_median":rmed,
          "realized_p25":float(np.quantile(r,.25)),
          "realized_p50":rmed,
          "realized_p75":float(np.quantile(r,.75)),
          "ratio_realized_median_to_predicted_median":ratio_med,
          "ratio_realized_mean_to_predicted_mean":safe_ratio(rm,pm),
          "median_overprediction":float(pmed-rmed),
          "mean_overprediction":float(pm-rm)
        }
    return out,ratios

def shrinkage_report(pred,real,ratios):
    arr=np.asarray(ratios,float)
    factors={
      "S50":float(np.quantile(arr,.50)),
      "S25":float(np.quantile(arr,.25)),
      "S10":float(np.quantile(arr,.10)),
    }
    out={}
    pred=np.asarray(pred,float);real=np.asarray(real,float)
    for name,s in factors.items():
        cal=np.maximum(0,pred*s)
        diff=real-cal
        out[name]={
          "factor":s,
          "calibrated_target_quantiles":qdict(cal),
          "realized_hit_rate":float(np.mean(real>=cal)),
          "mean_realized_minus_target":float(np.mean(diff)),
          "median_realized_minus_target":float(np.median(diff))
        }
    return out

def excursion_diag(rows,key,q):
    pred=np.asarray([r[f"pred_{key}_{q}"] for r in rows],float)
    real=np.asarray([r[f"{key}60"] for r in rows],float)
    dec,ratios=decile_report(pred,real)
    d={
      "predicted_quantiles":qdict(pred),
      "deciles":dec,
      "pearson":float(np.corrcoef(pred,real)[0,1]),
      "spearman":float(spearmanr(pred,real).statistic),
      "coverage_realized_le_predicted":float(np.mean(real<=pred))
    }
    if key=="mfe" and q in (.70,.80):
        d["shrinkage_candidates"]=shrinkage_report(pred,real,ratios)
    return d

def first_hit(fav,adv,target,stop):
    for i,(f,a) in enumerate(zip(fav,adv),1):
        if f>=target and a>=stop:return "STOP_AMBIG",i
        if a>=stop:return "STOP",i
        if f>=target:return "TARGET",i
    return "NONE",60

def risk_anchor_report(rows,anchor_key):
    vals=[];mae=[];survivor_mfe=[];hits=0
    for r in rows:
        if anchor_key=="mae_q50":a=r["pred_mae_0.5"]
        elif anchor_key=="mae_q70":a=r["pred_mae_0.7"]
        else:a=r["structure_stop"]
        a=max(float(a),1e-9)
        vals.append(a);mae.append(r["mae60"])
        reason,_=first_hit(r["_fav"],r["_adv"],1e9,a)
        if reason.startswith("STOP"):hits+=1
        else:survivor_mfe.append(r["mfe60"])
    vals=np.asarray(vals,float);mae=np.asarray(mae,float)
    return {
      "median":float(np.median(vals)),
      "p75":float(np.quantile(vals,.75)),
      "p90":float(np.quantile(vals,.90)),
      "stop_hit_rate_60m":float(hits/len(rows)),
      "realized_mfe_if_stop_not_hit_first_mean":float(np.mean(survivor_mfe)) if survivor_mfe else None,
      "realized_mfe_if_stop_not_hit_first_median":float(np.median(survivor_mfe)) if survivor_mfe else None,
      "pearson_with_realized_mae":float(np.corrcoef(vals,mae)[0,1]),
      "spearman_with_realized_mae":float(spearmanr(vals,mae).statistic),
      "realized_mae_median_to_anchor_median":safe_ratio(float(np.median(mae)),float(np.median(vals)))
    }

def rr_compare(rows,shrink):
    out={}
    for anchor in ("mae_q50","structure"):
        vals=[]
        for r in rows:
            tgt=max(0,r["pred_mfe_0.7"]*shrink)
            st=r["pred_mae_0.5"] if anchor=="mae_q50" else r["structure_stop"]
            if st>0: vals.append(tgt/st)
        out[anchor]={
          "n":len(vals),
          "rr_median":float(np.median(vals)) if vals else None,
          "rr_p25":float(np.quantile(vals,.25)) if vals else None,
          "rr_p75":float(np.quantile(vals,.75)) if vals else None
        }
    return out

def main(argv):
    if len(argv)!=2+7*4:
        raise SystemExit("usage: diagnose_root_reset_v2_excursion_calibration.py <out.json> 7x <partitioned> <features> <bid> <ask>")
    out=Path(argv[1]);args=argv[2:]
    sets=[tuple(args[i*4:(i+1)*4]) for i in range(7)]
    setmap={y:fs for y,fs in zip(range(2016,2023),sets)}

    train=[];val=[]
    for year in range(2016,2023):
        ev=rr.generate_year(*setmap[year],year)
        for c in ev:
            if c["partition"]=="TRAIN":train.append(c)
            elif c["partition"]=="VALIDATION":val.append(c)
            elif c["partition"] in ("DEVELOPMENT_TEST","FINAL_OOS"):
                raise SystemExit("FORBIDDEN_PARTITION_ACCESS")

    models=v2.fit_models(train)
    v2.score(val,models)
    v2.enrich_paths(val,setmap)

    report={
      "status":"PASS",
      "diagnosis":"ROOT_RESET_V2_EXCURSION_CALIBRATION",
      "development_test_accessed":False,
      "final_oos":"NOT_ACCESSED",
      "validation_events":len(val),
      "sides":{}
    }

    for side in ("BUY","SELL"):
        rows=[r for r in val if r["side"]==side]
        sideout={}
        for key in ("mfe","mae"):
            for q in (.50,.70,.80):
                sideout[f"{key}_q{int(q*100)}"]=excursion_diag(rows,key,q)

        sideout["risk_anchors"]={
          "pred_mae_q50":risk_anchor_report(rows,"mae_q50"),
          "pred_mae_q70":risk_anchor_report(rows,"mae_q70"),
          "structure_invalidation":risk_anchor_report(rows,"structure")
        }

        s50=sideout["mfe_q70"]["shrinkage_candidates"]["S50"]["factor"]
        s25=sideout["mfe_q70"]["shrinkage_candidates"]["S25"]["factor"]
        s10=sideout["mfe_q70"]["shrinkage_candidates"]["S10"]["factor"]
        sideout["rr_comparison_calibrated_mfe_q70"]={
          "S50":rr_compare(rows,s50),
          "S25":rr_compare(rows,s25),
          "S10":rr_compare(rows,s10)
        }
        report["sides"][side]=sideout

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":"PASS",
      "validation_events":len(val),
      "development_test_accessed":False,
      "final_oos":"NOT_ACCESSED"
    },indent=2))

if __name__=="__main__":
    main(sys.argv)
