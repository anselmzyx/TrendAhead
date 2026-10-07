"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from "recharts";
import type { DailyViews } from "@/lib/mock-trends";

const compact = new Intl.NumberFormat("en", { notation: "compact" });
const full = new Intl.NumberFormat("en");

function formatDate(iso: string): string {
  const d = new Date(iso + "T00:00:00Z");
  return d.toLocaleDateString("en", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

function ChartTooltip({ active, payload, label }: TooltipContentProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-hairline bg-surface px-3 py-2 shadow-sm">
      <p className="text-sm font-semibold tabular-nums">
        {full.format(Number(payload[0].value ?? 0))}{" "}
        <span className="font-normal text-ink-muted">views</span>
      </p>
      <p className="text-xs text-ink-muted">{formatDate(String(label))}</p>
    </div>
  );
}

export default function TrendChart({
  series,
  baseline,
}: {
  series: DailyViews[];
  baseline: number;
}) {
  return (
    <div className="h-64 w-full sm:h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={series}
          margin={{ top: 12, right: 12, bottom: 0, left: 0 }}
        >
          <CartesianGrid
            vertical={false}
            stroke="var(--chart-grid)"
            strokeWidth={1}
          />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            ticks={[
              series[0]?.date,
              series[9]?.date,
              series[19]?.date,
              series[29]?.date,
            ].filter(Boolean)}
            tick={{ fill: "var(--ink-muted)", fontSize: 12 }}
            axisLine={{ stroke: "var(--chart-axis)" }}
            tickLine={false}
            dy={6}
          />
          <YAxis
            tickFormatter={(v: number) => compact.format(v)}
            tick={{ fill: "var(--ink-muted)", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={44}
          />
          <Tooltip
            content={ChartTooltip}
            cursor={{ stroke: "var(--chart-axis)", strokeWidth: 1 }}
          />
          <ReferenceLine
            y={baseline}
            stroke="var(--ink-muted)"
            strokeWidth={1}
            strokeDasharray="4 4"
            label={{
              value: "30-day baseline",
              position: "insideBottomLeft",
              fill: "var(--ink-muted)",
              fontSize: 11,
            }}
          />
          <Area
            type="monotone"
            dataKey="views"
            stroke="var(--accent)"
            strokeWidth={2}
            strokeLinecap="round"
            fill="var(--accent)"
            fillOpacity={0.1}
            activeDot={{
              r: 4,
              fill: "var(--accent)",
              stroke: "var(--surface)",
              strokeWidth: 2,
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
