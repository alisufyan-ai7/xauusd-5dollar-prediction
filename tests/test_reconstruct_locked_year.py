#!/usr/bin/env python3
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("r",ROOT/"scripts"/"reconstruct_locked_year.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.month_bounds(2017,1)==("2017-01-01","2017-02-01")
assert m.month_bounds(2017,12)==("2017-12-01","2018-01-01")
print("chunked reconstruction date-boundary test passed")
