"""Tests for site_data.py — slugs, explanations, building, validation."""

import unittest

from site_data import (
    assign_slugs,
    build_site_data,
    explanation,
    slugify,
    validate_site_data,
    why_bullets,
)


def make_row(title="Test Topic", score=50, status="Building",
             ratio=3.0, recent=30_000, baseline=10_000, days=40):
    history = [[f"2026-09-{i + 1:02d}" if i < 30 else f"2026-10-{i - 29:02d}", baseline]
               for i in range(days - 3)]
    history += [[f"2026-10-{d:02d}", recent] for d in (8, 9, 10)]
    return {
        "title": title,
        "reasons": ["new entrant"],
        "score": score,
        "status": status,
        "components": {"acceleration": 0.7, "anomaly": 1.0, "persistence": 0.8,
                       "momentum": 0.9, "volume": 0.7, "spike_quality": 0.8},
        "stats": {"recent_avg": recent, "baseline_avg": baseline,
                  "baseline_std": 50.0, "latest": recent, "growth_ratio": ratio},
        "history": [(d, v) for d, v in history],
    }


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Solid-state battery"), "solid-state-battery")

    def test_underscores_and_parentheses(self):
        self.assertEqual(slugify("Cleo_(mathematician)"), "cleo-mathematician")

    def test_accents_transliterated(self):
        self.assertEqual(slugify("Parti_Québécois"), "parti-quebecois")
        self.assertEqual(slugify("Goiânia_accident"), "goiania-accident")

    def test_en_dash_becomes_hyphen(self):
        self.assertEqual(slugify("2026–27_UEFA_Nations_League"), "2026-27-uefa-nations-league")

    def test_apostrophes_and_punctuation(self):
        self.assertEqual(slugify("O'Connor & Sons: Rise!"), "o-connor-sons-rise")

    def test_non_latin_falls_back_to_stable_hash(self):
        a, b = slugify("東京物語"), slugify("東京物語")
        self.assertEqual(a, b)  # deterministic
        self.assertTrue(a.startswith("topic-"))
        self.assertNotEqual(a, slugify("歌舞伎"))

    def test_collisions_get_suffixes_not_overwritten(self):
        slugs = assign_slugs(["AC/DC", "AC DC", "AC-DC"])
        self.assertEqual(len(set(slugs.values())), 3)
        self.assertEqual(slugs["AC/DC"], "ac-dc")
        self.assertEqual(slugs["AC DC"], "ac-dc-2")
        self.assertEqual(slugs["AC-DC"], "ac-dc-3")


class TestExplanation(unittest.TestCase):
    def test_ratio_wording(self):
        self.assertIn("3.0×", explanation(make_row(ratio=3.0)))

    def test_large_ratio_rounded(self):
        self.assertIn("250×", explanation(make_row(ratio=249.5)))

    def test_small_change_uses_percent(self):
        self.assertIn("%", explanation(make_row(ratio=1.4)))

    def test_fading_wording_does_not_imply_acceleration(self):
        text = explanation(make_row(status="Peaked / fading", ratio=12.0))
        self.assertIn("fallen back", text)

    def test_why_bullets_mention_fading(self):
        bullets = why_bullets(make_row(status="Peaked / fading"))
        self.assertTrue(any("receding" in b for b in bullets))


class TestBuildAndValidate(unittest.TestCase):
    def test_build_produces_valid_dataset(self):
        rows = [make_row(f"Topic {i}", score=90 - i) for i in range(30)]
        trending, topics = build_site_data(rows, "2026-10-10", "2026-10-11T06:00:00+00:00")
        self.assertEqual(validate_site_data(trending, topics), [])
        self.assertEqual(len(trending["topics"]), 12)
        self.assertEqual(len(topics), 24)
        self.assertEqual(trending["topics"][0]["rank"], 1)
        self.assertEqual(len(trending["topics"][0]["sparkline"]), 14)

    def test_validation_catches_bad_score(self):
        rows = [make_row("Good"), make_row("Bad")]
        trending, topics = build_site_data(rows, "2026-10-10", "x")
        topics[list(topics)[0]]["score"] = 150
        self.assertTrue(any("out of range" in p for p in validate_site_data(trending, topics)))

    def test_validation_catches_duplicate_slugs(self):
        rows = [make_row("Good"), make_row("Other")]
        trending, topics = build_site_data(rows, "2026-10-10", "x")
        trending["topics"][1]["slug"] = trending["topics"][0]["slug"]
        self.assertTrue(any("duplicate" in p for p in validate_site_data(trending, topics)))

    def test_validation_catches_history_not_ending_at_data_through(self):
        rows = [make_row("Good")]
        trending, topics = build_site_data(rows, "2026-12-31", "x")
        self.assertTrue(any("data_through" in p for p in validate_site_data(trending, topics)))


if __name__ == "__main__":
    unittest.main()
