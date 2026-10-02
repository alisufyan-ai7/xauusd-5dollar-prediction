#!/usr/bin/env python3
"""Acquire and normalize the Stage 2 V1 first-party U.S. macro schedule.

Schedule only. This script deliberately excludes actual/forecast/previous/
revision/surprise values.

Sources:
- BLS yearly historical release schedules: CPI, Employment Situation, JOLTS
- Federal Reserve historical FOMC pages + statement pages
- BEA national GDP archive + release pages
- DOL/ETA UI Weekly Claims official publication rule

ISM is intentionally not synthesized in V1 because historical first-party
holiday exceptions are not reproducibly available from the public archive.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time as time_mod
from calendar import monthcalendar, THURSDAY
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = timezone.utc
UA = "Mozilla/5.0 (compatible; XAUUSD-Information-Parity-Research/1.0; +https://github.com/alisufyan-ai7/xauusd-5dollar-prediction)"

FIELDS = [
    "event_id",
    "event_family",
    "scheduled_time_utc",
    "scheduled_time_local",
    "source_timezone",
    "source_agency",
    "source_document_id_or_url",
    "release_stage",
    "historical_exception_flag",
    "normalization_version",
]
VERSION = "IPV1_MACRO_SCHEDULE_V1"

FAMILY_FLOORS = {
    "CPI": 11,
    "NFP": 11,
    "JOLTS": 11,
    "FOMC": 8,
    "CLAIMS": 50,
    "GDP": 11,
}


@dataclass(frozen=True)
class Event:
    family: str
    dt_local: datetime
    agency: str
    source: str
    stage: str = ""
    exception: int = 0

    def row(self) -> dict[str, str]:
        local = self.dt_local.astimezone(ET)
        utc = local.astimezone(UTC)
        token = f"{self.agency}|{self.family}|{utc.isoformat()}|{self.stage}|{self.source}"
        event_id = hashlib.sha256(token.encode()).hexdigest()[:20]
        return {
            "event_id": event_id,
            "event_family": self.family,
            "scheduled_time_utc": utc.isoformat(),
            "scheduled_time_local": local.isoformat(),
            "source_timezone": "America/New_York",
            "source_agency": self.agency,
            "source_document_id_or_url": self.source,
            "release_stage": self.stage,
            "historical_exception_flag": str(int(self.exception)),
            "normalization_version": VERSION,
        }


class Fetcher:
    def __init__(self, raw_dir: Path):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept": "text/html,*/*"})
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.counter = 0
        self.fetch_log: list[dict] = []

    def get(self, url: str, label: str) -> str:
        last = None
        for attempt in range(3):
            try:
                r = self.session.get(url, timeout=30)
                r.raise_for_status()
                text = r.text
                safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", label)[:120]
                p = self.raw_dir / f"{self.counter:04d}-{safe}.html"
                self.counter += 1
                p.write_text(text, encoding="utf-8")
                self.fetch_log.append({
                    "url": url,
                    "status_code": r.status_code,
                    "bytes": len(r.content),
                    "sha256": hashlib.sha256(r.content).hexdigest(),
                    "raw_file": str(p),
                })
                return text
            except Exception as e:
                last = e
                if attempt < 2:
                    time_mod.sleep(1.0 + attempt)
        raise RuntimeError(f"FETCH_FAILED:{url}:{last}")


def parse_date_time_et(date_text: str, time_text: str) -> datetime:
    d = datetime.strptime(" ".join(date_text.split()), "%A, %B %d, %Y").date()
    t = datetime.strptime(" ".join(time_text.upper().split()), "%I:%M %p").time()
    return datetime.combine(d, t, tzinfo=ET)


def acquire_bls(fetch: Fetcher, year: int) -> tuple[list[Event], list[str]]:
    url = f"https://www.bls.gov/schedule/{year}/"
    errors = []
    events = []
    try:
        html = fetch.get(url, f"bls-{year}")
        soup = BeautifulSoup(html, "html.parser")
        seen = set()
        for tr in soup.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) < 3:
                continue
            date_txt, time_txt, release = cells[0], cells[1], cells[2]
            family = None
            if release.startswith("Consumer Price Index for"):
                family = "CPI"
            elif release.startswith("Employment Situation for"):
                family = "NFP"
            elif release.startswith("Job Openings and Labor Turnover Survey for"):
                family = "JOLTS"
            if family is None or not re.search(r"d{1,2}:d{2}s*[AP]M", time_txt, re.I):
                continue
            try:
                dt = parse_date_time_et(date_txt, time_txt)
            except Exception as e:
                errors.append(f"BLS_PARSE:{year}:{date_txt}:{time_txt}:{release}:{e}")
                continue
            key = (family, dt)
            if key in seen:
                continue
            seen.add(key)
            events.append(Event(
                family=family,
                dt_local=dt,
                agency="BLS",
                source=url,
            ))
    except Exception as e:
        errors.append(str(e))
    return events, errors


def parse_release_time(text: str) -> tuple[int, int] | None:
    m = re.search(
        r"For\s+release\s+at\s+(\d{1,2}):(\d{2})\s*([ap])\.m\.",
        text,
        re.I,
    )
    if not m:
        return None
    h = int(m.group(1))
    minute = int(m.group(2))
    ap = m.group(3).lower()
    if ap == "p" and h != 12:
        h += 12
    if ap == "a" and h == 12:
        h = 0
    return h, minute


def acquire_fomc(fetch: Fetcher, year: int) -> tuple[list[Event], list[str]]:
    base = f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm"
    events = []
    errors = []
    try:
        html = fetch.get(base, f"fomc-history-{year}")
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = urljoin(base, a["href"])
            txt = a.get_text(" ", strip=True).lower()
            if "statement" not in txt:
                continue
            m = re.search(r"monetary(\d{8})a\.htm", href, re.I)
            if m and int(m.group(1)[:4]) == year:
                links.append((m.group(1), href))
        seen = set()
        for ymd, href in sorted(set(links)):
            try:
                page = fetch.get(href, f"fomc-statement-{ymd}")
                text = BeautifulSoup(page, "html.parser").get_text(" ", strip=True)
                hm = parse_release_time(text)
                if hm is None:
                    errors.append(f"FOMC_TIME_PARSE:{href}")
                    continue
                d = datetime.strptime(ymd, "%Y%m%d").date()
                dt = datetime.combine(d, time(hm[0], hm[1]), tzinfo=ET)
                key = ("FOMC", dt)
                if key in seen:
                    continue
                seen.add(key)
                events.append(Event(
                    family="FOMC",
                    dt_local=dt,
                    agency="FEDERAL_RESERVE",
                    source=href,
                    stage="statement",
                ))
            except Exception as e:
                errors.append(f"FOMC_PAGE:{href}:{e}")
    except Exception as e:
        errors.append(str(e))
    return events, errors


def parse_bea_embargo(text: str) -> datetime | None:
    # Examples:
    # EMBARGOED UNTIL RELEASE AT 8:30 A.M. EDT, Thursday, April 28, 2016
    m = re.search(
        r"(?:EMBARGOED\s+UNTIL\s+RELEASE\s+AT|RELEASE\s+AT)\s+"
        r"(\d{1,2}):(\d{2})\s*([AP])\.M\.\s+(?:EDT|EST|ET),?\s+"
        r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        text,
        re.I,
    )
    if not m:
        return None
    h = int(m.group(1))
    minute = int(m.group(2))
    ap = m.group(3).lower()
    if ap == "p" and h != 12:
        h += 12
    if ap == "a" and h == 12:
        h = 0
    d = datetime.strptime(m.group(4), "%B %d, %Y").date()
    return datetime.combine(d, time(h, minute), tzinfo=ET)


def gdp_stage(title: str) -> str:
    t = title.lower()
    if "advance estimate" in t:
        return "advance"
    if "second estimate" in t:
        return "second"
    if "third estimate" in t:
        return "third"
    return "other"


def acquire_gdp(fetch: Fetcher, year: int) -> tuple[list[Event], list[str]]:
    events = []
    errors = []
    seen_urls = set()

    for page in range(0, 8):
        url = (
            "https://www.bea.gov/news/archive"
            f"?field_related_product_target_id=451&created_1={year}&page={page}&title="
        )
        try:
            html = fetch.get(url, f"bea-gdp-archive-{year}-{page}")
        except Exception as e:
            errors.append(str(e))
            break
        soup = BeautifulSoup(html, "html.parser")
        page_hits = 0
        for tr in soup.find_all("tr"):
            a = tr.find("a", href=True)
            if a is None:
                continue
            title = a.get_text(" ", strip=True)
            if not title.startswith("Gross Domestic Product,"):
                continue
            href = urljoin(url, a["href"])
            if href in seen_urls:
                continue
            seen_urls.add(href)
            page_hits += 1
            try:
                body = fetch.get(href, f"bea-gdp-release-{year}-{len(seen_urls)}")
                text = BeautifulSoup(body, "html.parser").get_text(" ", strip=True)
                dt = parse_bea_embargo(text)
                if dt is None:
                    errors.append(f"BEA_TIME_PARSE:{href}")
                    continue
                if dt.year != year:
                    continue
                events.append(Event(
                    family="GDP",
                    dt_local=dt,
                    agency="BEA",
                    source=href,
                    stage=gdp_stage(title),
                ))
            except Exception as e:
                errors.append(f"BEA_PAGE:{href}:{e}")
        if page_hits == 0:
            break

    unique = {}
    for e in events:
        unique[(e.family, e.dt_local, e.stage, e.source)] = e
    return sorted(unique.values(), key=lambda e: e.dt_local), errors


def fourth_thursday(year: int, month: int) -> date:
    weeks = monthcalendar(year, month)
    thursdays = [w[THURSDAY] for w in weeks if w[THURSDAY] != 0]
    return date(year, month, thursdays[3])


def claims_holiday(d: date) -> bool:
    if (d.month, d.day) in {(1, 1), (7, 4), (11, 11), (12, 25)}:
        return True
    if d.year >= 2021 and (d.month, d.day) == (6, 19):
        return True
    if d.month == 11 and d == fourth_thursday(d.year, 11):
        return True
    return False


def acquire_claims(year: int) -> tuple[list[Event], list[str]]:
    source = "https://oui.doleta.gov/unemploy/archive.asp"
    d = date(year, 1, 1)
    while d.weekday() != 3:
        d += timedelta(days=1)
    events = []
    while d.year == year:
        release = d
        exception = 0
        if claims_holiday(d):
            release = d - timedelta(days=1)
            exception = 1
        dt = datetime.combine(release, time(8, 30), tzinfo=ET)
        events.append(Event(
            family="CLAIMS",
            dt_local=dt,
            agency="DOL_ETA",
            source=source,
            exception=exception,
        ))
        d += timedelta(days=7)
    return events, []


def validate_rows(rows: list[dict], start_year: int, end_year: int):
    forbidden = {"actual", "forecast", "consensus", "previous", "revised", "surprise"}
    for row in rows:
        if forbidden.intersection(row):
            raise RuntimeError("FORBIDDEN_MACRO_FIELD")
        dt = datetime.fromisoformat(row["scheduled_time_utc"])
        if dt.tzinfo is None:
            raise RuntimeError("NAIVE_MACRO_TIMESTAMP")
        if not (start_year <= dt.year <= end_year):
            raise RuntimeError(f"MACRO_YEAR_OUTSIDE_RANGE:{dt.isoformat()}")


def main(argv: list[str]) -> None:
    if len(argv) != 6:
        raise SystemExit(
            "usage: acquire_macro_schedule_stage2.py "
            "<start-year> <end-year> <out.csv> <coverage.json> <raw-dir>"
        )

    start_year = int(argv[1])
    end_year = int(argv[2])
    if start_year < 2016 or end_year > 2021 or start_year > end_year:
        raise SystemExit("STAGE2_RANGE_VIOLATION: only 2016-2021 allowed")

    out_path = Path(argv[3])
    coverage_path = Path(argv[4])
    raw_dir = Path(argv[5])
    fetch = Fetcher(raw_dir)

    all_events: list[Event] = []
    years = {}

    for year in range(start_year, end_year + 1):
        yearly_events: list[Event] = []
        errors: list[str] = []

        for func in (
            lambda: acquire_bls(fetch, year),
            lambda: acquire_fomc(fetch, year),
            lambda: acquire_gdp(fetch, year),
            lambda: acquire_claims(year),
        ):
            ev, err = func()
            yearly_events.extend(ev)
            errors.extend(err)

        # Deduplicate exact family/timestamp/source/stage identity.
        unique = {}
        for e in yearly_events:
            unique[(e.family, e.dt_local, e.agency, e.source, e.stage)] = e
        yearly_events = sorted(unique.values(), key=lambda e: (e.dt_local, e.family, e.agency))
        all_events.extend(yearly_events)

        counts = {family: 0 for family in FAMILY_FLOORS}
        for e in yearly_events:
            counts[e.family] = counts.get(e.family, 0) + 1

        family_pass = {
            family: counts.get(family, 0) >= floor
            for family, floor in FAMILY_FLOORS.items()
        }
        years[str(year)] = {
            "counts": counts,
            "family_pass": family_pass,
            "errors": errors,
            "ism_manufacturing_status": "DEFERRED_PUBLIC_HISTORICAL_EXCEPTIONS_UNRESOLVED",
            "ism_services_status": "DEFERRED_PUBLIC_HISTORICAL_EXCEPTIONS_UNRESOLVED",
            "stage2_macro_schedule_available": bool(all(family_pass.values()) and not errors),
        }

    rows = [e.row() for e in sorted(all_events, key=lambda e: (e.dt_local, e.family, e.agency))]
    validate_rows(rows, start_year, end_year)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    coverage = {
        "schema_version": "IPV1_STAGE2_MACRO_COVERAGE_V1",
        "status": "PASS" if all(v["stage2_macro_schedule_available"] for v in years.values()) else "INCOMPLETE",
        "scope": f"{start_year}-{end_year}_TRAIN_ONLY",
        "sealed_xauusd_periods_accessed": [],
        "included_families": sorted(FAMILY_FLOORS),
        "deferred_families": ["ISM_MANUFACTURING", "ISM_SERVICES"],
        "family_sanity_floors": FAMILY_FLOORS,
        "years": years,
        "normalized_rows": len(rows),
        "fetch_log": fetch.fetch_log,
    }
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(coverage, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
