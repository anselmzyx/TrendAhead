/**
 * ⚠️ MOCK DATA — Phase 2 only.
 *
 * Every topic, score and pageview number in this file is invented for UI
 * development. Nothing here comes from a real data source. In Phase 6 this
 * module is replaced by real generated files (data/trending.json), which is
 * why the shapes below mirror what the pipeline will output.
 */

export const IS_MOCK_DATA = true;
export const MOCK_DATA_SOURCE = "Demo data (mock) — real Wikipedia signals arrive in a later phase";

/** Fixed mock timestamp so server and client always render identical data. */
export const MOCK_LAST_UPDATED = "2026-10-07T06:00:00Z";

export type TrendStatus = "Emerging" | "Rising" | "Stable" | "Fading";

export interface DailyViews {
  date: string; // YYYY-MM-DD
  views: number;
}

export interface Trend {
  slug: string;
  name: string;
  /** TrendAhead Score, 0–100. Hand-assigned mock value. */
  score: number;
  status: TrendStatus;
  /** One-sentence human explanation of why this topic ranks. */
  why: string;
  /** 30 days of daily attention, oldest first. */
  series: DailyViews[];
}

/** Derived numbers every surface (card, topic page) shares. */
export interface TrendStats {
  recentAvg: number; // mean of the last 7 days
  baselineAvg: number; // mean of the first 23 days
  changePercent: number; // recent vs baseline, as +N%
  ratio: number; // recent / baseline, e.g. 2.8
  zScore: number; // how unusual the latest day is vs baseline
  latest: number; // most recent day's views
}

/** Deterministic pseudo-random in [0, 1) — keeps renders identical everywhere. */
function noise(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

/**
 * Builds a 30-day series: a noisy flat baseline that accelerates near the end.
 * `rampDays` controls how many final days rise; `peakMultiple` how high they go.
 */
function buildSeries(
  seed: number,
  baseline: number,
  rampDays: number,
  peakMultiple: number,
): DailyViews[] {
  const end = new Date(MOCK_LAST_UPDATED);
  const series: DailyViews[] = [];
  for (let i = 0; i < 30; i++) {
    const d = new Date(end);
    d.setUTCDate(d.getUTCDate() - (29 - i));
    const wobble = 1 + (noise(seed + i) - 0.5) * 0.18;
    const rampIndex = i - (30 - rampDays);
    const ramp =
      rampIndex >= 0
        ? 1 + (peakMultiple - 1) * Math.pow((rampIndex + 1) / rampDays, 1.6)
        : 1;
    series.push({
      date: d.toISOString().slice(0, 10),
      views: Math.round(baseline * wobble * ramp),
    });
  }
  return series;
}

export function trendStats(trend: Trend): TrendStats {
  const views = trend.series.map((d) => d.views);
  const recent = views.slice(-7);
  const base = views.slice(0, 23);
  const mean = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length;
  const recentAvg = mean(recent);
  const baselineAvg = mean(base);
  const variance = mean(base.map((v) => (v - baselineAvg) ** 2));
  const std = Math.sqrt(variance) || 1;
  const latest = views[views.length - 1];
  return {
    recentAvg: Math.round(recentAvg),
    baselineAvg: Math.round(baselineAvg),
    changePercent: Math.round(((recentAvg - baselineAvg) / baselineAvg) * 100),
    ratio: Math.round((recentAvg / baselineAvg) * 10) / 10,
    zScore: Math.round(((latest - baselineAvg) / std) * 10) / 10,
    latest,
  };
}

/** Ranked list, highest TrendAhead Score first. */
export const trends: Trend[] = [
  {
    slug: "solid-state-batteries",
    name: "Solid-state batteries",
    score: 87,
    status: "Emerging",
    why: "Attention jumped after reports of a manufacturing breakthrough, and has kept climbing for six consecutive days.",
    series: buildSeries(1, 3100, 8, 3.4),
  },
  {
    slug: "small-modular-reactors",
    name: "Small modular reactors",
    score: 84,
    status: "Rising",
    why: "Interest has risen steadily for two weeks as new reactor approvals made international news.",
    series: buildSeries(2, 5200, 14, 2.6),
  },
  {
    slug: "neuromorphic-computing",
    name: "Neuromorphic computing",
    score: 81,
    status: "Emerging",
    why: "A niche research topic suddenly drawing mainstream attention — daily interest is far above its usual baseline.",
    series: buildSeries(3, 1900, 7, 3.1),
  },
  {
    slug: "lab-grown-coffee",
    name: "Lab-grown coffee",
    score: 78,
    status: "Emerging",
    why: "Attention spiked after the first retail launch announcement and is holding well above baseline.",
    series: buildSeries(4, 1400, 6, 3.0),
  },
  {
    slug: "sleep-tourism",
    name: "Sleep tourism",
    score: 74,
    status: "Rising",
    why: "Search and reading interest has grown steadily for ten days, suggesting a building lifestyle trend.",
    series: buildSeries(5, 2600, 10, 2.2),
  },
  {
    slug: "digital-twin-cities",
    name: "Digital twin cities",
    score: 72,
    status: "Rising",
    why: "Consistent day-over-day growth as several governments announced urban simulation projects.",
    series: buildSeries(6, 2100, 12, 2.0),
  },
  {
    slug: "analog-horror",
    name: "Analog horror",
    score: 69,
    status: "Emerging",
    why: "A fast-growing internet culture genre — attention is accelerating ahead of the Halloween season.",
    series: buildSeries(7, 4400, 7, 1.9),
  },
  {
    slug: "retro-dumbphones",
    name: "Retro dumbphones",
    score: 67,
    status: "Rising",
    why: "The digital-minimalism wave keeps building: interest has doubled against its monthly baseline.",
    series: buildSeries(8, 1800, 11, 1.9),
  },
  {
    slug: "biodegradable-electronics",
    name: "Biodegradable electronics",
    score: 64,
    status: "Emerging",
    why: "Early-stage acceleration from a low base after a widely shared research paper.",
    series: buildSeries(9, 900, 6, 2.4),
  },
  {
    slug: "vertical-farming",
    name: "Vertical farming",
    score: 61,
    status: "Rising",
    why: "Moderate but persistent growth across the past two weeks, above seasonal norms.",
    series: buildSeries(10, 3300, 13, 1.6),
  },
];

export function getTrend(slug: string): Trend | undefined {
  return trends.find((t) => t.slug === slug);
}
