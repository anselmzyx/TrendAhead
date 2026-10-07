"""Phase 5 evaluation: compare scoring formulations on the real Phase 4
candidate histories, check weight sensitivity, and print the V1 ranking.

Needs cached histories (run collect_histories.py first — zero extra API
requests after that).  Run:  python3 pipeline/evaluate_scoring.py
"""

from __future__ import annotations

import json
from pathlib import Path

import scoring
from scoring import score_series

OUTPUT_DIR = Path(__file__).parent / "output"


def load_histories() -> dict[str, dict]:
    paths = sorted(OUTPUT_DIR.glob("histories_*.json"))
    if not paths:
        raise SystemExit("No cached histories — run collect_histories.py first.")
    data = json.loads(paths[-1].read_text())
    print(f"Loaded {len(data['histories'])} histories from {paths[-1].name}\n")
    return data["histories"]


# --- Alternative formulations (same components, different composition) ----


def formula_f1(c: dict) -> float:
    """CHOSEN SHAPE: additive core x sqrt(volume) gate x quality damp."""
    core = 0.35 * c["acceleration"] + 0.25 * c["anomaly"] + 0.40 * c["persistence"]
    return 100 * core * c["volume"] ** 0.5 * (0.25 + 0.75 * c["spike_quality"])


def formula_f2(c: dict) -> float:
    """Volume as an ADDITIVE component instead of a gate."""
    core = (
        0.30 * c["acceleration"]
        + 0.20 * c["anomaly"]
        + 0.30 * c["persistence"]
        + 0.20 * c["volume"]
    )
    return 100 * core * (0.25 + 0.75 * c["spike_quality"])


def formula_f3(c: dict) -> float:
    """Geometric mean core: any weak component drags everything down."""
    eps = 1e-6
    core = (
        max(c["acceleration"], eps)
        * max(c["anomaly"], eps)
        * max(c["persistence"], eps)
    ) ** (1 / 3)
    return 100 * core * c["volume"] ** 0.5 * (0.25 + 0.75 * c["spike_quality"])


def main() -> None:
    histories = load_histories()
    rows = []
    skipped = []
    for title, h in histories.items():
        views = [v for _, v in h["series"]]
        try:
            r = score_series(views)
        except ValueError as e:
            skipped.append((title, str(e)))
            continue
        rows.append({"title": title, "sample": h["sample"], **r})
    if skipped:
        print("Skipped (invalid history):")
        for t, e in skipped:
            print(f"  {t}: {e}")

    # --- Formula comparison ----------------------------------------------
    print("=== FORMULA COMPARISON (top 15 each; scores rounded) ===\n")
    variants = {"F1 gate(chosen)": formula_f1, "F2 additive-vol": formula_f2, "F3 geometric": formula_f3}
    tops = {}
    for name, fn in variants.items():
        ranked = sorted(rows, key=lambda r: fn(r["components"]), reverse=True)
        tops[name] = [r["title"] for r in ranked[:15]]
        print(f"--- {name} ---")
        for i, r in enumerate(ranked[:15], 1):
            print(f"  {i:>2}. {r['title'].replace('_',' ')[:40]:<40} {fn(r['components']):5.1f}")
        print()

    # --- Sensitivity check -------------------------------------------------
    print("=== SENSITIVITY: F1 weight perturbations, top-10 overlap ===")
    base_weights = (0.35, 0.25, 0.40)
    perturbed = [(0.40, 0.25, 0.35), (0.30, 0.30, 0.40), (0.35, 0.30, 0.35), (0.30, 0.25, 0.45)]

    def rank_with(weights):
        wa, wb, wc = weights

        def f(c):
            core = wa * c["acceleration"] + wb * c["anomaly"] + wc * c["persistence"]
            return core * c["volume"] ** 0.5 * (0.25 + 0.75 * c["spike_quality"])

        return [r["title"] for r in sorted(rows, key=lambda r: f(r["components"]), reverse=True)[:10]]

    base_top = rank_with(base_weights)
    for w in perturbed:
        other = rank_with(w)
        overlap = len(set(base_top) & set(other))
        same_leader = base_top[0] == other[0]
        print(f"  weights {w}: top-10 overlap {overlap}/10, same #1: {same_leader}")

    # --- Final V1 ranking ---------------------------------------------------
    ranked = sorted(rows, key=lambda r: r["score"], reverse=True)
    print("\n=================== TRENDAHEAD SCORE V1 — EXPERIMENTAL ===================")
    print(f"{'#':>2} {'Topic':<34} {'Score':>5} {'Status':<22} {'Recent':>8} "
          f"{'Basln':>7} {'Grw':>5} {'Pers':>4} {'Qual':>4}")
    print("-" * 103)
    for i, r in enumerate(ranked[:20], 1):
        c, st = r["components"], r["stats"]
        mark = "*" if r["sample"] == "improver" else " "
        title = r["title"].replace("_", " ")
        title = title if len(title) <= 33 else title[:30] + "..."
        print(f"{i:>2} {title:<33}{mark} {r['score']:>5} {r['status']:<22} "
              f"{st['recent_avg']:>8,} {st['baseline_avg']:>7,} {st['growth_ratio']:>5.1f} "
              f"{c['persistence']:>4.2f} {c['spike_quality']:>4.2f}")
    print("-" * 103)
    print("* = evaluation-only 'improver' sample (not from Phase 4 discovery)")

    out = OUTPUT_DIR / "scores_v1.json"
    out.write_text(json.dumps(
        {"note": "TrendAhead Score V1 — EXPERIMENTAL", "ranked": ranked}, indent=1))
    print(f"\nSaved full scored output → {out}")


if __name__ == "__main__":
    main()
