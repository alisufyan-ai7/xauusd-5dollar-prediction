#!/usr/bin/env python3
import csv,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ONE=60000

def write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(["timestamp","open","high","low","close","volume"]);w.writerows(rows)

def run_case(bid_rows,ask_rows):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);b=td/"b.csv";a=td/"a.csv";o=td/"o.csv"
        write(b,bid_rows);write(a,ask_rows)
        subprocess.run([sys.executable,str(ROOT/"scripts"/"label_exp002.py"),str(b),str(a),str(o)],check=True,capture_output=True,text=True)
        with o.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

# 61 contiguous bars: row0 is decision bar, row1 entry.
bid=[];ask=[]
for i in range(61):
    bp=100.0; ap=100.2
    bid.append([i*ONE,bp,bp+0.4,bp-0.4,bp,1])
    ask.append([i*ONE,ap,ap+0.4,ap-0.4,ap,1])
# BUY entry = 100.2, target BID=105.2. Hit at minute 3.
bid[3]=[3*ONE,100,105.3,99.8,105.0,1]
ask[3]=[3*ONE,100.2,105.5,100.0,105.2,1]
rows=run_case(bid,ask)
r=rows[0]
assert abs(float(r["buy_entry_ask"])-100.2)<1e-9
assert abs(float(r["buy_target_bid"])-105.2)<1e-9
assert r["buy_label"]=="SUCCESS"
assert r["coverage_complete"]=="True"

# SELL entry = BID 100, target ASK 95.0. Hit at minute 4.
bid=[];ask=[]
for i in range(61):
    bid.append([i*ONE,100,100.4,99.6,100,1])
    ask.append([i*ONE,100.2,100.6,99.8,100.2,1])
ask[4]=[4*ONE,100.2,100.4,94.9,95.1,1]
bid[4]=[4*ONE,100,100.2,94.7,94.9,1]
r=run_case(bid,ask)[0]
assert r["sell_label"]=="SUCCESS"
assert abs(float(r["sell_target_ask"])-95.0)<1e-9

# Same-minute target + adverse => ambiguous.
bid=[];ask=[]
for i in range(61):
    bid.append([i*ONE,100,100.4,99.6,100,1])
    ask.append([i*ONE,100.2,100.6,99.8,100.2,1])
bid[2]=[2*ONE,100,105.3,97.0,100,1]
ask[2]=[2*ONE,100.2,105.5,97.2,100.2,1]
r=run_case(bid,ask)[0]
assert r["buy_label"]=="AMBIGUOUS"

# Missing internal minute invalidates coverage.
bid=[];ask=[]
for i in list(range(31))+list(range(32,62)):
    bid.append([i*ONE,100,100.4,99.6,100,1])
    ask.append([i*ONE,100.2,100.6,99.8,100.2,1])
r=run_case(bid,ask)[0]
assert r["coverage_complete"]=="False"

print("EXP-002 label tests passed")
