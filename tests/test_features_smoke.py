#!/usr/bin/env python3
import csv,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 p=Path(td); raw=p/"raw.csv"; out=p/"f.csv"
 with raw.open("w") as f:
  f.write("timestamp,open,high,low,close,volume\n")
  for i in range(70):
   x=100+i*0.1
   f.write(f"{i*60000},{x},{x+1},{x-1},{x+0.2},1\n")
 subprocess.run([sys.executable,str(ROOT/"scripts"/"build_features.py"),str(raw),str(out)],check=True)
 rows=list(csv.DictReader(out.open()))
 assert rows[59]["feature_complete"]=="False"
 assert rows[60]["feature_complete"]=="True"
 assert abs(float(rows[60]["ret_60m"])-6.0)<1e-9
 assert rows[60]["session_utc"]=="ASIA"
print("feature smoke test passed")
