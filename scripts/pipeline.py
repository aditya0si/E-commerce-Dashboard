"""Pipeline entry point: build Olist marts (CSV + SQLite). PostgreSQL optional."""
from __future__ import annotations

import argparse

from scripts.olist_marts import build_marts


def run_pipeline(to_postgres: bool = False) -> dict:
    summary = build_marts()
    if to_postgres:
        from scripts.load import load_to_postgres
        import pandas as pd
        from scripts.config import PROCESSED_DIR
        fact = pd.read_csv(PROCESSED_DIR / "fact_orders.csv")
        load_to_postgres(fact, table_name="fact_orders")
    print("Pipeline completed successfully.")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Olist marts.")
    parser.add_argument("--postgres", action="store_true",
                        help="Also load fact_orders into PostgreSQL (needs SQLAlchemy + .env)")
    args = parser.parse_args()
    summary = run_pipeline(to_postgres=args.postgres)
    for k, v in summary.items():
        print(f"{k}={v}")
