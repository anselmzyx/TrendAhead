import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About",
  description:
    "TrendAhead detects unusual acceleration in public online attention to identify topics gaining momentum before they become obviously mainstream.",
  alternates: { canonical: "/about" },
};

export default function AboutPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-12 sm:px-6 sm:py-16">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        About TrendAhead
      </h1>
      <div className="mt-6 max-w-2xl space-y-4 text-ink-secondary leading-relaxed">
        <p className="text-lg text-foreground">
          TrendAhead detects unusual acceleration in public online attention to
          identify topics gaining momentum before they become obviously
          mainstream.
        </p>
        <p>
          Most trend tools show you what is already popular. By then, everyone
          knows. TrendAhead instead watches for topics whose attention is
          unusually far above their own normal level — and prefers interest
          that keeps building across days over one-day spikes.
        </p>
        <p>
          <strong className="text-foreground">What it is today:</strong> an
          experimental attention-discovery system built entirely from public
          Wikimedia data — daily Wikipedia pageview statistics, processed into
          a transparent 0–100 TrendAhead Score. It measures one meaningful lens
          on online attention, not the whole internet; additional independent
          sources (like news coverage volume) are planned next.
        </p>
        <p>
          It&apos;s built for people who benefit from being early: content
          creators, journalists, newsletter writers, marketers, founders,
          researchers and the simply curious.
        </p>
        <p>
          Every ranking is driven by transparent statistics on public data — no
          black boxes, no AI guessing. You can read exactly how it works on the{" "}
          <Link href="/methodology" className="font-medium text-accent hover:underline">
            methodology page
          </Link>
          .
        </p>
        <h2 className="pt-2 text-lg font-semibold tracking-tight text-foreground">
          Privacy
        </h2>
        <p>
          TrendAhead has no user accounts and collects no personal
          information. To understand aggregate usage we use Cloudflare Web
          Analytics, a privacy-focused tool that works without cookies and
          without tracking individuals. There are no advertising trackers and
          no session recording.
        </p>
      </div>
    </main>
  );
}
