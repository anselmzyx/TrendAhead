import type { MetadataRoute } from "next";
import { SITE_ORIGIN } from "@/lib/site";
import { getAllTopicSlugs, getTrending } from "@/lib/trends";

/**
 * Built from the CURRENT generated dataset only — topics that fall out of
 * the data on regeneration automatically leave the sitemap on the next
 * deploy, so it never lists pages that no longer exist.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const trending = await getTrending();
  const slugs = await getAllTopicSlugs();
  // Data-generation time is the meaningful "last modified" for data pages;
  // prose pages (methodology/about) omit it rather than faking freshness.
  const generated = trending?.generated_at_utc
    ? new Date(trending.generated_at_utc)
    : undefined;

  return [
    { url: `${SITE_ORIGIN}/`, lastModified: generated },
    { url: `${SITE_ORIGIN}/methodology` },
    { url: `${SITE_ORIGIN}/about` },
    ...slugs.map((slug) => ({
      url: `${SITE_ORIGIN}/topic/${slug}`,
      lastModified: generated,
    })),
  ];
}
