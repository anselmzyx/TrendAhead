"""End-to-end pipeline orchestration: discovery → histories → scores.

Single reusable entry point so the CLI tools (discover_and_score.py,
generate_site_data.py) share one implementation. No printing here.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
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
NEW_ENTRANT_CAP = 25  # separate caps so both discovery paths stay represented
IMPROVER_CAP = 15
HISTORY_DAYS = 40

OUTPUT_DIR = Path(__file__).parent / "output"


def latest_complete_day() -> date:
    """Yesterday in UTC — the current UTC day is always incomplete."""
    return datetime.now(timezone.utc).date() - timedelta(days=1)


def _load_history_cache(end: date) -> dict:
    path = OUTPUT_DIR / f"histories_{end}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())["histories"]
        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupt cache fails safe: ignore it and refetch live.
            print(f"  ⚠ cache {path.name} is corrupt — ignoring and refetching")
    return {}


def _save_history_cache(end: date, window: list[date], histories: dict) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / f"histories_{end}.json").write_text(
        json.dumps(
            {
                "end_day": str(end),
                "window": [str(d) for d in window],
                "failures": [],
                "histories": histories,
            },
            indent=1,
        )
    )


def run_pipeline(end: date | None = None, log=print) -> dict:
    """Discovery → filters → two candidate paths → histories → V1 scores.

    Returns {end, window, removed, entrants, improvers, combined, failures,
    rows} where rows are score-sorted dicts with title, reasons, score,
    status, components, stats and the full (date, views) history.
    """
    end = end or latest_complete_day()
    days = [end - timedelta(days=i) for i in range(SAMPLE_DAYS - 1, -1, -1)]
    early, late = set(days[: SAMPLE_DAYS // 2]), set(days[SAMPLE_DAYS // 2 :])

    day_lists = {}
    for day in days:
        day_lists[day] = fetch_top_articles(day)
        log(f"  top list {day}: {len(day_lists[day])} entries")
    pool = build_pool(day_lists)
    raw_unique = len(pool)

    removed: dict[str, list[str]] = {}
    for title in list(pool):
        reason = noise_reason(title)
        if reason:
            removed.setdefault(reason, []).append(title)
            del pool[title]

    entrants = select_new_entrants(pool, early, late, NEW_ENTRANT_CAP)
    improvers = select_improvers(pool, early, late, IMPROVER_CAP)
    combined = combine_candidates(entrants, improvers)

    cache = _load_history_cache(end)
    hist_start = end - timedelta(days=HISTORY_DAYS - 1)
    fetched = 0
    failures: list[dict] = []
    for title in combined:
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
            log(f"  FETCH FAIL {title}: {e}")
    _save_history_cache(end, days, cache)
    log(f"  histories: {fetched} newly fetched, {len(combined) - fetched - len(failures)} cached")

    rows = []
    for title, reasons in combined.items():
        h = cache.get(title)
        if not h:
            continue
        views = [v for _, v in h["series"]]
        try:
            result = score_series(views)
        except ValueError as e:
            failures.append({"title": title, "error": f"scoring: {e}"})
            continue
        rows.append(
            {
                "title": title,
                "reasons": reasons,
                "history": [(d, v) for d, v in h["series"]],
                **result,
            }
        )
    rows.sort(key=lambda r: r["score"], reverse=True)

    return {
        "end": end,
        "window": days,
        "raw_unique": raw_unique,
        "removed": removed,
        "entrants": entrants,
        "improvers": improvers,
        "combined": combined,
        "failures": failures,
        "rows": rows,
    }
