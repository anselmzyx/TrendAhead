# TrendAhead — Project Plan

## Current phase

**Phase 5.5 — Discovery alignment & source hygiene** (complete: awaiting review)

## Completed phases

- **Phase 0 — Environment Check** (2026-10-07)
  macOS, Git 2.39.5, Node v20.12.2, npm 10.5.0, Python 3.12.4 all present.
- **Phase 1 — Project Foundation** (2026-10-07)
  Next.js 16.4.0 + TypeScript + Tailwind, Git initialised, docs files,
  basic homepage confirmed working in browser.
- **Phase 2 — Visual MVP with mock data** (2026-10-07)
  Nav, hero, 10 labelled mock trend cards, Score meter, sparklines,
  Recharts topic chart, /topic/[slug] + 404, /methodology, /about.
  Dark-mode colour fix + restrained accent hierarchy confirmed in browser.
- **Phase 3 — Wikimedia API PoC** (2026-10-07) real pageviews fetched,
  recent-vs-baseline signal verified; public repo + compliant User-Agent.
- **Phase 4 — Candidate discovery** (2026-10-07) automatic new-entrant
  discovery from top-1000 lists, noise filter, provisional ranking.
- **Phase 5 — Scoring engine V1** (2026-10-07) 0-100 shape-based score
  (pipeline/SCORING.md), benchmarked + tested, pushed to GitHub.

## Current checkpoint

Phase 5.5 done pending review: discovery now has two paths — new entrants
(cap 25) + improvers (>= 2 days in each window half, late avg >= 1.4x
early avg, cap 15) — combined/deduped with discovery reasons tracked.
Tiny exact-match infrastructure filter (Wikimedia_Foundation, MediaWiki,
Wiki) documented in DECISIONS.md. Combined run (2026-10-06): 25 + 15,
0 overlap, 0 failures, only 7 new API fetches thanks to history cache.
Improver path surfaced sustained climbers invisible to Phase 4 (Quebec
election #1, Neha Bora #5, Michael Douglas #8, UEFA Nations League #10,
John Steinbeck #13); Wikimedia Foundation artefact gone. 53 tests pass.

## Next checkpoint

**Phase 6 — Connect real data to the website**: pipeline writes
data/trending.json + per-topic files; replace homepage mock data; wire
topic routes, charts, timestamps; full build and manual inspection.

## Outstanding phases (summary)

5. TrendAhead scoring engine + tests → `data/trending.json`
6. Connect real data to the website
7. Improve signal quality (noise filtering)
8. GDELT proof of concept (news attention)
9. Cross-source confirmation
10. Production hardening
11. GitHub repository
12. Deployment (free tier, likely Vercel)
13. Automated data refresh (GitHub Actions)
14. SEO foundation
15. Analytics (privacy-conscious, free)
16. Public MVP review / validation

## Deliberately NOT building yet

User accounts, Radars, alerts, payments, categories, daily pages, exports,
mobile app. The product must earn complexity.
