CREATE TABLE IF NOT EXISTS sales (
    order_id TEXT PRIMARY KEY,
    order_date TIMESTAMP,
    customer_id TEXT,
    product_id TEXT,
    category TEXT,
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    revenue NUMERIC(12, 2)
);
