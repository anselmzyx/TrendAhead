"""Lag-aware cross-source confirmation: Wikipedia (primary) × GDELT news
(secondary corroboration).

Design decisions (Phase 9):
- GDELT answers ONE question: "has independent news attention also risen
  over an ALIGNED historical window?" It never validates today's freshest
  breakouts (its raw timelines lag ~3–4 days) and never gates a topic.
- Three distinct outcomes — never collapsed together:
    confirmed      usable query, news attention also rose
    not_confirmed  usable query, no meaningful news rise (not "bad")
    unavailable    ambiguous query / zero data / timeline too incomplete
- The TrendAhead Score is untouched: confirmation is display-only
  provenance-labelled metadata (Approach A).
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone

from gdelt import (
    GdeltError,
    drop_unreliable_tail,
    fetch_articles,
    fetch_timeline,
    fill_missing_days,
)
from news_query import (
    MIN_RELEVANCE,
    query_variants,
    relevance_confidence,
    syndication_ratio,
)

RECENT_DAYS = 3
MIN_BASELINE_DAYS = 14  # under this much aligned history → unavailable
MAX_BASELINE_DAYS = 30
MAX_END_LAG_DAYS = 7  # usable GDELT end older than this vs wiki end → unavailable
MIN_RECENT_ARTICLES = 2.0  # avg articles/day below this can't confirm anything
CONFIRM_THRESHOLD = 0.30
GROWTH_CAP = 10  # 10x news growth = max growth credit
VOLUME_FULL = 20  # >= 20 articles/day = full volume credit


# ---------------------------------------------------------------------------
# Pure confirmation maths (unit-tested)
# ---------------------------------------------------------------------------


def aligned_windows(points: list[dict]) -> dict | None:
    """Split a complete, reliable daily news series into aligned recent /
    baseline windows ending on the latest COMPLETE GDELT date.
    Returns None when there is too little history."""
    if len(points) < RECENT_DAYS + MIN_BASELINE_DAYS:
        return None
    recent = points[-RECENT_DAYS:]
    baseline = points[-(RECENT_DAYS + MAX_BASELINE_DAYS) : -RECENT_DAYS]
    recent_avg = sum(p["articles"] for p in recent) / len(recent)
    baseline_avg = sum(p["articles"] for p in baseline) / len(baseline)
    return {
        "aligned_through": points[-1]["date"],
        "recent_avg": round(recent_avg, 1),
        "baseline_avg": round(baseline_avg, 1),
        "baseline_days": len(baseline),
    }


def confirmation_value(
    recent_avg: float, baseline_avg: float, relevance: float
) -> float:
    """Bounded 0–1 confirmation strength.

    growth  = log10(min(recent/max(baseline, 0.5), 10)) / log10(10)
    volume  = log-ramp from 2 articles/day (0) to 20/day (1)
    value   = growth × volume × relevance
    The 0.5 baseline floor and the volume ramp mean 0→1 articles/day can
    never register as confirmation."""
    ratio = recent_avg / max(baseline_avg, 0.5)
    if ratio <= 1:
        return 0.0
    growth = min(math.log10(min(ratio, GROWTH_CAP)) / math.log10(GROWTH_CAP), 1.0)
    if recent_avg <= MIN_RECENT_ARTICLES:
        return 0.0
    volume = min(
        math.log10(recent_avg / MIN_RECENT_ARTICLES)
        / math.log10(VOLUME_FULL / MIN_RECENT_ARTICLES),
        1.0,
    )
    return round(growth * volume * relevance, 3)


def classify(value: float | None) -> str:
    if value is None:
        return "unavailable"
    return "confirmed" if value >= CONFIRM_THRESHOLD else "not_confirmed"


# ---------------------------------------------------------------------------
# Live evaluation (network via gdelt.py — cached, paced)
# ---------------------------------------------------------------------------


def evaluate_news_confirmation(title: str, wiki_end: date | None = None) -> dict:
    """Full evaluation for one topic. Never raises on GDELT trouble —
    failures become {"state": "unavailable", "reason": ...} so the core
    Wikimedia product can never be broken by the news layer."""
    today = datetime.now(timezone.utc).date()
    wiki_end = wiki_end or (today - timedelta(days=1))
    result: dict = {"state": "unavailable", "value": None, "query": None}

    # 1. find a usable query via the relevance gate
    chosen = None
    for query in query_variants(title):
        try:
            articles = fetch_articles(query, 8)
        except GdeltError as e:
            result["reason"] = f"article lookup failed: {e}"
            return result
        titles = [a["title"] for a in articles]
        confidence = relevance_confidence(query, titles)
        if len(articles) >= 3 and confidence >= MIN_RELEVANCE:
            chosen = {
                "query": query,
                "relevance": confidence,
                "sample_titles": titles[:5],
                "unique_domain_ratio": syndication_ratio(
                    [a["domain"] for a in articles]
                ),
            }
            break
    if not chosen:
        result["reason"] = "no query variant passed the relevance gate"
        result["variants_tried"] = query_variants(title)
        return result
    result.update(chosen)

    # 2. aligned timeline
    try:
        raw = fetch_timeline(chosen["query"], wiki_end - timedelta(days=39), wiki_end)
    except GdeltError as e:
        result["reason"] = f"timeline failed: {e}"
        return result
    kept = drop_unreliable_tail(raw, today)
    if not kept:
        result["reason"] = "no reliable timeline buckets"
        return result
    end = kept[-1]["date"]
    if (wiki_end - end).days > MAX_END_LAG_DAYS:
        result["reason"] = f"GDELT data too stale (ends {end})"
        return result
    full = fill_missing_days(kept, kept[0]["date"], end)
    windows = aligned_windows(full)
    if not windows:
        result["reason"] = "too little aligned history"
        return result

    # 3. confirmation
    value = confirmation_value(
        windows["recent_avg"], windows["baseline_avg"], chosen["relevance"]
    )
    change = (
        round(
            (windows["recent_avg"] - windows["baseline_avg"])
            / windows["baseline_avg"]
            * 100
        )
        if windows["baseline_avg"] > 0
        else None
    )
    result.update(
        {
            "state": classify(value),
            "value": value,
            "aligned_through": str(windows["aligned_through"]),
            "recent_news_avg": windows["recent_avg"],
            "baseline_news_avg": windows["baseline_avg"],
            "baseline_days": windows["baseline_days"],
            "news_change_percent": change,
        }
    )
    return result
