"""
Print summary stats for whatever era is currently loaded in Neo4j.

Run right after an era's ladder finishes (the graph then holds that era at its
top block count) to capture the numbers used in the cross-era discussion:
node/relationship counts, contract ratio, external/internal tx volume, and the
top-received accounts with their contract flag (to track WETH's role per era).

Usage:
    python scripts/dump_stats.py [label]     # label just tags the printout
"""

import sys
from ether.config import NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD
from ether.db.connection import Neo4JConnection

WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "(current graph)"
    c = Neo4JConnection(NEO4J_API_URI, NEO4J_API_USERNAME, NEO4J_API_PASSWORD)
    s = c.session

    def scalar(q):
        return s.run(q).single()[0]

    blocks = scalar("MATCH (b:Block) RETURN count(b)")
    ext = scalar("MATCH (t:ExternalTransaction) RETURN count(t)")
    internal = scalar("MATCH (i:InternalTransaction) RETURN count(i)")
    users = scalar("MATCH (u:User) RETURN count(u)")
    contracts = scalar("MATCH (u:User {iscontract:true}) RETURN count(u)")

    print(f"\n=== {label} ===")
    print(f"blocks={blocks}  external_tx={ext}  internal_tx={internal}  "
          f"users={users}  contracts={contracts}")
    if blocks:
        print(f"  external_tx/block = {ext/blocks:.1f}   internal/external = "
              f"{(internal/ext if ext else 0):.2f}   contract share = "
              f"{(contracts/users*100 if users else 0):.1f}%")

    print("top-10 received (account, ETH, isContract):")
    rows = s.run(
        "MATCH (u:User)-[:RECEIVED_BY]->(tx) "
        "WITH u, CASE WHEN tx:ExternalTransaction THEN tx.value ELSE tx.amount END AS v "
        "RETURN u.address AS a, u.iscontract AS c, round(sum(v),2) AS total "
        "ORDER BY total DESC LIMIT 10"
    )
    weth_rank = None
    for i, r in enumerate(rows, 1):
        tag = "contract" if r["c"] else "EOA"
        mark = "  <-- WETH" if r["a"] == WETH else ""
        if r["a"] == WETH:
            weth_rank = i
        print(f"  {i:2}. {r['a']}  {r['total']:>12}  {tag}{mark}")
    print(f"WETH in top-10 received: {'rank ' + str(weth_rank) if weth_rank else 'NO'}")
    c.close()


if __name__ == "__main__":
    main()
