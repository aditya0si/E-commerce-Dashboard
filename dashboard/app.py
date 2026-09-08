"""Olist E-commerce BI — landing page."""
import streamlit as st

from dashboard._data import brl, query_view

st.set_page_config(page_title="Olist BI — Home", layout="wide")

st.title("Olist E-commerce BI")
st.caption("Brazilian marketplace orders, Sep 2016 – Oct 2018 · delivered-order revenue basis · see METRICS.md")

daily = query_view("v_daily_revenue")
funnel = query_view("v_funnel")
created = int(funnel.loc[funnel.stage == "01_created", "orders"].iat[0])
delivered = int(funnel.loc[funnel.stage == "04_delivered", "orders"].iat[0])
revenue = float(daily["revenue"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Delivered revenue", brl(revenue))
c2.metric("Delivered orders", f"{delivered:,}")
c3.metric("Delivered rate", f"{delivered / created:.1%}")
c4.metric("AOV (delivered)", brl(revenue / delivered))

st.divider()
st.subheader("Pages")
st.markdown(
    "- **Overview** — revenue trend, seasonality, payment mix, geography\n"
    "- **Category** — category performance table (revenue, orders, AOV, share)\n"
    "- **Cohorts / Retention** — monthly cohort retention matrix\n"
    "- **Customers / RFM** — RFM segmentation and realised LTV\n"
    "- **Funnel** — created → approved → carrier → delivered → reviewed"
)
st.subheader("How to read this dashboard")
st.markdown(
    "Revenue is the sum of `order_items.price` over **delivered** orders only. "
    "Payment totals (`payment_value`) run higher because they include freight. "
    "Full definitions live in `METRICS.md`; validation queries and results in `docs/EVAL.md`."
)
