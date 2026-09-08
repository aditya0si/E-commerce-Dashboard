"""Shared data layer for the dashboard.

Loads the marts built by `python -m scripts.olist_marts` (SQLite views).
If the database is missing (e.g. fresh Streamlit Cloud deploy), it is built
once from data/raw/ and then cached.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "processed" / "olist.db"

REFERENCE_DATE = pd.Timestamp("2018-10-17")  # max purchase timestamp in data


@st.cache_resource(show_spinner="Building marts from raw Olist data (first run only)...")
def get_connection() -> sqlite3.Connection:
    if not DB_PATH.exists():
        from scripts.olist_marts import build_marts
        build_marts()
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


@st.cache_data(ttl=3600)
def query_view(name: str) -> pd.DataFrame:
    con = get_connection()
    return pd.read_sql_query(f"SELECT * FROM {name}", con)


@st.cache_data(ttl=3600)
def query_fact_monthly() -> pd.DataFrame:
    con = get_connection()
    return pd.read_sql_query(
        """SELECT order_month,
                  COUNT(DISTINCT order_id) AS orders,
                  SUM(revenue_items) AS revenue,
                  AVG(review_score) AS avg_review,
                  AVG(is_late) AS late_rate
           FROM fact_orders WHERE is_delivered = 1
           GROUP BY order_month ORDER BY order_month""", con)


@st.cache_data(ttl=3600)
def query_payments_mix() -> pd.DataFrame:
    con = get_connection()
    return pd.read_sql_query(
        """SELECT payment_type,
                  COUNT(DISTINCT order_id) AS orders,
                  SUM(revenue_payments) AS revenue
           FROM fact_orders GROUP BY payment_type ORDER BY revenue DESC""", con)


@st.cache_data(ttl=3600)
def query_review_dist() -> pd.DataFrame:
    con = get_connection()
    return pd.read_sql_query(
        """SELECT review_score, COUNT(*) AS orders
           FROM fact_orders WHERE is_delivered = 1 AND review_score IS NOT NULL
           GROUP BY review_score ORDER BY review_score""", con)


@st.cache_data(ttl=3600)
def query_quality() -> dict:
    """Late-delivery rate and review average over delivered orders."""
    con = get_connection()
    row = con.execute(
        """SELECT AVG(is_late) AS late_rate, AVG(review_score) AS avg_review,
                  COUNT(*) AS delivered
           FROM fact_orders WHERE is_delivered = 1""").fetchone()
    return {"late_rate": row[0], "avg_review": row[1], "delivered": row[2]}


@st.cache_data(ttl=3600)
def query_state_revenue() -> pd.DataFrame:
    con = get_connection()
    return pd.read_sql_query(
        """SELECT customer_state AS state,
                  COUNT(DISTINCT order_id) AS orders,
                  SUM(revenue_items) AS revenue
           FROM fact_orders WHERE is_delivered = 1
           GROUP BY customer_state ORDER BY revenue DESC""", con)


def rfm_scored(rfm: pd.DataFrame) -> pd.DataFrame:
    """Add R/F/M quintile scores (5 = best) and a segment label."""
    df = rfm.copy()
    df["last_order"] = pd.to_datetime(df["last_order"])
    df["recency_days"] = (REFERENCE_DATE - df["last_order"]).dt.days
    for col, ascending in [("recency_days", False), ("frequency", True), ("monetary", True)]:
        # rank first so qcut never fails on ties
        df[col + "_score"] = pd.qcut(df[col].rank(method="first"), 5,
                                     labels=[1, 2, 3, 4, 5]).astype(int)
        if not ascending:
            df[col + "_score"] = 6 - df[col + "_score"]

    def segment(row):
        if row["recency_days_score"] >= 4 and row["frequency_score"] >= 4:
            return "Champions"
        if row["frequency_score"] >= 4:
            return "Loyal"
        if row["recency_days_score"] >= 4:
            return "Recent buyers"
        if row["recency_days_score"] <= 2 and row["frequency_score"] >= 3:
            return "At risk"
        if row["recency_days_score"] <= 2:
            return "Lost"
        return "Needs attention"

    df["segment"] = df.apply(segment, axis=1)
    return df


def brl(x: float) -> str:
    return f"R$ {x:,.2f}"
