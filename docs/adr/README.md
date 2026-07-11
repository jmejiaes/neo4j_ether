# Architecture Decision Records

Decisions behind the paper-enhancement work, in order.

| ADR | Decision |
|-----|----------|
| [0001](0001-data-source-bigquery.md) | Use BigQuery `crypto_ethereum` as the primary data source (not Etherscan) |
| [0002](0002-drop-balance-attribute.md) | Drop the unused `balance` attribute (and block reward) |
| [0003](0003-experiment-design-scale-ladder-multi-era.md) | Scale ladder {2,10,50,100,1k,10k} across removable eras |
| [0004](0004-repo-restructure.md) | One home repo, `src/ether/` src-layout |
| [0005](0005-neo4j-runtime-and-write-path.md) | Local Neo4j Community + batched UNWIND writes |
| [0006](0006-unify-transaction-label.md) | Unify external-tx node label to `ExternalTransaction` |
| [0007](0007-bigquery-partition-pruning.md) | Prune BigQuery partitions by `block_timestamp` (~3000× less data) |
| [0008](0008-correct-participation-denominator.md) | Correct Query 4.2.3 denominator (participations, not all nodes) — fixes a false "concentration sharpens" trend |

See also `../roadmap.md` (ordered plan + status) and `../glossary.md`.
