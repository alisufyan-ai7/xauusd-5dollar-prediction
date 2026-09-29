#!/usr/bin/env python3
"""EXP-007 causal sequence model V1.

Small fixed temporal CNN over 60 causal synchronized M1 bars plus BASE48 context.
FINAL_OOS 2025 access is forbidden.
"""

import csv,json,math,sys
from collections import deque,Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    mean_absolute_error,mean_squared_error,roc_auc_score,
    average_precision_score,brier_score_loss
)

import execution_economics_exp002_v1 as exp2
import exp005_downside_first_direct_v1 as e5

FRICTIONS={"F0":0.0,"F05":0.05,"F10":0.10,"F20":0.20}
THRESHOLDS={"T0":0.00,"T25":0.25,"T50":0.50,"T75":0.75}
ARMS=("A_SEQ_DIRECT_ONLY","B_SEQ_DIRECT_EF_Q50","C_SEQ_DIRECT_EF_Q25","D_SEQ_DIRECT_EF_Q10")
BATCH=512
EPOCHS=8
SEED=7

def rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        yield from csv.DictReader(f)

def fields(direction):
    return e5.fields(direction)

def realized_gross(p,direction):
    return e5.realized_gross(p,direction)

def early_failure(p,direction):
    return e5.early_failure(p,direction)

def compact_row(p):
    keys=[
      "coverage_complete","decision_time_ms",
      "buy_label","buy_expiry_pnl","buy_terminal_bar_timestamp_ms",
      "sell_label","sell_expiry_pnl","sell_terminal_bar_timestamp_ms"
    ]
    return {k:p[k] for k in keys}

def static_x(f):
    out=[]
    try:
        for k in exp2.FEATURES:
            v=float(f[k])
            if not math.isfinite(v): return None
            out.append(v)
    except Exception:
        return None
    return np.asarray(out,dtype=np.float32)

def make_seq(buf):
    if len(buf)!=61:return None
    bs=list(buf)
    for i in range(1,61):
        if bs[i]["ts"]-bs[i-1]["ts"]!=60000:return None
    bars=bs[1:]
    scale=float(np.median([b["hi"]-b["lo"] for b in bars]))
    if not math.isfinite(scale) or scale<1e-6:scale=1e-6
    seq=np.empty((6,60),dtype=np.float32)
    prev=bs[0]["cl"]
    for j,b in enumerate(bars):
        rng=b["hi"]-b["lo"]
        upper=b["hi"]-max(b["op"],b["cl"])
        lower=min(b["op"],b["cl"])-b["lo"]
        seq[0,j]=(b["cl"]-prev)/scale
        seq[1,j]=rng/scale
        seq[2,j]=(b["cl"]-b["op"])/scale
        seq[3,j]=upper/scale
        seq[4,j]=lower/scale
        seq[5,j]=b["spread"]/scale
        prev=b["cl"]
    if not np.all(np.isfinite(seq)):return None
    return seq

def iter_samples(pp,fp,bidp,askp):
    pr=rows(pp);fr=rows(fp);br=rows(bidp);ar=rows(askp)
    buf=deque(maxlen=61)
    while True:
        try:p=next(pr)
        except StopIteration:p=None
        try:f=next(fr)
        except StopIteration:f=None
        try:b=next(br)
        except StopIteration:b=None
        try:a=next(ar)
        except StopIteration:a=None
        if p is None and f is None and b is None and a is None:break
        if None in (p,f,b,a):raise SystemExit("ROW_COUNT_MISMATCH")
        ts=p["timestamp"]
        if ts!=f["timestamp"] or ts!=b["timestamp"] or ts!=a["timestamp"]:
            raise SystemExit("TIMESTAMP_MISMATCH")
        if p["partition"]=="FINAL_OOS":raise SystemExit("FINAL_OOS_ACCESS_FORBIDDEN")
        bt={
          "ts":int(ts),"op":float(b["open"]),"hi":float(b["high"]),
          "lo":float(b["low"]),"cl":float(b["close"]),
          "spread":float(a["close"])-float(b["close"])
        }
        if bt["spread"]<0 or not math.isfinite(bt["spread"]):
            raise SystemExit("INVALID_SPREAD")
        buf.append(bt)
        if p["partition_boundary_eligible"]!="True" or p["coverage_complete"]!="True" or f["feature_complete"]!="True":
            continue
        sx=static_x(f)
        if sx is None:continue
        seq=make_seq(buf)
        if seq is None:continue
        yield p,sx,seq

