"""GDELT DOC 2.0 API client — EXPERIMENTAL proof of concept (Phase 8).

NOT connected to the production pipeline. The TrendAhead Score and website
rankings remain Wikimedia-only.

API: https://api.gdeltproject.org/api/v2/doc/doc (no key required).
Rate limit: the API enforces ~1 request / 5 seconds (HTTP 429 with an
explicit message beyond that) — we pace at 6s and back off on 429.
Data terms: GDELT data is free for unlimited use incl. commercial, with a
required citation + link to gdeltproject.org.
Searchable window: rolling 3 months. Timeline timestamps are UTC.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

USER_AGENT = "TrendAhead/0.1 (https://github.com/anselmzyx/TrendAhead)"
API = "https://api.gdeltproject.org/api/v2/doc/doc"
REQUEST_DELAY = 6.0  # seconds between requests (API enforces 1 per 5s)

CACHE_PATH = Path(__file__).parent / "output" / "gdelt_cache.json"


class GdeltError(Exception):
    """A GDELT request ultimately failed after retries."""


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=1))


def _get_json(params: dict, retries: int = 3) -> dict:
    """GET with pacing; retries on 429/non-JSON/HTTP errors with backoff.
    Responses are cached on disk so PoC re-runs create no traffic."""
    url = f"{API}?{urllib.parse.urlencode(params)}"
    cache = _load_cache()
    if url in cache:
        return cache[url]
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace")
            payload = json.loads(body)  # HTML/plain-text errors fail here
            cache = _load_cache()
            cache[url] = payload
            _save_cache(cache)
            time.sleep(REQUEST_DELAY)
            return payload
        except urllib.error.HTTPError as e:
            last_error = e
            # Empirically, a tripped 429 limiter stays tripped for minutes.
            wait = 60 * attempt if e.code == 429 else 5 * attempt
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_error = e
            wait = 6 * attempt
        if attempt < retries:
            time.sleep(wait)
    raise GdeltError(f"failed after {retries} attempts: {url} ({last_error})")


# ---------------------------------------------------------------------------
# Pure parsing/maths (unit-tested; no network)
# ---------------------------------------------------------------------------


def parse_timeline(payload: dict) -> list[dict]:
    """GDELT timelinevolraw JSON → [{date, articles, norm}] date-ascending.

    `articles` is the RAW count of distinct matching articles that day;
    `norm` is the total number of articles GDELT monitored that day."""
    try:
        points = payload["timeline"][0]["data"]
    except (KeyError, IndexError, TypeError):
        raise GdeltError(f"unexpected timeline response shape: {str(payload)[:200]}")
    out = []
    for p in points:
        ts, value, norm = p.get("date"), p.get("value"), p.get("norm")
        if not isinstance(ts, str) or len(ts) < 8:
            raise GdeltError(f"malformed timeline point: {p!r}")
        if not isinstance(value, int) or value < 0:
            raise GdeltError(f"malformed timeline value: {p!r}")
        out.append(
            {
                "date": datetime.strptime(ts[:8], "%Y%m%d").date(),
                "articles": value,
                "norm": norm if isinstance(norm, int) else 0,
            }
        )
    out.sort(key=lambda p: p["date"])
    return out


def drop_unreliable_tail(points: list[dict], today_utc: date) -> list[dict]:
    """Remove the current (incomplete) UTC day and any trailing bucket whose
    `norm` is under half the series median norm — observed in practice: the
    final bucket's norm can be a fraction of a normal day while GDELT is
    still backfilling it."""
    pts = [p for p in points if p["date"] < today_utc]
    if not pts:
        return pts
    norms = sorted(p["norm"] for p in pts if p["norm"] > 0)
    if not norms:
        return pts
    median = norms[len(norms) // 2]
    while pts and 0 < pts[-1]["norm"] < 0.5 * median:
        pts = pts[:-1]
    return pts


def fill_missing_days(points: list[dict], start: date, end: date) -> list[dict]:
    """Complete daily series start..end; absent days become 0 articles
    (GDELT omits some zero-coverage days from raw timelines)."""
    by_date = {p["date"]: p for p in points}
    out = []
    d = start
    while d <= end:
        out.append(by_date.get(d, {"date": d, "articles": 0, "norm": 0}))
        d += timedelta(days=1)
    return out


def news_stats(points: list[dict], recent_days: int = 3) -> dict | None:
    """Recent vs baseline for a complete daily series (Phase-3 style).
    Baseline = everything before the recent window (up to 30 days).
    Returns None when there's too little history to be meaningful."""
    if len(points) < recent_days + 7:
        return None
    counts = [p["articles"] for p in points]
    recent = counts[-recent_days:]
    baseline = counts[-(recent_days + 30) : -recent_days]
    recent_avg = sum(recent) / len(recent)
    baseline_avg = sum(baseline) / len(baseline)
    return {
        "recent_avg": round(recent_avg, 1),
        "baseline_avg": round(baseline_avg, 1),
        "baseline_days": len(baseline),
        "abs_change": round(recent_avg - baseline_avg, 1),
        "pct_change": (
            round((recent_avg - baseline_avg) / baseline_avg * 100)
            if baseline_avg > 0
            else None
        ),
    }


# ---------------------------------------------------------------------------
# Network fetchers
# ---------------------------------------------------------------------------


def fetch_timeline(query: str, start: date, end: date) -> list[dict]:
    """Raw daily article-count timeline for an exact query."""
    payload = _get_json(
        {
            "query": f'"{query}"',
            "mode": "timelinevolraw",
            "format": "json",
            "startdatetime": f"{start:%Y%m%d}000000",
            "enddatetime": f"{end:%Y%m%d}235959",
        }
    )
    return parse_timeline(payload)


def fetch_articles(query: str, max_records: int = 10) -> list[dict]:
    """Small sample of recent matching articles for relevance inspection."""
    payload = _get_json(
        {
            "query": f'"{query}"',
            "mode": "artlist",
            "format": "json",
            "maxrecords": str(max_records),
            "sort": "datedesc",
            "timespan": "2w",
        }
    )
    articles = payload.get("articles", [])
    if not isinstance(articles, list):
        raise GdeltError(f"unexpected artlist shape: {str(payload)[:200]}")
    return [
        {
            "title": a.get("title", ""),
            "domain": a.get("domain", ""),
            "seendate": a.get("seendate", ""),
            "language": a.get("language", ""),
        }
        for a in articles
    ]
