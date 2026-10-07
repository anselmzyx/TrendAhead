# TrendAhead — Project Plan

## Current phase

**Phase 3 — Wikimedia API proof of concept** (complete: awaiting confirmation)

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

## Current checkpoint

Phase 3 done pending confirmation: official Wikimedia AQS pageviews API
researched (no key, CC0 data, User-Agent policy noted in DECISIONS.md).
`pipeline/` created (Python stdlib only): poc_wikipedia.py fetched 40 real
days for "Artificial intelligence" with retries/validation; trend_math.py
computes recent-3-day vs prior-30-day baseline (non-overlapping) with
sanity checks; 14 unit tests pass. Real result: −10.6% vs baseline.

## Next checkpoint

**Phase 4 — Candidate discovery**: use the pageviews/top endpoint to
automatically discover candidate pages, filter obvious noise (Main Page,
Special:, etc.), fetch histories sequentially, rank by simple statistics,
and inspect the top ~10–20 in the terminal. Add real User-Agent contact
info first.

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
