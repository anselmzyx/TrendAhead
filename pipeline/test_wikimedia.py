"""Tests for Wikimedia client retry behaviour — fully mocked, no network.

Motivated by the 2026-10-09 incident: a scheduled run failed because
Wikimedia transiently returned HTTP 404 for a valid top-pages date; the
identical request succeeded minutes later.
"""

import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from wikimedia import FetchError, _get_json, retry_wait


def http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("http://x", code, "err", {}, io.BytesIO(b""))


class FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def urlopen_sequence(*outcomes):
    """Each outcome is an Exception to raise or a dict to return."""
    it = iter(outcomes)

    def fake(request, timeout=None):
        outcome = next(it)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(outcome)

    return fake


class TestRetryWait(unittest.TestCase):
    def test_429_backs_off_longest(self):
        self.assertEqual([retry_wait(a, 429) for a in (1, 2, 3)], [30, 60, 90])

    def test_http_errors_moderate_backoff(self):
        self.assertEqual([retry_wait(a, 404) for a in (1, 2, 3)], [10, 20, 30])
        self.assertEqual(retry_wait(2, 503), 20)

    def test_network_errors_quick_backoff(self):
        self.assertEqual([retry_wait(a, None) for a in (1, 2, 3)], [2, 4, 8])


class TestGetJsonRetries(unittest.TestCase):
    def run_case(self, *outcomes, retries=4):
        sleeps = []
        with patch("wikimedia.urllib.request.urlopen", urlopen_sequence(*outcomes)):
            result = _get_json("http://x", retries=retries, sleep=sleeps.append)
        return result, sleeps

    def test_transient_404_then_success_recovers(self):
        result, sleeps = self.run_case(http_error(404), {"ok": 1})
        self.assertEqual(result, {"ok": 1})
        self.assertEqual(sleeps, [10])  # one 404 backoff, then success

    def test_persistent_404_still_fails_after_all_retries(self):
        # Genuinely missing data is never silently hidden.
        sleeps = []
        with patch(
            "wikimedia.urllib.request.urlopen",
            urlopen_sequence(*[http_error(404)] * 4),
        ):
            with self.assertRaises(FetchError) as ctx:
                _get_json("http://x", retries=4, sleep=sleeps.append)
        self.assertIn("404", str(ctx.exception))
        self.assertEqual(sleeps, [10, 20, 30])  # retried, backed off, gave up

    def test_transient_5xx_then_success(self):
        result, sleeps = self.run_case(http_error(503), http_error(502), {"ok": 2})
        self.assertEqual(result, {"ok": 2})
        self.assertEqual(sleeps, [10, 20])

    def test_429_uses_long_backoff(self):
        _, sleeps = self.run_case(http_error(429), {"ok": 3})
        self.assertEqual(sleeps, [30])

    def test_network_error_then_success(self):
        result, sleeps = self.run_case(urllib.error.URLError("boom"), {"ok": 4})
        self.assertEqual(result, {"ok": 4})
        self.assertEqual(sleeps, [2])

    def test_never_retries_forever(self):
        with patch(
            "wikimedia.urllib.request.urlopen",
            urlopen_sequence(*[http_error(503)] * 10),
        ) as fake:
            sleeps = []
            with self.assertRaises(FetchError):
                _get_json("http://x", retries=4, sleep=sleeps.append)
        self.assertEqual(len(sleeps), 3)  # exactly retries-1 waits, then stop

    def test_success_first_try_never_sleeps(self):
        result, sleeps = self.run_case({"ok": 5})
        self.assertEqual(result, {"ok": 5})
        self.assertEqual(sleeps, [])


if __name__ == "__main__":
    unittest.main()
