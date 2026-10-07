export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-24 text-center">
      <p className="mb-6 text-sm font-medium uppercase tracking-widest text-neutral-500">
        TrendAhead
      </p>
      <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl dark:text-neutral-50">
        The internet is suddenly interested in...
      </h1>
      <p className="mt-6 max-w-xl text-lg text-neutral-600 dark:text-neutral-400">
        See what&apos;s gaining momentum before everyone else does.
      </p>
      <p className="mt-12 rounded-full border border-neutral-200 px-4 py-1.5 text-sm text-neutral-500 dark:border-neutral-800">
        Phase 1 — project foundation. Trend data coming soon.
      </p>
    </main>
  );
}
