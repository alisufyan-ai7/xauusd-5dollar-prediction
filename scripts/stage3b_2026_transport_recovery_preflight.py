"""D-137 fail-closed guard after the single D-134 recovery attempt was consumed."""
from __future__ import annotations
import json

D134_RECOVERY_AUTH="8cdd4edf222b88ac1d7ce15e3d3ac8639a2be155"
D136_EXECUTION="c20e987e559f9ed4a1c7d8d5674e017baeb211b9"
D135_PREFLIGHT_RUN=45901246019
D135_PREFLIGHT_JOB=140187267884
TRANSPORT_VERSION="1.51.1"
START="2026-06-01T00:00:00Z"
END="2026-10-09T00:00:00Z"
SYMBOLS=("XAUUSD_BID","XAUUSD_ASK","EURUSD_BID","USDJPY_BID","GBPUSD_BID","USDCAD_BID","USDSEK_BID","USDCHF_BID")
RECOVERY_PROVIDER_ENABLED=False
AUTHORIZED_RECOVERY_DECISION_SHAS=frozenset()

def proposed_recovery_plan() -> dict:
    return {
        "status":"RECOVERY_ATTEMPT_CONSUMED_HTTP_403_ACCESS_DENIED",
        "recovery_authorization_commit":D134_RECOVERY_AUTH,
        "consumed_recovery_execution_commit":D136_EXECUTION,
        "preflight":{"passed":True,"workflow_run_id":D135_PREFLIGHT_RUN,"workflow_job_id":D135_PREFLIGHT_JOB},
        "transport":{"package":"dukascopy-node","version":TRANSPORT_VERSION},
        "window":[START,END],
        "symbols":list(SYMBOLS),
        "max_recovery_attempts":1,
        "recovery_attempts_consumed":1,
        "provider_enabled":False,
        "model_fit_enabled":False,
        "sanity_result":{
            "symbol":"XAUUSD_BID",
            "window":["2026-06-01T00:00:00Z","2026-06-02T00:00:00Z"],
            "http_status":403,
            "waf_token_used":False,
            "classification":"HTTP_403_ACCESS_DENIED",
            "file_saved":False,
            "usable_rows":0,
        },
        "full_acquisition_started":False,
        "model_fit_performed":False,
        "scientific_result":"NOT_TESTED",
        "rerun_allowed":False,
    }

def require_recovery_authorized(plan: dict) -> None:
    raise PermissionError("D134 recovery authorization was consumed by D136; no provider recovery is currently authorized")

def require_recovery_execution_ready(plan: dict) -> None:
    raise PermissionError("D136 recovery attempt consumed on plain HTTP 403; new provider-access strategy authorization required")

if __name__=="__main__":
    print(json.dumps(proposed_recovery_plan(),indent=2,sort_keys=True))
