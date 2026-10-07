"""Pure logic for turning scored pipeline rows into the website's JSON.

The Python pipeline is the single source of truth for every number the
website shows — the frontend only formats, it never recalculates.
"""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata

SOURCE = "Wikipedia pageviews (Wikimedia Analytics API, CC0)"
SCORE_VERSION = "v1"
HOMEPAGE_TOPICS = 12
TOPIC_PAGES = 24
SPARKLINE_DAYS = 14


# ---------------------------------------------------------------------------
# Slugs
# ---------------------------------------------------------------------------


def slugify(title: str) -> str:
    """URL-safe slug from a Wikipedia title.

    Accents are transliterated (Québécois → quebecois), punctuation becomes
    hyphens, and a title with no Latin characters at all falls back to a
    stable short hash so it still gets a valid, deterministic URL."""
    text = title.replace("_", " ")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    if not text:
        digest = hashlib.sha256(title.encode("utf-8")).hexdigest()[:10]
        return f"topic-{digest}"
    return text


def assign_slugs(titles: list[str]) -> dict[str, str]:
    """Map each title to a unique slug; collisions get -2, -3, … suffixes
    (in input order) rather than silently overwriting one another."""
    seen: dict[str, int] = {}
    out: dict[str, str] = {}
    for title in titles:
        base = slugify(title)
        seen[base] = seen.get(base, 0) + 1
        out[title] = base if seen[base] == 1 else f"{base}-{seen[base]}"
    return out


# ---------------------------------------------------------------------------
# Deterministic explanation text (no LLMs, no causal claims)
# ---------------------------------------------------------------------------


def display_title(title: str) -> str:
    return title.replace("_", " ")


def explanation(row: dict) -> str:
    """One factual sentence for the trend card."""
    ratio = row["stats"]["growth_ratio"]
    fading = row["status"] == "Fading / collapsing"
    if fading:
        if ratio >= 2:
            return (
                f"Attention surged to {_fmt_ratio(ratio)} its 30-day baseline "
                "but has fallen back from its peak."
            )
        return "Attention spiked recently but has fallen back from its peak."
    if ratio >= 2:
        return f"Attention is {_fmt_ratio(ratio)} its 30-day baseline."
    change = (ratio - 1) * 100
    return f"Recent attention is {change:+.0f}% vs its 30-day baseline."


def _fmt_ratio(ratio: float) -> str:
    return f"{ratio:.0f}×" if ratio >= 10 else f"{ratio:.1f}×"


def why_bullets(row: dict) -> list[str]:
    """Short factual statements derived from component subscores only.
    Shape, never cause — we know what attention did, not why."""
    c = row["components"]
    s = row["stats"]
    bullets = []
    if c["acceleration"] >= 0.6:
        bullets.append("Recent attention is far above this topic's own 30-day normal.")
    elif c["acceleration"] >= 0.25:
        bullets.append("Recent attention is meaningfully above this topic's 30-day normal.")
    else:
        bullets.append("Recent attention is close to this topic's usual level.")
    if c["persistence"] >= 0.75:
        bullets.append("Interest has stayed elevated and kept climbing across recent days.")
    elif c["persistence"] >= 0.45:
        bullets.append("Interest has stayed elevated for more than one day.")
    else:
        bullets.append("The elevated interest has not yet persisted across multiple days.")
    if c["spike_quality"] < 0.45:
        bullets.append(
            "Much of the recent traffic arrived in a short burst — a spike pattern "
            "rather than steady growth."
        )
    elif c["spike_quality"] >= 0.7:
        bullets.append("Recent traffic is spread across several days rather than one spike.")
    if row["status"] == "Fading / collapsing":
        bullets.append("The latest day is well below the recent peak — attention is receding.")
    bullets.append(
        f"Averaging {s['recent_avg']:,} views/day over the last 3 days "
        f"(30-day baseline: {s['baseline_avg']:,})."
    )
    return bullets


