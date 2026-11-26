#!/usr/bin/env python3
"""Run the frozen Stage 3B GOLD vs FULL recognition benchmark on candidate rows."""
from __future__ import annotations
import json,sys,warnings
from pathlib import Path
import numpy as np,pandas as pd,sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss,balanced_accuracy_score,confusion_matrix

SEED=20261010

def feature_defs(spec,arm):
    return [f for f in spec["features"] if f["arm"]=="GOLD" or arm=="FULL"]

def fit_preprocessor(df,defs,spec):
    unique=df.drop_duplicates("market_row_key",keep="first")
    nums=[f for f in defs if f["dtype"]!="categorical"]; cats=[f for f in defs if f["dtype"]=="categorical"]
    numeric={}
    for f in nums:
        name=f["name"]; x=pd.to_numeric(unique[name],errors="coerce").to_numpy(float); finite=np.isfinite(x)
        med=float(np.median(x[finite])) if finite.any() else 0.0
        imp=np.where(finite,x,med); mean=float(imp.mean()) if len(imp) else 0.0; std=float(imp.std()) if len(imp) else 1.0
        if not np.isfinite(std) or std<=1e-12: std=1.0
        numeric[name]=(med,mean,std)
    categorical={}
    vocabs=spec.get("categorical_vocabularies",{})
    for f in cats:
        name=f["name"]; vocab=list(vocabs.get(name,["UNKNOWN"]))
        if "UNKNOWN" not in vocab: vocab.append("UNKNOWN")
        categorical[name]=vocab
    return {"nums":[f["name"] for f in nums],"cats":[f["name"] for f in cats],"numeric":numeric,"categorical":categorical}

def transform(df,p):
    blocks=[]
    if p["nums"]:
        xs=[]; miss=[]
        for name in p["nums"]:
            med,mean,std=p["numeric"][name]; raw=pd.to_numeric(df[name],errors="coerce").to_numpy(float); m=~np.isfinite(raw)
            xs.append((np.where(m,med,raw)-mean)/std); miss.append(m.astype(float))
        blocks.append(np.column_stack(xs)); blocks.append(np.column_stack(miss))
    for name in p["cats"]:
        vocab=p["categorical"][name]; index={v:i for i,v in enumerate(vocab)}; arr=np.zeros((len(df),len(vocab)),float)
        vals=df[name].fillna("").astype(str).tolist()
        for i,v in enumerate(vals): arr[i,index.get(v,index["UNKNOWN"])]=1.0
        blocks.append(arr)
    return np.concatenate(blocks,axis=1) if blocks else np.empty((len(df),0))

def event_weights(train,ycol):
    ev=train[["event_id",ycol]].drop_duplicates()
    counts=ev[ycol].astype(int).value_counts().to_dict()
    if set(counts)!={0,1}: raise SystemExit(f"STAGE3B_TRAIN_CLASS:{ycol}:{counts}")
    scale={0:0.5/counts[0],1:0.5/counts[1]}
    return train["interval_weight"].astype(float).to_numpy()*train[ycol].astype(int).map(scale).to_numpy(float)

