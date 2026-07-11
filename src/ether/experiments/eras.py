"""Era definitions — the "sections" of the blockchain we sample (ADR-0003).

An **era** is a contiguous block window drawn from a distinct period of Ethereum
history. Within each era we run the same cumulative-count ladder and the same 14
queries; comparing across eras is what surfaces structural evolution (e.g. the
birth of WETH as a dominant intermediary, the rise of internal-tx complexity).

Removability (per ADR-0003): eras are just entries in ERAS. To keep only the
original 2024 window your advisor worked on, delete/comment the other entries and
skip the cross-era reporting stage — nothing else changes. ERAS[0] is canonical.

Block heights were verified against real block timestamps (via `verify_era_dates`
in ingestion/bigquery.py); the era dates below are confirmed.
"""

from dataclasses import dataclass

# Cumulative cut-offs, shared by every era. The first four preserve continuity
# with the published paper; 1_000 and 10_000 are the new scale points.
LADDER = [2, 10, 50, 100, 1_000, 10_000]


@dataclass(frozen=True)
class Era:
    name: str          # stable slug, used in output paths: data/results/<name>/<n>/
    start_block: int   # first block of the window
    description: str   # human-facing label for figures/tables

    @property
    def top(self) -> int:
        """Highest cut-off in the ladder (window size actually loaded)."""
        return max(LADDER)

    @property
    def end_block(self) -> int:
        """Last block loaded for this era (start + top - 1)."""
        return self.start_block + self.top - 1


# --- The eras. ERAS[0] is the canonical/original window (do not remove). ---------
ERAS: list[Era] = [
    Era(
        name="recent_2024",
        start_block=20_512_878,   # Aug-12-2024 13:38:23 UTC — the paper's original window
        description="Post-Dencun (Aug 2024) — original canonical window",
    ),
    # --- Additional eras below are removable (ADR-0003). ---
    Era(
        name="early_2016",
        start_block=2_000_000,    # Aug-02-2016 (verified) — pre-DeFi, sparse, no WETH
        description="Pre-DeFi (~2016) — sparse activity, few internal txs",
    ),
    Era(
        name="defi_summer_2020",
        start_block=10_700_000,   # Aug-20-2020 (verified) — WETH/Uniswap surge, PoW gas wars
        description="DeFi Summer (~Aug 2020) — WETH/Uniswap surge",
    ),
    Era(
        name="post_merge_2023",
        start_block=17_000_000,   # Apr-07-2023 (verified) — 12s blocks, MEV, staking
        description="Post-Merge PoS (~2023) — 12s blocks, MEV",
    ),
]

CANONICAL_ERA = ERAS[0]


def era_by_name(name: str) -> Era:
    for e in ERAS:
        if e.name == name:
            return e
    raise KeyError(f"No era named {name!r}. Known: {[e.name for e in ERAS]}")
