"""Phase 5, Step 1: collect and cache full daily histories for score design.

Collects two samples over the same 6-day window Phase 4 used:
  * "new entrants"  — the Phase 4 selection (late top lists only)
  * "improvers"     — EVALUATION-ONLY extra sample: pages in BOTH early and
    late top lists whose late views grew meaningfully (>= 1.4x). Phase 4's
    discovery misses these slower climbers; we need them to validate the
    score. This does NOT change the discovery pipeline itself.

Histories are cached to pipeline/output/histories_<end>.json so repeated
scoring experiments cost zero extra API requests.

Run:  python3 pipeline/collect_histories.py [--inspect TITLE ...]
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from discovery import (
    build_pool,
    fill_gaps,
    noise_reason,
    select_improvers,
    select_new_entrants,
)
from wikimedia import FetchError, fetch_daily_views, fetch_top_articles

SAMPLE_DAYS = 6
NEW_ENTRANT_LIMIT = 30
IMPROVER_LIMIT = 8
HISTORY_DAYS = 40

OUTPUT_DIR = Path(__file__).parent / "output"


def collect() -> dict:
    today_utc = datetime.now(timezone.utc).date()
    end = today_utc - timedelta(days=1)
    cache_path = OUTPUT_DIR / f"histories_{end}.json"
    if cache_path.exists():
        print(f"Using cached histories: {cache_path}")
        return json.loads(cache_path.read_text())

    days = [end - timedelta(days=i) for i in range(SAMPLE_DAYS - 1, -1, -1)]
    early, late = set(days[: SAMPLE_DAYS // 2]), set(days[SAMPLE_DAYS // 2 :])

    day_lists = {}
    for day in days:
        day_lists[day] = fetch_top_articles(day)
        print(f"  top list {day}: {len(day_lists[day])} entries")

    pool = build_pool(day_lists)
    for title in list(pool):
        if noise_reason(title):
            del pool[title]

    entrants = select_new_entrants(pool, early, late, NEW_ENTRANT_LIMIT)
    improvers = select_improvers(pool, early, late, IMPROVER_LIMIT)
    titles = entrants + [t for t in improvers if t not in entrants]
    print(f"\nnew entrants: {len(entrants)}  |  improvers (evaluation-only): {len(improvers)}")

    hist_start = end - timedelta(days=HISTORY_DAYS - 1)
    histories, failures = {}, []
    for i, title in enumerate(titles, 1):
        try:
            series = fetch_daily_views(title, hist_start, end)
            full, filled = fill_gaps(series, hist_start, end)
            histories[title] = {
                "sample": "new_entrant" if title in entrants else "improver",
                "days_filled_as_zero": filled,
                "series": [[str(d), v] for d, v in full],
            }
            print(f"  [{i:>2}/{len(titles)}] ok    {title}")
        except (FetchError, ValueError) as e:
            failures.append({"title": title, "error": str(e)})
            print(f"  [{i:>2}/{len(titles)}] FAIL  {title}: {e}")

    data = {
        "end_day": str(end),
        "window": [str(d) for d in days],
        "failures": failures,
        "histories": histories,
    }
    OUTPUT_DIR.mkdir(exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=1))
    print(f"\nCached {len(histories)} histories → {cache_path}")
    return data


def inspect(data: dict, titles: list[str]) -> None:
    """Print signal shape for selected titles: enough to see baseline,
    takeoff, rising days, peak, and post-peak behaviour."""
    for title in titles:
        h = data["histories"].get(title)
        if not h:
            print(f"\n### {title}: NOT IN SAMPLE")
            continue
        series = [(date.fromisoformat(d), v) for d, v in h["series"]]
        views = [v for _, v in series]
        base = views[:-7]
        base_avg = sum(base) / len(base)
        last14 = series[-14:]
        peak_day, peak = max(last14, key=lambda p: p[1])
        latest = views[-1]
        rising = sum(
            1 for a, b in zip(views[-8:], views[-7:]) if b > a
        )
        print(f"\n### {title}  [{h['sample']}]")
        print(f"    33-day pre-week baseline avg: {base_avg:,.0f}  |  peak(14d): "
              f"{peak:,} on {peak_day}  |  latest: {latest:,} "
              f"({latest / peak:.0%} of peak)  |  rising days (last 7): {rising}")
        bars = ""
        for d, v in last14:
            bars += f"    {d}  {v:>9,}  {'█' * min(60, int(60 * v / peak))}\n"
        print(bars, end="")


if __name__ == "__main__":
    data = collect()
    args = sys.argv[1:]
    if args and args[0] == "--inspect":
        inspect(data, [a.replace(" ", "_") for a in args[1:]])
