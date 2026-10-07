import Link from "next/link";

const links = [
  { href: "/", label: "Trends" },
  { href: "/methodology", label: "Methodology" },
  { href: "/about", label: "About" },
];

export default function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-hairline bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="text-base font-semibold tracking-tight">
          Trend<span className="text-accent">Ahead</span>
        </Link>
        <nav aria-label="Main navigation" className="flex items-center gap-4 sm:gap-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-sm text-ink-secondary transition-colors hover:text-foreground"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
