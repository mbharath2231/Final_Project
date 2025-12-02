import streamlit as st
import pandas as pd
import numpy as np

# 1. SETUP
st.set_page_config(page_title="Real-Wage Calculator", layout="wide")

# Load Data
@st.cache_data
def load_data():
    # Go up one level from 'app' to find 'data'
    return pd.read_csv("data/master_dataset.csv")

try:
    df = load_data()
except:
    st.error("⚠️ Data not found! Run scripts/03_force_fix.py first.")
    st.stop()

# 2. SIDEBAR
with st.sidebar:
    st.title("🎛️ Settings")
    
    # Role Filter
    roles = sorted(df['search_role'].unique())
    selected_role = st.selectbox("Job Role", roles)
    
    # Filter Data by Role
    filtered_df = df[df['search_role'] == selected_role]
    
    # Salary Slider
    min_sal = int(filtered_df['salary_min'].min())
    max_sal = int(filtered_df['salary_min'].max())
    salary_filter = st.slider("Min Salary", min_sal, max_sal, 90000)
    
    # City Filter
    all_cities = sorted(filtered_df['merge_city'].unique())
    default_cities = ["new york", "austin", "chicago"]
    # Only default to cities that actually exist in the data
    valid_defaults = [c for c in default_cities if c in all_cities]
    
    selected_cities = st.multiselect("Cities to Compare", all_cities, default=valid_defaults)

# 3. MAIN DASHBOARD
st.title(f"💰 Real-Wage Calculator: {selected_role}")

# Filter Logic
display_df = filtered_df[filtered_df['merge_city'].isin(selected_cities)]
if display_df.empty:
    st.warning("No jobs found for these filters. Try adding more cities!")
else:
    # A. KPI ROW
    avg_salary = display_df['salary_min'].mean()
    avg_real = display_df['Real_Wage'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Nominal Salary", f"${avg_salary:,.0f}")
    col2.metric("Avg Real Wage (Purchasing Power)", f"${avg_real:,.0f}", 
                delta=f"{(avg_real-avg_salary)/avg_salary:.1%} Value")
    col3.metric("Avg Unemployment Risk", f"{display_df['Unemployment_Rate'].mean():.1f}%")

    st.divider()

    # B. CHARTS
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💸 Salary vs. Real Wage")
        # Simple Bar Chart
        chart_data = display_df.groupby('merge_city')[['salary_min', 'Real_Wage']].mean()
        st.bar_chart(chart_data)
        
    with c2:
        st.subheader("📉 Unemployment Risk")
        risk_data = display_df.groupby('merge_city')['Unemployment_Rate'].mean()
        st.line_chart(risk_data)

    # C. DATA TABLE
    st.subheader("📄 Top Job Listings")
    st.dataframe(
        display_df[['title', 'Company', 'merge_city', 'salary_min', 'Real_Wage']]
        .sort_values('Real_Wage', ascending=False)
        .head(10)
    )