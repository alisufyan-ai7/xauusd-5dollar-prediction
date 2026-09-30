#!/usr/bin/env python3
"""Validation-only gate-overlap diagnosis for Root-Reset V1."""

import json,sys
from pathlib import Path
import numpy as np

import root_reset_event_driven_v1 as rr

Q=(.01,.05,.10,.25,.50,.75,.90,.95,.99,1.0)
TH=(.10,.15,.20,.25,.30,.40,.50,.60,.70,.80)

def qdict(vals):
    a=np.asarray(vals,dtype=float)
    return {str(x):float(np.quantile(a,x)) for x in Q}

def subset_stats(rows):
    if not rows:
        return {
          "n":0,"opportunity5_rate":None,
          "mfe60_mean":None,"mfe60_median":None,
          "mae60_mean":None,"mae60_median":None
        }
    return {
      "n":len(rows),
      "opportunity5_rate":float(np.mean([r["opportunity5"] for r in rows])),
      "mfe60_mean":float(np.mean([r["mfe60"] for r in rows])),
      "mfe60_median":float(np.median([r["mfe60"] for r in rows])),
      "mae60_mean":float(np.mean([r["mae60"] for r in rows])),
      "mae60_median":float(np.median([r["mae60"] for r in rows])),
    }

def side_report(rows,cut):
    scores=np.asarray([r["p_opportunity5"] for r in rows],dtype=float)
    risks=np.asarray([r["p_early_damage"] for r in rows],dtype=float)
    stops=np.asarray([r["initial_stop"] for r in rows],dtype=float)

    admiss=[r for r in rows if r["stop_admissible"]]
    rejected=[r for r in rows if not r["stop_admissible"]]
    below=[r for r in rows if r["p_early_damage"]<=cut]
    above=[r for r in rows if r["p_early_damage"]>cut]
    adm_below=[r for r in admiss if r["p_early_damage"]<=cut]

    score_thresholds={}
    intersections={}
    for t in TH:
        opp=[r for r in rows if r["p_opportunity5"]>=t]
        opp_stop=[r for r in opp if r["stop_admissible"]]
        opp_risk=[r for r in opp if r["p_early_damage"]<=cut]
        all3=[r for r in opp if r["stop_admissible"] and r["p_early_damage"]<=cut]
        score_thresholds[str(t)]={
          "n":len(opp),
          "realized_opportunity5_rate":float(np.mean([r["opportunity5"] for r in opp])) if opp else None
        }
        intersections[str(t)]={
          "opportunity_only":len(opp),
          "stop_only":len(admiss),
          "risk_only":len(below),
          "opportunity_plus_stop":len(opp_stop),
          "opportunity_plus_risk":len(opp_risk),
          "stop_plus_risk":len(adm_below),
          "opportunity_plus_stop_plus_risk":len(all3),
          "three_way_stats":subset_stats(all3)
        }

    edges=np.quantile(scores,np.linspace(0,1,11))
    deciles={}
    for i in range(10):
        lo,hi=edges[i],edges[i+1]
        d=[r for r in rows if r["p_opportunity5"]>=lo and
           (r["p_opportunity5"]<=hi if i==9 else r["p_opportunity5"]<hi)]
        s=subset_stats(d)
        s.update({
          "score_low":float(lo),"score_high":float(hi),
          "stop_admissible_share":float(np.mean([r["stop_admissible"] for r in d])) if d else None,
          "risk_pass_share":float(np.mean([r["p_early_damage"]<=cut for r in d])) if d else None
        })
        deciles[f"D{i+1}"]=s

    return {
      "events":len(rows),
      "opportunity_score_quantiles":qdict(scores),
      "opportunity_score_thresholds":score_thresholds,
      "stop_admissibility":{
        "count":len(admiss),
        "share":float(len(admiss)/len(rows)),
        "stop_distance_quantiles":qdict(stops),
        "admissible_stats":subset_stats(admiss),
        "rejected_stats":subset_stats(rejected),
        "admissible_score_quantiles":qdict([r["p_opportunity5"] for r in admiss]),
        "rejected_score_quantiles":qdict([r["p_opportunity5"] for r in rejected])
      },
      "early_damage":{
        "risk_cutoff_q50":float(cut),
        "predicted_risk_quantiles":qdict(risks),
        "realized_rate_all":float(np.mean([r["early_damage"] for r in rows])),
        "realized_rate_stop_admissible":float(np.mean([r["early_damage"] for r in admiss])) if admiss else None,
        "below_cutoff":{"n":len(below),"realized_rate":float(np.mean([r["early_damage"] for r in below])) if below else None},
        "above_cutoff":{"n":len(above),"realized_rate":float(np.mean([r["early_damage"] for r in above])) if above else None}
      },
      "gate_intersections":intersections,
      "opportunity_score_deciles":deciles
    }

def main(argv):
    if len(argv)!=2+7*4:
        raise SystemExit("usage: diagnose_root_reset_v1_gates.py <out.json> 7x <partitioned> <features> <bid> <ask>")
    out=Path(argv[1]);args=argv[2:]
    sets=[tuple(args[i*4:(i+1)*4]) for i in range(7)]

    train=[];validation=[]
    for year,fs in zip(range(2016,2023),sets):
        ev=rr.generate_year(*fs,year)
        for c in ev:
            if c["partition"]=="TRAIN":train.append(c)
            elif c["partition"]=="VALIDATION":validation.append(c)
            elif c["partition"] in ("DEVELOPMENT_TEST","FINAL_OOS"):
                raise SystemExit(f"FORBIDDEN_PARTITION_ACCESS:{c['partition']}")

    models={side:rr.fit_models(train,side) for side in ("BUY","SELL")}
    rr.score(validation,models)
    cuts=rr.risk_cutoffs(validation)

    report={
      "status":"PASS",
      "diagnosis":"ROOT_RESET_V1_GATE_OVERLAP",
      "development_test_accessed":False,
      "final_oos":"NOT_ACCESSED",
      "train_events":len(train),
      "validation_events":len(validation),
      "risk_q50":cuts,
      "sides":{}
    }
    for side in ("BUY","SELL"):
        rows=[c for c in validation if c["side"]==side]
        report["sides"][side]=side_report(rows,cuts[side])

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":"PASS",
      "development_test_accessed":False,
      "final_oos":"NOT_ACCESSED",
      "validation_events":len(validation)
    },indent=2))

if __name__=="__main__":
    main(sys.argv)
