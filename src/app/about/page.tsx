import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About",
  description:
    "TrendAhead detects unusual acceleration in public online attention to identify topics gaining momentum before they become obviously mainstream.",
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
          unusually far above their own normal level — the moment a trend starts
          moving, not the moment it peaks.
        </p>
        <p>
          It&apos;s built for people who benefit from being early: content
          creators, journalists, newsletter writers, marketers, founders,
          researchers and the simply curious.
        </p>
        <p>
          Every ranking is driven by transparent statistics on public data — no
          black boxes. You can read exactly how it works on the{" "}
          <Link href="/methodology" className="font-medium text-accent hover:underline">
            methodology page
          </Link>
          .
        </p>
      </div>
    </main>
  );
}
