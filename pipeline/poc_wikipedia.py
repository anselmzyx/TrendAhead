"""Phase 3 proof of concept: fetch real daily pageviews for ONE Wikipedia
article and compute a first recent-vs-baseline signal.

Run:  python3 pipeline/poc_wikipedia.py
Network code lives in wikimedia.py; calculations in trend_math.py.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from trend_math import mean, missing_dates, percent_change, split_recent_baseline
from wikimedia import FetchError, fetch_daily_views

ARTICLE = "Artificial intelligence"
PROJECT = "en.wikipedia.org"
DAYS_WANTED = 40  # >= 33 needed: 3 recent + 30 baseline
RECENT_DAYS = 3
BASELINE_DAYS = 30


def main() -> None:
    # The current (UTC) day is always incomplete — request up to yesterday.
    today_utc = datetime.now(timezone.utc).date()
    end = today_utc - timedelta(days=1)
    start = end - timedelta(days=DAYS_WANTED - 1)

    print(f"Fetching daily pageviews for: {ARTICLE}")
    print(f"Project: {PROJECT}  |  agent=user (humans only)  |  {start} → {end}\n")

    try:
        series = fetch_daily_views(ARTICLE, start, end, project=PROJECT)
    except FetchError as e:
        raise SystemExit(f"ERROR: {e}")
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
