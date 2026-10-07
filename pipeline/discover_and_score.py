"""Phase 5.5: combined candidate discovery (new entrants + improvers),
source hygiene, and TrendAhead Score V1 ranking.

Discovery paths (both over the same 6 complete days of top-1000 lists):
  * new entrants — in a late-day list but no early-day list (Phase 4 path)
  * improvers    — in BOTH halves, late-half avg views >= 1.4x early-half

Histories are cached in pipeline/output/histories_<end>.json — already
cached titles cost zero API requests on re-runs.

Run:  python3 pipeline/discover_and_score.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from discovery import (
    build_pool,
    combine_candidates,
    fill_gaps,
    noise_reason,
    select_improvers,
    select_new_entrants,
)
from scoring import score_series
from wikimedia import FetchError, fetch_daily_views, fetch_top_articles

SAMPLE_DAYS = 6
NEW_ENTRANT_CAP = 25  # separate caps so both paths stay represented
IMPROVER_CAP = 15
HISTORY_DAYS = 40

OUTPUT_DIR = Path(__file__).parent / "output"


def load_history_cache(end) -> dict:
    path = OUTPUT_DIR / f"histories_{end}.json"
    if path.exists():
        return json.loads(path.read_text())["histories"]
    return {}


def save_history_cache(end, window, histories: dict) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"histories_{end}.json"
    path.write_text(json.dumps(
        {"end_day": str(end), "window": [str(d) for d in window],
         "failures": [], "histories": histories}, indent=1))


def main() -> None:
    today_utc = datetime.now(timezone.utc).date()
    end = today_utc - timedelta(days=1)
    days = [end - timedelta(days=i) for i in range(SAMPLE_DAYS - 1, -1, -1)]
    early, late = set(days[: SAMPLE_DAYS // 2]), set(days[SAMPLE_DAYS // 2 :])
    print(f"Discovery window: {days[0]} → {days[-1]}")

    # --- Top lists + pool ---------------------------------------------------
    day_lists = {}
    for day in days:
        day_lists[day] = fetch_top_articles(day)
    pool = build_pool(day_lists)
    raw_unique = len(pool)

    # --- Noise + infrastructure filter (transparent) ------------------------
    removed: dict[str, list[str]] = {}
    for title in list(pool):
        reason = noise_reason(title)
        if reason:
            removed.setdefault(reason, []).append(title)
            del pool[title]
    print(f"\nUnique candidates: {raw_unique:,} → {len(pool):,} after filters.")
    print("Removed by filter:")
    for reason, titles in sorted(removed.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(titles):>4}  {reason}  (e.g. {', '.join(titles[:3])})")

    # --- Two discovery paths ------------------------------------------------
    entrants = select_new_entrants(pool, early, late, NEW_ENTRANT_CAP)
    improvers = select_improvers(pool, early, late, IMPROVER_CAP)
    combined = combine_candidates(entrants, improvers)
    overlap = [t for t, r in combined.items() if len(r) > 1]
    print(f"\nNew entrants: {len(entrants)}  |  improvers: {len(improvers)}  |  "
          f"overlap: {len(overlap)}  |  combined: {len(combined)}")

    # --- Histories (cache-aware) --------------------------------------------
    cache = load_history_cache(end)
    hist_start = end - timedelta(days=HISTORY_DAYS - 1)
    fetched = 0
    failures = []
    for i, title in enumerate(combined, 1):
        if title in cache:
            continue
        try:
            series = fetch_daily_views(title, hist_start, end)
            full, filled = fill_gaps(series, hist_start, end)
            cache[title] = {
                "sample": "combined",
                "days_filled_as_zero": filled,
                "series": [[str(d), v] for d, v in full],
            }
            fetched += 1
        except (FetchError, ValueError) as e:
            failures.append({"title": title, "error": str(e)})
            print(f"  FAIL {title}: {e}")
    save_history_cache(end, days, cache)
    print(f"Histories: {len(combined) - len(failures)} available "
          f"({fetched} newly fetched, rest cached)  |  failures: {len(failures)}")

    # --- Score with the approved V1 engine ----------------------------------
    rows = []
    for title, reasons in combined.items():
        h = cache.get(title)
        if not h:
            continue
        views = [v for _, v in h["series"]]
        try:
            r = score_series(views)
        except ValueError as e:
            failures.append({"title": title, "error": str(e)})
            continue
        rows.append({"title": title, "reasons": reasons, **r})
    rows.sort(key=lambda r: r["score"], reverse=True)

    print("\n============ TRENDAHEAD SCORE V1 — COMBINED DISCOVERY (EXPERIMENTAL) ============")
    print(f"{'#':>2} {'Topic':<32} {'Score':>5} {'Discovery':<21} {'Recent':>8} "
          f"{'Basln':>7} {'Pers':>4} {'Qual':>4}  Status")
    print("-" * 110)
    for i, r in enumerate(rows[:20], 1):
        c, st = r["components"], r["stats"]
        title = r["title"].replace("_", " ")
        title = title if len(title) <= 32 else title[:29] + "..."
        reason = " + ".join(r["reasons"])
        print(f"{i:>2} {title:<32} {r['score']:>5} {reason:<21} {st['recent_avg']:>8,} "
              f"{st['baseline_avg']:>7,} {c['persistence']:>4.2f} "
              f"{c['spike_quality']:>4.2f}  {r['status']}")
    print("-" * 110)

    out = OUTPUT_DIR / f"combined_scores_{end}.json"
    out.write_text(json.dumps(
        {"note": "TrendAhead Score V1, combined discovery — EXPERIMENTAL",
         "window": [str(d) for d in days],
         "removed_by_filter": removed, "failures": failures,
         "ranked": rows}, indent=1))
    print(f"Saved → {out}")


if __name__ == "__main__":
    sys.exit(main())
