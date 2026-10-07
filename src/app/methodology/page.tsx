import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How TrendAhead measures unusual online attention and computes the 0–100 TrendAhead Score.",
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
        explains exactly what it measures, in plain language.
      </p>

      <Section title="What TrendAhead measures">
        <p>
          TrendAhead looks for topics whose public attention is growing
          unusually fast <em>relative to their own normal</em>. We care about
          the rate of change, not absolute popularity: a topic going from 1,000
          to 8,000 daily views is often more interesting than one sitting
          steadily at a million.
        </p>
      </Section>

      <Section title="What data we use">
        <p>
          The first data source will be public Wikipedia pageview statistics,
          published by the Wikimedia Foundation — a good proxy for &quot;people
          actively looking something up.&quot; Later phases may add independent
          confirmation sources such as news coverage volume.
        </p>
        <p className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 font-medium text-amber-700 dark:text-amber-400">
          Right now the site shows demo data only, while the product is under
          construction. No numbers on this site are real yet.
        </p>
      </Section>

      <Section title="How baselines work">
        <p>
          Every topic is compared against itself. We average its attention over
          roughly the previous 30 days to establish a personal
          &quot;normal&quot; — the baseline — then measure how far the last few
          days sit above it. This is why a niche topic can outrank a famous one:
          fame is already in its baseline.
        </p>
      </Section>

      <Section title="How the TrendAhead Score works">
        <p>A topic&apos;s 0–100 score combines four simple ingredients:</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <strong className="text-foreground">Recent growth</strong> — how much
            attention increased over the last few days.
          </li>
          <li>
            <strong className="text-foreground">Deviation from baseline</strong>{" "}
            — how statistically unusual current attention is versus the
            topic&apos;s own history (a z-score).
          </li>
          <li>
            <strong className="text-foreground">Volume</strong> — a minimum
            amount of real attention, so 2 → 10 views can&apos;t outrank a
            genuine trend.
          </li>
          <li>
            <strong className="text-foreground">Persistence</strong> — growth
            sustained across multiple days counts more than a single spike.
          </li>
        </ul>
        <p>
          The exact formula will be published on this page once the real scoring
          engine is built, and kept up to date whenever it changes.
        </p>
      </Section>

      <Section title="Limitations — please read">
        <ul className="list-disc space-y-1 pl-5">
          <li>
            The score is a derived statistical indicator. It is not
            scientifically validated and does not predict the future.
          </li>
          <li>
            Attention data is noisy: news events, celebrity mentions and even
            bots can cause spikes that mean little.
          </li>
          <li>
            Early signals are early — many emerging topics fade again. Treat
            TrendAhead as one research input, never as the sole basis for
            decisions (especially financial ones).
          </li>
        </ul>
      </Section>
    </main>
  );
}
