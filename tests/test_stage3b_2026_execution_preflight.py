"""D-133 fail-closed tests after D-132 consumed the D-124 provider attempt."""
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest
source=Path(__file__).resolve().parents[1]/"scripts"/"stage3b_2026_execution_preflight.py"
spec=importlib.util.spec_from_file_location("stage3b_2026_execution_preflight",source)
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

class TestExecutionPlan(unittest.TestCase):
    def test_attempt_is_consumed_and_execution_fails_closed(self):
        plan=p.proposed_acquisition_plan()
        self.assertTrue(p.ATTEMPT_CONSUMED)
        self.assertEqual(plan["status"],"ATTEMPT_CONSUMED_PROVIDER_TRANSPORT_FAILURE")
        self.assertEqual(plan["attempts_consumed"],1)
        self.assertEqual(plan["provider_requests_performed"],1)
        self.assertEqual(plan["usable_provider_rows"],0)
        self.assertFalse(plan["model_fit_performed"])
        self.assertEqual(len(p.AUTHORIZED_FINAL_DECISION_SHAS),0)
        with self.assertRaises(PermissionError):
            p.require_owner_final_approval(plan)

    def test_scope_remains_frozen(self):
        plan=p.proposed_acquisition_plan()
        self.assertEqual(plan["window"],["2026-06-01T00:00:00Z","2026-10-09T00:00:00Z"])
        self.assertEqual(len(plan["symbols"]),8)
        self.assertEqual(plan["max_attempts"],1)
        self.assertEqual(plan["owner_final_approval_decision_sha"],p.D124_AUTH)
        self.assertEqual(plan["consumed_execution_sha"],p.D132_EXECUTION)

    def test_no_raw_github_upload(self):
        self.assertFalse(p.proposed_acquisition_plan()["raw_artifact_github_upload_allowed"])
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"plan.json"; p.save_plan(path)
            text=path.read_text()
            self.assertIn("ATTEMPT_CONSUMED_PROVIDER_TRANSPORT_FAILURE",text)
            self.assertIn(p.D132_EXECUTION,text)

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
