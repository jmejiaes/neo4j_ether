"""
Regenerate the paper's figures (fig4–fig8) from the result artifacts under
`data/results/`. Run after an experiment so the CSVs/summary.json exist.

Figures:
  fig4  within-2024, top-10 by total ETH received, across the block-count ladder
  fig5  within-2024, top-10 by transaction-participation %, across the ladder
  fig6  cross-era volume: external tx/block (left) + internal/external ratio (right)
  fig7  cross-era, top-10 by participation %, at 10,000-block windows
  fig8  cross-era, top-10 by total ETH received, at 10,000-block windows

fig4/5/7/8 are rank-vs-value line charts (one line per series); fig6 is a paired
bar chart from each era's summary.json. Outputs overwrite docs/paper/figures/*.png.

Usage:
    uv run python scripts/gen_paper_figures.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ether.experiments.eras import LADDER

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data" / "results"
FIGDIR = ROOT / "docs" / "paper" / "figures"

CANON = "recent_2024"          # within-era figures use the canonical 2024 window
TOP = max(LADDER)              # cross-era figures use the top (10,000-block) window
N = 10                         # top-N accounts per ranking

# Era display metadata. Cross-era *line* charts (fig7/8) order series
# alphabetically by name (matplotlib default color cycle then matches the
# committed figures); the fig6 bar chart orders eras chronologically.
ERA_META = {
    "early_2016":       {"year": "2016", "phase": "pre-DeFi",     "start": 2_000_000},
    "defi_summer_2020": {"year": "2020", "phase": "DeFi Summer",  "start": 10_700_000},
    "post_merge_2023":  {"year": "2023", "phase": "post-Merge",   "start": 17_000_000},
    "recent_2024":      {"year": "2024", "phase": "post-Dencun",  "start": 20_512_878},
}


def _csv(era: str, n: int, rel: str) -> pd.DataFrame | None:
    p = RESULTS / era / str(n) / rel
    return pd.read_csv(p) if p.exists() else None


def _line_chart(series, value_col, y_label, out, legend_title, series_fmt):
    """Rank-vs-value line chart, one line per (label, dataframe) in `series`."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for label, df in series:
        if df is None or df.empty:
            continue
        d = df.head(N).reset_index(drop=True)
        ax.plot(range(1, len(d) + 1), d[value_col], marker="o", label=series_fmt(label))
    ax.set_xlabel("Rank")
    ax.set_ylabel(y_label)
    ax.legend(title=legend_title)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def within_era_figures():
    # fig4 — top received across the ladder
    series = [(n, _csv(CANON, n, "query_1/query_1_1.csv")) for n in LADDER]
    _line_chart(series, "total_received", "Total ETH Received",
                FIGDIR / "fig4_within2024_received.png",
                "Blocks", lambda n: f"{n} blocks")

    # fig5 — participation % across the ladder
    series = [(n, _csv(CANON, n, "query_2/query_2_3.csv")) for n in LADDER]
    _line_chart(series, "total_percentage", "% of transaction participations",
                FIGDIR / "fig5_within2024_participation.png",
                "Blocks", lambda n: f"{n} blocks")


def cross_era_line_figures():
    eras = sorted(ERA_META)  # alphabetical — matches the committed figures' colors

    # fig7 — participation % across eras at the top window
    series = [(e, _csv(e, TOP, "query_2/query_2_3.csv")) for e in eras]
    _line_chart(series, "total_percentage", "% of transaction participations",
                FIGDIR / "fig7_crossera_participation.png",
                "Era", lambda e: e)

    # fig8 — top received across eras at the top window
    series = [(e, _csv(e, TOP, "query_1/query_1_1.csv")) for e in eras]
    _line_chart(series, "total_received", "Total ETH Received",
                FIGDIR / "fig8_crossera_received.png",
                "Era", lambda e: e)


def cross_era_volume_figure():
    """fig6 — external tx/block and internal/external ratio, per era (chronological)."""
    eras = sorted(ERA_META, key=lambda e: ERA_META[e]["start"])
    labels, tx_per_block, ratio = [], [], []
    for e in eras:
        p = RESULTS / e / "summary.json"
        if not p.exists():
            continue
        s = json.loads(p.read_text())
        m = ERA_META[e]
        labels.append(f"{m['year']}\n({m['phase']})")
        tx_per_block.append(s["external_tx"] / s["blocks"])
        ratio.append(s["internal_tx"] / s["external_tx"])

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(14, 6))

    axl.bar(labels, tx_per_block, color="#4c72b0")
    axl.set_title("External transactions per block")
    axl.set_ylabel("external tx / block")
    for i, v in enumerate(tx_per_block):
        axl.text(i, v, f"{v:.1f}", ha="center", va="bottom")

    axr.bar(labels, ratio, color="#55a868")
    axr.set_title("Internal-to-external transaction ratio")
    axr.set_ylabel("internal / external")
    for i, v in enumerate(ratio):
        axr.text(i, v, f"{v:.2f}", ha="center", va="bottom")

    fig.tight_layout()
    out = FIGDIR / "fig6_cross_era_volume.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def main():
    if not RESULTS.is_dir():
        raise FileNotFoundError(
            f"No results at {RESULTS}. Run scripts/run_experiments.py first."
        )
    FIGDIR.mkdir(parents=True, exist_ok=True)
    within_era_figures()
    cross_era_volume_figure()
    cross_era_line_figures()


if __name__ == "__main__":
    main()
