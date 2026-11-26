#!/usr/bin/env python3
"""Validate the exact bounded D-124 provider files and write compact identities."""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone

START_MS=int(datetime(2026,6,1,tzinfo=timezone.utc).timestamp()*1000)
END_MS=int(datetime(2026,10,9,tzinfo=timezone.utc).timestamp()*1000)
CAP_RAW=350*1024*1024
EXPECTED=("XAUUSD_BID","XAUUSD_ASK","EURUSD_BID","USDJPY_BID","GBPUSD_BID","USDCAD_BID","USDSEK_BID","USDCHF_BID")
SCHEMA=["timestamp","open","high","low","close","volume"]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def validate(symbol: str,path: Path) -> dict:
    rows=0; first=None; last=None; prior=None
    with path.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        if r.fieldnames!=SCHEMA: raise SystemExit(f"STAGE3B_PROVIDER_SCHEMA:{symbol}:{r.fieldnames}")
        for row in r:
            ts=int(row["timestamp"])
            if ts<START_MS or ts>=END_MS: raise SystemExit(f"STAGE3B_PROVIDER_TIME_FENCE:{symbol}:{ts}")
            if ts%60000: raise SystemExit(f"STAGE3B_PROVIDER_OFF_GRID:{symbol}:{ts}")
            if prior is not None and ts<=prior: raise SystemExit(f"STAGE3B_PROVIDER_NONMONOTONIC:{symbol}:{ts}")
            for c in ("open","high","low","close","volume"): float(row[c])
            prior=ts; first=ts if first is None else first; last=ts; rows+=1
    if rows==0: raise SystemExit(f"STAGE3B_PROVIDER_EMPTY:{symbol}")
    return {"symbol":symbol,"path":str(path),"bytes":path.stat().st_size,"sha256":sha256(path),"rows":rows,"first_timestamp_ms":first,"last_timestamp_ms":last}

def main(argv):
    if len(argv)!=10: raise SystemExit("usage: validate_stage3b_2026_provider_files.py <out.json> SYMBOL=path x8")
    out=Path(argv[1]); pairs={}
    for spec in argv[2:]:
        if "=" not in spec: raise SystemExit("STAGE3B_PROVIDER_SPEC")
        symbol,path=spec.split("=",1)
        if symbol in pairs: raise SystemExit(f"STAGE3B_PROVIDER_DUPLICATE:{symbol}")
        pairs[symbol]=Path(path)
    if tuple(sorted(pairs))!=tuple(sorted(EXPECTED)): raise SystemExit(f"STAGE3B_PROVIDER_SYMBOL_SET:{sorted(pairs)}")
    records=[validate(symbol,pairs[symbol]) for symbol in EXPECTED]
    total=sum(x["bytes"] for x in records)
    if total>CAP_RAW: raise SystemExit(f"STAGE3B_PROVIDER_RAW_BUDGET:{total}>{CAP_RAW}")
    report={"status":"PASS","scope":"D124_BOUNDED_2026","start_ms":START_MS,"end_ms_exclusive":END_MS,"total_raw_bytes":total,"raw_bytes_cap":CAP_RAW,"files":records}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__": main(sys.argv)
