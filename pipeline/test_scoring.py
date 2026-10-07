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

# --- Phase 7 (V1.1) benchmark shapes ---------------------------------------
STILL_ACCELERATING = flat(1_000, 27) + [1_500, 2_500, 4_000, 7_000, 12_000, 20_000]
TWO_DAY_PLATEAU = flat(1_000, 31) + [30_000, 29_000]
POST_PEAK_DECLINE = flat(1_000, 28) + [20_000, 30_000, 15_000, 6_000, 2_500]
SLOW_STEADY_BUILD = flat(3_000, 27) + [3_300, 3_700, 4_200, 4_800, 5_400, 6_100]
FRESH_BREAKOUT = flat(1_000, 32) + [40_000]
COLLAPSED_SPIKE = flat(1_000, 30) + [40_000, 3_000, 1_200]


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


class TestV11Benchmarks(unittest.TestCase):
    def test_still_accelerating_scores_high(self):
        self.assertGreaterEqual(s(STILL_ACCELERATING), 50)

    def test_two_day_plateau_moderate_but_below_sustained(self):
        plateau = s(TWO_DAY_PLATEAU)
        self.assertGreaterEqual(plateau, 25)
        self.assertLess(plateau, s(SUSTAINED_CLIMBER))

    def test_post_peak_decline_substantially_penalised(self):
        self.assertLessEqual(s(POST_PEAK_DECLINE), 15)
        self.assertLess(s(POST_PEAK_DECLINE), s(TWO_DAY_PLATEAU))

    def test_slow_steady_build_respectable(self):
        self.assertGreaterEqual(s(SLOW_STEADY_BUILD), 25)

    def test_fresh_breakout_beats_already_collapsed_spike(self):
        # A huge latest-day jump with no collapse evidence must NOT be
        # treated like a spike that has already collapsed.
        self.assertGreaterEqual(s(FRESH_BREAKOUT), 20)
        self.assertLessEqual(s(COLLAPSED_SPIKE), 15)
        self.assertGreater(s(FRESH_BREAKOUT), s(COLLAPSED_SPIKE) + 10)


class TestStatus(unittest.TestCase):
    def status(self, views):
        return score_series(views)["status"]

    def test_sustained_climber_is_building(self):
        self.assertEqual(self.status(SUSTAINED_CLIMBER), "Building")

    def test_slow_steady_build_is_building(self):
        self.assertEqual(self.status(SLOW_STEADY_BUILD), "Building")

    def test_fresh_breakout_is_breaking_out(self):
        self.assertEqual(self.status(FRESH_BREAKOUT), "Breaking out")

    def test_two_day_plateau_is_breaking_out(self):
        # 2-day-old surge still at peak: too new to call sustained.
        self.assertEqual(self.status(TWO_DAY_PLATEAU), "Breaking out")

    def test_high_plateau_is_elevated(self):
        plateau = flat(100, 27) + [150, 250, 5_000, 4_900, 4_800, 4_700]
        self.assertEqual(self.status(plateau), "Elevated")

    def test_collapsed_spike_is_peaked_fading(self):
        self.assertEqual(self.status(COLLAPSED_SPIKE), "Peaked / fading")
        self.assertEqual(self.status(POST_PEAK_DECLINE), "Peaked / fading")

    def test_flat_topic_is_weak_not_fading(self):
        # No spike ever happened — must not be labelled fading.
        self.assertEqual(self.status(STABLE_POPULAR), "Weak signal")
        self.assertEqual(self.status(HUGE_FLAT), "Weak signal")


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
