"""
OPERATIONAL SQL QUERIES
Production-ready SQL queries for business intelligence, reporting, and decision-making.
All queries are compatible with SQLite and PostgreSQL.
"""

# ==========================================
# QUERY 1: CRITICAL ACTION ITEMS
# ==========================================
QUERY_CRITICAL_ACTIONS = """
SELECT 
    product_id,
    product_name,
    category,
    current_inventory,
    reorder_point,
    predicted_demand_7day,
    (reorder_point - current_inventory) as shortage_units,
    (predicted_demand_7day * 2 - current_inventory) as recommended_order_qty,
    lead_time_days,
    CASE 
        WHEN current_inventory <= 0 THEN 'URGENT: OUT OF STOCK'
        WHEN current_inventory < reorder_point * 0.5 THEN 'CRITICAL: Reorder immediately'
        ELSE 'High priority reorder'
    END as action_priority,
    alert_created_at as last_alert_time
FROM reorder_alerts
WHERE alert_status = 'CRITICAL RESTOCK'
  AND action_required = 1
ORDER BY current_inventory ASC
LIMIT 20;
"""

# ==========================================
# QUERY 2: INVENTORY HEALTH SCORECARD
# ==========================================
QUERY_INVENTORY_HEALTH = """
SELECT 
    category,
    COUNT(DISTINCT product_id) as total_products,
    SUM(current_inventory) as total_units_in_stock,
    SUM(predicted_demand_7day) as predicted_7day_demand,
    AVG(current_inventory) as avg_product_inventory,
    AVG(days_inventory_remaining) as avg_days_inventory,
    ROUND(100.0 * SUM(CASE WHEN alert_status = 'HEALTHY' THEN 1 ELSE 0 END) 
          / COUNT(DISTINCT product_id), 1) as health_percentage,
    SUM(CASE WHEN alert_status = 'CRITICAL RESTOCK' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN alert_status = 'WATCHLIST' THEN 1 ELSE 0 END) as watchlist_count
FROM reorder_alerts
GROUP BY category
ORDER BY health_percentage ASC, critical_count DESC;
"""

# ==========================================
# QUERY 3: 7-DAY DEMAND FORECAST BY CATEGORY
# ==========================================
QUERY_DEMAND_FORECAST_BY_CATEGORY = """
SELECT 
    p.category,
    COUNT(DISTINCT fd.product_id) as num_products,
    SUM(fd.predicted_quantity) as total_predicted_qty,
    AVG(fd.predicted_quantity) as avg_daily_forecast,
    MIN(fd.predicted_quantity) as min_daily_forecast,
    MAX(fd.predicted_quantity) as max_daily_forecast,
    fd.forecast_date
FROM forecasted_demand fd
INNER JOIN products p ON fd.product_id = p.product_id
WHERE fd.forecast_date >= DATE('now')
  AND fd.forecast_date <= DATE('now', '+7 days')
GROUP BY p.category, fd.forecast_date
ORDER BY fd.forecast_date DESC, total_predicted_qty DESC;
"""

# ==========================================
# QUERY 4: FORECAST ACCURACY vs ACTUAL SALES
# ==========================================
QUERY_FORECAST_ACCURACY = """
WITH forecast_data AS (
    SELECT 
        fd.product_id,
        p.product_name,
        SUM(fd.predicted_quantity) as total_forecast
    FROM forecasted_demand fd
    JOIN products p ON fd.product_id = p.product_id
    WHERE fd.forecast_created_at >= DATE('now', '-7 days')
    GROUP BY fd.product_id, p.product_name
),

actual_data AS (
    SELECT 
        product_id,
        SUM(quantity_sold) as total_actual
    FROM sales_transactions
    WHERE transaction_date >= DATE('now', '-7 days')
    GROUP BY product_id
)

SELECT 
    f.product_id,
    f.product_name,
    COALESCE(a.total_actual, 0) as actual_quantity,
    f.total_forecast as forecasted_quantity,
    ABS(f.total_forecast - COALESCE(a.total_actual, 0)) as absolute_error,
    ROUND(100.0 * ABS(f.total_forecast - COALESCE(a.total_actual, 0)) 
          / NULLIF(COALESCE(a.total_actual, f.total_forecast), 0), 1) as error_percentage,
    CASE 
        WHEN ABS(f.total_forecast - COALESCE(a.total_actual, 0)) <= f.total_forecast * 0.1 THEN 'Excellent'
        WHEN ABS(f.total_forecast - COALESCE(a.total_actual, 0)) <= f.total_forecast * 0.2 THEN 'Good'
        WHEN ABS(f.total_forecast - COALESCE(a.total_actual, 0)) <= f.total_forecast * 0.3 THEN 'Fair'
        ELSE 'Poor'
    END as accuracy_grade
FROM forecast_data f
LEFT JOIN actual_data a ON f.product_id = a.product_id
ORDER BY error_percentage DESC;
"""

