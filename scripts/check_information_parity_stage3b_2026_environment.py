#!/usr/bin/env python3
"""Fail fast unless the exact D-124 Stage 3B runtime is reproduced."""
import importlib.metadata, json, platform
from pathlib import Path
LOCK=Path("requirements/information-parity-stage3b-2026.lock.txt"); EXPECTED_PYTHON="3.12.14"
def parse_lock(path):
    out={}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line or line.startswith("#"): continue
        if "==" not in line: raise SystemExit("STAGE3B_UNPINNED_REQUIREMENT:"+line)
        name,version=line.split("==",1); out[name.strip().lower()]=version.strip()
    return out
def main():
    expected=parse_lock(LOCK); py=platform.python_version(); mismatches=[]
    for name,want in expected.items():
        try: actual=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: actual="MISSING"
        if actual!=want: mismatches.append({"package":name,"expected":want,"actual":actual})
    report={"python":{"expected":EXPECTED_PYTHON,"actual":py},"mismatches":mismatches,"status":"PASS" if py==EXPECTED_PYTHON and not mismatches else "FAIL"}
    print(json.dumps(report,indent=2,sort_keys=True))
    if report["status"]!="PASS": raise SystemExit("STAGE3B_EXACT_ENVIRONMENT_MISMATCH")
if __name__=="__main__": main()
