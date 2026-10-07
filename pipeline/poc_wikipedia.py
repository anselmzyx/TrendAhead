"""Phase 3 proof of concept: fetch real daily pageviews for ONE Wikipedia
article from the official Wikimedia Analytics API and compute a first
recent-vs-baseline signal.

Standard library only. Run:  python3 pipeline/poc_wikipedia.py

API: https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/...
Data license: CC0 1.0 (public domain). No API key required.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

from trend_math import mean, missing_dates, percent_change, split_recent_baseline

ARTICLE = "Artificial intelligence"
PROJECT = "en.wikipedia.org"
DAYS_WANTED = 40  # complete days to request (>= 33 needed: 3 recent + 30 baseline)
RECENT_DAYS = 3
BASELINE_DAYS = 30

# Wikimedia User-Agent policy requires a descriptive UA. We are in local
# development with no public URL yet; before any deployed/scheduled use this
# MUST gain real contact info (public repo URL or email) to qualify for the
# higher "identified client" rate limit.
USER_AGENT = "TrendAhead/0.1 (local development proof-of-concept; contact info to be added before deployment)"

API_BASE = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"


def fetch_daily_views(
    article: str, start: date, end: date, retries: int = 3
) -> list[dict]:
    """Fetch daily pageviews (human users only), with retry + backoff."""
    quoted = urllib.parse.quote(article.replace(" ", "_"), safe="")
    url = (
        f"{API_BASE}/{PROJECT}/all-access/user/{quoted}/daily/"
        f"{start:%Y%m%d}/{end:%Y%m%d}"
    )
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=15) as resp:
                body = resp.read()
            payload = json.loads(body)
            items = payload.get("items")
            if not isinstance(items, list) or not items:
                raise ValueError(f"API response contained no items: {payload!r:.200}")
            return items
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as e:
            last_error = e
            if attempt < retries:
                wait = 2**attempt
                print(f"  attempt {attempt} failed ({e}); retrying in {wait}s...")
                time.sleep(wait)
    raise SystemExit(f"ERROR: could not fetch pageviews after {retries} attempts: {last_error}")


def parse_items(items: list[dict]) -> list[tuple[date, int]]:
    """Validate and convert API items to a date-ascending (date, views) list."""
    series = []
    for item in items:
        ts = item.get("timestamp")
        views = item.get("views")
        if not isinstance(ts, str) or len(ts) < 8:
            raise SystemExit(f"ERROR: malformed timestamp in API item: {item!r}")
        if not isinstance(views, int) or views < 0:
            raise SystemExit(f"ERROR: malformed views value in API item: {item!r}")
        series.append((datetime.strptime(ts[:8], "%Y%m%d").date(), views))
    series.sort(key=lambda pair: pair[0])
    return series


def main() -> None:
    # The current (UTC) day is always incomplete, and yesterday's data can
    # lag by a few hours — so request up to yesterday and simply use whatever
    # complete days come back.
    today_utc = datetime.now(timezone.utc).date()
    end = today_utc - timedelta(days=1)
    start = end - timedelta(days=DAYS_WANTED - 1)

    print(f"Fetching daily pageviews for: {ARTICLE}")
    print(f"Project: {PROJECT}  |  agent=user (humans only)  |  {start} → {end}\n")

    series = parse_items(fetch_daily_views(ARTICLE, start, end))
    dates = [d for d, _ in series]

    gaps = missing_dates(dates)
    print(f"Days returned: {len(series)}  ({dates[0]} → {dates[-1]})")
    if gaps:
        print(f"⚠ Missing days inside that range: {', '.join(str(g) for g in gaps)}")
    else:
        print("No missing days inside the returned range.")

    print("\nSample of the raw data (last 10 days):")
    print("  Date        | Pageviews")
    print("  ------------|----------")
    for d, v in series[-10:]:
        print(f"  {d}  | {v:>8,}")

    # --- First signal -----------------------------------------------------
    recent, baseline = split_recent_baseline(series, RECENT_DAYS, BASELINE_DAYS)
    recent_avg = mean([v for _, v in recent])
    baseline_avg = mean([v for _, v in baseline])
    change = percent_change(recent_avg, baseline_avg)

    # --- Sanity checks ----------------------------------------------------
    recent_dates = {d for d, _ in recent}
    baseline_dates = {d for d, _ in baseline}
    checks = {
        f"recent period has {RECENT_DAYS} days": len(recent) == RECENT_DAYS,
        f"baseline period has {BASELINE_DAYS} days": len(baseline) == BASELINE_DAYS,
        "periods do not overlap": not (recent_dates & baseline_dates),
        "baseline ends right before recent starts": max(baseline_dates)
        < min(recent_dates),
        "dates are ordered oldest-first": dates == sorted(dates),
        "baseline average is non-zero": baseline_avg != 0,
    }
    print("\nSanity checks:")
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not all(checks.values()):
        raise SystemExit("ERROR: sanity checks failed — do not trust the numbers above.")

    period_gaps = missing_dates(sorted(baseline_dates | recent_dates))
    if period_gaps:
        print(f"  NOTE  calculation periods are missing days: {period_gaps}")

    # --- Results ----------------------------------------------------------
    print("\n================ FIRST SIGNAL ================")
    print(f"Article:                    {ARTICLE}")
    print(f"Latest complete day:        {series[-1][0]}  ({series[-1][1]:,} views)")
    print(f"Recent {RECENT_DAYS}-day average:       {recent_avg:,.0f} views/day")
    print(f"Previous {BASELINE_DAYS}-day baseline:  {baseline_avg:,.0f} views/day")
    print(f"Absolute difference:        {recent_avg - baseline_avg:+,.0f} views/day")
    if change is None:
        print("Change vs baseline:         n/a (zero baseline)")
    else:
        print(f"Change vs baseline:         {change:+.1f}%")
    print("==============================================")


if __name__ == "__main__":
    sys.exit(main())
