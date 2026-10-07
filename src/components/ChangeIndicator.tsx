import type { TrendCore } from "@/lib/trends";

/**
 * Formats the recent-vs-baseline change truthfully:
 * - fading topics say so (amber ↓) instead of implying acceleration
 * - very large ratios read as "N× baseline" (a "+82,000%" looks absurd)
 * - everything else is a plain percentage
 * All values come from the pipeline; nothing is recalculated here.
 */
export default function ChangeIndicator({ topic }: { topic: TrendCore }) {
  if (topic.status === "Peaked / fading") {
    return (
      <span className="text-sm font-medium text-amber-700 dark:text-amber-400">
        ↓ falling from its peak
      </span>
    );
  }
  const label =
    topic.growth_ratio >= 10
      ? `${Math.round(topic.growth_ratio)}× baseline attention`
      : topic.change_percent !== null && topic.change_percent >= 0
        ? `+${topic.change_percent}% recent attention`
        : `${topic.change_percent ?? 0}% recent attention`;
  return <span className="text-sm font-medium text-delta-up">↑ {label}</span>;
}
