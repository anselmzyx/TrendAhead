import type { TrendStatus } from "@/lib/mock-trends";

/**
 * Status is always carried by the text label; the glyph is reinforcement,
 * never the only signal.
 */
const glyphs: Record<TrendStatus, string> = {
  Emerging: "●",
  Rising: "▲",
  Stable: "■",
  Fading: "▼",
};

export default function StatusBadge({ status }: { status: TrendStatus }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-hairline px-2.5 py-0.5 text-xs font-medium text-ink-secondary">
      <span aria-hidden className="text-[8px] text-accent">
        {glyphs[status]}
      </span>
      {status}
    </span>
  );
}
