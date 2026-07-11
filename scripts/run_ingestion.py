"""
Ingestion entry point.

Clears the local Neo4j database and loads a block window from BigQuery (ADR-0001)
into Neo4j using batched writes (ADR-0005). Analysis is a separate step
(scripts/run_analysis.py) so this can load large windows without re-querying.

Usage:
    python scripts/run_ingestion.py                    # canonical era, 100 blocks
    python scripts/run_ingestion.py recent_2024 1000   # named era, 1000 blocks
    python scripts/run_ingestion.py recent_2024 10000  # full ladder top

Requires BigQuery auth (`gcloud auth application-default login`) and GCP_PROJECT
set in .env. Neo4j target comes from .env (bolt://localhost by default).
"""

import sys

from ether.config import NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD
from ether.db.connection import Neo4JConnection
from ether.ingestion.pipeline import load_blocks
from ether.experiments.eras import CANONICAL_ERA, era_by_name


def main():
    era = era_by_name(sys.argv[1]) if len(sys.argv) > 1 else CANONICAL_ERA
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    initial_block = era.start_block
    final_block = era.start_block + count - 1

    print(f"Era '{era.name}': loading blocks {initial_block}–{final_block} "
          f"({count} blocks) — {era.description}")

    connection = Neo4JConnection(NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD)
    connection.clear_database()
    print("Database cleared.")

    load_blocks(connection, initial_block, final_block)

    block_count = connection.get_block_count().single()["block_count"]
    connection.close()
    print(f"Done. {block_count} blocks loaded into Neo4j.")


if __name__ == "__main__":
    main()
