"""
Full experiment runner (ADR-0003).

For each selected era: load the cumulative block-count ladder into Neo4j and run
the query suite at each cut-off. Then build within-era comparisons (across block
counts) and cross-era comparisons (across eras at each cut-off).

Usage:
    python scripts/run_experiments.py                      # all eras in eras.py
    python scripts/run_experiments.py recent_2024          # one era
    python scripts/run_experiments.py recent_2024 defi_summer_2020

Requires BigQuery auth + GCP_PROJECT, and local Neo4j (see .env).
Outputs go to data/results/<era>/<n>/ and data/output/.
"""

import sys
from pathlib import Path

from ether.config import NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD
from ether.db.connection import Neo4JConnection
from ether.experiments.eras import ERAS, LADDER, era_by_name
from ether.experiments.runner import run_era_ladder
from ether.reporting.comparison import run_within_era, run_cross_era

BASE = str(Path(__file__).resolve().parents[1] / "data")


def main():
    names = sys.argv[1:] or [e.name for e in ERAS]
    eras = [era_by_name(n) for n in names]
    print(f"Running eras: {[e.name for e in eras]}")

    connection = Neo4JConnection(NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD)
    try:
        for era in eras:
            run_era_ladder(connection, era, BASE)
    finally:
        connection.close()

    # within-era comparisons (across the ladder)
    for era in eras:
        run_within_era(BASE, BASE, era.name)

    # cross-era comparisons (across eras at each cut-off) — needs >=2 eras
    if len(eras) >= 2:
        for n in LADDER:
            run_cross_era(BASE, BASE, [e.name for e in eras], n)

    print(f"Done. Results in {BASE}/results, comparisons in {BASE}/output")


if __name__ == "__main__":
    main()
