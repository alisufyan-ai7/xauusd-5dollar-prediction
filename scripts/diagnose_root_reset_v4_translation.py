#!/usr/bin/env python3
"""TRAIN-only translation diagnosis for Root-Reset V4 Badar-Core."""

import sys,json,math
from pathlib import Path
from collections import defaultdict
from datetime import timedelta
import numpy as np
import pandas as pd
import root_reset_v4_badar_core as v4

def swing_state(bars):
    return v4.structure_state(bars)

def one_close_mss(side, confirm_t, expire_t, bars, states):
    s=v4.lookup_row(states,confirm_t)
    if s is None:return None
    ref=float(s["swing_high"] if side=="BUY" else s["swing_low"])
    if not math.isfinite(ref):return None
    p0=bars.index.searchsorted(confirm_t,side="right")
    p1=bars.index.searchsorted(expire_t,side="right")
    cl=bars["close"].to_numpy(float);hi=bars["high"].to_numpy(float);lo=bars["low"].to_numpy(float)
    for j in range(p0,p1):
        ok=(cl[j]>ref) if side=="BUY" else (cl[j]<ref)
        if not ok:continue
        fvg=None
        for k in (j,j-1,j-2):
            if k<2 or bars.index[k]<=confirm_t:continue
            if side=="BUY" and hi[k-2]<lo[k]:
                fvg=(float(hi[k-2]),float(lo[k]));break
            if side=="SELL" and lo[k-2]>hi[k]:
                fvg=(float(hi[k]),float(lo[k-2]));break
        return {"time":bars.index[j],"ref":ref,"fvg":fvg}
    return None

def m1_state(bid):
    b=bid[["open","high","low","close"]].copy()
    return v4.structure_state(b)

def executable_direct_entry(side,t,bid,ask):
    nxt=t+pd.Timedelta(minutes=1)
    if nxt not in bid.index or nxt not in ask.index:return None
    return float(ask.loc[nxt,"open"] if side=="BUY" else bid.loc[nxt,"open"]),nxt

def midpoint_fill(side,mid,start,end,bid,ask):
    return v4.first_limit_fill(side,mid,bid,ask,start,end)

def target_distances(side,entry,asian,london,prevday,h1s,h4s,t):
    vals={}
    if side=="BUY":
        candidates={
          "asian":asian["high"],"london":london["high"],"prev_day":prevday["high"] if prevday else None,
          "h1_swing":float(v4.lookup_row(h1s,t)["swing_high"]) if v4.lookup_row(h1s,t) is not None else None,
          "h4_swing":float(v4.lookup_row(h4s,t)["swing_high"]) if v4.lookup_row(h4s,t) is not None else None,
        }
        for k,x in candidates.items():
            vals[k]=(float(x-entry) if x is not None and math.isfinite(float(x)) and x>entry else None)
    else:
        candidates={
          "asian":asian["low"],"london":london["low"],"prev_day":prevday["low"] if prevday else None,
          "h1_swing":float(v4.lookup_row(h1s,t)["swing_low"]) if v4.lookup_row(h1s,t) is not None else None,
          "h4_swing":float(v4.lookup_row(h4s,t)["swing_low"]) if v4.lookup_row(h4s,t) is not None else None,
        }
        for k,x in candidates.items():
            vals[k]=(float(entry-x) if x is not None and math.isfinite(float(x)) and x<entry else None)
    return vals

def summarize_targets(rows,entry_type):
    out={}
    for fam in ("asian","london","prev_day","h1_swing","h4_swing"):
        vals=[r[entry_type]["targets"].get(fam) for r in rows if r.get(entry_type) and r[entry_type]["targets"].get(fam) is not None]
        if not vals:
            out[fam]={"n":0};continue
        a=np.asarray(vals,float)
        out[fam]={
          "n":len(a),"median":float(np.median(a)),"p75":float(np.quantile(a,.75)),
          "ge3_share":float(np.mean(a>=3)),"ge5_share":float(np.mean(a>=5)),"ge7_share":float(np.mean(a>=7))
        }
    return out

