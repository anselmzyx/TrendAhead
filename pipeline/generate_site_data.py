"""Generate the website's real data files from the full pipeline.

    Wikimedia → discovery → histories → TrendAhead Score V1 → data/*.json

Writes:
  data/trending.json        (homepage, top 12)
  data/topics/<slug>.json   (top 24 topic pages)

Validates everything before writing; exits non-zero on any problem so a
broken dataset can never silently ship.

Run from the repo root:  python3 pipeline/generate_site_data.py
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from run_pipeline import run_pipeline
from site_data import build_site_data, validate_site_data

DATA_DIR = Path(__file__).parent.parent / "data"


def main() -> int:
    print("Running TrendAhead pipeline (discovery → histories → scores)...")
    result = run_pipeline()
    rows = result["rows"]
    print(f"\nWindow {result['window'][0]} → {result['end']}  |  "
          f"candidates scored: {len(rows)}  |  failures: {len(result['failures'])}")
    if not rows:
        print("ERROR: pipeline produced no scored topics; refusing to write site data.")
        return 1

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    trending, topics = build_site_data(rows, str(result["end"]), generated_at)

    problems = validate_site_data(trending, topics)
    if problems:
        print("ERROR: generated data failed validation:")
        for p in problems:
            print(f"  - {p}")
        return 1

    # Safe replacement: build everything in temporary paths first, then swap.
    # A crash mid-write can therefore never leave the website with a
    # half-written dataset — the last good files survive untouched.
    topics_dir = DATA_DIR / "topics"
    tmp_topics = DATA_DIR / "topics.tmp"
    tmp_trending = DATA_DIR / "trending.json.tmp"
    if tmp_topics.exists():
        shutil.rmtree(tmp_topics)
    tmp_topics.mkdir(parents=True)
    for slug, topic in topics.items():
        (tmp_topics / f"{slug}.json").write_text(json.dumps(topic, indent=1))
    tmp_trending.write_text(json.dumps(trending, indent=1))
    # Swap into place (near-atomic: two renames after all writing succeeded).
    if topics_dir.exists():
        shutil.rmtree(topics_dir)
    tmp_topics.rename(topics_dir)
    tmp_trending.replace(DATA_DIR / "trending.json")

    print(f"\nWrote data/trending.json ({len(trending['topics'])} homepage topics)")
    print(f"Wrote {len(topics)} topic files to data/topics/")
    print(f"Data through: {trending['data_through']}  |  generated: {generated_at}")
    print("\nHomepage ranking:")
    for e in trending["topics"]:
        print(f"  {e['rank']:>2}. {e['title']:<36} {e['score']:>3}  {e['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
