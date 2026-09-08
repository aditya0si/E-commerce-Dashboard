# EVAL notes — validation, data quality, follow-ups

## View validation (all run, all green)

`pytest tests/ -q` → **8 passed**. Each test recomputes expectations from the
raw CSVs inside the test (no hard-coded business numbers):

| Test | What it proves |
|---|---|
| `test_revenue_matches_raw` | `v_daily_revenue` total == raw item-price sum over delivered orders |
| `test_order_counts_consistent` | daily view sums to 96,478 delivered orders |
| `test_funnel_is_monotone` | stages strictly non-increasing, 99,441 enter at top |
| `test_category_revenue_sums_to_total` | category view and daily view agree to 1e-6 |
| `test_cohort_period_zero_equals_size` | period-0 actives == cohort size for every cohort |
| `test_rfm_ltv_row_agreement` | RFM and LTV views agree on rows (>90k) and totals |

Dashboard pages verified with `streamlit.testing.v1.AppTest`: all 6 scripts
run with **zero exceptions** (deprecation warnings fixed).

## Bugs found and fixed during this pass

1. **Funnel `05_reviewed` counted reviews on cancelled/undelivered orders**
   (98,673 > 96,476 delivered — non-monotone). Fixed to delivered+reviewed
   (95,830); test now asserts monotonicity.
2. **Review averaging created fractional scores** (3.33, 4.5) on multi-review
   orders. Fixed to first-review-wins; distribution is integer 1–5 again.
3. **`sql/schema.sql` described a generic `sales` table that matched nothing.**
   Replaced with the real Olist table definitions; legacy `sales` kept for compat.
4. **`scripts/load.py` imported SQLAlchemy at module top** although it is not
   installed and not needed. Now lazy with a clear error; default path is SQLite.
5. **`scripts/config.py` hard-required `python-dotenv`.** Now optional import.

## Data-quality notes

- 775 orders (0.8%) have no `order_items` rows; 625 cancelled + 609 unavailable
  explain most. Revenue views use delivered orders only, unaffected.
- `payment_value` total exceeds item revenue by ~R$ 2.8M (freight + rounding);
  documented in METRICS.md rather than reconciled away.
- Duplicated reviews per order are rare (<0.5%); first-row-wins is immaterial.

## Follow-ups (not done — scoped out honestly)

- Late-delivery × low-review join (hypothesis stated on Funnel page, untested).
- Seller-side views (top sellers, carrier delay by seller state).
- Price-elasticity / promo modelling — no promo flags in data, would need inference.
- Postgres CI target — views are written in portable SQL but only SQLite is tested.
