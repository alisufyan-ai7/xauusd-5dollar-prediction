#!/usr/bin/env python3
import csv,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ONE=60000

def write(p,rows):
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(["timestamp","open","high","low","close","volume"]);w.writerows(rows)

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    b=td/"b.csv";a=td/"a.csv";ob=td/"ob.csv";oa=td/"oa.csv"
    # BID missing minute 1, ASK missing minute 2, both absent minute 3.
    write(b,[
      [0,100,101,99,100,1],
      [2*ONE,100.1,100.2,100.0,100.1,1],
      [4*ONE,102,103,101,102,1],
    ])
    write(a,[
      [0,100.2,101.2,99.2,100.2,1],
      [1*ONE,100.3,100.5,100.1,100.3,1],
      [4*ONE,102.2,103.2,101.2,102.2,1],
    ])
    subprocess.run([sys.executable,str(ROOT/"scripts"/"synchronize_exp002_m1.py"),str(b),str(a),str(ob),str(oa)],check=True)
    with ob.open(newline="",encoding="utf-8") as f: br=list(csv.DictReader(f))
    with oa.open(newline="",encoding="utf-8") as f: ar=list(csv.DictReader(f))
    assert [int(x["timestamp"]) for x in br]==[0,ONE,2*ONE,4*ONE]
    assert [int(x["timestamp"]) for x in ar]==[0,ONE,2*ONE,4*ONE]
    assert br[1]["volume"]=="0" and float(br[1]["close"])==100.0
    assert ar[2]["volume"]=="0" and float(ar[2]["close"])==100.3
    # Minute 3 absent on both sides must remain absent.
    assert 3*ONE not in [int(x["timestamp"]) for x in br]
print("EXP-002 synchronization tests passed")
