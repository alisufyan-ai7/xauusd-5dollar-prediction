# D-152 — Owner Authorization for One D-148 FREESERV Provider Attempt

**STATUS: OWNER AUTHORIZED / EXACTLY ONE ATTEMPT / ZERO RETRIES / NO RERUN**

Recorded owner authorization, verbatim:

> **I authorize one Stage 3B provider-access attempt under D-148 using the preregistered DUKASCOPY_FREESERV_CHART_JSON3_M1_V1 representation through Dukascopy's FREESERV chart/json3 transport, limited to the frozen eight logical M1 series and 2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z. The attempt must begin with exactly eight sanity requests, one per logical series, with a maximum sanity limit of 2 rows per request. If and only if all eight sanity requests pass, full acquisition may proceed using a maximum page limit of 30,000 rows, no more than 11 full requests per logical series, and a hard maximum of 96 provider requests for the entire attempt. Raw-response data must not exceed 350 MiB and normalized/intermediate data must not exceed 750 MiB. Exactly one attempt is authorized, with zero retries after any provider or transport failure, no alternate host, source, mirror, proxy, VPN, or provider representation, and no rerun. All existing D-124/D-116 teacher data, 92/155 feature allowlists, 39 LODO folds, bounded cold-start and macro fail-closed semantics, synchronization and synthetic-DXY rules, models, preprocessing, event weighting and pooling, bootstrap, metrics, thresholds, date boundaries, sealed periods, quarantine/shadow restrictions, and broker restrictions remain unchanged.**

## Immutable execution scope

- Provider representation: `DUKASCOPY_FREESERV_CHART_JSON3_M1_V1`
- Endpoint: `https://freeserv.dukascopy.com/2.0/index.php` with `path=chart/json3`, `interval=1MIN`.
- Eight logical series: XAU/USD BID+ASK; EUR/USD, USD/JPY, GBP/USD, USD/CAD, USD/SEK, USD/CHF BID.
- Half-open UTC window: `2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`.
- Exactly eight initial sanity requests, each with limit <=2; failure of any sanity request consumes/stops the attempt.
- On sanity success only: limit <=30,000 per full request, <=11 full requests per logical series, <=96 provider requests overall.
- Raw response <=367,001,600 bytes (350 MiB); normalized/intermediate <=786,432,000 bytes (750 MiB).
- Exactly one provider attempt. Zero retries on provider or transport failure; no alternate host, source, mirror, proxy, VPN, or representation. No rerun.
- No raw/derived market data committed to GitHub; compact diagnostic/metrics evidence only.
- D-124/D-116 scientific invariants, sealed periods, quarantine, shadow and broker restrictions all unchanged.

## Acceptance sequence

1. Freeze this owner authorization on the active research branch.
2. Prepare a separate **one-time** D-148 execution workflow and an exact-SHA guard referencing *this authorization commit* (not a floating branch).
3. Review deterministic code, scope, no-retry/host guard, test harness and workflow syntax before triggering.
4. Enable provider access and create the immutable one-time trigger only after no-provider checks accept; this is the point the authorized attempt may start.
5. Capture actual provider outcome; regardless of outcome, disable executable provider access, remove trigger, and record final Stage 3B scientific state without retries or reruns.

No owner-operated AWS/account/credential or external setup is required.
