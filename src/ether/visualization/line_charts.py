import matplotlib.pyplot as plt
import pandas as pd


def plot_comparison_chart(
    pivot: pd.DataFrame,
    value_column: str,
    y_label: str,
    output_path: str,
    title: str | None = None,
    legend_title: str = "Blocks",
    series_fmt=lambda s: f"{s} blocks",
):
    """Line chart comparing a metric across a dimension (block count or era).

    `pivot` must have a MultiIndex column (series, field_name), sorted by series.
    The dimension is generic: pass `legend_title`/`series_fmt` to label series as
    block counts (default) or eras.
    """
    series_values = pivot.columns.get_level_values(0).unique()
    ranks = pivot.index

    fig, ax = plt.subplots(figsize=(12, 6))
    for s in series_values:
        ax.plot(ranks, pivot[(s, value_column)], marker="o", label=series_fmt(s))

    ax.set_title(title)
    ax.set_xlabel("Rank")
    ax.set_ylabel(y_label)
    ax.legend(title=legend_title)
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
