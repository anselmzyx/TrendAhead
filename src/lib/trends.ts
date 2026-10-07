/**
 * Server-side loader for the REAL generated trend data.
 *
 * The Python pipeline (pipeline/generate_site_data.py) is the single source
 * of truth for every number shown on the site — this module only reads and
 * types the generated JSON; it never recalculates scores.
 */

import { promises as fs } from "fs";
import path from "path";

export type TrendStatus =
  | "Building"
  | "Breaking out"
  | "Elevated"
  | "Peaked / fading"
  | "Weak signal";

export interface TrendCore {
  title: string;
  slug: string;
  score: number;
  status: TrendStatus;
  change_percent: number | null;
  growth_ratio: number;
  recent_avg: number;
  baseline_avg: number;
  explanation: string;
  discovery: string[];
}

export interface TrendingTopic extends TrendCore {
  rank: number;
  sparkline: number[];
}

export interface TrendingData {
  source: string;
  score_version: string;
  experimental: boolean;
  data_through: string;
  generated_at_utc: string;
  topics: TrendingTopic[];
}

export interface TopicComponents {
  acceleration: number;
  anomaly: number;
  persistence: number;
  momentum: number;
  volume: number;
  spike_quality: number;
}

export interface TopicData extends TrendCore {
  abs_change: number;
  latest: number;
  components: TopicComponents;
  why: string[];
  history: { date: string; views: number }[];
  wikipedia_title: string;
  source: string;
  score_version: string;
  data_through: string;
  generated_at_utc: string;
}

const DATA_DIR = path.join(process.cwd(), "data");
const SLUG_PATTERN = /^[a-z0-9-]+$/;

/** Homepage data; null when no dataset has been generated yet. */
export async function getTrending(): Promise<TrendingData | null> {
  "use cache";
  try {
    const raw = await fs.readFile(path.join(DATA_DIR, "trending.json"), "utf8");
    const data = JSON.parse(raw) as TrendingData;
    if (!Array.isArray(data.topics)) return null;
    return data;
  } catch {
    return null;
  }
}

/** One topic's data; null for unknown/invalid slugs (caller shows 404). */
export async function getTopic(slug: string): Promise<TopicData | null> {
  "use cache";
  if (!SLUG_PATTERN.test(slug)) return null;
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, "topics", `${slug}.json`),
      "utf8",
    );
    return JSON.parse(raw) as TopicData;
  } catch {
    return null;
  }
}

export async function getAllTopicSlugs(): Promise<string[]> {
  "use cache";
  try {
    const files = await fs.readdir(path.join(DATA_DIR, "topics"));
    return files
      .filter((f) => f.endsWith(".json"))
      .map((f) => f.replace(/\.json$/, ""));
  } catch {
    return [];
  }
}

/** "2026-10-06" → "Oct 6, 2026" (UTC, matching the pipeline's dating). */
export function formatDataDate(iso: string): string {
  return new Date(iso + "T00:00:00Z").toLocaleDateString("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}
