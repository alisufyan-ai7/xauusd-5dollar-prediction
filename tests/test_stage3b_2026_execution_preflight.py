"""D-121 no-provider tests: immutable source bounds, lock check and final-approval stop."""
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest

source=Path(__file__).resolve().parents[1]/"scripts"/"stage3b_2026_execution_preflight.py"
spec=importlib.util.spec_from_file_location("stage3b_2026_execution_preflight",source)
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class TestExecutionPlan(unittest.TestCase):
    def test_no_provider_requests_and_user_approval_required(self):
        plan=p.proposed_acquisition_plan()
        self.assertEqual(plan["provider_requests_performed"],0)
        self.assertEqual(len(plan["symbols"]),8)
        with self.assertRaises(PermissionError): p.require_owner_final_approval(plan)
        plan["owner_final_approval_decision_sha"]="a"*40
        with self.assertRaises(PermissionError): p.require_owner_final_approval(plan)
        plan["status"]="FINAL_APPROVED"
        with self.assertRaises(PermissionError): p.require_owner_final_approval(plan)
        plan["window"]=["2026-05-01T00:00:00Z", p.END]
        with self.assertRaises(PermissionError): p.require_owner_final_approval(plan)

    def test_empty_authorization_allowlist(self):
        self.assertEqual(len(p.AUTHORIZED_FINAL_DECISION_SHAS), 0)

    def test_no_upload_right(self):
        self.assertFalse(p.proposed_acquisition_plan()["raw_artifact_github_upload_allowed"])
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"plan.json"
            p.save_plan(path)
            self.assertTrue(path.read_text().startswith("{\n"))
            self.assertIn('"DESIGN_ONLY_NOT_APPROVED"',path.read_text())

    def test_hash_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fake.csv"
            path.write_bytes(b"fixture only\n")
            with self.assertRaises(ValueError): p.verify_local_assets(path,path,path)
            self.assertEqual(p.sha256_file(path),hashlib.sha256(b"fixture only\n").hexdigest())

    def test_exact_environment_not_fabricated(self):
        result=p.inspect_environment()
        self.assertEqual(result["expected_python"],"3.12.14")
        self.assertEqual(result["exact_runtime_pass"],result["python"]=="3.12.14" and result["packages"]==result["expected_packages"])

if __name__=="__main__": unittest.main()
