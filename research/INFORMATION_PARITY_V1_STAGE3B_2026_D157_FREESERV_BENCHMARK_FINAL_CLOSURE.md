# D-157 — D-148/D-152 FREESERV Stage 3B Execution: Scientific Result and Final Closure

**STATUS: EXECUTION SUCCESS / SOURCE ADEQUATE / FROZEN HYPOTHESIS NEGATIVE / D-152 ATTEMPT CONSUMED / PROVIDER FAIL-CLOSED / NO RERUN**

## Exact authorization and run

- Owner authorization: D-152, commit `ce9e4a1eef48df2e7f1ee8775afe74edc10cbe71`.
- Preregistered representation: `DUKASCOPY_FREESERV_CHART_JSON3_M1_V1`.
- D-153 no-provider hardened preflight: run `45975306543`, job `140425441301`; Python 3.12.14, 18/18 mocked tests PASS, no market request.
- D-154 one-time execution-readiness document: commit `e9bdd9daf6af2fe94c16db17aa717810ed3142c8`.
- D-155 **only** execution commit: `910184e82d82da26774795e6608da84a2dbca3c9`.
- GitHub Actions run: **45975512932**; job **140426128757**; run attempt **1**.
- Run URL: https://github.com/alisufyan-ai7/xauusd-5dollar-prediction/actions/runs/45975512932
- Run conclusion: **SUCCESS**; 2026-11-27 09:39:23–09:42:20 UTC.
- Frozen Stage 3B runtime: CPython 3.12.14; scikit-learn 1.8.0; seed 20261010.
- Immutable trigger, exact runtime, dependency lock, deterministic tests, acquisition, causal features, dataset, benchmark and cleanup/upload: all PASS.
- **D-152 authorization is now consumed. No rerun.**

D-156 seal commit `a29d3a1c538c942400532d7391c18a06de7818a0` was made after D-155 checkout while its one-time job was running; it restored `PROVIDER_EXECUTION_ENABLED=False`, emptied `AUTHORIZED_D148_DECISION_SHAS`, and deleted the one-time execution trigger. This did **not** alter the D-155 pinned run.

## Source acquisition: successful and within authorization

Frozen market window:
`2026-06-01T00:00:00Z <= t < 2026-10-09T00:00:00Z`.

- Exactly **8** sanity requests, each HTTP 200 and each returning **2** decoded rows.
- **40** subsequent full-page requests: **5 per logical series**, each below the 11-per-series cap.
- **48** provider requests total, versus hard maximum **96**.
- Raw response payload: **79,268,154 bytes** (350 MiB cap: 367,001,600).
- Normalized provider CSV: **56,516,253 bytes**.
- Final derived normalized-size gate: **68,047,560 bytes** (750 MiB cap: 786,432,000).
- Retries: **0**. No alternate host, source, proxy, VPN, mirror or representation.
- Source adequacy: **ADEQUATE**.

Accepted eight M1 series and row counts:

| Series | Rows | Full requests |
|---|---:|---:|
| XAU/USD BID | 129,086 | 5 |
| XAU/USD ASK | 129,086 | 5 |
| EUR/USD BID | 134,662 | 5 |
| USD/JPY BID | 134,829 | 5 |
| GBP/USD BID | 134,717 | 5 |
| USD/CAD BID | 134,349 | 5 |
| USD/SEK BID | 134,558 | 5 |
| USD/CHF BID | 134,537 | 5 |

Total accepted per-series M1 observations: **1,065,824**.

The source is this separately admitted FREESERV chart JSON3 representation, **not a claim of byte equivalence** with Stage-2 JETTA or D-140 direct BI5.

## Dataset and causal feature build

- Dataset build status: **PASS**.
- Candidate dataset SHA-256: `f6efeebfb98e1cb41d2d444a09cd4ea1aa76aa34f617f2c8d13db2f0258b880b`.
- Candidate rows: **343**.
- Scientific evaluated event set: **250**, comprising **107 ACT** and **143 eligible P3**.
- Source dates: **39**.
- XAUUSD state age at scored event positions: maximum **0 minutes**.
- Macro schedule availability: `[0.0]`, reflecting **D-121 UNAVAILABLE_FAIL_CLOSED**, not future backfill.
- Causal layer output feature-ready market share: **0.8248144648**.
- DXY available share: **0.9999380258**.
- D-120 bounded cold start applied; full Stage-2 continuity equivalence was not claimed.
- No 2022–2025 sealed-period data, Oct 9–Nov 30 quarantine or December shadow data was used.

## Frozen benchmark: negative primary scientific result

The exact recorded benchmark states:

`scientific_result = "NEGATIVE FOR FROZEN STAGE 3B HYPOTHESIS"`

`source_adequacy = "ADEQUATE"`

`status = "PASS"` means the **benchmark pipeline executed correctly**, NOT that the hypothesis passed.

Task A (ACT vs eligible P3; n=250, positive ACT=107, negative=143):

