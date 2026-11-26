"""D-125 no-provider tests: exact D-124 approval is admitted, all mutations fail."""
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest
source=Path(__file__).resolve().parents[1]/"scripts"/"stage3b_2026_execution_preflight.py"
spec=importlib.util.spec_from_file_location("stage3b_2026_execution_preflight",source)
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
AUTH="c99ad84e4b7254d074b96df7a5f4c371ccbe01c2"
class TestExecutionPlan(unittest.TestCase):
    def test_exact_owner_approval_is_required_and_admitted(self):
        plan=p.proposed_acquisition_plan()
        self.assertEqual(plan["provider_requests_performed"],0)
        self.assertEqual(len(plan["symbols"]),8)
        self.assertEqual(plan["owner_final_approval_decision_sha"],AUTH)
        self.assertEqual(plan["status"],"FINAL_APPROVED")
        p.require_owner_final_approval(plan)
        for mutation in ({"owner_final_approval_decision_sha":"a"*40},{"status":"DESIGN_ONLY_NOT_APPROVED"},{"window":["2026-05-01T00:00:00Z",p.END]},{"symbols":plan["symbols"]+["BTCUSD_BID"]},{"max_attempts":2}):
            with self.assertRaises(PermissionError): p.require_owner_final_approval({**plan,**mutation})
    def test_authorization_allowlist_exact(self):
        self.assertEqual(p.AUTHORIZED_FINAL_DECISION_SHAS,frozenset({AUTH}))
    def test_no_raw_github_upload(self):
        self.assertFalse(p.proposed_acquisition_plan()["raw_artifact_github_upload_allowed"])
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"plan.json"; p.save_plan(path); text=path.read_text()
            self.assertIn('"FINAL_APPROVED"',text); self.assertIn(AUTH,text)
    def test_hash_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fake.csv"; path.write_bytes(b"fixture only\n")
            with self.assertRaises(ValueError): p.verify_local_assets(path,path,path)
            self.assertEqual(p.sha256_file(path),hashlib.sha256(b"fixture only\n").hexdigest())
    def test_exact_environment_not_fabricated(self):
        result=p.inspect_environment()
        self.assertEqual(result["expected_python"],"3.12.14")
        self.assertEqual(result["exact_runtime_pass"],result["python"]=="3.12.14" and result["packages"]==result["expected_packages"])
if __name__=="__main__": unittest.main()
