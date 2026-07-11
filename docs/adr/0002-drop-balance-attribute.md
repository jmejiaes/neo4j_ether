# ADR-0002: Drop the `balance` account attribute

- Status: Accepted
- Date: 2026-07-06

## Context

The paper's account model defines `NaccountDt = (address, balance, isContract)`.
The pipeline fetches `balance` for every account via Etherscan using
`tag: latest`, which is roughly half of all API calls.

Two problems:
1. **No query uses it.** All 14 analytics queries in
   `src/db/analytics_queries.py` read `value`/`amount`, counts, and
   `iscontract` — none read `balance`.
2. **It is semantically wrong for historical analysis.** `tag: latest` returns
   the account's balance *today*, not at the analyzed block height, so it does
   not describe the trajectory window being studied.

BigQuery does not expose current balance directly either (see ADR-0001).

## Decision

Remove `balance` from ingestion and from the account node. Keep `is_contract`,
which queries do use. Document the removal as a deliberate simplification in the
paper's model section (or reintroduce a *block-time* balance later if a query
ever needs it).

## Consequences

- Eliminates the largest single class of per-address lookups.
- Account model in the paper narrows to `(address, isContract)`; the model
  section must be updated to reflect this (or justify the omission).
- If future work wants balance, it should be block-time balance derived from
  value flows, not `latest`.
- **Block reward is dropped for the same reason.** The old pipeline stored
  `block_reward` on Block nodes, but no query reads it and it is not cheaply
  available from BigQuery. Block nodes now carry only `number` + `time`, matching
  the paper's model §3.1 `(blockNumber, dateCreation)`.
