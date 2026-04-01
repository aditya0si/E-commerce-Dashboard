from pathlib import Path

import pandas as pd

from scripts.config import RAW_DIR


def extract_sales_data(file_name: str = "sales.csv") -> pd.DataFrame:
    """Read raw sales data from the raw data directory."""
    file_path = RAW_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing source file: {file_path}")
    return pd.read_csv(file_path)


if __name__ == "__main__":
    df = extract_sales_data()
    print(df.head())
