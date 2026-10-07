import type { TrendStatus } from "@/lib/trends";

/**
 * Status answers "what is the attention doing now?" — derived purely from
 * the time-series shape by the pipeline. The text label always carries the
 * meaning; glyph and tint are reinforcement, never the only signal.
 */
const styles: Record<TrendStatus, { glyph: string; className: string }> = {
  Building: {
    glyph: "●",
    className: "border-accent/40 bg-accent/15 text-accent",
  },
  "Breaking out": {
    glyph: "▲",
    className: "border-accent/25 bg-accent/5 text-accent",
  },
  Elevated: {
    glyph: "■",
    className: "border-hairline bg-surface text-ink-secondary",
  },
  "Peaked / fading": {
    glyph: "▼",
    className:
      "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400",
  },
  "Weak signal": {
    glyph: "■",
    className: "border-hairline text-ink-muted",
  },
};

export default function StatusBadge({ status }: { status: TrendStatus }) {
  const s = styles[status] ?? styles["Weak signal"];
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
