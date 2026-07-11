"""
Regenerate the paper's conceptual model figures (fig1–fig3) with Graphviz.

These are static schema diagrams (they do not depend on experiment data), kept
consistent with the model in Section 3 of the paper:
  - Account nodes carry only {address, isContract} — no `balance` (ADR-0002).
  - Block nodes carry {blockNumber, dateCreation}.
  - Transaction nodes carry {transactionHash, isInternalTransaction, value,
    sequenceId, (parentTransactionHash)}.

  fig1  External and internal transactions (conceptual flow)
  fig2  Structure of blocks and external transactions (node/edge schema)
  fig3  Relationship between external and internal transactions

Requires the Graphviz `dot` binary (`brew install graphviz`). Outputs high-DPI
PNGs to docs/paper/figures/.

Usage:
    uv run python scripts/gen_model_figures.py
"""

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "docs" / "paper" / "figures"

# Pastel palette matching the original diagrams.
BLOCK = "#cfe0f8"      # blue
TX = "#fce3c8"         # orange
ACC = "#efefef"        # gray
BLOCK_B = "#7fa8dd"
TX_B = "#e0a15f"
ACC_B = "#b0b0b0"
EDGE = "#333333"


def _propmap(pairs: list[tuple[str, str]]) -> str:
    """Format {'k': v, ...} as a centered multi-line node label for DOT."""
    inner = ",\\n".join(f"'{k}': {v}" for k, v in pairs)
    return "{\\n" + inner + "\\n}"


def _render(dot: str, out: Path):
    if not shutil.which("dot"):
        raise RuntimeError("Graphviz `dot` not found. Install with `brew install graphviz`.")
    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=200", "-o", str(out)],
        input=dot.encode(), check=True,
    )
    print(f"wrote {out.relative_to(ROOT)}")


# --- Figure 1 — external/internal transactions (conceptual flow) -------------

def fig1():
    dot = f'''
digraph fig1 {{
  rankdir=LR; bgcolor=white; fontname="Helvetica";
  node [fontname="Helvetica", fontsize=13];
  edge [color="#4c78b0", penwidth=2.2, arrowsize=1.1];

  eoa [label="EOA\\n(Sender)", shape=box, style="rounded", color="#888888", fontsize=13];

  subgraph cluster_sc {{
    label="Smart contract"; labelloc=t; fontsize=15; color=black; penwidth=2; style=solid;
    ext  [label="External\\ntransaction", shape=box, color="#444444"];
    code [label="contract\\ncode", shape=box, style="rounded", color="#444444"];
    intl [label="Internal\\ntransactions", shape=box, color="#444444"];
    ext -> code -> intl;
  }}

  eoa -> ext;
  recv [label="Receiver (EOA or Smart contract)", shape=box, style="rounded", color="#888888"];
  code -> recv [minlen=2];
}}
'''
    _render(dot, FIGDIR / "fig1_model_transactions.png")


# --- Figure 2 — blocks + external transaction schema -------------------------