# ==========================================
# QUERY 5: DAYS-TO-STOCKOUT ANALYSIS
# ==========================================
QUERY_DAYS_TO_STOCKOUT = """
SELECT 
    product_id,
    product_name,
    category,
    current_inventory,
    predicted_demand_7day,
    days_inventory_remaining,
    CASE 
        WHEN days_inventory_remaining <= 3 THEN 'CRITICAL - Reorder TODAY'
        WHEN days_inventory_remaining <= 7 THEN 'URGENT - Reorder this week'
        WHEN days_inventory_remaining <= 14 THEN 'HIGH - Reorder soon'
        WHEN days_inventory_remaining <= 30 THEN 'NORMAL - Monitor'
        ELSE 'HEALTHY - Well stocked'
    END as stockout_risk,
    alert_status,
    recommended_restock_qty
FROM reorder_alerts
ORDER BY days_inventory_remaining ASC;
"""

# ==========================================
# QUERY 6: PRODUCT PERFORMANCE METRICS
# ==========================================
QUERY_PRODUCT_PERFORMANCE = """
WITH sales_summary AS (
    SELECT 
        product_id,
        COUNT(*) as transaction_count,
        SUM(quantity_sold) as total_sold_30day,
        AVG(quantity_sold) as avg_daily_sales,
        STDDEV(quantity_sold) as demand_volatility,
        MIN(quantity_sold) as min_daily_sales,
        MAX(quantity_sold) as max_daily_sales
    FROM sales_transactions
    WHERE transaction_date >= DATE('now', '-30 days')
    GROUP BY product_id
)

SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price,
    ss.transaction_count,
    ss.total_sold_30day,
    ROUND(ss.avg_daily_sales, 1) as avg_daily_sales,
    ROUND(ss.demand_volatility, 2) as demand_volatility,
    ROUND(ss.total_sold_30day * p.unit_price, 2) as revenue_30day,
    ROUND((ss.total_sold_30day * p.unit_price) / 30, 2) as daily_revenue,
    CASE 
        WHEN ss.total_sold_30day < ss.avg_daily_sales * 15 THEN 'Low'
        WHEN ss.total_sold_30day < ss.avg_daily_sales * 25 THEN 'Medium'
        ELSE 'High'
    END as sales_velocity
FROM products p
LEFT JOIN sales_summary ss ON p.product_id = ss.product_id
ORDER BY ss.total_sold_30day DESC;
"""

# ==========================================
# QUERY 7: REORDER POINT OPTIMIZATION
# ==========================================
QUERY_REORDER_OPTIMIZATION = """
SELECT 
    product_id,
    product_name,
    category,
    lead_time_days,
    safety_stock_units,
    reorder_point,
    current_inventory,
    predicted_demand_7day,
    CASE 
        WHEN safety_stock_units < predicted_demand_7day * 0.5 THEN 'INCREASE safety stock'
        WHEN safety_stock_units > predicted_demand_7day * 2 THEN 'DECREASE safety stock (excess)'
        ELSE 'OPTIMAL safety stock'
    END as safety_stock_recommendation,
    CASE 
        WHEN reorder_point < (predicted_demand_7day * lead_time_days) THEN 'INCREASE reorder point'
        WHEN reorder_point > (predicted_demand_7day * lead_time_days * 1.5) THEN 'DECREASE reorder point'
        ELSE 'OPTIMAL reorder point'
    END as reorder_point_recommendation
FROM reorder_alerts
ORDER BY 
    CASE 
        WHEN safety_stock_recommendation LIKE 'INCREASE%' THEN 1
        WHEN reorder_point_recommendation LIKE 'INCREASE%' THEN 2
        ELSE 3
    END;
"""

