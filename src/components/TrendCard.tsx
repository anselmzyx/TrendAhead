import Link from "next/link";
import Score from "@/components/Score";
import Sparkline from "@/components/Sparkline";
import StatusBadge from "@/components/StatusBadge";
import ChangeIndicator from "@/components/ChangeIndicator";
import type { TrendingTopic } from "@/lib/trends";

export default function TrendCard({ topic }: { topic: TrendingTopic }) {
  return (
    <Link
      href={`/topic/${topic.slug}`}
      className="group flex flex-col rounded-2xl border border-hairline bg-surface p-5 transition-colors hover:border-accent/50"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-xs font-medium tabular-nums text-ink-muted">
            #{topic.rank}
          </p>
          <h3 className="mt-1 text-lg font-semibold tracking-tight group-hover:text-accent">
            {topic.title}
          </h3>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={topic.status} />
            <ChangeIndicator topic={topic} />
          </div>
        </div>
        <Score value={topic.score} />
      </div>
      <div className="mt-4 flex items-end justify-between gap-4">
        <p className="text-sm leading-snug text-ink-secondary">
          {topic.explanation}
        </p>
        <Sparkline values={topic.sparkline} />
      </div>
    </Link>
  );
}