def build_train(file_sets,direction):
    lab,_,_=fields(direction)
    seqs=[];stats=[];yr=[];yc=[];eligible=0
    for pp,fp,bidp,askp in file_sets:
        for p,sx,seq in iter_samples(pp,fp,bidp,askp):
            if p["partition"]!="TRAIN" or p[lab]=="AMBIGUOUS":continue
            if eligible%20==0:
                seqs.append(seq);stats.append(sx)
                yr.append(realized_gross(p,direction));yc.append(early_failure(p,direction))
            eligible+=1
    S=np.asarray(seqs,dtype=np.float32)
    X=np.asarray(stats,dtype=np.float32)
    yr=np.asarray(yr,dtype=np.float32)
    yc=np.asarray(yc,dtype=np.float32)
    med=np.median(X,axis=0).astype(np.float32)
    q25=np.quantile(X,.25,axis=0).astype(np.float32)
    q75=np.quantile(X,.75,axis=0).astype(np.float32)
    iqr=np.maximum(q75-q25,1e-6).astype(np.float32)
    X=np.clip((X-med)/iqr,-10,10).astype(np.float32)
    return S,X,yr,yc,med,iqr

class SeqNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1=nn.Conv1d(6,16,kernel_size=5,padding=2)
        self.conv2=nn.Conv1d(16,32,kernel_size=5,dilation=2,padding=4)
        self.pool=nn.AdaptiveAvgPool1d(1)
        self.fc=nn.Linear(32+len(exp2.FEATURES),32)
        self.out=nn.Linear(32,1)
    def forward(self,seq,static):
        z=torch.relu(self.conv1(seq))
        z=torch.relu(self.conv2(z))
        z=self.pool(z).squeeze(-1)
        z=torch.cat([z,static],dim=1)
        z=torch.relu(self.fc(z))
        return self.out(z).squeeze(1)

def train_model(S,X,y,task):
    torch.manual_seed(SEED);np.random.seed(SEED)
    torch.use_deterministic_algorithms(True)
    model=SeqNet()
    opt=torch.optim.Adam(model.parameters(),lr=.001,weight_decay=.0001)
    lossfn=nn.MSELoss() if task=="reg" else nn.BCEWithLogitsLoss()
    n=len(y);last=None
    model.train()
    for _ in range(EPOCHS):
        total=0.0;seen=0
        for st in range(0,n,BATCH):
            en=min(st+BATCH,n)
            seq=torch.from_numpy(S[st:en])
            static=torch.from_numpy(X[st:en])
            target=torch.from_numpy(y[st:en])
            opt.zero_grad()
            pred=model(seq,static)
            loss=lossfn(pred,target)
            loss.backward();opt.step()
            total+=float(loss.detach())*(en-st);seen+=en-st
        last=total/seen
    return model,float(last)

def infer(model,S,X,task):
    out=[]
    model.eval()
    with torch.no_grad():
        for st in range(0,len(S),2048):
            seq=torch.from_numpy(S[st:st+2048])
            static=torch.from_numpy(X[st:st+2048])
            z=model(seq,static).cpu().numpy()
            if task=="clf":z=1/(1+np.exp(-np.clip(z,-30,30)))
            out.append(z)
    return np.concatenate(out) if out else np.asarray([],dtype=float)

