"""Deterministic tests for the D-124 bounded Stage 3B pipeline implementation."""
import csv, importlib.util, json, tempfile, unittest
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
v=load("provider_guard",Path("scripts/validate_stage3b_2026_provider_files.py"))
b=load("benchmark",Path("scripts/run_stage3b_2026_benchmark.py"))

class TestStage3BPipeline(unittest.TestCase):
    def test_provider_validator_fence(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.csv"
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=v.SCHEMA); w.writeheader()
                w.writerow({"timestamp":v.START_MS,"open":"1","high":"1.1","low":"0.9","close":"1","volume":"1"})
                w.writerow({"timestamp":v.START_MS+60000,"open":"1","high":"1.1","low":"0.9","close":"1","volume":"1"})
            rec=v.validate("XAUUSD_BID",p)
            self.assertEqual(rec["rows"],2)
            with p.open("a",newline="") as f:
                csv.writer(f).writerow([v.END_MS,1,1,1,1,1])
            with self.assertRaises(SystemExit): v.validate("XAUUSD_BID",p)

    def test_event_weights_are_event_and_class_normalized(self):
        df=pd.DataFrame([
            {"event_id":"a","task_a_label":1,"interval_weight":.5},{"event_id":"a","task_a_label":1,"interval_weight":.5},
            {"event_id":"b","task_a_label":1,"interval_weight":1.0},{"event_id":"n","task_a_label":0,"interval_weight":1.0},
        ])
        w=b.event_weights(df,"task_a_label")
        self.assertAlmostEqual(float(w[df.task_a_label.to_numpy()==1].sum()),.5)
        self.assertAlmostEqual(float(w[df.task_a_label.to_numpy()==0].sum()),.5)
        self.assertAlmostEqual(float(w[0]+w[1]),.25)
        self.assertAlmostEqual(float(w[2]),.25)

    def test_all_missing_numeric_is_neutral_and_explicit(self):
        spec={"features":[{"name":"x","arm":"GOLD","dtype":"numeric"}],"categorical_vocabularies":{}}
        df=pd.DataFrame({"market_row_key":[1,2,3],"x":[np.nan,np.nan,np.nan]})
        prep=b.fit_preprocessor(df,spec["features"],spec); x=b.transform(df,prep)
        self.assertEqual(x.shape,(3,2))
        self.assertTrue(np.all(x[:,0]==0))
        self.assertTrue(np.all(x[:,1]==1))

    def test_provider_workflow_one_attempt_and_no_raw_upload(self):
        text=(ROOT/".github/workflows/stage3b-2026-authorized-benchmark.yml").read_text()
        self.assertIn('".github/stage3b-2026-authorized-trigger"',text)
        self.assertNotIn('test "$GITHUB_RUN_NUMBER" = "1"',text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"',text)
        self.assertIn("[STAGE3B_PROVIDER_EXECUTE_D124]",text)
        self.assertIn("D-130 authorized bounded provider execution",text)
        self.assertIn("test -f .github/stage3b-2026-authorized-trigger",text)
        self.assertNotIn("/raw/**",text)
        self.assertNotIn("data/raw",text)
        self.assertIn("Remove provider payloads before artifact upload",text)

if __name__=="__main__": unittest.main()
