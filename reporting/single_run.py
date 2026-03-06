"""
Queries Neo4j for a completed ingestion run, saves per-query CSVs and bar charts.

Expected call after load_blocks() completes:
    process_run(connection, result_dir, block_count)
"""

import os
import pandas as pd
import seaborn as sns

from src.db.connection import Neo4JConnection
from src.reporting.io import save_csv
from src.visualization.bar_charts import plot_bar_chart


_RED = sns.color_palette("Reds", n_colors=10)[::-1]
_GREEN = sns.color_palette("Greens", n_colors=10)[::-1]
_BLUE = sns.color_palette("Blues", n_colors=10)[::-1]


def process_run(connection: Neo4JConnection, result_dir: str, block_count: int):
    _query_1(connection, result_dir, block_count)
    _query_2(connection, result_dir, block_count)
    _query_4(connection, result_dir)
    _query_5(connection, result_dir)
    _query_6(connection, result_dir)


# --- helpers ---

def _run(connection: Neo4JConnection, method_name: str) -> pd.DataFrame:
    result = getattr(connection, method_name)()
    return pd.DataFrame(result, columns=result.keys())


def _bar(df, x_col, y_col, palette, title, x_label, y_label, result_dir, subpath, block_count):
    save_csv(df, os.path.join(result_dir, os.path.dirname(subpath)), os.path.basename(subpath))
    plot_bar_chart(
        x=df[x_col],
        y=df[y_col],
        palette=palette,
        title=title,
        x_label=x_label,
        y_label=y_label,
        output_path=os.path.join(result_dir, f"{subpath}.png"),
        block_count=block_count,
    )


# --- query groups ---

def _query_1(connection, result_dir, block_count):
    os.makedirs(os.path.join(result_dir, "query_1"), exist_ok=True)

    df = _run(connection, "get_accounts_most_received_eth")
    _bar(df, "account", "total_received", _GREEN,
         "Top 10 Accounts by Total Received Ether", "Total Received Ether", "Account",
         result_dir, "query_1/query_1_1", block_count)

    df = _run(connection, "get_accounts_most_sent_eth")
    _bar(df, "account", "total_sent", _RED,
         "Top 10 Accounts by Total Sent Ether", "Total Sent Ether", "Account",
         result_dir, "query_1/query_1_2", block_count)


def _query_2(connection, result_dir, block_count):
    os.makedirs(os.path.join(result_dir, "query_2"), exist_ok=True)

    df = _run(connection, "get_most_active_accounts_received_percentage")
    _bar(df, "account", "received_percentage", _GREEN,
         "Top 10 Most Active Accounts by Received Transactions", "Account",
         "Received Transaction %", result_dir, "query_2/query_2_1", block_count)

    df = _run(connection, "get_most_active_accounts_sent_percentage")
    _bar(df, "account", "sent_percentage", _RED,
         "Top 10 Most Active Accounts by Sent Transactions", "Account",
         "Sent Transaction %", result_dir, "query_2/query_2_2", block_count)

    df = _run(connection, "get_most_active_accounts_total_percentage")
    _bar(df, "account", "total_percentage", _BLUE,
         "Top 10 Most Active Accounts by Total Transactions", "Account",
         "Total Transaction %", result_dir, "query_2/query_2_3", block_count)


def _query_4(connection, result_dir):
    os.makedirs(os.path.join(result_dir, "query_4"), exist_ok=True)
    save_csv(_run(connection, "get_transaction_statistics"),
             os.path.join(result_dir, "query_4"), "query_4_1")
    save_csv(_run(connection, "get_internal_transaction_statistics"),
             os.path.join(result_dir, "query_4"), "query_4_2")


def _query_5(connection, result_dir):
    os.makedirs(os.path.join(result_dir, "query_5"), exist_ok=True)
    for method, filename in [
        ("get_top_account_pairs_external",    "query_5_1"),
        ("get_top_account_pairs_internal",    "query_5_2"),
        ("get_top_pairs_user_to_contract",    "query_5_3"),
        ("get_top_pairs_contract_to_user",    "query_5_4"),
        ("get_top_pairs_user_to_user",        "query_5_5"),
    ]:
        save_csv(_run(connection, method), os.path.join(result_dir, "query_5"), filename)


def _query_6(connection, result_dir):
    os.makedirs(os.path.join(result_dir, "query_6"), exist_ok=True)
    save_csv(_run(connection, "get_top_account_pairs_by_value_sent"),
             os.path.join(result_dir, "query_6"), "query_6")
