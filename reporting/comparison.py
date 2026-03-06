"""
Cross-run analysis: reads per-run CSVs from multiple results folders and produces
comparison pivot tables and line charts across different block counts.

Expects results_dir to contain subdirectories named like:
    results_for_2_(20512878_20512879)/
    results_for_10_(20512880_20512887)/
    ...
"""

import os
import pandas as pd

from src.reporting.io import save_csv_and_markdown
from src.visualization.line_charts import plot_comparison_chart


def run_comparison(results_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    _ranked_query(results_dir, output_dir, 1, 1, "total_received",
                  "Total ETH Received", title="Total Received ETH by Rank Across Blocks")
    _ranked_query(results_dir, output_dir, 1, 2, "total_sent",
                  "Total ETH Sent", title="Total Sent ETH by Rank Across Blocks")

    _ranked_query(results_dir, output_dir, 2, 1, "received_percentage",
                  "% of Transactions Received", title="Received Transaction % by Rank Across Blocks")
    _ranked_query(results_dir, output_dir, 2, 2, "sent_percentage",
                  "% of Transactions Sent", title="Sent Transaction % by Rank Across Blocks")
    _ranked_query(results_dir, output_dir, 2, 3, "total_percentage",
                  "% of Total Transactions", title="Total Transaction % by Rank Across Blocks")

    _statistics_query(results_dir, output_dir, 4, 1)
    _statistics_query(results_dir, output_dir, 4, 2)

    _pair_query(results_dir, output_dir, 5, 1, "transaction_count",
                "Number of Transactions", title="Transaction Count by Pair Rank Across Blocks")
    _pair_query(results_dir, output_dir, 6, None, "total_value_sent",
                "Total ETH Sent", title="Total ETH Sent by Pair Rank Across Blocks")


# --- loaders ---

def _block_count_from_folder(folder_name: str) -> str:
    return folder_name.split("_for_")[1].split("_")[0]


def _iter_run_folders(results_dir: str):
    for folder in sorted(os.listdir(results_dir)):
        path = os.path.join(results_dir, folder)
        if os.path.isdir(path) and "_for_" in folder:
            yield folder, path, _block_count_from_folder(folder)


def _read_csv(run_path: str, query_number: int, subquery_number: int | None) -> pd.DataFrame | None:
    if subquery_number is not None:
        filename = f"query_{query_number}_{subquery_number}.csv"
    else:
        filename = f"query_{query_number}.csv"
    csv_path = os.path.join(run_path, f"query_{query_number}", filename)
    return pd.read_csv(csv_path) if os.path.exists(csv_path) else None


def _build_pivot(combined: pd.DataFrame, value_column: str, id_column: str = "account") -> pd.DataFrame:
    pivot = combined.pivot(index="rank", columns="blocks", values=[id_column, value_column])
    pivot.columns = pd.MultiIndex.from_tuples([(col[1], col[0]) for col in pivot.columns])
    return pivot.sort_index(axis=1, level=0, key=lambda x: x.astype(int))


def _load_ranked_query(results_dir: str, query_number: int, subquery_number: int, value_column: str) -> pd.DataFrame:
    frames = []
    for _, run_path, blocks in _iter_run_folders(results_dir):
        df = _read_csv(run_path, query_number, subquery_number)
        if df is None:
            continue
        df["rank"] = range(1, len(df) + 1)
        df["blocks"] = blocks
        frames.append(df)
    return _build_pivot(pd.concat(frames), value_column)


def _load_pair_query(results_dir: str, query_number: int, subquery_number: int | None, value_column: str) -> pd.DataFrame:
    def shorten(addr: str) -> str:
        return addr[:6] + "..." + addr[-6:]

    frames = []
    for _, run_path, blocks in _iter_run_folders(results_dir):
        df = _read_csv(run_path, query_number, subquery_number)
        if df is None:
            continue
        df["pair"] = df["sender"].apply(shorten) + " → " + df["receiver"].apply(shorten)
        df = df.drop(columns=["sender", "receiver"])
        df["rank"] = range(1, len(df) + 1)
        df["blocks"] = blocks
        frames.append(df)
    return _build_pivot(pd.concat(frames), value_column, id_column="pair")


def _load_statistics_query(results_dir: str, query_number: int, subquery_number: int) -> pd.DataFrame:
    frames = []
    for _, run_path, blocks in _iter_run_folders(results_dir):
        df = _read_csv(run_path, query_number, subquery_number)
        if df is None:
            continue
        df["blocks"] = int(blocks)
        frames.append(df)
    return pd.concat(frames).sort_values("blocks")


# --- output helpers ---

def _output_dir(output_dir: str, query_number: int) -> str:
    path = os.path.join(output_dir, f"query_{query_number}")
    os.makedirs(path, exist_ok=True)
    return path


def _chart_path(output_dir: str, query_number: int, subquery_number: int) -> str:
    return os.path.join(_output_dir(output_dir, query_number), f"query_{query_number}_{subquery_number}.png")


# --- query runners ---

def _ranked_query(results_dir, output_dir, q, sq, value_col, y_label, title=None):
    pivot = _load_ranked_query(results_dir, q, sq, value_col)
    save_csv_and_markdown(pivot, _output_dir(output_dir, q), f"query_{q}_{sq}")
    plot_comparison_chart(pivot, value_col, y_label, _chart_path(output_dir, q, sq), title=title)


def _pair_query(results_dir, output_dir, q, sq, value_col, y_label, title=None):
    sq_label = sq if sq is not None else 1
    pivot = _load_pair_query(results_dir, q, sq, value_col)
    save_csv_and_markdown(pivot, _output_dir(output_dir, q), f"query_{q}_{sq_label}")
    plot_comparison_chart(pivot, value_col, y_label, _chart_path(output_dir, q, sq_label), title=title)


def _statistics_query(results_dir, output_dir, q, sq):
    df = _load_statistics_query(results_dir, q, sq)
    save_csv_and_markdown(df, _output_dir(output_dir, q), f"query_{q}_{sq}")