def fig2():
    b1 = _propmap([("blockNumber", "20019929"),
                   ("dateCreation", "'04-06-2024 17:24:11 +UTC'")])
    b2 = _propmap([("blockNumber", "20019930"),
                   ("dateCreation", "'04-06-2024 17:24:50 +UTC'")])
    tx = _propmap([("transactionHash", "'0xf19d...9dfbd'"),
                   ("isInternalTransaction", "False"),
                   ("value", "0"), ("sequenceId", "''")])
    snd = _propmap([("address", "'0x51877...d304'"), ("isContract", "False")])
    rcv = _propmap([("address", "'0x3fC9...b7FAD'"), ("isContract", "True")])

    dot = f'''
digraph fig2 {{
  bgcolor=white; fontname="Helvetica"; rankdir=TB; nodesep=0.6; ranksep=1.0;
  node [fontname="Helvetica", fontsize=11, style=filled, penwidth=1.4];
  edge [color="{EDGE}", fontname="Helvetica", fontsize=11, penwidth=1.3];

  subgraph cluster_legend {{
    label="Legend"; fontsize=12; color="#cccccc"; style=rounded;
    lb [label="Block", shape=box, fillcolor="{BLOCK}", color="{BLOCK_B}"];
    lt [label="Transaction", shape=box, fillcolor="{TX}", color="{TX_B}"];
    la [label="Account", shape=box, fillcolor="{ACC}", color="{ACC_B}"];
    lb -> lt -> la [style=invis];
  }}

  b1 [label="{b1}", shape=circle, fillcolor="{BLOCK}", color="{BLOCK_B}"];
  tx [label="{tx}", shape=circle, fillcolor="{TX}", color="{TX_B}"];
  b2 [label="{b2}", shape=circle, fillcolor="{BLOCK}", color="{BLOCK_B}"];
  snd [label="{snd}", shape=circle, fillcolor="{ACC}", color="{ACC_B}"];
  rcv [label="{rcv}", shape=circle, fillcolor="{ACC}", color="{ACC_B}"];

  b2 -> b1 [label="previous block"];
  tx -> b1 [label="recorded in"];
  tx -> snd [label="sent by"];
  tx -> rcv [label="received by"];

  {{ rank=same; snd; tx; rcv; }}
}}
'''
    _render(dot, FIGDIR / "fig2_model_block_external.png")


# --- Figure 3 — external/internal relationship schema ------------------------

def fig3():
    b = _propmap([("blockNumber", "20019929"),
                  ("dateCreation", "'04-06-2024 17:24:11 +UTC'")])
    tx = _propmap([("transactionHash", "'0xf19d...9dfbd'"),
                   ("isInternalTransaction", "False"),
                   ("value", "0"), ("sequenceId", "''")])
    it1 = _propmap([("isInternalTransaction", "True"), ("value", "0"), ("sequenceId", "1")])
    it2 = _propmap([("isInternalTransaction", "True"), ("value", "0.27085"), ("sequenceId", "2")])
    a1 = _propmap([("address", "'0x3fC...b7FAD'"), ("isContract", "True")])
    a2 = _propmap([("address", "'0x5187...63d304'"), ("isContract", "False")])
    a3 = _propmap([("address", "'0xC02aa...756Cc2'"), ("isContract", "True")])
    a4 = _propmap([("address", "'0x3fC...b7FAD'"), ("isContract", "True")])

    dot = f'''
digraph fig3 {{
  bgcolor=white; fontname="Helvetica"; rankdir=TB; nodesep=0.5; ranksep=1.0;
  node [fontname="Helvetica", fontsize=11, style=filled, penwidth=1.4];
  edge [color="{EDGE}", fontname="Helvetica", fontsize=11, penwidth=1.3];

  b  [label="{b}", shape=circle, fillcolor="{BLOCK}", color="{BLOCK_B}"];
  tx [label="{tx}", shape=circle, fillcolor="{TX}", color="{TX_B}"];
  it1 [label="{it1}", shape=circle, fillcolor="{TX}", color="{TX_B}"];
  it2 [label="{it2}", shape=circle, fillcolor="{TX}", color="{TX_B}"];
  a1 [label="{a1}", shape=circle, fillcolor="{ACC}", color="{ACC_B}"];
  a2 [label="{a2}", shape=circle, fillcolor="{ACC}", color="{ACC_B}"];
  a3 [label="{a3}", shape=circle, fillcolor="{ACC}", color="{ACC_B}"];
  a4 [label="{a4}", shape=circle, fillcolor="{ACC}", color="{ACC_B}"];

  tx -> b   [label="recorded in"];
  tx -> it1 [label="internal transaction"];
  tx -> it2 [label="internal transaction"];
  it1 -> a1 [label="internal sent by"];
  it1 -> a2 [label="internal received by"];
  it2 -> a3 [label="internal sent by"];
  it2 -> a4 [label="internal received by"];

  {{ rank=same; it1; b; it2; }}
}}
'''
    _render(dot, FIGDIR / "fig3_model_internal.png")


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig1()
    fig2()
    fig3()


if __name__ == "__main__":
    main()
