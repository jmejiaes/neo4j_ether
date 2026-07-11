import os
import pandas as pd


def era_result_dir(base_dir: str, era_name: str, block_count: int) -> str:
    """Per-run output dir: <base_dir>/results/<era_name>/<block_count>/ (ADR-0003).

    Partitioning by era keeps runs separable — deleting an era = deleting its
    directory, with no effect on other eras' results.
    """
    path = os.path.join(base_dir, "results", era_name, str(block_count))
    os.makedirs(path, exist_ok=True)
    return path


def save_csv(df: pd.DataFrame, directory: str, filename: str):
    """Save `df` to `<directory>/<filename>.csv`."""
    os.makedirs(directory, exist_ok=True)
    df.to_csv(os.path.join(directory, f"{filename}.csv"), index=False)


def save_csv_and_markdown(df: pd.DataFrame, directory: str, filename: str):
    """Save `df` as both CSV and Markdown to `<directory>/`."""
    os.makedirs(directory, exist_ok=True)
    base = os.path.join(directory, filename)
    df.to_csv(f"{base}.csv", index=False)
    with open(f"{base}.md", "w") as f:
        f.write(df.to_markdown())
