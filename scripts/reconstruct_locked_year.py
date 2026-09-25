#!/usr/bin/env python3
"""Reconstruct one locked yearly CSV from independently downloaded monthly chunks."""
import calendar, csv, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def month_bounds(year, month):
    start=f"{year:04d}-{month:02d}-01"
    if month==12:
        end=f"{year+1:04d}-01-01"
    else:
        end=f"{year:04d}-{month+1:02d}-01"
    return start,end

def main():
    if len(sys.argv) not in (3,4):
        raise SystemExit("usage: reconstruct_locked_year.py <year> <output.csv> [lock.json]")
    year=int(sys.argv[1]); out=Path(sys.argv[2])
    lock=Path(sys.argv[3]) if len(sys.argv)==4 else ROOT/"research"/"EXP-001_DATASET_LOCK.json"
    out.parent.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        chunks=[]
        for month in range(1,13):
            start,end=month_bounds(year,month)
            p=td/f"{year}-{month:02d}.csv"
            subprocess.run([
                "bash",str(ROOT/"scripts"/"download_xauusd_m1.sh"),
                start,end,str(p)
            ],check=True)
            chunks.append(p)

        header=None
        with out.open("w",encoding="utf-8",newline="") as dst:
            writer=None
            for p in chunks:
                with p.open("r",encoding="utf-8-sig",newline="") as src:
                    r=csv.reader(src)
                    h=next(r,None)
                    if h is None:
                        continue
                    if header is None:
                        header=h
                        writer=csv.writer(dst,lineterminator="\n")
                        writer.writerow(header)
                    elif h != header:
                        raise SystemExit(f"schema mismatch in {p}")
                    for row in r:
                        writer.writerow(row)

    subprocess.run([
        sys.executable,str(ROOT/"scripts"/"validate_m1.py"),str(out)
    ],check=True)
    subprocess.run([
        sys.executable,str(ROOT/"scripts"/"verify_locked_year.py"),
        str(lock),str(year),str(out)
    ],check=True)
    print(f"RECONSTRUCT_LOCK_MATCH year={year} file={out}")

if __name__=="__main__":
    main()
