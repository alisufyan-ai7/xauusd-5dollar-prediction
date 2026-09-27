#!/usr/bin/env python3
"""Memory-bounded EXP-001 descriptive baselines.

FINAL_OOS inputs are forbidden. Partition and feature CSVs are streamed in
lockstep by timestamp. TRAIN rv_60m values are stored in a temporary SQLite
file only long enough to calculate exact tertiles without retaining millions
of joined rows in RAM.
"""
import csv,json,math,sqlite3,sys,tempfile
from collections import defaultdict
from pathlib import Path

ALLOWED={"TRAIN","VALIDATION","DEVELOPMENT_TEST"}

def iter_join(partitioned,features):
    with Path(partitioned).open(encoding="utf-8",newline="") as pf, Path(features).open(encoding="utf-8",newline="") as ff:
        pr=csv.DictReader(pf); fr=csv.DictReader(ff)
        while True:
            try: p=next(pr)
            except StopIteration: p=None
            try: f=next(fr)
            except StopIteration: f=None
            if p is None and f is None: break
            if p is None or f is None:
                raise SystemExit(f"ROW_COUNT_MISMATCH partitioned={partitioned} features={features}")
            if p["timestamp"]!=f["timestamp"]:
                raise SystemExit(f"TIMESTAMP_MISMATCH partitioned={p['timestamp']} features={f['timestamp']}")
            yield p,f

def eligible(p,f):
    if p["partition"]=="FINAL_OOS":
        raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
    if p["partition"] not in ALLOWED: return False
    return p["partition_boundary_eligible"]=="True" and p["coverage_complete"]=="True" and f["feature_complete"]=="True"

def exact_quantile(conn,q):
    n=conn.execute("select count(*) from rv").fetchone()[0]
    if not n: return None
    pos=(n-1)*q
    lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    vlo=conn.execute("select v from rv order by v limit 1 offset ?",(lo,)).fetchone()[0]
    if lo==hi: return vlo
    vhi=conn.execute("select v from rv order by v limit 1 offset ?",(hi,)).fetchone()[0]
    return vlo*(hi-pos)+vhi*(pos-lo)

def add(bucket,label):
    if label=="AMBIGUOUS":
        bucket["ambiguous"]+=1
        return
    bucket["n"]+=1
    if label=="SUCCESS": bucket["success"]+=1
    elif label=="FAILURE": bucket["failure"]+=1
    elif label=="UNRESOLVED": bucket["unresolved"]+=1

def finish(d):
    out={}
    for k,v in d.items():
        x=dict(v)
        x["success_rate_all_nonambiguous"]=round(x["success"]/x["n"],6) if x["n"] else None
        resolved=x["success"]+x["failure"]
        x["success_rate_resolved"]=round(x["success"]/resolved,6) if resolved else None
        out[k]=x
    return out

def main(argv):
    if len(argv)<4 or (len(argv)-2)%2:
        raise SystemExit("usage: baseline_exp001.py <out.json> <partitioned.csv> <features.csv> [...]")
    outp=Path(argv[1]); pairs=list(zip(argv[2::2],argv[3::2]))

    # Pass 1: disk-backed exact TRAIN rv60 distribution.
    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/"rv.sqlite"
        conn=sqlite3.connect(db)
        conn.execute("create table rv(v real not null)")
        batch=[]
        for pth,fth in pairs:
            for p,f in iter_join(pth,fth):
                if not eligible(p,f): continue
                if p["partition"]=="TRAIN":
                    batch.append((float(f["rv_60m"]),))
                    if len(batch)>=10000:
                        conn.executemany("insert into rv(v) values (?)",batch); batch.clear()
        if batch: conn.executemany("insert into rv(v) values (?)",batch)
        conn.commit()
        q1,q2=exact_quantile(conn,1/3),exact_quantile(conn,2/3)
        conn.close()

    if q1 is None or q2 is None:
        raise SystemExit("NO_TRAIN_ROWS")

    def volbin(v):
        v=float(v)
        return "LOW" if v<=q1 else ("MID" if v<=q2 else "HIGH")

    empty=lambda:{"n":0,"success":0,"failure":0,"unresolved":0,"ambiguous":0}
    unconditional=defaultdict(empty)
    by_session=defaultdict(empty)
    by_vol=defaultdict(empty)
    by_momentum=defaultdict(empty)
    eligible_count=0

    # Pass 2: streaming aggregation only; no joined-row retention.
    for pth,fth in pairs:
        for p,f in iter_join(pth,fth):
            if not eligible(p,f): continue
            eligible_count+=1
            part=p["partition"]; sess=f["session_utc"]; vb=volbin(f["rv_60m"])
            mom=float(f["ret_60m"]); mb="UP" if mom>1 else ("DOWN" if mom<-1 else "FLAT")
            for direction,col in (("BUY","buy_label"),("SELL","sell_label")):
                lab=p[col]
                add(unconditional[f"{part}:{direction}"],lab)
                add(by_session[f"{part}:{direction}:{sess}"],lab)
                add(by_vol[f"{part}:{direction}:{vb}"],lab)
                add(by_momentum[f"{part}:{direction}:{mb}"],lab)

    report={
      "status":"PASS",
      "implementation":"STREAMING_SQLITE_QUANTILES_V1",
      "final_oos":"NOT_ACCESSED",
      "eligible_complete_feature_rows":eligible_count,
      "train_rv60_tertiles":{"q33":q1,"q67":q2},
      "unconditional":finish(unconditional),
      "by_session":finish(by_session),
      "by_volatility":finish(by_vol),
      "by_60m_momentum":finish(by_momentum),
    }
    outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__": main(sys.argv)
