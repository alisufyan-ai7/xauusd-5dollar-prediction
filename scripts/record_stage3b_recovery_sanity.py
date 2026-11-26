#!/usr/bin/env python3
"""Record compact identity for the D-134 XAUUSD BID transport sanity file."""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
START=int(datetime(2026,6,1,tzinfo=timezone.utc).timestamp()*1000)
END=int(datetime(2026,6,2,tzinfo=timezone.utc).timestamp()*1000)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def main(argv):
    if len(argv)!=3: raise SystemExit("usage: record_stage3b_recovery_sanity.py <csv> <out.json>")
    path=Path(argv[1]); rows=0; first=None; last=None
    with path.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        if r.fieldnames!=["timestamp","open","high","low","close","volume"]: raise SystemExit("RECOVERY_SANITY_SCHEMA")
        prior=None
        for row in r:
            ts=int(row["timestamp"])
            if ts<START or ts>=END or ts%60000: raise SystemExit(f"RECOVERY_SANITY_TIME_FENCE:{ts}")
            if prior is not None and ts<=prior: raise SystemExit("RECOVERY_SANITY_NONMONOTONIC")
            prior=ts; first=ts if first is None else first; last=ts; rows+=1
    if rows==0: raise SystemExit("RECOVERY_SANITY_EMPTY")
    obj={"status":"PASS","symbol":"XAUUSD_BID","window_utc_half_open":["2026-06-01T00:00:00Z","2026-06-02T00:00:00Z"],
         "rows":rows,"bytes":path.stat().st_size,"sha256":sha(path),"first_timestamp_ms":first,"last_timestamp_ms":last}
    Path(argv[2]).parent.mkdir(parents=True,exist_ok=True); Path(argv[2]).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print(json.dumps(obj,indent=2,sort_keys=True))
if __name__=="__main__": main(sys.argv)
