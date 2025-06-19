import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Streamlit Page Configuration ---
# THIS MUST BE THE ABSOLUTE FIRST STREAMLIT COMMAND IN YOUR SCRIPT
st.set_page_config(
    page_title="Interactive Sales Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Load Data (Now reads from your_data.csv) ---
@st.cache_data
@st.cache_data
def load_data():
    try:
        # Load your data from a CSV file
        df = pd.read_csv("Sample - Superstore.csv")

        # Ensure 'Order Date' and 'Ship Date' are datetime objects
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')

        df.dropna(subset=['Order Date', 'Ship Date'], inplace=True)

        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}. Please check the file path and format.")
        return None


# Load the data
df = load_data()

# Handle case where data loading might have failed.
# This check is performed *after* set_page_config is safely called.
if df is None:
    # If df is None, it means load_data failed and an error message was shown there.
    # We stop the app execution here.
    st.stop()
elif df.empty:
    st.warning("The loaded dataset is empty or contains no valid data after processing. Please check your CSV file.")
    st.stop()


# --- Title and Description ---
st.title("📈 Interactive Sales Dashboard")
st.markdown("Explore your sales data with interactive filters and visualizations.")

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Initialize a mutable copy of the DataFrame for filtering
df_filtered = df.copy()

# Date Range Filter
# Ensure min_date and max_date are only calculated if df is not empty
if not df.empty:
    min_date = df['Order Date'].min().to_pydatetime()
    max_date = df['Order Date'].max().to_pydatetime()
else: # Fallback for empty df, though st.stop() above should prevent reaching here if df is empty
    min_date = pd.to_datetime('2000-01-01')
    max_date = pd.to_datetime('2023-12-31')

selected_dates = st.sidebar.slider(
    "Select Order Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)
df_filtered = df_filtered[(df_filtered['Order Date'] >= selected_dates[0]) & (df_filtered['Order Date'] <= selected_dates[1])]


# IMPORTANT: Define options based on the original df or the current state of df_filtered if you want true cascading
# For better user experience, often it's good to show all original options unless a specific cascading logic is intended.
# Here, I'm maintaining the cascading effect, but making sure it's clear.

# Multi-select filters for categorical data
# Regions
all_regions = df['Region'].unique()
selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=all_regions,
    default=list(all_regions) if all_regions.size > 0 else [] # Convert numpy array to list for default
)
if selected_regions:
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]

# Categories
all_categories = df['Category'].unique()
selected_categories = st.sidebar.multiselect(
    "Select Category(ies)",
    options=all_categories,
    default=list(all_categories) if all_categories.size > 0 else []
)
if selected_categories:
    df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]

# Sub-Category filter, dependent on selected Categories (cascading)
available_sub_categories = df_filtered['Sub-Category'].unique() # Options based on current filtered_df
selected_sub_categories = st.sidebar.multiselect(
    "Select Sub-Category(ies)",
    options=available_sub_categories,
    default=list(available_sub_categories) if available_sub_categories.size > 0 else []
)
if selected_sub_categories:
    df_filtered = df_filtered[df_filtered['Sub-Category'].isin(selected_sub_categories)]
# Check if no categories selected AND filtered_df is empty due to other filters
elif not selected_categories and df_filtered.empty:
    st.sidebar.warning("Please select at least one Category to filter Sub-Categories or adjust other filters.")
# Check if no sub-categories selected but there were available options
elif not selected_sub_categories and not available_sub_categories.size == 0:
    st.sidebar.warning("No Sub-Categories selected. Showing no data for sub-category related charts.")


# Segments
all_segments = df['Segment'].unique()
selected_segments = st.sidebar.multiselect(
    "Select Segment(s)",
    options=all_segments,
    default=list(all_segments) if all_segments.size > 0 else []
)
if selected_segments:
    df_filtered = df_filtered[df_filtered['Segment'].isin(selected_segments)]

# Ship Modes
all_ship_modes = df['Ship Mode'].unique()
selected_ship_modes = st.sidebar.multiselect(
    "Select Ship Mode(s)",
    options=all_ship_modes,
    default=list(all_ship_modes) if all_ship_modes.size > 0 else []
)
if selected_ship_modes:
    df_filtered = df_filtered[df_filtered['Ship Mode'].isin(selected_ship_modes)]

