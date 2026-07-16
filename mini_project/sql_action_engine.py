"""
PHASE 3: SQL ACTION ENGINE
Saves ML predictions to database and calculates intelligent reorder points
with automated operational alerts (CRITICAL RESTOCK, WATCHLIST, HEALTHY).
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = "retail_demand_forecast.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

def build_simple_forecasts_dataframe():
    """Create a lightweight 7-day forecast directly from recent sales history."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            products_df = pd.read_sql_query("SELECT product_id, product_name, category FROM products", conn)
            sales_df = pd.read_sql_query(
                "SELECT product_id, quantity_sold, transaction_date FROM sales_transactions ORDER BY transaction_date",
                conn,
            )

        if products_df.empty or sales_df.empty:
            return pd.DataFrame()

        sales_df['transaction_date'] = pd.to_datetime(sales_df['transaction_date'], errors='coerce')
        sales_df = sales_df.dropna(subset=['transaction_date'])

        forecast_rows = []
        for _, product in products_df.iterrows():
            product_sales = sales_df[sales_df['product_id'] == product['product_id']].copy()
            if product_sales.empty:
                continue
            recent_sales = product_sales.sort_values('transaction_date').tail(7)
            avg_daily = recent_sales['quantity_sold'].mean() if not recent_sales.empty else 0
            base_qty = max(1, int(round(avg_daily)))

            for day_ahead in range(1, 8):
                predicted_qty = max(1, int(round(base_qty * (1 + 0.02 * day_ahead))))
                forecast_rows.append({
                    'product_id': product['product_id'],
                    'forecast_date': datetime.now().date() + timedelta(days=day_ahead),
                    'predicted_quantity': predicted_qty,
                    'confidence_interval_lower': max(1, int(round(predicted_qty * 0.8))),
                    'confidence_interval_upper': max(1, int(round(predicted_qty * 1.2))),
                    'forecast_created_at': datetime.now(),
                })

        return pd.DataFrame(forecast_rows)
    except Exception as e:
        logger.warning(f"Falling back to simple forecast generation: {str(e)}")
        return pd.DataFrame()


def build_simple_alerts_dataframe():
    """Create simple reorder alerts directly from current inventory and recent demand."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            products_df = pd.read_sql_query(
                "SELECT product_id, product_name, category, current_inventory, lead_time_days, safety_stock_units FROM products",
                conn,
            )

        if products_df.empty:
            return pd.DataFrame()

        forecasts_df = build_simple_forecasts_dataframe()
        if forecasts_df.empty:
            return pd.DataFrame()

        alerts = []
        for _, product in products_df.iterrows():
            product_forecast = forecasts_df[forecasts_df['product_id'] == product['product_id']]
            if product_forecast.empty:
                continue
            avg_daily_forecast = product_forecast['predicted_quantity'].mean()
            reorder_point = int(round((avg_daily_forecast * product['lead_time_days']) + product['safety_stock_units']))
            days_inventory_remaining = int(round(product['current_inventory'] / avg_daily_forecast)) if avg_daily_forecast > 0 else 999

            if product['current_inventory'] < reorder_point:
                alert_status = 'CRITICAL RESTOCK'
            elif product['current_inventory'] < (reorder_point * 1.25):
                alert_status = 'WATCHLIST'
            else:
                alert_status = 'HEALTHY'

            alerts.append({
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'category': product['category'],
                'reorder_point': reorder_point,
                'current_inventory': product['current_inventory'],
                'predicted_demand_7day': int(round(product_forecast['predicted_quantity'].sum())),
                'days_inventory_remaining': days_inventory_remaining,
                'lead_time_days': product['lead_time_days'],
                'safety_stock_units': product['safety_stock_units'],
                'alert_status': alert_status,
                'action_required': 1 if alert_status == 'CRITICAL RESTOCK' else 0,
            })

        return pd.DataFrame(alerts)
    except Exception as e:
        logger.warning(f"Falling back to simple alert generation: {str(e)}")
        return pd.DataFrame()


# SQL query to calculate reorder points and generate alerts
REORDER_POINT_CALCULATION_QUERY = """
WITH forecast_aggregation AS (
    -- Aggregate 7-day forecasted demand by product
    SELECT 
        product_id,
        SUM(predicted_quantity) AS predicted_demand_7day,
        AVG(predicted_quantity) AS avg_daily_forecast,
        MIN(confidence_interval_lower) AS lower_bound_total,
        MAX(confidence_interval_upper) AS upper_bound_total
    FROM forecasted_demand
    WHERE forecast_date >= DATE('now')
      AND forecast_date <= DATE('now', '+7 days')
    GROUP BY product_id
),

