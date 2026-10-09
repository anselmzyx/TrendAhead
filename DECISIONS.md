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

## 2026-10-07 — Phase 4 candidate discovery design (provisional, NOT the Score)

Discovery samples the official top-1000 most-viewed lists for the last 6
complete days (6 requests), split into early 3 / late 3 days. Candidates =
pages appearing in a late-day list but NO early-day list ("new entrants"),
ordered by observed top-list views, capped at 30 histories per run (~36
total requests, sequential with 0.35s delay). Noise filter: internal
namespaces (Special:, Wikipedia:, File:, …) and navigation pages
(Main_Page), kept in one inspectable function (discovery.noise_reason).
Missing history days are filled as 0 views (page likely didn't exist) and
flagged. Provisional ranking: require recent 3-day avg >= 5,000 views/day,
rank by recent_avg / max(baseline_avg, 100) — the floor stops tiny-baseline
ratio explosions. This ranking exists only to choose what humans inspect;
the real TrendAhead Score is designed separately in Phase 5.

## 2026-10-07 — TrendAhead Score V1 formula (Phase 5)

score = 100 x (0.35 acceleration + 0.25 anomaly + 0.40 persistence)
x volume^0.5 x (0.25 + 0.75 spike_quality), integers 0-100. Persistence
carries the largest weight by design: the product decision is that
sustained multi-day climbers outrank one-day explosions. Volume is a
multiplicative log-ramp gate (sqrt-softened) so tiny pages score 0 while
mid-volume climbers aren't crushed; spike quality (traffic concentration +
collapse-from-peak) damps spikes to as little as 25% rather than deleting
them. No semantic rules (no celebrity/sports/death classification) — shape
only. Chosen over an additive-volume variant (let popular-but-flat pages
creep up) and a geometric-mean variant (same ranking, harder to explain).
Full documentation: pipeline/SCORING.md. Status labels are provisional and
momentum-aware; secondary to the score.

## 2026-10-07 — Two-path candidate discovery + infrastructure filter (Phase 5.5)

Discovery now combines (a) new entrants — in a late-day top list, absent
from all early days (Phase 4 path, cap 25) — and (b) improvers — present
on >= 2 days in BOTH halves of the 6-day window with late-half average
top-list views >= 1.4x the early-half average (cap 15). Separate caps keep
both paths represented; discovery reason is tracked as metadata only and
does not feed the Score. Rationale: Phase 5 proved the best sustained
climber (2026 Quebec general election) was invisible to the entrant-only
path. Source hygiene: a deliberately tiny exact-match blocklist
(Wikimedia_Foundation, MediaWiki, Wiki) for pages whose surges come from
Wikimedia's own site/banner infrastructure — explicitly NOT keyword or
topic censorship; no semantic rules (celebrity/sports/death/election all
stay eligible).

## 2026-10-08 — Website reads committed generated JSON (Phase 6)

