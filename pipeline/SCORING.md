# TrendAhead Score V1 — Methodology

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
day-over-day changes that are increases)`.
*Why:* this is what separates `100,100,100,8000,120` from
`100,300,700,1500,3000`. Elevation share rewards staying up; rising share
rewards still climbing.

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

## Final formula

```
core  = 0.35·acceleration + 0.25·anomaly + 0.40·persistence
score = round( 100 · core · volume^0.5 · (0.25 + 0.75·spike_quality) )
```

Clamped to [0, 100]. Integer output — more precision would be fake.

## Status labels (provisional, secondary to the score)

- **Fading / collapsing** — the last 7 days contain a spike ≥ 3× baseline
  AND the latest day is below 40% of that peak (momentum check, applied
  regardless of score)
- **Strong emerging signal** — score ≥ 60
- **Emerging signal** — score 35–59
- **Weak signal** — score < 35

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

| Shape | Score | Expectation met |
|---|---|---|
| Stable popular (60k/day flat) | 3 | LOW ✓ |
| Tiny explosion (2 → 20) | 0 | VERY LOW ✓ |
| One-day spike + collapse | 14 | LOW-MODERATE, not deleted ✓ |
| Sustained 5-day climber | 60 | HIGH ✓ |
| Rise then collapse | 24 | below sustained ✓ |
| Moderate persistent growth | 47 | meaningfully high ✓ |
| Huge flat (1M/day) | 3 | LOW ✓ |

## Known limitations (V1, honest)

1. **A 2-day plateau at peak looks like an early climber.** A death/news
   spike that holds for two days (e.g. Robert Kelker-Kelly) is
   shape-indistinguishable from day 2 of a genuine multi-week trend.
   More days of data resolve it; the score alone cannot.
2. **Wikimedia-internal artefacts score well** (e.g. a fundraising banner
   driving "Wikimedia Foundation" views in a multi-day climb shape).
   Needs source-aware filtering in Phase 7 — not a shape problem.
3. **The "Fading / collapsing" label can co-exist with a high score**
   (spiked hugely, still elevated, but off its peak). Arguably correct,
   but the UI copy will need care.
4. Candidate discovery (Phase 4) still over-samples sudden entrants and
   misses slower climbers — the evaluation-only "improver" sample proved
   such topics exist (the #1 topic came from it). Discovery improvement
   is deferred, deliberately.
5. Constants (floors, caps, weights) are judgement calls validated against
   one week of data; they will be revisited with longer-term evidence.
