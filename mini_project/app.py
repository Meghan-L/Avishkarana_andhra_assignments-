"""
PHASE 4: STREAMLIT FRONTEND DASHBOARD
Interactive dashboard for monitoring demand forecasts and inventory alerts.
Single-file Streamlit application providing real-time operational intelligence.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = "retail_demand_forecast.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Page configuration
st.set_page_config(
    page_title="Retail Demand Forecasting & Inventory Control",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    .critical-badge {
        background-color: #ff4444;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    .watchlist-badge {
        background-color: #ffaa00;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    .healthy-badge {
        background-color: #44aa44;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection():
    """Create database connection (cached)."""
    return create_engine(DATABASE_URL)

@st.cache_data(ttl=3600)
def load_alerts():
    """Load reorder alerts from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT * FROM reorder_alerts 
        ORDER BY alert_created_at DESC 
        LIMIT 100;
        """
        alerts_df = pd.read_sql_query(query, conn)
        conn.close()
        return alerts_df
    except Exception as e:
        st.error(f"Error loading alerts: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_forecasts():
    """Load demand forecasts from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT fd.*, p.product_name, p.category
        FROM forecasted_demand fd
        JOIN products p ON fd.product_id = p.product_id
        WHERE fd.forecast_created_at = (
            SELECT MAX(forecast_created_at) FROM forecasted_demand
        );
        """
        forecasts_df = pd.read_sql_query(query, conn)
        conn.close()
        return forecasts_df
    except Exception as e:
        st.error(f"Error loading forecasts: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_historical_sales():
    """Load historical sales data for comparison."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT 
            transaction_date,
            product_id,
            SUM(quantity_sold) as daily_quantity
        FROM sales_transactions
        WHERE transaction_date >= DATE('now', '-30 days')
        GROUP BY transaction_date, product_id
        ORDER BY transaction_date, product_id;
        """
        sales_df = pd.read_sql_query(query, conn)
        conn.close()
        return sales_df
    except Exception as e:
        st.error(f"Error loading sales data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_products():
    """Load product catalog."""
    try:
        conn = sqlite3.connect(DB_PATH)
        products_df = pd.read_sql_query("SELECT * FROM products;", conn)
        conn.close()
        return products_df
    except Exception as e:
        st.error(f"Error loading products: {str(e)}")
        return pd.DataFrame()

def get_alert_color(status):
    """Return color based on alert status."""
    if status == "CRITICAL RESTOCK":
        return "🔴"
    elif status == "WATCHLIST":
        return "🟡"
    else:
        return "🟢"

def format_metric_value(value):
    """Format numeric values for display."""
    if isinstance(value, float):
        return f"{value:,.1f}"
    return f"{value:,}"

# ========================
# MAIN DASHBOARD
# ========================

st.title("📊 Dual-Engine Retail Demand Forecasting & Inventory Control")
st.markdown("*Real-time operational intelligence powered by ML & SQL optimization*")

# Load data
alerts = load_alerts()
forecasts = load_forecasts()
historical_sales = load_historical_sales()
products = load_products()

if alerts.empty:
    st.warning("⚠️ No alert data available. Please run the ML pipeline first.")
    st.stop()

# ========================
# KPI METRICS SECTION
# ========================

st.markdown("---")
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_predicted_demand = forecasts['predicted_quantity'].sum() if not forecasts.empty else 0
    st.metric(
        "7-Day Predicted Demand",
        f"{int(total_predicted_demand):,}",
        delta="units",
        help="Total forecasted units for next 7 days"
    )

with col2:
    critical_restock = len(alerts[alerts['alert_status'] == 'CRITICAL RESTOCK'])
    st.metric(
        "🔴 Critical Restock",
        critical_restock,
        delta="products",
        help="Products requiring immediate action"
    )

with col3:
    watchlist_count = len(alerts[alerts['alert_status'] == 'WATCHLIST'])
    st.metric(
        "🟡 Watchlist",
        watchlist_count,
        delta="products",
        help="Products to monitor closely"
    )

with col4:
    healthy_count = len(alerts[alerts['alert_status'] == 'HEALTHY'])
    st.metric(
        "🟢 Healthy",
        healthy_count,
        delta="products",
        help="Products with sufficient inventory"
    )

with col5:
    avg_days_inventory = alerts['days_inventory_remaining'].mean()
    st.metric(
        "Avg Days Inventory",
        f"{avg_days_inventory:.1f}",
        delta="days",
        help="Average days of inventory remaining"
    )

# ========================
# CHARTS SECTION
# ========================

st.markdown("---")
st.subheader("📉 Forecast vs Historical Sales Comparison")

# Select product for detailed comparison
if not products.empty:
    product_list = products.sort_values('product_name')['product_name'].tolist()
    selected_product = st.selectbox(
        "Select Product for Detailed Analysis",
        product_list,
        key="product_selector"
    )
    
    selected_product_id = products[products['product_name'] == selected_product]['product_id'].values[0]
    
    # Get data for selected product
    product_forecasts = forecasts[forecasts['product_id'] == selected_product_id].sort_values('forecast_date')
    product_historical = historical_sales[historical_sales['product_id'] == selected_product_id].sort_values('transaction_date')
    
    if not product_forecasts.empty:
        # Create comparison chart
        fig = go.Figure()
        
        # Add historical sales
        if not product_historical.empty:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(product_historical['transaction_date']),
                y=product_historical['daily_quantity'],
                mode='lines+markers',
                name='Historical Sales (30 days)',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(product_forecasts['forecast_date']),
            y=product_forecasts['predicted_quantity'],
            mode='lines+markers',
            name='7-Day ML Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond')
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(product_forecasts['forecast_date']).tolist() + 
              pd.to_datetime(product_forecasts['forecast_date']).tolist()[::-1],
            y=product_forecasts['confidence_interval_upper'].tolist() + 
              product_forecasts['confidence_interval_lower'].tolist()[::-1],
            fill='toself',
            name='Confidence Interval (±20%)',
            fillcolor='rgba(255, 127, 14, 0.2)',
            line=dict(color='rgba(255, 127, 14, 0)')
        ))
        
        fig.update_layout(
            title=f"Sales Forecast vs Historical Data: {selected_product}",
            xaxis_title="Date",
            yaxis_title="Quantity (units)",
            hovermode='x unified',
            height=450,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No forecast data available for this product yet.")

# ========================
# INVENTORY ALERTS TABLE
# ========================

st.markdown("---")
st.subheader("🚨 Automated Reorder Alerts & Inventory Status")

# Filter alerts by status
col1, col2, col3 = st.columns(3)
with col1:
    show_critical = st.checkbox("Show Critical Restock", value=True)
with col2:
    show_watchlist = st.checkbox("Show Watchlist", value=True)
with col3:
    show_healthy = st.checkbox("Show Healthy", value=False)

# Apply filters
filtered_alerts = alerts.copy()
statuses_to_show = []
if show_critical:
    statuses_to_show.append("CRITICAL RESTOCK")
if show_watchlist:
    statuses_to_show.append("WATCHLIST")
if show_healthy:
    statuses_to_show.append("HEALTHY")

filtered_alerts = filtered_alerts[filtered_alerts['alert_status'].isin(statuses_to_show)]

# Display alerts table with formatting
if not filtered_alerts.empty:
    display_df = filtered_alerts[[
        'product_name', 'alert_status', 'current_inventory', 
        'reorder_point', 'predicted_demand_7day', 
        'days_inventory_remaining'
    ]].copy()
    
    display_df.columns = [
        'Product Name', 'Alert Status', 'Current Inventory', 
        'Reorder Point', '7-Day Demand Forecast', 'Days Inventory Left'
    ]
    
    # Rename status for display
    display_df['Alert Status'] = display_df['Alert Status'].map({
        'CRITICAL RESTOCK': '🔴 CRITICAL RESTOCK',
        'WATCHLIST': '🟡 WATCHLIST',
        'HEALTHY': '🟢 HEALTHY'
    })
    
    # Create styled dataframe
    def highlight_critical(row):
        if '🔴' in str(row['Alert Status']):
            return ['background-color: #ffcccc'] * len(row)
        elif '🟡' in str(row['Alert Status']):
            return ['background-color: #ffffcc'] * len(row)
        else:
            return ['background-color: #ccffcc'] * len(row)
    
    st.dataframe(
        display_df.style.apply(highlight_critical, axis=1),
        use_container_width=True,
        height=400
    )
    
    # Summary statistics
    st.markdown("**Summary Statistics**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Alerted Products",
            len(filtered_alerts),
            help="Number of products with alerts"
        )
    
    with col2:
        avg_inventory = filtered_alerts['current_inventory'].mean()
        st.metric(
            "Avg Inventory Level",
            f"{int(avg_inventory):,}",
            help="Average inventory across alerted products"
        )
    
    with col3:
        total_7day_demand = filtered_alerts['predicted_demand_7day'].sum()
        st.metric(
            "Total 7-Day Demand",
            f"{int(total_7day_demand):,}",
            help="Combined predicted demand for next 7 days"
        )
    
    with col4:
        avg_lead_time = filtered_alerts['lead_time_days'].mean()
        st.metric(
            "Avg Lead Time",
            f"{avg_lead_time:.1f}",
            help="Average product lead time in days"
        )
else:
    st.info("No alerts match the selected filters.")

# ========================
# ALERT DISTRIBUTION CHART
# ========================

st.markdown("---")
st.subheader("📊 Alert Distribution by Product Category")

if not alerts.empty:
    category_stats = alerts.groupby(['category', 'alert_status']).size().unstack(fill_value=0)
    
    fig = px.bar(
        category_stats,
        x=category_stats.index,
        y=category_stats.columns,
        barmode='stack',
        title="Inventory Alert Distribution by Product Category",
        labels={'index': 'Category', 'value': 'Number of Products'},
        color_discrete_map={
            'CRITICAL RESTOCK': '#ff4444',
            'WATCHLIST': '#ffaa00',
            'HEALTHY': '#44aa44'
        },
        height=400
    )
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ========================
# CRITICAL ACTIONS PANEL
# ========================

critical_products = alerts[alerts['alert_status'] == 'CRITICAL RESTOCK']

if len(critical_products) > 0:
    st.markdown("---")
    st.subheader("⚠️ CRITICAL ACTION ITEMS - IMMEDIATE ATTENTION REQUIRED")
    
    with st.container():
        for idx, row in critical_products.iterrows():
            with st.expander(
                f"🔴 {row['product_name']} - REORDER NOW",
                expanded=(idx == critical_products.index[0])
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Current Inventory",
                        f"{int(row['current_inventory']):,} units",
                        delta=f"Below reorder point by {int(row['reorder_point'] - row['current_inventory'])} units",
                        delta_color="inverse"
                    )
                
                with col2:
                    st.metric(
                        "Reorder Point",
                        f"{int(row['reorder_point']):,} units",
                        help="Calculated based on lead time + safety stock"
                    )
                
                with col3:
                    st.metric(
                        "7-Day Forecast",
                        f"{int(row['predicted_demand_7day']):,} units",
                        help="Expected demand over next 7 days"
                    )
                
                st.warning(
                    f"**ACTION**: Reorder at least {int(row['predicted_demand_7day'] * 2 - row['current_inventory']):,} units immediately. "
                    f"Lead time: {int(row['lead_time_days'])} days. "
                    f"Current stock will be depleted in approximately {int(row['days_inventory_remaining'])} days."
                )

# ========================
# SIDEBAR - SETTINGS & INFO
# ========================

with st.sidebar:
    st.markdown("### ⚙️ Dashboard Settings")
    
    refresh_interval = st.slider(
        "Auto-refresh interval (seconds)",
        30, 600, 300, step=30
    )
    
    st.markdown("---")
    st.markdown("### 📋 Dashboard Information")
    st.info(
        """
        **Dual-Engine System:**
        - **SQL Engine**: Advanced feature engineering with CTEs and window functions
        - **ML Engine**: XGBoost model with 7-day demand forecasting
        - **Action Engine**: Automated reorder point calculation & alerts
        
        **Alert Levels:**
        - 🔴 **CRITICAL RESTOCK**: Immediate action required
        - 🟡 **WATCHLIST**: Monitor closely for restocking
        - 🟢 **HEALTHY**: Sufficient inventory levels
        
        **Metrics:**
        - Reorder Point = (Predicted Daily Demand × Lead Time) + Safety Stock
        - Confidence intervals based on ±20% forecast variance
        """
    )
    
    st.markdown("---")
    st.markdown("### 🔄 Last Updated")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    if st.button("🔄 Refresh All Data", key="refresh_button"):
        st.cache_data.clear()
        st.rerun()
    
    if st.button("📊 Export Alert Report"):
        csv = alerts.to_csv(index=False)
        st.download_button(
            label="Download CSV Report",
            data=csv,
            file_name=f"inventory_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ========================
# FOOTER
# ========================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
    <p><b>Dual-Engine Retail Demand Forecasting & Automated Inventory Control System</b></p>
    <p>Powered by SQLite, XGBoost ML, and Streamlit | Real-time Operational Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)
