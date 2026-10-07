import TrendCard from "@/components/TrendCard";
import { MOCK_LAST_UPDATED, trends } from "@/lib/mock-trends";

function formatUpdated(iso: string): string {
  return new Date(iso).toLocaleString("en", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  });
}

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-6xl px-4 pb-20 sm:px-6">
      {/* Hero */}
      <section className="py-16 text-center sm:py-24">
        <h1 className="mx-auto max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
          The internet is suddenly interested in...
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-ink-secondary">
          See what&apos;s gaining momentum before everyone else does.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-2 text-sm">
          <span className="rounded-full border border-hairline px-3 py-1 text-ink-muted">
            Last updated {formatUpdated(MOCK_LAST_UPDATED)} UTC
          </span>
          <span className="rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 font-medium text-amber-700 dark:text-amber-400">
            Demo data — these are not real trends yet
          </span>
        </div>
      </section>

      {/* Ranked trend cards */}
      <section aria-labelledby="top-trends">
        <h2 id="top-trends" className="text-xl font-semibold tracking-tight">
          Top emerging topics
        </h2>
        <p className="mt-1 text-sm text-ink-muted">
          Ranked by TrendAhead Score — a 0–100 measure of unusual, accelerating
          attention.
        </p>
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          {trends.map((t, i) => (
            <TrendCard key={t.slug} trend={t} rank={i + 1} />
          ))}
        </div>
      </section>

      {/* Score explainer */}
      <section className="mt-20 rounded-2xl border border-hairline bg-surface p-6 sm:p-10">
        <h2 className="text-xl font-semibold tracking-tight">
          What is the TrendAhead Score?
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink-secondary">
          A 0–100 indicator of how unusually fast a topic is gaining attention.
          It rewards rate of change, not raw popularity — a topic going from
          1,000 to 8,000 daily views can outrank one sitting steadily at a
          million.
        </p>
        <div className="mt-6 grid gap-6 sm:grid-cols-3">
          <div>
            <h3 className="text-sm font-semibold">Recent growth</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              How much attention has accelerated over the last few days.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Deviation from baseline</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              How far current interest sits above the topic&apos;s own 30-day
              normal.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Volume &amp; persistence</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              Enough real attention, sustained across multiple days — not a
              one-hour blip.
            </p>
          </div>
        </div>
        <p className="mt-6 text-sm">
          <a href="/methodology" className="font-medium text-accent hover:underline">
            Read the full methodology →
          </a>
        </p>
      </section>
    </main>
  );
}