The pipeline writes data/trending.json (12 homepage topics) and
data/topics/<slug>.json (24 pages); the Next.js site reads these at build
time and never calls Wikimedia per visit. Generated data is COMMITTED to
Git deliberately: it is the deployable artifact, inspectable in history.
Validation in generate_site_data.py refuses to write datasets with bad
scores, duplicate slugs, or malformed histories. Slugs: ASCII-transliterated
(Québécois → quebecois), hash fallback for non-Latin titles, -2/-3
suffixes on collisions. Frontend never recalculates scores — Python is the
single source of truth; it only formats (e.g. ratios >= 10 render as "N×
baseline" instead of absurd percentages, fading topics say "falling from
its peak"). Honest coverage labelling: "Wikipedia attention ·
Experimental" — we do not claim to measure the whole internet. Next 16
Cache Components required "use cache" on the fs-reading loaders (build
error otherwise; fixed, noted here instead of ERROR_LOG as it was a
15-minute framework behaviour, not a bug).

## 2026-10-08 — Score V1.1: momentum damp + refined persistence (Phase 7)

Phase 7 diagnostics on real shapes showed post-peak topics (latest day
23-31% of peak, declining) still scoring 45-55, and persistence crediting
sub-baseline noise rises (61→71→92 views). V1.1 keeps the V1 core and adds
a momentum damp: score x= 0.4 + 0.6 x momentum, where momentum = 0.6 x
(latest/7-day peak) + 0.4 x recency-weighted rising share of the last 3
changes. Persistence now only counts rises that land on an elevated day.
Momentum-as-additive-component was rejected (a flat line trivially sits at
its own "peak" and gained points); a persistence/momentum blend was
rejected (inflated fresh spikes). Fresh breakouts stay meaningful (26 vs 7
for an already-collapsed spike) — TrendAhead does not wait days to show a
breakout, it labels it. Statuses are now shape-based and score-independent:
Building / Breaking out / Elevated / Peaked, fading / Weak signal.
Known instability documented: candidates at the top-1000 list boundary can
flap between runs because Wikimedia finalises counts late (Parti Québécois
dropped out of the pool between two same-window runs).

## 2026-10-08 — GDELT DOC 2.0 proof of concept (Phase 8, experimental only)

GDELT chosen modes: timelinevolraw (TRUE raw matching-article counts per
day, plus "norm" = total articles GDELT monitored that day) and artlist
(headline samples for relevance checks). No API key. Searchable window:
rolling 3 months; timestamps UTC. Terms: free for unlimited use including
commercial, with required citation + link to gdeltproject.org (will be
added to the site when/if GDELT ships in production). Rate limits are NOT
in the docs but ARE enforced by the API: HTTP 429 says "limit requests to
one every 5 seconds", and empirically a tripped limiter stays tripped for
minutes — client paces at 6s and backs off 60s+/attempt on 429, with disk
caching so re-runs create zero traffic. CRITICAL findings for Phase 9:
(1) raw daily timelines LAG several days behind (requests on Oct 7 UTC
returned usable data only through ~Oct 2-3), so GDELT cannot confirm
fresh 1-2-day breakouts, only multi-day trends; (2) the final returned
bucket can be partially backfilled (norm a fraction of a normal day) and
must be dropped; (3) naive Wikipedia-title queries can fail completely —
"2026 Quebec general election" matched ~zero articles while "Quebec
election" matched highly relevant coverage; title→news-query mapping is
the main Phase 9 problem. GDELT remains proof-of-concept ONLY: the
TrendAhead Score and website are untouched and Wikimedia-only.

## 2026-10-08 — Cross-source confirmation built, GDELT kept OFFLINE (Phase 9)

Built the full lag-aware confirmation layer (news_query.py, cross_source.py):
deterministic query variants (exact title → parenthetical removed → leading
year removed → "general election"→"election"; max 3, generic rules only),
a conservative relevance gate (0.7 x phrase-in-title share + 0.3 x
distinctive-token share over >= 3 sampled articles; < 0.30 → unavailable),
syndication ratio (unique domains / articles) as a reliability note, and a
bounded confirmation value = log-capped news growth x volume ramp
(2→20 articles/day) x relevance, with three distinct states: confirmed /
not_confirmed / unavailable — a fresh Wikipedia breakout with lagged GDELT
is "unavailable", never a failed signal. Approach A (display-only) chosen
over a score bonus: in live evaluation only 1 of 8 topics produced a
usable confirmation (Michael Douglas: news +48%, value 0.017,
not_confirmed; aligned wiki +80% — both rising, Wikipedia more sharply),
so any bonus would reward "famous + lucky with the rate limiter", not
signal quality.

PRODUCTION DECISION: GDELT stays experimental/offline. Reasons: (a) its
raw timelines lag 3-4 days; (b) its rate limiter repeatedly blocked us for
minutes-long windows (6/8 topics unavailable in the live run) — a new
circuit breaker in gdelt.py stops live calls after 2 consecutive 429
failures so a stuck limiter can never hang or hammer; (c) measured
coverage is too sparse to justify a topic-page section that would read
"unavailable" for most topics. Revisit with a clean request budget,
and consider GDELT's ngrams dataset (which its own 429 message recommends
for high-traffic use). The website and Score remain 100% Wikimedia-only;
no GDELT imports exist in the production path (verified).

## 2026-10-08 — Production hardening decisions (Phase 10)

Crash-safe data writes: generate_site_data.py now writes trending.json and
all topic files to temporary paths and swaps them in with renames only
after validation — a mid-write failure can never destroy the last good
dataset. Corrupt history caches are ignored (refetch) instead of crashing.
Security headers added in next.config.ts: X-Content-Type-Options nosniff,
X-Frame-Options DENY, Referrer-Policy strict-origin-when-cross-origin; no
CSP (would need careful tuning against Next.js internals for little gain
on a static site). Known limitation accepted: invalid /topic/<slug> URLs
return HTTP 200 while rendering the styled not-found page with Next's
auto-injected noindex meta — Next 16 cacheComponents streams the shell
before notFound() runs and is incompatible with dynamicParams=false;
users and crawlers are handled correctly, only the raw status code is
imperfect (revisit in Phase 14/SEO). Deployment needs: Node >= 20.9, zero
env vars, no Python at runtime.

## 2026-10-08 — Deployed to Netlify Free (Phase 12)

Netlify chosen over Vercel because Vercel's Hobby plan forbids commercial
use while Netlify's Free plan allows it, with a HARD 300-credit/month cap
(sites pause when exceeded; auto-recharge impossible on Free; no card on
file). Verified against current docs: Next.js supported via the
auto-installed OpenNext adapter incl. App Router, Cache Components and
PPR — zero config, defaults accepted (build `npm run build`, publish
`.next`). Production URL: https://trendahead.netlify.app, continuous
deployment from GitHub main (verified working twice). Two deploy-time
fixes: (1) new Netlify projects default to team-only "site protection" —
turned off in the dashboard to make the site public; (2) unknown
/topic/<slug> URLs 500ed in the serverless fallback because Cache
Components forbids awaiting params outside <Suspense> — the page now
wraps its dynamic content in a Suspense boundary, and invalid slugs render
the styled 404 UI (status 200 + noindex, the Phase 10 known quirk,
unchanged). data/ JSON is also explicitly traced into serverless bundles
(outputFileTracingIncludes) as a correctness guarantee.