# ==========================================
# QUERY 8: INVENTORY TURNOVER ANALYSIS
# ==========================================
QUERY_INVENTORY_TURNOVER = """
WITH inventory_metrics AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.current_inventory,
        SUM(st.quantity_sold) as qty_sold_30day,
        AVG(p.unit_price) as avg_unit_price,
        (SUM(st.quantity_sold) / NULLIF(p.current_inventory, 0)) as turnover_ratio
    FROM products p
    LEFT JOIN sales_transactions st ON p.product_id = st.product_id 
        AND st.transaction_date >= DATE('now', '-30 days')
    GROUP BY p.product_id, p.product_name, p.category, p.current_inventory, p.unit_price
)

SELECT 
    product_id,
    product_name,
    category,
    current_inventory as units_in_stock,
    qty_sold_30day,
    ROUND(qty_sold_30day * avg_unit_price, 2) as inventory_value,
    ROUND(COALESCE(turnover_ratio, 0), 2) as turnover_ratio_30day,
    CASE 
        WHEN COALESCE(turnover_ratio, 0) < 0.5 THEN 'Slow Moving - Consider Liquidation'
        WHEN COALESCE(turnover_ratio, 0) < 1 THEN 'Below Average - Reduce Stock'
        WHEN COALESCE(turnover_ratio, 0) < 2 THEN 'Normal'
        ELSE 'Fast Moving - Increase Stock'
    END as inventory_status
FROM inventory_metrics
ORDER BY turnover_ratio DESC;
"""

# ==========================================
# QUERY 9: WEEKLY DEMAND TREND
# ==========================================
QUERY_WEEKLY_DEMAND_TREND = """
SELECT 
    day_of_week,
    COUNT(*) as transaction_count,
    SUM(quantity_sold) as total_quantity,
    ROUND(AVG(quantity_sold), 1) as avg_quantity_per_transaction,
    ROUND(AVG(sale_price), 2) as avg_sale_price,
    ROUND(SUM(quantity_sold * sale_price), 2) as total_revenue
FROM sales_transactions
WHERE transaction_date >= DATE('now', '-90 days')
GROUP BY day_of_week
ORDER BY CASE 
    WHEN day_of_week = 'Monday' THEN 1
    WHEN day_of_week = 'Tuesday' THEN 2
    WHEN day_of_week = 'Wednesday' THEN 3
    WHEN day_of_week = 'Thursday' THEN 4
    WHEN day_of_week = 'Friday' THEN 5
    WHEN day_of_week = 'Saturday' THEN 6
    WHEN day_of_week = 'Sunday' THEN 7
END;
"""

# ==========================================
# QUERY 10: ALERT HISTORY & TRENDS
# ==========================================
QUERY_ALERT_HISTORY = """
SELECT 
    DATE(alert_created_at) as alert_date,
    alert_status,
    COUNT(*) as alert_count,
    COUNT(DISTINCT product_id) as unique_products,
    SUM(CASE WHEN action_required = 1 THEN 1 ELSE 0 END) as critical_actions,
    ROUND(100.0 * SUM(CASE WHEN action_required = 1 THEN 1 ELSE 0 END) 
          / COUNT(*), 1) as action_required_percentage
FROM reorder_alerts
WHERE alert_created_at >= DATE('now', '-30 days')
GROUP BY DATE(alert_created_at), alert_status
ORDER BY alert_date DESC, alert_status;
"""

