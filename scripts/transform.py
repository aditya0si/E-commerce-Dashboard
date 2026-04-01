import pandas as pd


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply basic cleaning and derived metrics."""
    cleaned = df.copy()
    cleaned.columns = [column.strip().lower() for column in cleaned.columns]

    if {"quantity", "unit_price"}.issubset(cleaned.columns):
        cleaned["revenue"] = cleaned["quantity"] * cleaned["unit_price"]

    return cleaned
