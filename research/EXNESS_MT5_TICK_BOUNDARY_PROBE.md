# Exness MT5 Tick-History Boundary Probe

After the initial point-sample probe succeeds, run:

```powershell
git pull
python scripts\exness_mt5_tick_boundary_probe.py
```

Default scan:
- one 15-minute midweek UTC window per month;
- September 2026 backward through January 2023;
- BID/ASK information only;
- read-only;
- no order functions.

Output:

`exness_tick_probe\exness_tick_boundary_report.json`

Send that JSON report back.

The monthly scan is deliberately lightweight. It locates the approximate earliest
month exposed by the Exness MT5 server before any large tick download is attempted.
