"""D-135 deterministic no-provider tests for the D-134 transport recovery."""
import importlib.util,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
p=load("recovery",Path("scripts/stage3b_2026_transport_recovery_preflight.py"))
c=load("classify",Path("scripts/classify_stage3b_transport_log.py"))
class TestRecovery(unittest.TestCase):
    def test_exact_d134_and_transport_are_frozen(self):
        plan=p.proposed_recovery_plan(); p.require_recovery_authorized(plan)
        self.assertEqual(plan["recovery_authorization_commit"],"8cdd4edf222b88ac1d7ce15e3d3ac8639a2be155")
        self.assertEqual(plan["transport"]["version"],"1.51.1")
        self.assertEqual(plan["window"],["2026-06-01T00:00:00Z","2026-10-09T00:00:00Z"])
        self.assertEqual(len(plan["symbols"]),8); self.assertFalse(plan["rerun_allowed"])
        with self.assertRaises(PermissionError): p.require_recovery_execution_ready(plan)
    def test_scope_mutations_fail(self):
        plan=p.proposed_recovery_plan()
        for bad in (
          {**plan,"recovery_authorization_commit":"a"*40},
          {**plan,"transport":{**plan["transport"],"version":"1.51.2"}},
          {**plan,"window":["2026-05-01T00:00:00Z",plan["window"][1]]},
          {**plan,"symbols":plan["symbols"]+["BTCUSD_BID"]},
          {**plan,"max_recovery_attempts":2},
          {**plan,"rerun_allowed":True},
        ):
            with self.assertRaises(PermissionError): p.require_recovery_authorized(bad)
    def test_transport_log_classification(self):
        self.assertEqual(c.classify("dukascopy-node:waf HTTP 202 https://x (WAF token: no)\nSomething went wrong: WAF")["category"],"HTTP_202_WAF_CHALLENGE")
        self.assertEqual(c.classify("dukascopy-node:waf HTTP 403 https://x (WAF token: yes)\nSomething went wrong: denied")["category"],"HTTP_403_ACCESS_DENIED")
        self.assertEqual(c.classify("Request returned an empty dataset for https://x")["category"],"VALID_HTTP200_EMPTY_DATASET")
        self.assertEqual(c.classify("dukascopy-node:waf HTTP 202 https://x\n√ File saved: x.csv (1 KB)")["category"],"SUCCESS_AFTER_WAF_OR_HTTP_RECOVERY")
        red=c.classify("cookie aws-waf-token=secret123\nSomething went wrong: x")
        self.assertNotIn("secret123",str(red))
    def test_recovery_shell_is_exact_and_separate(self):
        d=(ROOT/"scripts/download_dukascopy_m1_recovery.sh").read_text()
        a=(ROOT/"scripts/acquire_information_parity_stage3b_2026_recovery.sh").read_text()
        self.assertIn('VERSION="1.51.1"',d); self.assertNotIn("1.50.0",d)
        self.assertIn("dukascopy-node:waf",d); self.assertIn("--waf-token-cache-path",d)
        self.assertIn("2026-06-01 2026-06-02",a)
        self.assertLess(a.index("transport-sanity"),a.index("Full frozen acquisition"))
        self.assertIn('rm -rf "$RAW" "$PRIVATE"',a)
        self.assertIn("require_recovery_execution_ready",a)
if __name__=="__main__": unittest.main()
