"""Customers — RFM segmentation and realised LTV."""
import streamlit as st

from dashboard._data import brl, query_view, rfm_scored

st.set_page_config(page_title="Customers / RFM", layout="wide")
st.title("Customers / RFM")

rfm = rfm_scored(query_view("v_customer_rfm"))
repeat_rate = float((rfm["frequency"] > 1).mean())

s1, s2, s3, s4 = st.columns(4)
s1.metric("Unique customers (delivered)", f"{len(rfm):,}")
s2.metric("Repeat-buyer rate", f"{repeat_rate:.2%}")
s3.metric("Mean realised LTV", brl(float(rfm["monetary"].mean())))
s4.metric("Median realised LTV", brl(float(rfm["monetary"].median())))

st.subheader("Segments")
seg = (rfm.groupby("segment")
          .agg(customers=("monetary", "size"),
               avg_ltv=("monetary", "mean"),
               avg_orders=("frequency", "mean"))
          .sort_values("customers", ascending=False))
st.bar_chart(seg["customers"])
st.dataframe(seg, width="stretch")

st.subheader("LTV distribution (percentiles)")
st.write(rfm["monetary"].quantile([0.5, 0.75, 0.9, 0.95, 0.99]).rename("LTV (R$)").to_frame())
ltv_hist = rfm["monetary"].clip(upper=1000).value_counts(bins=20).sort_index()
ltv_hist.index = ltv_hist.index.astype(str)
st.bar_chart(ltv_hist)

st.caption(
    "R/F/M scored into quintiles (5 = best; recency measured to 2018-10-17). "
    "LTV is realised delivered revenue per customer — a lower bound on true lifetime "
    "value given the 25-month window. See METRICS.md.")
