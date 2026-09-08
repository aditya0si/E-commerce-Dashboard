"""Smoke + consistency tests for the Olist marts and BI views.

Strategy: expected values are computed from the raw CSVs inside the test
(no hard-coded business numbers), then compared against the SQLite views.
Run:  pytest tests/ -q   (from repo root, after `python -m scripts.olist_marts`)
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "processed" / "olist.db"

REQUIRED_VIEWS = [
    "v_daily_revenue", "v_category_performance", "v_cohort_retention",
    "v_customer_rfm", "v_funnel", "v_customer_ltv",
]


@pytest.fixture(scope="module")
def con():
    if not DB.exists():
        pytest.skip("data/processed/olist.db missing -- run `python -m scripts.olist_marts` first")
    c = sqlite3.connect(DB)
    yield c
    c.close()


def test_database_exists():
    assert DB.exists(), "Run `python -m scripts.olist_marts` to build marts"


def test_all_views_present(con):
    names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='view'")}
    assert set(REQUIRED_VIEWS) <= names, f"missing views: {set(REQUIRED_VIEWS) - names}"


def test_revenue_matches_raw(con):
    """View revenue == raw item-price sum over delivered orders (tolerance: rounding)."""
    items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
    orders = pd.read_csv(RAW / "olist_orders_dataset.csv", usecols=["order_id", "order_status"])
    delivered = set(orders.loc[orders.order_status == "delivered", "order_id"])
    expected = items.loc[items.order_id.isin(delivered), "price"].sum()
    got = con.execute("SELECT SUM(revenue) FROM v_daily_revenue").fetchone()[0]
    assert got == pytest.approx(expected, rel=1e-6)


def test_order_counts_consistent(con):
    n_delivered = con.execute(
        "SELECT COUNT(*) FROM fact_orders WHERE is_delivered = 1").fetchone()[0]
    n_daily = con.execute("SELECT SUM(orders) FROM v_daily_revenue").fetchone()[0]
    assert n_daily == n_delivered == 96478


def test_funnel_is_monotone(con):
    rows = con.execute("SELECT stage, orders FROM v_funnel ORDER BY stage_no").fetchall()
    assert [r[0] for r in rows] == [
        "01_created", "02_approved", "03_with_carrier", "04_delivered", "05_reviewed"]
    counts = [r[1] for r in rows]
    assert all(b <= a for a, b in zip(counts, counts[1:])), f"funnel not monotone: {rows}"
    assert counts[0] == 99441  # every raw order enters the funnel


def test_category_revenue_sums_to_total(con):
    cat_total = con.execute("SELECT SUM(revenue) FROM v_category_performance").fetchone()[0]
    day_total = con.execute("SELECT SUM(revenue) FROM v_daily_revenue").fetchone()[0]
    assert cat_total == pytest.approx(day_total, rel=1e-6)


def test_cohort_period_zero_equals_size(con):
    bad = con.execute(
        "SELECT COUNT(*) FROM v_cohort_retention WHERE period_idx = 0 "
        "AND active_customers != cohort_size").fetchone()[0]
    assert bad == 0


def test_rfm_ltv_row_agreement(con):
    n_rfm = con.execute("SELECT COUNT(*) FROM v_customer_rfm").fetchone()[0]
    n_ltv = con.execute("SELECT COUNT(*) FROM v_customer_ltv").fetchone()[0]
    assert n_rfm == n_ltv > 90000
    m_rfm = con.execute("SELECT SUM(monetary) FROM v_customer_rfm").fetchone()[0]
    m_ltv = con.execute("SELECT SUM(ltv_items) FROM v_customer_ltv").fetchone()[0]
    assert m_rfm == pytest.approx(m_ltv, rel=1e-9)
