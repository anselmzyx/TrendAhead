import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Score from "@/components/Score";
import StatusBadge from "@/components/StatusBadge";
import TrendChart from "@/components/TrendChart";
import {
  MOCK_DATA_SOURCE,
  MOCK_LAST_UPDATED,
  getTrend,
  trendStats,
  trends,
} from "@/lib/mock-trends";

export function generateStaticParams() {
  return trends.map((t) => ({ slug: t.slug }));
}

export async function generateMetadata({
  params,
}: PageProps<"/topic/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const trend = getTrend(slug);
  if (!trend) return { title: "Topic not found" };
  return {
    title: trend.name,
    description: `${trend.name} has a TrendAhead Score of ${trend.score}/100 (${trend.status}). ${trend.why}`,
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

export default async function TopicPage({ params }: PageProps<"/topic/[slug]">) {
  const { slug } = await params;
  const trend = getTrend(slug);
  if (!trend) notFound();

  const stats = trendStats(trend);
  const updated = new Date(MOCK_LAST_UPDATED).toLocaleString("en", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  });

  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <Link href="/" className="text-sm text-ink-muted hover:text-foreground">
        ← All trends
      </Link>

      {/* Title + score */}
      <div className="mt-6 flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            {trend.name}
          </h1>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <StatusBadge status={trend.status} />
            <span className="text-sm font-medium text-delta-up">
              ↑ +{stats.changePercent}% recent attention
            </span>
          </div>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-ink-secondary">
            {trend.why}
          </p>
        </div>
        <Score value={trend.score} size="hero" />
      </div>

      {/* Chart */}
      <section className="mt-10 rounded-2xl border border-hairline bg-surface p-4 sm:p-6">
        <h2 className="text-sm font-semibold">Daily attention — last 30 days</h2>
        <p className="mt-0.5 text-xs text-ink-muted">
          Hover or tap the chart for exact daily values.
        </p>
        <div className="mt-4">
          <TrendChart series={trend.series} baseline={stats.baselineAvg} />
        </div>
      </section>

      {/* Stats */}
      <section className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat
          label="Recent attention"
          value={num.format(stats.recentAvg)}
          hint="avg daily views, last 7 days"
        />
        <Stat
          label="Baseline attention"
          value={num.format(stats.baselineAvg)}
          hint="avg daily views, 30-day baseline"
        />
        <Stat
          label="Acceleration"
          value={`${stats.ratio}×`}
          hint="recent vs baseline"
        />
        <Stat
          label="Anomaly (z-score)"
          value={stats.zScore.toFixed(1)}
          hint="how unusual the latest day is"
        />
      </section>

      {/* Why it ranks */}
      <section className="mt-10">
        <h2 className="text-lg font-semibold tracking-tight">
          Why this topic is ranking
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink-secondary">
          TrendAhead flags topics whose current attention is far above their own
          recent normal. {trend.name} is averaging {num.format(stats.recentAvg)}{" "}
          daily views over the past week — {stats.ratio}× its 30-day baseline of{" "}
          {num.format(stats.baselineAvg)} — and the move has persisted across
          multiple days rather than spiking once. That combination of growth,
          deviation from baseline and persistence produces its TrendAhead Score
          of {trend.score}/100.
        </p>
        <p className="mt-4 text-sm">
          <Link href="/methodology" className="font-medium text-accent hover:underline">
            How the score works →
          </Link>
        </p>
      </section>

      {/* Source */}
      <section className="mt-10 rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 text-sm">
        <p className="font-medium text-amber-700 dark:text-amber-400">
          Data source: {MOCK_DATA_SOURCE}
        </p>
        <p className="mt-1 text-ink-secondary">Last updated {updated} UTC.</p>
      </section>
    </main>
  );
}
