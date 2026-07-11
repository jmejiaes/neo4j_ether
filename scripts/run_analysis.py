"""
Cross-run analysis entry point.

Rebuilds comparison tables + charts from already-extracted per-run CSVs under
data/results/<era>/<block_count>/. No Neo4j/BigQuery needed — pure post-processing.
Produces within-era comparisons (across the ladder) and cross-era comparisons
(across eras at each cut-off).

Usage:
    python scripts/run_analysis.py            # all eras found under data/results/
"""

import os
from pathlib import Path

from ether.experiments.eras import LADDER
from ether.reporting.comparison import run_within_era, run_cross_era

BASE = str(Path(__file__).resolve().parents[1] / "data")


def main():
    results_root = os.path.join(BASE, "results")
    if not os.path.isdir(results_root):
        raise FileNotFoundError(f"No results directory: {results_root}")

    eras = sorted(d for d in os.listdir(results_root)
                  if os.path.isdir(os.path.join(results_root, d)))
    print(f"Eras found: {eras}")

    for era in eras:
        run_within_era(BASE, BASE, era)

    if len(eras) >= 2:
        for n in LADDER:
            run_cross_era(BASE, BASE, eras, n)

    print(f"Done. Comparisons in {BASE}/output")


if __name__ == "__main__":
    main()
