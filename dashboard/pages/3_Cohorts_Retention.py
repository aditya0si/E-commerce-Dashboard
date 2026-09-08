"""Cohorts and retention."""
import pandas as pd
import streamlit as st

from dashboard._data import query_view

st.set_page_config(page_title="Cohorts / Retention", layout="wide")
st.title("Cohorts / Retention")

coh = query_view("v_cohort_retention")
coh = coh[coh["cohort_size"] >= 50].copy()  # hide tiny pre-launch cohorts
pivot = coh.pivot(index="cohort_month", columns="period_idx", values="retention_rate")
pivot = pivot.iloc[:, :7]  # first 7 periods keep the matrix readable

st.subheader("Retention matrix (share of cohort active N months after first purchase)")
st.dataframe(pivot.style.format("{:.1%}").background_gradient(axis=None),
             width="stretch")
st.caption(
    "Cohort = first delivered-purchase month. Olist is overwhelmingly one-time "
    "purchase: month-1 retention is typically below 1%. Read across rows for decay, "
    "down columns for seasonality of repeat behaviour.")

sizes = coh[coh["period_idx"] == 0][["cohort_month", "cohort_size"]]
st.subheader("Cohort sizes (new customers per month)")
st.bar_chart(sizes.set_index("cohort_month")["cohort_size"])

st.subheader("Average retention by period")
avg = coh.groupby("period_idx")["retention_rate"].mean().head(7)
st.bar_chart(avg)
st.dataframe(avg.rename("avg retention").to_frame(), width="stretch")
