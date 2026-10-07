import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col items-center justify-center px-6 py-24 text-center">
      <p className="text-sm font-medium uppercase tracking-widest text-ink-muted">
        404
      </p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight">
        Nothing is trending here
      </h1>
      <p className="mt-3 max-w-md text-sm leading-relaxed text-ink-secondary">
        This page doesn&apos;t exist — the topic may have been removed, or the
        address was mistyped.
      </p>
      <Link
        href="/"
        className="mt-8 rounded-full bg-accent px-5 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
      >
        Back to all trends
      </Link>
    </main>
  );
}