def collect_partition(file_sets,partition,med,iqr):
    rows_out=[];seqs=[];stats=[]
    for pp,fp,bidp,askp in file_sets:
        for p,sx,seq in iter_samples(pp,fp,bidp,askp):
            if p["partition"]!=partition:continue
            rows_out.append(compact_row(p));seqs.append(seq);stats.append(sx)
    S=np.asarray(seqs,dtype=np.float32)
    X=np.asarray(stats,dtype=np.float32)
    X=np.clip((X-med)/iqr,-10,10).astype(np.float32)
    return rows_out,S,X

def predictive_metrics(rows,direction,pred_gross,pred_net,ef):
    labels=np.asarray([realized_gross(p,direction) for p in rows],dtype=float)
    y=labels
    efr=np.asarray([early_failure(p,direction) for p in rows],dtype=int)
    corr=float(np.corrcoef(pred_gross,y)[0,1]) if len(y)>1 and np.std(pred_gross)>0 and np.std(y)>0 else None

    def fixed_band(v):
        if v<=-.50:return "LE_NEG50"
        if v<=0:return "NEG50_TO_0"
        if v<.25:return "0_TO_25"
        if v<.50:return "25_TO_50"
        if v<.75:return "50_TO_75"
        return "GE_75"

    bands={}
    for name in ("LE_NEG50","NEG50_TO_0","0_TO_25","25_TO_50","50_TO_75","GE_75"):
        m=np.asarray([fixed_band(x)==name for x in pred_net])
        bands[name]={"n":int(m.sum()),
                     "predicted_gross_mean":float(np.mean(pred_gross[m])) if m.any() else None,
                     "realized_gross_mean":float(np.mean(y[m])) if m.any() else None}

    qs=np.quantile(pred_net,np.linspace(0,1,11));decs={}
    for i in range(10):
        m=(pred_net>=qs[i])&((pred_net<=qs[i+1]) if i==9 else (pred_net<qs[i+1]))
        decs[f"D{i+1}"]={"n":int(m.sum()),
                         "predicted_net_mean":float(np.mean(pred_net[m])) if m.any() else None,
                         "realized_net_mean":float(np.mean(y[m]-.10)) if m.any() else None}

    rqs=np.quantile(ef,np.linspace(0,1,11));risk={}
    for i in range(10):
        m=(ef>=rqs[i])&((ef<=rqs[i+1]) if i==9 else (ef<rqs[i+1]))
        risk[f"D{i+1}"]={"n":int(m.sum()),
                         "predicted_risk_mean":float(np.mean(ef[m])) if m.any() else None,
                         "realized_early_failure_rate":float(np.mean(efr[m])) if m.any() else None}

    return {
      "n":int(len(y)),
      "regression":{
        "mae":float(mean_absolute_error(y,pred_gross)),
        "rmse":float(mean_squared_error(y,pred_gross)**.5),
        "predicted_gross_mean":float(np.mean(pred_gross)),
        "realized_gross_mean":float(np.mean(y)),
        "pearson":corr,
        "score_deciles":decs,
        "fixed_net_bands":bands,
      },
      "early_failure":{
        "base_rate":float(np.mean(efr)),
        "roc_auc":float(roc_auc_score(efr,ef)) if len(np.unique(efr))>1 else None,
        "pr_auc":float(average_precision_score(efr,ef)) if len(np.unique(efr))>1 else None,
        "brier":float(brier_score_loss(efr,ef)),
        "risk_deciles":risk,
      }
    }

def qualifies(v,t,name):
    return v>0 if name=="T0" else v>=t

def risk_ok(arm,risk,cuts):
    if arm=="A_SEQ_DIRECT_ONLY":return True
    if arm=="B_SEQ_DIRECT_EF_Q50":return risk<=cuts["Q50"]
    if arm=="C_SEQ_DIRECT_EF_Q25":return risk<=cuts["Q25"]
    if arm=="D_SEQ_DIRECT_EF_Q10":return risk<=cuts["Q10"]
    return False

