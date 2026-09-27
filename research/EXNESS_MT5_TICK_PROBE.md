# Exness MT5 Historical Tick Probe

## Purpose

This is a read-only diagnostic for determining whether the Exness MT5 demo server exposes useful historical XAUUSD BID/ASK tick data.

It does not place, modify, or close trades and does not write account credentials to disk.

The script uses the official MetaTrader 5 Python integration to request historical ticks with COPY_TICKS_INFO, which returns BID/ASK-change ticks.

Script:

`scripts/exness_mt5_tick_probe.py`

## What is required

On the Windows machine:

1. MetaTrader 5 desktop terminal installed.
2. Exness demo account already logged in inside that MT5 terminal.
3. XAUUSD visible/available in Market Watch.
4. Python installed.
5. MetaTrader5 Python package installed.

No Exness password, account number, API key, or other credential should be pasted into ChatGPT or committed to GitHub.

## One-time Windows setup

Open PowerShell.

Check Python:

```powershell
python --version
```

Install the MT5 Python package:

```powershell
python -m pip install --upgrade MetaTrader5
```

Clone/open this project's repository and switch to the research branch containing the probe script.

## Before running

1. Start the Exness MetaTrader 5 terminal.
2. Log in to the DEMO account normally inside MT5.
3. Leave MT5 running.
4. Open Market Watch.
5. Confirm the exact gold symbol shown by Exness.

If it is `XAUUSD`, use the default command below.

If Exness shows another exact symbol, such as a suffix/prefix variant, pass it with `--symbol`.

## Run

From the repository root:

```powershell
python scripts\exness_mt5_tick_probe.py
```

For a different exact symbol:

```powershell
python scripts\exness_mt5_tick_probe.py --symbol "EXACT_SYMBOL_HERE"
```

If Python cannot automatically locate the terminal:

```powershell
python scripts\exness_mt5_tick_probe.py --terminal-path "C:\Program Files\MetaTrader 5\terminal64.exe"
```

Use the actual terminal path installed on that machine.

## What it probes

The script requests small 15-minute historical windows around:

- September 2026
- January 2025
- January 2024
- January 2023
- January 2020
- January 2016

It does not attempt a large historical download.

For each probe it records:

- tick count;
- first/last returned tick timestamp;
- valid BID count;
- valid ASK count;
- valid BID+ASK count;
- minimum spread;
- median spread;
- mean spread;
- 95th-percentile spread;
- maximum spread.

Times are explicitly requested and reported in UTC.

## Output

A local directory is created:

`exness_tick_probe\`

Main result:

`exness_tick_probe\exness_tick_probe_report.json`

Small CSV samples are also written for each probe window.

The report intentionally omits the MT5 account login/number.

## What to send back

Send only:

`exness_tick_probe_report.json`

You may also send one or more generated sample CSV files if deeper verification is needed.

Do NOT send:

- MT5 password;
- Exness password;
- investor password;
- account credentials;
- authentication cookies;
- private keys.

## Interpretation

If 2023 and 2024 probes return substantial BID+ASK tick data, we can test a larger Exness historical acquisition for DEVELOPMENT_TEST execution validation.

If deep history is unavailable, that is still useful evidence. We can use Dukascopy historical BID+ASK for long-history execution reconstruction and reserve Exness MT5 for recent broker-specific spread/slippage validation.
