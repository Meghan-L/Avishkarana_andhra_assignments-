"""
CONFIGURATION FILE
Centralized configuration for the entire system.
Modify these settings to customize the system for your specific needs.
"""

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE_TYPE = "sqlite"  # Options: "sqlite", "postgresql"
DATABASE_PATH = "retail_demand_forecast.db"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_NAME = "retail_forecast"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = ""

# Generate DATABASE_URL based on type
if DATABASE_TYPE == "sqlite":
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
else:
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


# ==========================================
# MOCK DATA GENERATION
# ==========================================

# Number of products to generate
NUM_PRODUCTS = 15

# Product categories
PRODUCT_CATEGORIES = ["Electronics", "Home & Garden", "Sports", "Food & Beverage", "Fashion"]

# Days of historical data to generate
HISTORICAL_DAYS = 180

# Price range (in currency units)
MIN_PRODUCT_PRICE = 10
MAX_PRODUCT_PRICE = 500

# Inventory range
MIN_INITIAL_INVENTORY = 100
MAX_INITIAL_INVENTORY = 500

# Lead time range (days)
MIN_LEAD_TIME = 3
MAX_LEAD_TIME = 15

# Safety stock range
MIN_SAFETY_STOCK = 20
MAX_SAFETY_STOCK = 100

# Base demand range (units per day)
MIN_BASE_DEMAND = 20
MAX_BASE_DEMAND = 150


# ==========================================
# SALES PATTERN CONFIGURATION
# ==========================================

# Weekend sales multiplier (1.3 = 30% higher on weekends)
WEEKEND_DEMAND_MULTIPLIER = 1.3

# Trend multiplier (0.2 = 20% increase over 180 days)
TREND_MULTIPLIER = 0.2

# Noise/variance in demand (0.15 = ±15% random variation)
DEMAND_NOISE_STD = 0.15


# ==========================================
# ML MODEL CONFIGURATION
# ==========================================

# Model type: "xgboost" or "random_forest"
ML_MODEL_TYPE = "xgboost"

# Test set size (fraction)
TEST_SIZE = 0.2

# XGBoost hyperparameters
XGBOOST_PARAMS = {
    'n_estimators': 150,
    'max_depth': 7,
    'learning_rate': 0.05,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'tree_method': 'hist',
    'device': 'cpu'
}

# Random Forest hyperparameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}

# Feature scaling method
FEATURE_SCALING = 'standard'  # Options: "standard", "minmax", "robust"

# Random seed for reproducibility
RANDOM_SEED = 42


# ==========================================
# FORECASTING CONFIGURATION
# ==========================================

# Number of days to forecast ahead
FORECAST_HORIZON = 7

# Decay factor for forecasts further in future (0.98 = 2% decrease per day)
FORECAST_DECAY_FACTOR = 0.98

# Confidence interval width (0.2 = ±20%)
CONFIDENCE_INTERVAL_WIDTH = 0.2


# ==========================================
# REORDER POINT CONFIGURATION
# ==========================================

# Reorder point formula: (Predicted Daily Demand * Lead Time) + Safety Stock
# Alert thresholds (as multipliers of reorder point)
CRITICAL_THRESHOLD = 1.0      # At or below reorder point
WATCHLIST_THRESHOLD = 1.25    # 25% above reorder point
HEALTHY_THRESHOLD = 1.25      # Above watchlist threshold

# Recommended restock quantity multiplier (days of demand to stock)
RESTOCK_MULTIPLIER = 2.0  # Stock for 2x the 7-day forecast


# ==========================================
# FEATURE ENGINEERING
# ==========================================

# Rolling window sizes (days)
ROLLING_7DAY = 7
ROLLING_30DAY = 30

# Lag features (days ago)
LAG_1_DAY = 1
LAG_7_DAY = 7

# Categorical features to encode
CATEGORICAL_FEATURES = ['category', 'day_of_week']

# Numerical features to scale
NUMERICAL_FEATURES = [
    'unit_price', 'lead_time_days', 'safety_stock_units', 'avg_price',
    'transaction_count', 'is_weekend', 'rolling_7day_avg', 'rolling_30day_avg',
    'prev_day_quantity', 'quantity_7day_ago', 'month', 'quarter'
]

# Interaction features to create
CREATE_INTERACTION_FEATURES = True


