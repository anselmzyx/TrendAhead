# TrendAhead — Error Log

Meaningful problems we encountered, their cause, and the fix.
(Trivial warnings are not logged.)

## 2026-10-07 — Charts and accent colours invisible in dark mode

**Error:** In dark mode, the topic-page chart line rendered near-black on the
black background, card sparklines were invisible, and the UI looked
monochrome (no blue score/meter/badge colours).

**Cause:** The dev server had been running since Phase 1 and kept serving a
stale compiled stylesheet that predated the Phase 2 rewrite of
`globals.css`. Every Phase 2 CSS variable (`--accent`, `--surface`, …) was
therefore undefined in the browser: an undefined `var()` in an SVG
`fill`/`stroke` collapses to the default (black fill), and Tailwind classes
like `text-accent` resolved to nothing. The source code was correct — the
production build contained the right CSS.

**Fix:** Restarted the dev server; verified the served stylesheet now
contains both light- and dark-mode variable sets and the accent utilities.
Lesson: after large stylesheet rewrites, restart `npm run dev` and re-check
rather than trusting hot reload.

## 2026-10-08 — iCloud Desktop sync creates " 2" duplicate files

**Error:** Files named like `routes.d 2.ts` and `karl-deisseroth 2.json`
appeared throughout the project (70+ found), breaking `tsc` once and
polluting a Git commit with junk topic files.

**Cause:** The project lives in `~/Desktop/TrendAhead`, and macOS
Desktop folders are synced by iCloud Drive. When iCloud hits a sync
conflict (frequent while builds rewrite many files), it keeps both
versions, naming the duplicate "<name> 2.<ext>".

**Fix:** Deleted all duplicates (`find . -name "* 2.*" -delete`), removed
the committed ones from Git, verified the build. **Ongoing risk:** this
will likely recur while the project stays inside an iCloud-synced folder.
Options if it keeps happening: move the project out of Desktop (e.g.
`~/Projects/TrendAhead`), or disable "Desktop & Documents" iCloud sync.
GitHub is the real backup either way.
**Resolved 2026-10-08:** project moved to `~/Developer/TrendAhead`
(outside iCloud sync); Git history, remote and local server verified
working from the new location.

## 2026-10-09 — Scheduled refresh failed on a transient Wikimedia 404

**Error:** The daily GitHub Actions run failed: Wikimedia returned HTTP
404 for the top-pages list of a valid older date (2026-10-03). Re-running
the identical workflow minutes later succeeded.

**Cause:** The Wikimedia client treated every 404 as permanent ("no data
for that page/day") and raised immediately without retrying. That
assumption is wrong: Wikimedia's API can transiently 404 valid dates.

**Fix:** All failure modes now retry with conservative tiered backoff
(429: 30/60/90s · other HTTP incl. 404/5xx: 10/20/30s · network/JSON:
2/4/8s; 4 attempts max — never forever). Genuinely missing data still
fails after retries, so nothing is silently hidden, and the existing
guarantee holds: a failed pipeline commits and deploys nothing. Covered
by 10 new mocked retry tests (no live API calls).
