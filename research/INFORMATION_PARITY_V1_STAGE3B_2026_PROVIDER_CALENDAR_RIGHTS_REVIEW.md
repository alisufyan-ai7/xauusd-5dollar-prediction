# D-119 — 2026 source-rights, point-in-time calendar and warm-up evidence matrix

Status: **PUBLIC-DOCUMENT REVIEW COMPLETED; PROVIDER RIGHTS / FULL POINT-IN-TIME CALENDAR / STRUCTURAL WARM-UP STILL UNSATISFIED**.

Read-only review on 2026-11-27, under Option B design-only approval. **No historical quote downloads or provider API calls.** This is a provenance / constraints audit, not legal advice or commercial permission.

## Market provider

| Evidence | Source / observation | Gate |
|---|---|---|
| Historical quote export | https://www.dukascopy.com/api/data/get/historical-data-export (official describes BID/ASK and volumes) | **SOURCE DOCUMENTED; entitlement NOT ESTABLISHED** |
| Data-feed historical guide | https://wiki.dukascopy.com/en/development/data-export/ (official guide; an S3 Requester Pays route can incur AWS charges/needs credentials) | **SOURCE DOCUMENTED; no paid access or credentials used** |
| Official Bank terms | https://www.dukascopy.com/swiss/english/legal-pages/terms-of-use/ | **BLOCKED FOR AUTOMATED FUTURE EXECUTION pending acceptable written authorization/legal basis** |

Bank terms reviewed directly: website access is generally restricted to personal noncommercial use; section 3 forbids automated scraper/bot/data-mining acquisition without **prior express written consent**; section 4 licenses downloaded website content only on a limited personal noncommercial basis. A free download tool, prior TRAIN research use or a third-party open-source downloader does not establish the right to automate new 2026 acquisition for this project. Before any provider calls, obtain unambiguous rights covering the intended automated method, the eight M1 series, the June–October date fence, research storage/processing and artifact/data-retention treatment. Do not commit or redistribute provider raw market files. An alternate licensed provider would require a **new source/protocol addendum**; do not silently substitute one.

**Owner-dependent gate:** evidence of existing permitted access, or provider's explicit written authorization/licence and any paid account/cost acceptance, may need the owner. Merely saying 'I approve the experiment' does **not** waive provider restrictions.

## First-party scheduled macro archives

| Family | Official review source | Finding | Execution status |
|---|---|---|---|
| CPI, NFP, JOLTS | https://www.bls.gov/schedule/2026/ ; monthly historical lists and their 'Last Modified Date' statements | 2026 public release schedule exists in ET; individual month revisions and the time its *future schedule* was known require event-by-event publication-version evidence | **PARTIAL / NOT CERTIFIED** |
| FOMC | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | 2026 meeting calendar and statement pages available; meeting announcement's earlier-publication version and exact decision release availability distinct from hindsight statement URLs | **PARTIAL / NOT CERTIFIED** |
| GDP | https://www.bea.gov/news/schedule/full | Official 2026 release schedule, but currently displayed schedule is not proof of availability at each historical decision minute or that subsequently revised dates were foreknown | **PARTIAL / NOT CERTIFIED** |
| Initial claims | https://www.dol.gov/newsroom/economicdata and https://www.dol.gov/newsroom/releases/eta | Weekly historical release statements can establish *past* releases, but 2026 future holiday and rescheduling publication versions are not yet reconstructed | **PARTIAL / NOT CERTIFIED** |

Rules for later completion (source-only and no outcome peeking):
1. For each 2026 event within the proposed research fence, store `agency`, `family`, `release_time_utc`, `announced_at_utc` (proof, not inferred), immutable archive URL/revision identity and ET→UTC offset (DST).
2. Do not feed a future scheduled release into decision-time features until evidence establishes `announced_at_utc <= candidate_minute_start`; otherwise represent unavailable/missing consistent with Stage 2 rules.
3. Historical actual/forecast/previous/surprise never admitted. Schedule presence must not be inferred from eventual actual release alone.
4. Existing Stage 2 `acquire_macro_schedule_stage2.py` computes some recurring release patterns and first-party scrape snapshots; that alone is not a source-versioned 2026 point-in-time schedule proof.
5. No retroactive 'it was always known' assumptions. Where verification is impossible, document missingness and abstain/fail source-coverage gate as prescribed; changing channels needs a separate preregistration.

## Research-history warm-up problem (source-code-confirmed)

Accepted `scripts/build_information_parity_stage2_year.py`:
- rolls volume/spread/continuity over at most **240 contiguous M1 bars**;
- computes daily from completed H1 bars and weekly from prior complete D1 bars;
- **carries last confirmed swing with no maximum age** (`asof_event`);
- carries **active FVG without maximum creation-age cap** (`build_fvg_records` + `fvg_state_for_decisions`).

Therefore the proposed `2026-06-01` warm-up start **cannot guarantee equivalence** to continuous historical market state for a 2026-07-06 teacher event. An active swing/FVG could have originated before June 1. Do not claim June 1 passed a continuity test by only checking 240 bars.

Required scientific resolution *before any provider acquisition*: either (a) prove a verified pre-June boundary state snapshot can be carried in from a separately authorized history without retrieving extra forbidden data, or (b) preregister a distinct cold-start/missingness contract that explicitly accepts the Stage 2 representation difference, or (c) obtain further owner date-bound approval with a new prior-history range. None is automatically approved by D-118. Until then **WARMUP_SUFFICIENCY = NOT CERTIFIED**.

## Proposed budget forecast and limits

One controlled 2026 acquisition, **up to eight logical series** (XAUUSD BID/ASK + 6 FX BID), strict half-open `2026-06-01T00:00:00Z` to `2026-10-09T00:00:00Z`, **350 MiB raw / 750 MiB normalized** caps, one attempt, no ticks. The Stage 2 accepted TRAIN raw count of 932,099,909 bytes across six calendar years indicates a coarse linear budget interpolation of roughly 55 MB for 130 days; **that is not a verified 2026 size or entitlement**, and does not remove the stop-on-overrun rule. No market quote rows were downloaded to check.

## Outcome

Provider docs exist; point-in-time calendar source families have legitimate primary archives; code-level warm-up limitation is confirmed. **Neither entitlement, point-in-time completeness nor warm-up equivalence is certified.** Execution remains blocked by these independent gates and by D-088/final owner approval.


---

## D-120 owner-confirmed access clarification (2026-11-27)

The owner states they already possess **written permission or a data licence allowing automated Dukascopy historical-data acquisition for this project**. This statement supersedes D-119's *unverified owner entitlement* as an owner-input blocker. Do not repeatedly request licence documents or represent its absence as grounds to halt documentation/testing. **This is an owner assertion; exact licence wording/coverage was not independently examined here and is not disclosed.** Future authorized acquisition must still respect vendor terms, budgets, security and the agreed method. This confirmation is **not** the separately required final scientific/execution approval.

Calendar evidence inventory: `research/reference/information-parity-v1/stage3b-2026-macro-asof-evidence-v1.json`. FOMC 2026 meetings were published by the Fed in August 2024; BLS monthly modified dates differ, and some August release times cannot be certified from the current month's last-modified metadata. Unknown future-schedule rows remain unknown and may not be retroactively filled.
