# TrendAhead

**See what's gaining momentum before everyone else does.**

TrendAhead detects topics that are beginning to gain unusual attention online,
before they become obviously mainstream. It measures the *rate of change* of
public attention (not just absolute popularity) and ranks emerging topics with
a 0–100 **TrendAhead Score**.

> Status: experimental — live at **https://trendahead.netlify.app**
> (Netlify Free, deployed automatically from this repository's `main`
> branch; data is a static snapshot until scheduled refresh arrives).

## How the data flows (end to end)

```
Wikimedia Analytics API  (official, CC0, no key)
   │  daily top-1000 lists + per-article histories
   ▼
pipeline/  (Python, stdlib only)
   discovery (new entrants + improvers) → noise/infrastructure filters
   → 40-day histories (cached) → TrendAhead Score V1
   ▼
data/trending.json + data/topics/<slug>.json   (generated, committed)
   ▼
Next.js website  (reads the JSON — never calls Wikimedia at page load)
```

To regenerate the site's data (one command, ~1–3 min):

```bash
python3 pipeline/generate_site_data.py
```

It validates everything (score ranges, slug uniqueness, history integrity)
and refuses to write a broken dataset.

## Automatic data refresh

A GitHub Action refreshes TrendAhead data **every day** (05:37 UTC): it
re-runs discovery + scoring, runs all tests, and commits the new JSON to
`main` as `github-actions[bot]`. The public site redeploys roughly **every
second day** (even days of the year) — daily Netlify deploys would exceed
the free plan's 300 monthly credits (~15 credits per deploy), so odd-day
commits carry `[skip netlify]` and the next even-day deploy ships them.

- **Manual data refresh:** GitHub → Actions → "Refresh trend data" →
  Run workflow (leave `deploy_now` off — data updates on GitHub only).
- **Manual refresh + immediate deploy:** same, but tick `deploy_now`.
  ⚠ This spends ~15 Netlify production-deploy credits.
- **Failures:** visible under GitHub → Actions; a failed run commits and
  deploys nothing, so the live site always keeps its last good data.

## How to run it locally

1. Open Terminal and go to the project folder:
   ```bash
   cd ~/Developer/TrendAhead
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
3. Open http://localhost:3000 in your browser.
   ("localhost" means "this computer" — the site runs only on your machine.)
4. Stop the server with `Ctrl+C` in the terminal.

## Tech stack

- [Next.js](https://nextjs.org) 16 (React framework for the website)
- TypeScript (JavaScript with type checking)
- Tailwind CSS (styling)
- Python 3.12, standard library only (data pipeline in `pipeline/`)

## Data pipeline (`pipeline/`)

- `trend_math.py` — pure calculation helpers (averages, baseline split,
  percent change, missing-date detection)
- `test_trend_math.py` — unit tests: `cd pipeline && python3 -m unittest discover .`
- `wikimedia.py` — shared API client for the official Wikimedia Analytics
  API (CC0-licensed data, no API key; polite sequential requests)
- `poc_wikipedia.py` — Phase 3 proof of concept; fetches real daily
  pageviews for one article and prints a recent-vs-baseline signal:
  `python3 pipeline/poc_wikipedia.py`
- `discovery.py` — pure candidate-discovery logic (noise filters, pooling,
  new-entrant selection, provisional volume-floored ranking)
- `discover_candidates.py` — Phase 4 experiment; automatically discovers
  ~30 newly-trending candidate pages from 6 days of top-viewed lists and
  prints a PROVISIONAL ranking (not the TrendAhead Score):
  `python3 pipeline/discover_candidates.py` (writes debug JSON to
  `pipeline/output/`, which is gitignored)
- `scoring.py` — the TrendAhead Score V1 (0–100): pure, deterministic,
  documented in full in `pipeline/SCORING.md`
- `collect_histories.py` — fetches + caches 40-day histories for score
  evaluation (new entrants + an evaluation-only "improver" sample)
- `evaluate_scoring.py` — compares scoring formulations on real cached
  histories, checks weight sensitivity, prints the experimental V1 ranking
- `discover_and_score.py` — the combined pipeline: two-path discovery
  (new entrants + improvers), source-hygiene filtering, V1 scoring:
  `python3 pipeline/discover_and_score.py`
- `gdelt.py` + `poc_gdelt.py` — EXPERIMENTAL Phase 8 proof of concept for
  GDELT news-attention data; not connected to production (the site and
  TrendAhead Score use Wikipedia data only)
- `news_query.py`, `cross_source.py`, `poc_cross_source.py` — EXPERIMENTAL
  Phase 9 cross-source confirmation layer (query mapping, relevance gate,
  lag-aware aligned windows, bounded confirmation value). Deliberately NOT
  integrated into production — see DECISIONS.md (2026-10-08)

## Requirements & deployment notes

- **Node.js ≥ 20.9** (we develop on v20.12) — runs the website.
- **Python 3.12** — runs the OFFLINE data pipeline only. The deployed
  website never needs Python: it reads the pre-generated, committed JSON.
- **Environment variables: none.** The app needs no secrets or config to
  build or run.
- `npm run build` works fully offline from the committed `data/` files — a
  Wikimedia outage cannot break deployment of the existing snapshot.
- Data generation is crash-safe: new JSON is written to temporary files and
  swapped in only after validation, so the last good dataset survives any
  pipeline failure.

## Project documentation

- `PROJECT_PLAN.md` — roadmap and current phase
- `DECISIONS.md` — significant technical/product decisions and why
- `ERROR_LOG.md` — meaningful problems we hit and how we fixed them

More sections (architecture, data pipeline, scoring, deployment) will be added
as those parts are built.
