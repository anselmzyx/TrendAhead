/**
 * The TrendAhead Score (0–100) with a thin meter underneath.
 * The meter track is a lighter step of the same accent ramp, so the
 * filled/unfilled state reads across the whole bar.
 */
export default function Score({
  value,
  size = "card",
}: {
  value: number;
  size?: "card" | "hero";
}) {
  const isHero = size === "hero";
  return (
    <div className={isHero ? "w-36" : "w-20"}>
      <div className="flex items-baseline gap-1">
        <span
          className={
            (isHero ? "text-6xl" : "text-3xl") +
            " font-semibold tracking-tight leading-none text-accent"
          }
        >
          {value}
        </span>
        <span className="text-xs text-ink-muted">/100</span>
      </div>
      <div
        role="meter"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={value}
        aria-label={`TrendAhead Score ${value} out of 100`}
        className={
          "mt-2 rounded-full bg-accent-soft/40 " + (isHero ? "h-1.5" : "h-1")
        }
      >
        <div
          className="h-full rounded-full bg-accent"
          style={{ width: `${value}%` }}
        />
      </div>
      <p className="mt-1.5 text-[10px] font-medium uppercase tracking-widest text-ink-muted">
        TrendAhead Score
      </p>
    </div>
  );
}
