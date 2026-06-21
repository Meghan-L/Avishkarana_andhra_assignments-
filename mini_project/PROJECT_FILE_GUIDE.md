# PROJECT FILE GUIDE
## Dual-Engine Retail Demand Forecasting & Automated Inventory Control System

---

## 📁 DIRECTORY STRUCTURE & FILE DESCRIPTIONS

### Core Orchestration Files

#### `orchestrate.py` ⭐ **START HERE**
- **Purpose**: Main entry point that executes all four phases sequentially
- **Execution**: `python orchestrate.py`
- **Functions**:
  - Phase 1: Database setup and mock data generation
  - Phase 2: ML model training and forecasting
  - Phase 3: Prediction storage and alert generation
  - Phase 4: Validation and readiness check
- **Output**: Logs all metrics, model performance, and alert summary
- **Runtime**: ~2-3 minutes

#### `quick_start.py`
- **Purpose**: Simplified setup wizard with interactive prompts
- **Execution**: `python quick_start.py`
- **Handles**: Dependency installation, pipeline execution, dashboard launch
- **Best For**: First-time users who want guided setup

---

### PHASE 1: Database & Feature Engineering

#### `database_setup.py`
- **Purpose**: Database initialization and mock data generation
- **Key Classes**: 
  - `DemandForecastingPipeline`: Main pipeline orchestrator
- **Key Functions**:
  - `initialize_database()`: Creates DDL tables
  - `generate_mock_products()`: Creates 15 realistic products
  - `generate_mock_sales()`: Generates 180 days of sales (2700 transactions)
  - `setup_database()`: Main entry point
- **Output**: `retail_demand_forecast.db` (SQLite database)
- **Data Generated**:
  - 15 products across 5 categories
  - 180 days of historical sales with seasonality
  - Includes weekend demand boost and trend simulation

#### `feature_engineering.sql`
- **Purpose**: Advanced SQL query for feature engineering
- **Type**: Reference SQL script (not executed directly)
- **Features Engineered**:
  - Daily aggregates
  - 7-day and 30-day rolling averages
  - Window functions for lag features
  - Seasonal indicators
  - Interaction features
- **Integration**: Used by ML pipeline (embedded in `ml_pipeline.py`)
- **CTEs Used**: 
  - `daily_aggregates`: Group sales by day
  - `rolling_averages`: Calculate moving statistics
  - `feature_enrichment`: Add metadata and features

---

### PHASE 2: Machine Learning Pipeline

#### `ml_pipeline.py`
- **Purpose**: ML model training, evaluation, and forecasting
- **Key Class**: `DemandForecastingPipeline`
- **Key Methods**:
  - `load_features_from_database()`: Executes feature engineering SQL
  - `preprocess_data()`: Handles missing values, encoding, feature creation
  - `create_time_based_split()`: Temporal train/test split (prevents leakage)
  - `prepare_feature_matrix()`: Formats data for ML model
  - `train_model()`: Trains XGBoost or Random Forest
  - `generate_7day_forecasts()`: Creates 7-day predictions
  - `execute_pipeline()`: Main orchestration method
- **Model Details**:
  - Algorithm: XGBoost Regressor (default) / Random Forest (fallback)
  - Trees: 150 (XGBoost) or 100 (Random Forest)
  - Max Depth: 7 (XGBoost) or 15 (Random Forest)
  - Train/Test Split: 80/20 (temporal)
- **Evaluation Metrics**:
  - MAE (Mean Absolute Error)
  - RMSE (Root Mean Squared Error)
  - R² Score (coefficient of determination)
- **Output Files**:
  - Forecast DataFrame (used by action engine)
  - `demand_forecast_model.pkl` (trained model + scaler + encoders)

---

### PHASE 3: SQL Action Engine

#### `sql_action_engine.py`
- **Purpose**: Closes the loop by storing predictions and generating alerts
- **Key Class**: `SQLActionEngine`
- **Key Methods**:
  - `save_forecasts_to_database()`: Saves ML predictions to `forecasted_demand` table
  - `generate_reorder_alerts()`: Executes complex reorder point SQL
  - `save_alerts_to_database()`: Saves alerts to `reorder_alerts` table
  - `get_critical_actions()`: Filters CRITICAL_RESTOCK items
  - `get_watchlist_products()`: Filters WATCHLIST items
  - `generate_executive_summary()`: Aggregates KPIs
- **Reorder Point Formula**:
  ```
  Reorder Point = (Predicted Daily Demand × Lead Time) + Safety Stock
  ```
- **Alert Levels**:
  - 🔴 CRITICAL RESTOCK: Inventory < Reorder Point
  - 🟡 WATCHLIST: Inventory < Reorder Point × 1.25
  - 🟢 HEALTHY: Inventory >= Reorder Point × 1.25
