# TrendAhead — Project Plan

## Current phase

**Phase 2 — Visual MVP with mock data** (built: awaiting visual verification)

## Completed phases

- **Phase 0 — Environment Check** (2026-10-07)
  macOS, Git 2.39.5, Node v20.12.2, npm 10.5.0, Python 3.12.4 all present.
- **Phase 1 — Project Foundation** (2026-10-07)
  Next.js 16.4.0 + TypeScript + Tailwind, Git initialised, docs files,
  basic homepage confirmed working in browser.

## Current checkpoint

Phase 2 complete pending user review: header/footer navigation, hero,
10 mock trend cards (reusable TrendCard), Score meter component, SVG
sparklines, Recharts topic chart, /topic/[slug] with 404 handling,
/methodology, /about. Mock data clearly labelled on homepage, topic pages
and methodology. Lint ✓, tsc ✓, production build ✓ (17 static pages).

## Next checkpoint

**Phase 3 — Wikimedia API proof of concept**: research official pageview
endpoints, rate limits and licensing; fetch real data for one page in a
standalone script; compute recent average vs baseline and show the results.

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
