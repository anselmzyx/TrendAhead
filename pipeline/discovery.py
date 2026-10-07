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

# Source hygiene (Phase 5.5): pages whose top-list surges are driven by
# Wikimedia's own site/banner infrastructure rather than public interest in
# a topic (observed: fundraising banners linking "Wikimedia Foundation").
# Deliberately TINY and exact-match only — this is not keyword censorship.
INFRASTRUCTURE_EXACT = {
    "Wikimedia_Foundation",
    "MediaWiki",
    "Wiki",
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
    if title in INFRASTRUCTURE_EXACT:
        return "Wikimedia infrastructure page (site/banner-driven attention)"
    return None


# ---------------------------------------------------------------------------
# Candidate pool
# ---------------------------------------------------------------------------


def build_pool(day_lists: dict[date, list[dict]]) -> dict[str, dict]:
    """Merge per-day top lists into {title: info} with dedup.

    info: days (sorted list of dates seen), views_by_day ({date: views}),
    best_rank, max_views (highest single-day views in any sampled list).
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
                title,
                {"days": [], "views_by_day": {}, "best_rank": rank, "max_views": 0},
            )
            info["days"].append(day)
            info["views_by_day"][day] = views
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


IMPROVER_GROWTH = 1.4  # late-period avg views must be >= 1.4x early-period avg
IMPROVER_MIN_DAYS = 2  # must appear on >= 2 days in EACH half of the window


def select_improvers(
    pool: dict[str, dict],
    early_days: set[date],
    late_days: set[date],
    limit: int,
) -> list[str]:
    """Pick candidates already IN the top lists whose attention is climbing.

    The Phase 4 new-entrant path misses pages that were visible early and
    grew — exactly the sustained climbers TrendAhead prioritises. A title
    qualifies when it appears on >= IMPROVER_MIN_DAYS days in BOTH halves of
    the window and its late-half average top-list views are at least
    IMPROVER_GROWTH x its early-half average. Ordered by late-half average
    (most attention first), capped at `limit`."""
    out = []
    for title, info in pool.items():
        vbd = info["views_by_day"]
        early_views = [vbd[d] for d in vbd if d in early_days]
        late_views = [vbd[d] for d in vbd if d in late_days]
        if len(early_views) < IMPROVER_MIN_DAYS or len(late_views) < IMPROVER_MIN_DAYS:
            continue
        early_avg = sum(early_views) / len(early_views)
        late_avg = sum(late_views) / len(late_views)
        if early_avg > 0 and late_avg >= IMPROVER_GROWTH * early_avg:
            out.append((title, late_avg))
    out.sort(key=lambda pair: pair[1], reverse=True)
    return [title for title, _ in out[:limit]]


def combine_candidates(
    entrants: list[str], improvers: list[str]
) -> dict[str, list[str]]:
    """One deduplicated pool: {title: discovery reasons}. A title found by
    both paths keeps both reasons. Reasons are metadata only — they do not
    feed the TrendAhead Score."""
    combined: dict[str, list[str]] = {}
    for title in entrants:
        combined.setdefault(title, []).append("new entrant")
    for title in improvers:
        combined.setdefault(title, []).append("improver")
    return combined


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
