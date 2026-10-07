"""Phase 8 proof of concept: can GDELT provide a usable independent
news-attention signal for TrendAhead topics?

EXPERIMENTAL — not connected to production. Run:
    python3 pipeline/poc_gdelt.py

Requests are paced (1 per ~6s) and cached in pipeline/output/, so a full
run makes at most ~8 live requests, and re-runs make none.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gdelt import (
    GdeltError,
    drop_unreliable_tail,
    fetch_articles,
    fetch_timeline,
    fill_missing_days,
    news_stats,
)
from scoring import score_series

OUTPUT_DIR = Path(__file__).parent / "output"

TOPICS = [
    "Michael Douglas",
    "Karl Deisseroth",
    "2026 Quebec general election",
]
# Query-ambiguity experiment (Step 11): the Wikipedia title vs how news
# writers actually phrase it. Max 2 variants, no alias machinery.
AMBIGUITY_VARIANTS = ["2026 Quebec general election", "Quebec election"]


def show_articles(query: str) -> None:
    try:
        articles = fetch_articles(query, 8)
    except GdeltError as e:
        print(f"  articles FAILED: {e}")
        return
    if not articles:
        print("  (no matching articles in the last 2 weeks)")
    for a in articles:
        title = a["title"][:76]
        print(f"  [{a['seendate'][:8]}] {title}  — {a['domain']} ({a['language']})")


def analyse_timeline(query: str, verbose: bool = True) -> dict | None:
    today = datetime.now(timezone.utc).date()
    end = today - timedelta(days=1)
    start = end - timedelta(days=39)
    try:
        raw = fetch_timeline(query, start, end)
    except GdeltError as e:
        print(f"  timeline FAILED: {e}")
        return None
    kept = drop_unreliable_tail(raw, today)
    dropped = len(raw) - len(kept)
    if not kept:
        print("  timeline empty after dropping unreliable tail")
        return None
    span_start, span_end = kept[0]["date"], kept[-1]["date"]
    missing = (span_end - span_start).days + 1 - len(kept)
    full = fill_missing_days(kept, span_start, span_end)
    stats = news_stats(full)
    if verbose:
        print(f"  requested {start} → {end}  |  usable {span_start} → {span_end}")
        print(f"  {len(raw)} raw points, {dropped} unreliable tail point(s) dropped, "
              f"{missing} absent day(s) filled as 0")
        print("  last 10 usable days (Date | articles | monitored that day):")
        for p in full[-10:]:
            print(f"    {p['date']}  {p['articles']:>5}  / {p['norm']:,}")
        if stats:
            pct = f"{stats['pct_change']:+d}%" if stats["pct_change"] is not None else "n/a (zero baseline)"
            print(f"  news recent 3-day avg: {stats['recent_avg']}  |  "
                  f"baseline avg ({stats['baseline_days']}d): {stats['baseline_avg']}  |  "
                  f"change: {pct}")
    return {"full": full, "stats": stats, "span": (str(span_start), str(span_end))}


def wikipedia_summary(title: str) -> str:
    cache = sorted(OUTPUT_DIR.glob("histories_*.json"))[-1]
    histories = json.loads(cache.read_text())["histories"]
    h = histories.get(title.replace(" ", "_"))
    if not h:
        return "no cached Wikipedia history"
    views = [v for _, v in h["series"]]
    r = score_series(views)
    pct = (r["stats"]["recent_avg"] - r["stats"]["baseline_avg"]) / max(
        r["stats"]["baseline_avg"], 1
    ) * 100
    return (f"recent {r['stats']['recent_avg']:,}/day vs baseline "
            f"{r['stats']['baseline_avg']:,}/day ({pct:+.0f}%) — shape: {r['status']}")


def main() -> None:
    print("GDELT DOC 2.0 proof of concept — EXPERIMENTAL, not in production\n")
    results = {}
    for topic in TOPICS:
        print(f"### {topic}  (query: \"{topic}\")")
        print("  — recent matching articles —")
        show_articles(topic)
        print("  — news-attention timeline —")
        results[topic] = analyse_timeline(topic)
        print()

    print("### Query ambiguity experiment")
    for variant in AMBIGUITY_VARIANTS:
        print(f'\n  variant: "{variant}"')
        show_articles(variant)
        r = analyse_timeline(variant, verbose=False)
        if r and r["stats"]:
            s = r["stats"]
            print(f"  → recent avg {s['recent_avg']} vs baseline {s['baseline_avg']} "
                  f"articles/day (usable {r['span'][0]} → {r['span'][1]})")

    print("\n### Wikipedia vs GDELT (same topics)")
    for topic in TOPICS:
        print(f"\n  {topic}")
        print(f"    Wikipedia: {wikipedia_summary(topic)}")
        r = results.get(topic)
        if r and r["stats"]:
            s = r["stats"]
            pct = f"{s['pct_change']:+d}%" if s["pct_change"] is not None else "n/a"
            print(f"    GDELT:     recent {s['recent_avg']} vs baseline "
                  f"{s['baseline_avg']} articles/day ({pct})")
        else:
            print("    GDELT:     no usable timeline")


if __name__ == "__main__":
    main()
