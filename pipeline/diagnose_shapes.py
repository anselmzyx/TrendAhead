"""Phase 7, Step 1: shape diagnostics for the current top candidates.

Reads the latest cached histories (no API calls), rescores with the current
engine, and prints per-topic time-series diagnostics so shape patterns can
be judged by a human before any scoring change.

Run:  python3 pipeline/diagnose_shapes.py
"""

from __future__ import annotations

import json
from pathlib import Path

from scoring import BASELINE_FLOOR, score_series

OUTPUT_DIR = Path(__file__).parent / "output"


def rising_streak(views: list[int]) -> int:
    """Consecutive day-over-day increases ending at the latest day."""
    n = 0
    for a, b in zip(reversed(views[:-1]), reversed(views[1:])):
        if b > a:
            n += 1
        else:
            break
    return n


def elevated_streak(views: list[int], threshold: float) -> int:
    """Consecutive days >= threshold ending at the latest day."""
    n = 0
    for v in reversed(views):
        if v >= threshold:
            n += 1
        else:
            break
    return n


def diagnose(title: str, views: list[int], reasons: list[str]) -> dict:
    r = score_series(views)
    last7 = views[-7:]
    peak = max(last7)
    peak_idx = len(views) - 7 + last7.index(peak)
    base = max(r["stats"]["baseline_avg"], BASELINE_FLOOR)
    deltas3 = [b - a for a, b in zip(views[-4:-1], views[-3:])]
    direction = (
        "rising" if deltas3[-1] > 0 else "flat" if deltas3[-1] == 0 else "declining"
    )
    return {
        "title": title.replace("_", " "),
        "score": r["score"],
        "reasons": "+".join("NE" if x == "new entrant" else "IM" for x in reasons),
        "baseline": r["stats"]["baseline_avg"],
        "last7": last7,
        "peak": peak,
        "peak_days_ago": len(views) - 1 - peak_idx,
        "latest": views[-1],
        "latest_peak_ratio": views[-1] / peak if peak else 0,
        "elev_streak": elevated_streak(views, 2 * base),
        "rise_streak": rising_streak(views),
        "rising_last3": sum(1 for d in deltas3 if d > 0),
        "direction": direction,
        "concentration": peak / sum(last7) if sum(last7) else 0,
        "quality": r["components"]["spike_quality"],
        "persistence": r["components"]["persistence"],
    }


def main() -> None:
    cache_path = sorted(OUTPUT_DIR.glob("histories_*.json"))[-1]
    data = json.loads(cache_path.read_text())
    combined = json.loads(
        sorted(OUTPUT_DIR.glob("combined_scores_*.json"))[-1].read_text()
    )
    reasons = {r["title"]: r["reasons"] for r in combined["ranked"]}

    rows = []
    for title, h in data["histories"].items():
        views = [v for _, v in h["series"]]
        try:
            rows.append(diagnose(title, views, reasons.get(title, ["?"])))
        except ValueError:
            pass
    rows.sort(key=lambda r: r["score"], reverse=True)

    print(f"Diagnostics from {cache_path.name} (no API calls)\n")
    print(f"{'Topic':<30} {'Sc':>3} {'Src':<5} {'Baseln':>7} {'Peak':>8} {'PkAgo':>5} "
          f"{'Latest':>8} {'L/Pk':>5} {'ElevSt':>6} {'RiseSt':>6} {'R3':>2} {'Dir':<9} {'Conc':>5}")
    print("-" * 112)
    for r in rows[:20]:
        t = r["title"] if len(r["title"]) <= 30 else r["title"][:27] + "..."
        print(f"{t:<30} {r['score']:>3} {r['reasons']:<5} {r['baseline']:>7,} "
              f"{r['peak']:>8,} {r['peak_days_ago']:>5} {r['latest']:>8,} "
              f"{r['latest_peak_ratio']:>5.2f} {r['elev_streak']:>6} {r['rise_streak']:>6} "
              f"{r['rising_last3']:>2} {r['direction']:<9} {r['concentration']:>5.2f}")
    print("-" * 112)
    print("Src: NE=new entrant IM=improver · PkAgo: days since 7-day peak · L/Pk: latest/peak")
    print("ElevSt/RiseSt: consecutive elevated(≥2×baseline)/rising days ending today · R3: rising days of last 3")

    print("\nLast 7 days for the top 10:")
    for r in rows[:10]:
        series = "  ".join(f"{v:,}" for v in r["last7"])
        print(f"  {r['title']:<30} {series}")


if __name__ == "__main__":
    main()