| Metric | GOLD | FULL |
|---|---:|---:|
| Pooled ROC-AUC | 0.7057055094 | 0.7026991700 |
| Mean per-date ROC-AUC | 0.5023547440 | 0.4705726372 |
| Brier score | 0.2179810153 | 0.2177027241 |
| Average precision | 0.6738453577 | 0.6823134848 |
| Log loss | 0.6299650638 | 0.6290991440 |

Primary paired-date delta in mean ROC-AUC, FULL minus GOLD:
**−0.0317821068**.

Preregistered paired-date bootstrap 95% confidence interval:
**[−0.1066165547, +0.0324778000]**.

Prerequisite for Task A advancement:
- improvement at least **+0.03**;
- 95% interval lower bound **strictly above zero**;
- Task A Brier nonregression tolerance **+0.01**.

Task A gate: **FAIL**. Its Brier tolerance alone is met; the primary discrimination improvement and positive lower CI are not.

Task B (LONG vs SHORT conditional on ACT; n=107, LONG=47, SHORT=60):

| Metric | GOLD | FULL |
|---|---:|---:|
| ROC-AUC | 0.3312056738 | 0.3617021277 |
| Balanced accuracy | 0.3785460993 | 0.4437943262 |
| Brier score | 0.2748558847 | 0.2842473372 |
| Log loss | 0.7443726878 | 0.7661144998 |

Task B nonregression gate: **PASS**, within frozen balanced-accuracy and Brier tolerances. It does not rescue the primary Task A failure.

Scientific interpretation: adding the FULL feature set **did not demonstrate the preregistered incremental discriminative value over GOLD** in the bounded 2026 teacher/event experiment. It is not evidence of impossibility of XAUUSD prediction, nor a broker-exact trading profitability assessment. Do not retune or rescue this sealed Stage 3B result.

**D-148/D-152 Stage 3B scientific decision: NEGATIVE; no automatic Stage 4/5 promotion, threshold change, shadow deployment, sealed-year opening, or broker activation.**

## Evidence identities and verification

GitHub Actions compact artifact:
- ID: **15187346284**
- Name: `stage3b-2026-d148-d152-single-attempt`
- ZIP size: **27,003 bytes**
- SHA-256: `0d2a502c4a2b0842fb88c241315d32eb7741b6c2b53094c32b0d1a45224f06e0`
- Retention: 90 days, expiry 2027-02-25 UTC.

Important compact evidence file SHA-256:
- `reports/benchmark.json`: `b11d1d4c6b5454b2d6b1863cd4221be36ff8503566b3f24572a6f4a0de8c70ac`
- `reports/dataset.json`: `c9f5940adf434c8c67892b20f43bd818a35a88be8188c9adaca1eee89a5c7497`
- `reports/freeserv-acquisition.json`: `879c6835721d1445032c1d9d8ba0641fbc5905ba9a454404a63d8412f64cd126`
- `manifests/provider-m1-manifest.json`: `01ae7f5d8b779ec46d6ac0cc8cca9f2211b3171b1cfe0ca9bf692cf41fb031b6`
- `manifests/normalized-manifest.json`: `ac69b95ad5fd506f82dacbb1bc2114be42bc7056866b4cf20366823a39b46379`
- `reports/predictions.csv`: `e4f4b7d2e4d4ad381a2d99a528493b3f3198268d7bc7c7c07e0c86c232a2c10e`

Independent ZIP SHA-256 matched GitHub's artifact digest. **14 of the 15 embedded per-file hash entries validate exactly.** The remaining entry is an erroneous *self-reference* for `reports/compact-evidence-sha256.txt`: the SHA written in the file does not equal that completed file's SHA, because the generator hashed its own output while writing it. This is a compact-evidence harness defect, not a benchmark/model error; the ZIP outer digest and other 14 files are intact. No rerun of D-155 is allowed to address this minor manifest issue. Any future unrelated workflow should exclude the manifest itself from its hash input.

Raw and derived market/model payloads were removed before upload; they were never committed to GitHub. Compact reports/predictions/manifest evidence alone were retained in the artifact.

## Closure and next research governance

- D-132: consumed; no rerun.
- D-136: consumed; no rerun.
- D-146: consumed; no rerun.
- **D-155: consumed; no rerun.**
- D-156 seal: provider disabled, executable authorization allowlist empty, one-time trigger removed.
- No owner-operated external setup required.
- D-116 teacher, 92 GOLD / 155 FULL feature allowlists, 39 LODO folds, models, thresholds, source/fold semantics and all sealed/quarantine/shadow/broker restrictions remain unchanged.
- Stage 3B is no longer **NOT TESTED**; it is a **completed negative preregistered experiment with adequate data**.

Next allowed owner-independent work: static scientific result audit, documentation, and development of a **separately preregistered** next research hypothesis/proposal that does not alter or rerun D-155. No further fitting/provider access, no unsealing, no Stage 4/5 or trading mutation without distinct owner approval.
