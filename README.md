# neo4j_ether

A Neo4j graph-database model for Ethereum transaction analytics — the blockchain
modeled as a **trajectory** of consecutive blocks, with accounts, external
transactions, and internal transactions as nodes. Companion code for the paper
*"Blockchain Trajectories in Graph Databases: A Neo4j-Based Model for Ethereum
Transaction Analytics."*

The manuscript is `docs/paper/paper_v2.md` (and `.docx`). This repository extends
the original study in two ways: it scales the experiment from 100 to **10,000
blocks** and replicates the analysis across **four eras** of Ethereum history
(2016, 2020, 2023, 2024). See `docs/CHANGELOG.md` for the full what-and-why and
`docs/adr/` for the formal decisions.

## Model

- **Block** `(number, time)` — linked head-to-tail by `PREVIOUS_BLOCK` (the
  trajectory backbone).
- **User** `(address, isContract)` — EOAs and contracts.
- **ExternalTransaction** / **InternalTransaction** — value transfers, related to
  users via `SENT_BY` / `RECEIVED_BY`, to blocks via `BELONGS_TO`, and to each other
  via `HAS_INTERNAL_TRANSACTION`.

## Layout

```
├── src/ether/            # the package
│   ├── config.py         # env-driven config (loads project-root .env)
│   ├── ingestion/        # data acquisition (BigQuery) + graph loading pipeline
│   ├── db/               # Neo4j connection, schema (write) & analytics (read) queries
│   ├── reporting/        # within-run and cross-run/cross-era reporting
│   ├── visualization/    # line & bar charts
│   └── experiments/      # era definitions + block-count ladder (see docs/adr/0003)
├── scripts/              # entry points (see Usage)
├── docs/
│   ├── adr/              # architecture decision records (0001–0008)
│   ├── paper/            # manuscript (paper_v2.md/.docx), figures, appendix tables
│   ├── CHANGELOG.md      # what changed vs. the original paper, and why
│   ├── glossary.md
│   └── roadmap.md
└── data/                 # gitignored: results/<era>/<block_count>/…, output/
```

## Setup

```bash
uv sync                                  # install deps into .venv
cp .env.example .env                     # then fill in values

# Neo4j Community locally (see docs/adr/0005 for why not Aura at scale).
# Memory tuned for 10k-block loads; the tx cap keeps a runaway query from OOM-ing
# the JVM (heap + pagecache must fit the Docker VM's memory).
docker run -d --name neo4j-ether -p 7474:7474 -p 7687:7687 \
  -v neo4j-ether-data:/data \
  -e NEO4J_AUTH=neo4j/<password> \
  -e NEO4J_server_memory_heap_max__size=4G \
  -e NEO4J_server_memory_pagecache_size=2G \
  -e NEO4J_db_memory_transaction_total_max=3G \
  neo4j:2026.01.3

# BigQuery is the primary data source (see docs/adr/0001):
gcloud auth application-default login    # + set GCP_PROJECT in .env
```

## Usage

```bash
# Load one block window into Neo4j (clears the DB first):
uv run python scripts/run_ingestion.py                  # canonical era, 100 blocks
uv run python scripts/run_ingestion.py recent_2024 1000 # named era, N blocks

# Full experiment: for each era, load the cumulative ladder
# {2,10,50,100,1000,10000} and run the query suite at each cut-off,
# then build within-era and cross-era comparisons:
uv run python scripts/run_experiments.py                # all eras in eras.py
uv run python scripts/run_experiments.py recent_2024    # one era

# Rebuild comparison tables + charts from existing CSVs (no DB/BigQuery needed):
uv run python scripts/run_analysis.py

# Regenerate the paper's Appendix A tables from the result CSVs:
uv run python scripts/gen_appendix_tables.py

# Print summary stats for whatever era is currently loaded (cross-era discussion):
uv run python scripts/dump_stats.py [label]
```

Outputs land under `data/results/<era>/<n>/` (per-run) and `data/output/`
(comparisons); both are gitignored and fully regenerable.

## Regenerating the paper

The manuscript source is `docs/paper/paper_v2.md`; the `.docx` and the Appendix A
tables are derived from it and from the result CSVs.

```bash
# Conceptual model diagrams fig1–3 (static schema; needs `brew install graphviz`):
uv run python scripts/gen_model_figures.py

# Result figures fig4–8 (from data/results/ CSVs + summary.json):
uv run python scripts/gen_paper_figures.py

# Appendix A tables (from data/results/ CSVs) -> docs/paper/appendix_tables.md,
# whose content is embedded into the manuscript's Appendix A:
uv run python scripts/gen_appendix_tables.py

# paper_v2.md -> paper_v2.docx, with a table of contents and the figures
# (figures/*.png) embedded. Run from docs/paper/ so the relative paths resolve.
# Requires pandoc (https://pandoc.org).
cd docs/paper && pandoc paper_v2.md -o paper_v2.docx --toc
```

The figures and tables are derived from `data/results/` (gitignored); run
`scripts/run_experiments.py` first if that directory is empty.

## Experiment design (ADR-0003)

Each **era** is a contiguous block window from a distinct period of Ethereum
history. Within every era the same cumulative block-count **ladder**
`{2, 10, 50, 100, 1000, 10000}` and the same 14 queries run; comparing across eras
is what surfaces structural evolution (WETH's emergence, the post-Merge rise in
internal-transaction complexity, ~20× densification).

**Multi-era is designed to be removable.** Eras are just entries in
`src/ether/experiments/eras.py`; `recent_2024` is the canonical original window. To
keep only that window, delete the other entries and skip the cross-era stage —
nothing else breaks. See `docs/CHANGELOG.md` §5 for the full reversibility matrix.

## Design decisions

See `docs/adr/` — BigQuery data source & partition pruning (0001, 0007), dropped
`balance` (0002), experiment design (0003), repo restructure (0004), Neo4j runtime &
batched writes (0005), unified transaction label (0006), participation-denominator
correction (0008). `docs/roadmap.md` has the ordered plan; `docs/glossary.md`
defines the domain terms.
