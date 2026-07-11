"""Load a block window from BigQuery into Neo4j (ADR-0001, ADR-0005).

One `load_blocks(connection, start, end)` call fetches the whole window from
BigQuery in a handful of queries and writes it to Neo4j in batched UNWINDs —
replacing the old per-block, per-transaction Etherscan loop (see legacy
`etherscan.py`) that ran at ~4 min/block.
"""

from ether.ingestion import bigquery as bq
from ether.db.connection import Neo4JConnection


def load_blocks(connection: Neo4JConnection, initial_block: int, final_block: int):
    connection.create_constraints()

    # 0. Window time bounds — drive partition pruning on the big tables (ADR-0007)
    ts0, ts1 = bq.block_time_bounds(initial_block, final_block)
    print(f"  window time: {ts0} .. {ts1} UTC")

    # 1. Blocks + temporal backbone (PREVIOUS_BLOCK chain)
    blocks = bq.fetch_blocks(initial_block, final_block)
    print(f"  blocks: {len(blocks)}")
    connection.create_blocks(blocks)
    # Link every block to its predecessor. The edge query MATCHes the previous
    # block, so it is a no-op when the predecessor isn't loaded (the era's first
    # block); when loading cumulative increments, this links across increment
    # boundaries to the block already loaded in a prior step.
    connection.create_previous_block_edges([
        {"number": b["number"], "previous": b["number"] - 1} for b in blocks
    ])

    # 2. Fetch transactions, traces, and contract flags (partition-pruned by ts)
    txs = bq.fetch_transactions(initial_block, final_block, ts0, ts1)
    internal = bq.fetch_internal_transactions(initial_block, final_block, ts0, ts1)
    contract_addrs = bq.fetch_contract_addresses(initial_block, final_block, ts0, ts1)
    print(f"  external txs: {len(txs)}  internal txs: {len(internal)}  "
          f"contracts: {len(contract_addrs)}")

    # 3. Users = all distinct participants across external + internal txs
    addresses: set[str] = set()
    for t in txs:
        addresses.add(t["sender"]); addresses.add(t["receiver"])
    for it in internal:
        addresses.add(it["sender"]); addresses.add(it["receiver"])
    connection.create_users([
        {"address": a, "iscontract": a in contract_addrs} for a in addresses
    ])
    print(f"  users: {len(addresses)}")

    # 4. External transactions + edges
    connection.create_external_transactions([
        {"transactionhash": t["transactionhash"],
         "blocknumber": t["blocknumber"], "value": t["value"]}
        for t in txs
    ])
    connection.create_recorded_in_edges([
        {"transactionhash": t["transactionhash"], "blocknumber": t["blocknumber"]}
        for t in txs
    ])
    connection.create_sent_by_edges([
        {"address": t["sender"], "transactionhash": t["transactionhash"]} for t in txs
    ])
    connection.create_received_by_edges([
        {"address": t["receiver"], "transactionhash": t["transactionhash"]} for t in txs
    ])

    # 5. Internal transactions + edges
    connection.create_internal_transactions([
        {"parenttransactionhash": it["parenttransactionhash"],
         "sequence_id": it["sequence_id"], "amount": it["amount"]}
        for it in internal
    ])
    connection.create_internal_sent_by_edges([
        {"address": it["sender"], "parenttransactionhash": it["parenttransactionhash"],
         "sequence_id": it["sequence_id"]}
        for it in internal
    ])
    connection.create_internal_received_by_edges([
        {"address": it["receiver"], "parenttransactionhash": it["parenttransactionhash"],
         "sequence_id": it["sequence_id"]}
        for it in internal
    ])
