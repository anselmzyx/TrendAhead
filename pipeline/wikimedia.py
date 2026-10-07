"""Shared Wikimedia Analytics API client for the TrendAhead pipeline.

Network access lives here; calculation logic lives in trend_math.py /
discovery.py. Data license: CC0 1.0. No API key — but the User-Agent policy
requires a descriptive UA with contact info, and requests must be polite
and sequential (we add a small delay between calls).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime

USER_AGENT = "TrendAhead/0.1 (https://github.com/anselmzyx/TrendAhead)"
API_ROOT = "https://wikimedia.org/api/rest_v1/metrics/pageviews"

# Seconds to wait between consecutive API requests (polite, well under the
# ~200 req/min identified-client limit).
REQUEST_DELAY = 0.35


class FetchError(Exception):
    """A request ultimately failed after retries."""


def _get_json(url: str, retries: int = 3, timeout: int = 15) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            # 404 = no data for that page/day; retrying won't help.
            if e.code == 404:
                raise FetchError(f"404 no data: {url}") from e
            last_error = e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_error = e
        if attempt < retries:
            time.sleep(2**attempt)
    raise FetchError(f"failed after {retries} attempts: {url} ({last_error})")


def fetch_daily_views(
    article: str, start: date, end: date, project: str = "en.wikipedia.org"
) -> list[tuple[date, int]]:
    """Daily human (agent=user) pageviews for one article, date-ascending.

    Days Wikimedia has no data for (e.g. before the page existed) are simply
    absent from the result — callers decide how to treat gaps.
    """
    quoted = urllib.parse.quote(article.replace(" ", "_"), safe="")
    url = (
        f"{API_ROOT}/per-article/{project}/all-access/user/{quoted}/daily/"
        f"{start:%Y%m%d}/{end:%Y%m%d}"
    )
    payload = _get_json(url)
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise FetchError(f"response contained no items for {article!r}")
    series = []
    for item in items:
        ts, views = item.get("timestamp"), item.get("views")
        if not isinstance(ts, str) or len(ts) < 8 or not isinstance(views, int) or views < 0:
            raise FetchError(f"malformed item for {article!r}: {item!r}")
        series.append((datetime.strptime(ts[:8], "%Y%m%d").date(), views))
    series.sort(key=lambda pair: pair[0])
    time.sleep(REQUEST_DELAY)
    return series


def fetch_top_articles(
    day: date, project: str = "en.wikipedia.org"
) -> list[dict]:
    """The ~1000 most-viewed articles for one complete day.

    Returns raw entries: {"article": str, "views": int, "rank": int}.
    """
    url = f"{API_ROOT}/top/{project}/all-access/{day:%Y}/{day:%m}/{day:%d}"
    payload = _get_json(url)
    try:
        articles = payload["items"][0]["articles"]
    except (KeyError, IndexError, TypeError) as e:
        raise FetchError(f"unexpected top-articles response shape for {day}") from e
    if not isinstance(articles, list) or not articles:
        raise FetchError(f"empty top-articles list for {day}")
    time.sleep(REQUEST_DELAY)
    return articles
