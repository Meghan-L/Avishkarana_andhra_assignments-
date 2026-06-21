# 📊 Dual-Engine Retail Demand Forecasting & Automated Inventory Control System

A **production-ready, enterprise-grade** system that combines advanced SQL feature engineering, machine learning, and operational automation for real-time retail demand forecasting and intelligent inventory management.

## 🎯 Project Overview

This system implements a sophisticated dual-engine architecture:

### **SQL Engine** 
- Advanced feature engineering using CTEs (Common Table Expressions) and Window Functions
- Rolling averages (7-day, 30-day), lag features, and seasonal indicators
- Automated reorder point calculation with safety stock optimization
- Real-time inventory status monitoring and alert generation

### **ML Engine**
- XGBoost-based time-series demand forecasting model
- Proper train/test splitting based on temporal ordering to prevent data leakage
- Comprehensive evaluation metrics (MAE, RMSE, R² Score)
- 7-day ahead predictions with confidence intervals (±20%)
- Model persistence for production deployment

### **Action Engine**
- Closes the loop by feeding ML predictions back into SQL for operational decisions
- Calculates intelligent reorder points: **Reorder Point = (Daily Demand × Lead Time) + Safety Stock**
- Generates three-tier automated alerts:
  - 🔴 **CRITICAL RESTOCK**: Inventory below reorder point
  - 🟡 **WATCHLIST**: Inventory approaching reorder point
  - 🟢 **HEALTHY**: Sufficient inventory levels

### **Streamlit Dashboard**
- Real-time KPI metrics and performance indicators
- Interactive forecast vs. historical sales comparison charts
- Comprehensive inventory alert table with filtering capabilities
- Category-wise alert distribution analysis
- One-click export of operational reports

---

## 📁 Project Structure

```
mini_project/
├── database_setup.py           # Phase 1: Database initialization & mock data generation
├── feature_engineering.sql     # Phase 1: Advanced SQL feature engineering queries
├── ml_pipeline.py              # Phase 2: ML model training & forecasting
├── sql_action_engine.py        # Phase 3: Predictions storage & alert generation
├── app.py                      # Phase 4: Streamlit interactive dashboard
├── orchestrate.py              # Main orchestration script (run all phases)
├── requirements.txt            # Python dependencies
├── retail_demand_forecast.db   # SQLite database (auto-created)
├── demand_forecast_model.pkl   # Trained model artifact (auto-created)
└── README.md                   # This file
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Database** | SQLite (portable) / PostgreSQL syntax compatible |
| **Feature Engineering** | SQL with CTEs, Window Functions |
| **Data Processing** | Pandas, NumPy |
| **ML Models** | XGBoost, Scikit-learn (RandomForest fallback) |
| **ORM** | SQLAlchemy |
| **Dashboard** | Streamlit |
| **Visualization** | Plotly |
| **Language** | Python 3.8+ |

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 500MB+ free disk space
- Modern web browser (for Streamlit dashboard)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Complete Pipeline

```bash
python orchestrate.py
```

This executes all four phases:
1. ✅ Database setup with 180 days of realistic mock data
2. ✅ Feature engineering and ML model training
3. ✅ Prediction storage and alert generation
4. ✅ Ready for dashboard launch

**Expected runtime**: 2-3 minutes

### Step 3: Launch the Interactive Dashboard

In a new terminal/command prompt:

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

---

## 📊 System Architecture

### Phase 1: Database Setup & Feature Engineering

**database_setup.py:**
- Creates three core tables: `products`, `sales_transactions`, `inventory_logs`
- Generates 180 days of realistic time-series data
- Includes seasonality (weekends have 30% higher demand)
- Adds realistic trends (slight demand increase over time)
- Spans 15 products across 5 categories

**feature_engineering.sql:**
Advanced SQL query with multiple CTEs:
- `daily_aggregates`: Aggregate sales by product and date
- `rolling_averages`: Calculate rolling 7-day and 30-day moving averages
- `feature_enrichment`: Combine with product metadata and seasonal indicators

**Features engineered:**
- `rolling_7day_avg`: 7-day moving average
- `rolling_30day_avg`: 30-day moving average
- `prev_day_quantity`: Previous day's sales (lag-1)
- `quantity_7day_ago`: Sales from 7 days prior
- `is_weekend`: Binary indicator for weekend sales boost
- `demand_volatility`: Standard deviation of 7-day sales
- `month`, `quarter`: Temporal features
- `inventory_to_sales_ratio`: Inventory health indicator

### Phase 2: Machine Learning Pipeline

**ml_pipeline.py:**

**Data Loading & Preprocessing:**
- Connects to SQLite via SQLAlchemy
- Executes advanced feature engineering SQL
- Handles missing values with intelligent imputation
- Encodes categorical variables (category, day_of_week)
- Creates interaction features for non-linear relationships

**Model Training:**
- **Algorithm**: XGBoost Regressor (100-150 trees)
- **Train/Test Split**: Time-based (80/20) to prevent data leakage
- **Hyperparameters**: Tuned for retail demand patterns
  - max_depth: 7
  - learning_rate: 0.05
  - subsample: 0.8
  - colsample_bytree: 0.8

**Evaluation Metrics:**
- **MAE** (Mean Absolute Error): Average prediction error in units
- **RMSE** (Root Mean Squared Error): Penalizes large errors
- **R² Score**: Percentage of variance explained

**7-Day Forecasting:**
- Uses the latest product profiles for prediction
- Applies temporal decay (0.98 multiplier per day ahead)
- Generates confidence intervals (±20%)
- Ensures minimum of 1 unit per day

### Phase 3: SQL Action Engine

**sql_action_engine.py:**

**Advanced Reorder Point Calculation:**
```
Reorder Point = (Predicted Daily Demand × Lead Time) + Safety Stock

