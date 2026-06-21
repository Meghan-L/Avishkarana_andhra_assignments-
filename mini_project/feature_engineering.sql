"""
PHASE 1 CONTINUATION: ADVANCED SQL FEATURE ENGINEERING
CTEs and Window Functions for robust feature extraction for ML model training.
"""

# SQL Feature Engineering Query - save this for reference
FEATURE_ENGINEERING_QUERY = """
WITH daily_aggregates AS (
    -- Aggregate daily sales by product
    SELECT 
        product_id,
        transaction_date,
        SUM(quantity_sold) AS daily_quantity,
        AVG(sale_price) AS avg_price,
        COUNT(*) AS transaction_count,
        EXTRACT(DOW FROM transaction_date) AS day_of_week
    FROM sales_transactions
    GROUP BY product_id, transaction_date
),

rolling_averages AS (
    -- Calculate rolling 7-day and 30-day averages using window functions
    SELECT 
        product_id,
        transaction_date,
        daily_quantity,
        avg_price,
        transaction_count,
        day_of_week,
        
        -- 7-day rolling average
        AVG(daily_quantity) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7day_avg,
        
        -- 30-day rolling average
        AVG(daily_quantity) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS rolling_30day_avg,
        
        -- 7-day rolling standard deviation
        STDEV(daily_quantity) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7day_std,
        
        -- Previous day's quantity for lag feature
        LAG(daily_quantity, 1) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date
        ) AS prev_day_quantity,
        
        -- Quantity from same day last week (7-day lag)
        LAG(daily_quantity, 7) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date
        ) AS quantity_7day_ago
    FROM daily_aggregates
),

feature_enrichment AS (
    -- Add product metadata and calculated features
    SELECT 
        ra.product_id,
        p.product_name,
        p.category,
        p.unit_price,
        p.lead_time_days,
        p.safety_stock_units,
        p.current_inventory,
        ra.transaction_date,
        ra.daily_quantity,
        ra.avg_price,
        ra.transaction_count,
        ra.day_of_week,
        CASE 
            WHEN ra.day_of_week IN (5, 6) THEN 1 
            ELSE 0 
        END AS is_weekend,
        ra.rolling_7day_avg,
        ra.rolling_30day_avg,
        ra.rolling_7day_std,
        COALESCE(ra.rolling_7day_std, 0) AS demand_volatility,
        ra.prev_day_quantity,
        ra.quantity_7day_ago,
        
        -- Year-over-year comparison
        EXTRACT(MONTH FROM ra.transaction_date) AS month,
        EXTRACT(QUARTER FROM ra.transaction_date) AS quarter,
        
        -- Inventory to sales ratio
        CASE 
            WHEN ra.daily_quantity > 0 
            THEN CAST(p.current_inventory AS FLOAT) / ra.daily_quantity 
            ELSE 0 
        END AS inventory_to_sales_ratio
    FROM rolling_averages ra
    INNER JOIN products p ON ra.product_id = p.product_id
)

SELECT 
    product_id,
    product_name,
    category,
    unit_price,
    lead_time_days,
    safety_stock_units,
    current_inventory,
    transaction_date,
    daily_quantity,
    avg_price,
    transaction_count,
    day_of_week,
    is_weekend,
    rolling_7day_avg,
    rolling_30day_avg,
    demand_volatility,
    prev_day_quantity,
    quantity_7day_ago,
    month,
    quarter,
    inventory_to_sales_ratio
FROM feature_enrichment
WHERE transaction_date >= DATE('now', '-180 days')
ORDER BY product_id, transaction_date;
"""

if __name__ == "__main__":
    print("Feature Engineering SQL Query:")
    print("=" * 80)
    print(FEATURE_ENGINEERING_QUERY)
    print("=" * 80)
