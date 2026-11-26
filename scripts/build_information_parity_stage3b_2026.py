#!/usr/bin/env python3
"""Build bounded June1-Oct8 2026 Information Parity state using accepted Stage2 transforms."""
from __future__ import annotations
import importlib.util, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd

START_MS=int(datetime(2026,6,1,tzinfo=timezone.utc).timestamp()*1000)
END_MS=int(datetime(2026,10,9,tzinfo=timezone.utc).timestamp()*1000)

def load_stage2():
    p=Path(__file__).with_name("build_information_parity_stage2_year.py")
    spec=importlib.util.spec_from_file_location("ip_stage2_year",p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def unavailable_macro(dtimes):
    n=len(dtimes)
    out=pd.DataFrame({"decision_time_ms":dtimes})
    out["previous_event_families"]=""; out["next_event_families"]=""
    for c in ("minutes_since_previous_event","minutes_to_next_event","events_prior_120m_count","events_next_120m_count","event_0_15m_before","event_15_60m_before","event_0_15m_after","event_15_60m_after","event_60_120m_after"):
        out[c]=np.nan
    out["macro_schedule_available"]=np.zeros(n,dtype=np.int8)
    return out

def main(argv):
    if len(argv)!=5: raise SystemExit("usage: build_information_parity_stage3b_2026.py <sync.csv> <dxy.csv> <out-dir> <report.json>")
    s2=load_stage2(); sync=Path(argv[1]); dxy_path=Path(argv[2]); out=Path(argv[3]); report_path=Path(argv[4])
    m1=s2.add_m1_transforms(s2.load_m1(sync))
    ts=m1["timestamp_ms"].to_numpy(np.int64)
    if len(ts)==0 or ts.min()<START_MS or ts.max()>=END_MS: raise SystemExit("STAGE3B_LAYER_TIME_FENCE")
    dtimes=m1["decision_time_ms"].to_numpy(np.int64)
    tf={name:s2.resample_exact(m1,rule,expected) for name,(rule,expected) in s2.TF_RULES.items()}
    tf["d1"]=s2.build_d1(tf["h1"]); tf["w1"]=s2.build_w1(tf["d1"])
    structural=s2.add_structural_state(m1,tf)
    structural=structural.merge(s2.session_state(m1),on="decision_time_ms",how="left",validate="one_to_one")
    s2.add_previous_day(structural,dtimes,tf["d1"],m1["bid_close"].to_numpy(float))
    dxy=s2.load_dxy(dxy_path); dxy_available,dxy_age=s2.dxy_alignment(dtimes,dxy)
    macro=unavailable_macro(dtimes)
    dec_dt=pd.to_datetime(dtimes,unit="ms",utc=True)
    decision=pd.DataFrame({"timestamp_ms":m1["timestamp_ms"].to_numpy(np.int64),"decision_time_ms":dtimes,"year":2026,"utc_date":dec_dt.strftime("%Y-%m-%d"),"ny_date":dec_dt.tz_convert("America/New_York").strftime("%Y-%m-%d"),"feature_ready_market":m1["core_240m_contiguous_ready"].to_numpy(np.int8),"dxy_available":dxy_available,"dxy_age_minutes":dxy_age,"macro_schedule_available":np.zeros(len(m1),dtype=np.int8),"market_state_version":"IPV1_STAGE3B_2026_BOUNDED_D124"})
    out.mkdir(parents=True,exist_ok=True); outputs={}
    def write(name,df):
        p=out/f"{name}.csv.gz"; s2.write_csv_gz(df,p); outputs[name]=str(p)
    write("xauusd_m1_market_state",m1)
    for name,df in tf.items(): write(f"xauusd_{name}",df)
    write("xauusd_structural_state",structural); write("macro_event_state",macro); write("decision_index",decision)
    report={"status":"PASS","scope":"D124_BOUNDED_2026","cold_start_ms":START_MS,"end_ms_exclusive":END_MS,"full_stage2_continuity_equivalence_claimed":False,"macro_schedule_policy":"UNAVAILABLE_FAIL_CLOSED","rows":{"xauusd_m1_market_state":len(m1),**{f"xauusd_{k}":len(v) for k,v in tf.items()},"xauusd_structural_state":len(structural),"macro_event_state":len(macro),"decision_index":len(decision),"synthetic_dxy_m1":len(dxy)},"dxy_available_share":float(decision["dxy_available"].mean()),"feature_ready_market_share":float(decision["feature_ready_market"].mean()),"first_timestamp_ms":int(ts[0]),"last_timestamp_ms":int(ts[-1]),"outputs":outputs}
    report_path.parent.mkdir(parents=True,exist_ok=True); report_path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__": main(sys.argv)