def choose(mode,bscore,sscore,brisk,srisk,t,name,arm,bcuts,scuts):
    b=qualifies(bscore,t,name) and risk_ok(arm,brisk,bcuts)
    s=qualifies(sscore,t,name) and risk_ok(arm,srisk,scuts)
    if mode=="BUY_ONLY":return "BUY" if b else None
    if mode=="SELL_ONLY":return "SELL" if s else None
    if not b and not s:return None
    if b and not s:return "BUY"
    if s and not b:return "SELL"
    if abs(bscore-sscore)<.25:return None
    return "BUY" if bscore>sscore else "SELL"

def trade_from_row(p,direction):
    return e5.trade_from_row(p,direction)

def simulate(rows,bscore,sscore,brisk,srisk,t,name,arm,mode,bcuts,scuts):
    raw=0;busy=-1;trades=[]
    for i,p in enumerate(rows):
        d=choose(mode,bscore[i],sscore[i],brisk[i],srisk[i],t,name,arm,bcuts,scuts)
        if d is not None:raw+=1
        ts=int(p["decision_time_ms"])
        if d is None or ts<busy:continue
        tr=trade_from_row(p,d)
        if tr is None:continue
        trades.append(tr);busy=tr["exit_time_ms"]
    return raw,trades

def subset(trades,year=None,quarter=None):
    return e5.subset(trades,year=year,quarter=quarter)

def stats(trades,friction,calendar_days):
    return e5.stats(trades,friction,calendar_days)

def bootstrap(trades,reps=2000,seed=7):
    by=defaultdict(list)
    for x in trades:by[e5.date_of(x["entry_time_ms"])].append(x["gross"]-.10)
    days=sorted(by)
    if not days:return [None,None]
    rng=np.random.default_rng(seed);vals=[];n=len(days)
    for _ in range(reps):
        sample=[]
        for j in rng.integers(0,n,size=n):sample.extend(by[days[j]])
        vals.append(float(np.mean(sample)))
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def advancement(trades):
    allm=stats(trades,.10,731);m23=stats(subset(trades,2023),.10,365);m24=stats(subset(trades,2024),.10,366)
    ci=bootstrap(trades);qp=[];total=0.0
    for y in (2023,2024):
        for q in range(1,5):
            pnl=sum(x["gross"]-.10 for x in subset(trades,quarter=f"{y}-Q{q}"));qp.append(pnl)
            if pnl>0:total+=pnl
    maxshare=max([x/total for x in qp if x>0],default=0.0) if total>0 else None
    passed=(allm.get("trades",0)>=250 and m23.get("trades",0)>=75 and m24.get("trades",0)>=75 and
            m23.get("mean_net",0)>0 and m24.get("mean_net",0)>0 and
            (allm.get("profit_factor") or 0)>1 and ci[0] is not None and ci[0]>0 and
            maxshare is not None and maxshare<=.40)
    return {"passed":bool(passed),"bootstrap_95pct":ci,"positive_quarter_pnl_share_max":maxshare}

def eval_economics(rows,bscore,sscore,brisk,srisk,bcuts,scuts):
    res={}
    for arm in ARMS:
        res[arm]={}
        for name,t in THRESHOLDS.items():
            res[arm][name]={}
            for mode in ("BUY_ONLY","SELL_ONLY","COMBINED"):
                raw,trades=simulate(rows,bscore,sscore,brisk,srisk,t,name,arm,mode,bcuts,scuts)
                e={"raw_qualifying":raw,"executed_trades":len(trades),
                   "suppression_ratio":float(1-len(trades)/raw) if raw else None,
                   "frictions":{}}
                for fn,fr in FRICTIONS.items():
                    e["frictions"][fn]={
                      "ALL":stats(trades,fr,731),
                      "2023":stats(subset(trades,2023),fr,365),
                      "2024":stats(subset(trades,2024),fr,366),
                      "quarters":{f"{y}-Q{q}":stats(subset(trades,quarter=f"{y}-Q{q}"),fr,92)
                                  for y in (2023,2024) for q in range(1,5)}
                    }
                e["advancement"]=advancement(trades)
                res[arm][name][mode]=e
    return res

