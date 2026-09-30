#!/usr/bin/env python3
"""Root-Reset V4 Badar-Core TRAIN-only deterministic experiment."""

import sys, json, math
from pathlib import Path
from collections import defaultdict
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ONE_MIN = 60_000
NY = ZoneInfo("America/New_York")
LON = ZoneInfo("Europe/London")
UTC = timezone.utc

def load_pair(bid_path, ask_path):
    cols=["timestamp","open","high","low","close"]
    b=pd.read_csv(bid_path,usecols=cols)
    a=pd.read_csv(ask_path,usecols=cols)
    if len(b)!=len(a):
        raise SystemExit(f"PAIR_ROW_MISMATCH:{bid_path}")
    if not np.array_equal(b["timestamp"].to_numpy(),a["timestamp"].to_numpy()):
        raise SystemExit(f"PAIR_TS_MISMATCH:{bid_path}")
    for df in (b,a):
        df["timestamp"]=df["timestamp"].astype("int64")
        for c in ("open","high","low","close"):
            df[c]=df[c].astype("float64")
        df["dt"]=pd.to_datetime(df["timestamp"],unit="ms",utc=True)
        df.set_index("dt",inplace=True,drop=False)
    return b,a

def resample_exact(df, rule, expected):
    r=df[["open","high","low","close"]].resample(
        rule,origin="epoch",closed="left",label="right"
    )
    agg=r.agg({"open":"first","high":"max","low":"min","close":"last"})
    cnt=r["close"].count()
    out=agg.loc[cnt==expected].copy()
    out["count"]=cnt.loc[cnt==expected].astype(int)
    return out

def build_d1_from_h1(h1):
    if h1.empty:
        return h1.copy()
    tmp=h1.copy()
    tmp["day"]=(tmp.index-pd.Timedelta(nanoseconds=1)).floor("D")
    rows=[]
    for d,g in tmp.groupby("day"):
        if len(g)<20:
            continue
        rows.append({
            "dt":d+pd.Timedelta(days=1),
            "open":float(g.iloc[0]["open"]),
            "high":float(g["high"].max()),
            "low":float(g["low"].min()),
            "close":float(g.iloc[-1]["close"]),
            "count":int(len(g))
        })
    if not rows:
        return pd.DataFrame(columns=["open","high","low","close","count"])
    z=pd.DataFrame(rows).set_index("dt")
    z.index=pd.DatetimeIndex(z.index).tz_convert("UTC") if z.index.tz is not None else pd.DatetimeIndex(z.index,tz="UTC")
    return z

def structure_state(bars):
    n=len(bars)
    if n==0:
        return pd.DataFrame(index=bars.index)
    hi=bars["high"].to_numpy(float)
    lo=bars["low"].to_numpy(float)
    cl=bars["close"].to_numpy(float)
    state=np.zeros(n,dtype=np.int8)
    last_hi=np.full(n,np.nan)
    last_lo=np.full(n,np.nan)
    cur_state=0
    sh=np.nan; sl=np.nan
    for j in range(n):
        if j>=4:
            i=j-2
            if hi[i]>hi[i-1] and hi[i]>hi[i-2] and hi[i]>=hi[i+1] and hi[i]>=hi[i+2]:
                sh=float(hi[i])
            if lo[i]<lo[i-1] and lo[i]<lo[i-2] and lo[i]<=lo[i+1] and lo[i]<=lo[i+2]:
                sl=float(lo[i])
        if j>=1:
            bull=(math.isfinite(sh) and cl[j]>sh and cl[j-1]>sh)
            bear=(math.isfinite(sl) and cl[j]<sl and cl[j-1]<sl)
            if bull and not bear:
                cur_state=1
            elif bear and not bull:
                cur_state=-1
        state[j]=cur_state
        last_hi[j]=sh
        last_lo[j]=sl
    return pd.DataFrame({"state":state,"swing_high":last_hi,"swing_low":last_lo},index=bars.index)

def lookup_row(df, t):
    if df.empty:
        return None
    p=df.index.searchsorted(t,side="right")-1
    if p<0:
        return None
    return df.iloc[p]

