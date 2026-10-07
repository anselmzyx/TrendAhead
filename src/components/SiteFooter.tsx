import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="border-t border-hairline">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-8 text-sm text-ink-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>
          <span className="font-medium text-ink-secondary">TrendAhead</span> — see
          what&apos;s gaining momentum before everyone else does.
        </p>
        <p className="flex gap-4">
          <Link href="/methodology" className="hover:text-foreground">
            Methodology
          </Link>
          <Link href="/about" className="hover:text-foreground">
            About
          </Link>
        </p>
      </div>
    </footer>
  );
}
