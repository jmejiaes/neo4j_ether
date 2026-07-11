"""Cross-run analysis (ADR-0003).

Reads per-run CSVs written by single_run.process_run under
    <base>/results/<era>/<block_count>/query_X/...
and produces two kinds of comparison, both as pivot tables + line charts:

- **within-era**: for one era, compare a metric across the block-count ladder
  (the paper's original axis). Output: <base>/output/<era>/.
- **cross-era**: for a fixed block count, compare across eras (the new axis).
  Output: <base>/output/cross_era_<count>/.

The two share one dimension-agnostic engine; the only difference is whether the
pivot dimension is block count or era.
"""

import os
import pandas as pd

from ether.reporting.io import save_csv_and_markdown
from ether.visualization.line_charts import plot_comparison_chart

# (query_number, subquery_number, value_column, y_label)
_RANKED = [
    (1, 1, "total_received", "Total ETH Received"),
    (1, 2, "total_sent", "Total ETH Sent"),
    (2, 1, "received_percentage", "% of Transactions Received"),
    (2, 2, "sent_percentage", "% of Transactions Sent"),
    (2, 3, "total_percentage", "% of transaction participations"),
]
_PAIR = [
    (5, 1, "transaction_count", "Number of Transactions"),
    (6, None, "total_value_sent", "Total ETH Sent"),
]
_STATS = [(4, 1), (4, 2)]


# --- CSV loading ------------------------------------------------------------

def _read_csv(run_path: str, q: int, sq: int | None) -> pd.DataFrame | None:
    filename = f"query_{q}_{sq}.csv" if sq is not None else f"query_{q}.csv"
    csv_path = os.path.join(run_path, f"query_{q}", filename)
    return pd.read_csv(csv_path) if os.path.exists(csv_path) else None


def _shorten(addr: str) -> str:
    return addr[:6] + "..." + addr[-6:]


def _build_pivot(combined, value_col, id_col, dim_col, order) -> pd.DataFrame:
    pivot = combined.pivot(index="rank", columns=dim_col, values=[id_col, value_col])
    pivot.columns = pd.MultiIndex.from_tuples([(c[1], c[0]) for c in pivot.columns])
    present = [o for o in order if o in pivot.columns.get_level_values(0)]
    return pivot.reindex(columns=present, level=0)


def _load_ranked(pairs, q, sq, value_col, dim_col, order):
    frames = []
    for label, run_path in pairs:
        df = _read_csv(run_path, q, sq)
        if df is None:
            continue
        df["rank"] = range(1, len(df) + 1)
        df[dim_col] = label
        frames.append(df)
    return _build_pivot(pd.concat(frames), value_col, "account", dim_col, order)


def _load_pair(pairs, q, sq, value_col, dim_col, order):
    frames = []
    for label, run_path in pairs:
        df = _read_csv(run_path, q, sq)
        if df is None:
            continue
        df["pair"] = df["sender"].apply(_shorten) + " → " + df["receiver"].apply(_shorten)
        df = df.drop(columns=["sender", "receiver"])
        df["rank"] = range(1, len(df) + 1)
        df[dim_col] = label
        frames.append(df)
    return _build_pivot(pd.concat(frames), value_col, "pair", dim_col, order)


def _load_stats(pairs, q, sq, dim_col, order):
    frames = []
    for label, run_path in pairs:
        df = _read_csv(run_path, q, sq)
        if df is None:
            continue
        df[dim_col] = label
        frames.append(df)
    combined = pd.concat(frames)
    combined[dim_col] = pd.Categorical(combined[dim_col], categories=order, ordered=True)
    return combined.sort_values(dim_col)


# --- the dimension-agnostic engine ------------------------------------------

def compare_over(pairs, output_dir, dim_col, legend_title, series_fmt):
    """Run all comparison queries over `pairs` = [(label, run_path), ...].

    `dim_col` is the pivot dimension ('blocks' or 'era'); `order` is the label
    ordering for columns/series.
    """
    os.makedirs(output_dir, exist_ok=True)
    order = [label for label, _ in pairs]

    def _out(q):
        p = os.path.join(output_dir, f"query_{q}")
        os.makedirs(p, exist_ok=True)
        return p

    for q, sq, value_col, y_label in _RANKED:
        pivot = _load_ranked(pairs, q, sq, value_col, dim_col, order)
        save_csv_and_markdown(pivot, _out(q), f"query_{q}_{sq}")
        plot_comparison_chart(pivot, value_col, y_label,
                              os.path.join(_out(q), f"query_{q}_{sq}.png"),
                              legend_title=legend_title, series_fmt=series_fmt)

    for q, sq, value_col, y_label in _PAIR:
        sq_label = sq if sq is not None else 1
        pivot = _load_pair(pairs, q, sq, value_col, dim_col, order)
        save_csv_and_markdown(pivot, _out(q), f"query_{q}_{sq_label}")
        plot_comparison_chart(pivot, value_col, y_label,
                              os.path.join(_out(q), f"query_{q}_{sq_label}.png"),
                              legend_title=legend_title, series_fmt=series_fmt)

    for q, sq in _STATS:
        df = _load_stats(pairs, q, sq, dim_col, order)
        save_csv_and_markdown(df, _out(q), f"query_{q}_{sq}")


# --- public entry points ----------------------------------------------------

def _count_dirs(era_results_dir: str):
    """[(block_count_str, path)] under an era's results dir, sorted numerically."""
    entries = [(d, os.path.join(era_results_dir, d)) for d in os.listdir(era_results_dir)
               if d.isdigit() and os.path.isdir(os.path.join(era_results_dir, d))]
    return sorted(entries, key=lambda e: int(e[0]))


def run_within_era(results_base: str, output_base: str, era_name: str):
    """Compare across the block-count ladder for one era."""
    era_results = os.path.join(results_base, "results", era_name)
    pairs = _count_dirs(era_results)
    if not pairs:
        return
    out = os.path.join(output_base, "output", era_name)
    compare_over(pairs, out, dim_col="blocks",
                 legend_title="Blocks", series_fmt=lambda s: f"{s} blocks")


def run_cross_era(results_base: str, output_base: str, era_order: list[str], block_count: int):
    """Compare across eras at a fixed block count (the new axis, ADR-0003)."""
    pairs = []
    for era in era_order:
        path = os.path.join(results_base, "results", era, str(block_count))
        if os.path.isdir(path):
            pairs.append((era, path))
    if len(pairs) < 2:
        return
    out = os.path.join(output_base, "output", f"cross_era_{block_count}")
    compare_over(pairs, out, dim_col="era",
                 legend_title="Era", series_fmt=lambda s: str(s))
