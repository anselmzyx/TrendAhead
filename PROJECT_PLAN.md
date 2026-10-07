# TrendAhead — Project Plan

## Current phase

**Phase 1 — Project Foundation** (in progress: awaiting browser verification)

## Completed phases

- **Phase 0 — Environment Check** (2026-10-07)
  macOS, Git 2.39.5, Node v20.12.2, npm 10.5.0, Python 3.12.4 all present.

## Current checkpoint

Phase 1: Next.js 16.4.0 app created with TypeScript + Tailwind, Git
initialised, docs files created, basic TrendAhead homepage in place.
Waiting for user to confirm the page renders at http://localhost:3000.

## Next checkpoint

**Phase 2 — Visual MVP with mock data**: navigation, hero, trend cards,
TrendAhead Score visual treatment, basic topic page, methodology page,
small chart. Clearly labelled mock data. Lint + type check + production build.

## Outstanding phases (summary)

3. Wikimedia API proof of concept (one page, real pageview data)
4. Automated candidate topic discovery
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
