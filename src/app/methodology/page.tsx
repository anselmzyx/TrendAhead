import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How TrendAhead discovers topics and computes the 0–100 TrendAhead Score from Wikipedia attention data.",
  alternates: { canonical: "/methodology" },
};

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mt-10">
      <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
      <div className="mt-2 max-w-2xl space-y-3 text-sm leading-relaxed text-ink-secondary">
        {children}
      </div>
    </section>
  );
}

export default function MethodologyPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-12 sm:px-6 sm:py-16">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        Methodology
      </h1>
      <p className="mt-3 max-w-2xl text-ink-secondary">
        TrendAhead is a statistical indicator, not a crystal ball. This page
        explains exactly what it measures, in plain language. The scoring
        engine is <strong className="text-foreground">V1 and experimental</strong>.
      </p>

      <Section title="What TrendAhead measures">
        <p>
          TrendAhead looks for topics whose public attention is growing
          unusually fast <em>relative to their own normal</em>. We care about
          the rate of change, not absolute popularity: a topic going from 3,000
          to 60,000 daily views is more interesting to us than one sitting
          steadily at a million. Sustained multi-day climbs are deliberately
          rewarded over one-day spikes.
        </p>
      </Section>

      <Section title="The data: Wikipedia attention">
        <p>
          Every number currently comes from one source: daily pageview
          statistics for English Wikipedia, published openly by the Wikimedia
          Foundation (CC0 licensed). Pageviews are a good proxy for &quot;people
          actively looking something up&quot; — but they are one lens on online
          attention, not the whole internet. Independent confirmation sources
          (such as news coverage volume) are planned for later versions.
        </p>
        <p>
          We count human visits only (Wikimedia&apos;s bot-filtered
          &quot;user&quot; traffic), and data is precomputed daily — your visit
          to this site triggers no API calls.
        </p>
      </Section>

      <Section title="How topics are discovered">
        <p>
          Nobody types topic lists in by hand. Each day we examine the 1,000
          most-viewed Wikipedia articles for the last six complete days and
          select candidates by two paths:
        </p>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <strong className="text-foreground">New entrants</strong> — pages
            that appear in recent days&apos; top lists but were absent earlier
            in the window (sudden arrivals).
          </li>
          <li>
            <strong className="text-foreground">Improvers</strong> — pages
            present throughout, whose recent attention is at least 1.4× their
            earlier level (steady climbers).
          </li>
        </ul>
        <p>
          Obvious non-topics are filtered transparently: Wikipedia&apos;s
          internal pages (Special:, Portal:, File:, …), navigation pages like
          the Main Page, and a tiny explicit list of pages whose traffic is
          driven by Wikimedia&apos;s own site banners rather than public
          interest. There is no filtering by subject matter — sports, politics
          and celebrities are all eligible.
        </p>
      </Section>

      <Section title="How the TrendAhead Score works">
        <p>
          Each candidate&apos;s last 3 days are compared against the 30 days
          before them. Five transparent components combine into one 0–100
          score:
        </p>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <strong className="text-foreground">Acceleration (35%)</strong> —
            how many times above its own baseline the topic now sits, on a
            log scale so freak ratios can&apos;t dominate.
          </li>
          <li>
            <strong className="text-foreground">Anomaly (25%)</strong> — how
            statistically unusual the recent level is versus the topic&apos;s
            own history (a capped z-score).
          </li>
          <li>
            <strong className="text-foreground">Persistence (40%)</strong> —
            the largest weight, deliberately: how many recent days stayed
            elevated and kept rising. This is what makes a five-day climber
            outrank a one-day explosion.
          </li>
          <li>
            <strong className="text-foreground">Volume (gate)</strong> — a
            topic needs real attention (roughly 1,000+ daily views to count at
            all). 2 → 20 views is 10× growth and still means nothing.
          </li>
          <li>
            <strong className="text-foreground">Signal quality (damp)</strong>{" "}
            — traffic concentrated in a single day is scored down (to as
            little as a quarter) but never deleted.
          </li>
          <li>
            <strong className="text-foreground">Momentum (damp)</strong> —
            whether the signal appears to have momentum remaining: the latest
            day&apos;s distance from the recent peak plus the direction of the
            last few days. A topic whose peak has clearly passed keeps at
            most 40% of its score.
          </li>
        </ul>
        <p>
          Each topic also gets a status describing{" "}
          <em>what the attention is doing right now</em>, derived purely from
          the time-series shape:{" "}
          <strong className="text-foreground">Building</strong> (elevated for
          several days and still rising),{" "}
          <strong className="text-foreground">Breaking out</strong> (at its
          peak, but the surge is only a day or two old — too new to call
          sustained), <strong className="text-foreground">Elevated</strong> (a
          high plateau), <strong className="text-foreground">Peaked /
          fading</strong> (the latest day is well below the recent peak), and{" "}
          <strong className="text-foreground">Weak signal</strong>.
        </p>
      </Section>

      <Section title="Limitations — please read">
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <strong className="text-foreground">Wikipedia-only signal.</strong>{" "}
            Trends that don&apos;t drive Wikipedia lookups are invisible to us
            today.
          </li>
          <li>
            <strong className="text-foreground">Top-1000 discovery.</strong>{" "}
            Candidates must reach Wikipedia&apos;s daily top-1000 at least once
            during the window, so genuinely niche long-tail topics can be
            missed.
          </li>
          <li>
            News events create reactive attention spikes. We down-rank spike
            shapes, but a two-day-old story can look identical to day two of a
            lasting trend — only more days of data distinguish them.
          </li>
          <li>
            The score describes attention <em>shape</em>, never cause, and{" "}
            <strong className="text-foreground">does not predict future
            popularity</strong>. Treat it as one research input — never the
            sole basis for decisions (especially financial ones).
          </li>
          <li>Score V1 is experimental and its parameters will evolve.</li>
        </ul>
      </Section>
    </main>
  );
}
