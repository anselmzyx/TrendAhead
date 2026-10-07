# TrendAhead — Project Plan

## Current phase

**Phase 9 — Cross-source confirmation** (complete: GDELT kept offline)

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
- **Phase 8 — GDELT PoC** (2026-10-08) news timelines verified; lag,
  rate-limit and query-ambiguity constraints documented.

## Current checkpoint

Phase 9 done: lag-aware cross-source layer built and tested (17 new
fixture tests; 106 total). Query mapping + relevance gate + aligned
windows + bounded confirmation value with confirmed/not_confirmed/
unavailable states. Live evaluation on 8 topics: 1 usable result
(Michael Douglas not_confirmed, news +48% vs aligned wiki +80%), rest
unavailable (relevance gate or GDELT 429 rate limiting; circuit breaker
added). DECISION: Approach A semantics kept but GDELT NOT integrated into
production — stays experimental until coverage/reliability improve.
Baseline V1.1 ranking frozen in pipeline/output/baseline_phase9.json and
confirmed unchanged.

## Next checkpoint

**Phase 10 — Production hardening**: remove debug paths, verify error/
loading/empty states, mobile/desktop pass, tests, lint, build,
accessibility basics, metadata, no secrets. (GDELT revisit deferred.)

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
