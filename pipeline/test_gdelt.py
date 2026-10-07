"""Tests for gdelt.py pure logic — fixtures only, no live API calls."""

import unittest
from datetime import date

from gdelt import (
    GdeltError,
    drop_unreliable_tail,
    fill_missing_days,
    news_stats,
    parse_timeline,
)

TODAY = date(2026, 10, 8)


def pt(day: int, articles: int, norm: int = 150_000, month: int = 10) -> dict:
    return {"date": date(2026, month, day), "articles": articles, "norm": norm}


class TestParseTimeline(unittest.TestCase):
    PAYLOAD = {
        "query_details": {},
        "timeline": [
            {
                "series": "Article Count",
                "data": [
                    {"date": "20261003T000000Z", "value": 5, "norm": 150000},
                    {"date": "20261001T000000Z", "value": 2, "norm": 140000},
                ],
            }
        ],
    }

    def test_parses_and_sorts_ascending(self):
        points = parse_timeline(self.PAYLOAD)
        self.assertEqual([p["date"] for p in points],
                         [date(2026, 10, 1), date(2026, 10, 3)])
        self.assertEqual(points[1]["articles"], 5)
        self.assertEqual(points[0]["norm"], 140000)

    def test_missing_timeline_raises(self):
        with self.assertRaises(GdeltError):
            parse_timeline({"error": "nope"})

    def test_malformed_point_raises(self):
        bad = {"timeline": [{"data": [{"date": "20261001T000000Z", "value": -1}]}]}
        with self.assertRaises(GdeltError):
            parse_timeline(bad)


class TestDropUnreliableTail(unittest.TestCase):
    def test_current_utc_day_removed(self):
        points = [pt(6, 10), pt(7, 12), pt(8, 3)]
        kept = drop_unreliable_tail(points, TODAY)
        self.assertEqual(kept[-1]["date"], date(2026, 10, 7))

    def test_low_norm_tail_bucket_removed(self):
        # Final bucket's norm is a fraction of a normal day -> still backfilling.
        points = [pt(4, 10), pt(5, 12), pt(6, 9), pt(7, 2, norm=4_000)]
        kept = drop_unreliable_tail(points, TODAY)
        self.assertEqual(kept[-1]["date"], date(2026, 10, 6))

    def test_healthy_tail_kept(self):
        points = [pt(5, 10), pt(6, 12), pt(7, 11)]
        self.assertEqual(len(drop_unreliable_tail(points, TODAY)), 3)

    def test_empty_input(self):
        self.assertEqual(drop_unreliable_tail([], TODAY), [])


class TestFillMissingDays(unittest.TestCase):
    def test_gaps_become_zero_articles(self):
        points = [pt(1, 4), pt(3, 6)]
        full = fill_missing_days(points, date(2026, 10, 1), date(2026, 10, 4))
        self.assertEqual(len(full), 4)
        self.assertEqual(full[1]["articles"], 0)
        self.assertEqual(full[3]["articles"], 0)


class TestNewsStats(unittest.TestCase):
    def test_recent_vs_baseline(self):
        points = [pt(d, 10, month=9) for d in range(1, 31)] + [
            pt(1, 40), pt(2, 50), pt(3, 60)
        ]
        s = news_stats(points)
        self.assertEqual(s["recent_avg"], 50.0)
        self.assertEqual(s["baseline_avg"], 10.0)
        self.assertEqual(s["pct_change"], 400)
        self.assertEqual(s["baseline_days"], 30)

    def test_zero_baseline_returns_none_pct(self):
        points = [pt(d, 0, month=9) for d in range(1, 31)] + [pt(1, 9), pt(2, 9), pt(3, 9)]
        self.assertIsNone(news_stats(points)["pct_change"])

    def test_too_little_history_returns_none(self):
        self.assertIsNone(news_stats([pt(1, 5), pt(2, 6)]))


if __name__ == "__main__":
    unittest.main()