def build_h1_fvgs(h1):
    out={"BUY":[],"SELL":[]}
    hi=h1["high"].to_numpy(float); lo=h1["low"].to_numpy(float); cl=h1["close"].to_numpy(float)
    idx=h1.index
    n=len(h1)
    for k in range(2,n):
        if hi[k-2] < lo[k]:
            lower=float(hi[k-2]); upper=float(lo[k]); inv=None
            for j in range(k+1,min(n,k+74)):
                if cl[j] < lower:
                    inv=idx[j]; break
            out["BUY"].append((idx[k],inv,lower,upper))
        if lo[k-2] > hi[k]:
            lower=float(hi[k]); upper=float(lo[k-2]); inv=None
            for j in range(k+1,min(n,k+74)):
                if cl[j] > upper:
                    inv=idx[j]; break
            out["SELL"].append((idx[k],inv,lower,upper))
    return out

def active_fvg(fvgs, side, t, bar_low, bar_high):
    cutoff=t-pd.Timedelta(hours=72)
    best=None
    for created,invalid,lower,upper in fvgs[side]:
        if created>t or created<cutoff:
            continue
        if invalid is not None and invalid<=t:
            continue
        if bar_low<=upper and bar_high>=lower:
            if best is None or created>best[0]:
                best=(created,invalid,lower,upper)
    return best

