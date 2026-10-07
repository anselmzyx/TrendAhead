"""Tests for query mapping, relevance gate and confirmation maths.
Fixtures only — no live GDELT calls."""

import unittest
from datetime import date

from cross_source import (
    aligned_windows,
    classify,
    confirmation_value,
)
from news_query import (
    MIN_RELEVANCE,
    query_variants,
    relevance_confidence,
    syndication_ratio,
)


class TestQueryVariants(unittest.TestCase):
    def test_plain_title_single_variant(self):
        self.assertEqual(query_variants("Michael Douglas"), ["Michael Douglas"])

    def test_parenthetical_removed(self):
        self.assertEqual(
            query_variants("Cleo_(mathematician)"), ["Cleo (mathematician)", "Cleo"]
        )

    def test_election_title_generic_rules(self):
        self.assertEqual(
            query_variants("2026_Quebec_general_election"),
            [
                "2026 Quebec general election",
                "Quebec general election",
                "Quebec election",
            ],
        )

    def test_year_range_prefix_removed(self):
        variants = query_variants("2026–27_UEFA_Nations_League")
        self.assertIn("UEFA Nations League", variants)

    def test_at_most_three_variants(self):
        self.assertLessEqual(len(query_variants("2026_Quebec_general_election")), 3)


class TestRelevanceGate(unittest.TestCase):
    def test_phrase_matches_score_high(self):
        titles = [
            "Quebec election results: PQ wins",
            "Voters head to polls in Quebec election",
            "Quebec election campaign heats up",
            "Unrelated story about weather",
        ]
        self.assertGreaterEqual(
            relevance_confidence("Quebec election", titles), MIN_RELEVANCE
        )

    def test_unrelated_articles_fail_gate(self):
        titles = ["Stock markets rally", "Weather warning issued", "Recipe of the day"]
        self.assertLess(relevance_confidence("Quebec election", titles), MIN_RELEVANCE)

    def test_no_articles_scores_zero(self):
        self.assertEqual(relevance_confidence("Anything", []), 0.0)

    def test_syndication_ratio(self):
        self.assertEqual(syndication_ratio(["a.com", "a.com", "b.com", "c.com"]), 0.75)
        self.assertEqual(syndication_ratio([]), 0.0)


def pts(counts, start=date(2026, 9, 1)):
    from datetime import timedelta

    return [
        {"date": start + timedelta(days=i), "articles": c, "norm": 150_000}
        for i, c in enumerate(counts)
    ]


class TestAlignedWindows(unittest.TestCase):
    def test_windows_end_on_latest_complete_date(self):
        w = aligned_windows(pts([5] * 30 + [20, 25, 30]))
        self.assertEqual(w["recent_avg"], 25.0)
        self.assertEqual(w["baseline_avg"], 5.0)
        self.assertEqual(str(w["aligned_through"]), "2026-10-03")

    def test_too_little_history_returns_none(self):
        self.assertIsNone(aligned_windows(pts([5] * 10)))


class TestConfirmationValue(unittest.TestCase):
    def test_strong_confirmation(self):
        # meaningful baseline, sustained ~5x rise, confident query
        v = confirmation_value(recent_avg=25, baseline_avg=5, relevance=0.8)
        self.assertGreaterEqual(v, 0.3)
        self.assertEqual(classify(v), "confirmed")

    def test_tiny_baseline_zero_to_one_article_is_not_confirmation(self):
        v = confirmation_value(recent_avg=1, baseline_avg=0, relevance=1.0)
        self.assertEqual(v, 0.0)
        self.assertEqual(classify(v), "not_confirmed")

    def test_flat_news_not_confirmed(self):
        v = confirmation_value(recent_avg=20, baseline_avg=20, relevance=0.9)
        self.assertEqual(v, 0.0)
        self.assertEqual(classify(v), "not_confirmed")

    def test_low_relevance_drags_value_down(self):
        high = confirmation_value(30, 5, relevance=0.9)
        low = confirmation_value(30, 5, relevance=0.3)
        self.assertGreater(high, low)

    def test_unavailable_is_distinct_from_not_confirmed(self):
        self.assertEqual(classify(None), "unavailable")
        self.assertEqual(classify(0.1), "not_confirmed")

    def test_value_bounded_zero_to_one(self):
        v = confirmation_value(recent_avg=10_000, baseline_avg=1, relevance=1.0)
        self.assertLessEqual(v, 1.0)
        self.assertGreaterEqual(v, 0.0)


if __name__ == "__main__":
    unittest.main()
