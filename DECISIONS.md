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
