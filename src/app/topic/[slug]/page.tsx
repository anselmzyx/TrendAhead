import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { notFound } from "next/navigation";
import Score from "@/components/Score";
import StatusBadge from "@/components/StatusBadge";
import ChangeIndicator from "@/components/ChangeIndicator";
import TrendChart from "@/components/TrendChart";
import {
  formatDataDate,
  getAllTopicSlugs,
  getTopic,
  type TopicData,
} from "@/lib/trends";
import { SITE_NAME, SITE_ORIGIN, topicMetaDescription, topicMetaTitle } from "@/lib/site";

export async function generateStaticParams() {
  const slugs = await getAllTopicSlugs();
  return slugs.map((slug) => ({ slug }));
}
export async function generateMetadata({
  params,
}: PageProps<"/topic/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const topic = await getTopic(slug);
  if (!topic) return { title: "Topic not found" };
  const title = topicMetaTitle(topic.title, topic.score);
  const description = topicMetaDescription(topic);
  const path = `/topic/${topic.slug}`;
  return {
    // absolute: the title already carries the brand; the "%s — TrendAhead"
    // template would duplicate it.
    title: { absolute: title },
    description,
    alternates: { canonical: path },
    openGraph: { title, description, url: path, type: "website" },
  };
}

const num = new Intl.NumberFormat("en");

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-2xl border border-hairline bg-surface p-4">
      <p className="text-xs font-medium text-ink-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
      {hint ? <p className="mt-1 text-xs text-ink-muted">{hint}</p> : null}
    </div>
  );
}

/** One normalized 0–1 component subscore as a labelled meter. */
function ComponentMeter({
  label,
  value,
  description,
}: {
  label: string;
  value: number;
  description: string;
}) {
  const pct = Math.round(value * 100);
  return (
    <div>
      <div className="flex items-baseline justify-between gap-2">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs tabular-nums text-ink-muted">{pct}/100</p>
      </div>
      <div
        role="meter"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pct}
        aria-label={`${label} ${pct} out of 100`}
        className="mt-1.5 h-1 rounded-full bg-accent-soft/40"
      >
        <div className="h-full rounded-full bg-accent" style={{ width: `${pct}%` }} />
      </div>
      <p className="mt-1.5 text-xs leading-relaxed text-ink-muted">{description}</p>
    </div>
  );
}

function componentMeters(topic: TopicData) {
  const c = topic.components;
  return [
    {
      label: "Acceleration",
      value: c.acceleration,
      description: "How far recent attention sits above this topic's own 30-day baseline.",
    },
    {
      label: "Persistence",
      value: c.persistence,
      description: "Whether interest has stayed elevated and kept rising across recent days.",
    },
    {
      label: "Momentum",
      value: c.momentum,
      description: "Whether the latest days are still at or pushing past the recent peak.",
    },
    {
      label: "Anomaly",
      value: c.anomaly,
      description: "How statistically unusual the recent level is for this topic.",
    },
    {
      label: "Signal quality",
      value: c.spike_quality,
      description: "Traffic spread across several days scores high; one-day bursts score low.",
    },
    {
      label: "Attention volume",
      value: c.volume,
      description: "Absolute size of recent attention (log scale, 1k–100k daily views).",
    },
  ];
}

// Cache Components requires `params` to be awaited inside a Suspense
// boundary: without it, an on-demand render for a slug that wasn't
// prerendered crashes with "uncached runtime data during prerendering"
// (surfaced as a 500 on Netlify) instead of reaching notFound().
export default function TopicPage(props: PageProps<"/topic/[slug]">) {
  return (
    <Suspense fallback={null}>
      <TopicContent params={props.params} />
    </Suspense>
  );
}