# ==========================================
# QUERY 11: INVENTORY BY LEAD TIME
# ==========================================
QUERY_INVENTORY_BY_LEAD_TIME = """
SELECT 
    CASE 
        WHEN lead_time_days <= 5 THEN '< 5 days'
        WHEN lead_time_days <= 10 THEN '5-10 days'
        ELSE '> 10 days'
    END as lead_time_bucket,
    COUNT(DISTINCT product_id) as num_products,
    SUM(current_inventory) as total_inventory,
    AVG(reorder_point) as avg_reorder_point,
    SUM(CASE WHEN alert_status = 'CRITICAL RESTOCK' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN alert_status = 'WATCHLIST' THEN 1 ELSE 0 END) as watchlist_count,
    SUM(CASE WHEN alert_status = 'HEALTHY' THEN 1 ELSE 0 END) as healthy_count
FROM reorder_alerts
GROUP BY lead_time_bucket
ORDER BY MIN(lead_time_days);
"""

# ==========================================
# QUERY 12: EXECUTIVE DASHBOARD SUMMARY
# ==========================================
QUERY_EXECUTIVE_SUMMARY = """
SELECT 
    'Inventory Health' as metric_category,
    'Total Products Monitored' as metric,
    COUNT(DISTINCT product_id) as value
FROM reorder_alerts

UNION ALL

SELECT 
    'Inventory Health' as metric_category,
    'Critical Restock Required' as metric,
    COUNT(*) as value
FROM reorder_alerts
WHERE alert_status = 'CRITICAL RESTOCK'

UNION ALL

SELECT 
    'Inventory Health' as metric_category,
    'On Watchlist' as metric,
    COUNT(*) as value
FROM reorder_alerts
WHERE alert_status = 'WATCHLIST'

UNION ALL

SELECT 
    'Inventory Health' as metric_category,
    'Healthy Status' as metric,
    COUNT(*) as value
FROM reorder_alerts
WHERE alert_status = 'HEALTHY'

UNION ALL

SELECT 
    'Demand Forecast' as metric_category,
    'Total 7-Day Predicted Demand' as metric,
    SUM(predicted_demand_7day) as value
FROM reorder_alerts

UNION ALL

SELECT 
    'Demand Forecast' as metric_category,
    'Average Days Inventory Remaining' as metric,
    ROUND(AVG(days_inventory_remaining), 1) as value
FROM reorder_alerts

UNION ALL

SELECT 
    'Inventory Value' as metric_category,
    'Total Inventory Units' as metric,
    SUM(current_inventory) as value
FROM reorder_alerts;
"""


# ==========================================
# DICTIONARY FOR EASY ACCESS
# ==========================================

OPERATIONAL_QUERIES = {
    'critical_actions': QUERY_CRITICAL_ACTIONS,
    'inventory_health': QUERY_INVENTORY_HEALTH,
    'demand_forecast': QUERY_DEMAND_FORECAST_BY_CATEGORY,
    'forecast_accuracy': QUERY_FORECAST_ACCURACY,
    'days_to_stockout': QUERY_DAYS_TO_STOCKOUT,
    'product_performance': QUERY_PRODUCT_PERFORMANCE,
    'reorder_optimization': QUERY_REORDER_OPTIMIZATION,
    'inventory_turnover': QUERY_INVENTORY_TURNOVER,
    'weekly_trend': QUERY_WEEKLY_DEMAND_TREND,
    'alert_history': QUERY_ALERT_HISTORY,
    'inventory_by_lead_time': QUERY_INVENTORY_BY_LEAD_TIME,
    'executive_summary': QUERY_EXECUTIVE_SUMMARY
}


def print_query(query_name):
    """Print a query by name."""
    if query_name in OPERATIONAL_QUERIES:
        print(f"\n{'=' * 80}")
        print(f"QUERY: {query_name.upper()}")
        print(f"{'=' * 80}\n")
        print(OPERATIONAL_QUERIES[query_name])
        print(f"\n{'=' * 80}\n")
    else:
        print(f"Query '{query_name}' not found.")
        print(f"Available queries: {', '.join(OPERATIONAL_QUERIES.keys())}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query_name = sys.argv[1]
        print_query(query_name)
    else:
        print("Available Operational Queries:")
        print("=" * 50)
        for idx, query_name in enumerate(OPERATIONAL_QUERIES.keys(), 1):
            print(f"{idx:2d}. {query_name}")
        print("\nUsage: python sql_queries.py <query_name>")
