"""Overview — KPIs, revenue trend, seasonality, payments, geography."""
import pandas as pd
import streamlit as st

from dashboard._data import brl, query_fact_monthly, query_payments_mix, query_quality, query_state_revenue, query_view

st.set_page_config(page_title="Overview", layout="wide")
st.title("Overview")

daily = query_view("v_daily_revenue")
daily["order_date"] = pd.to_datetime(daily["order_date"])
monthly = query_fact_monthly()
mix = query_payments_mix()
states = query_state_revenue()

revenue = float(daily["revenue"].sum())
orders = int(daily["orders"].sum())
quality = query_quality()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Delivered revenue", brl(revenue))
k2.metric("Delivered orders", f"{orders:,}")
k3.metric("AOV", brl(revenue / orders))
k4.metric("Avg review (delivered)", f"{quality['avg_review']:.2f} / 5")
k5.metric("Late-delivery rate", f"{quality['late_rate']:.1%}")

st.subheader("Daily delivered revenue")
st.line_chart(daily.set_index("order_date")["revenue"])

st.subheader("Monthly revenue and orders")
st.bar_chart(monthly.set_index("order_month")["revenue"])
st.dataframe(
    monthly.rename(columns={"order_month": "month", "orders": "orders",
                            "revenue": "revenue (R$)", "avg_review": "avg review",
                            "late_rate": "late rate"}),
    width="stretch", hide_index=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Revenue by payment type")
    st.bar_chart(mix.set_index("payment_type")["revenue"])
    st.dataframe(mix, width="stretch", hide_index=True)
with col2:
    st.subheader("Revenue by state (top 10)")
    st.bar_chart(states.head(10).set_index("state")["revenue"])
    top = states.head(10).copy()
    top["share"] = top["revenue"] / states["revenue"].sum()
    st.dataframe(top, width="stretch", hide_index=True)
