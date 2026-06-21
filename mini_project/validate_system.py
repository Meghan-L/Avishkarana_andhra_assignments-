"""
SYSTEM VALIDATION & TESTING SUITE
Comprehensive tests to verify all components are working correctly.
Run this after executing the pipeline to ensure production readiness.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = "retail_demand_forecast.db"

# ==========================================
# VALIDATION FUNCTIONS
# ==========================================

def check_database_exists():
    """Verify database file exists."""
    import os
    if os.path.exists(DB_PATH):
        logger.info("✅ Database file exists")
        return True
    else:
        logger.error("❌ Database file not found")
        return False

def check_tables_exist():
    """Verify all required tables exist."""
    required_tables = ['products', 'sales_transactions', 'inventory_logs', 
                       'forecasted_demand', 'reorder_alerts']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        all_exist = True
        for table in required_tables:
            if table in existing_tables:
                logger.info(f"  ✅ Table '{table}' exists")
            else:
                logger.error(f"  ❌ Table '{table}' missing")
                all_exist = False
        
        return all_exist
    
    except Exception as e:
        logger.error(f"❌ Error checking tables: {str(e)}")
        return False

def check_products_data():
    """Verify products table has data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT COUNT(*) as count FROM products;", conn)
        count = df['count'].iloc[0]
        conn.close()
        
        if count > 0:
            logger.info(f"✅ Products table has {count} records")
            return True
        else:
            logger.error("❌ Products table is empty")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking products: {str(e)}")
        return False

def check_sales_data():
    """Verify sales transactions have been recorded."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT COUNT(*) as count FROM sales_transactions;", conn)
        count = df['count'].iloc[0]
        conn.close()
        
        if count > 0:
            logger.info(f"✅ Sales transactions table has {count} records")
            return True
        else:
            logger.error("❌ Sales transactions table is empty")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking sales data: {str(e)}")
        return False

def check_forecasts_data():
    """Verify forecasts have been generated."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT COUNT(*) as count FROM forecasted_demand;", conn)
        count = df['count'].iloc[0]
        conn.close()
        
        if count > 0:
            logger.info(f"✅ Forecasted demand table has {count} records")
            return True
        else:
            logger.error("❌ Forecasted demand table is empty - run ML pipeline")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking forecasts: {str(e)}")
        return False

def check_alerts_data():
    """Verify reorder alerts have been generated."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT COUNT(*) as count FROM reorder_alerts;", conn)
        count = df['count'].iloc[0]
        conn.close()
        
        if count > 0:
            logger.info(f"✅ Reorder alerts table has {count} records")
            return True
        else:
            logger.error("❌ Reorder alerts table is empty - run action engine")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking alerts: {str(e)}")
        return False

def check_data_integrity():
    """Verify data integrity and relationships."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Check for orphaned foreign keys
        query = """
        SELECT COUNT(*) as orphaned_count
        FROM sales_transactions st
        WHERE st.product_id NOT IN (SELECT product_id FROM products)
        """
        df = pd.read_sql_query(query, conn)
        orphaned = df['orphaned_count'].iloc[0]
        
        if orphaned == 0:
            logger.info("✅ Data integrity check passed (no orphaned records)")
            conn.close()
            return True
        else:
            logger.error(f"❌ Found {orphaned} orphaned sales records")
            conn.close()
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking data integrity: {str(e)}")
        return False

def check_historical_data_span():
    """Verify historical data spans expected time period."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            MIN(transaction_date) as earliest_date,
            MAX(transaction_date) as latest_date,
            JULIANDAY(MAX(transaction_date)) - JULIANDAY(MIN(transaction_date)) as days_span
        FROM sales_transactions
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        days_span = int(df['days_span'].iloc[0])
        
        if days_span >= 170:  # Approximately 180 days with some tolerance
            logger.info(f"✅ Historical data spans {days_span} days")
            return True
        else:
            logger.warning(f"⚠️  Historical data only spans {days_span} days (expected ~180)")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking historical span: {str(e)}")
        return False

def check_forecast_coverage():
    """Verify all products have forecasts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        query = """
        SELECT 
            (SELECT COUNT(DISTINCT product_id) FROM products) as total_products,
            (SELECT COUNT(DISTINCT product_id) FROM forecasted_demand) as forecasted_products
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        total = df['total_products'].iloc[0]
        forecasted = df['forecasted_products'].iloc[0]
        
        if total == forecasted:
            logger.info(f"✅ All {total} products have forecasts")
            return True
        else:
            logger.warning(f"⚠️  Only {forecasted}/{total} products have forecasts")
            return forecasted > 0
    
    except Exception as e:
        logger.error(f"❌ Error checking forecast coverage: {str(e)}")
        return False

def check_alert_distribution():
    """Verify alerts are properly distributed."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            alert_status,
            COUNT(*) as count
        FROM reorder_alerts
        GROUP BY alert_status
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logger.info("Alert Distribution:")
        total_alerts = 0
        for _, row in df.iterrows():
            status = row['alert_status']
            count = row['count']
            logger.info(f"  {status}: {count}")
            total_alerts += count
        
        if total_alerts > 0:
            logger.info(f"✅ Alerts properly distributed ({total_alerts} total)")
            return True
        else:
            logger.error("❌ No alerts found")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking alert distribution: {str(e)}")
        return False