reorder_calculation AS (
    -- Calculate reorder point using safety stock formula
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.current_inventory,
        p.lead_time_days,
        p.safety_stock_units,
        fa.predicted_demand_7day,
        fa.avg_daily_forecast,
        
        -- Reorder Point = (Predicted Daily Demand * Lead Time) + Safety Stock
        CAST(ROUND((fa.avg_daily_forecast * p.lead_time_days) + p.safety_stock_units) AS INTEGER) AS reorder_point,
        
        -- Days of inventory remaining
        CASE 
            WHEN fa.avg_daily_forecast > 0 
            THEN CAST(ROUND(p.current_inventory / fa.avg_daily_forecast) AS INTEGER)
            ELSE 999
        END AS days_inventory_remaining,
        
        fa.lower_bound_total,
        fa.upper_bound_total
    FROM products p
    LEFT JOIN forecast_aggregation fa ON p.product_id = fa.product_id
),

alert_generation AS (
    -- Generate operational alerts based on inventory levels
    SELECT 
        rc.product_id,
        rc.product_name,
        rc.category,
        rc.current_inventory,
        rc.reorder_point,
        rc.predicted_demand_7day,
        rc.days_inventory_remaining,
        rc.lead_time_days,
        rc.safety_stock_units,
        
        -- Alert logic: CRITICAL RESTOCK | WATCHLIST | HEALTHY
        CASE 
            WHEN rc.current_inventory < rc.reorder_point THEN 'CRITICAL RESTOCK'
            WHEN rc.current_inventory < (rc.reorder_point * 1.25) THEN 'WATCHLIST'
            ELSE 'HEALTHY'
        END AS alert_status,
        
        -- Action required flag
        CASE 
            WHEN rc.current_inventory < rc.reorder_point THEN 1
            ELSE 0
        END AS action_required,
        
        -- Recommended restock quantity
        CASE 
            WHEN rc.current_inventory < rc.reorder_point 
            THEN CAST(ROUND((rc.predicted_demand_7day * 2) - rc.current_inventory) AS INTEGER)
            ELSE 0
        END AS recommended_restock_qty
    FROM reorder_calculation rc
)

SELECT 
    product_id,
    product_name,
    category,
    current_inventory,
    reorder_point,
    predicted_demand_7day,
    days_inventory_remaining,
    lead_time_days,
    safety_stock_units,
    alert_status,
    action_required,
    recommended_restock_qty,
    DATETIME('now') AS alert_timestamp
