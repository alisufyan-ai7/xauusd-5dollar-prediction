#!/usr/bin/env python3
"""Join frozen D-116 source intervals to bounded causal market state."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np,pandas as pd

TEACHER_SHA="8089c9d9d4ade14bf1cd037331d298e787276657a2056daf0bbb2c84325433cd"
FEATURE_SHA="44a73f70a51f3c364ef53c5dc6353443e348e0a86bc9142fa6b8919fbe986104"
TEACHER_START=pd.Timestamp("2026-07-06T00:00:00Z").value//1_000_000
TEACHER_END=pd.Timestamp("2026-10-09T00:00:00Z").value//1_000_000

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def asof_pos(arr,t):
    i=int(np.searchsorted(arr,t,side="right")-1)
    return i if i>=0 else None
def read_table(path,time_col):
    df=pd.read_csv(path)
    arr=df[time_col].to_numpy(np.int64)
    if len(arr)>1 and np.any(np.diff(arr)<=0): raise SystemExit(f"STAGE3B_DATASET_NONMONOTONIC:{path}")
    return df,arr

def main(argv):
    if len(argv)!=7: raise SystemExit("usage: build_stage3b_2026_dataset.py <layer-dir> <dxy.csv> <teacher.csv> <feature.json> <out.csv.gz> <report.json>")
    layer=Path(argv[1]); dxy_path=Path(argv[2]); teacher_path=Path(argv[3]); spec_path=Path(argv[4]); out_path=Path(argv[5]); report_path=Path(argv[6])
    if sha(teacher_path)!=TEACHER_SHA: raise SystemExit("STAGE3B_TEACHER_SHA")
    if sha(spec_path)!=FEATURE_SHA: raise SystemExit("STAGE3B_FEATURE_SHA")
    spec=json.loads(spec_path.read_text()); defs=spec["features"]
    m1,m1t=read_table(layer/"xauusd_m1_market_state.csv.gz","decision_time_ms")
    structural,st=read_table(layer/"xauusd_structural_state.csv.gz","decision_time_ms")
    decision,dit=read_table(layer/"decision_index.csv.gz","decision_time_ms")
    macro,mat=read_table(layer/"macro_event_state.csv.gz","decision_time_ms")
    tfs={}
    for name in ("m3","m5","m15","m30","h1","h4","d1","w1"):
        tfs[name]=read_table(layer/f"xauusd_{name}.csv.gz","available_time_ms")
    dxy,dxt=read_table(dxy_path,"dxy_available_time_ms")
    teacher=pd.read_csv(teacher_path,dtype=str,keep_default_na=False)
    eligible=teacher[teacher["primary_task_a_eligible"].str.lower()=="true"].copy()
    if len(eligible)!=250: raise SystemExit(f"STAGE3B_ELIGIBLE_COUNT:{len(eligible)}")
    rows=[]
    for _,ev in eligible.iterrows():
        start=int(pd.Timestamp(ev["interval_start_utc"]).value//1_000_000); end=int(pd.Timestamp(ev["interval_end_utc"]).value//1_000_000)
        if start<TEACHER_START or end>=TEACHER_END or start%60000 or end%60000: raise SystemExit(f"STAGE3B_EVENT_TIME:{ev['event_id']}")
        k=(end-start)//60000+1
        if k!=int(ev["interval_width_minutes"]) or not 1<=k<=5: raise SystemExit(f"STAGE3B_INTERVAL:{ev['event_id']}")
        for j in range(k):
            t=start+j*60000
            mi=asof_pos(m1t,t)
            if mi is None: raise SystemExit(f"STAGE3B_NO_XAU_STATE:{ev['event_id']}:{t}")
            si=asof_pos(st,t); di=asof_pos(dit,t); mai=asof_pos(mat,t)
            if None in (si,di,mai): raise SystemExit(f"STAGE3B_NO_ALIGNED_STATE:{ev['event_id']}:{t}")
            if not (int(st[si])==int(m1t[mi])==int(dit[di])==int(mat[mai])): raise SystemExit(f"STAGE3B_STATE_KEY_MISMATCH:{ev['event_id']}:{t}")
            dpi=asof_pos(dxt,t)
            dxy_ok=dpi is not None and 0 <= (t-int(dxt[dpi]))/60000 <= 5
            rec={"event_id":ev["event_id"],"source_date":ev["source_date"],"event_type":ev["event_type"],"direction":ev["direction"],"provenance_class":ev["provenance_class"],"evidence_grade":ev["evidence_grade"],"timing_class":ev["timing_class"],"interval_width_minutes":int(ev["interval_width_minutes"]),"reject_reason":ev["reject_reason"],"candidate_minute_ms":t,"candidate_minute_utc":pd.to_datetime(t,unit="ms",utc=True).isoformat(),"interval_weight":1.0/k,"task_a_label":1 if ev["event_type"].startswith("COMMIT_") else 0,"task_b_label":(1 if ev["direction"]=="LONG" else 0) if ev["event_type"].startswith("COMMIT_") else np.nan,"market_row_key":int(m1t[mi]),"xauusd_state_age_minutes":(t-int(m1t[mi]))/60000}
            tfpos={name:asof_pos(arr,t) for name,(df,arr) in tfs.items()}
            for fd in defs:
                name=fd["name"]; prefix,field=name.split(".",1)
                if prefix=="xauusd_m1_market_state": val=m1.iloc[mi].get(field,np.nan)
                elif prefix=="xauusd_structural_state": val=structural.iloc[si].get(field,np.nan)
                elif prefix=="decision_index": val=decision.iloc[di].get(field,np.nan)
                elif prefix=="macro_event_state": val=macro.iloc[mai].get(field,np.nan)
                elif prefix=="synthetic_dxy_m1": val=dxy.iloc[dpi].get(field,np.nan) if dxy_ok else np.nan
                elif prefix.startswith("xauusd_"):
                    tf=prefix.removeprefix("xauusd_"); pos=tfpos.get(tf); val=tfs[tf][0].iloc[pos].get(field,np.nan) if pos is not None else np.nan
                else: raise SystemExit(f"STAGE3B_FEATURE_PREFIX:{name}")
                rec[name]=val
            rows.append(rec)
    out=pd.DataFrame(rows)
    if len(out)!=343 or out["event_id"].nunique()!=250: raise SystemExit(f"STAGE3B_CANDIDATE_COUNTS:{len(out)}:{out['event_id'].nunique()}")
    if abs(out.groupby("event_id")["interval_weight"].sum().sub(1).abs().max())>1e-12: raise SystemExit("STAGE3B_EVENT_WEIGHT")
    if out["source_date"].nunique()!=39: raise SystemExit("STAGE3B_SOURCE_DATES")
    out_path.parent.mkdir(parents=True,exist_ok=True); out.to_csv(out_path,index=False,compression="gzip")
    feature_names=[x["name"] for x in defs]
    missing={c:float(out[c].isna().mean() if out[c].dtype.kind!="O" else out[c].replace("",np.nan).isna().mean()) for c in feature_names}
    report={"status":"PASS","candidate_rows":len(out),"events":int(out["event_id"].nunique()),"source_dates":int(out["source_date"].nunique()),"act_events":int(out.loc[out.task_a_label==1,"event_id"].nunique()),"p3_events":int(out.loc[out.task_a_label==0,"event_id"].nunique()),"max_xauusd_state_age_minutes":float(out["xauusd_state_age_minutes"].max()),"dataset_sha256":sha(out_path),"missing_share_by_feature":missing,"macro_schedule_available_unique":sorted(pd.to_numeric(out["macro_event_state.macro_schedule_available"],errors="coerce").dropna().unique().tolist())}
    report_path.parent.mkdir(parents=True,exist_ok=True); report_path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="missing_share_by_feature"},indent=2,sort_keys=True))
if __name__=="__main__": main(sys.argv)
