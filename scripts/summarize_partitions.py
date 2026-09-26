#!/usr/bin/env python3
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

SEALED="FINAL_OOS"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main(argv):
    if len(argv) < 3:
        raise SystemExit("usage: summarize_partitions.py <out.json> <partitioned.csv> [more...]")
    out=Path(argv[1])
    paths=[Path(x) for x in argv[2:]]

    agg={}
    files=[]
    for path in paths:
        files.append({"file":str(path),"sha256":sha256(path)})
        with path.open("r",encoding="utf-8",newline="") as f:
            for r in csv.DictReader(f):
                p=r["partition"]
                if p=="OUTSIDE":
                    continue
                d=agg.setdefault(p, {
                    "rows":0,
                    "eligible_rows":0,
                    "boundary_ineligible_rows":0,
                    "buy":Counter(),
                    "sell":Counter(),
                })
                d["rows"]+=1
                eligible=r["partition_boundary_eligible"]=="True"
                if eligible:
                    d["eligible_rows"]+=1
                else:
                    d["boundary_ineligible_rows"]+=1
                # Do not inspect/report outcome distributions for sealed FINAL_OOS.
                if p != SEALED:
                    d["buy"][r["buy_label"]]+=1
                    d["sell"][r["sell_label"]]+=1

    report={"status":"PASS","sealed_partition":SEALED,"files":files,"partitions":{}}
    for p,d in agg.items():
        item={
            "rows":d["rows"],
            "eligible_rows":d["eligible_rows"],
            "boundary_ineligible_rows":d["boundary_ineligible_rows"],
        }
        if p==SEALED:
            item["outcomes"]="SEALED_NOT_SUMMARIZED"
        else:
            item["buy_counts"]=dict(d["buy"])
            item["sell_counts"]=dict(d["sell"])
        report["partitions"][p]=item

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main(sys.argv)