def ts_ms(x):
    return int(pd.Timestamp(x).value//1_000_000)

def session_bounds(d):
    tokyo=datetime.combine(d,time(0,0),tzinfo=UTC)
    lon=datetime.combine(d,time(8,0),tzinfo=LON).astimezone(UTC)
    nyopen=datetime.combine(d,time(8,0),tzinfo=NY).astimezone(UTC)
    ex0=datetime.combine(d,time(9,0),tzinfo=NY).astimezone(UTC)
    ex1=datetime.combine(d,time(10,30),tzinfo=NY).astimezone(UTC)
    cap=datetime.combine(d,time(11,30),tzinfo=NY).astimezone(UTC)
    return tokyo,lon,nyopen,ex0,ex1,cap

def range_stats(ts, hi, lo, start_ms, end_ms):
    l=np.searchsorted(ts,start_ms,"left")
    r=np.searchsorted(ts,end_ms,"left")
    if r<=l:
        return None
    seg=ts[l:r]
    expected=(end_ms-start_ms)//ONE_MIN
    if expected<=0 or len(seg)<0.95*expected:
        return None
    if len(seg)>1 and np.max(np.diff(seg))>5*ONE_MIN:
        return None
    return {"high":float(np.max(hi[l:r])),"low":float(np.min(lo[l:r])),"n":int(r-l)}

def is_news_time(t):
    lt=t.tz_convert(NY)
    mins=lt.hour*60+lt.minute
    return 9*60+55 <= mins <= 10*60+10

def consecutive_m1(ts, start_pos, end_pos):
    if end_pos-start_pos<=1:
        return True
    return bool(np.all(np.diff(ts[start_pos:end_pos])==ONE_MIN))

def first_limit_fill(side, limit_price, bid, ask, start, end):
    if side=="BUY":
        z=ask.loc[(ask.index>=start)&(ask.index<end)]
        hit=z[z["low"]<=limit_price]
    else:
        z=bid.loc[(bid.index>=start)&(bid.index<end)]
        hit=z[z["high"]>=limit_price]
    if hit.empty:
        return None
    return hit.index[0]

def nearest_target(side, entry, asian, london):
    if side=="BUY":
        vals=[x for x in (asian["high"],london["high"]) if x>entry]
        return min(vals) if vals else None
    vals=[x for x in (asian["low"],london["low"]) if x<entry]
    return max(vals) if vals else None

def find_mss_and_fvg(side, confirm_t, expire_t, m5, m5state):
    s=lookup_row(m5state,confirm_t)
    if s is None:
        return None
    ref=float(s["swing_high"] if side=="BUY" else s["swing_low"])
    if not math.isfinite(ref):
        return None
    pos0=m5.index.searchsorted(confirm_t,side="right")
    pos1=m5.index.searchsorted(expire_t,side="right")
    cl=m5["close"].to_numpy(float); hi=m5["high"].to_numpy(float); lo=m5["low"].to_numpy(float)
    for j in range(max(pos0+1,1),pos1):
        if m5.index[j]-m5.index[j-1] != pd.Timedelta(minutes=5):
            continue
        ok=(cl[j]>ref and cl[j-1]>ref) if side=="BUY" else (cl[j]<ref and cl[j-1]<ref)
        if not ok:
            continue
        chosen=None
        for k in (j,j-1,j-2):
            if k<2 or m5.index[k]<=confirm_t:
                continue
            if side=="BUY" and hi[k-2] < lo[k]:
                chosen=(k,float(hi[k-2]),float(lo[k]))
                break
            if side=="SELL" and lo[k-2] > hi[k]:
                chosen=(k,float(hi[k]),float(lo[k-2]))
                break
        if chosen is None:
            return {"mss":True,"fvg":False,"j":j,"ref":ref}
        k,lower,upper=chosen
        return {"mss":True,"fvg":True,"j":j,"k":k,"ref":ref,"lower":lower,"upper":upper,
                "mss_time":m5.index[j],"limit":(lower+upper)/2.0}
    return None

def outcome_for_stop(side, entry, target, stop, fill_t, bid, ask, horizon_end):
    stop_dist=(entry-stop) if side=="BUY" else (stop-entry)
    target_dist=(target-entry) if side=="BUY" else (entry-target)
    if stop_dist<=0 or target_dist<=0:
        return None
    # fill-bar conservative stop check
    fb_bid=bid.loc[fill_t] if fill_t in bid.index else None
    fb_ask=ask.loc[fill_t] if fill_t in ask.index else None
    if fb_bid is None or fb_ask is None:
        return None
    fill_stop=(float(fb_bid["low"])<=stop) if side=="BUY" else (float(fb_ask["high"])>=stop)
    if fill_stop:
        gross=-stop_dist
        return {"reason":"STOP_FILL_BAR","gross":gross,"stop_dist":stop_dist,"target_dist":target_dist,
                "net_r_f10":float((gross-0.10)/stop_dist),"target_first":0,"stop_first":1}
    start=fill_t+pd.Timedelta(minutes=1)
    if start>horizon_end:
        return None
    zbid=bid.loc[(bid.index>=start)&(bid.index<=horizon_end)]
    zask=ask.loc[(ask.index>=start)&(ask.index<=horizon_end)]
    if len(zbid)==0 or len(zbid)!=len(zask) or not np.array_equal(zbid["timestamp"].to_numpy(),zask["timestamp"].to_numpy()):
        return None
    tarr=zbid["timestamp"].to_numpy(np.int64)
    if len(tarr)>1 and not np.all(np.diff(tarr)==ONE_MIN):
        return None
    for t in zbid.index:
        if side=="BUY":
            st=float(zbid.at[t,"low"])<=stop
            tg=float(zbid.at[t,"high"])>=target
        else:
            st=float(zask.at[t,"high"])>=stop
            tg=float(zask.at[t,"low"])<=target
        if st:
            gross=-stop_dist
            return {"reason":"STOP" if not tg else "STOP_AMBIG","gross":gross,"stop_dist":stop_dist,
                    "target_dist":target_dist,"net_r_f10":float((gross-0.10)/stop_dist),
                    "target_first":0,"stop_first":1}
        if tg:
            gross=target_dist
            return {"reason":"TARGET","gross":gross,"stop_dist":stop_dist,"target_dist":target_dist,
                    "net_r_f10":float((gross-0.10)/stop_dist),"target_first":1,"stop_first":0}
    last=zbid.iloc[-1] if side=="BUY" else zask.iloc[-1]
    exit_px=float(last["close"])
    gross=(exit_px-entry) if side=="BUY" else (entry-exit_px)
    return {"reason":"TIME","gross":gross,"stop_dist":stop_dist,"target_dist":target_dist,
            "net_r_f10":float((gross-0.10)/stop_dist),"target_first":0,"stop_first":0}

def path_metrics(side, entry, fill_t, bid, ask, end_t):
    start=fill_t+pd.Timedelta(minutes=1)
    zbid=bid.loc[(bid.index>=start)&(bid.index<=end_t)]
    zask=ask.loc[(ask.index>=start)&(ask.index<=end_t)]
    if len(zbid)==0 or len(zbid)!=len(zask) or not np.array_equal(zbid["timestamp"].to_numpy(),zask["timestamp"].to_numpy()):
        return None
    ts=zbid["timestamp"].to_numpy(np.int64)
    if len(ts)>1 and not np.all(np.diff(ts)==ONE_MIN):
        return None
    if side=="BUY":
        fav=np.maximum(0,zbid["high"].to_numpy(float)-entry)
        adv=np.maximum(0,entry-zbid["low"].to_numpy(float))
    else:
        fav=np.maximum(0,entry-zask["low"].to_numpy(float))
        adv=np.maximum(0,zask["high"].to_numpy(float)-entry)
    mfe=float(np.max(fav)); mae=float(np.max(adv))
    plus5_before3=0
    for f,a in zip(fav,adv):
        if f>=5 and a>=3:
            plus5_before3=0;break
        if f>=5:
            plus5_before3=1;break
        if a>=3:
            plus5_before3=0;break
    return {"mfe":mfe,"mae":mae,"hit3":int(mfe>=3),"hit5":int(mfe>=5),"hit7":int(mfe>=7),
            "plus5_before3":plus5_before3}

def summarize(vals):
    a=np.asarray(vals,float)
    if len(a)==0:return None
    return {"mean":float(np.mean(a)),"median":float(np.median(a)),
            "p25":float(np.quantile(a,.25)),"p75":float(np.quantile(a,.75))}

def stop_summary(rows,key):
    rr=[r[key] for r in rows if r.get(key)]
    if not rr:return {"n":0}
    nets=np.asarray([x["net_r_f10"] for x in rr],float)
    pos=nets[nets>0].sum(); neg=-nets[nets<0].sum()
    return {
      "n":len(rr),
      "median_stop_distance":float(np.median([x["stop_dist"] for x in rr])),
      "median_target_stop_rr":float(np.median([x["target_dist"]/x["stop_dist"] for x in rr])),
      "target_before_stop_rate":float(np.mean([x["target_first"] for x in rr])),
      "mean_net_f10_r":float(np.mean(nets)),
      "profit_factor":float(pos/neg) if neg>0 else None,
      "reasons":{k:sum(x["reason"]==k for x in rr) for k in sorted(set(x["reason"] for x in rr))}
    }

def row_summary(rows):
    if not rows:return {"count":0}
    mfe60=[r["p60"]["mfe"] for r in rows if r.get("p60")]
    mae60=[r["p60"]["mae"] for r in rows if r.get("p60")]
    mfe120=[r["p120"]["mfe"] for r in rows if r.get("p120")]
    mae120=[r["p120"]["mae"] for r in rows if r.get("p120")]
    out={
      "count":len(rows),
      "target_distance":summarize([r["target_dist"] for r in rows]),
      "mfe60":summarize(mfe60),"mae60":summarize(mae60),
      "mfe120":summarize(mfe120),"mae120":summarize(mae120),
      "hit3_rate_120":float(np.mean([r["p120"]["hit3"] for r in rows if r.get("p120")])) if mfe120 else None,
      "hit5_rate_120":float(np.mean([r["p120"]["hit5"] for r in rows if r.get("p120")])) if mfe120 else None,
      "hit7_rate_120":float(np.mean([r["p120"]["hit7"] for r in rows if r.get("p120")])) if mfe120 else None,
      "plus5_before3_rate_120":float(np.mean([r["p120"]["plus5_before3"] for r in rows if r.get("p120")])) if mfe120 else None,
      "s_struct_60":stop_summary(rows,"struct60"),
      "s_struct_120":stop_summary(rows,"struct120"),
      "s_micro_60":stop_summary(rows,"micro60"),
      "s_micro_120":stop_summary(rows,"micro120"),
    }
    if mfe60 and mae60:
        out["median_mfe60_to_median_mae60"]=float(np.median(mfe60)/max(np.median(mae60),1e-9))
    if mfe120 and mae120:
        out["median_mfe120_to_median_mae120"]=float(np.median(mfe120)/max(np.median(mae120),1e-9))
        out["year_path_edge_proxy"]=float(np.median(np.asarray(mfe120)-np.asarray(mae120)))
    return out

def main(argv):
    if len(argv)!=1+6*2:
        raise SystemExit("usage: root_reset_v4_badar_core.py 6x <bid.csv> <ask.csv>")

    bids=[];asks=[]
    for i in range(6):
        b,a=load_pair(argv[1+i*2],argv[2+i*2])
        bids.append(b);asks.append(a)
    bid=pd.concat(bids).sort_index()
    ask=pd.concat(asks).sort_index()
    if bid.index.has_duplicates or ask.index.has_duplicates:
        raise SystemExit("DUPLICATE_TIMESTAMP")
    ts=bid["timestamp"].to_numpy(np.int64)
    bhi=bid["high"].to_numpy(float); blo=bid["low"].to_numpy(float)

    m5=resample_exact(bid,"5min",5)
    m15=resample_exact(bid,"15min",15)
    h1=resample_exact(bid,"1h",60)
    h4=resample_exact(bid,"4h",240)
    d1=build_d1_from_h1(h1)
    ask5=resample_exact(ask,"5min",5)
    ask15=resample_exact(ask,"15min",15)

    st5=structure_state(m5); st15=structure_state(m15)
    sth1=structure_state(h1); sth4=structure_state(h4); std1=structure_state(d1)
    fvgs=build_h1_fvgs(h1)

    funnel=defaultdict(int); yearly_funnel=defaultdict(lambda:defaultdict(int))
    rows=[]

    first_date=pd.Timestamp(bid.index.min()).tz_convert(NY).date()
    last_date=pd.Timestamp(bid.index.max()).tz_convert(NY).date()
    d=first_date
    while d<=last_date:
        if d.year<2016 or d.year>2021:
            d+=timedelta(days=1);continue
        tokyo,lon,nyopen,ex0,ex1,cap=session_bounds(d)
        tok=pd.Timestamp(tokyo); lo_t=pd.Timestamp(lon); ny_t=pd.Timestamp(nyopen)
        ex0t=pd.Timestamp(ex0); ex1t=pd.Timestamp(ex1); capt=pd.Timestamp(cap)
        asian=range_stats(ts,bhi,blo,ts_ms(tok),ts_ms(lo_t))
        london=range_stats(ts,bhi,blo,ts_ms(lo_t),ts_ms(ny_t))
        if asian is None or london is None:
            d+=timedelta(days=1);continue
        funnel["ny_dates_observed"]+=1; yearly_funnel[d.year]["ny_dates_observed"]+=1

        day15=m15.loc[(m15.index>ex0t)&(m15.index<=ex1t)]
        if day15.empty:
            d+=timedelta(days=1);continue

        for side in ("BUY","SELL"):
            filled_for_side=False
            blocked_until=ex0t
            dir_day_counted=False
            for t,bar in day15.iterrows():
                if filled_for_side or t<blocked_until or is_news_time(t):
                    continue
                s1=lookup_row(sth1,t);s4=lookup_row(sth4,t);sd=lookup_row(std1,t)
                if s1 is None or s4 is None or sd is None:
                    continue
                h1s=int(s1["state"]);h4s=int(s4["state"]);d1s=int(sd["state"])
                eligible=(h1s==1 and h4s!=-1 and d1s!=-1) if side=="BUY" else (h1s==-1 and h4s!=1 and d1s!=1)
                if not eligible:
                    continue
                if not dir_day_counted:
                    funnel["directionally_eligible_session_days"]+=1
                    yearly_funnel[d.year]["directionally_eligible_session_days"]+=1
                    dir_day_counted=True

                # ATR15 from four previous complete M15 bars
                p=m15.index.get_loc(t)
                if p<4:continue
                prev=m15.iloc[p-4:p]
                trs=[]
                prev_close=None
                for ii,rr in prev.iterrows():
                    if prev_close is None:
                        prev_pos=m15.index.get_loc(ii)-1
                        if prev_pos<0:break
                        prev_close=float(m15.iloc[prev_pos]["close"])
                    tr=max(float(rr["high"]-rr["low"]),abs(float(rr["high"])-prev_close),abs(float(rr["low"])-prev_close))
                    trs.append(tr);prev_close=float(rr["close"])
                if len(trs)!=4:continue
                atr15=float(np.mean(trs))
                if not math.isfinite(atr15) or atr15<=0:continue
                buf=.05*atr15

                levels=(asian["low"],london["low"]) if side=="BUY" else (asian["high"],london["high"])
                if side=="BUY":
                    pierced=[x for x in levels if float(bar["low"])<x-buf]
                else:
                    pierced=[x for x in levels if float(bar["high"])>x+buf]
                if not pierced:
                    continue
                funnel["m15_liquidity_sweeps"]+=1;yearly_funnel[d.year]["m15_liquidity_sweeps"]+=1
                level=min(pierced) if side=="BUY" else max(pierced)

                fvg=active_fvg(fvgs,side,t,float(bar["low"]),float(bar["high"]))
                if fvg is None:
                    continue
                funnel["sweeps_overlapping_h1_fvg"]+=1;yearly_funnel[d.year]["sweeps_overlapping_h1_fvg"]+=1

                closeback=(float(bar["close"])>level) if side=="BUY" else (float(bar["close"])<level)
                if not closeback:
                    continue
                funnel["m15_closeback_confirmations"]+=1;yearly_funnel[d.year]["m15_closeback_confirmations"]+=1

                mss_exp=min(t+pd.Timedelta(minutes=30),ex1t)
                mf=find_mss_and_fvg(side,t,mss_exp,m5,st5)
                if mf is None or not mf.get("mss"):
                    blocked_until=mss_exp
                    continue
                funnel["m5_mss_confirmations"]+=1;yearly_funnel[d.year]["m5_mss_confirmations"]+=1
                if not mf.get("fvg"):
                    blocked_until=mss_exp
                    continue
                funnel["mss_with_displacement_fvg"]+=1;yearly_funnel[d.year]["mss_with_displacement_fvg"]+=1

                entry=float(mf["limit"])
                target=nearest_target(side,entry,asian,london)
                if target is None:
                    blocked_until=mss_exp
                    continue
                funnel["valid_structural_target"]+=1;yearly_funnel[d.year]["valid_structural_target"]+=1
                target_dist=(target-entry) if side=="BUY" else (entry-target)
                if target_dist<5.0:
                    blocked_until=mss_exp
                    continue
                funnel["target_distance_ge_5"]+=1;yearly_funnel[d.year]["target_distance_ge_5"]+=1

                order_end=min(mf["mss_time"]+pd.Timedelta(minutes=30),ex1t)
                funnel["limit_orders_placed"]+=1;yearly_funnel[d.year]["limit_orders_placed"]+=1
                fill=first_limit_fill(side,entry,bid,ask,mf["mss_time"],order_end)
                if fill is None:
                    blocked_until=order_end
                    continue
                funnel["limit_orders_filled"]+=1;yearly_funnel[d.year]["limit_orders_filled"]+=1

                # structural stop
                if side=="BUY":
                    struct_stop=float(bar["low"])-buf
                else:
                    a15=ask15.loc[t] if t in ask15.index else None
                    if a15 is None:
                        struct_stop=float("nan")
                    else:
                        struct_stop=float(a15["high"])+buf

                # micro stop from the two M5 MSS confirmation bars
                j=mf["j"]
                m5a=m5.iloc[j-1:j+1]
                if side=="BUY":
                    micro_stop=float(m5a["low"].min())-buf
                else:
                    t1=m5.index[j-1];t2=m5.index[j]
                    if t1 not in ask5.index or t2 not in ask5.index:
                        micro_stop=float("nan")
                    else:
                        micro_stop=float(max(ask5.loc[t1,"high"],ask5.loc[t2,"high"])+buf)

                struct_valid=math.isfinite(struct_stop) and ((struct_stop<entry) if side=="BUY" else (struct_stop>entry))
                micro_valid=math.isfinite(micro_stop) and ((micro_stop<entry) if side=="BUY" else (micro_stop>entry))
                if struct_valid:
                    funnel["s_struct_valid"]+=1;yearly_funnel[d.year]["s_struct_valid"]+=1
                if micro_valid:
                    funnel["s_micro_valid"]+=1;yearly_funnel[d.year]["s_micro_valid"]+=1

                h60=min(fill+pd.Timedelta(minutes=60),capt)
                h120=min(fill+pd.Timedelta(minutes=120),capt)
                p60=path_metrics(side,entry,fill,bid,ask,h60)
                p120=path_metrics(side,entry,fill,bid,ask,h120)
                if p120 is None:
                    blocked_until=order_end
                    continue

                r={"date":d.isoformat(),"year":d.year,"side":side,"confirm_time":t.isoformat(),
                   "mss_time":mf["mss_time"].isoformat(),"fill_time":fill.isoformat(),
                   "entry":entry,"target":float(target),"target_dist":float(target_dist),
                   "liquidity_level":float(level),"atr15":atr15,
                   "h1_fvg_lower":float(fvg[2]),"h1_fvg_upper":float(fvg[3]),
                   "m5_fvg_lower":float(mf["lower"]),"m5_fvg_upper":float(mf["upper"]),
                   "p60":p60,"p120":p120}

                if struct_valid:
                    r["struct60"]=outcome_for_stop(side,entry,target,struct_stop,fill,bid,ask,h60)
                    r["struct120"]=outcome_for_stop(side,entry,target,struct_stop,fill,bid,ask,h120)
                if micro_valid:
                    r["micro60"]=outcome_for_stop(side,entry,target,micro_stop,fill,bid,ask,h60)
                    r["micro120"]=outcome_for_stop(side,entry,target,micro_stop,fill,bid,ask,h120)
                rows.append(r)
                filled_for_side=True
            # next side
        d+=timedelta(days=1)

    report={"status":"PASS","experiment":"ROOT_RESET_V4_BADAR_CORE","scope":"TRAIN_2016_2021_ONLY",
            "validation_accessed":False,"development_test_accessed":False,"final_oos":"NOT_ACCESSED",
            "funnel":dict(funnel),"yearly_funnel":{str(y):dict(v) for y,v in yearly_funnel.items()},
            "overall":row_summary(rows),"by_side":{},"by_year":{}}
    for side in ("BUY","SELL"):
        report["by_side"][side]=row_summary([r for r in rows if r["side"]==side])
    for y in range(2016,2022):
        report["by_year"][str(y)]=row_summary([r for r in rows if r["year"]==y])

    # Advancement gate
    overall=report["overall"]; yearly=report["by_year"]
    counts=[yearly[str(y)].get("count",0) for y in range(2016,2022)]
    edges=[yearly[str(y)].get("year_path_edge_proxy",float("-inf")) for y in range(2016,2022)]
    entry_pass=(
      overall.get("count",0)>=180 and all(c>=20 for c in counts) and
      (overall.get("median_mfe120_to_median_mae120") or 0)>=1.10 and
      float(np.median(edges))>0 and sum(e>0 for e in edges)>=4 and
      (overall.get("plus5_before3_rate_120") or 0)>=.35
    )
    stop_pass={}
    for label,key in (("S_STRUCT","s_struct_120"),("S_MICRO","s_micro_120")):
        s=overall.get(key,{"n":0})
        yr=[]
        for y in range(2016,2022):
            ys=yearly[str(y)].get(key,{"n":0})
            yr.append(ys.get("mean_net_f10_r"))
        valid=[x for x in yr if x is not None]
        stop_pass[label]=bool(
          s.get("n",0)>0 and (s.get("mean_net_f10_r") or 0)>0 and
          (s.get("profit_factor") or 0)>1 and len(valid)==6 and
          sum(x>0 for x in valid)>=4 and min(valid)>=-.35
        )
    report["advancement"]={"entry_population_pass":bool(entry_pass),"stop_hypotheses_pass":stop_pass,
                           "eligible_for_future_2022_preregistration":bool(entry_pass and any(stop_pass.values()))}

    out=Path("data/reports/root-reset-v4/badar-core-train.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","filled_trades":len(rows),"advancement":report["advancement"],
                      "validation_accessed":False,"development_test_accessed":False,"final_oos":"NOT_ACCESSED"},indent=2))

if __name__=="__main__":
    main(sys.argv)
