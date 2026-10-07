"""Unit tests for discovery.py — run with:  python3 -m unittest discover pipeline"""

import unittest
from datetime import date, timedelta

from discovery import (
    build_pool,
    fill_gaps,
    noise_reason,
    provisional_rank,
    select_new_entrants,
)

D1, D2, D3, D4 = (date(2026, 10, 1) + timedelta(days=i) for i in range(4))


class TestNoiseReason(unittest.TestCase):
    def test_real_topics_pass(self):
        for title in ["Solid-state_battery", "AC/DC", "Deaths_in_2026", "2026_film"]:
            self.assertIsNone(noise_reason(title), title)

    def test_namespaces_are_noise(self):
        self.assertIn("namespace", noise_reason("Special:Search"))
        self.assertIn("namespace", noise_reason("Wikipedia:Featured_pictures"))
        self.assertIn("namespace", noise_reason("Portal:Current_events"))

    def test_navigation_pages_are_noise(self):
        self.assertIsNotNone(noise_reason("Main_Page"))

    def test_blank_title_is_noise(self):
        self.assertIsNotNone(noise_reason(""))
        self.assertIsNotNone(noise_reason("   "))

    def test_colon_inside_title_is_not_noise(self):
        # Titles merely CONTAINING a colon are legitimate articles.
        self.assertIsNone(noise_reason("Star_Wars:_The_Rise_of_Skywalker"))


class TestBuildPool(unittest.TestCase):
    def test_dedup_and_aggregation(self):
        lists = {
            D1: [{"article": "A", "views": 100, "rank": 5}],
            D2: [
                {"article": "A", "views": 300, "rank": 2},
                {"article": "B", "views": 50, "rank": 9},
            ],
        }
        pool = build_pool(lists)
        self.assertEqual(set(pool), {"A", "B"})
        self.assertEqual(pool["A"]["days"], [D1, D2])
        self.assertEqual(pool["A"]["max_views"], 300)
        self.assertEqual(pool["A"]["best_rank"], 2)

    def test_malformed_entries_skipped(self):
        pool = build_pool({D1: [{"article": None, "views": 1}, {"views": 2}, {"article": "OK", "views": 3, "rank": 1}]})
        self.assertEqual(set(pool), {"OK"})


class TestSelectNewEntrants(unittest.TestCase):
    def test_only_late_appearers_selected_by_views(self):
        pool = {
            "Perennial": {"days": [D1, D3], "max_views": 9999, "best_rank": 1},
            "NewBig": {"days": [D3, D4], "max_views": 500, "best_rank": 10},
            "NewSmall": {"days": [D4], "max_views": 100, "best_rank": 90},
            "OldOnly": {"days": [D1], "max_views": 800, "best_rank": 3},
        }
        got = select_new_entrants(pool, {D1, D2}, {D3, D4}, limit=10)
        self.assertEqual(got, ["NewBig", "NewSmall"])

    def test_limit_respected(self):
        pool = {f"T{i}": {"days": [D4], "max_views": i, "best_rank": 1} for i in range(10)}
        self.assertEqual(len(select_new_entrants(pool, {D1}, {D4}, limit=3)), 3)


class TestFillGaps(unittest.TestCase):
    def test_missing_days_become_zero(self):
        series = [(D1, 10), (D3, 30)]
        full, filled = fill_gaps(series, D1, D4)
        self.assertEqual(full, [(D1, 10), (D2, 0), (D3, 30), (D4, 0)])
        self.assertEqual(filled, 2)

    def test_complete_series_untouched(self):
        series = [(D1, 1), (D2, 2)]
        full, filled = fill_gaps(series, D1, D2)
        self.assertEqual(full, series)
        self.assertEqual(filled, 0)


class TestProvisionalRank(unittest.TestCase):
    def make(self, title, recent, baseline):
        return {"title": title, "recent_avg": recent, "baseline_avg": baseline}

    def test_low_volume_excluded(self):
        # 2 -> 10 views: 400% growth but far below the volume floor.
        ranked, excluded = provisional_rank([self.make("tiny", 10, 2)])
        self.assertEqual(ranked, [])
        self.assertEqual(excluded[0]["title"], "tiny")
        self.assertIn("recent_avg", excluded[0]["excluded_because"])

    def test_zero_baseline_no_crash_and_floored(self):
        ranked, _ = provisional_rank([self.make("new", 50000, 0)])
        self.assertEqual(ranked[0]["ratio"], 50000 / 100)

    def test_ordering_by_ratio_not_raw_views(self):
        ranked, _ = provisional_rank(
            [
                self.make("huge_but_flat", 1_000_000, 950_000),
                self.make("smaller_but_surging", 30_000, 3_000),
            ]
        )
        self.assertEqual(ranked[0]["title"], "smaller_but_surging")


if __name__ == "__main__":
    unittest.main()
