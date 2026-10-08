/**
 * Central site identity for SEO/metadata.
 *
 * IMPORTANT: when a custom domain is purchased, change SITE_ORIGIN here —
 * it feeds metadataBase, every canonical URL, Open Graph URLs, robots.txt
 * and sitemap.xml. Nothing else needs touching.
 */

export const SITE_ORIGIN = "https://trendahead.netlify.app";
export const SITE_NAME = "TrendAhead";

const MAX_META_TOPIC_TITLE = 55;

/** Search-result title for a topic page (metadata only — never truncates
 * the visible on-page heading). */
export function topicMetaTitle(title: string, score: number): string {
  const t =
    title.length > MAX_META_TOPIC_TITLE
      ? title.slice(0, MAX_META_TOPIC_TITLE - 1).trimEnd() + "…"
      : title;
  return `${t} — TrendAhead Score ${score}`;
}

/** Deterministic, truthful topic meta description from generated data. */
export function topicMetaDescription(args: {
  title: string;
  score: number;
  status: string;
  growth_ratio: number;
  data_through: string;
}): string {
  const ratio =
    args.growth_ratio >= 10
      ? `${Math.round(args.growth_ratio)}×`
      : `${args.growth_ratio.toFixed(1)}×`;
  return (
    `Wikipedia attention for ${args.title} is currently "${args.status}" ` +
    `with a TrendAhead Score of ${args.score}/100 — recent attention is ` +
    `${ratio} its 30-day baseline. Data through ${args.data_through}.`
  );
}
