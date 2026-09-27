#!/usr/bin/env python3
"""Compare a freshly acquired full-history manifest to the prior canonical lock.

This is an audit/reporting tool only. It never blocks the research run.
The freshly acquired manifest is the source of truth for that run.
"""
import json, sys
from pathlib import Path

if len(sys.argv)!=4:
    raise SystemExit("usage: audit_snapshot_manifest.py <prior-lock.json> <fresh-manifest.json> <out.json>")

lock=json.loads(Path(sys.argv[1]).read_text())
fresh=json.loads(Path(sys.argv[2]).read_text())
old={int(x["year"]):x for x in lock["chunks"]}
rows=[]
for c in fresh["chunks"]:
    name=Path(c["file"]).name
    year=int(name.split("-")[1])
    p=old.get(year)
    rows.append({
        "year":year,
        "status":"MATCH" if p and p["rows"]==c["rows"] and p["sha256"]==c["sha256"] else "CHANGED",
        "prior_rows": None if not p else p["rows"],
        "prior_sha256": None if not p else p["sha256"],
        "fresh_rows": c["rows"],
        "fresh_sha256": c["sha256"],
    })

out={
    "policy":"fresh_full_snapshot_is_source_of_truth_for_this_run",
    "changed_years":[x["year"] for x in rows if x["status"]=="CHANGED"],
    "years":rows,
    "fresh_total_rows":fresh["total_rows"],
}
Path(sys.argv[3]).parent.mkdir(parents=True,exist_ok=True)
Path(sys.argv[3]).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
