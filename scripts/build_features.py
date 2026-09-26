#!/usr/bin/env python3
"""Timestamp-safe EXP-001 expert feature construction V2.

All features for decision row i use only rows <= i. The decision price is the
close of row i, matching EXP-001 labeling semantics.

V2 deliberately uses deterministic price-only context. FINAL_OOS access is
controlled by the calling research pipeline, not by this module.
"""
import bisect
import csv
import math
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

WINDOWS=(5,15,30,60,120,240)
OUT_FIELDS=[
"timestamp","decision_time_ms","reference_price","feature_complete","feature_version",
"ret_1m","ret_5m","ret_15m","ret_30m","ret_60m","ret_120m","ret_240m",
"range_1m","body_1m","body_range_ratio_1m","close_location_1m",
"upper_wick_1m","lower_wick_1m","wick_asymmetry_1m",
"range_15m","range_60m","range_240m",
"dist_high_15m","dist_low_15m","dist_high_60m","dist_low_60m",
"dist_high_240m","dist_low_240m",
"range_position_15m","range_position_60m","range_position_240m",
"rv_5m","rv_15m","rv_30m","rv_60m","rv_120m","rv_240m",
"tr_mean_15m","tr_mean_60m","tr_mean_240m",
"rv_short_long_ratio","compression_expansion_ratio","rv60_percentile_240m",
"recent_5dollar_range_frequency_240m","excursion_up_60m","excursion_down_60m",
"slope_15m","slope_60m","slope_240m",
"higher_high_15m","higher_low_15m","lower_high_15m","lower_low_15m",
"trend_persistence_15m","trend_persistence_60m","trend_persistence_240m",
"directional_agreement_m5_m15_h1_h4",
"previous_day_high_distance","previous_day_low_distance",
"current_day_high_distance","current_day_low_distance","current_day_range_position",
"distance_round_5","distance_round_10",
"consecutive_directional_bars","impulse_15m","pullback_depth_15m",
"impulse_pullback_ratio_15m","return_acceleration_5v15",
"directional_consistency_5m","directional_consistency_15m","directional_consistency_30m",
"hour_utc","weekday_utc","session_utc",
"minutes_since_europe_start","minutes_since_us_start","europe_us_overlap",
"minutes_to_session_transition","session_rv_60m"
]

def session(hour):
    if 0 <= hour < 7: return "ASIA"
    if 7 <= hour < 13: return "EUROPE"
    if 13 <= hour < 21: return "US"
    return "LATE"

