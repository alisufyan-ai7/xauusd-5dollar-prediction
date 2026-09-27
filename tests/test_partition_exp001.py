#!/usr/bin/env python3
import importlib.util,sys,datetime as dt
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"scripts"/"partition_exp001.py"
spec=importlib.util.spec_from_file_location("partition_exp001",p)
m=importlib.util.module_from_spec(spec)
sys.modules["partition_exp001"]=m
spec.loader.exec_module(m)

def t(s):
    return int(dt.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)

cases=[
    ("2016-01-01T00:00:00Z","TRAIN",True),
    ("2021-12-31T22:59:59Z","TRAIN",True),
    ("2021-12-31T23:00:01Z","TRAIN",False),
    ("2022-01-01T00:00:00Z","VALIDATION",True),
    ("2022-12-31T23:30:00Z","VALIDATION",False),
    ("2023-01-01T00:00:00Z","DEVELOPMENT_TEST",True),
    ("2024-12-31T23:30:00Z","DEVELOPMENT_TEST",False),
    ("2025-01-01T00:00:00Z","FINAL_OOS",True),
    ("2025-12-31T23:30:00Z","FINAL_OOS",False),
    ("2026-01-01T00:00:00Z",None,False),
]
for s,name,eligible in cases:
    got=m.assign(t(s))
    assert got==(name,eligible),(s,got,(name,eligible))

print("partition boundary tests passed")
