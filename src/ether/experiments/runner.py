"""Run one era's cumulative block-count ladder (ADR-0003).

Loads the era's blocks incrementally — 2, then +8 to reach 10, then +40 to reach
50, ... — so the graph *accumulates* and the 10k window is loaded only once
(not reloaded per ladder step). After reaching each cut-off, the full query suite
runs and its outputs are written under data/results/<era>/<n>/.
"""

import json
import os

from ether.experiments.eras import LADDER
from ether.ingestion.pipeline import load_blocks
from ether.reporting.single_run import process_run
from ether.reporting.io import era_result_dir


def run_era_ladder(connection, era, results_base: str, ladder=LADDER):
    connection.clear_database()
    connection.create_constraints()

    loaded_to = era.start_block - 1
    for n in ladder:
        target = era.start_block + n - 1
        print(f"[{era.name}] -> cumulative {n} blocks (loading {loaded_to + 1}..{target})")
        load_blocks(connection, loaded_to + 1, target)
        loaded_to = target

        block_count = connection.get_block_count().single()["block_count"]
        result_dir = era_result_dir(results_base, era.name, n)
        process_run(connection, result_dir, block_count)
        print(f"[{era.name}] {n} blocks done ({block_count} in graph) -> {result_dir}")

    capture_era_summary(connection, era, results_base)


def capture_era_summary(connection, era, results_base: str):
    """Write data/results/<era>/summary.json with graph-wide counts at the top
    cut-off (the graph holds this era until the next run clears it). Used for the
    cross-era discussion (densification, internal-tx growth, WETH's role)."""
    s = connection.session

    def scalar(q):
        return s.run(q).single()[0]

    summary = {
        "era": era.name,
        "start_block": era.start_block,
        "blocks": scalar("MATCH (b:Block) RETURN count(b)"),
        "external_tx": scalar("MATCH (t:ExternalTransaction) RETURN count(t)"),
        "internal_tx": scalar("MATCH (i:InternalTransaction) RETURN count(i)"),
        "users": scalar("MATCH (u:User) RETURN count(u)"),
        "contracts": scalar("MATCH (u:User {iscontract:true}) RETURN count(u)"),
    }
    summary["top_received"] = [
        {"address": r["a"], "is_contract": r["c"], "eth": round(r["v"], 2)}
        for r in s.run(
            "MATCH (u:User)-[:RECEIVED_BY]->(tx) "
            "WITH u, CASE WHEN tx:ExternalTransaction THEN tx.value ELSE tx.amount END AS val "
            "RETURN u.address AS a, u.iscontract AS c, sum(val) AS v "
            "ORDER BY v DESC LIMIT 10"
        )
    ]
    path = os.path.join(results_base, "results", era.name, "summary.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[{era.name}] summary -> {path}")