# States
all_states = df['State'].unique()
selected_states = st.sidebar.multiselect(
    "Select State(s)",
    options=all_states,
    default=list(all_states) if all_states.size > 0 else []
)
if selected_states:
    df_filtered = df_filtered[df_filtered['State'].isin(selected_states)]

# Cities, dependent on selected States (cascading)
available_cities = df_filtered['City'].unique() # Options based on current filtered_df
selected_cities = st.sidebar.multiselect(
    "Select City(ies)",
    options=available_cities,
    default=list(available_cities) if available_cities.size > 0 else []
)
if selected_cities:
    df_filtered = df_filtered[df_filtered['City'].isin(selected_cities)]
# Check if no states selected AND filtered_df is empty due to other filters
elif not selected_states and df_filtered.empty:
    st.sidebar.warning("Please select at least one State to filter Cities or adjust other filters.")
# Check if no cities selected but there were available options
elif not selected_cities and not available_cities.size == 0:
    st.sidebar.warning("No Cities selected. Showing no data for city related charts.")


# Numeric Range Filters
# Use the full dataframe for min/max values to ensure sliders cover the entire range,
# but apply the filter to df_filtered.
# Handle potential empty dataframe for min/max calculations
if not df.empty:
    min_sales_overall, max_sales_overall = float(df['Sales'].min()), float(df['Sales'].max())
    min_quantity_overall, max_quantity_overall = int(df['Quantity'].min()), int(df['Quantity'].max())
    min_discount_overall, max_discount_overall = float(df['Discount'].min()), float(df['Discount'].max())
    min_profit_overall, max_profit_overall = float(df['Profit'].min()), float(df['Profit'].max())
else:
    # Set default safe values if df is empty (should ideally be handled by the df is None check)
    min_sales_overall, max_sales_overall = 0.0, 1000.0
    min_quantity_overall, max_quantity_overall = 1, 20
    min_discount_overall, max_discount_overall = 0.0, 0.5
    min_profit_overall, max_profit_overall = -200.0, 500.0


selected_sales = st.sidebar.slider(
    "Sales Range",
    min_value=min_sales_overall,
    max_value=max_sales_overall,
    value=(min_sales_overall, max_sales_overall),
    step=10.0
)
df_filtered = df_filtered[(df_filtered['Sales'] >= selected_sales[0]) & (df_filtered['Sales'] <= selected_sales[1])]

selected_quantity = st.sidebar.slider(
    "Quantity Range",
    min_value=min_quantity_overall,
    max_value=max_quantity_overall,
    value=(min_quantity_overall, max_quantity_overall),
    step=1
)
df_filtered = df_filtered[(df_filtered['Quantity'] >= selected_quantity[0]) & (df_filtered['Quantity'] <= selected_quantity[1])]

selected_discount = st.sidebar.slider(
    "Discount Range",
    min_value=min_discount_overall,
    max_value=max_discount_overall,
    value=(min_discount_overall, max_discount_overall),
    step=0.01
)
df_filtered = df_filtered[(df_filtered['Discount'] >= selected_discount[0]) & (df_filtered['Discount'] <= selected_discount[1])]

selected_profit = st.sidebar.slider(
    "Profit Range",
    min_value=min_profit_overall,
    max_value=max_profit_overall,
    value=(min_profit_overall, max_profit_overall),
    step=1.0
)
df_filtered = df_filtered[(df_filtered['Profit'] >= selected_profit[0]) & (df_filtered['Profit'] <= selected_profit[1])]


st.markdown("---") # Markdown for separation
st.subheader("Key Performance Indicators (KPIs)")

