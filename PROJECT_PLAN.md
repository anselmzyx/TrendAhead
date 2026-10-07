# TrendAhead — Project Plan

## Current phase

**Phase 8 — GDELT proof of concept** (complete: awaiting review)

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
- **Phase 5.5 — Discovery alignment** (2026-10-07) two-path discovery
  (new entrants + improvers), infrastructure filter, healthier mix.
- **Phase 6 — Real data on the website** (2026-10-08) generated JSON,
  truthful Wikipedia-only labelling, 31 routes.
- **Phase 7 — Score V1.1** (2026-10-08) momentum damp, refined
  persistence, shape-based statuses.

## Current checkpoint

Phase 8 done pending review: isolated GDELT DOC 2.0 client
(pipeline/gdelt.py) + PoC (pipeline/poc_gdelt.py), 11 new fixture-based
tests. Verified: timelinevolraw returns raw daily article counts (UTC);
no API key; ~1 req/5s enforced via 429 with minutes-long penalty after a
burst; data free for commercial use with citation. Key findings: raw
timelines lag ~3-4 days (can't confirm fresh breakouts), final bucket can
be partially backfilled (dropped via norm check), and naive Wikipedia
titles can match zero news ("2026 Quebec general election" vs "Quebec
election"). Production untouched — Score and site remain Wikimedia-only.

## Next checkpoint

**Phase 9 — Cross-source confirmation**: design the Wikipedia+GDELT
combination around the discovered constraints (multi-day confirmation
only, title→query mapping, lag-aware alignment).

## Outstanding phases (summary)

5. TrendAhead scoring engine + tests → `data/trending.json`
6. Connect real data to the website
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
