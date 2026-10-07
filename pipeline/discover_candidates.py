"""Phase 4: automatic candidate discovery experiment.

Finds Wikipedia topics that recently ENTERED the daily top-viewed lists,
filters obvious noise, fetches 40-day histories for a small subset, and
prints a provisional ranking for human inspection.

Run:  python3 pipeline/discover_candidates.py

Output is PROVISIONAL CANDIDATE DISCOVERY — NOT the final TrendAhead Score.
Roughly: 6 top-list requests + ~30 history requests, sequential and polite.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from discovery import (
    BASELINE_FLOOR,
    MIN_RECENT_AVG,
    build_pool,
    fill_gaps,
    noise_reason,
    provisional_rank,
    select_new_entrants,
)
from trend_math import mean, percent_change, split_recent_baseline
from wikimedia import FetchError, fetch_daily_views, fetch_top_articles

SAMPLE_DAYS = 6  # complete days of top lists: first 3 = "early", last 3 = "late"
SUBSET_LIMIT = 30  # max candidates whose full history we fetch
HISTORY_DAYS = 40  # per-candidate history window (>= 33 needed)
RECENT_DAYS = 3
BASELINE_DAYS = 30

OUTPUT_DIR = Path(__file__).parent / "output"


def main() -> None:
    today_utc = datetime.now(timezone.utc).date()
    end = today_utc - timedelta(days=1)  # newest COMPLETE day
    days = [end - timedelta(days=i) for i in range(SAMPLE_DAYS - 1, -1, -1)]
    early_days, late_days = set(days[: SAMPLE_DAYS // 2]), set(days[SAMPLE_DAYS // 2 :])

    # --- Step 1: fetch top lists ------------------------------------------
    print(f"Discovery window: {days[0]} → {days[-1]}  "
          f"(early = first {len(early_days)}, late = last {len(late_days)})")
    day_lists: dict = {}
    for day in days:
        try:
            day_lists[day] = fetch_top_articles(day)
            print(f"  top list {day}: {len(day_lists[day])} entries")
        except FetchError as e:
            print(f"  ⚠ top list {day} FAILED: {e}")
    if len(day_lists) < SAMPLE_DAYS:
        raise SystemExit("ERROR: missing top lists — refusing to continue with partial window.")

    # --- Step 2: candidate pool -------------------------------------------
    raw_entries = sum(len(v) for v in day_lists.values())
    pool = build_pool(day_lists)
    print(f"\nRaw top-list entries: {raw_entries:,}")
    print(f"Unique candidates after dedup: {len(pool):,}")

    # --- Step 3: noise filter ---------------------------------------------
    removed: dict[str, list[str]] = {}
    for title in list(pool):
        reason = noise_reason(title)
        if reason:
            removed.setdefault(reason, []).append(title)
            del pool[title]
    n_removed = sum(len(v) for v in removed.values())
    print(f"\nNoise filter removed {n_removed} candidates:")
    for reason, titles in sorted(removed.items(), key=lambda kv: -len(kv[1])):
        sample = ", ".join(titles[:3])
        print(f"  {len(titles):>4}  {reason}  (e.g. {sample})")
    print(f"Candidates remaining: {len(pool):,}")

    # --- Step 4: select new entrants --------------------------------------
    selected = select_new_entrants(pool, early_days, late_days, SUBSET_LIMIT)
    print(f"\nSelection: pages present in a late-day top list but in NO early-day"
          f"\nlist (attention is new, not permanent), ordered by top-list views;"
          f"\ncapped at {SUBSET_LIMIT}. Selected: {len(selected)}")

    # --- Step 5: fetch histories ------------------------------------------
    hist_start = end - timedelta(days=HISTORY_DAYS - 1)
    print(f"\nFetching {HISTORY_DAYS}-day histories ({hist_start} → {end}), sequentially...")
    evaluated, failures = [], []
    for i, title in enumerate(selected, 1):
        try:
            series = fetch_daily_views(title, hist_start, end)
            full, filled = fill_gaps(series, hist_start, end)
            recent, baseline = split_recent_baseline(full, RECENT_DAYS, BASELINE_DAYS)
            recent_avg = mean([v for _, v in recent])
            baseline_avg = mean([v for _, v in baseline])
            evaluated.append(
                {
                    "title": title,
                    "recent_avg": round(recent_avg),
                    "baseline_avg": round(baseline_avg),
                    "abs_change": round(recent_avg - baseline_avg),
                    "pct_change": percent_change(recent_avg, baseline_avg),
                    "latest_views": full[-1][1],
                    "days_missing_filled_as_zero": filled,
                    "top_list_appearances": len(pool[title]["days"]),
                    "best_top_rank": pool[title]["best_rank"],
                }
            )
            print(f"  [{i:>2}/{len(selected)}] ok    {title}")
        except (FetchError, ValueError) as e:
            failures.append({"title": title, "error": str(e)})
            print(f"  [{i:>2}/{len(selected)}] FAIL  {title}: {e}")

    # --- Step 6: provisional ranking --------------------------------------
    ranked, excluded = provisional_rank(evaluated)
    print(f"\nEvaluated: {len(evaluated)}  |  failed: {len(failures)}  |  "
          f"excluded by volume rule: {len(excluded)}")
    print(f"Volume rule: recent_avg >= {MIN_RECENT_AVG:,}; ranking key = "
          f"recent_avg / max(baseline_avg, {BASELINE_FLOOR}).")

    top = ranked[:20]
    print("\n========= PROVISIONAL CANDIDATE DISCOVERY — NOT FINAL TRENDAHEAD SCORE =========")
    print(f"{'#':>2}  {'Topic':<42} {'Recent avg':>10} {'Baseline':>9} "
          f"{'Change %':>9} {'Abs chg':>9} {'Days':>4} {'Rank':>4}")
    print("-" * 97)
    for i, c in enumerate(top, 1):
        pct = f"{c['pct_change']:+,.0f}%" if c["pct_change"] is not None else "new"
        title = c["title"].replace("_", " ")
        title = title if len(title) <= 42 else title[:39] + "..."
        print(
            f"{i:>2}  {title:<42} {c['recent_avg']:>10,} {c['baseline_avg']:>9,} "
            f"{pct:>9} {c['abs_change']:>+9,} {c['top_list_appearances']:>4} "
            f"{c['best_top_rank']:>4}"
        )
    print("-" * 97)
    print("Days = appearances in the 6 sampled top lists · Rank = best top-list rank")

    # --- Step 7: save debug output ----------------------------------------
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"discovery_{end}.json"
    out_path.write_text(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "note": "PROVISIONAL candidate discovery — not TrendAhead Scores",
                "window": [str(d) for d in days],
                "raw_entries": raw_entries,
                "unique_candidates": len(pool) + n_removed,
                "noise_removed": {k: v for k, v in removed.items()},
                "selected": selected,
                "failures": failures,
                "excluded_low_volume": excluded,
                "ranked": ranked,
            },
            indent=2,
        )
    )
    print(f"\nSaved full results to {out_path.relative_to(Path.cwd()) if out_path.is_relative_to(Path.cwd()) else out_path}")


if __name__ == "__main__":
    sys.exit(main())
