"""
PHASE 1: SQL DATABASE SETUP & FEATURE ENGINEERING
Database initialization with realistic mock data generation for retail demand forecasting.
Spans 180 days of time-series data with realistic trends and seasonality.
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

# DDL Scripts
DDL_SCRIPTS = {
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            lead_time_days INTEGER NOT NULL DEFAULT 7,
            safety_stock_units INTEGER NOT NULL DEFAULT 50,
            current_inventory INTEGER NOT NULL DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "sales_transactions": """
        CREATE TABLE IF NOT EXISTS sales_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL,
            sale_price REAL NOT NULL,
            transaction_date DATE NOT NULL,
            day_of_week TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """,
    "inventory_logs": """
        CREATE TABLE IF NOT EXISTS inventory_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            stock_before INTEGER NOT NULL,
            stock_after INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """,
    "forecasted_demand": """
        CREATE TABLE IF NOT EXISTS forecasted_demand (
            forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            forecast_date DATE NOT NULL,
            predicted_quantity INTEGER NOT NULL,
            confidence_interval_lower REAL,
            confidence_interval_upper REAL,
            forecast_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """,
    "reorder_alerts": """
        CREATE TABLE IF NOT EXISTS reorder_alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Unknown',
            reorder_point INTEGER NOT NULL,
            current_inventory INTEGER NOT NULL,
            predicted_demand_7day INTEGER NOT NULL,
            days_inventory_remaining INTEGER NOT NULL DEFAULT 0,
            lead_time_days INTEGER NOT NULL DEFAULT 7,
            safety_stock_units INTEGER NOT NULL DEFAULT 50,
            alert_status TEXT NOT NULL,
            action_required INTEGER DEFAULT 1,
            alert_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """
}

def initialize_database():
    """Initialize SQLite database with DDL scripts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for table_name in DDL_SCRIPTS.keys():
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        for table_name, ddl_script in DDL_SCRIPTS.items():
            logger.info(f"Creating table: {table_name}")
            cursor.execute(ddl_script)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def generate_mock_products(num_products=15):
    """Generate realistic product data."""
    categories = ["Electronics", "Home & Garden", "Sports", "Food & Beverage", "Fashion"]
    products = []
    
    np.random.seed(42)
    for i in range(1, num_products + 1):
        products.append({
            'product_id': i,
            'product_name': f"Product_{chr(65 + (i % 26))}{i}",
            'category': np.random.choice(categories),
            'unit_price': round(np.random.uniform(10, 500), 2),
            'lead_time_days': np.random.randint(3, 15),
            'safety_stock_units': np.random.randint(20, 100),
            'current_inventory': np.random.randint(100, 500)
        })
    
    return pd.DataFrame(products)

def generate_mock_sales(products_df, days=180):
    """Generate 180 days of realistic time-series sales data with trends and seasonality."""
    transactions = []
    np.random.seed(42)
    
    start_date = datetime.now() - timedelta(days=days)
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for product_id in products_df['product_id'].values:
        product_row = products_df[products_df['product_id'] == product_id].iloc[0]
        base_demand = np.random.uniform(20, 150)
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            day_of_week = days_of_week[current_date.weekday()]
            
            # Add seasonality: higher sales on weekends
            weekend_multiplier = 1.3 if current_date.weekday() >= 4 else 1.0
            
            # Add trend: slight increase over time
            trend_multiplier = 1.0 + (day_offset / days) * 0.2
            
            # Add random noise
            noise = np.random.normal(1.0, 0.15)
            
            # Calculate quantity with all factors
            quantity = max(1, int(base_demand * weekend_multiplier * trend_multiplier * noise))
            
            transactions.append({
                'product_id': product_id,
                'quantity_sold': quantity,
                'sale_price': product_row['unit_price'] * np.random.uniform(0.9, 1.1),
                'transaction_date': current_date.date(),
                'day_of_week': day_of_week
            })
    
    return pd.DataFrame(transactions)

def populate_sales_transactions(transactions_df):
    """Insert sales transactions into database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        transactions_df.to_sql('sales_transactions', conn, if_exists='replace', index=False)
        conn.close()
        logger.info(f"Inserted {len(transactions_df)} sales transactions.")
    except Exception as e:
        logger.error(f"Error inserting sales transactions: {str(e)}")
        raise

def populate_products(products_df):
    """Insert products into database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        products_df.to_sql('products', conn, if_exists='replace', index=False)
        conn.close()
        logger.info(f"Inserted {len(products_df)} products.")
    except Exception as e:
        logger.error(f"Error inserting products: {str(e)}")
        raise

def setup_database():
    """Main function to initialize and populate the database."""
    logger.info("Starting database setup...")
    
    # Initialize database structure
    initialize_database()
    
    # Generate and populate mock data
    logger.info("Generating mock product data...")
    products_df = generate_mock_products(num_products=15)
    populate_products(products_df)
    
    logger.info("Generating 180 days of mock sales transactions...")
    transactions_df = generate_mock_sales(products_df, days=180)
    populate_sales_transactions(transactions_df)
    
    logger.info("Database setup completed successfully!")
    return DB_PATH, DATABASE_URL

if __name__ == "__main__":
    setup_database()
