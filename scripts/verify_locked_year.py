#!/usr/bin/env python3
import csv, hashlib, json, sys
from pathlib import Path

def sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def rows(path: Path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        r=csv.reader(f)
        next(r,None)
        return sum(1 for _ in r)

if len(sys.argv)!=4:
    raise SystemExit("usage: verify_locked_year.py <lock.json> <year> <csv>")

lock=json.loads(Path(sys.argv[1]).read_text())
year=int(sys.argv[2]); path=Path(sys.argv[3])
entry=next((x for x in lock["chunks"] if x["year"]==year),None)
if not entry:
    raise SystemExit(f"year {year} absent from lock")

actual={"rows":rows(path),"sha256":sha256(path)}
expected={"rows":entry["rows"],"sha256":entry["sha256"]}
print(json.dumps({"year":year,"expected":expected,"actual":actual},indent=2,sort_keys=True))
if actual != expected:
    raise SystemExit("LOCK_MISMATCH")
print("LOCK_MATCH")
