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

# Custom CSS for refined dashboard styling
st.markdown("""
    <style>
    :root {
        --bg-start: #07111f;
        --bg-end: #101f35;
        --panel: rgba(15, 23, 42, 0.9);
        --panel-strong: rgba(30, 41, 59, 0.95);
        --text: #e2e8f0;
        --muted: #94a3b8;
        --accent: #2dd4bf;
        --accent-strong: #14b8a6;
        --accent-2: #818cf8;
        --accent-3: #38bdf8;
        --danger: #f43f5e;
        --warning: #f59e0b;
        --success: #22c55e;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-end) 100%);
        color: var(--text);
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-end) 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(45, 212, 191, 0.16), rgba(129, 140, 248, 0.22));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(2, 6, 23, 0.25);
    }

    .hero-card h1 {
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }

    .hero-card p {
        color: var(--muted);
        margin-bottom: 0;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        background: rgba(45, 212, 191, 0.18);
        color: var(--accent);
        border-radius: 999px;
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }

    .section-title {
        color: #f8fafc;
        margin-top: 0.2rem;
        margin-bottom: 0.6rem;
    }

    .section-subtitle {
        color: var(--muted);
        margin-bottom: 0.8rem;
    }

    .stMetric {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 0.6rem 0.8rem;
        box-shadow: 0 8px 20px rgba(2, 6, 23, 0.16);
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .stMetric [data-testid="stMetricDelta"] {
        color: var(--accent);
    }

    .stDataFrame, .stTable {
        border-radius: 12px;
        overflow: hidden;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        color: #0f172a;
        border: none;
        border-radius: 999px;
        font-weight: 700;
    }

    .stButton > button:hover {
        opacity: 0.95;
        box-shadow: 0 8px 18px rgba(45, 212, 191, 0.25);
    }

    .sidebar .sidebar-content {
        background: linear-gradient(180deg, rgba(2, 6, 23, 0.96) 0%, rgba(15, 23, 42, 0.95) 100%);
    }

    .stAlert, .stInfo, .stWarning {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .st-emotion-cache-1x8yxb {
        background: transparent;
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

st.markdown("""
<div class="hero-card">
    <div class="hero-badge">Operations Intelligence</div>
    <h1>📊 Dual-Engine Retail Demand Forecasting & Inventory Control</h1>
    <p>Real-time forecasting, replenishment intelligence, and proactive alerting powered by SQL, ML, and automation.</p>
</div>
""", unsafe_allow_html=True)

# Load data
alerts = load_alerts()
forecasts = load_forecasts()
historical_sales = load_historical_sales()
products = load_products()

# Normalize alert columns for compatibility with older database snapshots
for col, default in {
    'category': 'Unknown',
    'days_inventory_remaining': 0,
    'lead_time_days': 0,
    'safety_stock_units': 0,
}.items():
    if col not in alerts.columns:
        alerts[col] = default

for col, default in {
    'forecast_date': pd.NaT,
    'predicted_quantity': 0,
    'confidence_interval_lower': 0,
    'confidence_interval_upper': 0,
}.items():
    if col not in forecasts.columns:
        forecasts[col] = default

if alerts.empty:
    st.warning("⚠️ No alert data available. Please run the ML pipeline first.")
    st.stop()

# ========================
# KPI METRICS SECTION
# ========================

st.markdown("---")
st.markdown("<div class='section-title'>📈 Key Performance Indicators</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>A concise view of operational health across the network.</div>", unsafe_allow_html=True)

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
    avg_days_inventory = pd.to_numeric(alerts['days_inventory_remaining'], errors='coerce').fillna(0).mean()
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
st.markdown("<div class='section-title'>📉 Forecast vs Historical Sales Comparison</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Compare recent demand behavior with the next seven days of projected sales.</div>", unsafe_allow_html=True)

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
    product_forecasts = forecasts[forecasts['product_id'] == selected_product_id].copy()
    product_forecasts = product_forecasts.sort_values('forecast_date') if 'forecast_date' in product_forecasts.columns else product_forecasts
    product_historical = historical_sales[historical_sales['product_id'] == selected_product_id].sort_values('transaction_date') if 'transaction_date' in historical_sales.columns else pd.DataFrame()

    if not product_forecasts.empty:
        product_forecasts['forecast_date'] = pd.to_datetime(product_forecasts['forecast_date'], errors='coerce')
        product_forecasts = product_forecasts.dropna(subset=['forecast_date'])
        product_forecasts['predicted_quantity'] = pd.to_numeric(product_forecasts['predicted_quantity'], errors='coerce').fillna(0)
        if 'confidence_interval_upper' not in product_forecasts.columns:
            product_forecasts['confidence_interval_upper'] = product_forecasts['predicted_quantity'] * 1.2
        if 'confidence_interval_lower' not in product_forecasts.columns:
            product_forecasts['confidence_interval_lower'] = product_forecasts['predicted_quantity'] * 0.8
        product_forecasts['confidence_interval_upper'] = pd.to_numeric(product_forecasts['confidence_interval_upper'], errors='coerce').fillna(0)
        product_forecasts['confidence_interval_lower'] = pd.to_numeric(product_forecasts['confidence_interval_lower'], errors='coerce').fillna(0)

        if not product_forecasts.empty:
            # Create comparison chart
            fig = go.Figure()
            
            # Add historical sales
            if not product_historical.empty:
                product_historical['transaction_date'] = pd.to_datetime(product_historical['transaction_date'], errors='coerce')
                product_historical = product_historical.dropna(subset=['transaction_date'])
                product_historical['daily_quantity'] = pd.to_numeric(product_historical['daily_quantity'], errors='coerce').fillna(0)
                fig.add_trace(go.Scatter(
                    x=product_historical['transaction_date'],
                    y=product_historical['daily_quantity'],
                    mode='lines+markers',
                    name='Historical Sales (30 days)',
                    line=dict(color='#38bdf8', width=2),
                    marker=dict(size=6)
                ))
            
            # Add forecast
            fig.add_trace(go.Scatter(
                x=product_forecasts['forecast_date'],
                y=product_forecasts['predicted_quantity'],
                mode='lines+markers',
                name='7-Day ML Forecast',
                line=dict(color='#2dd4bf', width=2, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=product_forecasts['forecast_date'].tolist() + 
                  product_forecasts['forecast_date'].tolist()[::-1],
                y=product_forecasts['confidence_interval_upper'].tolist() + 
                  product_forecasts['confidence_interval_lower'].tolist()[::-1],
                fill='toself',
                name='Confidence Interval (±20%)',
                fillcolor='rgba(45, 212, 191, 0.2)',
                line=dict(color='rgba(45, 212, 191, 0)')
            ))
            
            fig.update_layout(
                title=f"Sales Forecast vs Historical Data: {selected_product}",
                xaxis_title="Date",
                yaxis_title="Quantity (units)",
                hovermode='x unified',
                height=450,
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecast data available for this product yet.")
    else:
        st.info("No forecast data available for this product yet.")

# ========================
# INVENTORY ALERTS TABLE
# ========================

st.markdown("---")
st.markdown("<div class='section-title'>🚨 Automated Reorder Alerts & Inventory Status</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Filter the operational view by alert severity to focus on the most urgent replenishment needs.</div>", unsafe_allow_html=True)

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
    display_df['days_inventory_remaining'] = pd.to_numeric(display_df['days_inventory_remaining'], errors='coerce').fillna(0).astype(int)
    
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
            return ['background-color: #fef2f2; color: #7f1d1d'] * len(row)
        elif '🟡' in str(row['Alert Status']):
            return ['background-color: #fffbeb; color: #92400e'] * len(row)
        else:
            return ['background-color: #f0fdf4; color: #166534'] * len(row)
    
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
        avg_lead_time = pd.to_numeric(filtered_alerts['lead_time_days'], errors='coerce').fillna(0).mean()
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
st.markdown("<div class='section-title'>📊 Alert Distribution by Product Category</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Spot where inventory pressure is concentrated across the catalog.</div>", unsafe_allow_html=True)

if not alerts.empty:
    category_stats = alerts.assign(category=alerts['category'].fillna('Unknown')).groupby(['category', 'alert_status']).size().unstack(fill_value=0)
    
    fig = px.bar(
        category_stats,
        x=category_stats.index,
        y=category_stats.columns,
        barmode='stack',
        title="Inventory Alert Distribution by Product Category",
        labels={'index': 'Category', 'value': 'Number of Products'},
        color_discrete_map={
            'CRITICAL RESTOCK': '#f43f5e',
            'WATCHLIST': '#f59e0b',
            'HEALTHY': '#22c55e'
        },
        height=400
    )
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
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
                    f"Lead time: {int(row.get('lead_time_days', 0))} days. "
                    f"Current stock will be depleted in approximately {int(row.get('days_inventory_remaining', 0))} days."
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
    <div style='text-align: center; color: #cbd5e1; font-size: 12px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 16px;'>
    <p><b>Dual-Engine Retail Demand Forecasting & Automated Inventory Control System</b></p>
    <p>Powered by SQLite, XGBoost ML, and Streamlit | Real-time Operational Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)
