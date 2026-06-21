"""
PHASE 2: MACHINE LEARNING PIPELINE
Advanced ML pipeline with proper train/test splitting, preprocessing, 
model training (Random Forest + XGBoost), and comprehensive evaluation metrics.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pickle
import warnings

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = "retail_demand_forecast.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Feature Engineering Query (same as in feature_engineering.sql)
FEATURE_ENGINEERING_QUERY = """
WITH daily_aggregates AS (
    SELECT 
        product_id,
        transaction_date,
        SUM(quantity_sold) AS daily_quantity,
        AVG(sale_price) AS avg_price,
        COUNT(*) AS transaction_count,
        CAST(STRFTIME('%w', transaction_date) AS INTEGER) AS day_of_week
    FROM sales_transactions
    GROUP BY product_id, transaction_date
),

rolling_averages AS (
    SELECT 
        product_id,
        transaction_date,
        daily_quantity,
        avg_price,
        transaction_count,
        day_of_week,
        
        AVG(daily_quantity) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7day_avg,
        
        AVG(daily_quantity) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS rolling_30day_avg,
        
        LAG(daily_quantity, 1) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date
        ) AS prev_day_quantity,
        
        LAG(daily_quantity, 7) OVER (
            PARTITION BY product_id 
            ORDER BY transaction_date
        ) AS quantity_7day_ago
    FROM daily_aggregates
),

feature_enrichment AS (
    SELECT 
        ra.product_id,
        p.product_name,
        p.category,
        p.unit_price,
        p.lead_time_days,
        p.safety_stock_units,
        ra.transaction_date,
        ra.daily_quantity,
        ra.avg_price,
        ra.transaction_count,
        ra.day_of_week,
        CASE WHEN ra.day_of_week IN (5, 6) THEN 1 ELSE 0 END AS is_weekend,
        ra.rolling_7day_avg,
        ra.rolling_30day_avg,
        ra.prev_day_quantity,
        ra.quantity_7day_ago,
        CAST(STRFTIME('%m', ra.transaction_date) AS INTEGER) AS month,
        CAST(STRFTIME('%q', ra.transaction_date) AS INTEGER) AS quarter
    FROM rolling_averages ra
    INNER JOIN products p ON ra.product_id = p.product_id
)

SELECT 
    product_id, product_name, category, unit_price, lead_time_days, 
    safety_stock_units, transaction_date, daily_quantity, avg_price, 
    transaction_count, day_of_week, is_weekend, rolling_7day_avg, 
    rolling_30day_avg, prev_day_quantity, quantity_7day_ago, month, quarter
