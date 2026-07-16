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

def execute_action_engine(forecast_df):
    """Execute the complete SQL Action Engine workflow."""
    try:
        engine = SQLActionEngine()
        
        # 1. Save forecasts to database
        engine.save_forecasts_to_database(forecast_df)
        
        # 2. Generate reorder alerts using advanced SQL
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
