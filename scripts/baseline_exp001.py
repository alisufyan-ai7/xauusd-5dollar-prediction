#!/usr/bin/env python3
"""EXP-001 descriptive baselines. FINAL_OOS inputs are forbidden."""
import csv,json,math,sys
from collections import defaultdict
from pathlib import Path

ALLOWED={"TRAIN","VALIDATION","DEVELOPMENT_TEST"}

def qtile(xs,q):
    s=sorted(xs)
    if not s:return None
    pos=(len(s)-1)*q
    lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi:return s[lo]
    return s[lo]*(hi-pos)+s[hi]*(pos-lo)

def load_join(partitioned,features):
    frows={r["timestamp"]:r for r in csv.DictReader(Path(features).open(encoding="utf-8"))}
    out=[]
    with Path(partitioned).open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["partition"] not in ALLOWED: continue
            fr=frows.get(r["timestamp"])
            if not fr: continue
            if r["partition_boundary_eligible"]!="True" or r["coverage_complete"]!="True" or fr["feature_complete"]!="True":
                continue
            x=dict(r); x.update({f"f_{k}":v for k,v in fr.items()})
            out.append(x)
    return out

def add(bucket, direction, label):
    if label=="AMBIGUOUS": bucket["ambiguous"]+=1; return
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
    outp=Path(argv[1])
    pairs=list(zip(argv[2::2],argv[3::2]))
    allrows=[]
    for p,f in pairs: allrows.extend(load_join(p,f))
    if any(r["partition"]=="FINAL_OOS" for r in allrows):
        raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")

    train_rv=[float(r["f_rv_60m"]) for r in allrows if r["partition"]=="TRAIN"]
    q1,q2=qtile(train_rv,1/3),qtile(train_rv,2/3)

    def volbin(v):
        v=float(v)
        return "LOW" if v<=q1 else ("MID" if v<=q2 else "HIGH")

    unconditional=defaultdict(lambda:{"n":0,"success":0,"failure":0,"unresolved":0,"ambiguous":0})
    by_session=defaultdict(lambda:{"n":0,"success":0,"failure":0,"unresolved":0,"ambiguous":0})
    by_vol=defaultdict(lambda:{"n":0,"success":0,"failure":0,"unresolved":0,"ambiguous":0})
    by_momentum=defaultdict(lambda:{"n":0,"success":0,"failure":0,"unresolved":0,"ambiguous":0})

    for r in allrows:
        p=r["partition"]; sess=r["f_session_utc"]; vb=volbin(r["f_rv_60m"])
        mom=float(r["f_ret_60m"]); mb="UP" if mom>1 else ("DOWN" if mom<-1 else "FLAT")
        for direction,col in [("BUY","buy_label"),("SELL","sell_label")]:
            lab=r[col]
            add(unconditional[f"{p}:{direction}"],direction,lab)
            add(by_session[f"{p}:{direction}:{sess}"],direction,lab)
            add(by_vol[f"{p}:{direction}:{vb}"],direction,lab)
            add(by_momentum[f"{p}:{direction}:{mb}"],direction,lab)

    report={
      "status":"PASS",
      "final_oos":"NOT_ACCESSED",
      "eligible_complete_feature_rows":len(allrows),
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