FROM feature_enrichment
WHERE transaction_date >= DATE('now', '-180 days')
ORDER BY product_id, transaction_date;
"""

class DemandForecastingPipeline:
    """Complete ML pipeline for retail demand forecasting."""
    
    def __init__(self, db_url=DATABASE_URL):
        """Initialize the pipeline with database connection."""
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.categorical_features = ['category', 'day_of_week']
        self.numerical_features = [
            'unit_price', 'lead_time_days', 'safety_stock_units', 'avg_price',
            'transaction_count', 'is_weekend', 'rolling_7day_avg', 'rolling_30day_avg',
            'prev_day_quantity', 'quantity_7day_ago', 'month', 'quarter'
        ]
        logger.info("Pipeline initialized.")
    
    def load_features_from_database(self):
        """Load engineered features from database using advanced SQL."""
        try:
            logger.info("Loading features from database...")
            df = pd.read_sql_query(FEATURE_ENGINEERING_QUERY, self.engine)
            logger.info(f"Loaded {len(df)} rows with {len(df.columns)} features.")
            return df
        except Exception as e:
            logger.error(f"Error loading features: {str(e)}")
            raise
    
    def preprocess_data(self, df):
        """Comprehensive data preprocessing and feature engineering."""
        df = df.copy()
        
        # Handle missing values
        df['rolling_7day_avg'].fillna(df['daily_quantity'].mean(), inplace=True)
        df['rolling_30day_avg'].fillna(df['daily_quantity'].mean(), inplace=True)
        df['prev_day_quantity'].fillna(df['daily_quantity'].median(), inplace=True)
        df['quantity_7day_ago'].fillna(df['daily_quantity'].median(), inplace=True)
        
        # Encode categorical features
        for cat_feature in self.categorical_features:
            if cat_feature not in self.label_encoders:
                self.label_encoders[cat_feature] = LabelEncoder()
                df[cat_feature] = self.label_encoders[cat_feature].fit_transform(df[cat_feature].astype(str))
            else:
                df[cat_feature] = self.label_encoders[cat_feature].transform(df[cat_feature].astype(str))
        
        # Create interaction features
        df['price_demand_interaction'] = df['avg_price'] * df['rolling_7day_avg']
        df['inventory_ratio'] = df['rolling_7day_avg'] / (df['unit_price'] + 1e-5)
        
        # Create lag-based momentum features
        df['quantity_momentum'] = df['prev_day_quantity'] / (df['quantity_7day_ago'] + 1e-5)
        df['demand_acceleration'] = df['rolling_7day_avg'] / (df['rolling_30day_avg'] + 1e-5)
        
        # Handle infinite values
        df.replace([np.inf, -np.inf], 0, inplace=True)
        df.fillna(0, inplace=True)
        
        logger.info(f"Data preprocessed. Shape: {df.shape}")
        return df
    
    def create_time_based_split(self, df, test_size=0.2):
        """Time-based train/test split to prevent data leakage."""
        df = df.sort_values('transaction_date').reset_index(drop=True)
        split_point = int(len(df) * (1 - test_size))
        
        train_df = df[:split_point].copy()
        test_df = df[split_point:].copy()
        
        logger.info(f"Train set: {len(train_df)} rows | Test set: {len(test_df)} rows")
        return train_df, test_df
    
    def prepare_feature_matrix(self, df):
        """Prepare X and y for model training."""
        feature_cols = self.categorical_features + self.numerical_features + [
            'price_demand_interaction', 'inventory_ratio', 'quantity_momentum', 'demand_acceleration'
        ]
        
        X = df[feature_cols].values
        y = df['daily_quantity'].values
        
        self.feature_columns = feature_cols
        logger.info(f"Feature matrix shape: {X.shape}, Target shape: {y.shape}")
        return X, y, feature_cols
    
    def train_model(self, X_train, y_train, X_test, y_test, model_type='xgboost'):
        """Train ML model (Random Forest or XGBoost) with hyperparameter tuning."""
        try:
            logger.info(f"Training {model_type.upper()} model...")
            
            # Normalize features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            if model_type == 'random_forest':
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
            elif model_type == 'xgboost':
                self.model = xgb.XGBRegressor(
                    n_estimators=150,
                    max_depth=7,
                    learning_rate=0.05,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    tree_method='hist',
                    device='cpu'
                )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate on test set
            y_pred = self.model.predict(X_test_scaled)
            
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"Model Performance on Test Set:")
            logger.info(f"  MAE: {mae:.2f} units")
            logger.info(f"  RMSE: {rmse:.2f} units")
            logger.info(f"  R² Score: {r2:.4f}")
            
            return {
                'model': self.model,
                'mae': mae,
                'rmse': rmse,
                'r2_score': r2,
                'predictions': y_pred
            }
        
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def generate_7day_forecasts(self, df):
        """Generate 7-day forecasts for all products."""
        try:
            logger.info("Generating 7-day forecasts...")
            
            # Get latest data per product
            latest_data = df.sort_values('transaction_date').groupby('product_id').tail(1).copy().reset_index(drop=True)
            
            # Prepare features for prediction
            feature_cols = self.feature_columns
            X_latest = latest_data[feature_cols].values
            X_latest_scaled = self.scaler.transform(X_latest)
            
            # Generate predictions
            predictions = self.model.predict(X_latest_scaled)
            
            # Create forecast dataframe for next 7 days
            forecasts = []
            for pred_idx, (idx, row) in enumerate(latest_data.iterrows()):
                base_pred = predictions[pred_idx]
                
                for day_ahead in range(1, 8):
                    # Apply decay factor for days further in future
                    decay = 0.98 ** (day_ahead - 1)
                    predicted_qty = max(1, int(base_pred * decay))
                    
                    # Confidence interval (±20%)
                    lower_bound = predicted_qty * 0.80
                    upper_bound = predicted_qty * 1.20
                    
                    forecast_date = datetime.now().date() + timedelta(days=day_ahead)
                    
                    forecasts.append({
                        'product_id': int(row['product_id']),
                        'forecast_date': forecast_date,
                        'predicted_quantity': predicted_qty,
                        'confidence_interval_lower': lower_bound,
                        'confidence_interval_upper': upper_bound
                    })
            
            forecast_df = pd.DataFrame(forecasts)
            logger.info(f"Generated {len(forecast_df)} forecast records.")
            return forecast_df
        
        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
            raise
    
    def save_model(self, filename='demand_forecast_model.pkl'):
        """Save trained model and scaler to disk."""
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'label_encoders': self.label_encoders,
                    'feature_columns': self.feature_columns
                }, f)
            logger.info(f"Model saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def execute_pipeline(self):
        """Execute the complete ML pipeline."""
        try:
            # 1. Load data from database
            df = self.load_features_from_database()
            
            # 2. Preprocess data
            df = self.preprocess_data(df)
            
            # 3. Time-based train/test split
            train_df, test_df = self.create_time_based_split(df, test_size=0.2)
            
            # 4. Prepare features
            X_train, y_train, feature_cols = self.prepare_feature_matrix(train_df)
            X_test, y_test, _ = self.prepare_feature_matrix(test_df)
            
            # 5. Train XGBoost model
            results = self.train_model(X_train, y_train, X_test, y_test, model_type='xgboost')
            
            # 6. Save model
            self.save_model()
            
            # 7. Generate 7-day forecasts
            forecast_df = self.generate_7day_forecasts(df)
            
            logger.info("ML Pipeline completed successfully!")
            return forecast_df, results
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise

def run_ml_pipeline():
    """Entry point for the ML pipeline."""
    pipeline = DemandForecastingPipeline()
    forecast_df, results = pipeline.execute_pipeline()
    return forecast_df

if __name__ == "__main__":
    forecast_df = run_ml_pipeline()
    print("\n7-Day Forecast Sample:")
    print(forecast_df.head(20))