# ---------------------------------------------------------------------------
# JSON builders + validation
# ---------------------------------------------------------------------------


def change_percent(row: dict) -> int | None:
    base = row["stats"]["baseline_avg"]
    if base == 0:
        return None
    return round((row["stats"]["recent_avg"] - base) / base * 100)


def build_site_data(rows: list[dict], end_day: str, generated_at: str) -> tuple[dict, dict]:
    """(trending.json dict, {slug: topic.json dict}) from score-sorted rows."""
    pages = rows[:TOPIC_PAGES]
    slugs = assign_slugs([r["title"] for r in pages])

    topics = {}
    trending_entries = []
    for rank, row in enumerate(pages, 1):
        slug = slugs[row["title"]]
        common = {
            "title": display_title(row["title"]),
            "slug": slug,
            "score": row["score"],
            "status": row["status"],
            "change_percent": change_percent(row),
            "growth_ratio": row["stats"]["growth_ratio"],
            "recent_avg": row["stats"]["recent_avg"],
            "baseline_avg": row["stats"]["baseline_avg"],
            "explanation": explanation(row),
            "discovery": row["reasons"],
        }
        topics[slug] = {
            **common,
            "abs_change": row["stats"]["recent_avg"] - row["stats"]["baseline_avg"],
            "latest": row["stats"]["latest"],
            "components": row["components"],
            "why": why_bullets(row),
            "history": [{"date": d, "views": v} for d, v in row["history"]],
            "wikipedia_title": row["title"],
            "source": SOURCE,
            "score_version": SCORE_VERSION,
            "data_through": end_day,
            "generated_at_utc": generated_at,
        }
        if rank <= HOMEPAGE_TOPICS:
            trending_entries.append(
                {
                    "rank": rank,
                    **common,
                    "sparkline": [v for _, v in row["history"][-SPARKLINE_DAYS:]],
                }
            )

    trending = {
        "source": SOURCE,
        "score_version": SCORE_VERSION,
        "experimental": True,
        "data_through": end_day,
        "generated_at_utc": generated_at,
        "topics": trending_entries,
    }
    return trending, topics


def validate_site_data(trending: dict, topics: dict) -> list[str]:
    """Hard checks before anything is written for the website. Returns a
    list of problems (empty = valid)."""
    problems = []
    entries = trending.get("topics", [])
    if not entries:
        problems.append("trending.json has no topics")
    ranks = [e["rank"] for e in entries]
    if ranks != list(range(1, len(entries) + 1)):
        problems.append(f"ranks not consecutive from 1: {ranks}")
    scores = [e["score"] for e in entries]
    if scores != sorted(scores, reverse=True):
        problems.append("topics not ordered by descending score")
    if len({e["slug"] for e in entries}) != len(entries):
        problems.append("duplicate slugs in trending.json")
    for e in entries:
        if e["slug"] not in topics:
            problems.append(f"homepage topic {e['slug']} has no topic file")
    if len({t["slug"] for t in topics.values()}) != len(topics):
        problems.append("duplicate slugs across topic files")
    for slug, t in topics.items():
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            problems.append(f"invalid slug: {slug!r}")
        if not isinstance(t["score"], int) or not 0 <= t["score"] <= 100:
            problems.append(f"{slug}: score out of range: {t['score']!r}")
        for key in ("growth_ratio", "recent_avg", "baseline_avg"):
            v = t[key]
            if not isinstance(v, (int, float)) or not math.isfinite(v):
                problems.append(f"{slug}: non-finite {key}: {v!r}")
        hist = t["history"]
        if len(hist) < 33 or any(
            not isinstance(p["views"], int) or p["views"] < 0 for p in hist
        ):
            problems.append(f"{slug}: malformed history")
        dates = [p["date"] for p in hist]
        if dates != sorted(dates):
            problems.append(f"{slug}: history dates not ascending")
        if dates and dates[-1] != t["data_through"]:
            problems.append(f"{slug}: history does not end at data_through")
    return problems
