import os
import pandas as pd


def create_results_directory(block_count: int, initial_block: int, final_block: int) -> str:
    path = f"results_for_{block_count}_({initial_block}_{final_block})"
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
