# TrendAhead — Project Plan

## Current phase

**Phase 7 — Signal quality (Score V1.1)** (complete: awaiting review)

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

## Current checkpoint

Phase 7 done pending review: diagnostics revealed (a) persistence was
crediting sub-baseline noise rises, (b) a post-peak cluster (latest day at
23-31% of peak, declining) still scored 45-55, (c) several "5-day
climbers" were really 1-2-day event jumps. Score V1.1 adopted: refined
persistence (rises only count to elevated days) + momentum damp
(0.4 + 0.6 x [0.6 latest/peak + 0.4 recency-weighted rising direction]).
Chosen over momentum-as-additive-component (leaked points to flat topics)
and persistence-blend (inflated spikes). New shape-based statuses:
Building / Breaking out / Elevated / Peaked, fading / Weak signal.
Post-peak cluster fell out of the top 12; climbers (Michael Douglas,
UEFA Nations League) labelled Building; breakouts clearly labelled.
En-dash slug fix (2026-27-uefa-nations-league). 78 Python tests, lint,
tsc, build (31 routes) pass; site regenerated and verified.

## Next checkpoint

**Phase 8 — GDELT proof of concept** (news-attention second source), after
user reviews the V1.1 rankings and statuses.

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