def fold_predictions(data,spec,arm,task):
    defs=feature_defs(spec,arm); ycol="task_a_label" if task=="A" else "task_b_label"
    work=data.copy()
    if task=="B": work=work[work["task_a_label"].astype(int)==1].copy()
    rows=[]; iters=[]
    for date in sorted(work["source_date"].unique()):
        train=work[work.source_date!=date].copy(); test=work[work.source_date==date].copy()
        train[ycol]=pd.to_numeric(train[ycol],errors="raise").astype(int); test[ycol]=pd.to_numeric(test[ycol],errors="raise").astype(int)
        prep=fit_preprocessor(train,defs,spec); X=transform(train,prep); Xt=transform(test,prep)
        model=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",fit_intercept=True,class_weight=None,max_iter=1000,tol=0.0001)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always"); model.fit(X,train[ycol].to_numpy(),sample_weight=event_weights(train,ycol))
        if any(issubclass(x.category,ConvergenceWarning) for x in w): raise SystemExit(f"STAGE3B_CONVERGENCE:{arm}:{task}:{date}")
        p=model.predict_proba(Xt)[:,1]; test=test.copy(); test["_p"]=p; iters.append(int(model.n_iter_[0]))
        for event_id,g in test.groupby("event_id",sort=False):
            first=g.iloc[0]
            rows.append({"event_id":event_id,"source_date":first["source_date"],"event_type":first["event_type"],"direction":first["direction"],"provenance_class":first["provenance_class"],"evidence_grade":first["evidence_grade"],"timing_class":first["timing_class"],"interval_width_minutes":int(first["interval_width_minutes"]),"reject_reason":first["reject_reason"],"label":int(first[ycol]),"probability":float(g["_p"].mean())})
    out=pd.DataFrame(rows)
    return out,{"max_iterations":max(iters),"mean_iterations":float(np.mean(iters))}

