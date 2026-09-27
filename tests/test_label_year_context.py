#!/usr/bin/env python3
import csv,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ONE=60000

def write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["timestamp","open","high","low","close","volume"])
        w.writerows(rows)

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    primary=td/"primary.csv"
    nxt=td/"next.csv"
    out=td/"labels.csv"

    # Primary ends at minute 2; next-year context supplies minutes 3 and 4.
    write(primary,[
        [0*ONE,100,101,99,100,1],
        [1*ONE,100,101,99,100,1],
        [2*ONE,100,101,99,100,1],
    ])
    write(nxt,[
        [3*ONE,100,101,99,100,1],
        [4*ONE,100,101,99,100,1],
        [5*ONE,100,101,99,100,1],
    ])

    subprocess.run([
        sys.executable,str(ROOT/"scripts"/"label_exp001_year_context.py"),
        str(primary),str(out),str(nxt)
    ],check=True,capture_output=True,text=True)

    with out.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))

    assert len(rows)==3
    # For the final primary row, decision time is minute 3. With a 60-minute
    # default horizon this tiny fixture is still incomplete, proving context
    # rows are not emitted as primary rows.
    assert rows[-1]["timestamp"]==str(2*ONE)

print("year-context labeler smoke test passed")