- **Output Tables**:
  - `forecasted_demand`: ML predictions (105 records for 15 products × 7 days)
  - `reorder_alerts`: Operational alerts (15 records, 1 per product)

---

### PHASE 4: Streamlit Dashboard

#### `app.py`
- **Purpose**: Interactive web dashboard for real-time monitoring
- **Execution**: `streamlit run app.py`
- **Port**: http://localhost:8501
- **Key Components**:
  - **KPI Cards**: 5 metrics displayed in columns
  - **Line Chart**: Historical sales vs. 7-day forecast overlay
  - **Alert Table**: Filterable, color-coded inventory status
  - **Distribution Chart**: Alert breakdown by category
  - **Critical Actions**: Expandable cards for urgent items
  - **Sidebar**: Settings, actions, documentation
- **Features**:
  - Auto-refresh data from database
  - Interactive product selection
  - CSV export functionality
  - Color-coded alerts (red/yellow/green)
  - Confidence interval visualization
- **Caching**: 1-hour TTL for performance

---

### Configuration & Operational Files

#### `config.py`
- **Purpose**: Centralized configuration for entire system
- **Sections**:
  - Database configuration
  - Mock data generation parameters
  - Sales pattern settings
  - ML model hyperparameters
  - Forecasting configuration
  - Reorder point thresholds
  - Dashboard settings
  - Performance targets
- **Key Variables**:
  - `NUM_PRODUCTS`: Number of products (default: 15)
  - `HISTORICAL_DAYS`: Days of historical data (default: 180)
  - `ML_MODEL_TYPE`: 'xgboost' or 'random_forest'
  - `FORECAST_HORIZON`: Days ahead to forecast (default: 7)
- **Functions**:
  - `get_config_summary()`: Returns config as dictionary
  - `validate_config()`: Checks for configuration errors
- **Customization**: Modify this file to adjust system behavior

#### `sql_queries.py`
- **Purpose**: Collection of operational SQL queries for business intelligence
- **Queries (12 total)**:
  1. `QUERY_CRITICAL_ACTIONS`: Items needing immediate reorder
  2. `QUERY_INVENTORY_HEALTH`: Category-wise inventory scorecard
  3. `QUERY_DEMAND_FORECAST_BY_CATEGORY`: 7-day demand by category
  4. `QUERY_FORECAST_ACCURACY`: Compare predictions to actual sales
  5. `QUERY_DAYS_TO_STOCKOUT`: Days of inventory remaining analysis
  6. `QUERY_PRODUCT_PERFORMANCE`: Sales velocity and revenue metrics
  7. `QUERY_REORDER_OPTIMIZATION`: Safety stock recommendations
  8. `QUERY_INVENTORY_TURNOVER`: Stock movement analysis
  9. `QUERY_WEEKLY_DEMAND_TREND`: Day-of-week patterns
  10. `QUERY_ALERT_HISTORY`: Alert trend over 30 days
  11. `QUERY_INVENTORY_BY_LEAD_TIME`: Grouping by procurement lead time
  12. `QUERY_EXECUTIVE_SUMMARY`: KPI dashboard summary
- **Usage**: `python sql_queries.py <query_name>`
- **Integration**: Copy-paste queries into SQLite/PostgreSQL clients

---

### Testing & Validation

#### `validate_system.py`
- **Purpose**: Comprehensive system validation and health checking
- **Execution**: `python validate_system.py`
- **Validation Checks (13 total)**:
  1. Database file exists
  2. All tables created
  3. Products data populated
  4. Sales data exists
  5. Forecasts generated
  6. Alerts generated
  7. Data integrity (no orphaned records)
  8. Historical data spans ~180 days
  9. All products have forecasts
  10. Alerts properly distributed
  11. Forecast values reasonable
  12. Reorder logic correct
  13. Model file exists
- **Output**: Detailed pass/fail report + health metrics
- **Run When**: After completing pipeline for production deployment

---

### Documentation & Setup

#### `README.md`
- **Purpose**: Comprehensive project documentation
- **Sections**:
  - Overview of dual-engine architecture
  - Project structure
  - Technology stack
  - Quick start guide
  - Detailed system architecture
  - Database schema
  - Advanced SQL queries
  - Troubleshooting
  - Production deployment checklist
- **Length**: ~500 lines of detailed documentation

#### `requirements.txt`
- **Purpose**: Python dependencies specification
- **Packages**:
  - pandas, numpy: Data manipulation
  - scikit-learn: ML preprocessing
  - xgboost: ML model
  - sqlalchemy: Database ORM
  - streamlit: Dashboard framework
  - plotly: Interactive charts
  - python-dateutil: Date utilities
- **Installation**: `pip install -r requirements.txt`

