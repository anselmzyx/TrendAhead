"""Phase 9 live evaluation: news confirmation for ~8 real topics, plus the
Approach A vs B ranking comparison. Paced + cached; safe to re-run.

Run:  python3 -u pipeline/poc_cross_source.py
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from cross_source import evaluate_news_confirmation
from scoring import score_series

OUTPUT_DIR = Path(__file__).parent / "output"

TOPICS = [
    "Michael_Douglas",            # Building
    "Karl_Deisseroth",            # Breaking out (fresh event)
    "2026_Quebec_general_election",  # Breaking out (election climax)
    "2026–27_UEFA_Nations_League",   # Building
    "Jim_Bakker",                 # Breaking out
    "2026_Brazilian_general_election",  # Peaked / fading
    "Jeffrey_Archer",             # Breaking out
    "Neha_Bora",                  # Elevated
]


def wiki_aligned_summary(views: list[int], dates: list[str], through: str) -> str:
    """Wikipedia stats truncated to the GDELT-aligned end date."""
    if through not in dates:
        return "no aligned wiki data"
    idx = dates.index(through) + 1
    v = views[:idx]
    if len(v) < 17:
        return "too little aligned wiki data"
    recent = sum(v[-3:]) / 3
    base = v[-33:-3] if len(v) >= 33 else v[:-3]
    base_avg = sum(base) / len(base)
    pct = (recent - base_avg) / max(base_avg, 1) * 100
    return f"aligned wiki recent {recent:,.0f}/day vs baseline {base_avg:,.0f}/day ({pct:+.0f}%)"


def main() -> None:
    cache = sorted(OUTPUT_DIR.glob("histories_*.json"))[-1]
    histories = json.loads(cache.read_text())["histories"]
    wiki_end = date.fromisoformat(json.loads(cache.read_text())["end_day"])

    results = {}
    for title in TOPICS:
        print(f"\n{'=' * 70}\n### {title.replace('_', ' ')}")
        h = histories.get(title)
        base_score, status = None, "?"
        if h:
            views = [v for _, v in h["series"]]
            r = score_series(views)
            base_score, status = r["score"], r["status"]
            print(f"  TrendAhead V1.1: score {base_score}  status {status}")
        nc = evaluate_news_confirmation(title, wiki_end)
        results[title] = {"score": base_score, "status": status, "news": nc}
        print(f"  query variants: {nc.get('variants_tried') or '(first variant passed)'}")
        print(f"  selected query: {nc.get('query')!r}  relevance: {nc.get('relevance')}")
        for t in nc.get("sample_titles", [])[:4]:
            print(f"    · {t[:78]}")
        print(f"  STATE: {nc['state'].upper()}  value: {nc.get('value')}")
        if nc["state"] == "unavailable":
            print(f"  reason: {nc.get('reason')}")
        else:
            print(f"  news data through {nc['aligned_through']}  |  "
                  f"recent {nc['recent_news_avg']}/day vs baseline "
                  f"{nc['baseline_news_avg']}/day "
                  f"({nc['news_change_percent']}%)  |  "
                  f"unique-domain ratio {nc.get('unique_domain_ratio')}")
            if h:
                dates = [d for d, _ in h["series"]]
                print(f"  timing: {wiki_aligned_summary(views, dates, nc['aligned_through'])}")

    # --- Approach A vs B ----------------------------------------------------
    print(f"\n{'=' * 70}\nAPPROACH COMPARISON (A: display only · B: +5 x value bonus, max +5)")
    rows = [
        (t.replace("_", " "), r["score"], r["news"].get("value") or 0.0, r["news"]["state"])
        for t, r in results.items() if r["score"] is not None
    ]
    print(f"{'topic':<34} {'A(score)':>8} {'B(score)':>8}  state")
    for title, score, value, state in sorted(rows, key=lambda x: -x[1]):
        bonus = round(5 * value)
        print(f"{title:<34} {score:>8} {score + bonus:>8}  {state}"
              + (f"  (+{bonus})" if bonus else ""))

    out = OUTPUT_DIR / "cross_source_eval.json"
    out.write_text(json.dumps(
        {t: {**r, "news": {k: str(v) if isinstance(v, date) else v
                           for k, v in r["news"].items()}}
         for t, r in results.items()}, indent=1, default=str))
    print(f"\nSaved → {out}\nPOC DONE")


if __name__ == "__main__":
    main()
