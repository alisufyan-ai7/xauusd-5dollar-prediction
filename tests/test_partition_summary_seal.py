#!/usr/bin/env python3
import csv,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

fields=["timestamp","decision_time_ms","reference_price","buy_label","buy_terminal_bar_offset","buy_terminal_bar_timestamp_ms","buy_mfe","buy_mae","sell_label","sell_terminal_bar_offset","sell_terminal_bar_timestamp_ms","sell_mfe","sell_mae","bars_observed","coverage_complete","partition","partition_boundary_eligible"]

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    p=td/"x.csv"
    out=td/"summary.json"
    rows=[
      dict.fromkeys(fields,""),
      dict.fromkeys(fields,""),
    ]
    rows[0].update({"partition":"TRAIN","partition_boundary_eligible":"True","buy_label":"SUCCESS","sell_label":"FAILURE"})
    rows[1].update({"partition":"FINAL_OOS","partition_boundary_eligible":"True","buy_label":"SUCCESS","sell_label":"SUCCESS"})
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    subprocess.run([sys.executable,str(ROOT/"scripts"/"summarize_partitions.py"),str(out),str(p)],check=True)
    data=json.loads(out.read_text())
    assert data["partitions"]["TRAIN"]["buy_counts"]["SUCCESS"]==1
    assert data["partitions"]["FINAL_OOS"]["outcomes"]=="SEALED_NOT_SUMMARIZED"
    assert "buy_counts" not in data["partitions"]["FINAL_OOS"]

print("partition summary sealing test passed")
