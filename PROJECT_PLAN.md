# TrendAhead — Project Plan

## Current phase

**Phase 16 — Public MVP review** (complete — MVP finished)

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
- **Phase 12 — Public deployment** (2026-10-08) live on Netlify Free at
  trendahead.netlify.app with GitHub auto-deploys (Phase 11 done early).
- **Phase 13 — Automated refresh** (2026-10-08) daily GitHub Action,
  budget-aware ~48h Netlify deploy cadence, bot-authored data commits.
- **Phase 14 — SEO foundation** (2026-10-08) canonicals, OG, robots,
  dataset-driven sitemap, JSON-LD; soft-404 noindex mitigation.
- **Phase 15 — Analytics** (2026-10-08) Cloudflare Web Analytics,
  cookie-free, Netlify-builds-only beacon; privacy note on /about.

## Current checkpoint

Phase 16 complete — ALL 16 planned MVP phases done. Verdict: READY TO
SHARE at validation scale ($0/month, automated refresh with retry/
failure safety verified — though the 2026-10-09 scheduled run had to be
manually dispatched, so schedule reliability stays under watch; live at
trendahead.netlify.app). Search Console: verified, sitemap submitted,
awaiting Google's fetch — just recheck later. Full assessment +
prioritized backlog in MVP_REVIEW.md. Next: product milestone "Validate
with first ~20 external users" — not a build phase.

## Outstanding phases (summary)

None — the planned MVP roadmap (Phases 0–16) is complete. Future work is
milestone-driven; see MVP_REVIEW.md for the prioritized backlog.

## Deliberately NOT building yet

User accounts, Radars, alerts, payments, categories, daily pages, exports,
mobile app. The product must earn complexity.
