# TrendAhead — Phase 16 MVP Review (2026-10-09)

## Baseline (frozen)

- Commit `a0d7a62` (bot refresh, data through **2026-10-08**) — production = HEAD.
- Today's refresh was NOT unattended: the scheduled GitHub Actions run did
  not start, so the owner manually triggered the workflow with
  deploy_now=true. The first attempt exhausted the Wikimedia transient-404
  retries and failed safely (nothing committed, site untouched); the rerun
  succeeded end to end. Good evidence that failure safety and
  retry/recovery work as designed — but scheduled-run reliability itself
  still needs monitoring.
- 12 homepage topics, 24 topic pages, 116 Python tests. Verdict basis below.

## Verdict: READY TO SHARE (at validation scale)

No deployment blockers, no trust failures, honest copy, live automation.
"Share" means deliberate small-scale validation, not a launch blast.

## Current trend quality (all 12 homepage topics, 2026-10-08 data)

| # | Topic | Shape judgment |
|---|-------|----------------|
| 1 | Carrie (miniseries) 72 Building | **Strong**: improver path caught a 6-day pre-release climb (7k→170k) |
| 2 | Anne Carson 63 Breaking out | Reactive one-day event burst (349→279k, conc 0.98); honestly labelled |
| 3 | Nidal Hasan 63 Building | Reactive news holding high 3 days; high volume carries it |
| 4 | World Space Week 61 Breaking out | **Weakest class**: annual calendar event — predictable, not "early" |
| 5 | Other Mommy 54 Building | **Strong**: textbook sustained climber (19k→74k, conc 0.33) |
| 6 | Tanushree Dutta 53 Breaking out | Reactive news burst |
| 7 | 2009 Fort Hood shooting 53 Elevated | Reactive cluster with #3 |
| 8 | Shooting of Abby Zwerner 53 Breaking out | Reactive news burst |
| 9 | Cleo (mathematician) 50 Elevated | **Surprising**: organic internet-curiosity topic still elevated day 3 |
| 10 | The Social Reckoning 50 Building | **Strong**: film buzz building pre-release — exactly the product promise |
| 11 | Michael Dell 45 Breaking out | Reactive |
| 12 | Below (miniseries) 45 Breaking out | Entertainment-release breakout |

Mix: ~4 genuine early/sustained signals, ~6 honest reactive breakouts,
~2 calendar/institutional artefacts. The status system successfully
separates them at a glance — the core Phase 7 design works in production.

## Hypothesis: PROMISING BUT UNPROVEN

Supported: the improver path demonstrably surfaces climbing topics before
their peak (Carrie, Other Mommy, The Social Reckoning), baselines
correctly suppress permanently-famous pages, and labels are honest.
Unproven: no evidence yet that real users find it valuable or return;
single English-Wikipedia source; ~1 week of production history.

## Differentiation (one sentence)

TrendAhead ranks topics by how unusually fast attention is growing
relative to each topic's own baseline — with a transparent score that
separates sustained climbs from one-day spikes — rather than by raw
popularity. (vs. Google Trends: cross-topic discovery without knowing
what to search; vs. social trending: transparent, shape-aware, calmer.)

## Primary user

**Content creators / newsletter writers** — job: find timely topic ideas
before saturation; current product already usable for a daily skim;
biggest missing piece for them: knowing *what a topic is* at a glance.
Secondary: journalists (story radar), data-curious professionals.

## Biggest product gap (ONE)

**Topic pages don't say what the topic IS.** A visitor must leave to
Wikipedia to learn that "Other Mommy" is a horror novel adaptation. A
one-line description is available deterministically from Wikipedia's own
free REST summary endpoint (same source, no LLM) — highest-value P1.

## Backlog

### P0 — fix before actively sharing
None. (Soft-404 is mitigated with noindex; no trust/correctness blockers.)

