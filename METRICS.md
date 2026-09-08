# Metrics layer

Single source of truth for every KPI in the notebook and dashboard.
All figures are computed from the Olist raw CSVs by `scripts/olist_marts.py`
into `data/processed/`; nothing here is hand-estimated.

## Revenue basis

| Metric | Definition | SQL / code |
|---|---|---|
| `revenue_items` | SUM of `order_items.price` over **delivered** orders only | `v_daily_revenue.revenue` |
| `revenue_payments` | SUM of `order_payments.payment_value` (reported separately) | `fact_orders.revenue_payments` |
| `AOV` | `revenue_items / delivered orders` = **R$ 137.04** | `v_daily_revenue.aov` |

Why two revenue numbers: `payment_value` (R$ 16,008,872.12 total) includes
freight and instalment artefacts; item price on delivered orders
(R$ 13,221,498.11) is the cleaner product-revenue signal. Both are shown so
the gap is explicit, not hidden.

## Headline values (recomputed by the pipeline)

- Orders: **99,441** total → **96,478 delivered** (97.0%), 625 cancelled.
- Window: 2016-09-04 → 2018-10-17. Peak order month: **2017-11 (7,544)**.
  Peak delivered-revenue month: **2017-11 (R$ 987,765.37)**.
- Customers: **96,096** unique (`customer_unique_id`); 93,358 have ≥1 delivered order.
- Repeat-buyer rate: **3.00%** of delivered customers (2,801 / 93,358).
- Reviews (delivered): avg **4.16/5**; 5★ 59.2%, 1★ 9.8%.
- Late delivery: **8.1%** of delivered orders arrive after the estimate.
- Geography: SP holds **38.3%** of delivered revenue (RJ 13.3%, MG 11.7%).
- Payments: credit_card **79.2%** of payment revenue, boleto 17.9%.
- Top category: health_beauty, **9.3%** of delivered revenue (R$ 1.23M).

## Derived metrics

- **Cohort / retention**: cohort = first delivered-purchase month (`YYYY-MM`);
  `period_idx` = months since cohort; `retention_rate` = active / cohort_size
  (`v_cohort_retention`). Month-1 retention is typically < 1% — Olist is
  overwhelmingly one-time purchase; that *is* the finding.
- **RFM** (`v_customer_rfm` + `dashboard/_data.py:rfm_scored`): recency in days
  to reference date **2018-10-17** (dataset max), frequency = delivered orders,
  monetary = delivered item revenue. Quintile scores 1–5 (5 = best, rank-based
  `qcut` so ties can't break it). Segments: Champions (R≥4,F≥4) 14,908 ·
  Loyal 22,435 · Recent buyers 22,435 · At risk 7,468 · Lost 15,005 ·
  Needs attention 11,107.
- **Funnel** (`v_funnel`): created 99,441 → approved 99,281 (99.8%) →
  with-carrier 97,658 (98.2%) → delivered 96,476 (97.0%) →
  reviewed 95,830 (96.4% of created; 99.3% of delivered). Stages are cumulative
  milestones, hence monotone. The reviewed stage counts delivered+reviewed only;
  an earlier version counted reviews on cancelled orders too (fixed, see EVAL).
- **LTV** (`v_customer_ltv`): realised delivered revenue per unique customer.
  Mean R$ 141.62, median R$ 89.73, p99 R$ 1,004.99, max R$ 13,440.00.
  This is a *lower bound* on true lifetime value (25-month window, §limitations).

## Limitations (honest)

1. No cost / margin data → revenue only, no profit views.
2. 25-month window with heavy right-censoring → retention and LTV are truncated.
3. `customer_unique_id` repeat matching is Olist's own heuristic.
4. Geolocation table (60 MB) is unused — city/state from customers suffices.
5. Funnel uses timestamp presence, not event logs — no drop-off reasons.
