# TrendAhead Score V1.1 — Methodology

> Status: **experimental**. This documents the exact formula implemented in
> `pipeline/scoring.py`. Keep the two in sync. The score is a derived
> statistical indicator of attention-signal shape — it is not scientifically
> validated and does not predict the future.

## What the score rewards

A 0–100 integer where higher = stronger emerging-attention signal. The
design decision (2026-10-07): **sustained multi-day climbers rank above
short one-or-two-day attention explosions.** The score judges only the
*shape and quality of the daily pageview time series* — it never classifies
the real-world cause (no "celebrity/sports/death" rules).

## Input

At least 33 complete daily view counts, oldest first, gaps pre-filled with
0 (`discovery.fill_gaps`). The last 3 days are the **recent** window; the
30 days before them are the **baseline**. Non-negative integers only;
shorter or malformed series are rejected with an error, never guessed.

## Components (each 0–1)

### A. Acceleration — weight 0.35
`ratio = recent_avg / max(baseline_avg, 100)`, then
`log10(min(ratio, 50)) / log10(50)`, clamped to [0, 1].
*Why:* log damping stops +600,000% freak ratios from dominating (10× and
1000× should not differ absurdly); the 100-views baseline floor stops
near-zero baselines exploding; the 50× cap means "50× your normal is as
accelerated as we care about".

### B. Anomaly — weight 0.25
z-score of recent_avg vs the baseline: `(recent − baseline) / std`,
divided by a cap of 10, clamped to [0, 1]. The std has a floor of
`max(5% of baseline_avg, 1)` so flat histories can't produce infinite z.
*Why:* "unusual for this topic" is different from "grew a lot" — a noisy
topic must climb further before it counts as unusual.

### C. Persistence — weight 0.40 (the largest, deliberately)
Over the last 5 days:
`0.6 × (fraction of days ≥ 1.5× baseline) + 0.4 × (fraction of
day-over-day increases TO AN ELEVATED DAY)`.
*Why:* this is what separates `100,100,100,8000,120` from
`100,300,700,1500,3000`. Elevation share rewards staying up; rising share
rewards still climbing. (V1.1: a rise only counts when the destination day
is itself elevated — Phase 7 diagnostics showed sub-baseline noise like
61 → 71 → 92 views was earning "rising" credit.)

### D. Volume — multiplicative gate, exponent 0.5
`(log10(recent_avg) − log10(1,000)) / (log10(100,000) − log10(1,000))`,
clamped to [0, 1]; 0 at ≤1,000 views/day, 1 at ≥100,000. Applied as
`volume^0.5`.
*Why a gate:* if volume were additive, a 2→20-views page could still
collect points from other components. As a multiplier, no volume = no
score. *Why sqrt:* volume should qualify a topic, not dominate the score —
without it, mid-volume ideal-shaped climbers could never score above ~50.
*Why smooth:* a log ramp avoids an arbitrary cliff at some magic number.

### E. Spike quality — multiplicative damp, floor 0.25
Over the last 7 days:
`0.5 × concentration quality + 0.5 × collapse quality`, where
concentration quality = 1 − (share of the window's traffic on its biggest
single day, rescaled so a perfectly even week = 1 and an all-on-one-day
week = 0), and collapse quality = latest day ÷ window peak (capped at 1).
Applied as `0.25 + 0.75 × quality`, so the worst spike keeps 25% of its
score — **down-ranked, not deleted**, per the product decision.

