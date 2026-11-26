"""D-135 no-provider guard for the D-134 transport-recovery authorization."""
from __future__ import annotations
import json

D134_RECOVERY_AUTH="8cdd4edf222b88ac1d7ce15e3d3ac8639a2be155"
D124_AUTH="c99ad84e4b7254d074b96df7a5f4c371ccbe01c2"
D132_EXECUTION="707bdf424b4a810c93dc9ae7d30a07aff245582c"
TRANSPORT_VERSION="1.51.1"
TRANSPORT_UPSTREAM_COMMIT="068bf57b67e3cae3f5c952653ef20157d3852699"
START="2026-06-01T00:00:00Z"
END="2026-10-09T00:00:00Z"
SANITY_START="2026-06-01T00:00:00Z"
SANITY_END="2026-06-02T00:00:00Z"
SYMBOLS=("XAUUSD_BID","XAUUSD_ASK","EURUSD_BID","USDJPY_BID","GBPUSD_BID","USDCAD_BID","USDSEK_BID","USDCHF_BID")
AUTHORIZED_RECOVERY_DECISION_SHAS=frozenset({D134_RECOVERY_AUTH})
RECOVERY_PROVIDER_ENABLED=False

def proposed_recovery_plan() -> dict:
    return {
        "status":"RECOVERY_AUTHORIZED_PREFLIGHT_PENDING",
        "recovery_authorization_commit":D134_RECOVERY_AUTH,
        "parent_authorization_commit":D124_AUTH,
        "consumed_parent_execution_commit":D132_EXECUTION,
        "transport":{"package":"dukascopy-node","version":TRANSPORT_VERSION,"upstream_commit":TRANSPORT_UPSTREAM_COMMIT},
        "window":[START,END],
        "sanity_window":[SANITY_START,SANITY_END],
        "sanity_symbol":"XAUUSD_BID",
        "symbols":list(SYMBOLS),
        "max_recovery_attempts":1,
        "recovery_attempts_consumed":0,
        "provider_enabled":RECOVERY_PROVIDER_ENABLED,
        "model_fit_enabled":RECOVERY_PROVIDER_ENABLED,
        "same_scientific_scope_as_d124":True,
        "rerun_allowed":False,
    }

def require_recovery_authorized(plan: dict) -> None:
    sha=plan.get("recovery_authorization_commit")
    if sha not in AUTHORIZED_RECOVERY_DECISION_SHAS:
        raise PermissionError("recovery authorization SHA is not admitted")
    if plan.get("transport",{}).get("version") != TRANSPORT_VERSION:
        raise PermissionError("recovery transport version changed")
    if plan.get("window") != [START,END] or plan.get("symbols") != list(SYMBOLS):
        raise PermissionError("recovery scientific scope changed")
    if plan.get("max_recovery_attempts") != 1 or plan.get("rerun_allowed") is not False:
        raise PermissionError("recovery attempt budget changed")

def require_recovery_execution_ready(plan: dict) -> None:
    require_recovery_authorized(plan)
    if not RECOVERY_PROVIDER_ENABLED or not plan.get("provider_enabled"):
        raise PermissionError("D134 recovery is authorized but provider execution remains gated on D135 exact-runtime preflight")

if __name__=="__main__":
    plan=proposed_recovery_plan()
    require_recovery_authorized(plan)
    print(json.dumps(plan,indent=2,sort_keys=True))
