# Roadmap — broaden the experimentation + refactor

Derived from ADR-0001…0006. Ordered by dependency.

## Locked decisions (see ADRs)
- **Source:** BigQuery `crypto_ethereum`, not Etherscan (ADR-0001).
- **Balance:** dropped — unused by queries (ADR-0002).
- **Design:** cumulative ladder {2, 10, 50, 100, 1,000, 10,000} across 3–4
  removable eras; single-era (Aug-2024, block 20,512,878) is the canonical,
  deletable-to default (ADR-0003).
- **Repo:** adopt `jmejiaes/neo4j_ether`, src-layout `src/ether/`, `_legacy/`
  archive, `.env.example` (ADR-0004).
- **Neo4j:** local Community via Docker; batched `UNWIND` writes; indexes first
  (ADR-0005).
- **Label:** external tx node = `ExternalTransaction` (ADR-0006).
- **Deliverable:** machinery + regenerated figures/tables + drafted Methodology &
  Experiments sections (markdown).

## Status (2026-07-06)
- [x] Step 1 — repo restructure (committed)
- [x] Step 2 — local Neo4j Community 2026.01.3 via Docker (verified)
- [x] Step 3 — BigQuery ingestion + batched writes + label unification
      (validated on real data; reproduces paper's Appendix A)
- [x] Step 4 — label unification (folded into Step 3, ADR-0006)
- [x] Step 5 — era-aware reporting + experiment runner (validated)
- [x] Step 6 — full ladder × 4 eras loaded; within-era + cross-era comparisons built
- [x] Step 7 — manuscript sections drafted (methodology, within-era + cross-era
      results with real numbers, abstract) under docs/paper/

Also fixed along the way: ADR-0007 (BigQuery partition pruning, ~3000× less data);
query_2_3 cartesian blowup (78min→2s); clear-database OOM (two-phase batched delete).

## Results (10,000-block windows)
| Era | ext txs | int txs | tx/block | int/ext | WETH rank |
|-----|--------:|--------:|---------:|--------:|:----------|
| 2016 |    80,796 |  16,133 |   8.1 | 0.20 | absent |
| 2020 | 1,878,933 | 385,042 | 187.9 | 0.20 | 2 (Uniswap router #1) |
| 2023 | 1,301,965 | 739,050 | 130.2 | 0.57 | 2 |
| 2024 | 1,530,170 | 849,527 | 153.0 | 0.56 | 1 |

Raw outputs (gitignored, regenerable): data/results/<era>/<n>/, data/output/.

## Execution order

1. **Repo restructure (foundation).** Relocate `src/.git` → root; rename package
   `src` → `ether`; create `scripts/`, `docs/`, `data/`; move superseded
   artifacts to gitignored `_legacy/`; add `.gitignore` + `.env.example`; fix
   imports. Commit.
2. **Local Neo4j.** Docker Neo4j Community (pin version); point `NEO4J_URI` at
   `bolt://localhost`; create constraints/indexes.
3. **Ingestion rewrite.** `ingestion/bigquery.py` (blocks, txs, traces,
   is_contract); drop balance; `experiments/eras.py` era config; batched UNWIND
   write path in `connection.py` + `pipeline.py`.
4. **Label unification** (ADR-0006) — folded into the db-layer touch in step 3.
5. **Reporting era-axis.** Generalize `reporting/comparison.py` to
   (era × block_count); per-era output dirs `data/results/<era>/<n>/`; separate
   cross-era comparison stage (skippable → removability).
6. **Run experiments.** Pin & verify era block heights; load each era's 10k
   window once; query at cumulative cut-offs; generate CSV/PNG/markdown tables.
7. **Draft manuscript sections.** Methodology (BigQuery, local Neo4j, dropped
   balance, eras) + Experiments (new scale + cross-era findings) + abstract tweak,
   as markdown for the author to paste into the `.docx`.

## Open items to verify during implementation
- Exact block heights for eras 2–4 (2016 / DeFi-summer 2020 / post-Merge 2023).
- BigQuery `is_contract` detection method (contracts table vs trace types).
- Neo4j Community version to pin for reproducibility.
- Whether early eras (2016) have enough internal-tx volume to be interesting at
  the top of the ladder — report tx-per-block per era regardless.
