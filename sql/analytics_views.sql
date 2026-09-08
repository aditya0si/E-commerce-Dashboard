-- Olist BI views. Portable SQL: runs on SQLite (>= 3.25) and PostgreSQL.
-- Conventions (see METRICS.md):
--   * Revenue = SUM(revenue_items) over DELIVERED orders only.
--   * order_month is 'YYYY-MM' text -> lexicographic compare == chronological.
--   * Month index arithmetic uses CAST(substr(...)) -- valid in both engines.

-- 1. Daily revenue (delivered orders only)
CREATE VIEW IF NOT EXISTS v_daily_revenue AS
SELECT
    order_date,
    COUNT(DISTINCT order_id) AS orders,
    SUM(revenue_items) AS revenue,
    SUM(revenue_items) / COUNT(DISTINCT order_id) AS aov
FROM fact_orders
WHERE is_delivered = 1
GROUP BY order_date
ORDER BY order_date;

-- 2. Category performance (item grain, delivered orders only)
CREATE VIEW IF NOT EXISTS v_category_performance AS
WITH delivered AS (
    SELECT order_id FROM fact_orders WHERE is_delivered = 1
)
SELECT
    fi.category_en AS category,
    SUM(fi.price) AS revenue,
    COUNT(DISTINCT fi.order_id) AS orders,
    COUNT(*) AS items,
    SUM(fi.price) / COUNT(DISTINCT fi.order_id) AS aov
FROM fact_items fi
JOIN delivered d ON d.order_id = fi.order_id
GROUP BY fi.category_en
ORDER BY revenue DESC;

-- 3. Cohort retention: cohort = first purchase month; period = months since cohort.
-- Month index = year*12 + month so period_idx is portable integer math.
CREATE VIEW IF NOT EXISTS v_cohort_retention AS
WITH cust_orders AS (
    SELECT DISTINCT customer_unique_id, order_month
    FROM fact_orders
    WHERE is_delivered = 1
),
cohorts AS (
    SELECT customer_unique_id, MIN(order_month) AS cohort_month
    FROM cust_orders
    GROUP BY customer_unique_id
),
idx AS (
    SELECT
        c.cohort_month,
        o.order_month,
        (CAST(substr(o.order_month, 1, 4) AS INTEGER) * 12
         + CAST(substr(o.order_month, 6, 2) AS INTEGER))
        - (CAST(substr(c.cohort_month, 1, 4) AS INTEGER) * 12
           + CAST(substr(c.cohort_month, 6, 2) AS INTEGER)) AS period_idx,
        o.customer_unique_id
    FROM cust_orders o
    JOIN cohorts c ON c.customer_unique_id = o.customer_unique_id
),
sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM cohorts
    GROUP BY cohort_month
)
SELECT
    i.cohort_month,
    i.period_idx,
    COUNT(DISTINCT i.customer_unique_id) AS active_customers,
    s.cohort_size,
    CAST(COUNT(DISTINCT i.customer_unique_id) AS REAL) / s.cohort_size AS retention_rate
FROM idx i
JOIN sizes s ON s.cohort_month = i.cohort_month
GROUP BY i.cohort_month, i.period_idx, s.cohort_size
ORDER BY i.cohort_month, i.period_idx;

-- 4. RFM base (one row per real customer). Scoring into quintiles is done in
-- the dashboard with pandas so the rule is inspectable; see METRICS.md.
CREATE VIEW IF NOT EXISTS v_customer_rfm AS
SELECT
    customer_unique_id,
    orders AS frequency,
    monetary_items AS monetary,
    first_order,
    last_order,
    first_month AS cohort_month,
    state
FROM dim_customers;

-- 5. Purchase funnel: milestone timestamps present per order.
CREATE VIEW IF NOT EXISTS v_funnel AS
WITH stages AS (
    SELECT '01_created'   AS stage, 1 AS stage_no, COUNT(*) AS orders FROM fact_orders
    UNION ALL
    SELECT '02_approved', 2, COUNT(*) FROM fact_orders WHERE order_approved_at IS NOT NULL
    UNION ALL
    SELECT '03_with_carrier', 3, COUNT(*) FROM fact_orders WHERE order_delivered_carrier_date IS NOT NULL
    UNION ALL
    SELECT '04_delivered', 4, COUNT(*) FROM fact_orders WHERE order_delivered_customer_date IS NOT NULL
    UNION ALL
    SELECT '05_reviewed', 5, COUNT(*) FROM fact_orders
    WHERE order_delivered_customer_date IS NOT NULL AND review_score IS NOT NULL
)
SELECT
    stage,
    stage_no,
    orders,
    CAST(orders AS REAL) / (SELECT orders FROM stages WHERE stage_no = 1) AS conv_from_top,
    CAST(orders AS REAL) / LAG(orders) OVER (ORDER BY stage_no) AS conv_from_prev
FROM stages
ORDER BY stage_no;

-- 6. Customer LTV (realised, delivered revenue per unique customer)
CREATE VIEW IF NOT EXISTS v_customer_ltv AS
SELECT
    customer_unique_id,
    orders,
    monetary_items AS ltv_items,
    monetary_payments AS ltv_payments,
    first_order,
    last_order,
    state
FROM dim_customers
ORDER BY ltv_items DESC;
