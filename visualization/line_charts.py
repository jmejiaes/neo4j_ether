import matplotlib.pyplot as plt
import pandas as pd


def plot_comparison_chart(
    pivot: pd.DataFrame,
    value_column: str,
    y_label: str,
    output_path: str,
    title: str | None = None,
):
    """Line chart comparing a metric across different block counts.

    `pivot` must have a MultiIndex column (block_count, field_name), sorted by block_count.
    """
    block_counts = pivot.columns.get_level_values(0).unique()
    ranks = pivot.index

    fig, ax = plt.subplots(figsize=(12, 6))
    for block in block_counts:
        ax.plot(ranks, pivot[(block, value_column)], marker="o", label=f"{block} blocks")

    resolved_title = title or f"{' '.join(value_column.split('_')).title()} by Rank Across Blocks"
    ax.set_title(resolved_title)
    ax.set_xlabel("Rank")
    ax.set_ylabel(y_label)
    ax.legend(title="Blocks")
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
