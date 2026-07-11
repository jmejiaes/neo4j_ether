"""
Regenerate the paper's conceptual model figures (fig1–fig3).

These are static schema diagrams (they do not depend on experiment data), drawn
with fixed coordinates to match the layout of the original manuscript figures, and
kept consistent with the model in Section 3 of the paper:
  - Account nodes carry only {address, isContract} — no `balance` (ADR-0002).
  - Block nodes carry {blockNumber, dateCreation}.
  - Transaction nodes carry {transactionHash, isInternalTransaction, value,
    sequenceId, (parentTransactionHash)}.

  fig1  External and internal transactions (conceptual flow)
  fig2  Structure of blocks and external transactions (node/edge schema)
  fig3  Relationship between external and internal transactions

Pure matplotlib (no system dependencies). Outputs high-DPI PNGs to
docs/paper/figures/.

Usage:
    uv run python scripts/gen_model_figures.py
"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, FancyArrow, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "docs" / "paper" / "figures"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]

# Pastel palette matching the original diagrams.
BLOCK_FILL, BLOCK_EDGE = "#c9def6", "#6f9fdc"
TX_FILL, TX_EDGE = "#fce4c6", "#e6a44b"
ACC_FILL, ACC_EDGE = "#efefef", "#bcbcbc"
FLOW = "#4c78b0"
TXT = "#333333"


def _circle(ax, cx, cy, r, fill, edge, text):
    ax.add_patch(Circle((cx, cy), r, facecolor=fill, edgecolor=edge,
                        linewidth=1.6, zorder=2))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=8.5,
            color=TXT, zorder=3, linespacing=1.3)


def _edge(ax, cf, rf, ct, rt, label=None, lw=1.4, color=TXT, ldx=0.0, ldy=0.0):
    dx, dy = ct[0] - cf[0], ct[1] - cf[1]
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    start = (cf[0] + ux * rf, cf[1] + uy * rf)
    end = (ct[0] - ux * rt, ct[1] - uy * rt)
    ax.annotate("", xy=end, xytext=start, zorder=1.6,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=18))
    if label:
        mx = (start[0] + end[0]) / 2 + ldx
        my = (start[1] + end[1]) / 2 + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=9.5,
                color="black", zorder=4,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))


def _dashed_box(ax, x0, y0, x1, y1):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                 boxstyle="round,pad=0,rounding_size=0.6", fill=False,
                 edgecolor="#444444", linewidth=1.8, linestyle=(0, (6, 4)),
                 zorder=1))


def _legend(ax, x, ys):
    for (cy, fill, edge, label) in ys:
        ax.add_patch(FancyBboxPatch((x - 1.3, cy - 0.55), 2.6, 1.1,
                     boxstyle="round,pad=0,rounding_size=0.25",
                     facecolor=fill, edgecolor=edge, linewidth=1.5, zorder=2))
        ax.text(x, cy, label, ha="center", va="center", fontsize=11,
                color=TXT, zorder=3)


def _save(fig, name):
    out = FIGDIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


# --- property-map labels (no `balance`; keys spaced like the original) -------

B1 = "{\n'blockNumber' : 20019929,\n'dateCreation' : '04-06-2024 17:24:11\n+UTC'\n}"
B2 = "{\n'blockNumber' : 20019930,\n'dateCreation' : '04-06-2024 17:24:50\n+UTC'\n}"
TX = ("{\n'transactionHash' : '0xf19d...9dfbd',\n'isInternalTransaction' : False,"
      "\n'value' : 0,\n'sequenceId' : ''\n}")
IT1 = "{\n'isInternalTransaction' : True,\n'value' : 0,\n'sequenceId' : 1\n}"
IT2 = "{\n'isInternalTransaction' : True,\n'value' : 0.27085,\n'sequenceId' : 2\n}"


def _acct(addr, is_contract):
    return f"{{\n'address' : '{addr}',\n'isContract' : {is_contract}\n}}"


# --- icon helpers (outline person / document) + block arrow ------------------

def _person(ax, cx, cy, s=1.0, lw=2.0):
    """Outline person icon: circular head + a shoulders arc."""
    ax.add_patch(Circle((cx, cy + 0.55 * s), 0.34 * s, fill=False,
                        edgecolor="black", linewidth=lw, zorder=3))
    ax.add_patch(Arc((cx, cy - 0.30 * s), 1.5 * s, 1.7 * s, angle=0,
                    theta1=25, theta2=155, edgecolor="black", linewidth=lw, zorder=3))


def _document(ax, cx, cy, w=1.1, h=1.5, lw=1.8):
    """Outline document/contract icon: page + text lines + a '— ×' footer."""
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, facecolor="white",
                          edgecolor="black", linewidth=lw, zorder=3))
    for yy in (cy + 0.28 * h, cy + 0.10 * h, cy - 0.08 * h):
        ax.plot([cx - 0.28 * w, cx + 0.28 * w], [yy, yy], color="black", lw=1.2, zorder=4)
    ax.plot([cx - 0.28 * w, cx - 0.05 * w], [cy - 0.26 * h, cy - 0.26 * h],
            color="black", lw=1.2, zorder=4)
    ax.text(cx + 0.13 * w, cy - 0.26 * h, "×", ha="center", va="center",
            fontsize=8, zorder=4)


def _barrow(ax, x, y, dx, dy):
    """Solid blue block arrow (rectangular shaft + triangular head)."""
    ax.add_patch(FancyArrow(x, y, dx, dy, width=0.16, head_width=0.5, head_length=0.45,
                 length_includes_head=True, facecolor=FLOW, edgecolor=FLOW, zorder=2))


# --- Figure 1 — external/internal transactions (conceptual flow) -------------

def fig1():
    fig, ax = plt.subplots(figsize=(15, 7.5))
    ax.set_xlim(0, 20); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")

    def box(cx, cy, w, h, label, lw=1.6, fs=13):
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fill=False,
                     edgecolor="black", linewidth=lw, zorder=2))
        ax.text(cx, cy, label, ha="center", va="center", fontsize=fs, zorder=3)

    # EOA (person icon + label)
    _person(ax, 2.3, 6.5)
    ax.text(2.3, 5.25, "EOA\n(Sender)", ha="center", va="center", fontsize=13, zorder=3)

    # Smart-contract container
    ax.add_patch(Rectangle((5.3, 5.0), 11.3, 3.2, fill=False, edgecolor="black",
                 linewidth=2.0, zorder=1.5))
    ax.text(10.95, 7.7, "Smart contract", ha="center", va="center", fontsize=15, zorder=3)
    box(7.2, 6.3, 2.7, 1.6, "External\ntransaction")
    _document(ax, 10.5, 6.3, w=1.1, h=1.5)
    box(13.9, 6.3, 2.7, 1.6, "Internal\ntransactions")

    # horizontal block arrows through the flow
    _barrow(ax, 3.35, 6.3, 2.4, 0)      # EOA -> External transaction
    _barrow(ax, 8.65, 6.3, 1.2, 0)      # External transaction -> contract code
    _barrow(ax, 11.15, 6.3, 1.35, 0)    # contract code -> Internal transactions

    # downward block arrow from the smart contract to the receiver
    _barrow(ax, 10.95, 4.9, 0, -1.5)

    # Receiver box (person + document icons), label below
    ax.add_patch(Rectangle((8.7, 1.4), 4.5, 2.0, fill=False, edgecolor="black",
                 linewidth=2.0, zorder=2))
    _person(ax, 10.0, 2.35, s=0.8)
    _document(ax, 12.0, 2.4, w=0.9, h=1.25)
    ax.text(10.95, 0.8, "Receiver (EOA or Smart contract)", ha="center",
            va="center", fontsize=13, zorder=3)

    _save(fig, "fig1_model_transactions.png")


# --- Figure 2 — blocks + external transaction schema -------------------------

def fig2():
    fig, ax = plt.subplots(figsize=(15, 8.3))
    ax.set_xlim(0, 20); ax.set_ylim(0, 11); ax.set_aspect("equal"); ax.axis("off")

    _legend(ax, 2.6, [(9.2, BLOCK_FILL, BLOCK_EDGE, "Block"),
                      (7.6, TX_FILL, TX_EDGE, "Transaction"),
                      (6.0, ACC_FILL, ACC_EDGE, "Account")])

    rB, rT, rA = 2.0, 2.0, 2.0
    b1 = (9.3, 8.0); b2 = (16.7, 8.0); tx = (9.3, 2.6)
    snd = (3.1, 2.6); rcv = (16.7, 2.6)

    _dashed_box(ax, 6.9, 0.4, 11.7, 10.3)
    _circle(ax, *b1, rB, BLOCK_FILL, BLOCK_EDGE, B1)
    _circle(ax, *b2, rB, BLOCK_FILL, BLOCK_EDGE, B2)
    _circle(ax, *tx, rT, TX_FILL, TX_EDGE, TX)
    _circle(ax, *snd, rA, ACC_FILL, ACC_EDGE, _acct("0x51877...d304", "False"))
    _circle(ax, *rcv, rA, ACC_FILL, ACC_EDGE, _acct("0x3fC9...b7FAD", "True"))

    _edge(ax, b2, rB, b1, rB, "previous block", ldy=0.35)
    _edge(ax, tx, rT, b1, rB, "recorded in", ldx=0.9)
    _edge(ax, tx, rT, snd, rA, "sent by", ldy=0.35)
    _edge(ax, tx, rT, rcv, rA, "received by", ldy=0.35)
    _save(fig, "fig2_model_block_external.png")


# --- Figure 3 — external/internal relationship schema ------------------------

def fig3():
    fig, ax = plt.subplots(figsize=(16, 8.8))
    ax.set_xlim(0, 20); ax.set_ylim(0, 11); ax.set_aspect("equal"); ax.axis("off")

    rI, rT, rB, rA = 1.9, 1.9, 1.7, 1.7
    it1 = (4.5, 8.0); b = (9.8, 8.7); it2 = (15.1, 8.0); tx = (9.8, 4.0)
    a1 = (2.6, 1.2); a2 = (6.4, 1.2); a3 = (13.2, 1.2); a4 = (17.0, 1.2)

    _dashed_box(ax, 7.6, 1.9, 12.0, 10.7)
    _circle(ax, *b, rB, BLOCK_FILL, BLOCK_EDGE, B1)
    _circle(ax, *tx, rT, TX_FILL, TX_EDGE, TX)
    _circle(ax, *it1, rI, TX_FILL, TX_EDGE, IT1)
    _circle(ax, *it2, rI, TX_FILL, TX_EDGE, IT2)
    _circle(ax, *a1, rA, ACC_FILL, ACC_EDGE, _acct("0x3fC...b7FAD", "True"))
    _circle(ax, *a2, rA, ACC_FILL, ACC_EDGE, _acct("0x5187...63d304", "False"))
    _circle(ax, *a3, rA, ACC_FILL, ACC_EDGE, _acct("0xC02aa...756Cc2", "True"))
    _circle(ax, *a4, rA, ACC_FILL, ACC_EDGE, _acct("0x3fC...b7FAD", "True"))

    _edge(ax, tx, rT, b, rB, "recorded in", ldx=0.9)
    _edge(ax, tx, rT, it1, rI, "internal transaction", ldx=-0.2, ldy=-0.4)
    _edge(ax, tx, rT, it2, rI, "internal transaction", ldx=0.2, ldy=-0.4)
    _edge(ax, it1, rI, a1, rA, "internal sent by", ldx=-0.6)
    _edge(ax, it1, rI, a2, rA, "internal received by", ldx=0.7)
    _edge(ax, it2, rI, a3, rA, "internal sent by", ldx=-0.7)
    _edge(ax, it2, rI, a4, rA, "internal received by", ldx=0.6)
    _save(fig, "fig3_model_internal.png")


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig1()
    fig2()
    fig3()


if __name__ == "__main__":
    main()
