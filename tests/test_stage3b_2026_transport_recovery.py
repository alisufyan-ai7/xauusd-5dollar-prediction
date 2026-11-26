"""D-137 fail-closed tests after D-136 consumed the D-134 recovery attempt."""
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
p=load("recovery",Path("scripts/stage3b_2026_transport_recovery_preflight.py"))
c=load("classify",Path("scripts/classify_stage3b_transport_log.py"))
class TestRecoveryClosed(unittest.TestCase):
    def test_recovery_attempt_consumed_and_fail_closed(self):
        plan=p.proposed_recovery_plan()
        self.assertEqual(plan["status"],"RECOVERY_ATTEMPT_CONSUMED_HTTP_403_ACCESS_DENIED")
        self.assertEqual(plan["recovery_attempts_consumed"],1)
        self.assertFalse(plan["provider_enabled"])
        self.assertFalse(plan["model_fit_enabled"])
        self.assertFalse(plan["rerun_allowed"])
        self.assertEqual(len(p.AUTHORIZED_RECOVERY_DECISION_SHAS),0)
        with self.assertRaises(PermissionError): p.require_recovery_authorized(plan)
        with self.assertRaises(PermissionError): p.require_recovery_execution_ready(plan)
    def test_observed_sanity_result_is_frozen(self):
        s=p.proposed_recovery_plan()["sanity_result"]
        self.assertEqual(s["symbol"],"XAUUSD_BID")
        self.assertEqual(s["window"],["2026-06-01T00:00:00Z","2026-06-02T00:00:00Z"])
        self.assertEqual(s["http_status"],403)
        self.assertFalse(s["waf_token_used"])
        self.assertEqual(s["classification"],"HTTP_403_ACCESS_DENIED")
        self.assertFalse(s["file_saved"])
        self.assertEqual(s["usable_rows"],0)
        plan=p.proposed_recovery_plan()
        self.assertFalse(plan["full_acquisition_started"])
        self.assertFalse(plan["model_fit_performed"])
        self.assertEqual(plan["scientific_result"],"NOT_TESTED")
    def test_classifier_still_distinguishes_403_from_202_and_empty(self):
        self.assertEqual(c.classify("dukascopy-node:waf HTTP 403 https://x (WAF token: no)\nSomething went wrong: denied")["category"],"HTTP_403_ACCESS_DENIED")
        self.assertEqual(c.classify("dukascopy-node:waf HTTP 202 https://x (WAF token: no)\nSomething went wrong: challenge")["category"],"HTTP_202_WAF_CHALLENGE")
        self.assertEqual(c.classify("Request returned an empty dataset for https://x")["category"],"VALID_HTTP200_EMPTY_DATASET")
if __name__=="__main__": unittest.main()
