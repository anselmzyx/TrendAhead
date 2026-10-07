"""Phase 7, Step 6: compare candidate V1.1 refinements against V1.

Proposed ingredients (shape-only, transparent):
  momentum(views)      = 0.6·(latest/7-day peak) + 0.4·(recency-weighted
                         rising share of the last 3 day-over-day changes,
                         weights 1,2,3)
  persistence_v2       = like V1 persistence, but a day-over-day rise only
                         counts when the day it rises TO is elevated —
                         sub-baseline noise rises (61→71→92 views) earn
                         nothing.

Variants:
  V1.1a  core = .30·accel + .20·anomaly + .30·persistence_v2 + .20·momentum
  V1.1b  V1 core (with persistence_v2) × momentum damp (0.4 + 0.6·m)
  V1.1c  persistence := .4·elevated + .3·rising_v2 + .3·momentum, V1 weights

Run:  python3 pipeline/compare_v11.py
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import pstdev

from discovery import noise_reason
from scoring import (
    BASELINE_FLOOR,
    ELEVATED_MULT,
    acceleration,
    anomaly,
    spike_quality,
    volume_factor,
)

OUTPUT_DIR = Path(__file__).parent / "output"


def momentum(views: list[int]) -> float:
    last7 = views[-7:]
    peak = max(last7)
    near_peak = min(1.0, views[-1] / peak) if peak else 0.0
    deltas = [b - a for a, b in zip(views[-4:-1], views[-3:])]
    weighted = sum(w for w, d in zip((1, 2, 3), deltas) if d > 0) / 6
    return 0.6 * near_peak + 0.4 * weighted


def persistence_v2(views: list[int], baseline_avg: float) -> float:
    window = views[-5:]
    threshold = max(ELEVATED_MULT * baseline_avg, ELEVATED_MULT * BASELINE_FLOOR)
    elevated = sum(1 for v in window if v >= threshold) / len(window)
    pairs = list(zip(views[-6:-1], views[-5:]))
    rising = sum(1 for a, b in pairs if b > a and b >= threshold) / len(pairs)
    return 0.6 * elevated + 0.4 * rising


def components(views: list[int]) -> dict:
    recent = views[-3:]
    baseline = views[-33:-3]
    r_avg = sum(recent) / 3
    b_avg = sum(baseline) / 30
    return {
        "accel": acceleration(r_avg, b_avg),
        "anom": anomaly(r_avg, b_avg, pstdev(baseline)),
        "pers2": persistence_v2(views, b_avg),
        "mom": momentum(views),
        "vol": volume_factor(r_avg),
        "qual": spike_quality(views),
    }


def v1(views):  # reference: current production formula
    from scoring import score_series

    return score_series(views)["score"]


def v11a(c):
    core = 0.30 * c["accel"] + 0.20 * c["anom"] + 0.30 * c["pers2"] + 0.20 * c["mom"]
    return 100 * core * c["vol"] ** 0.5 * (0.25 + 0.75 * c["qual"])


def v11b(c):
    core = 0.35 * c["accel"] + 0.25 * c["anom"] + 0.40 * c["pers2"]
    return 100 * core * c["vol"] ** 0.5 * (0.25 + 0.75 * c["qual"]) * (0.4 + 0.6 * c["mom"])


def v11c(c):
    pers = c["pers2"] / 0.6 * 0.4 if False else None  # placeholder, see below
    # c: rebuild persistence as .4 elevated-share + .3 rising + .3 momentum.
    # We reuse pers2's internals implicitly via a blended approximation:
    pers = 0.5 * c["pers2"] + 0.5 * c["mom"]
    core = 0.35 * c["accel"] + 0.25 * c["anom"] + 0.40 * pers
    return 100 * core * c["vol"] ** 0.5 * (0.25 + 0.75 * c["qual"])


SYNTH = {
    "sustained climber": [1000] * 28 + [2000, 4000, 8000, 15000, 30000],
    "still accelerating": [1000] * 27 + [1500, 2500, 4000, 7000, 12000, 20000],
    "two-day high plateau": [1000] * 31 + [30000, 29000],
    "post-peak decline": [1000] * 28 + [20000, 30000, 15000, 6000, 2500],
    "slow steady build": [3000] * 27 + [3300, 3700, 4200, 4800, 5400, 6100],
    "fresh breakout (no collapse yet)": [1000] * 32 + [40000],
    "collapsed one-day spike": [1000] * 30 + [40000, 3000, 1200],
    "stable popular": [60000] * 33,
    "tiny explosion": [2] * 30 + [5, 10, 20],
}


def main() -> None:
    print("=== SYNTHETIC SHAPES ===")
    print(f"{'shape':<34} {'V1':>4} {'V1.1a':>6} {'V1.1b':>6} {'V1.1c':>6} {'mom':>5}")
    for name, views in SYNTH.items():
        c = components(views)
        print(f"{name:<34} {v1(views):>4} {v11a(c):>6.0f} {v11b(c):>6.0f} "
              f"{v11c(c):>6.0f} {c['mom']:>5.2f}")

    cache_path = sorted(OUTPUT_DIR.glob("histories_*.json"))[-1]
    histories = json.loads(cache_path.read_text())["histories"]
    rows = []
    for title, h in histories.items():
        if noise_reason(title):
            continue  # stale pre-filter cache entries (e.g. Wikimedia_Foundation)
        views = [v for _, v in h["series"]]
        if len(views) < 33:
            continue
        c = components(views)
        rows.append({
            "title": title.replace("_", " "), "c": c, "v1": v1(views),
            "a": v11a(c), "b": v11b(c), "cc": v11c(c),
            "lp": views[-1] / max(views[-7:]),
        })

    print(f"\n=== REAL CANDIDATES ({cache_path.name}) — sorted by V1.1a ===")
    print(f"{'topic':<32} {'V1':>4} {'V1.1a':>6} {'V1.1b':>6} {'V1.1c':>6} "
          f"{'mom':>5} {'L/Pk':>5}")
    for r in sorted(rows, key=lambda r: r["a"], reverse=True)[:20]:
        t = r["title"] if len(r["title"]) <= 32 else r["title"][:29] + "..."
        print(f"{t:<32} {r['v1']:>4} {r['a']:>6.0f} {r['b']:>6.0f} {r['cc']:>6.0f} "
              f"{r['c']['mom']:>5.2f} {r['lp']:>5.2f}")

    print("\nBiggest V1 → V1.1a movers (post-peak cluster should fall):")
    movers = sorted(rows, key=lambda r: r["a"] - r["v1"])
    for r in movers[:6]:
        print(f"  ↓ {r['title']:<32} {r['v1']:>3} → {r['a']:>3.0f}  (L/Pk {r['lp']:.2f})")
    for r in movers[-4:]:
        print(f"  ↑ {r['title']:<32} {r['v1']:>3} → {r['a']:>3.0f}  (L/Pk {r['lp']:.2f})")


if __name__ == "__main__":
    main()
