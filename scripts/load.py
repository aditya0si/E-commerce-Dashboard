import pandas as pd
from sqlalchemy import create_engine

from scripts.config import DB_CONFIG


def get_connection_string() -> str:
    return (
        "postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def load_to_postgres(df: pd.DataFrame, table_name: str = "sales") -> None:
    """Load a DataFrame into PostgreSQL."""
    engine = create_engine(get_connection_string())
    df.to_sql(table_name, engine, if_exists="replace", index=False)
