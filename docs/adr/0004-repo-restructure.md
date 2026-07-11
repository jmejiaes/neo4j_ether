# ADR-0004: Repository restructure — one home repo, src-layout package

- Status: Accepted
- Date: 2026-07-06

## Context

The working folder `Desktop/ether` has **no git commits**. The real code lives in
a *nested* repo at `src/.git` → `github.com/jmejiaes/neo4j_ether.git`, which tracks
only the package (`config.py`, `db/`, `ingestion/`, `reporting/`, `visualization/`)
— not the entry points, notebooks, paper, or data. Two `.env` files with live
secrets sit untracked. The outer folder is littered with superseded artifacts
(3 old notebooks — `cop.ipynb` and `ordenado.ipynb` are byte-identical —,
`comunes/`, `ether_results/`, `ether_data/`, a stray `results_for_<Result...>`
dir, `ether_results.zip`) and reference PDFs.

## Decision

**Adopt `jmejiaes/neo4j_ether` as the single home repo, preserving its history.**
Relocate its `.git` to the project root and restructure to:

```
neo4j_ether/
├── README.md  pyproject.toml  .env.example  .gitignore
├── docs/{adr/, glossary.md, paper/}
├── src/ether/{config.py, ingestion/, db/, reporting/, visualization/, experiments/eras.py}
├── scripts/{run_ingestion.py, run_analysis.py}   # were main.py / analyze.py
└── data/    # gitignored: results/<era>/<block_count>/…, raw/
```

Key moves:
- **Rename package `src` → `ether`** (matches `pyproject.toml` name); update all
  `from src.…` imports to `from ether.…`.
- **Secrets:** never commit `.env`; add `.env.example` with the 4 keys
  (`API_KEY`, `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`). Gitignore `.env`.
- **`.gitignore`** adds: `.env`, `data/`, `_legacy/`, `*.pdf`, `__pycache__/`,
  `.DS_Store`, `.venv`.
- **Superseded artifacts → gitignored `_legacy/`** (ADR: archive, not delete —
  reversible, keeps old outputs on disk, out of the clean tree).
- **Paper:** manuscript `.docx` under `docs/paper/`; heavy reference PDFs
  gitignored (kept locally, not pushed).

## Consequences

- One versioned repo covering code + docs + paper; the remote URL is unchanged.
- Import path churn (`src.` → `ether.`) — mechanical, one-time.
- History preserved via `.git` relocation (file moves tracked as renames).
- Removing multi-era later (ADR-0003) stays a config + `data/<era>` deletion.
