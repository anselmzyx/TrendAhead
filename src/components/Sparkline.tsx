/**
 * Tiny server-rendered SVG sparkline for trend cards: 2px accent line,
 * ~10% area wash, end-dot with a surface-colored ring. Decorative summary
 * only — the full interactive chart lives on the topic page.
 */
export default function Sparkline({ values }: { values: number[] }) {
  const W = 120;
  const H = 36;
  const PAD = 4;
  if (values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  const x = (i: number) => PAD + (i / (values.length - 1)) * (W - PAD * 2);
  const y = (v: number) => H - PAD - ((v - min) / span) * (H - PAD * 2);
  const points = values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`);
  const line = `M${points.join(" L")}`;
  const area = `${line} L${x(values.length - 1).toFixed(1)},${H - 1} L${x(0).toFixed(1)},${H - 1} Z`;
  const endX = x(values.length - 1);
  const endY = y(values[values.length - 1]);

  return (
    <svg
      width={W}
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="14-day attention trend"
      className="shrink-0"
    >
      <path d={area} fill="var(--accent)" opacity={0.1} />
      <path
        d={line}
        fill="none"
        stroke="var(--accent)"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx={endX} cy={endY} r={5} fill="var(--surface)" />
      <circle cx={endX} cy={endY} r={3} fill="var(--accent)" />
    </svg>
  );
}
