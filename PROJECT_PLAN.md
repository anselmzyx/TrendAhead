# TrendAhead — Project Plan

## Current phase

**Phase 6 — Real data connected to the website** (complete: awaiting visual verification)

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

Phase 6 done pending visual check: generate_site_data.py produces
data/trending.json (top 12) + data/topics/<slug>.json (top 24) with
validation; slugs are unique/ASCII-safe with collision suffixes; homepage,
topic pages, methodology and about now use ONLY real generated data (mock
module deleted). Truthful labelling: "Wikipedia attention · Experimental"
+ "Data through <date>"; fading topics say "falling from its peak".
Topic pages show component meters + deterministic "why" bullets from the
pipeline. Site never calls Wikimedia at page load. 68 Python tests, lint,
tsc, production build (31 routes) all pass; 3 topics' displayed values
verified identical to pipeline JSON.

## Next checkpoint

**Phase 7 — Improve signal quality** after the user reviews real pages.

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
