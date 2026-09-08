"""Funnel — created to reviewed, plus review and delivery quality."""
import streamlit as st

from dashboard._data import query_quality, query_review_dist, query_view

st.set_page_config(page_title="Funnel", layout="wide")
st.title("Purchase funnel")

funnel = query_view("v_funnel")
funnel["conv_from_top"] = funnel["conv_from_top"].map(lambda x: f"{x:.2%}")
funnel["conv_from_prev"] = funnel["conv_from_prev"].map(
    lambda x: "—" if x is None else f"{x:.2%}")
st.dataframe(funnel.rename(columns={"stage": "stage", "stage_no": "#",
                                    "orders": "orders",
                                    "conv_from_top": "of created",
                                    "conv_from_prev": "of previous"}),
             width="stretch", hide_index=True)
st.bar_chart(query_view("v_funnel").set_index("stage")["orders"])

st.caption(
    "Stages are cumulative milestone timestamps, so conversion is monotone. "
    "The reviewed stage counts delivered orders that left a review.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Review scores (delivered orders)")
    rev = query_review_dist()
    st.bar_chart(rev.set_index("review_score")["orders"])
    st.dataframe(rev, width="stretch", hide_index=True)
    five = float(rev.loc[rev.review_score == 5, "orders"].iat[0] / rev["orders"].sum())
    st.metric("5-star share", f"{five:.1%}")
with col2:
    st.subheader("Delivery quality")
    late = query_quality()["late_rate"]
    st.metric("Late-delivery rate", f"{late:.1%}",
              help="Delivered after the estimated date; computed in fact_orders.is_late")
    st.markdown(
        "Late = `delivered_customer_date > estimated_delivery_date`. "
        "Late delivery is the main lever suspected "
        "behind 1–3 star reviews — testable join left as a follow-up in EVAL notes.")