### F. Momentum — multiplicative damp, floor 0.40 (new in V1.1)
`0.6 × (latest day ÷ 7-day peak) + 0.4 × (recency-weighted rising share of
the last 3 day-over-day changes, weights 1,2,3)`.
Applied as `0.4 + 0.6 × momentum`.
*Why:* Phase 7 diagnostics showed a post-peak cluster (latest day at only
23–31% of the recent peak and declining) still scoring 45–55. Momentum
asks "does this signal appear to have momentum remaining?" — a
still-climbing series keeps its full score, a high plateau keeps most of
it, and a clearly post-peak series keeps at most 40%. A fresh breakout
(huge latest day, no collapse evidence yet) is *not* punished — it sits at
its peak, so momentum stays high. *Why a damp and not a core component:*
tested as an additive component it leaked points to flat topics ("latest ≈
peak" is trivially true for a flat line); as a damp, flat topics stay at
zero and only elevated signals are modulated.

## Final formula

```
core  = 0.35·acceleration + 0.25·anomaly + 0.40·persistence
score = round( 100 · core · volume^0.5
               · (0.25 + 0.75·spike_quality)
               · (0.40 + 0.60·momentum) )
```

Clamped to [0, 100]. Integer output — more precision would be fake.

## Status labels (V1.1 — shape-based, independent of the score)

Each answers "what is the attention doing NOW?", computed only from the
last 7 days' shape (thresholds in `scoring.py`):

- **Peaked / fading** — the latest day is below 55% of the recent peak
- **Building** — still rising, at/near the peak, elevated for ≥ 3 days,
  traffic spread across days (peak day ≤ 50% of the week's traffic)
- **Breaking out** — at/near the peak, but the surge is only 1–2 days old
  or concentrated in a burst — too new to call sustained
- **Elevated** — holding well above baseline without a clear rising
  direction (a plateau)
- **Weak signal** — no meaningful elevation above baseline

## Why this formulation won (vs. 2 alternatives)

Tested on 38 real candidate histories (2026-10-06) + 7 synthetic shapes:
- **F2 (volume as additive component)**: stable already-popular pages crept
  up the ranking (volume was being paid twice); tiny pages could still
  collect points. Rejected.
- **F3 (geometric-mean core)**: rankings nearly identical to F1 on real
  data, but a single zero component nukes legitimate topics and the
  formula is harder to explain. Rejected for opacity without benefit.
- **F1 (chosen)**: additive core (explainable "points for each quality"),
  volume as a gate, spike quality as a damp. Weight perturbations of ±5pp
  kept 9–10 of the top 10 identical (the #1/#2 spots swap among
  near-tied leaders, which is expected at 1-point separations).

## Validated benchmark behaviour (tests in test_scoring.py)

| Shape | V1.1 score | Status | Expectation met |
|---|---|---|---|
| Stable popular (60k/day flat) | 0 | Weak signal | LOW ✓ |
| Tiny explosion (2 → 20) | 0 | Weak signal | VERY LOW ✓ |
| One-day spike, collapsed | 6 | Peaked / fading | heavily penalised, not deleted ✓ |
| Sustained 5-day climber | 60 | Building | HIGH ✓ |
| Still accelerating (6 rising days) | 57 | Building | HIGH ✓ |
| Moderate persistent growth | 47 | Building | meaningfully high ✓ |
| Two-day high plateau | 36 | Breaking out | moderate, below sustained ✓ |
| Slow steady build (+13%/day) | 31 | Building | respectable ✓ |
| Fresh breakout (no collapse yet) | 26 | Breaking out | meaningful, ≫ collapsed spike ✓ |
| Rise then collapse | 11 | Peaked / fading | strongly below sustained ✓ |
| Post-peak decline | 6 | Peaked / fading | substantially penalised ✓ |
| Huge flat (1M/day) | 0 | Weak signal | LOW ✓ |

## Known limitations (V1, honest)

1. **A 2-day plateau at peak looks like an early climber.** A death/news
   spike that holds for two days (e.g. Robert Kelker-Kelly) is
   shape-indistinguishable from day 2 of a genuine multi-week trend.
   More days of data resolve it; the score alone cannot.
2. **Wikimedia-internal artefacts score well** (e.g. a fundraising banner
   driving "Wikimedia Foundation" views in a multi-day climb shape).
   Resolved in Phase 5.5 by the tiny exact-match infrastructure filter —
   not a shape problem.
3. **V1.1 resolved the worst of this** (2026-10-08): the momentum damp cut
   the post-peak cluster by ~40% of its score, and the shape-based labels
   (Building / Breaking out / Elevated / Peaked / fading) now communicate
   signal maturity directly. Fresh 1–2-day breakouts still rank near the
   top while at their peak — by design, clearly labelled "Breaking out".
4. Candidate discovery (Phase 4) still over-samples sudden entrants and
   misses slower climbers — the evaluation-only "improver" sample proved
   such topics exist (the #1 topic came from it). Discovery improvement
   is deferred, deliberately.
5. Constants (floors, caps, weights) are judgement calls validated against
   one week of data; they will be revisited with longer-term evidence.
