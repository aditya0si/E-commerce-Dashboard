"""Category performance."""
import streamlit as st

from dashboard._data import query_view

st.set_page_config(page_title="Category", layout="wide")
st.title("Category performance")

cat = query_view("v_category_performance")
cat["share"] = cat["revenue"] / cat["revenue"].sum()

top_n = st.slider("Show top N categories", 5, 30, 10)
view = cat.head(top_n)

st.bar_chart(view.set_index("category")["revenue"])
st.dataframe(
    view.rename(columns={"category": "category", "revenue": "revenue (R$)",
                         "orders": "orders", "items": "items",
                         "aov": "AOV (R$)", "share": "revenue share"}),
    width="stretch", hide_index=True)

st.caption(
    f"Top category: {cat['category'].iat[0]} "
    f"({cat['share'].iat[0]:.1%} of delivered revenue). "
    f"Top {top_n} categories hold {cat['share'].head(top_n).sum():.1%} of revenue.")
