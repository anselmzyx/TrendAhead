"""Pure calculation helpers for the TrendAhead pipeline.

No network access, no side effects — everything here is deterministic and
unit-tested in test_trend_math.py.
"""

from __future__ import annotations

from datetime import date, timedelta


def mean(values: list[int | float]) -> float:
    """Average of a non-empty list."""
    if not values:
        raise ValueError("cannot average an empty list")
    return sum(values) / len(values)


def split_recent_baseline(
    series: list[tuple[date, int]],
    recent_days: int = 3,
    baseline_days: int = 30,
) -> tuple[list[tuple[date, int]], list[tuple[date, int]]]:
    """Split a date-ascending series into (recent, baseline).

    recent  = the last `recent_days` observations
    baseline = the `baseline_days` observations immediately before them
    The two periods never overlap. Raises if there isn't enough data or the
    series isn't sorted oldest-first.
    """
    needed = recent_days + baseline_days
    if len(series) < needed:
        raise ValueError(
            f"need at least {needed} days, got {len(series)}"
        )
    dates = [d for d, _ in series]
    if dates != sorted(dates):
        raise ValueError("series must be sorted oldest-first")
    if len(set(dates)) != len(dates):
        raise ValueError("series contains duplicate dates")
    recent = series[-recent_days:]
    baseline = series[-needed:-recent_days]
    return recent, baseline


def percent_change(recent_avg: float, baseline_avg: float) -> float | None:
    """Percentage change of recent vs baseline; None when baseline is zero
    (a percentage against nothing is meaningless, not infinite)."""
    if baseline_avg == 0:
        return None
    return (recent_avg - baseline_avg) / baseline_avg * 100


def missing_dates(dates: list[date]) -> list[date]:
    """Dates absent between the first and last observation (inclusive)."""
    if not dates:
        return []
    present = set(dates)
    out = []
    d = min(dates)
    while d <= max(dates):
        if d not in present:
            out.append(d)
        d += timedelta(days=1)
    return out