def main(argv):
    if len(argv)<6 or (len(argv)-2)%4:
        raise SystemExit("usage: exp007_causal_sequence_v1.py <out.json> <partitioned.csv> <base48.csv> <bid.csv> <ask.csv> [...]")
    out=Path(argv[1]);file_sets=[]
    args=argv[2:]
    for i in range(0,len(args),4):
        file_sets.append(tuple(args[i:i+4]))

    result={"status":"PASS","experiment":"EXP-007_CAUSAL_SEQUENCE_V1","final_oos":"NOT_ACCESSED",
            "sequence_shape":[6,60],"static_features":len(exp2.FEATURES),"directions":{}}
    models={};norms={}

    for d in ("BUY","SELL"):
        S,X,yr,yc,med,iqr=build_train(file_sets,d)
        reg,regloss=train_model(S,X,yr,"reg")
        clf,clfloss=train_model(S,X,yc,"clf")
        models[d]=(reg,clf);norms[d]=(med,iqr)
        result["directions"][d]={
          "train_rows":int(len(yr)),
          "train_early_failures":int(np.sum(yc)),
          "final_regression_loss":regloss,
          "final_classifier_loss":clfloss,
        }

    scored={}
    for d in ("BUY","SELL"):
        med,iqr=norms[d];reg,clf=models[d]
        vr,Sv,Xv=collect_partition(file_sets,"VALIDATION",med,iqr)
        dr,Sd,Xd=collect_partition(file_sets,"DEVELOPMENT_TEST",med,iqr)
        vg=np.clip(infer(reg,Sv,Xv,"reg"),-3,5);vn=vg-.10;vef=infer(clf,Sv,Xv,"clf")
        dg=np.clip(infer(reg,Sd,Xd,"reg"),-3,5);dn=dg-.10;defr=infer(clf,Sd,Xd,"clf")
        cuts={"Q50":float(np.quantile(vef,.50)),"Q25":float(np.quantile(vef,.25)),"Q10":float(np.quantile(vef,.10))}
        m23=np.asarray([e5.year_of(int(p["decision_time_ms"]))==2023 for p in dr])
        m24=np.asarray([e5.year_of(int(p["decision_time_ms"]))==2024 for p in dr])
        result["directions"][d].update({
          "validation_risk_cutoffs":cuts,
          "VALIDATION":predictive_metrics(vr,d,vg,vn,vef),
          "DEVELOPMENT_TEST":predictive_metrics(dr,d,dg,dn,defr),
          "DEVELOPMENT_TEST_2023":predictive_metrics([p for i,p in enumerate(dr) if m23[i]],d,dg[m23],dn[m23],defr[m23]),
          "DEVELOPMENT_TEST_2024":predictive_metrics([p for i,p in enumerate(dr) if m24[i]],d,dg[m24],dn[m24],defr[m24]),
        })
        scored[d]=(dr,dn,defr,cuts)

    if [p["decision_time_ms"] for p in scored["BUY"][0]] != [p["decision_time_ms"] for p in scored["SELL"][0]]:
        raise SystemExit("DIRECTION_ROW_ALIGNMENT_MISMATCH")
    dr=scored["BUY"][0]
    result["economics"]=eval_economics(
      dr,scored["BUY"][1],scored["SELL"][1],
      scored["BUY"][2],scored["SELL"][2],
      scored["BUY"][3],scored["SELL"][3]
    )
    passing=[]
    for arm,a in result["economics"].items():
        for th,modes in a.items():
            for mode,v in modes.items():
                if v["advancement"]["passed"]:
                    passing.append({"arm":arm,"threshold":th,"mode":mode})
    result["passing_policies"]=passing

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","passing_policies":passing,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
