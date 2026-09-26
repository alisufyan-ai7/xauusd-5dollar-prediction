#!/usr/bin/env python3
import csv,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
pf=["timestamp","decision_time_ms","reference_price","buy_label","buy_terminal_bar_offset","buy_terminal_bar_timestamp_ms","buy_mfe","buy_mae","sell_label","sell_terminal_bar_offset","sell_terminal_bar_timestamp_ms","sell_mfe","sell_mae","bars_observed","coverage_complete","partition","partition_boundary_eligible"]
ff=["timestamp","decision_time_ms","reference_price","feature_complete","ret_1m","ret_5m","ret_15m","ret_60m","range_1m","body_1m","upper_wick_1m","lower_wick_1m","range_15m","range_60m","dist_high_15m","dist_low_15m","dist_high_60m","dist_low_60m","rv_15m","rv_60m","hour_utc","weekday_utc","session_utc"]
with tempfile.TemporaryDirectory() as td:
 d=Path(td); p=d/"p.csv"; f=d/"f.csv"; o=d/"o.json"
 with p.open("w",newline="") as z:
  w=csv.DictWriter(z,fieldnames=pf);w.writeheader()
  for i,lab in enumerate(["SUCCESS","FAILURE","UNRESOLVED"]):
   r={k:"" for k in pf};r.update(timestamp=str(i),decision_time_ms=str(i),reference_price="100",buy_label=lab,sell_label=lab,bars_observed="60",coverage_complete="True",partition="TRAIN",partition_boundary_eligible="True");w.writerow(r)
 with f.open("w",newline="") as z:
  w=csv.DictWriter(z,fieldnames=ff);w.writeheader()
  for i in range(3):
   r={k:"0" for k in ff};r.update(timestamp=str(i),decision_time_ms=str(i),reference_price="100",feature_complete="True",rv_60m=str(i+1),ret_60m="0",session_utc="ASIA");w.writerow(r)
 subprocess.run([sys.executable,str(ROOT/"scripts"/"baseline_exp001.py"),str(o),str(p),str(f)],check=True)
 x=json.loads(o.read_text()); b=x["unconditional"]["TRAIN:BUY"]
 assert b["n"]==3 and b["success"]==1 and b["success_rate_all_nonambiguous"]==round(1/3,6)
 assert x["final_oos"]=="NOT_ACCESSED"
 assert x["implementation"]=="STREAMING_SQLITE_QUANTILES_V1"
print("baseline smoke test passed")
