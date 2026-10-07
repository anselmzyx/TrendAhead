"""Phase 5.5 CLI: combined candidate discovery (new entrants + improvers),
source hygiene, and TrendAhead Score V1 ranking — printed for inspection.

All logic lives in run_pipeline.py / discovery.py / scoring.py.

Run:  python3 pipeline/discover_and_score.py
"""

from __future__ import annotations

import json
import sys

from run_pipeline import OUTPUT_DIR, run_pipeline


def main() -> None:
    result = run_pipeline()
    days = result["window"]
    print(f"Discovery window: {days[0]} → {days[-1]}")

    pool_after = result["raw_unique"] - sum(len(v) for v in result["removed"].values())
    print(f"\nUnique candidates: {result['raw_unique']:,} → {pool_after:,} after filters.")
    print("Removed by filter:")
    for reason, titles in sorted(result["removed"].items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(titles):>4}  {reason}  (e.g. {', '.join(titles[:3])})")

    overlap = [t for t, r in result["combined"].items() if len(r) > 1]
    print(f"\nNew entrants: {len(result['entrants'])}  |  improvers: "
          f"{len(result['improvers'])}  |  overlap: {len(overlap)}  |  "
          f"combined: {len(result['combined'])}  |  failures: {len(result['failures'])}")

    rows = result["rows"]
    print("\n============ TRENDAHEAD SCORE V1 — COMBINED DISCOVERY (EXPERIMENTAL) ============")
    print(f"{'#':>2} {'Topic':<32} {'Score':>5} {'Discovery':<21} {'Recent':>8} "
          f"{'Basln':>7} {'Pers':>4} {'Qual':>4}  Status")
    print("-" * 110)
    for i, r in enumerate(rows[:20], 1):
        c, st = r["components"], r["stats"]
        title = r["title"].replace("_", " ")
        title = title if len(title) <= 32 else title[:29] + "..."
        reason = " + ".join(r["reasons"])
        print(f"{i:>2} {title:<32} {r['score']:>5} {reason:<21} {st['recent_avg']:>8,} "
              f"{st['baseline_avg']:>7,} {c['persistence']:>4.2f} "
              f"{c['spike_quality']:>4.2f}  {r['status']}")
    print("-" * 110)

    out = OUTPUT_DIR / f"combined_scores_{result['end']}.json"
    out.write_text(json.dumps(
        {"note": "TrendAhead Score V1, combined discovery — EXPERIMENTAL",
         "window": [str(d) for d in days],
         "removed_by_filter": result["removed"], "failures": result["failures"],
         "ranked": [{k: v for k, v in r.items() if k != "history"} for r in rows]},
        indent=1))
    print(f"Saved → {out}")


if __name__ == "__main__":
    sys.exit(main())
