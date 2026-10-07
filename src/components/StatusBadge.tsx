import type { TrendStatus } from "@/lib/trends";

/**
 * Status is always carried by the text label; the glyph and tint are
 * reinforcement, never the only signal.
 * Blue = emerging TrendAhead signal · amber = attention receding.
 */
const styles: Record<TrendStatus, { glyph: string; className: string }> = {
  "Strong emerging signal": {
    glyph: "●",
    className: "border-accent/40 bg-accent/15 text-accent",
  },
  "Emerging signal": {
    glyph: "●",
    className: "border-accent/25 bg-accent/5 text-accent",
  },
  "Weak signal": {
    glyph: "■",
    className: "border-hairline text-ink-secondary",
  },
  "Fading / collapsing": {
    glyph: "▼",
    className:
      "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400",
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
