import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2

# Page configuration
st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="🏭",
    layout="wide"
)


# --- Database Connection ---
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host='localhost',
        database='supply_chain',
        user='admin',
        password='password'
    )


# --- Data Loading Functions ---
@st.cache_data(ttl=30)  # Cache data for 30 seconds
def load_data(query):
    try:
        conn = init_connection()
        df = pd.read_sql_query(query, conn)
        return df
    except (Exception, psycopg2.Error):
        return pd.DataFrame()


# --- Page 1: Overview ---
def show_overview():
    st.header("📊 Overview Dashboard")

    demand_df = load_data("SELECT * FROM demand_data ORDER BY timestamp DESC LIMIT 1000")
    inventory_df = load_data("SELECT * FROM inventory_data ORDER BY timestamp DESC LIMIT 1000")

    if demand_df.empty or inventory_df.empty:
        st.warning("No data available yet. Please ensure the Kafka producer and consumer are running.")
        return

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products Tracked", inventory_df['product_id'].nunique())
    with col2:
        st.metric("Avg Demand Per Transaction", f"{demand_df['demand_quantity'].mean():.1f}")
    with col3:
        total_inventory = inventory_df.drop_duplicates(subset=['product_id'])['quantity'].sum()
        st.metric("Total Current Inventory", f"{total_inventory:,}")
    with col4:
        stockout_risk = len(inventory_df[inventory_df['quantity'] < inventory_df['reorder_point']])
        st.metric("Products at Risk of Stockout", stockout_risk)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demand by Region")
        demand_by_region = demand_df.groupby('region')['demand_quantity'].sum().reset_index()
        fig = px.bar(demand_by_region, x='region', y='demand_quantity', title="Total Demand by Region")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Inventory by Location")
        latest_inventory = inventory_df.loc[inventory_df.groupby('product_id')['timestamp'].idxmax()]
        inventory_by_location = latest_inventory.groupby('location')['quantity'].sum().reset_index()
        fig = px.pie(inventory_by_location, values='quantity', names='location',
                     title="Current Inventory Distribution by Location")
        st.plotly_chart(fig, use_container_width=True)


# --- Page 2: Inventory Optimization ---
def show_inventory_optimization():
    st.header("📦 Inventory Optimization Analysis")

    opt_df = load_data("SELECT * FROM inventory_optimization")

    if opt_df.empty:
        st.warning("No optimization data found. Please run the `run_inventory_analysis.py` script first.")
        return

    st.subheader("Optimization Results")
    st.dataframe(opt_df.style.format({
        "eoq": "{:.1f}",
        "reorder_point": "{:.1f}",
        "safety_stock": "{:.1f}",
        "annual_demand": "{:,.0f}",
        "avg_daily_demand": "{:.1f}"
    }))


# --- Main App ---
def main():
    st.title("🏭 Supply Chain Optimization Dashboard")

    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Inventory Optimization"]
    )

    if page == "Overview":
        show_overview()
    elif page == "Inventory Optimization":
        show_inventory_optimization()


if __name__ == "__main__":
    main()