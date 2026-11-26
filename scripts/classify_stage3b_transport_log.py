#!/usr/bin/env python3
"""Classify sanitized dukascopy-node 1.51.1 transport diagnostics."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ANSI=re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
HTTP=re.compile(r"\bHTTP\s+(\d{3})\b")
TOKEN=re.compile(r"(aws-waf-token=)[^\s;]+",re.I)

def classify(text: str) -> dict:
    clean=ANSI.sub("",text)
    clean=TOKEN.sub(r"\1<REDACTED>",clean)
    statuses=[int(x) for x in HTTP.findall(clean)]
    saved="File saved:" in clean
    failed=("Something went wrong:" in clean or "DOWNLOAD_FAILED:" in clean or "VALIDATION_FAILED:" in clean)
    empty="Request returned an empty dataset" in clean
    access=("DukascopyAccessDeniedError" in clean or "access denied" in clean.lower())
    invalid=("Invalid Dukascopy JSON" in clean or "Expected Dukascopy JSON" in clean)
    if saved and statuses:
        category="SUCCESS_AFTER_WAF_OR_HTTP_RECOVERY"
    elif saved:
        category="SUCCESS_NO_REPORTED_HTTP_CHALLENGE"
    elif 403 in statuses or access:
        category="HTTP_403_ACCESS_DENIED"
    elif 202 in statuses:
        category="HTTP_202_WAF_CHALLENGE"
    elif empty:
        category="VALID_HTTP200_EMPTY_DATASET"
    elif invalid:
        category="INVALID_OR_NONJSON_RESPONSE"
    elif failed:
        category="TRANSPORT_ERROR_OTHER"
    else:
        category="UNKNOWN"
    interesting=[]
    for line in clean.splitlines():
        if ("dukascopy-node:waf" in line or "Something went wrong:" in line or
            "Request returned an empty dataset" in line or "File saved:" in line or
            "DukascopyAccessDeniedError" in line or "Invalid Dukascopy JSON" in line or
            "Expected Dukascopy JSON" in line or "dukascopy-node:cli:version" in line):
            interesting.append(line[-1000:])
    return {"category":category,"http_statuses":statuses,"file_saved":saved,
            "terminal_error_observed":failed,"valid_empty_dataset_error":empty,
            "access_denied_observed":access,"invalid_response_observed":invalid,
            "diagnostic_excerpt":interesting[-40:]}

def main(argv):
    if len(argv)!=3:
        raise SystemExit("usage: classify_stage3b_transport_log.py <log> <out.json>")
    obj=classify(Path(argv[1]).read_text(encoding="utf-8",errors="replace"))
    Path(argv[2]).parent.mkdir(parents=True,exist_ok=True)
    Path(argv[2]).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(obj,indent=2,sort_keys=True))
if __name__=="__main__": main(sys.argv)