def main(argv):
    if len(argv)!=1+6*2:raise SystemExit("usage: diagnose_root_reset_v4_translation.py 6x <bid> <ask>")
    bids=[];asks=[]
    for i in range(6):
        b,a=v4.load_pair(argv[1+i*2],argv[2+i*2]);bids.append(b);asks.append(a)
    bid=pd.concat(bids).sort_index();ask=pd.concat(asks).sort_index()
    ts=bid["timestamp"].to_numpy(np.int64);bhi=bid["high"].to_numpy(float);blo=bid["low"].to_numpy(float)

    m5=v4.resample_exact(bid,"5min",5);m15=v4.resample_exact(bid,"15min",15)
    h1=v4.resample_exact(bid,"1h",60);h4=v4.resample_exact(bid,"4h",240);d1=v4.build_d1_from_h1(h1)
    m3=v4.resample_exact(bid,"3min",3)
    st1=m1_state(bid);st3=swing_state(m3);st5=swing_state(m5);sth1=swing_state(h1);sth4=swing_state(h4);std1=swing_state(d1)
    fvgs=v4.build_h1_fvgs(h1)

    counts=defaultdict(int);rows=[]
    first=pd.Timestamp(bid.index.min()).tz_convert(v4.NY).date()
    last=pd.Timestamp(bid.index.max()).tz_convert(v4.NY).date()
    d=first
    while d<=last:
        if d.year<2016 or d.year>2021:d+=timedelta(days=1);continue
        tok,lon,nyopen,ex0,ex1,cap=v4.session_bounds(d)
        tok,lon,nyopen,ex0,ex1=map(pd.Timestamp,(tok,lon,nyopen,ex0,ex1))
        asian=v4.range_stats(ts,bhi,blo,v4.ts_ms(tok),v4.ts_ms(lon))
        london=v4.range_stats(ts,bhi,blo,v4.ts_ms(lon),v4.ts_ms(nyopen))
        if asian is None or london is None:d+=timedelta(days=1);continue
        pday=(tok-pd.Timedelta(days=1)).floor("D")
        prev=bid.loc[(bid.index>=pday)&(bid.index<pday+pd.Timedelta(days=1))]
        prevday=None if prev.empty else {"high":float(prev["high"].max()),"low":float(prev["low"].min())}
        for side in ("BUY","SELL"):
            day15=m15.loc[(m15.index>ex0)&(m15.index<=ex1)]
            filled_for_side=False
            blocked_until=ex0
            for t,bar in day15.iterrows():
                if filled_for_side or t<blocked_until or v4.is_news_time(t):continue
                s1=v4.lookup_row(sth1,t);s4=v4.lookup_row(sth4,t);sd=v4.lookup_row(std1,t)
                if s1 is None or s4 is None or sd is None:continue
                h1v,h4v,d1v=int(s1["state"]),int(s4["state"]),int(sd["state"])
                elig=(h1v==1 and h4v!=-1 and d1v!=-1) if side=="BUY" else (h1v==-1 and h4v!=1 and d1v!=1)
                if not elig:continue
                p=m15.index.get_loc(t)
                if p<4:continue
                prev15=m15.iloc[p-4:p]
                trs=[];pc=float(m15.iloc[p-5]["close"]) if p>=5 else None
                if pc is None:continue
                for _,rr in prev15.iterrows():
                    trs.append(max(float(rr["high"]-rr["low"]),abs(float(rr["high"])-pc),abs(float(rr["low"])-pc)))
                    pc=float(rr["close"])
                atr=float(np.mean(trs));buf=.05*atr
                levels=(asian["low"],london["low"]) if side=="BUY" else (asian["high"],london["high"])
                pierced=[x for x in levels if (float(bar["low"])<x-buf if side=="BUY" else float(bar["high"])>x+buf)]
                if not pierced:continue
                level=min(pierced) if side=="BUY" else max(pierced)
                fvg=v4.active_fvg(fvgs,side,t,float(bar["low"]),float(bar["high"]))
                if fvg is None:continue
                closeback=(float(bar["close"])>level) if side=="BUY" else (float(bar["close"])<level)
                if not closeback:continue
                counts["m15_confirmations"]+=1
                exp=min(t+pd.Timedelta(minutes=30),ex1)
                c2=v4.find_mss_and_fvg(side,t,exp,m5,st5)
                c1=one_close_mss(side,t,exp,m5,st5)
                c3=one_close_mss(side,t,exp,m3,st3)
                c4=one_close_mss(side,t,exp,bid,st1)
                if c2 and c2.get("mss"):counts["c2_two_close_m5"]+=1
                if c1:counts["c1_one_close_m5"]+=1
                if c3:counts["c3_one_close_m3"]+=1
                if c4:counts["c4_one_close_m1"]+=1
                if (not c2 or not c2.get("mss")) and c1:counts["recover_m5_one_close"]+=1
                if (not c2 or not c2.get("mss")) and (c3 or c4):counts["recover_m3_or_m1"]+=1

                rec={"year":d.year,"side":side}
                for name,cx,bars in (("c1",c1,m5),("c2",c2,m5),("c3",c3,m3),("c4",c4,bid)):
                    if not cx or (name=="c2" and not cx.get("mss")):continue
                    ct=(cx.get("mss_time") or bars.index[int(cx["j"])]) if name=="c2" else cx["time"]
                    direct=executable_direct_entry(side,ct,bid,ask)
                    if direct:
                        ep,et=direct
                        rec[name+"_direct"]={"entry":ep,"time":et.isoformat(),"targets":target_distances(side,ep,asian,london,prevday,sth1,sth4,ct)}
                        counts[name+"_direct_entries"]+=1
                    fvgx=(cx.get("lower"),cx.get("upper")) if name=="c2" and cx.get("fvg") else cx.get("fvg")
                    if fvgx:
                        mid=(fvgx[0]+fvgx[1])/2
                        fill=midpoint_fill(side,mid,ct,min(ct+pd.Timedelta(minutes=30),ex1),bid,ask)
                        counts[name+"_with_fvg"]+=1
                        if fill is not None:
                            rec[name+"_mid"]={"entry":mid,"time":fill.isoformat(),"wait_minutes":(fill-ct).total_seconds()/60,
                                             "targets":target_distances(side,mid,asian,london,prevday,sth1,sth4,ct)}
                            counts[name+"_mid_fills"]+=1
                rows.append(rec)

                # Preserve V4 candidate-spacing semantics exactly. Although this
                # diagnosis changes only logic after M15 close-back, V4 blocks
                # subsequent M15 candidates while its frozen downstream attempt
                # is active. Reproduce that blocking so the diagnosed M15 set is
                # the same V4 set (135 confirmations in the reference run).
                if c2 is None or not c2.get("mss") or not c2.get("fvg"):
                    blocked_until=exp
                    continue
                v4_entry=float(c2["limit"])
                v4_target=v4.nearest_target(side,v4_entry,asian,london)
                if v4_target is None:
                    blocked_until=exp
                    continue
                v4_target_dist=(v4_target-v4_entry) if side=="BUY" else (v4_entry-v4_target)
                if v4_target_dist<5.0:
                    blocked_until=exp
                    continue
                v4_order_end=min(c2["mss_time"]+pd.Timedelta(minutes=30),ex1)
                v4_fill=v4.first_limit_fill(side,v4_entry,bid,ask,c2["mss_time"],v4_order_end)
                if v4_fill is None:
                    blocked_until=v4_order_end
                    continue
                filled_for_side=True
        d+=timedelta(days=1)

    report={"status":"PASS","diagnosis":"ROOT_RESET_V4_TRANSLATION","scope":"TRAIN_2016_2021_ONLY",
            "validation_accessed":False,"development_test_accessed":False,"final_oos":"NOT_ACCESSED",
            "counts":dict(counts),"target_summaries":{},"entry_observability":{}}
    for name in ("c1_direct","c1_mid","c2_direct","c2_mid","c3_direct","c3_mid","c4_direct","c4_mid"):
        report["target_summaries"][name]=summarize_targets(rows,name)
    for name in ("c1","c2","c3","c4"):
        direct_n=sum(1 for r in rows if r.get(name+"_direct"))
        fvg_n=int(counts.get(name+"_with_fvg",0))
        mid_fill_n=int(counts.get(name+"_mid_fills",0))
        waits=[float(r[name+"_mid"]["wait_minutes"]) for r in rows if r.get(name+"_mid")]
        direct_without_mid=sum(1 for r in rows if r.get(name+"_direct") and not r.get(name+"_mid"))
        report["entry_observability"][name]={
          "direct_entries":direct_n,
          "fvg_available":fvg_n,
          "midpoint_fills":mid_fill_n,
          "midpoint_fill_rate":float(mid_fill_n/fvg_n) if fvg_n else None,
          "median_wait_to_midpoint_fill_minutes":float(np.median(waits)) if waits else None,
          "direct_entry_without_midpoint_fill":direct_without_mid,
          "direct_entry_without_midpoint_fill_share":float(direct_without_mid/direct_n) if direct_n else None,
        }
    # broader-target recovery: direct entries where max broader >=5 and max session <5
    for name in ("c1_direct","c2_direct","c3_direct","c4_direct"):
        n=0;tot=0
        for r in rows:
            if not r.get(name):continue
            tot+=1;t=r[name]["targets"]
            sess=max([x for x in (t.get("asian"),t.get("london")) if x is not None],default=-1)
            broad=max([x for x in (t.get("prev_day"),t.get("h1_swing"),t.get("h4_swing")) if x is not None],default=-1)
            if broad>=5 and sess<5:n+=1
        report["counts"][name+"_broader_ge5_session_lt5"]=n
        report["counts"][name+"_broader_ge5_session_lt5_share"]=float(n/tot) if tot else None

    out=Path("data/reports/root-reset-v4/translation-diagnosis.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","counts":report["counts"],"validation_accessed":False,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":main(sys.argv)
