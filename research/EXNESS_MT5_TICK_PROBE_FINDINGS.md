# Exness MT5 Tick Probe Findings

Status: INITIAL PROBE COMPLETE

## Environment

- Symbol: XAUUSD
- MetaTrader5 Python package: 5.0.6090
- Terminal build: 500 / 6182 / 5 Sep 2026
- Symbol digits: 3
- Symbol point: 0.001
- Probe window length: 15 minutes
- Read-only: yes

## Recent 2026 sample

Requested:
2026-09-01 12:00:00 UTC to 12:15:00 UTC

Returned:
- ticks: 4,697
- valid BID ticks: 4,697
- valid ASK ticks: 4,697
- valid BID+ASK ticks: 4,697
- spread min: ~0.182
- spread median: ~0.182
- spread mean: ~0.182
- spread p95: ~0.182
- spread max: ~0.182

Conclusion:
The Exness MT5 demo server exposes contemporaneous XAUUSD BID+ASK tick history suitable for broker-specific spread validation.

## Older point probes

The sampled 15-minute windows in:
- January 2025
- January 2024
- January 2023
- January 2020
- January 2016

returned zero ticks with no MT5 error.

Interpretation:
These point samples do not prove the entire older periods are unavailable. A monthly boundary scan is required to identify the approximate earliest available Exness tick-history month.

Next tool:
scripts/exness_mt5_tick_boundary_probe.py

No credentials were recorded and no trading mutation occurred.