FROM alert_generation
ORDER BY action_required DESC, alert_status DESC, current_inventory ASC;
"""

class SQLActionEngine:
    """
    SQL Action Engine that orchestrates prediction storage and alert generation.
    Closes the loop by feeding ML outputs back into operational SQL tables.
    """
    
    def __init__(self, db_url=DATABASE_URL):
        """Initialize the SQL Action Engine."""
        self.db_url = db_url
        self.engine = create_engine(db_url)
        logger.info("SQL Action Engine initialized.")
    
    def save_forecasts_to_database(self, forecast_df):
        """Save ML forecasts to the forecasted_demand table."""
        try:
            logger.info("Saving forecasts to database...")
            
            # Prepare data for insertion
            forecast_data = forecast_df.copy()
            forecast_data['forecast_created_at'] = datetime.now()
            
            # Insert into database
            with sqlite3.connect(DB_PATH) as conn:
                forecast_data.to_sql(
                    'forecasted_demand',
                    conn,
                    if_exists='append',
                    index=False
                )
            
            logger.info(f"Successfully saved {len(forecast_data)} forecast records.")
            return True
        
        except Exception as e:
            logger.error(f"Error saving forecasts: {str(e)}")
            raise
    
    def generate_reorder_alerts(self):
        """Execute reorder point calculation and generate alerts."""
        try:
            logger.info("Generating reorder alerts using SQL Action Engine...")
            
            # Execute the comprehensive reorder calculation query
            alerts_df = pd.read_sql_query(REORDER_POINT_CALCULATION_QUERY, self.engine)
            
            logger.info(f"Generated {len(alerts_df)} alert records.")
            
            # Log summary statistics
            critical_count = len(alerts_df[alerts_df['alert_status'] == 'CRITICAL RESTOCK'])
            watchlist_count = len(alerts_df[alerts_df['alert_status'] == 'WATCHLIST'])
            healthy_count = len(alerts_df[alerts_df['alert_status'] == 'HEALTHY'])
            
            logger.info(f"Alert Summary: CRITICAL={critical_count}, WATCHLIST={watchlist_count}, HEALTHY={healthy_count}")
            
            return alerts_df
        
        except Exception as e:
            logger.error(f"Error generating alerts: {str(e)}")
            raise
    
    def save_alerts_to_database(self, alerts_df):
        """Save generated alerts to the reorder_alerts table."""
        try:
            logger.info("Saving alerts to database...")
            
            required_columns = [
                'product_id', 'product_name', 'category', 'reorder_point',
                'current_inventory', 'predicted_demand_7day',
                'days_inventory_remaining', 'lead_time_days',
                'safety_stock_units', 'alert_status', 'action_required'
            ]

            for col in required_columns:
                if col not in alerts_df.columns:
                    alerts_df[col] = 0

            alerts_data = alerts_df[required_columns].copy()
            alerts_data['alert_created_at'] = datetime.now()
            
            with sqlite3.connect(DB_PATH) as conn:
                alerts_data.to_sql(
                    'reorder_alerts',
                    conn,
                    if_exists='append',
                    index=False
                )
            
            logger.info(f"Successfully saved {len(alerts_data)} alert records to database.")
            return True
        
        except Exception as e:
            logger.error(f"Error saving alerts: {str(e)}")
            raise
    
    def get_critical_actions(self, alerts_df):
        """Extract critical restock actions requiring immediate attention."""
        critical = alerts_df[alerts_df['alert_status'] == 'CRITICAL RESTOCK'].copy()
        logger.info(f"Critical actions requiring immediate attention: {len(critical)}")
        return critical
    
    def get_watchlist_products(self, alerts_df):
        """Extract products on watchlist for preventive monitoring."""
        watchlist = alerts_df[alerts_df['alert_status'] == 'WATCHLIST'].copy()
        logger.info(f"Products on watchlist for monitoring: {len(watchlist)}")
        return watchlist
    
    def generate_executive_summary(self, alerts_df):
        """Generate executive summary of inventory status."""
        summary = {
            'total_products': len(alerts_df),
            'critical_restock': len(alerts_df[alerts_df['alert_status'] == 'CRITICAL RESTOCK']),
            'watchlist': len(alerts_df[alerts_df['alert_status'] == 'WATCHLIST']),
            'healthy': len(alerts_df[alerts_df['alert_status'] == 'HEALTHY']),
            'total_7day_demand': alerts_df['predicted_demand_7day'].sum(),
            'total_current_inventory': alerts_df['current_inventory'].sum(),
            'average_days_inventory': alerts_df['days_inventory_remaining'].mean()
        }
        
        logger.info("=" * 60)
        logger.info("EXECUTIVE INVENTORY SUMMARY")
        logger.info("=" * 60)
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 60)
        
        return summary

def execute_action_engine(forecast_df=None):
    """Execute a lightweight alert workflow without requiring a separate ML pipeline."""
    try:
        if forecast_df is None:
            forecast_df = build_simple_forecasts_dataframe()

        if forecast_df.empty:
            logger.warning("No forecast data available; falling back to lightweight forecast generation.")
            forecast_df = build_simple_forecasts_dataframe()

        engine = SQLActionEngine()

        # 1. Save forecasts to database
        engine.save_forecasts_to_database(forecast_df)

        # 2. Generate reorder alerts using the current SQL logic
        alerts_df = engine.generate_reorder_alerts()
        
        # 3. Save alerts to database
        engine.save_alerts_to_database(alerts_df)
        
        # 4. Get critical actions
        critical_actions = engine.get_critical_actions(alerts_df)
        
        # 5. Get watchlist
        watchlist = engine.get_watchlist_products(alerts_df)
        
        # 6. Generate executive summary
        summary = engine.generate_executive_summary(alerts_df)
        
        logger.info("SQL Action Engine execution completed successfully!")
        
        return {
            'alerts': alerts_df,
            'critical_actions': critical_actions,
            'watchlist': watchlist,
            'summary': summary
        }
    
    except Exception as e:
        logger.error(f"SQL Action Engine failed: {str(e)}")
        raise

if __name__ == "__main__":
    # This will be called from the main orchestration script
    pass
