# Exness MT5 Tick-History Boundary Findings

Status: COMPLETE

Source: read-only Windows MT5 boundary probe supplied by the owner.

## Result

The monthly probe scanned 45 monthly windows from September 2026 backward through January 2023.

Earliest sampled month returning XAUUSD BID+ASK ticks:
- January 2026
- first returned tick in probe: 2026-01-07 12:00:00.125 UTC
- ticks in 15-minute sample: 4,119

Every sampled monthly window in 2025, 2024, and 2023 returned zero ticks with no MT5 error.

## 2026 spread examples

Observed median spreads in sampled 15-minute windows varied materially:
- Jan 2026: ~0.112
- Feb 2026: ~0.252
- Mar 2026: ~0.277
- Apr 2026: ~0.216
- May 2026: ~0.216
- Jun 2026: ~0.196
- Jul 2026: ~0.168
- Aug 2026: ~0.168
- Sep 2026: ~0.182

These are point samples, not a complete 2026 spread distribution.

## Decision

This Exness demo server is not suitable as the primary source for 2023-2024 historical execution reconstruction.

Use:
- Dukascopy BID+ASK for historical side-aware execution reconstruction;
- Exness MT5 2026 BID+ASK for broker-specific spread/shadow validation and later demo execution verification.

No trading mutation occurred.
No credentials were recorded.
