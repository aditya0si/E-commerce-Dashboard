CREATE OR REPLACE VIEW daily_revenue AS
SELECT
    DATE(order_date) AS order_day,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders
FROM sales
GROUP BY DATE(order_date)
ORDER BY order_day;
