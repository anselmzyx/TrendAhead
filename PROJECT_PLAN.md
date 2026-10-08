# TrendAhead — Project Plan

## Current phase

**Phase 12 — Public deployment** (complete: LIVE on Netlify)

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
- **Phase 9 — Cross-source confirmation** (2026-10-08) full lag-aware
  layer built + tested; GDELT deliberately kept offline.
- **Phase 10 — Production hardening** (2026-10-08) audits, crash-safe
  writes, security headers, production-server verification.

## Current checkpoint

Phase 12 complete: TrendAhead is publicly deployed at
https://trendahead.netlify.app (Netlify Free, hard usage cap, no payment
info on file), continuous deployment from GitHub main. All routes, data
values, security headers and 404 behaviour verified against the live URL;
visitor pages make no Wikimedia/GDELT requests. Phase 11 (GitHub) was
completed early in Phase 3.

## Next checkpoint

**Phase 13 — Automated data refresh**: GitHub Actions to run the pipeline
daily, validate, commit new data/ JSON and let Netlify auto-deploy.
Data remains a static snapshot (Oct 6) until then.

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