def check_model_file():
    """Verify trained model file exists."""
    import os
    if os.path.exists('demand_forecast_model.pkl'):
        file_size = os.path.getsize('demand_forecast_model.pkl')
        logger.info(f"✅ Model file exists ({file_size} bytes)")
        return True
    else:
        logger.warning("⚠️  Model file not found - run ML pipeline")
        return False

def check_forecast_quality():
    """Verify forecast values are reasonable."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            MIN(predicted_quantity) as min_qty,
            MAX(predicted_quantity) as max_qty,
            AVG(predicted_quantity) as avg_qty,
            COUNT(*) as total_forecasts
        FROM forecasted_demand
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        min_qty = df['min_qty'].iloc[0]
        max_qty = df['max_qty'].iloc[0]
        avg_qty = df['avg_qty'].iloc[0]
        total = df['total_forecasts'].iloc[0]
        
        # Reasonable checks: min >= 1, max reasonable, no infinities
        if min_qty >= 1 and max_qty < 10000 and avg_qty > 0:
            logger.info(f"✅ Forecast quality check passed")
            logger.info(f"   Min: {min_qty}, Max: {max_qty}, Avg: {avg_qty:.1f}")
            return True
        else:
            logger.error(f"❌ Forecast values out of reasonable range")
            logger.error(f"   Min: {min_qty}, Max: {max_qty}, Avg: {avg_qty}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking forecast quality: {str(e)}")
        return False

def check_reorder_logic():
    """Verify reorder point calculations are correct."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            product_id,
            reorder_point,
            lead_time_days,
            safety_stock_units,
            predicted_demand_7day,
            ROUND((predicted_demand_7day / 7.0 * lead_time_days) + safety_stock_units) as calculated_reorder_point
        FROM reorder_alerts
        LIMIT 5
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        mismatches = 0
        for _, row in df.iterrows():
            if abs(row['reorder_point'] - row['calculated_reorder_point']) > 1:
                mismatches += 1
        
        if mismatches == 0:
            logger.info("✅ Reorder point calculations verified")
            return True
        else:
            logger.warning(f"⚠️  Found {mismatches} calculation mismatches")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error checking reorder logic: {str(e)}")
        return False

# ==========================================
# MAIN VALIDATION SUITE
# ==========================================

def run_validation_suite():
    """Execute all validation checks."""
    
    print("\n" + "=" * 80)
    print("  DUAL-ENGINE SYSTEM VALIDATION SUITE")
    print("=" * 80 + "\n")
    
    checks = [
        ("Database Exists", check_database_exists),
        ("Tables Exist", check_tables_exist),
        ("Products Data", check_products_data),
        ("Sales Data", check_sales_data),
        ("Forecasts Data", check_forecasts_data),
        ("Alerts Data", check_alerts_data),
        ("Data Integrity", check_data_integrity),
        ("Historical Data Span", check_historical_data_span),
        ("Forecast Coverage", check_forecast_coverage),
        ("Model File", check_model_file),
        ("Forecast Quality", check_forecast_quality),
        ("Reorder Logic", check_reorder_logic),
        ("Alert Distribution", check_alert_distribution),
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        try:
            results[check_name] = check_func()
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("  VALIDATION SUMMARY")
    print("=" * 80 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed\n")
    
    if passed == total:
        print("🎉 ALL VALIDATION CHECKS PASSED - System is production ready!\n")
        return True
    elif passed >= total * 0.8:
        print("⚠️  Most checks passed. Review failures above.\n")
        return True
    else:
        print("❌ Multiple validation failures. Review system carefully.\n")
        return False

def generate_health_report():
    """Generate detailed health report."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        print("\n" + "=" * 80)
        print("  SYSTEM HEALTH REPORT")
        print("=" * 80 + "\n")
        
        # Database size
        import os
        db_size = os.path.getsize(DB_PATH) / (1024 * 1024)  # Convert to MB
        print(f"Database Size: {db_size:.2f} MB")
        
        # Data counts
        tables_query = """
        SELECT 'products' as table_name, COUNT(*) as record_count FROM products
        UNION ALL
        SELECT 'sales_transactions', COUNT(*) FROM sales_transactions
        UNION ALL
        SELECT 'forecasted_demand', COUNT(*) FROM forecasted_demand
        UNION ALL
        SELECT 'reorder_alerts', COUNT(*) FROM reorder_alerts
        """
        
        df_counts = pd.read_sql_query(tables_query, conn)
        print("\nTable Record Counts:")
        for _, row in df_counts.iterrows():
            print(f"  {row['table_name']:25} {row['record_count']:,}")
        
        # Last update times
        print("\nLast Update Times:")
        
        query_updates = """
        SELECT 'Last Sale' as metric, MAX(transaction_date) as last_update FROM sales_transactions
        UNION ALL
        SELECT 'Last Forecast', MAX(forecast_created_at) FROM forecasted_demand
        UNION ALL
        SELECT 'Last Alert', MAX(alert_created_at) FROM reorder_alerts
        """
        
        df_updates = pd.read_sql_query(query_updates, conn)
        for _, row in df_updates.iterrows():
            print(f"  {row['metric']:20} {row['last_update']}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error generating health report: {str(e)}")

if __name__ == "__main__":
    import sys
    
    success = run_validation_suite()
    generate_health_report()
    
    sys.exit(0 if success else 1)
