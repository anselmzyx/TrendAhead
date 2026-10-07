"""Unit tests for trend_math — run with:  python3 -m unittest discover pipeline"""

import unittest
from datetime import date, timedelta

from trend_math import mean, missing_dates, percent_change, split_recent_baseline


def make_series(n: int, views: int = 100, start: date = date(2026, 1, 1)):
    return [(start + timedelta(days=i), views) for i in range(n)]


class TestMean(unittest.TestCase):
    def test_simple_average(self):
        self.assertEqual(mean([1, 2, 3]), 2.0)

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            mean([])


class TestSplitRecentBaseline(unittest.TestCase):
    def test_sizes_and_no_overlap(self):
        series = make_series(40)
        recent, baseline = split_recent_baseline(series)
        self.assertEqual(len(recent), 3)
        self.assertEqual(len(baseline), 30)
        recent_dates = {d for d, _ in recent}
        baseline_dates = {d for d, _ in baseline}
        self.assertFalse(recent_dates & baseline_dates)
        # baseline ends the day before recent begins
        self.assertEqual(
            max(baseline_dates) + timedelta(days=1), min(recent_dates)
        )

    def test_recent_is_newest_data(self):
        series = make_series(33)
        recent, _ = split_recent_baseline(series)
        self.assertEqual(recent[-1][0], series[-1][0])

    def test_too_little_data_raises(self):
        with self.assertRaises(ValueError):
            split_recent_baseline(make_series(32))

    def test_unsorted_raises(self):
        series = make_series(33)
        series.reverse()
        with self.assertRaises(ValueError):
            split_recent_baseline(series)

    def test_duplicate_dates_raise(self):
        series = make_series(33)
        series[5] = series[4]
        with self.assertRaises(ValueError):
            split_recent_baseline(series)


class TestPercentChange(unittest.TestCase):
    def test_rising(self):
        self.assertAlmostEqual(percent_change(200, 100), 100.0)

    def test_falling(self):
        self.assertAlmostEqual(percent_change(50, 100), -50.0)

    def test_flat(self):
        self.assertAlmostEqual(percent_change(100, 100), 0.0)

    def test_zero_baseline_returns_none(self):
        self.assertIsNone(percent_change(10, 0))


class TestMissingDates(unittest.TestCase):
    def test_complete_range_has_no_gaps(self):
        dates = [d for d, _ in make_series(10)]
        self.assertEqual(missing_dates(dates), [])

    def test_gap_is_reported(self):
        dates = [d for d, _ in make_series(10)]
        removed = dates.pop(4)
        self.assertEqual(missing_dates(dates), [removed])

    def test_empty_list(self):
        self.assertEqual(missing_dates([]), [])


if __name__ == "__main__":
    unittest.main()
