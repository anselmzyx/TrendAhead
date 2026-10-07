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