# ==========================================
# LOGGING CONFIGURATION
# ==========================================

LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# ==========================================
# DASHBOARD CONFIGURATION
# ==========================================

# Streamlit page layout
STREAMLIT_LAYOUT = "wide"  # Options: "centered", "wide"

# Dashboard refresh cache TTL (seconds)
CACHE_TTL = 3600  # 1 hour

# Maximum rows to display in alert table
MAX_ROWS_DISPLAY = 100

# Color scheme for alerts
ALERT_COLORS = {
    'CRITICAL RESTOCK': '#ff4444',
    'WATCHLIST': '#ffaa00',
    'HEALTHY': '#44aa44'
}

# Chart height (pixels)
CHART_HEIGHT = 450


# ==========================================
# EXPORT CONFIGURATION
# ==========================================

# Enable CSV export
ENABLE_CSV_EXPORT = True

# Export directory
EXPORT_DIRECTORY = "./exports"

# Default export columns
EXPORT_COLUMNS = [
    'product_id', 'product_name', 'category', 
    'current_inventory', 'reorder_point', 'predicted_demand_7day',
    'alert_status', 'action_required', 'alert_created_at'
]


# ==========================================
# FILE PATHS
# ==========================================

MODEL_SAVE_PATH = "demand_forecast_model.pkl"
SQL_QUERIES_PATH = "sql_queries/"


# ==========================================
# ALERT NOTIFICATIONS
# ==========================================

# Enable email notifications for critical alerts
ENABLE_EMAIL_ALERTS = False

# Email configuration (only if enabled)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
RECIPIENT_EMAILS = ["operations@company.com", "manager@company.com"]

# Minimum days to send alert (avoid duplicate alerts within X days)
MIN_DAYS_BETWEEN_ALERTS = 1


# ==========================================
# PERFORMANCE TARGETS
# ==========================================

# Target forecast accuracy metrics
TARGET_MAE = 15.0          # Units
TARGET_RMSE = 25.0         # Units
TARGET_R2_SCORE = 0.85     # Percentage of variance explained

# Target inventory metrics
TARGET_STOCKOUT_RATE = 0.02          # 2% stockout rate
TARGET_INVENTORY_DAYS = 30           # Days of inventory on hand
TARGET_FORECAST_ACCURACY = 0.85      # 85% accuracy


# ==========================================
# SYSTEM BEHAVIOR
# ==========================================

# Auto-reorder enabled
AUTO_REORDER_ENABLED = False  # Set to True for automated purchasing

# Minimum inventory check frequency (hours)
INVENTORY_CHECK_FREQUENCY = 24

# Pipeline execution schedule (if running as service)
PIPELINE_SCHEDULE_HOUR = 3    # 3 AM daily
PIPELINE_SCHEDULE_MINUTE = 0


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def get_config_summary():
    """Return a summary of current configuration."""
    return {
        'database_url': DATABASE_URL,
        'num_products': NUM_PRODUCTS,
        'historical_days': HISTORICAL_DAYS,
        'ml_model': ML_MODEL_TYPE,
        'forecast_horizon': FORECAST_HORIZON,
        'test_size': TEST_SIZE,
        'random_seed': RANDOM_SEED
    }

def validate_config():
    """Validate configuration values."""
    errors = []
    
    if NUM_PRODUCTS < 1:
        errors.append("NUM_PRODUCTS must be >= 1")
    
    if HISTORICAL_DAYS < 7:
        errors.append("HISTORICAL_DAYS must be >= 7")
    
    if not (0 < TEST_SIZE < 1):
        errors.append("TEST_SIZE must be between 0 and 1")
    
    if FORECAST_HORIZON < 1:
        errors.append("FORECAST_HORIZON must be >= 1")
    
    if ML_MODEL_TYPE not in ["xgboost", "random_forest"]:
        errors.append("ML_MODEL_TYPE must be 'xgboost' or 'random_forest'")
    
    if DATABASE_TYPE not in ["sqlite", "postgresql"]:
        errors.append("DATABASE_TYPE must be 'sqlite' or 'postgresql'")
    
    return errors

if __name__ == "__main__":
    print("Configuration Summary:")
    print("=" * 50)
    for key, value in get_config_summary().items():
        print(f"{key}: {value}")
    
    print("\nValidating configuration...")
    errors = validate_config()
    if errors:
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuration is valid!")
