import matplotlib.pyplot as plt
import pandas as pd


def plot_bar_chart(
    x: pd.Series,
    y: pd.Series,
    palette: list,
    title: str,
    x_label: str,
    y_label: str,
    output_path: str,
    block_count: int,
):
    # Truncate addresses for readability on the axis
    x = x.str[:6] + "..." + x.str[-6:]

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.barh(x, y, color=palette)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(f"{title} ({block_count} blocks)")

    for i, v in enumerate(y):
        ax.text(v + 0.1, i, str(round(v, 2)), va="center")

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