Where:
- Predicted Daily Demand: Average forecast over next 7 days
- Lead Time: Product-specific procurement lead time
- Safety Stock: Buffer for demand variability
```

**Three-Tier Alert System:**

| Alert Level | Condition | Action |
|-------------|-----------|--------|
| 🔴 CRITICAL RESTOCK | Inventory < Reorder Point | **IMMEDIATE ORDER REQUIRED** |
| 🟡 WATCHLIST | Reorder Point × 0.75 < Inventory < Reorder Point | Monitor closely |
| 🟢 HEALTHY | Inventory > Reorder Point × 0.75 | Continue normal operations |

**Tables Created:**
- `forecasted_demand`: ML predictions (7 days × products)
- `reorder_alerts`: Operational alerts with action flags

### Phase 4: Streamlit Dashboard

**app.py:**

**KPI Metrics Dashboard:**
- 7-Day Predicted Demand (total units)
- Critical Restock Products (count)
- Watchlist Products (count)
- Healthy Products (count)
- Average Days of Inventory Remaining

**Interactive Charts:**
- Line chart: Historical sales (30 days) vs. 7-day ML forecast
- Confidence interval visualization (±20%)
- Stacked bar chart: Alert distribution by product category

**Alert Management Table:**
- Filterable by alert status
- Color-coded rows (red/yellow/green)
- Real-time inventory levels
- Reorder point comparisons
- Days inventory remaining calculation

**Critical Actions Panel:**
- Expandable cards for urgent restock items
- Recommended restock quantities
- Lead time information
- Days-until-stockout alerts

**Data Export:**
- One-click CSV export of all alerts
- Timestamp included for audit trail

---

## 🔧 Configuration & Customization

### Adjusting Lead Times

Edit **database_setup.py**, function `generate_mock_products()`:

```python
'lead_time_days': np.random.randint(3, 15),  # Change range as needed
```

### Adjusting Safety Stock

```python
'safety_stock_units': np.random.randint(20, 100),  # Change range as needed
```

### Modifying Forecast Horizon

Edit **ml_pipeline.py**, function `generate_7day_forecasts()`:

```python
for day_ahead in range(1, 8):  # Change 8 to desired number of days + 1
```

### Changing ML Model

Edit **ml_pipeline.py**, function `train_model()`:

```python
if model_type == 'random_forest':  # Select either 'random_forest' or 'xgboost'
```

---

## 📈 Sample Output

### Console Output (orchestrate.py):
```
2024-01-15 10:30:45 - INFO - [PHASE 1] Setting up database...
2024-01-15 10:30:46 - INFO - ✓ Database initialized
2024-01-15 10:30:47 - INFO - ✓ Inserted 15 products
2024-01-15 10:30:48 - INFO - ✓ Inserted 2700 sales transactions

2024-01-15 10:31:00 - INFO - [PHASE 2] Executing ML Pipeline...
2024-01-15 10:31:05 - INFO - Model Performance:
2024-01-15 10:31:05 - INFO -   MAE: 12.34 units
2024-01-15 10:31:05 - INFO -   RMSE: 18.56 units
2024-01-15 10:31:05 - INFO -   R² Score: 0.8742

2024-01-15 10:31:15 - INFO - [PHASE 3] Executing SQL Action Engine...
2024-01-15 10:31:16 - INFO - ✓ Generated 105 forecast records
2024-01-15 10:31:17 - INFO - Alert Summary: CRITICAL=2, WATCHLIST=3, HEALTHY=10

====================================
EXECUTIVE SUMMARY:
  Total Products: 15
  Critical Restock: 2
  Watchlist: 3
  Healthy: 10
