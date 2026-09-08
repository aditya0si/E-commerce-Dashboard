import pandas as pd

from scripts.config import DB_CONFIG


def get_connection_string() -> str:
    return (
        "postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def load_to_postgres(df: pd.DataFrame, table_name: str = "sales") -> None:
    """Load a DataFrame into PostgreSQL (optional; needs sqlalchemy + psycopg2)."""
    try:
        from sqlalchemy import create_engine
    except ImportError as exc:
        raise RuntimeError(
            "PostgreSQL load needs `pip install sqlalchemy psycopg2-binary`. "
            "The default pipeline (SQLite marts) does not require it.") from exc
    engine = create_engine(get_connection_string())
    df.to_sql(table_name, engine, if_exists="replace", index=False)
