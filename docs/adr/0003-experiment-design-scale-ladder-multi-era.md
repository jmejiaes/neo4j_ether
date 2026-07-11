# ADR-0003: Experiment design — scale ladder across removable eras

- Status: Accepted
- Date: 2026-07-06

## Context

The paper's stated main limitation is that 100 blocks is a small sample. The goal
is to (a) scale to ≥1,000 blocks and (b) optionally compare across several eras
("sections") of Ethereum's history. The model, schema, and the 14 Cypher queries
do not need to change — only the *scope of data* and the *comparison/discussion*
layer do.

A hard constraint from the author: multi-era must be **easy to remove**. If the
advisor wants to keep only the original 2024 era worked on this year, deleting the
other eras must be trivial and must not disturb the single-era results.

## Decision

**Design:** run the paper's *cumulative block-count ladder* within each era, and
run that same ladder across multiple eras.

- **Eras are declarative config.** A list of named windows, each = (era name,
  start block, ladder of cumulative cut-offs). Entry #1 is the canonical original
  window (start block 20,512,878, Aug-12-2024).
- **Block count is fixed per ladder step, not wall-clock time.** Matches the
  block-trajectory model. Each window's time span is *reported*, since block
  times differ across eras (pre-Merge ~13s variable, post-Merge exactly 12s).
- **Same 14 queries** run against every era's graph — no per-era queries.
- **Outputs partitioned per era.** `results/<era>/<block_count>/...`. The
  cross-era comparison is a **separate reporting stage** that reads per-era
  outputs and can be skipped entirely.

**Removability contract:**
- Removing an era = delete its config entry (+ optionally its output dir).
- Removing multi-era entirely = keep only era #1 and don't run the cross-era
  stage. Single-era results and the paper's single-era spine are untouched.
- The paper is structured so single-era results are the spine and cross-era is a
  clearly separable subsection/appendix.

**Era set (working default, 4 eras — may be trimmed to 3):**
1. Recent / post-Dencun — block 20,512,878 (Aug 2024). *Canonical, original.*
2. Early / pre-DeFi — ~2016 (~block 2M). Sparse, few internal txs, no WETH.
3. DeFi Summer — ~Aug 2020 (~block 10.7M). WETH/Uniswap surge, PoW gas wars.
4. Post-Merge PoS — ~2023 (~block 17M). 12s blocks, MEV.

Exact era-2/3/4 block heights to be pinned during implementation and verified.

## Consequences

- New finding available: structural *evolution* across eras (e.g. the birth of
  WETH as dominant intermediary; rise of internal-tx complexity; densification).
- Cross-era comparability is per-block-count, not per-transaction-count — this is
  itself reportable (tx-per-block grows across eras).
- Reporting layer gains one axis (era × block-count); comparison code generalizes
  rather than duplicates.
- Ladder top-end (1k vs 10k vs 100k) drives Neo4j sizing and runtime — see the
  next ADR / open question.
