"""Build Olist marts: fact tables -> data/processed/ + SQLite DB.

Reads the 9 raw Olist CSVs, joins them into analysis-ready marts and a
portable SQLite database that the Streamlit dashboard and the test-suite
both consume. PostgreSQL remains optional (see scripts/load.py).

Grain & revenue rule (see METRICS.md):
- One row per order in fact_orders.
- Primary revenue = SUM(order_items.price) for DELIVERED orders only.
- payment_value is reported separately (includes freight / installments).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from scripts.config import PROCESSED_DIR, RAW_DIR

REFERENCE_DATE = "2018-10-17"  # max(order_purchase_timestamp) in the dataset


def _read(name: str, **kw) -> pd.DataFrame:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    return pd.read_csv(path, **kw)


def build_marts(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> dict:
    orders = _read("olist_orders_dataset.csv")
    items = _read("olist_order_items_dataset.csv")
    pay = _read("olist_order_payments_dataset.csv")
    cust = _read("olist_customers_dataset.csv")
    prod = _read("olist_products_dataset.csv")
    trans = _read("product_category_name_translation.csv")
    rev = _read("olist_order_reviews_dataset.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    for c in ["order_approved_at", "order_delivered_carrier_date",
              "order_delivered_customer_date", "order_estimated_delivery_date"]:
        orders[c] = pd.to_datetime(orders[c], errors="coerce")

    cat = prod[["product_id", "product_category_name"]].merge(trans, on="product_category_name", how="left")
    cat["category_en"] = cat["product_category_name_english"].fillna(cat["product_category_name"])
    items = items.merge(cat[["product_id", "category_en"]], on="product_id", how="left")
    items["category_en"] = items["category_en"].fillna("unknown")

    # Per-order aggregates
    g_items = items.groupby("order_id").agg(
        revenue_items=("price", "sum"), freight=("freight_value", "sum"),
        n_items=("price", "size"))
    g_pay = pay.groupby("order_id").agg(
        revenue_payments=("payment_value", "sum"),
        payment_type=("payment_type", lambda s: s.mode().iat[0] if len(s) else None),
        n_installments=("payment_installments", "max"))
    # One review per order: keep first row on ties (multi-review orders are rare).
    g_rev = rev.groupby("order_id").agg(review_score=("review_score", "first"))

    fact = (orders
            .merge(cust[["customer_id", "customer_unique_id", "customer_state", "customer_city"]],
                   on="customer_id", how="left")
            .merge(g_items, on="order_id", how="left")
            .merge(g_pay, on="order_id", how="left")
            .merge(g_rev, on="order_id", how="left"))
    fact[["revenue_items", "freight", "n_items"]] = fact[["revenue_items", "freight", "n_items"]].fillna(0)
    fact["revenue_payments"] = fact["revenue_payments"].fillna(0)
    fact["is_delivered"] = (fact["order_status"] == "delivered").astype(int)
    fact["order_date"] = fact["order_purchase_timestamp"].dt.strftime("%Y-%m-%d")
    fact["order_month"] = fact["order_purchase_timestamp"].dt.strftime("%Y-%m")
    late = (fact["order_delivered_customer_date"].notna()
            & fact["order_estimated_delivery_date"].notna()
            & (fact["order_delivered_customer_date"] > fact["order_estimated_delivery_date"]))
    fact["is_late"] = late.astype(int)

    # Per-order top category (by item price) for mix analysis
    top_cat = (items.sort_values("price", ascending=False)
               .drop_duplicates("order_id").set_index("order_id")["category_en"])
    fact["top_category"] = fact["order_id"].map(top_cat).fillna("unknown")

    # Customer grain (unique customers = real people)
    d = fact[fact["is_delivered"] == 1]
    cust_mart = (d.groupby("customer_unique_id").agg(
        orders=("order_id", "nunique"),
        monetary_items=("revenue_items", "sum"),
        monetary_payments=("revenue_payments", "sum"),
        first_order=("order_date", "min"),
        last_order=("order_date", "max"),
        first_month=("order_month", "min"),
        state=("customer_state", "first")).reset_index())

    fact_items = items[["order_id", "product_id", "category_en", "price", "freight_value"]].copy()

    out_dir.mkdir(parents=True, exist_ok=True)
    fact.to_csv(out_dir / "fact_orders.csv", index=False)
    cust_mart.to_csv(out_dir / "dim_customers.csv", index=False)
    fact_items.to_csv(out_dir / "fact_items.csv", index=False)

    db_path = out_dir / "olist.db"
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    fact.to_sql("fact_orders", con, index=False)
    cust_mart.to_sql("dim_customers", con, index=False)
    fact_items.to_sql("fact_items", con, index=False)
    views_sql = Path(__file__).resolve().parent.parent / "sql" / "analytics_views.sql"
    if views_sql.exists():
        con.executescript(views_sql.read_text(encoding="utf-8"))
    con.commit()

    # Summary for logs / EVAL notes (computed, never hand-written)
    summary = {
        "orders_total": int(len(fact)),
        "orders_delivered": int(fact["is_delivered"].sum()),
        "revenue_items_delivered": round(float(d["revenue_items"].sum()), 2),
        "revenue_payments_total": round(float(fact["revenue_payments"].sum()), 2),
        "customers_unique": int(fact["customer_unique_id"].nunique()),
        "date_min": str(fact["order_date"].min()),
        "date_max": str(fact["order_date"].max()),
    }
    con.close()
    (out_dir / "_build_summary.txt").write_text(
        "\n".join(f"{k}={v}" for k, v in summary.items()), encoding="utf-8")
    return summary


if __name__ == "__main__":
    from pprint import pprint
    pprint(build_marts())
