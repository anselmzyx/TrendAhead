# TrendAhead — Decisions Log

## 2026-10-07 — Next.js 16.4.0 + TypeScript + Tailwind CSS

Chose the current stable Next.js (16.4.0) scaffolded with create-next-app,
with TypeScript and Tailwind. Reason: one framework covers pages, routing,
server rendering and SEO; current stable version is patched and compatible
with the installed Node v20.12.2 (requires ≥20.9).

## 2026-10-07 — Keep the npm audit warnings in the lint toolchain

`npm audit` reports 5 "high" advisories, all in `braces`/`micromatch`, used
only by the ESLint config (a development-time code checker). This code never
runs on the website itself, and the only automated fix would downgrade to
eslint-config-next 14 (a breaking downgrade). Decision: accept the advisory;
revisit when eslint-config-next updates its dependencies.

## 2026-10-07 — JSON files instead of a database for the MVP

Trend data will be precomputed into files like `data/trending.json`. Reason:
free, inspectable, debuggable, deployable anywhere, and the MVP has no
user-generated data. A database will only be added if a feature requires it.

## 2026-10-07 — Recharts 3.10.1 for charts, hand-rolled SVG for sparklines

Recharts chosen for the topic-page chart: officially supports React 19,
actively maintained, small composable API — far lighter than D3/ECharts.
Card sparklines are ~30 lines of plain server-rendered SVG instead, so the
homepage ships no client-side chart code and stays fast.

## 2026-10-07 — Mock data lives in one module shaped like the future pipeline

All Phase 2 demo content sits in `src/lib/mock-trends.ts`, flagged
`IS_MOCK_DATA`, with deterministic generated series (no randomness, so
server and client always render identically). Its types mirror what the
real pipeline will emit into `data/trending.json`, making the Phase 6 swap
a data-source change rather than a rewrite. Mock status is visibly
labelled in the UI (homepage pill, topic-page source box, methodology).

## 2026-10-07 — Restrained accent hierarchy for dark mode

Dark mode now uses a brighter cyan-blue accent (#38bdf8) and a brighter
positive green (#34d399) because the earlier mid-tone values read too dim
on the near-black background; light mode keeps the validated #2a78d6 /
#006300 pair. Semantic colour rules: cyan-blue = TrendAhead data/score
(line, sparkline, score number, meter, Emerging badge), green = positive
movement only (+% change, Rising badge), amber = warnings/demo-data
notices, red reserved for future negative signals. Everything else stays
neutral so topic name → score → trend direction → chart remains the eye's
path. The chart's 30-day baseline is a dashed muted grey reference line,
distinct from the solid accent data line.

## 2026-10-07 — Wikimedia Analytics API (AQS) as data source 1

Per-article endpoint `wikimedia.org/api/rest_v1/metrics/pageviews/per-article/
{project}/{access}/{agent}/{article}/daily/{start}/{end}` and, for later
candidate discovery, the `pageviews/top/{project}/{access}/{y}/{m}/{d}`
endpoint. Verified against official docs (doc.wikimedia.org AQS reference +
access policy): no API key; pageview data is CC0 1.0 (public domain —
commercial use permitted, no attribution legally required); a descriptive
User-Agent is mandatory. Under the 2026 Wikimedia rate rules, a UA without
contact info is "Unidentified" (10 req/min) while one with contact info
gets ~200 req/min. Requests must be sequential, not parallel. Our use
(low-volume scheduled fetches of public statistics) is compatible with the
published API usage guidelines. We query agent=user to count humans and
exclude bot/spider traffic.

## 2026-10-07 — Python (stdlib only) for the data pipeline

The pipeline lives in `pipeline/` as plain Python 3.12 using only the
standard library (urllib/json/datetime/unittest): zero dependencies to
install, calculation logic (`trend_math.py`) kept pure and unit-tested
separately from network code. TypeScript stays for the website only.

## 2026-10-07 — Temporary User-Agent contact placeholder

The PoC User-Agent identifies TrendAhead and states that contact info will
be added before deployment, rather than inventing a fake URL/email. Before
Phase 4 scales up requests (and certainly before any scheduled production
use), we must add real contact info — the public GitHub repo URL and/or an
email the owner approves — to qualify as an identified client.

## 2026-10-07 — Public GitHub repo created early for the User-Agent contact URL

github.com/anselmzyx/TrendAhead created ahead of the full GitHub phase,
solely to provide a legitimate permanent contact URL for the Wikimedia
User-Agent (owner chose the repo URL over a personal email) and an early
remote backup. User-Agent is now `TrendAhead/0.1
(https://github.com/anselmzyx/TrendAhead)`. gh CLI was installed from the
official GitHub release binary because Homebrew is blocked by outdated
Apple Command Line Tools on this machine.
