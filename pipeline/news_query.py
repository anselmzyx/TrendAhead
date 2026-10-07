"""Deterministic Wikipedia-title → news-query mapping + relevance gate.

Pure logic, no network. Conservative by design: when we cannot show that a
query plausibly refers to the intended topic, the news signal is treated
as UNAVAILABLE rather than forced into the product. No LLMs, no per-topic
hand-written aliases — only generic, transparent transformations.
"""

from __future__ import annotations

import re

# Generic (not topic-specific) transformation rules, applied in order.
# Each produces at most one extra variant; max 3 queries per title.
_YEAR_PREFIX = re.compile(r"^\d{4}(?:[–-]\d{2,4})?\s+")
_PARENTHETICAL = re.compile(r"\s*\([^)]*\)\s*$")

# Tokens too generic to serve as relevance evidence on their own.
_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into",
    "general", "election", "elections", "list", "history",
}


def query_variants(title: str) -> list[str]:
    """1–3 deterministic query candidates, most specific first.

    1. the exact Wikipedia title (underscores as spaces)
    2. parenthetical disambiguator removed ("Cleo (mathematician)" → "Cleo")
    3. leading year removed ("2026 Quebec general election" →
       "Quebec general election"), then "general election" simplified to
       "election" — a generic rule for how news wording differs from
       Wikipedia's formal election titles.
    """
    exact = title.replace("_", " ").strip()
    variants = [exact]
    no_paren = _PARENTHETICAL.sub("", exact).strip()
    if no_paren and no_paren != exact:
        variants.append(no_paren)
    no_year = _YEAR_PREFIX.sub("", no_paren).strip()
    if no_year and no_year not in variants:
        variants.append(no_year)
    simplified = no_year.replace("general election", "election").strip()
    if simplified and simplified not in variants:
        variants.append(simplified)
    return variants[:3]


def _tokens(text: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9]+", text.lower())
        if len(t) >= 4 and t not in _STOPWORDS
    }


def relevance_confidence(query: str, article_titles: list[str]) -> float:
    """0–1 confidence that sampled articles refer to the intended topic.

    0.7 × share of sampled titles containing the full query phrase
    + 0.3 × share containing at least one distinctive query token.
    (GDELT matches queries against full article text, so a title mentioning
    the phrase is strong evidence; a lone token is weak evidence.)
    Returns 0.0 when there are no articles to judge.
    """
    if not article_titles:
        return 0.0
    q = query.lower()
    q_tokens = _tokens(query)
    phrase_hits = sum(1 for t in article_titles if q in t.lower())
    token_hits = sum(
        1 for t in article_titles if q_tokens and (q_tokens & _tokens(t))
    )
    return round(
        0.7 * phrase_hits / len(article_titles)
        + 0.3 * token_hits / len(article_titles),
        3,
    )


# A query below this confidence is treated as ambiguous → unavailable.
MIN_RELEVANCE = 0.30


def syndication_ratio(domains: list[str]) -> float:
    """unique domains / articles — 1.0 = all distinct outlets, low values
    indicate heavy wire-service syndication (a reliability note, not a
    correction; we do not attempt real deduplication)."""
    if not domains:
        return 0.0
    return round(len(set(domains)) / len(domains), 2)