====================================
```

### Dashboard Display:
- Real-time KPI cards with color-coded metrics
- Interactive product selection dropdown
- Forecast vs. historical sales overlay chart
- Color-coded alert table (red/yellow/green rows)
- Category distribution bar chart
- Expandable critical action items

---

## 🔍 Database Schema

### products table
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL,
    lead_time_days INTEGER NOT NULL,
    safety_stock_units INTEGER NOT NULL,
    current_inventory INTEGER NOT NULL,
    created_at TIMESTAMP
);
```

### sales_transactions table
```sql
CREATE TABLE sales_transactions (
    transaction_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity_sold INTEGER NOT NULL,
    sale_price REAL NOT NULL,
    transaction_date DATE NOT NULL,
    day_of_week TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### forecasted_demand table
```sql
CREATE TABLE forecasted_demand (
    forecast_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_quantity INTEGER NOT NULL,
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    forecast_created_at TIMESTAMP
);
```

### reorder_alerts table
```sql
CREATE TABLE reorder_alerts (
    alert_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    reorder_point INTEGER NOT NULL,
    current_inventory INTEGER NOT NULL,
    predicted_demand_7day INTEGER NOT NULL,
    alert_status TEXT NOT NULL,
    action_required INTEGER,
    alert_created_at TIMESTAMP
);
```

---

## 📊 Advanced SQL Queries

### Get Products Requiring Immediate Restocking
```sql
SELECT product_name, current_inventory, reorder_point, 
       (predicted_demand_7day * 2 - current_inventory) as recommended_order_qty
FROM reorder_alerts
WHERE alert_status = 'CRITICAL RESTOCK'
ORDER BY current_inventory ASC;
```

### Inventory Health Report (30-Day View)
```sql
SELECT category, 
       COUNT(*) as total_products,
       SUM(current_inventory) as total_inventory,
       AVG(days_inventory_remaining) as avg_days_remaining
FROM reorder_alerts
GROUP BY category
ORDER BY avg_days_remaining ASC;
```

### Forecast Accuracy Analysis (After 7 Days)
```sql
SELECT 
    p.product_name,
    fd.predicted_quantity,
    SUM(st.quantity_sold) as actual_quantity,
    ABS(fd.predicted_quantity - SUM(st.quantity_sold)) as forecast_error
FROM forecasted_demand fd
JOIN products p ON fd.product_id = p.product_id
LEFT JOIN sales_transactions st ON fd.product_id = st.product_id 
    AND st.transaction_date >= fd.forecast_date 
    AND st.transaction_date < DATE(fd.forecast_date, '+1 day')
WHERE fd.forecast_created_at < DATE('now', '-7 days')
GROUP BY p.product_name, fd.predicted_quantity
ORDER BY forecast_error DESC;
```

---

## 🐛 Troubleshooting

### "No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Database is locked"
- Close any open connections to the database
- Delete `retail_demand_forecast.db` and re-run orchestrate.py

### XGBoost import error on M1/M2 Mac
```bash
pip install xgboost --upgrade
```

### Dashboard shows "No alert data available"
- Ensure orchestrate.py completed successfully
- Check for `retail_demand_forecast.db` in the project directory
- Try refreshing the dashboard

---

## 📈 Production Deployment Checklist

- [ ] Test with 3+ years of historical data
- [ ] Validate forecast accuracy against holdout test set
- [ ] Set up automated daily pipeline execution via cron/scheduler
- [ ] Configure database backup strategy
- [ ] Implement email alerts for CRITICAL_RESTOCK status
- [ ] Set up monitoring for pipeline failures
- [ ] Document manual override procedures
- [ ] Train operations team on dashboard usage
- [ ] Establish KPI targets (e.g., target forecast accuracy >85%)

---

## 🤝 Contributing & Customization

The system is designed to be highly customizable:

1. **Add more features**: Extend `feature_engineering.sql` with additional CTEs
2. **Use different ML models**: Replace XGBoost with Prophet, LSTM, or ARIMA
3. **Add more products**: Simply increase `num_products` in `database_setup.py`
4. **Extend historical data**: Adjust `days=180` parameter
5. **Customize alerts**: Modify threshold logic in `sql_action_engine.py`
6. **Enhance dashboard**: Add more visualizations to `app.py`

---

## 📚 Key Learnings & Technical Highlights

✅ **Time-Series Prediction**: Proper temporal train/test splitting prevents data leakage
✅ **Feature Engineering**: SQL window functions compute rolling statistics efficiently
✅ **ML Pipeline**: XGBoost captures non-linear demand patterns
✅ **Operational Automation**: SQL formulas drive real-time business alerts
✅ **Interactive BI**: Streamlit dashboards provide instant insights
✅ **Production Ready**: Error handling, logging, and persistence built-in

---

## 📞 Support & Documentation

For detailed information on specific modules:
- See inline comments in each Python file
- Review SQL query structure in `feature_engineering.sql`
- Check Streamlit documentation at https://docs.streamlit.io/

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

**Built with ❤️ for data engineers and ML practitioners**

*Last Updated: January 2024*