def rows(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        yield from csv.DictReader(f)

def div(a,b):
    return a/b if b and math.isfinite(b) else 0.0

def sign(x,eps=1e-12):
    return 1 if x>eps else (-1 if x<-eps else 0)

def rolling_extreme(values,window,want_max=True):
    out=[None]*len(values); q=deque()
    for i,v in enumerate(values):
        while q and q[0] <= i-window: q.popleft()
        if want_max:
            while q and values[q[-1]] <= v: q.pop()
        else:
            while q and values[q[-1]] >= v: q.pop()
        q.append(i)
        if i>=window-1: out[i]=values[q[0]]
    return out

def prefix(values):
    p=[0.0]
    for v in values: p.append(p[-1]+v)
    return p

def psum(p,start,end):
    return p[end+1]-p[start]

def rolling_slope(closes,p_y,p_jy,i,n):
    start=i-n+1
    sy=psum(p_y,start,i)
    sjy=psum(p_jy,start,i)-start*sy
    sx=n*(n-1)/2
    sx2=n*(n-1)*(2*n-1)/6
    den=n*sx2-sx*sx
    return (n*sjy-sx*sy)/den if den else 0.0

def minutes_to_next_transition(minute_of_day):
    bounds=(0,7*60,13*60,21*60,24*60)
    for b in bounds[1:]:
        if minute_of_day < b: return b-minute_of_day
    return 0

def build(inp:Path,out:Path):
    data=list(rows(inp))
    out.parent.mkdir(parents=True,exist_ok=True)
    n=len(data)
    closes=[float(r["close"]) for r in data]
    highs=[float(r["high"]) for r in data]
    lows=[float(r["low"]) for r in data]
    opens=[float(r["open"]) for r in data]
    ts=[int(r["timestamp"]) for r in data]

    one_returns=[0.0]*n
    contiguous=[False]*n
    true_ranges=[0.0]*n
    pos=[0]*n; neg=[0]*n
    for i in range(n):
        if i>0 and ts[i]-ts[i-1]==60000:
            contiguous[i]=True
            one_returns[i]=closes[i]-closes[i-1]
            true_ranges[i]=max(highs[i]-lows[i],abs(highs[i]-closes[i-1]),abs(lows[i]-closes[i-1]))
        else:
            true_ranges[i]=highs[i]-lows[i]
        pos[i]=1 if one_returns[i]>0 else 0
        neg[i]=1 if one_returns[i]<0 else 0

    p_ret2=prefix([x*x for x in one_returns])
    p_tr=prefix(true_ranges)
    p_pos=prefix(pos); p_neg=prefix(neg)
    p_close=prefix(closes)
    p_jclose=prefix([i*v for i,v in enumerate(closes)])

    maxv={w:rolling_extreme(highs,w,True) for w in (15,60,240)}
    minv={w:rolling_extreme(lows,w,False) for w in (15,60,240)}

    range60=[None]*n
    for i in range(59,n): range60[i]=maxv[60][i]-minv[60][i]

    # Previous observed UTC trading-day summary; current-day extrema are online only.
    prev_day_high=[None]*n; prev_day_low=[None]*n
    curr_day_high=[None]*n; curr_day_low=[None]*n
    current_date=None; day_hi=day_lo=None; last_completed=None
    for i,t in enumerate(ts):
        d=datetime.fromtimestamp((t+60000)/1000,tz=timezone.utc).date()
        if current_date is None or d!=current_date:
            if current_date is not None: last_completed=(day_hi,day_lo)
            current_date=d; day_hi=highs[i]; day_lo=lows[i]
        else:
            day_hi=max(day_hi,highs[i]); day_lo=min(day_lo,lows[i])
        if last_completed:
            prev_day_high[i],prev_day_low[i]=last_completed
        curr_day_high[i],curr_day_low[i]=day_hi,day_lo

    # Sliding percentile of rv60 against prior/current 240 observed contiguous-ready values.
    rv60=[None]*n
    for i in range(59,n):
        if all(contiguous[k] for k in range(i-58,i+1)):
            rv60[i]=math.sqrt(psum(p_ret2,i-59,i)/60)
    rv60_pct=[None]*n
    sorted_rv=[]; q=deque()
    for i,v in enumerate(rv60):
        while q and q[0][0] < i-239:
            _,old=q.popleft(); sorted_rv.pop(bisect.bisect_left(sorted_rv,old))
        if v is not None:
            bisect.insort(sorted_rv,v); q.append((i,v))
            rv60_pct[i]=bisect.bisect_right(sorted_rv,v)/len(sorted_rv)

    # Recent frequency of completed 60m ranges >= $5.
    five=[0 if x is None else int(x>=5.0) for x in range60]
    p_five=prefix(five)

    with out.open("w",encoding="utf-8",newline="") as f:
        wri=csv.DictWriter(f,fieldnames=OUT_FIELDS); wri.writeheader()
        for i in range(n):
            dt=datetime.fromtimestamp((ts[i]+60000)/1000,tz=timezone.utc)
            minute=dt.hour*60+dt.minute
            complete=i>=240 and all(contiguous[k] for k in range(i-239,i+1))
            bar_range=highs[i]-lows[i]
            vals={
                "timestamp":ts[i],"decision_time_ms":ts[i]+60000,
                "reference_price":closes[i],"feature_complete":complete,"feature_version":"V2",
                "range_1m":bar_range,"body_1m":closes[i]-opens[i],
                "body_range_ratio_1m":div(abs(closes[i]-opens[i]),bar_range),
                "close_location_1m":div(closes[i]-lows[i],bar_range),
                "upper_wick_1m":highs[i]-max(opens[i],closes[i]),
                "lower_wick_1m":min(opens[i],closes[i])-lows[i],
                "wick_asymmetry_1m":div((highs[i]-max(opens[i],closes[i]))-(min(opens[i],closes[i])-lows[i]),bar_range),
                "hour_utc":dt.hour,"weekday_utc":dt.weekday(),"session_utc":session(dt.hour),
                "minutes_since_europe_start": minute-420 if 420<=minute<780 else "",
                "minutes_since_us_start": minute-780 if 780<=minute<1260 else "",
                "europe_us_overlap": int(780<=minute<900),
                "minutes_to_session_transition":minutes_to_next_transition(minute),
            }
            if complete:
                rets={m:closes[i]-closes[i-m] for m in WINDOWS}
                for m,v in rets.items(): vals[f"ret_{m}m"]=v
                vals["ret_1m"]=closes[i]-closes[i-1]

                for m in (15,60,240):
                    hi=maxv[m][i]; lo=minv[m][i]; rg=hi-lo
                    vals[f"range_{m}m"]=rg
                    vals[f"dist_high_{m}m"]=hi-closes[i]
                    vals[f"dist_low_{m}m"]=closes[i]-lo
                    vals[f"range_position_{m}m"]=div(closes[i]-lo,rg)

                rv={}
                for m in WINDOWS:
                    rv[m]=math.sqrt(psum(p_ret2,i-m+1,i)/m)
                    vals[f"rv_{m}m"]=rv[m]
                vals["tr_mean_15m"]=psum(p_tr,i-14,i)/15
                vals["tr_mean_60m"]=psum(p_tr,i-59,i)/60
                vals["tr_mean_240m"]=psum(p_tr,i-239,i)/240
                vals["rv_short_long_ratio"]=div(rv[15],rv[240])
                vals["compression_expansion_ratio"]=div(vals["range_15m"]*4,vals["range_60m"])
                vals["rv60_percentile_240m"]=rv60_pct[i]
                vals["recent_5dollar_range_frequency_240m"]=psum(p_five,i-239,i)/240

                anchor=closes[i-60]
                vals["excursion_up_60m"]=maxv[60][i]-anchor
                vals["excursion_down_60m"]=anchor-minv[60][i]

                vals["slope_15m"]=rolling_slope(closes,p_close,p_jclose,i,15)
                vals["slope_60m"]=rolling_slope(closes,p_close,p_jclose,i,60)
                vals["slope_240m"]=rolling_slope(closes,p_close,p_jclose,i,240)

                prev_hi=max(highs[i-29:i-14]); prev_lo=min(lows[i-29:i-14])
                cur_hi=max(highs[i-14:i+1]); cur_lo=min(lows[i-14:i+1])
                vals["higher_high_15m"]=int(cur_hi>prev_hi)
                vals["higher_low_15m"]=int(cur_lo>prev_lo)
                vals["lower_high_15m"]=int(cur_hi<prev_hi)
                vals["lower_low_15m"]=int(cur_lo<prev_lo)

                for m in (15,60,240):
                    agg=sign(rets[m])
                    same=psum(p_pos,i-m+1,i) if agg>0 else (psum(p_neg,i-m+1,i) if agg<0 else 0)
                    vals[f"trend_persistence_{m}m"]=same/m

                signs=[sign(rets[5]),sign(rets[15]),sign(rets[60]),sign(rets[240])]
                vals["directional_agreement_m5_m15_h1_h4"]=abs(sum(signs))/4

                vals["previous_day_high_distance"]="" if prev_day_high[i] is None else prev_day_high[i]-closes[i]
                vals["previous_day_low_distance"]="" if prev_day_low[i] is None else closes[i]-prev_day_low[i]
                vals["current_day_high_distance"]=curr_day_high[i]-closes[i]
                vals["current_day_low_distance"]=closes[i]-curr_day_low[i]
                vals["current_day_range_position"]=div(closes[i]-curr_day_low[i],curr_day_high[i]-curr_day_low[i])
                vals["distance_round_5"]=abs(closes[i]-round(closes[i]/5)*5)
                vals["distance_round_10"]=abs(closes[i]-round(closes[i]/10)*10)

                d=sign(vals["ret_1m"]); run=0
                if d:
                    j=i
                    while j>=0 and run<240 and sign(one_returns[j])==d:
                        run+=1; j-=1
                vals["consecutive_directional_bars"]=d*run
                impulse=rets[15]
                pullback=(cur_hi-closes[i]) if impulse>=0 else (closes[i]-cur_lo)
                vals["impulse_15m"]=impulse
                vals["pullback_depth_15m"]=pullback
                vals["impulse_pullback_ratio_15m"]=div(abs(impulse),pullback+1e-9)
                vals["return_acceleration_5v15"]=rets[5]-rets[15]/3
                for m in (5,15,30):
                    agg=sign(rets[m])
                    same=psum(p_pos,i-m+1,i) if agg>0 else (psum(p_neg,i-m+1,i) if agg<0 else 0)
                    vals[f"directional_consistency_{m}m"]=same/m

                # Session-local trailing RV, using only current-session contiguous observations.
                start_hour={"ASIA":0,"EUROPE":7,"US":13,"LATE":21}[session(dt.hour)]
                elapsed=max(1,minute-start_hour*60+1)
                sm=min(60,elapsed)
                vals["session_rv_60m"]=math.sqrt(psum(p_ret2,i-sm+1,i)/sm)
            else:
                for k in OUT_FIELDS:
                    if k not in vals and k not in ("timestamp","decision_time_ms","reference_price","feature_complete","feature_version",
                                                   "range_1m","body_1m","body_range_ratio_1m","close_location_1m",
                                                   "upper_wick_1m","lower_wick_1m","wick_asymmetry_1m",
                                                   "hour_utc","weekday_utc","session_utc",
                                                   "minutes_since_europe_start","minutes_since_us_start","europe_us_overlap",
                                                   "minutes_to_session_transition"):
                        vals[k]=""
            wri.writerow(vals)
    print(f"FEATURES_V2_PASS rows={n} output={out}")

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: build_features.py <raw.csv> <features.csv>")
    build(Path(sys.argv[1]),Path(sys.argv[2]))
