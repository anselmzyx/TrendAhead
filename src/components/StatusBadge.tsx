import type { TrendStatus } from "@/lib/mock-trends";

/**
 * Status is always carried by the text label; the glyph and tint are
 * reinforcement, never the only signal.
 * Emerging → accent (new signal) · Rising → green (positive movement) ·
 * Stable/Fading → neutral until real data justifies more states.
 */
const styles: Record<TrendStatus, { glyph: string; className: string }> = {
  Emerging: {
    glyph: "●",
    className: "border-accent/30 bg-accent/10 text-accent",
  },
  Rising: {
    glyph: "▲",
    className: "border-delta-up/30 bg-delta-up/10 text-delta-up",
  },
  Stable: {
    glyph: "■",
    className: "border-hairline text-ink-secondary",
  },
  Fading: {
    glyph: "▼",
    className: "border-hairline text-ink-muted",
  },
};

export default function StatusBadge({ status }: { status: TrendStatus }) {
  const s = styles[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${s.className}`}
    >
      <span aria-hidden className="text-[8px]">
        {s.glyph}
      </span>
      {status}
    </span>
  );
}
