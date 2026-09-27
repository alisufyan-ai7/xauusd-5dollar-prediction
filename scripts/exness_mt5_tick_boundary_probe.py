#!/usr/bin/env python3
"""Read-only Exness/MT5 tick-history boundary probe.

Scans one small midweek UTC window per month backward through history to locate
how far Exness MT5 exposes XAUUSD BID/ASK ticks. No trading functions are used.
"""

from __future__ import annotations
import argparse, json, math
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import MetaTrader5 as mt5
except ImportError:
    raise SystemExit("Install MetaTrader5 first: python -m pip install MetaTrader5")

UTC=timezone.utc

def month_iter(start_year:int,start_month:int,end_year:int,end_month:int):
    y,m=start_year,start_month
    while (y,m) >= (end_year,end_month):
        yield y,m
        m-=1
        if m==0:
            y-=1;m=12

def first_wednesday_noon(year:int,month:int)->datetime:
    d=datetime(year,month,1,12,0,tzinfo=UTC)
    while d.weekday()!=2:
        d+=timedelta(days=1)
    return d

def summarize(ticks):
    if ticks is None:
        return {"ticks":0,"first_tick_utc":None,"last_tick_utc":None,
                "valid_bid_ask_ticks":0,"spread_median":None,
                "spread_p95":None,"spread_max":None,"error":list(mt5.last_error())}
    rows=len(ticks)
    spreads=[]
    both=0
    for t in ticks:
        bid=float(t["bid"]);ask=float(t["ask"])
        if bid>0 and ask>0:
            both+=1;spreads.append(ask-bid)
    spreads.sort()
    def q(p):
        if not spreads:return None
        pos=(len(spreads)-1)*p
        lo=int(math.floor(pos));hi=int(math.ceil(pos))
        if lo==hi:return spreads[lo]
        w=pos-lo
        return spreads[lo]*(1-w)+spreads[hi]*w
    first=datetime.fromtimestamp(int(ticks[0]["time_msc"])/1000,tz=UTC).isoformat() if rows else None
    last=datetime.fromtimestamp(int(ticks[-1]["time_msc"])/1000,tz=UTC).isoformat() if rows else None
    return {"ticks":rows,"first_tick_utc":first,"last_tick_utc":last,
            "valid_bid_ask_ticks":both,
            "spread_median":q(0.5),"spread_p95":q(0.95),
            "spread_max":max(spreads) if spreads else None,"error":None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--symbol",default="XAUUSD")
    ap.add_argument("--terminal-path",default=None)
    ap.add_argument("--start-year",type=int,default=2026)
    ap.add_argument("--start-month",type=int,default=9)
    ap.add_argument("--end-year",type=int,default=2023)
    ap.add_argument("--end-month",type=int,default=1)
    ap.add_argument("--minutes",type=int,default=15)
    ap.add_argument("--out",default="exness_tick_probe/exness_tick_boundary_report.json")
    args=ap.parse_args()

    ok=mt5.initialize(path=args.terminal_path) if args.terminal_path else mt5.initialize()
    if not ok: raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        info=mt5.symbol_info(args.symbol)
        if info is None: raise SystemExit(f"Symbol {args.symbol!r} not found")
        if not info.visible and not mt5.symbol_select(args.symbol,True):
            raise SystemExit(f"Could not select symbol {args.symbol!r}: {mt5.last_error()}")

        probes=[]
        for y,m in month_iter(args.start_year,args.start_month,args.end_year,args.end_month):
            start=first_wednesday_noon(y,m)
            end=start+timedelta(minutes=args.minutes)
            ticks=mt5.copy_ticks_range(args.symbol,start,end,mt5.COPY_TICKS_INFO)
            s=summarize(ticks)
            s.update({"year":y,"month":m,"requested_from_utc":start.isoformat(),
                      "requested_to_utc":end.isoformat()})
            probes.append(s)

        available=[p for p in probes if p["ticks"]>0]
        earliest=min(available,key=lambda p:(p["year"],p["month"])) if available else None
        report={
            "status":"PASS","read_only":True,"symbol":args.symbol,
            "mt5_package_version":getattr(mt5,"__version__",None),
            "terminal_build":mt5.version(),
            "months_scanned":len(probes),
            "earliest_available_month":{
                "year":earliest["year"],"month":earliest["month"],
                "first_tick_utc":earliest["first_tick_utc"],
                "ticks_in_probe":earliest["ticks"]
            } if earliest else None,
            "probes":probes,
            "privacy_note":"Account login/number intentionally omitted.",
            "trading_note":"No order_send or trading mutation function is used."
        }
        out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2,sort_keys=True))
        print(f"\nSaved report: {out.resolve()}")
    finally:
        mt5.shutdown()

if __name__=="__main__":
    main()
