import io
import lzma
import struct
import sys
import unittest
import urllib.error
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import acquire_dukascopy_public_datafeed_stage3b_2026 as acq
import stage3b_2026_public_datafeed_preflight as gate

class FakeResponse(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(body); self.status=status
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    def getcode(self): return self.status

class TestD144ExecutionSurface(unittest.TestCase):
    def payload(self):
        raw=struct.pack(">5if",0,2650123,2650456,2649987,2650789,12.5)
        return lzma.compress(raw,format=lzma.FORMAT_ALONE)

    def test_exact_d144_authorization_is_frozen_and_provider_disabled(self):
        self.assertEqual(acq.D144_AUTHORIZATION_SHA,"eb05ac27af18f68232d86a9148597aa565688709")
        self.assertEqual(acq.AUTHORIZED_D140_DECISION_SHAS,{acq.D144_AUTHORIZATION_SHA})
        self.assertFalse(acq.PROVIDER_EXECUTION_ENABLED)
        with self.assertRaises(PermissionError): acq.require_execution_authorized()

    def test_only_frozen_direct_datafeed_host_is_accepted(self):
        with self.assertRaises(PermissionError):
            acq.fetch_once("https://example.com/datafeed/XAUUSD/2026/05/01/BID_candles_min_1.bi5",opener=lambda *a,**k: FakeResponse(b""))

    def test_fetch_once_is_single_call_and_decodable(self):
        calls=[]; body=self.payload()
        def opener(req,timeout=0): calls.append((req.full_url,timeout)); return FakeResponse(body,200)
        u=gate.build_url(gate.RequestSpec("XAUUSD","BID",date(2026,6,1)))
        status,payload=acq.fetch_once(u,opener=opener)
        self.assertEqual(status,200); self.assertEqual(payload,body); self.assertEqual(len(calls),1)
        rows=acq.decoder.decode_payload(payload,"XAUUSD",date(2026,6,1)); self.assertEqual(len(rows),1)

    def test_http_404_is_returned_without_retry(self):
        calls=[]
        def opener(req,timeout=0):
            calls.append(req.full_url)
            raise urllib.error.HTTPError(req.full_url,404,"missing",{},io.BytesIO(b""))
        u=gate.build_url(gate.RequestSpec("EURUSD","BID",date(2026,6,6)))
        status,payload=acq.fetch_once(u,opener=opener)
        self.assertEqual((status,payload),(404,b"")); self.assertEqual(len(calls),1)

    def test_full_plan_is_1040_plus_8_and_below_cap(self):
        specs=list(acq.iter_full_specs())
        self.assertEqual(len(specs),1040)
        self.assertEqual(8+len(specs),1048)
        self.assertLessEqual(1048,gate.MAX_GETS)
        self.assertEqual(len({(s.instrument,s.side) for s in specs[:8]}),8)
        self.assertTrue(all(s.day==date(2026,6,1) for s in specs[:8]))
        self.assertTrue(all(gate.START<=s.day<gate.END_EXCLUSIVE for s in specs))

    def test_output_series_are_exactly_eight(self):
        self.assertEqual(len(acq.SERIES),8)
        self.assertEqual({(i,s) for i,s,_ in acq.SERIES},{(x.instrument,x.side) for x in gate.sanity_specs()})

if __name__=="__main__": unittest.main()