def binary_metrics(df):
    y=df.label.to_numpy(int); p=df.probability.to_numpy(float)
    return {"n":len(df),"positive":int(y.sum()),"negative":int((1-y).sum()),"roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,"average_precision":float(average_precision_score(y,p)) if y.sum()>0 else None,"brier":float(brier_score_loss(y,p)),"log_loss":float(log_loss(y,p,labels=[0,1]))}

def task_a_metrics(df):
    by={}
    for date,g in df.groupby("source_date"):
        by[date]=float(roc_auc_score(g.label,g.probability)) if g.label.nunique()==2 else None
    vals=[x for x in by.values() if x is not None]
    m=binary_metrics(df); m["per_date_roc_auc"]=by; m["mean_per_date_roc_auc"]=float(np.mean(vals)); return m

def task_b_metrics(df):
    y=df.label.to_numpy(int); p=df.probability.to_numpy(float); pred=(p>=0.5).astype(int)
    return {"n":len(df),"long":int(y.sum()),"short":int((1-y).sum()),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),"roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,"brier":float(brier_score_loss(y,p)),"log_loss":float(log_loss(y,p,labels=[0,1])),"confusion_matrix":confusion_matrix(y,pred,labels=[0,1]).tolist()}

def sensitivity(gold,full):
    z=gold.merge(full[["event_id","probability"]],on="event_id",suffixes=("_gold","_full"),validate="one_to_one")
    out={}
    groups={"EXACT_M1":z.interval_width_minutes==1,"INTERVAL_2M":z.interval_width_minutes==2,"INTERVAL_3_TO_5M":z.interval_width_minutes>=3,"E1":z.evidence_grade=="E1","E2":z.evidence_grade=="E2"}
    for name,mask in groups.items():
        g=z[mask]; item={"n":len(g),"positive":int(g.label.sum()) if len(g) else 0}
        if len(g) and g.label.nunique()==2:
            item["gold_auc"]=float(roc_auc_score(g.label,g.probability_gold)); item["full_auc"]=float(roc_auc_score(g.label,g.probability_full))
        out[name]=item
    for pc in ("P1","P2"):
        g=z[(z.provenance_class==pc)&(z.label==1)]
        out[pc]={"n":len(g),"gold_mean_p_act":float(g.probability_gold.mean()) if len(g) else None,"full_mean_p_act":float(g.probability_full.mean()) if len(g) else None}
    reasons={}
    for reason,g in z[z.label==0].groupby("reject_reason",dropna=False):
        key=str(reason) if str(reason) not in ("","nan") else "UNSPECIFIED"
        reasons[key]={"n":len(g),"gold_mean_p_act":float(g.probability_gold.mean()),"full_mean_p_act":float(g.probability_full.mean())}
    out["reject_reasons"]=reasons; return out

def main(argv):
    if len(argv)!=5: raise SystemExit("usage: run_stage3b_2026_benchmark.py <dataset.csv.gz> <feature.json> <result.json> <predictions.csv>")
    data=pd.read_csv(argv[1]); spec=json.loads(Path(argv[2]).read_text())
    if len(data)!=343 or data.event_id.nunique()!=250 or data.source_date.nunique()!=39: raise SystemExit("STAGE3B_BENCHMARK_DATA_COUNTS")
    pred={}; fit={}
    for task in ("A","B"):
        for arm in ("GOLD","FULL"):
            pred[(task,arm)],fit[f"{task}_{arm}"]=fold_predictions(data,spec,arm,task)
    ma_g=task_a_metrics(pred[("A","GOLD")]); ma_f=task_a_metrics(pred[("A","FULL")])
    mb_g=task_b_metrics(pred[("B","GOLD")]); mb_f=task_b_metrics(pred[("B","FULL")])
    dates=sorted(ma_g["per_date_roc_auc"]); delta=np.array([ma_f["per_date_roc_auc"][d]-ma_g["per_date_roc_auc"][d] for d in dates],float)
    rng=np.random.default_rng(SEED); n=len(delta); boot=np.empty(10000)
    for i in range(10000): boot[i]=delta[rng.integers(0,n,n)].mean()
    ci=[float(x) for x in np.percentile(boot,[2.5,97.5])]; dmean=float(delta.mean())
    task_a_pass=dmean>=0.03 and ci[0]>0 and ma_f["brier"]<=ma_g["brier"]+0.01
    task_b_ok=mb_f["balanced_accuracy"]>=mb_g["balanced_accuracy"]-0.02 and mb_f["brier"]<=mb_g["brier"]+0.01
    result="PASS" if task_a_pass and task_b_ok else ("MIXED — ACTION INFORMATION IMPROVED, DIRECTION DEGRADED" if task_a_pass else "NEGATIVE FOR FROZEN STAGE 3B HYPOTHESIS")
    merged=pred[("A","GOLD")].rename(columns={"probability":"task_a_gold"}).merge(pred[("A","FULL")][["event_id","probability"]].rename(columns={"probability":"task_a_full"}),on="event_id",validate="one_to_one")
    b=pred[("B","GOLD")][["event_id","probability"]].rename(columns={"probability":"task_b_gold"}).merge(pred[("B","FULL")][["event_id","probability"]].rename(columns={"probability":"task_b_full"}),on="event_id",validate="one_to_one")
    merged=merged.merge(b,on="event_id",how="left",validate="one_to_one"); Path(argv[4]).parent.mkdir(parents=True,exist_ok=True); merged.to_csv(argv[4],index=False)
    report={"status":"PASS","scientific_result":result,"source_adequacy":"ADEQUATE","sklearn_version":sklearn.__version__,"seed":SEED,"folds":39,"task_a":{"GOLD":ma_g,"FULL":ma_f,"full_minus_gold_mean_per_date_auc":dmean,"paired_date_bootstrap_95_ci":ci,"task_a_gate_pass":task_a_pass},"task_b":{"GOLD":mb_g,"FULL":mb_f,"task_b_nonregression_pass":task_b_ok},"fit_diagnostics":fit,"sensitivity":sensitivity(pred[("A","GOLD")],pred[("A","FULL")]),"frozen_advancement_rule":{"delta_auc_min":0.03,"ci_lower_gt":0.0,"task_a_brier_tolerance":0.01,"task_b_balanced_accuracy_tolerance":-0.02,"task_b_brier_tolerance":0.01}}
    Path(argv[3]).parent.mkdir(parents=True,exist_ok=True); Path(argv[3]).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"scientific_result":result,"task_a_delta":dmean,"task_a_ci":ci,"task_b_gold_balacc":mb_g["balanced_accuracy"],"task_b_full_balacc":mb_f["balanced_accuracy"]},indent=2))
if __name__=="__main__": main(sys.argv)
