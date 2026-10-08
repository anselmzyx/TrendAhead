import type { Metadata } from "next";
import Link from "next/link";
import TrendCard from "@/components/TrendCard";
import { formatDataDate, getTrending } from "@/lib/trends";
import { SITE_NAME, SITE_ORIGIN } from "@/lib/site";

export const metadata: Metadata = {
  alternates: { canonical: "/" },
};

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE_NAME,
  url: `${SITE_ORIGIN}/`,
  description:
    "TrendAhead detects topics gaining unusual attention before they become obviously mainstream, using public Wikipedia attention data and a transparent 0–100 score.",
};

export default async function Home() {
  const data = await getTrending();

  return (
    <main className="mx-auto w-full max-w-6xl px-4 pb-20 sm:px-6">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }}
      />
      {/* Hero */}
      <section className="py-16 text-center sm:py-24">
        <h1 className="mx-auto max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
          The internet is suddenly interested in...
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-ink-secondary">
          See what&apos;s gaining momentum before everyone else does.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-2 text-sm">
          <span className="rounded-full border border-accent/30 bg-accent/5 px-3 py-1 font-medium text-accent">
            Wikipedia attention · Experimental
          </span>
          {data ? (
            <span className="rounded-full border border-hairline px-3 py-1 text-ink-muted">
              Data through {formatDataDate(data.data_through)}
            </span>
          ) : null}
        </div>
        <p className="mx-auto mt-4 max-w-md text-xs leading-relaxed text-ink-muted">
          The current experimental signal measures unusual acceleration in
          Wikipedia pageviews — one lens on online attention, not the whole
          internet. More independent sources are planned.
        </p>
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
        {data && data.topics.length > 0 ? (
          <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
            {data.topics.map((t) => (
              <TrendCard key={t.slug} topic={t} />
            ))}
          </div>
        ) : (
          <div className="mt-6 rounded-2xl border border-hairline bg-surface p-10 text-center">
            <p className="font-medium">No trend data available yet.</p>
            <p className="mt-2 text-sm text-ink-muted">
              The data pipeline hasn&apos;t produced a dataset. Run{" "}
              <code className="rounded bg-background px-1.5 py-0.5 font-mono text-xs">
                python3 pipeline/generate_site_data.py
              </code>{" "}
              and reload.
            </p>
          </div>
        )}
      </section>

      {/* Score explainer */}
      <section className="mt-20 rounded-2xl border border-hairline bg-surface p-6 sm:p-10">
        <h2 className="text-xl font-semibold tracking-tight">
          What is the TrendAhead Score?
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink-secondary">
          A 0–100 indicator of how unusually fast a topic is gaining attention,
          computed from public Wikipedia pageview statistics. It rewards rate
          of change, not raw popularity — and sustained multi-day climbs rank
          above one-day spikes.
        </p>
        <div className="mt-6 grid gap-6 sm:grid-cols-3">
          <div>
            <h3 className="text-sm font-semibold">Acceleration &amp; anomaly</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              How far current attention sits above the topic&apos;s own 30-day
              baseline, and how statistically unusual that is.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Persistence</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              Interest that stays elevated and keeps climbing across several
              days counts for more than a single spike.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Volume &amp; signal quality</h3>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              Enough real attention to matter, and traffic spread across days
              rather than concentrated in one burst.
            </p>
          </div>
        </div>
        <p className="mt-6 text-sm">
          <Link href="/methodology" className="font-medium text-accent hover:underline">
            Read the full methodology →
          </Link>
        </p>
      </section>
    </main>
  );
}
