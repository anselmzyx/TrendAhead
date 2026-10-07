import Link from "next/link";
import Score from "@/components/Score";
import Sparkline from "@/components/Sparkline";
import StatusBadge from "@/components/StatusBadge";
import { trendStats, type Trend } from "@/lib/mock-trends";

export default function TrendCard({
  trend,
  rank,
}: {
  trend: Trend;
  rank: number;
}) {
  const stats = trendStats(trend);
  return (
    <Link
      href={`/topic/${trend.slug}`}
      className="group flex flex-col rounded-2xl border border-hairline bg-surface p-5 transition-colors hover:border-accent/50"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-xs font-medium tabular-nums text-ink-muted">
            #{rank}
          </p>
          <h3 className="mt-1 truncate text-lg font-semibold tracking-tight group-hover:text-accent">
            {trend.name}
          </h3>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={trend.status} />
            <span className="text-sm font-medium text-delta-up">
              ↑ +{stats.changePercent}% recent attention
            </span>
          </div>
        </div>
        <Score value={trend.score} />
      </div>
      <div className="mt-4 flex items-end justify-between gap-4">
        <p className="text-sm leading-snug text-ink-secondary">
          Interest is {stats.ratio}× above its 30-day baseline.
        </p>
        <Sparkline series={trend.series} />
      </div>
    </Link>
  );
}
