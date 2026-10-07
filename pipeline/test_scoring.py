"""Tests for the TrendAhead Score V1 — synthetic benchmarks + edge cases.

Run with:  python3 -m unittest discover pipeline
"""

import math
import unittest

from scoring import MIN_HISTORY, score_series, validate_series


def flat(level: int, n: int = 33) -> list[int]:
    return [level] * n


def wobble(level: int, n: int = 33, amp: float = 0.05) -> list[int]:
    """Deterministic +-amp wobble around level (no randomness)."""
    return [int(level * (1 + amp * math.sin(i * 1.7))) for i in range(n)]


# --- The benchmark shapes (Step 4 of the phase brief) ----------------------

STABLE_POPULAR = wobble(60_000)  # case 1
TINY_EXPLOSION = flat(2, 30) + [5, 10, 20]  # case 2
ONE_DAY_SPIKE = flat(1_000, 30) + [50_000, 1_200, 1_100]  # case 3
SUSTAINED_CLIMBER = flat(1_000, 28) + [2_000, 4_000, 8_000, 15_000, 30_000]  # case 4
RISE_THEN_COLLAPSE = flat(1_000, 28) + [4_000, 15_000, 30_000, 6_000, 2_500]  # case 5
MODERATE_PERSISTENT = flat(2_000, 27) + [2_600, 3_400, 4_400, 5_700, 7_000, 9_000]  # case 6
HUGE_FLAT = wobble(1_000_000, amp=0.01)  # case 7


def s(views):
    return score_series(views)["score"]


class TestSyntheticBenchmarks(unittest.TestCase):
    def test_case1_stable_popular_scores_low(self):
        self.assertLess(s(STABLE_POPULAR), 20)

    def test_case2_tiny_explosion_scores_very_low(self):
        self.assertLess(s(TINY_EXPLOSION), 5)

    def test_case3_one_day_spike_low_to_moderate(self):
        self.assertLess(s(ONE_DAY_SPIKE), 40)
        self.assertGreater(s(ONE_DAY_SPIKE), 0)  # damped, not deleted

    def test_case4_sustained_climber_scores_high(self):
        self.assertGreaterEqual(s(SUSTAINED_CLIMBER), 55)

    def test_case5_collapse_scores_below_sustained(self):
        self.assertLess(s(RISE_THEN_COLLAPSE), s(SUSTAINED_CLIMBER))

    def test_case6_moderate_persistent_meaningfully_high(self):
        self.assertGreaterEqual(s(MODERATE_PERSISTENT), 25)
        self.assertGreater(s(MODERATE_PERSISTENT), s(ONE_DAY_SPIKE))

    def test_case7_huge_flat_scores_low(self):
        self.assertLess(s(HUGE_FLAT), 15)

    # The two ordering guarantees the product decision demands:
    def test_sustained_climber_beats_one_day_spike(self):
        self.assertGreater(s(SUSTAINED_CLIMBER), s(ONE_DAY_SPIKE))

    def test_meaningful_volume_growth_beats_tiny_percentage_explosion(self):
        # 10,000 -> 30,000 (3x) must beat 2 -> 20 (10x)
        meaningful = flat(10_000, 28) + [12_000, 15_000, 19_000, 24_000, 30_000]
        self.assertGreater(s(meaningful), s(TINY_EXPLOSION))


class TestStatus(unittest.TestCase):
    def test_sustained_climber_is_strong(self):
        self.assertEqual(
            score_series(SUSTAINED_CLIMBER)["status"], "Strong emerging signal"
        )

    def test_collapsed_spike_is_fading(self):
        collapsed = flat(1_000, 29) + [80_000, 30_000, 5_000, 1_500]
        self.assertEqual(score_series(collapsed)["status"], "Fading / collapsing")

    def test_flat_topic_is_weak_not_fading(self):
        # No spike ever happened — must not be labelled collapsing.
        self.assertEqual(score_series(STABLE_POPULAR)["status"], "Weak signal")


class TestPathologicalInputs(unittest.TestCase):
    CASES = {
        "zero baseline": flat(0, 30) + [20_000, 40_000, 60_000],
        "near-zero baseline": flat(1, 30) + [50_000, 60_000, 70_000],
        "zero variance": flat(5_000),
        "all zeros": flat(0),
        "one extreme outlier": flat(3_000, 20) + [900_000] + flat(3_000, 12),
        "negative trend": [10_000 - 200 * i for i in range(33)],
        "huge volume": wobble(5_000_000, amp=0.02),
        "tiny volume": wobble(5),
        "sawtooth noise": [1_000 + (9_000 if i % 2 else 0) for i in range(33)],
    }

    def test_all_cases_produce_valid_finite_scores(self):
        for name, views in self.CASES.items():
            with self.subTest(case=name):
                result = score_series(views)
                self.assertIsInstance(result["score"], int)
                self.assertGreaterEqual(result["score"], 0, name)
                self.assertLessEqual(result["score"], 100, name)
                for k, v in result["components"].items():
                    self.assertTrue(math.isfinite(v), f"{name}/{k} not finite")

    def test_short_history_rejected(self):
        with self.assertRaises(ValueError):
            score_series(flat(1_000, MIN_HISTORY - 1))

    def test_malformed_values_rejected(self):
        for bad in [[-5], [1.5], ["100"], [None], [True]]:
            with self.assertRaises(ValueError):
                validate_series(flat(1_000, 32) + bad)

    def test_zero_baseline_rising_page_still_scores(self):
        # A genuinely new page with real volume must not be zeroed out.
        result = score_series(flat(0, 28) + [3_000, 8_000, 20_000, 45_000, 90_000])
        self.assertGreaterEqual(result["score"], 50)


if __name__ == "__main__":
    unittest.main()
