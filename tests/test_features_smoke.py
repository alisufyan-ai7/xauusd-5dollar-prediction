#!/usr/bin/env python3
import csv,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def make_raw(path,mutate_future=False,gap=False):
    with path.open("w") as f:
        f.write("timestamp,open,high,low,close,volume\n")
        for i in range(320):
            minute=i+(1 if gap and i>=250 else 0)
            x=100+i*0.05
            if mutate_future and i>=301:
                x+=50
            f.write(f"{minute*60000},{x},{x+0.4},{x-0.3},{x+0.1},1\n")

with tempfile.TemporaryDirectory() as td:
    p=Path(td); raw=p/"raw.csv"; out=p/"f.csv"
    make_raw(raw)
    subprocess.run([sys.executable,str(ROOT/"scripts"/"build_features.py"),str(raw),str(out)],check=True)
    rows=list(csv.DictReader(out.open()))
    assert rows[239]["feature_complete"]=="False"
    assert rows[240]["feature_complete"]=="True"
    r=rows[300]
    assert r["feature_version"]=="V2"
    assert abs(float(r["ret_240m"])-12.0)<1e-9
    assert "rv60_percentile_240m" in r and r["rv60_percentile_240m"]!=""
    assert "slope_240m" in r and r["slope_240m"]!=""
    assert "directional_agreement_m5_m15_h1_h4" in r
    assert "current_day_range_position" in r
    assert "impulse_pullback_ratio_15m" in r

    # Future-data mutation must not change features at an earlier decision row.
    raw2=p/"raw2.csv"; out2=p/"f2.csv"
    make_raw(raw2,mutate_future=True)
    subprocess.run([sys.executable,str(ROOT/"scripts"/"build_features.py"),str(raw2),str(out2)],check=True)
    rows2=list(csv.DictReader(out2.open()))
    for key in rows[300]:
        assert rows[300][key]==rows2[300][key], (key,rows[300][key],rows2[300][key])

    # An internal M1 gap inside the 240m feature window must fail feature completeness.
    raw3=p/"raw3.csv"; out3=p/"f3.csv"
    make_raw(raw3,gap=True)
    subprocess.run([sys.executable,str(ROOT/"scripts"/"build_features.py"),str(raw3),str(out3)],check=True)
    rows3=list(csv.DictReader(out3.open()))
    assert rows3[300]["feature_complete"]=="False"

print("feature V2 smoke/leakage/gap tests passed")