#### `.gitignore`
- **Purpose**: Version control exclusion rules
- **Excludes**:
  - Database files (*.db, *.sqlite)
  - Model artifacts (*.pkl, *.joblib)
  - Python cache (__pycache__, *.pyc)
  - Virtual environments
  - IDE configurations
  - Logs and temporary files
  - OS files

#### `PROJECT_FILE_GUIDE.md` (This File)
- **Purpose**: Detailed description of all project files
- **Sections**: Organization by phase and function

---

## 🚀 EXECUTION FLOW

### Option A: Full Pipeline (Recommended)
```bash
python orchestrate.py
```
Executes: Database Setup → ML Training → Action Engine → Ready Check

### Option B: Step-by-Step
```bash
python database_setup.py                # Phase 1
python ml_pipeline.py                   # Phase 2
python sql_action_engine.py             # Phase 3
streamlit run app.py                    # Phase 4
```

### Option C: Interactive Setup
```bash
python quick_start.py
```
Guided setup with prompts

### Option D: Validation Only
```bash
python validate_system.py
```
Health check of existing system

---

## 📊 DATABASE TABLES

### `products`
- product_id (PK), product_name, category, unit_price
- lead_time_days, safety_stock_units, current_inventory

### `sales_transactions`
- transaction_id (PK), product_id (FK), quantity_sold, sale_price
- transaction_date, day_of_week

### `inventory_logs`
- log_id (PK), product_id (FK), stock_before, stock_after
- transaction_type, log_date

### `forecasted_demand`
- forecast_id (PK), product_id (FK), forecast_date
- predicted_quantity, confidence_interval_lower/upper
- forecast_created_at

### `reorder_alerts`
- alert_id (PK), product_id (FK), product_name, reorder_point
- current_inventory, predicted_demand_7day, alert_status
- action_required, alert_created_at

---

## 🎯 KEY METRICS & OUTPUTS

### From ML Pipeline
- MAE: Mean Absolute Error (units)
- RMSE: Root Mean Squared Error (units)
- R² Score: Variance explained (0-1)
- 105 Forecast records: 15 products × 7 days

### From Action Engine
- Reorder Points: Calculated for all products
- Alert Status: CRITICAL/WATCHLIST/HEALTHY
- 15 Alert records: One per product

### Dashboard KPIs
- Total Predicted Demand (7-day)
- Critical Restock Count
- Watchlist Count
- Healthy Count
- Average Days Inventory

---

## 🔧 CUSTOMIZATION POINTS

1. **Adjust Data Generation**:
   - Edit `database_setup.py`: `NUM_PRODUCTS`, `HISTORICAL_DAYS`

2. **Tune ML Model**:
   - Edit `config.py`: `XGBOOST_PARAMS` or `RANDOM_FOREST_PARAMS`

3. **Change Alert Thresholds**:
   - Edit `config.py`: `CRITICAL_THRESHOLD`, `WATCHLIST_THRESHOLD`

4. **Add More Features**:
   - Edit `feature_engineering.sql`: Add more CTEs
   - Update `ml_pipeline.py`: `NUMERICAL_FEATURES` list

5. **Customize Dashboard**:
   - Edit `app.py`: Add/modify Streamlit components

---

## ✅ PRODUCTION DEPLOYMENT CHECKLIST

- [ ] Run `python validate_system.py` - all checks pass
- [ ] Review model metrics (MAE, RMSE, R²)
- [ ] Test dashboard with sample data
- [ ] Set up daily pipeline execution (cron job)
- [ ] Configure database backups
- [ ] Document operational procedures
- [ ] Train operations team on dashboard
- [ ] Set up alerts for critical items
- [ ] Monitor forecast accuracy vs actual

---

## 📞 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Database locked | Close all connections, delete .db file, re-run |
| Dashboard shows no data | Run `orchestrate.py` first |
| XGBoost import error | `pip install --upgrade xgboost` |
| Model not saving | Check write permissions in directory |

---

## 📈 SYSTEM COMPONENTS SUMMARY

| Component | Files | Purpose |
|-----------|-------|---------|
| Database Layer | database_setup.py | Data storage & retrieval |
| Feature Engineering | feature_engineering.sql | Advanced SQL transformations |
| ML Pipeline | ml_pipeline.py | Model training & forecasting |
| Operations Layer | sql_action_engine.py | Alert generation |
| UI/Dashboard | app.py | Real-time monitoring |
| Configuration | config.py | System parameters |
| Utilities | sql_queries.py, validate_system.py | Queries & validation |

---

**Total Files**: 11 Python files + 2 SQL/Reference files + 3 Config files = 16 files
**Total Lines of Code**: ~3,500+ lines of production-ready code
**Documentation**: Comprehensive README + inline comments

---

*Last Updated: January 2024*