## 2026-10-08 — Automated daily refresh with budget-aware deploys (Phase 13)

GitHub Actions workflow (.github/workflows/refresh-trends.yml) runs daily
at 05:37 UTC on the default branch: generate -> test -> validate -> commit
only on real changes. Verified platform facts: Actions scheduled workflows
are free on public-repo standard runners, cron is UTC, runs use the
default branch, start times can drift past the requested minute, and
schedules are auto-disabled after ~60 days of repository inactivity;
Netlify supports "[skip netlify]"/"[skip ci]" anywhere in the head commit
message, and the next unmarked push deploys all accumulated commits.
Deploy cadence: scheduled runs deploy only on EVEN days of the year
(day-of-year parity), odd days commit with [skip netlify] — roughly 15
production deploys/month x ~15 credits = ~225 of the 300 free credits,
leaving headroom for traffic (prices rechecked 2026-10-08; recheck
periodically). Manual workflow_dispatch defaults to deploy_now=false so
experiments never spend deploy credits. Loop safety: no push trigger +
GITHUB_TOKEN pushes don't trigger workflows. Failure safety: any step
failure aborts before commit — broken data can never reach Git or the
site. Bot commits are authored by github-actions[bot]; human commits stay
anselmzyx. Actions cache deliberately NOT used: the history cache keys on
the end date, so daily runs could never hit it.

## 2026-10-08 — SEO foundation (Phase 14)

Canonical origin centralised in src/lib/site.ts (SITE_ORIGIN =
https://trendahead.netlify.app — change that ONE constant when a custom
domain arrives; it feeds metadataBase, canonicals, OG URLs, robots and
sitemap). Added: canonicals on all pages; Open Graph + twitter summary
card (no fake social images); robots.txt (allow all + sitemap);
sitemap.xml built from the CURRENT generated dataset only (27 URLs:
3 static + 24 topics, lastModified = data generation time; prose pages
omit it). Topic meta titles are absolute ("<topic> — TrendAhead Score N",
truncated at ~55 chars metadata-only) with deterministic truthful
descriptions. Structured data kept minimal and honest: WebSite (homepage)
+ BreadcrumbList (topic pages); deliberately no Organization (no legal
entity), no Dataset/Article/NewsArticle (semantics don't fit; topics are
not authored articles). Soft-404: invalid slugs still return HTTP 200
with the 404 UI + noindex — confirmed a known open Next.js bug
(vercel/next.js#98518) with no cacheComponents-compatible fix; mitigation
retained (noindex + sitemap lists only valid pages). Topic lifecycle
policy A: topics that fall out of the dataset genuinely disappear
(soft-404 + noindex, auto-removed from the sitemap on the next deploy) —
no historical archive in the MVP. Duplicate-URL audit: trailing slashes
308-redirect; uppercase/invalid slug variants are noindex'd; slugs are
unique by construction. Frontend metadata is verified via rendered-output
checks rather than a new JS test framework (adding one for a few string
assertions wasn't justified).

## 2026-10-08 — Cloudflare Web Analytics (Phase 15)

Chosen for the MVP: free with no traffic cap (non-proxied sites limited
to 10/account), works on Netlify via JS snippet with no DNS change,
cookie-free with no personal-data collection per official docs, and
provides exactly the MVP metrics we need (visits, pageviews, top paths,
referrers, countries, browser/OS, Core Web Vitals RUM). The beacon script
is included ONLY in builds made on Netlify (gated on the platform's own
NETLIFY env var), so dev and local production testing never pollute
stats; the beacon token is public by design and lives in the layout. The
site renders fully even if the analytics script fails — it is a deferred
module script with no render dependency. No cookie banner added: the
implementation is technically cookie-free per Cloudflare's docs; legal
consent obligations can vary by jurisdiction and are a separate matter —
we make no universal compliance claim. A concise Privacy section was
added to /about instead of a dedicated legal-style privacy page (no
accounts, no personal data — a dedicated page would be empty ceremony at
this stage). Dashboard: dash.cloudflare.com → Web Analytics
(trendahead.netlify.app). A temporarily created scoped API token (for a
dashboard-bug workaround that proved unnecessary) was deleted by the
owner without being used or shared.

## 2026-10-09 — Phase 16 MVP review verdict (see MVP_REVIEW.md)

READY TO SHARE at validation scale. Hypothesis "promising but unproven":
the improver path demonstrably surfaces pre-peak climbers (Carrie
miniseries, Other Mommy, The Social Reckoning) and statuses honestly
separate them from reactive news bursts, but no user evidence exists yet.
Primary early user: content creators/newsletter writers. Biggest gap:
topic pages don't say what a topic IS (fix: Wikipedia REST summary line,
P1). Next investment is improving the existing Wikipedia signal, NOT a
second data source. Monetisation: uniformly too early. Next milestone:
validate with first ~20 external users. Full backlog in MVP_REVIEW.md.
