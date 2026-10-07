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
