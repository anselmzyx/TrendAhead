# TrendAhead — Project Plan

## Current phase

**Phase 5 — TrendAhead scoring engine** (complete: awaiting review)

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

## Current checkpoint

Phase 5 done pending review: TrendAhead Score V1 implemented in
pipeline/scoring.py (acceleration 0.35 + anomaly 0.25 + persistence 0.40,
x sqrt(volume) gate x spike-quality damp; full formula in
pipeline/SCORING.md). 3 formulations compared on 38 real histories (30 new
entrants + 8 evaluation-only "improvers"); F1 chosen. 7 synthetic
benchmarks pass as tests; weight sensitivity: 9-10/10 top-10 overlap.
Real V1 ranking: sustained climber (2026 Quebec general election) is #1;
collapsed spikes (Fallstreak hole, Bryce Young) fell out of the top 20.

## Next checkpoint

**Phase 6 — Connect real data to the website**: generate data/trending.json
from the pipeline, replace homepage mock data, wire topic routes/charts/
timestamps, full build. (Then Phase 7 signal quality: Wikimedia-internal
artefacts like the Foundation banner page, 2-day plateau ambiguity,
discovery of slower climbers.)

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
