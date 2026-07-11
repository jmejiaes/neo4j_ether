# Glossary

Domain and project terms used across the paper, the code, and these ADRs.
Terms are kept aligned between the paper's model and the code's schema.

## Blockchain domain

- **Block** — A collection of validated transactions with metadata (`blockNumber`
  / height, timestamp). The temporal backbone of the model; consecutive blocks
  form the "trajectory."
- **External transaction** — A user-initiated action from an Externally Owned
  Account (EOA), recorded directly in a block, identified by a `transactionHash`.
  In the code this is the `:Transaction` node label (paper calls it
  `ExternalTransaction` — see the label mismatch note below).
- **Internal transaction** — A value transfer or contract call triggered *during*
  execution of an external transaction (a "message call"). Identified by its
  parent `transactionHash` + a `sequenceId`. In BigQuery these are rows in the
  `traces` table.
- **EOA (Externally Owned Account)** — An account controlled by a user's private
  key, not by code. `isContract = false`.
- **Smart contract account** — An account controlled by deployed code.
  `isContract = true`. Detected in BigQuery via the `contracts` table / trace
  types (replaces Etherscan `eth_getCode`).
- **WETH (Wrapped Ether)** — Contract `0xc02aaa39...756cc2` implementing ERC-20
  wrapping of ETH. Appears as a dominant intermediary in the paper's results.
- **Trajectory (in this work)** — Not a spatial path: an ordered sequence of
  consecutive blocks defining temporal progression, each block a trajectory
  point anchoring its transactions.
- **Era / section** — (project term) A contiguous block window drawn from a
  distinct period of Ethereum's history, used to compare behavioral patterns
  across time. See the experiment-design ADR.

## Model attributes

- **value** — ETH amount transferred by an external transaction.
- **amount** — ETH amount transferred by an internal transaction.
- **isContract / iscontract** — Boolean; account is a contract. (Property key is
  `iscontract` in the Neo4j schema.)
- **balance** — DROPPED (see ADR-0002); previously current balance, unused by any
  query.

## Pipeline / infrastructure

- **BigQuery** — Google's data warehouse; `bigquery-public-data.crypto_ethereum`
  is the primary source (ADR-0001).
- **Cumulative batches** — The paper evaluates queries over nested ranges
  (2, 10, 50, 100 blocks) from a single start block.

## Label unification (resolved — ADR-0006)

The paper's Cypher used `ExternalTransaction`; the code used `:Transaction`.
Resolved by ADR-0006: standardize on **`ExternalTransaction`** in the code so the
manuscript's printed queries run as written. External amount = `value`, internal
amount = `amount`, in both paper and code.