async function TopicContent({
  params,
}: {
  params: PageProps<"/topic/[slug]">["params"];
}) {
  const { slug } = await params;
  const topic = await getTopic(slug);
  if (!topic) notFound();

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: SITE_NAME, item: `${SITE_ORIGIN}/` },
      {
        "@type": "ListItem",
        position: 2,
        name: topic.title,
        item: `${SITE_ORIGIN}/topic/${topic.slug}`,
      },
    ],
  };

  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <Link href="/" className="text-sm text-ink-muted hover:text-foreground">
        ← All trends
      </Link>

      {/* Title + score */}
      <div className="mt-6 flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            {topic.title}
          </h1>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <StatusBadge status={topic.status} />
            <ChangeIndicator topic={topic} />
          </div>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-ink-secondary">
            {topic.explanation}
          </p>
        </div>
        <Score value={topic.score} size="hero" />
      </div>

      {/* Chart */}
      <section className="mt-10 rounded-2xl border border-hairline bg-surface p-4 sm:p-6">
        <h2 className="text-sm font-semibold">
          Daily Wikipedia pageviews — last {topic.history.length} days
        </h2>
        <p className="mt-0.5 text-xs text-ink-muted">
          Hover or tap the chart for exact daily values.
        </p>
        <div className="mt-4">
          <TrendChart series={topic.history} baseline={topic.baseline_avg} />
        </div>
      </section>

      {/* Stats */}
      <section className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat
          label="Recent attention"
          value={num.format(topic.recent_avg)}
          hint="avg daily views, last 3 days"
        />
        <Stat
          label="Baseline attention"
          value={num.format(topic.baseline_avg)}
          hint="avg daily views, 30-day baseline"
        />
        <Stat
          label="Acceleration"
          value={`${topic.growth_ratio >= 10 ? Math.round(topic.growth_ratio) : topic.growth_ratio}×`}
          hint="recent vs baseline"
        />
        <Stat
          label="Latest day"
          value={num.format(topic.latest)}
          hint={`views on ${formatDataDate(topic.data_through)}`}
        />
      </section>

      {/* Why it ranks */}
      <section className="mt-10">
        <h2 className="text-lg font-semibold tracking-tight">
          Why this topic is ranking
        </h2>
        <ul className="mt-3 max-w-2xl space-y-2 text-sm leading-relaxed text-ink-secondary">
          {topic.why.map((line) => (
            <li key={line} className="flex gap-2">
              <span aria-hidden className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
              {line}
            </li>
          ))}
        </ul>
        <p className="mt-3 max-w-2xl text-xs leading-relaxed text-ink-muted">
          These statements describe the shape of the attention data only —
          TrendAhead measures what attention did, not why it happened.
        </p>
      </section>

      {/* Score components */}
      <section className="mt-10 rounded-2xl border border-hairline bg-surface p-6">
        <h2 className="text-lg font-semibold tracking-tight">
          Score components
        </h2>
        <p className="mt-1 text-sm text-ink-muted">
          The TrendAhead Score of {topic.score} combines these subscores.{" "}
          <Link href="/methodology" className="font-medium text-accent hover:underline">
            How the score works →
          </Link>
        </p>
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {componentMeters(topic).map((m) => (
            <ComponentMeter key={m.label} {...m} />
          ))}
        </div>
      </section>

      {/* Source */}
      <section className="mt-10 rounded-xl border border-hairline bg-surface p-4 text-sm text-ink-secondary">
        <p>
          <span className="font-medium text-foreground">Source:</span>{" "}
          {topic.source} · Score {topic.score_version.toUpperCase()} ·
          Experimental
        </p>
        <p className="mt-1 text-ink-muted">
          Data through {formatDataDate(topic.data_through)} · Wikipedia article:{" "}
          <a
            href={`https://en.wikipedia.org/wiki/${encodeURIComponent(topic.wikipedia_title)}`}
            className="text-accent hover:underline"
            rel="noopener noreferrer"
            target="_blank"
          >
            {topic.title}
          </a>
        </p>
      </section>
    </main>
  );
}