### P1 — highest-value next (max 5)
1. One-line topic descriptions via Wikipedia REST summary API (pipeline-side, deterministic).
2. Status legend/tooltips so Building vs Breaking out is understood without visiting Methodology.
3. "New today / rank change vs yesterday" indicator (retain prior day's trending.json — tiny, adds daily-return value).
4. Seasonal-recurrence awareness: compare vs same period last year (pageviews API supports it) to flag annual-event artefacts like World Space Week.
5. Investigate zero-cost daily public freshness (deploy-credit math or free static hosting alternatives) — site currently lags data by up to 2 days.

### P2 — useful later (max 8)
Daily archive page (/daily/<date>) · simple category tags · search over
current topics · multi-day top-list sampling to smooth the rank-1000
discovery boundary · GDELT ngrams revisit for news corroboration ·
non-English Wikipedia editions · branded OG social image · topic
comparison view.

### Do not build yet
Accounts · payments/tiers · watchlists/alerts · API access · personal
recommendations · LLM-generated summaries · mobile app · full
multi-source scoring · historical database/archive.

## Data-source decision

**Improve the existing Wikipedia signal first.** Phase 8/9 showed news
volume (GDELT) is too slow and too ambiguous to validate fresh signals;
another source adds complexity without fixing the real gaps (context,
freshness, recurrence). When a second source is justified, the needed
TYPE is a fast-moving independent conversation/search signal — chosen
after user validation, not before.

## Monetisation: all too early

Ads/affiliate/paid alerts/premium/subscription/API — every one "too
early". Evidence that would justify revisiting: organic return visitors,
users explicitly asking for alerts/watchlists, search traffic growth.

## Validation plan (cheap, ethical)

1. Show 5–10 people in content/marketing the homepage; ask "which 3 would you click and why" — encouraging: they pick topics they didn't already know.
2. One community post (e.g. Show HN / relevant subreddit) presenting it as an experimental open data project — encouraging: discussion engages with actual trends; CF analytics shows return visits.
3. LinkedIn post as a data project — encouraging: profile-relevant interest, portfolio feedback.
4. 5-day self-test: note each morning's top 5; record which become obviously mainstream 2–3 days later (rough precision estimate).
5. Watch Cloudflare analytics directionally: homepage→topic click-through, pages/visit, any return visits, referrers. No thresholds invented yet.

## Data Analyst portfolio value — strongest talking points

1. Metric design under constraints: V1.1's log-damping, volume gates, momentum damp — each decision driven by observed failure cases, with synthetic benchmarks as regression tests.
2. Time-series shape classification (Building/Breaking out/Elevated/Peaked) from first principles, validated on real data.
3. Evidence-based rejection: built a full GDELT cross-source layer, measured it, and kept it OUT of production — negative results honestly handled.
4. End-to-end ownership: official APIs → cleaning/validation → scoring → automated daily CI/CD with budget-aware deploys → live analytics.
5. Communication: every number on the site is explainable (component meters, methodology page, deterministic why-bullets).

## Search Console status (2026-10-09)

Ownership is verified and sitemap.xml has been submitted. The homepage
Live Test reports "URL is available to Google"; the sitemap currently
shows "Couldn't fetch" while Google processes/retries it, and today's
manual indexing-request quota is exhausted. Next action: simply recheck
Search Console in a few days — do NOT re-verify ownership.

## Technical debt register

- Scheduled GitHub Actions runs may not start reliably (observed
  2026-10-09; manual dispatch needed): **monitor** — if it recurs,
  consider a second cron time as redundancy.
- Soft-404 returns HTTP 200 (upstream Next.js bug #98518): **monitor**.
- Netlify 300-credit ceiling caps deploy cadence: **monitor**.
- GitHub scheduled workflows disable after ~60 days repo inactivity: **monitor**.
- Wikimedia API/top-1000 dependency + boundary flapping: **monitor**.
- iCloud duplicate-file risk: resolved by the move; **ignore**.

## Cost

**$0/month recurring.** (Netlify Free hard cap · GitHub Actions free on
public repo · Cloudflare Web Analytics free · Wikimedia free/CC0 · no
domain.) Future cost triggers: traffic beyond free credits, custom
domain (~$10–15/yr), any paid data source.

## Security/privacy spot-check

No accounts, no collected personal data, no credentials in the browser
or repo (beacon + GSC tokens are public by design), public GitHub repo
contains only code/docs/generated public data. Unchanged since Phase 10.

## Next milestone

**Milestone: Validate with the first ~20 external users.**
Complete when: ≥20 real people have used the site, ≥5 gave qualitative
feedback on trend usefulness, CF analytics shows whether homepage→topic
clicks and any return visits happen, and the P1 list is re-ranked against
that evidence.
