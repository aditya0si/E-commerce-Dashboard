from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="E-commerce Analytics", layout="wide")

st.title("E-commerce Analytics Dashboard")
st.caption("Starter Streamlit dashboard for pipeline outputs")

processed_file = Path(__file__).resolve().parent.parent / "data" / "processed" / "sales_clean.csv"

if processed_file.exists():
    df = pd.read_csv(processed_file)
    st.subheader("Processed Sales Data")
    st.dataframe(df, use_container_width=True)

    if "revenue" in df.columns:
        st.metric("Total Revenue", f"{df['revenue'].sum():,.2f}")
else:
    st.info("No processed file found yet. Run the pipeline and save an output to data/processed/sales_clean.csv.")