# If df_filtered is empty after all selections, display a warning.
# Otherwise, show the KPIs and charts.
# This check is crucial to prevent errors when trying to calculate sums or create charts on an empty DataFrame.
if df_filtered.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    col1, col2, col3 = st.columns(3)

    total_sales = df_filtered['Sales'].sum()
    total_profit = df_filtered['Profit'].sum()
    total_quantity = df_filtered['Quantity'].sum()

    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Profit", f"${total_profit:,.2f}")
    with col3:
        st.metric("Total Quantity", f"{int(total_quantity):,}")

    st.markdown("---") # Markdown for separation
    st.subheader("Interactive Visualizations")

    # 1. Sales Over Time
    st.markdown("#### Sales Trend Over Time")
    sales_over_time = df_filtered.groupby(pd.Grouper(key='Order Date', freq='M'))['Sales'].sum().reset_index()
    fig_sales_time = px.line(
        sales_over_time,
        x='Order Date',
        y='Sales',
        title='Monthly Sales Trend',
        labels={'Order Date': 'Date', 'Sales': 'Total Sales'},
        template="plotly_white"
    )
    fig_sales_time.update_traces(mode='lines+markers', marker=dict(size=6))
    fig_sales_time.update_layout(hovermode="x unified")
    st.plotly_chart(fig_sales_time, use_container_width=True)

    # 2. Sales by Category and Sub-Category
    st.markdown("#### Sales & Profit by Category and Sub-Category")
    col4, col5 = st.columns(2)
    with col4:
        sales_by_category = df_filtered.groupby('Category')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
        fig_sales_category = px.bar(
            sales_by_category,
            x='Category',
            y='Sales',
            title='Sales by Product Category',
            color='Category',
            template="plotly_white"
        )
        st.plotly_chart(fig_sales_category, use_container_width=True)

    with col5:
        profit_by_sub_category = df_filtered.groupby('Sub-Category')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False)
        fig_profit_sub_category = px.bar(
            profit_by_sub_category,
            x='Sub-Category',
            y='Profit',
            title='Profit by Product Sub-Category',
            color='Profit', # Color by profit value
            template="plotly_white",
            color_continuous_scale="RdYlGn" # Fixed: Use string name for RdYlGn
        )
        st.plotly_chart(fig_profit_sub_category, use_container_width=True)

    # 3. Sales vs. Profit Scatter Plot
    st.markdown("#### Sales vs. Profit per Order")
    fig_scatter = px.scatter(
        df_filtered,
        x='Sales',
        y='Profit',
        color='Category',
        hover_data=['Product Name', 'Customer Name', 'Order ID', 'Order Date'], # Added Order ID
        title='Sales vs. Profit',
        labels={'Sales': 'Sales Amount', 'Profit': 'Profit Amount'},
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 4. Sales by Region and Segment
    st.markdown("#### Sales Distribution by Region & Customer Segment")
    col6, col7 = st.columns(2)
    with col6:
        sales_by_region = df_filtered.groupby('Region')['Sales'].sum().reset_index()
        fig_sales_region = px.pie(
            sales_by_region,
            values='Sales',
            names='Region',
            title='Sales Distribution by Region',
            hole=0.3, # Donut chart
            template="plotly_white"
        )
        fig_sales_region.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sales_region, use_container_width=True)

    with col7:
        sales_by_segment = df_filtered.groupby('Segment')['Sales'].sum().reset_index()
        fig_sales_segment = px.bar(
            sales_by_segment,
            x='Segment',
            y='Sales',
            title='Sales by Customer Segment',
            color='Segment',
            template="plotly_white"
        )
        st.plotly_chart(fig_sales_segment, use_container_width=True)

    # 5. Sales by State
    st.markdown("#### Sales by State")
    sales_by_state = df_filtered.groupby('State')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
    fig_sales_state = px.bar(
        sales_by_state.head(20), # Show top 20 states
        x='State',
        y='Sales',
        title='Top 20 States by Sales',
        color='Sales',
        template="plotly_white"
    )
    st.plotly_chart(fig_sales_state, use_container_width=True)

    st.markdown("---") # Markdown for separation
    st.subheader("Filtered Raw Data")

    # --- Display Raw Data (optional) ---
    if st.checkbox("Show Raw Data"):
        st.dataframe(df_filtered)

st.caption("Dashboard created with Streamlit and Plotly Express.")

st.sidebar.markdown("---") # Markdown for separation in sidebar
st.sidebar.subheader("Load Your Own Data")

# Instructions for users to load their own data.
st.sidebar.markdown(
    """
    To use your own dataset, save it as a CSV file (e.g., `your_data.csv`)
    in the same directory as this script. Remember that the code expects
    the following columns: `Row ID`, `Order ID`, `Order Date`, `Ship Date`,
    `Ship Mode`, `Customer ID`, `Customer Name`, `Segment`, `Country`, `City`,
    `State`, `Postal Code`, `Region`, `Product ID`, `Category`, `Sub-Category`,
    `Product Name`, `Sales`, `Quantity`, `Discount`, `Profit`.

    Ensure date columns (`Order Date`, `Ship Date`) are in a format Pandas can parse
    (e.g., `YYYY-MM-DD`). If not, you might need to adjust the `pd.to_datetime`
    conversion in the `load_data` function or specify a `format` argument.
    """
)
