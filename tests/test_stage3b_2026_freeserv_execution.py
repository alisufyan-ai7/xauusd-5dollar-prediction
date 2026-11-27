import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import stage3b_2026_freeserv_preflight as gate
import acquire_dukascopy_freeserv_stage3b_2026 as acq

class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, status: int = 200):
        super().__init__(body)
        self.status = status
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    def getcode(self):
        return self.status

def payload_for(spec, rows):
    cb = gate.request_params(spec)["jsonp"]
    return f"{cb}({json.dumps(rows)});".encode()

class TestD148Execution(unittest.TestCase):
    def test_execution_guard_allows_only_d152(self):
        self.assertEqual(acq.AUTHORIZED_D148_DECISION_SHAS, frozenset({"ce9e4a1eef48df2e7f1ee8775afe74edc10cbe71"}))
        self.assertTrue(acq.PROVIDER_EXECUTION_ENABLED)
        acq.require_execution_authorized("ce9e4a1eef48df2e7f1ee8775afe74edc10cbe71")
        with self.assertRaises(PermissionError):
            acq.require_execution_authorized("anything")

    def test_fetch_once_calls_opener_exactly_once(self):
        calls = []
        spec = gate.RequestSpec("XAU/USD", "B", gate.START_MS, 2)
        body = payload_for(spec, [[gate.START_MS, 1, 2, 0.5, 1.5, 2]])
        def opener(req, timeout=0):
            calls.append((req.full_url, timeout))
            return FakeResponse(body, 200)
        status, got = acq.fetch_once(spec, opener=opener)
        self.assertEqual((status, got), (200, body))
        self.assertEqual(len(calls), 1)


    def test_redirect_handler_does_not_follow_off_host_or_same_host_redirects(self):
        handler = acq.NoRedirectHandler()
        spec = gate.RequestSpec("XAU/USD", "B", gate.START_MS, 2)
        from urllib.request import Request
        req = Request(gate.build_url(spec))
        for target in ("https://evil.example/market", gate.BASE_URL):
            self.assertIsNone(handler.redirect_request(req, None, 302, "redirect", {}, target))

    def test_explicit_direct_proxy_free_transport_builds_without_env_proxy(self):
        import urllib.request
        orig = urllib.request.build_opener
        captured = []
        def fake_build(*handlers):
            captured.extend(handlers)
            class Dummy:
                def open(self, req, timeout):
                    return FakeResponse(b"x", 200)
            return Dummy()
        try:
            urllib.request.build_opener = fake_build
            spec = gate.RequestSpec("XAU/USD", "B", gate.START_MS, 2)
            from urllib.request import Request
            with acq.no_proxy_no_redirect_open(Request(gate.build_url(spec)), 45) as resp:
                self.assertEqual(resp.read(), b"x")
        finally:
            urllib.request.build_opener = orig
        self.assertTrue(any(isinstance(h, urllib.request.ProxyHandler) and h.proxies == {} for h in captured))
        self.assertTrue(any(isinstance(h, acq.NoRedirectHandler) for h in captured))

    def test_fetch_once_transport_failure_is_not_retried(self):
        calls = []
        spec = gate.RequestSpec("XAU/USD", "B", gate.START_MS, 2)
        def opener(req, timeout=0):
            calls.append(req.full_url)
            raise ConnectionResetError(104, "reset")
        with self.assertRaises(acq.AcquisitionFailure):
            acq.fetch_once(spec, opener=opener)
        self.assertEqual(len(calls), 1)

    def test_sanity_phase_is_exactly_eight(self):
        calls = []
        def fetcher(spec):
            calls.append((spec.instrument, spec.side, spec.limit))
            rows = [
                [gate.START_MS, 1, 2, 0.5, 1.5, 2, None],
                [gate.START_MS + 60000, 1.5, 2, 1, 1.8, 3, None],
            ]
            return 200, payload_for(spec, rows)
        records, count, raw = acq.sanity_phase(fetcher)
        self.assertEqual(count, 8)
        self.assertEqual(len(records), 8)
        self.assertEqual(len(calls), 8)
        self.assertTrue(all(x[2] == 2 for x in calls))
        self.assertGreater(raw, 0)

    def test_sanity_stops_on_first_failure(self):
        calls = []
        def fetcher(spec):
            calls.append(spec)
            return 503, b"unavailable"
        with self.assertRaises(acq.AcquisitionFailure):
            acq.sanity_phase(fetcher)
        self.assertEqual(len(calls), 1)

    def test_series_paging_duplicate_cursor_and_half_open_end(self):
        calls = []
        def fetcher(spec):
            calls.append(spec)
            if len(calls) == 1:
                rows = [
                    [gate.START_MS, 1, 2, 0.5, 1.5, 2],
                    [gate.START_MS + 60000, 1.5, 2, 1, 1.8, 3],
                ]
            else:
                rows = [
                    [gate.START_MS + 60000, 1.5, 2, 1, 1.8, 3],
                    [gate.END_EXCLUSIVE_MS, 2, 3, 1.5, 2.5, 4],
                ]
            return 200, payload_for(spec, rows)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "x.csv"
            report, raw = acq.acquire_series("XAU/USD", "B", path, fetcher)
            lines = path.read_text().splitlines()
        self.assertEqual(report["requests"], 2)
        self.assertEqual(report["rows"], 2)
        self.assertEqual(len(lines), 3)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].cursor_ms, gate.START_MS + 60000)
        self.assertGreater(raw, 0)

    def test_series_fails_if_request_budget_cannot_reach_end(self):
        def fetcher(spec):
            rows = [
                [spec.cursor_ms, 1, 2, 0.5, 1.5, 2],
                [spec.cursor_ms + 60000, 1.5, 2, 1, 1.8, 3],
            ]
            return 200, payload_for(spec, rows)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(acq.AcquisitionFailure):
                acq.acquire_series("EUR/USD", "B", Path(td) / "x.csv", fetcher)

    def test_full_run_cannot_start_without_future_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(PermissionError):
                acq.run(Path(td) / "out", Path(td) / "report.json", "not-authorized", fetcher=lambda spec: (200, b""))

if __name__ == "__main__":
    unittest.main()
