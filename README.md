# Olist E-commerce BI

Deployable BI product over the Brazilian Olist marketplace dataset
(99,441 orders, Sep 2016 – Oct 2018). Headline: **R$ 13.22M delivered revenue**
across **96,478 delivered orders** (AOV R$ 137.04).

## Pages (Streamlit)

| Page | Content |
|---|---|
| Home | KPI snapshot + how-to-read |
| Overview | revenue trend, seasonality, payment mix, top states |
| Category | revenue / orders / AOV / share by category |
| Cohorts / Retention | monthly cohort retention matrix |
| Customers / RFM | RFM segments + realised LTV |
| Funnel | created → approved → carrier → delivered → reviewed |

Metric definitions: [`METRICS.md`](METRICS.md). Validation: [`docs/EVAL.md`](docs/EVAL.md).

## Quickstart (local)

```bash
pip install -r requirements.txt
python -m scripts.pipeline      # builds data/processed/ + SQLite marts + views
python -m pytest tests/ -q      # 8 passed
streamlit run dashboard/app.py  # http://localhost:8501
```

Notebook: `notebooks/eda.ipynb` (regenerate with `python scripts/build_notebook.py`;
every finding recomputes from `data/raw/`).

## Deploy (Streamlit Community Cloud, free)

1. Push this repo to GitHub (make it public) — `data/raw/*.csv` is already tracked.
2. Go to <https://share.streamlit.io> → New app → select repo/branch →
   main file path **`dashboard/app.py`**.
3. No secrets needed. On first launch the app builds its SQLite marts from
   `data/raw/` automatically (≈1 min cold start, then cached).
4. Optional PostgreSQL: set `POSTGRES_*` in `.env` (see `.env.example`),
   `pip install sqlalchemy psycopg2-binary`, run `python -m scripts.pipeline --postgres`.

## Layout

```text
sql/schema.sql            # real Olist table definitions (SQLite + Postgres)
sql/analytics_views.sql   # 6 BI views: daily_revenue, category, cohort, RFM, funnel, LTV
scripts/olist_marts.py    # raw CSVs -> fact_orders / dim_customers / fact_items + olist.db
dashboard/                # app.py + 5 pages, shared layer in _data.py
tests/test_views.py       # consistency tests, expectations recomputed from raw CSVs
METRICS.md / docs/EVAL.md # metric definitions / validation notes
```
