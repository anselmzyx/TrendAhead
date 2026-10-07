# TrendAhead — Project Plan

## Current phase

**Phase 4 — Candidate discovery** (complete: awaiting review of results)

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

Phase 4 done pending review: discover_candidates.py samples 6 days of
top-1000 lists, dedupes (6,000 raw → 2,288 unique), filters namespace/nav
noise (17 removed), selects 30 "new entrant" pages, fetches 40-day
histories (30/30 ok), and prints a provisional ranking (volume floor
5,000/day; ratio with baseline floored at 100). First real run dominated
by news/death spikes, NFL players, Nobel-season scientists, plus genuinely
curious entries (Fallstreak hole, Cleo (mathematician)). 28 unit tests
pass. Output saved to pipeline/output/ (gitignored).

## Next checkpoint

**Phase 5 — TrendAhead scoring engine**: design + document the real 0–100
score (growth, baseline deviation, volume, persistence), with tests for
normal/rising/falling/low-volume/missing-day/zero-baseline/outlier cases;
generate data/trending.json. Signal-quality lessons from Phase 4: damp
one-day spikes, consider multi-day persistence, watch Wikimedia-internal
artefacts (e.g. Wikimedia Foundation banner traffic).

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
