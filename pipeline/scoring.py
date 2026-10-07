"""TrendAhead Score V1 — pure, deterministic scoring logic.

Input: a COMPLETE daily views series (oldest first, gaps already filled).
Output: 0–100 integer score + inspectable component subscores + status.

The full methodology, with reasoning for every constant, is documented in
pipeline/SCORING.md. Keep that file in sync with any change here.

The score judges the SHAPE and QUALITY of the attention time series only —
it never classifies the real-world reason behind the attention.
"""

from __future__ import annotations

from statistics import pstdev

MIN_HISTORY = 33  # 3 recent days + 30 baseline days
RECENT_DAYS = 3
BASELINE_DAYS = 30

BASELINE_FLOOR = 100  # views/day; stops near-zero baselines exploding ratios
RATIO_CAP = 50  # growth ratios above 50x earn nothing extra
Z_CAP = 10  # anomaly z-scores above 10 earn nothing extra
STD_FLOOR_FRAC = 0.05  # std floored at 5% of baseline (zero-variance guard)
VOL_LO = 1_000  # recent views/day at (or below) which volume factor = 0
VOL_HI = 100_000  # recent views/day at (or above) which volume factor = 1
ELEVATED_MULT = 1.5  # a day is "elevated" at >= 1.5x baseline
PERSISTENCE_WINDOW = 5  # days examined for elevation/rising streaks
QUALITY_WINDOW = 7  # days examined for concentration/collapse
COLLAPSE_RATIO = 0.4  # latest below 40% of recent peak => fading status

WEIGHTS = {"acceleration": 0.35, "anomaly": 0.25, "persistence": 0.40}
QUALITY_FLOOR = 0.25  # worst spike keeps 25% of its score (damped, not deleted)
VOLUME_EXPONENT = 0.5  # sqrt softens the gate: volume qualifies a topic, it
# shouldn't dominate the score (it's already log-scaled; tiny pages still = 0)


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _mean(xs: list[int | float]) -> float:
    return sum(xs) / len(xs)


# --------------------------------------------------------------------------
# Components — each returns a value in [0, 1]
# --------------------------------------------------------------------------


def acceleration(recent_avg: float, baseline_avg: float) -> float:
    """Log-damped growth of recent attention vs the topic's own baseline.
    log10 keeps 10x vs 1000x from differing absurdly; capped at RATIO_CAP."""
    from math import log10

    ratio = recent_avg / max(baseline_avg, BASELINE_FLOOR)
    if ratio <= 1:
        return 0.0
    return _clamp01(log10(min(ratio, RATIO_CAP)) / log10(RATIO_CAP))


def anomaly(recent_avg: float, baseline_avg: float, baseline_std: float) -> float:
    """How statistically unusual recent attention is (capped z-score).
    The std floor keeps flat histories from producing infinite z."""
    std = max(baseline_std, STD_FLOOR_FRAC * baseline_avg, 1.0)
    z = (recent_avg - baseline_avg) / std
    return _clamp01(z / Z_CAP)


def persistence(views: list[int], baseline_avg: float) -> float:
    """Reward attention that stays elevated and keeps rising across the last
    PERSISTENCE_WINDOW days — the heart of "sustained climber > spike".

    0.6 x fraction of recent days elevated above baseline
    + 0.4 x fraction of recent day-over-day changes that are increases."""
    window = views[-PERSISTENCE_WINDOW:]
    threshold = max(ELEVATED_MULT * baseline_avg, ELEVATED_MULT * BASELINE_FLOOR)
    elevated = sum(1 for v in window if v >= threshold) / len(window)
    deltas = list(zip(views[-(PERSISTENCE_WINDOW + 1) :], views[-PERSISTENCE_WINDOW:]))
    rising = sum(1 for a, b in deltas if b > a) / len(deltas)
    return 0.6 * elevated + 0.4 * rising


def volume_factor(recent_avg: float) -> float:
    """Smooth log-scale weight for absolute attention: 0 at <=VOL_LO
    views/day, 1 at >=VOL_HI. Multiplies the whole score, so tiny pages
    cannot rank on percentage growth alone — no cliff, just a ramp."""
    from math import log10

    if recent_avg <= VOL_LO:
        return 0.0
    return _clamp01((log10(recent_avg) - log10(VOL_LO)) / (log10(VOL_HI) - log10(VOL_LO)))


def spike_quality(views: list[int]) -> float:
    """1 = healthy sustained signal, 0 = pathological one-day spike.

    Judged purely on the last QUALITY_WINDOW days of the series:
    - concentration: share of the window's traffic on its single biggest
      day (1/7 = perfectly even -> quality 1; ~all on one day -> 0)
    - collapse: latest day as a share of the window's peak (1 = still at
      peak; near 0 = the attention is already gone)."""
    window = views[-QUALITY_WINDOW:]
    total = sum(window)
    if total == 0:
        return 0.0
    peak = max(window)
    even = 1 / len(window)
    concentration_quality = 1 - _clamp01((peak / total - even) / (1 - even))
    collapse_quality = _clamp01(views[-1] / peak)
    return 0.5 * concentration_quality + 0.5 * collapse_quality


# --------------------------------------------------------------------------
# The score
# --------------------------------------------------------------------------


def validate_series(views: list[int]) -> None:
    if len(views) < MIN_HISTORY:
        raise ValueError(f"need >= {MIN_HISTORY} complete days, got {len(views)}")
    for v in views:
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            raise ValueError(f"views must be non-negative integers, got {v!r}")


def score_series(views: list[int]) -> dict:
    """Compute the TrendAhead Score V1 for one complete daily series.

    Returns a dict with the integer `score` (0–100), a provisional
    `status`, every component subscore, and the underlying stats — nothing
    is hidden behind the final number.
    """
    validate_series(views)
    recent = views[-RECENT_DAYS:]
    baseline = views[-MIN_HISTORY:-RECENT_DAYS]
    recent_avg = _mean(recent)
    baseline_avg = _mean(baseline)
    baseline_std = pstdev(baseline)

    components = {
        "acceleration": acceleration(recent_avg, baseline_avg),
        "anomaly": anomaly(recent_avg, baseline_avg, baseline_std),
        "persistence": persistence(views, baseline_avg),
        "volume": volume_factor(recent_avg),
        "spike_quality": spike_quality(views),
    }
    core = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)
    quality_factor = QUALITY_FLOOR + (1 - QUALITY_FLOOR) * components["spike_quality"]
    raw = 100 * core * components["volume"] ** VOLUME_EXPONENT * quality_factor
    score = int(round(max(0.0, min(100.0, raw))))

    return {
        "score": score,
        "status": _status(score, views, baseline_avg),
        "components": {k: round(v, 3) for k, v in components.items()},
        "stats": {
            "recent_avg": round(recent_avg),
            "baseline_avg": round(baseline_avg),
            "baseline_std": round(baseline_std, 1),
            "latest": views[-1],
            "growth_ratio": round(recent_avg / max(baseline_avg, BASELINE_FLOOR), 2),
        },
    }


def _status(score: int, views: list[int], baseline_avg: float) -> str:
    """Provisional, momentum-aware label — secondary to the score."""
    window = views[-QUALITY_WINDOW:]
    peak = max(window)
    spiked = peak >= 3 * max(baseline_avg, BASELINE_FLOOR)
    if spiked and views[-1] < COLLAPSE_RATIO * peak:
        return "Fading / collapsing"
    if score >= 60:
        return "Strong emerging signal"
    if score >= 35:
        return "Emerging signal"
    return "Weak signal"
