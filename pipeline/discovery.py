"""Pure candidate-discovery logic for Phase 4. No network access here.

NOTE: the ranking in this module is a PROVISIONAL discovery ranking used to
decide which candidates deserve a human look. It is NOT the TrendAhead Score
(Phase 5 designs that separately).
"""

from __future__ import annotations

from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Noise filtering — transparent rules, inspectable in one place.
# ---------------------------------------------------------------------------

# Wikipedia namespace prefixes: these are site infrastructure, not topics.
NOISE_PREFIXES = (
    "Special:",
    "Wikipedia:",
    "Portal:",
    "Help:",
    "Talk:",
    "User:",
    "User_talk:",
    "File:",
    "Template:",
    "Category:",
    "Draft:",
    "Module:",
    "MediaWiki:",
    "Book:",
    "TimedText:",
)

# Exact titles that are navigation/infrastructure rather than topics.
NOISE_EXACT = {
    "Main_Page",
    "Wikipedia",  # the article about Wikipedia itself tops lists via UI links
}


def noise_reason(title: str) -> str | None:
    """Why a title is obvious noise, or None if it looks like a real topic."""
    if not title or not title.strip():
        return "empty/blank title"
    for prefix in NOISE_PREFIXES:
        if title.startswith(prefix):
            return f"internal namespace ({prefix[:-1]})"
    if title in NOISE_EXACT:
        return "site navigation page"
    return None


# ---------------------------------------------------------------------------
# Candidate pool
# ---------------------------------------------------------------------------


def build_pool(day_lists: dict[date, list[dict]]) -> dict[str, dict]:
    """Merge per-day top lists into {title: info} with dedup.

    info: days (sorted list of dates seen), best_rank, max_views
    (highest single-day views seen in any sampled top list).
    """
    pool: dict[str, dict] = {}
    for day in sorted(day_lists):
        for entry in day_lists[day]:
            title = entry.get("article")
            views = entry.get("views")
            rank = entry.get("rank")
            if not isinstance(title, str) or not isinstance(views, int):
                continue  # malformed entry — top lists occasionally have junk
            info = pool.setdefault(
                title, {"days": [], "best_rank": rank, "max_views": 0}
            )
            info["days"].append(day)
            info["max_views"] = max(info["max_views"], views)
            if isinstance(rank, int) and (
                info["best_rank"] is None or rank < info["best_rank"]
            ):
                info["best_rank"] = rank
    return pool


def select_new_entrants(
    pool: dict[str, dict],
    early_days: set[date],
    late_days: set[date],
    limit: int,
) -> list[str]:
    """Pick candidates that entered the top lists only RECENTLY.

    A title qualifies when it appears in at least one `late` day's top list
    but in none of the `early` days' lists — the simplest possible signal
    that attention is new rather than permanent. Qualifiers are ordered by
    their max observed top-list views (most attention first), capped at
    `limit`.
    """
    entrants = []
    for title, info in pool.items():
        seen = set(info["days"])
        if seen & late_days and not (seen & early_days):
            entrants.append(title)
    entrants.sort(key=lambda t: pool[t]["max_views"], reverse=True)
    return entrants[:limit]


# ---------------------------------------------------------------------------
# History normalisation + provisional ranking
# ---------------------------------------------------------------------------


def fill_gaps(
    series: list[tuple[date, int]], start: date, end: date
) -> tuple[list[tuple[date, int]], int]:
    """Return a complete start..end daily series, treating absent days as 0
    views (Wikimedia omits days with no data — e.g. before a page existed).
    Also returns how many days were filled, so callers can flag it."""
    present = dict(series)
    full = []
    filled = 0
    d = start
    while d <= end:
        if d in present:
            full.append((d, present[d]))
        else:
            full.append((d, 0))
            filled += 1
        d += timedelta(days=1)
    return full, filled


# Provisional discovery ranking rules (NOT the TrendAhead Score):
MIN_RECENT_AVG = 5000  # views/day — below this, growth % is too easily noise
BASELINE_FLOOR = 100  # views/day — stops tiny/zero baselines exploding ratios


def provisional_rank(candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split into (ranked, excluded) by transparent volume rules.

    Eligible candidates need recent_avg >= MIN_RECENT_AVG. Ranking key is
    the growth ratio recent_avg / max(baseline_avg, BASELINE_FLOOR): floored
    so a 2→10-views page cannot top the list, while a genuinely new page
    (near-zero baseline but tens of thousands of recent views) still ranks
    high — which is exactly the "emerging" shape we want to inspect.
    Each candidate dict must carry recent_avg and baseline_avg.
    """
    ranked, excluded = [], []
    for c in candidates:
        if c["recent_avg"] < MIN_RECENT_AVG:
            excluded.append({**c, "excluded_because": f"recent_avg < {MIN_RECENT_AVG}"})
            continue
        c = {**c, "ratio": c["recent_avg"] / max(c["baseline_avg"], BASELINE_FLOOR)}
        ranked.append(c)
    ranked.sort(key=lambda c: c["ratio"], reverse=True)
    return ranked, excluded
