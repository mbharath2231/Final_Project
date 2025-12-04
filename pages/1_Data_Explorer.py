import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import plotly.express as px
import pydeck as pdk
st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")

# ---------------------------------------------------------
# 1. CONTEXT DICTIONARY
# ---------------------------------------------------------
dataset_context = {
    "✨ Final Cleaned Master": """
    ### 🏆 The Gold Standard Record
    **Role:** The engine of the application.
    **Construction:** This dataset is the result of merging the three raw sources below using a robust ETL pipeline.
    **Key Features:**
    * **`Real_Wage`:** A synthetic metric calculated as `Salary / (Cost_Index / 100)`.
    * **`State`:** Extracted via NLP from raw location strings.
    * **`Salary`:** Imputed using Hierarchical Grouping (Role > City > National).
    """,
    
    "📦 Raw Jobs (Adzuna)": """
    ### 🕵️ Source 1: The Market Pulse
    **Origin:** [Adzuna API](https://developer.adzuna.com/)
    **Purpose:** Provides real-time labor market data.
    **Why we need it:**
    * **`Salary_Min/Max`:** The baseline for our predictions.
    * **`Description`:** The raw text used for our NLP Skill Extractor.
    * **`Location`:** The messy string we must parse to find coordinates.
    """,
    
    "📉 Economy (BLS)": """
    ### 🏛️ Source 2: Economic Risk
    **Origin:** [Bureau of Labor Statistics (BLS)](https://www.bls.gov/developers/)
    **Purpose:** Quantifies "Career Stability" for a given location.
    **Why we need it:**
    * High salaries in unstable markets are risky. 
    * We use **Unemployment Rate** as a proxy for "Market Risk."
    * *Note:* Cities not found here are imputed using State-Level averages.
    """,
    
    "🛒 Cost of Living (Numbeo)": """
    ### 🛒 Source 3: The Reality Check
    **Origin:** [Numbeo / Kaggle](https://www.kaggle.com/datasets/debdutta/cost-of-living-index-by-country)
    **Purpose:** Calculates the *true* value of a dollar.
    **Why we need it:**
    * **`Cost of Living Index`:** Used to deflate nominal salaries. (NYC = 100.0, Austin = 70.5).
    * **`Rent Index`:** Used to validate housing affordability (though not used in the main Real Wage formula).
    """
}

# ---------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------
current_script = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_script)
data_folder = os.path.join(project_root, 'data')

print("DAta", data_folder)

@st.cache_data
def load_all_data():
    datasets = {}
    
    # Define paths
    files = {
        "✨ Final Cleaned Master": f"{data_folder}/cleaned_master_dataset.csv",
        "📦 Raw Jobs (Adzuna)": f"{data_folder}/raw_jobs_multi.csv",
        "📉 Economy (BLS)": f"{data_folder}/economy_data.csv",
        "🛒 Cost of Living (Numbeo)": f"{data_folder}/cost_of_living.csv"
    }
    for name, path in files.items():
        if os.path.exists(path):
            datasets[name] = pd.read_csv(path)
        else:
            datasets[name] = None
    return datasets

all_datasets = load_all_data()

# ---------------------------------------------------------
# 3. SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("🗂️ Data Sources")
selected_name = st.sidebar.radio("Select Dataset:", list(all_datasets.keys()))
df = all_datasets[selected_name]

if df is None:
    st.error("File not found. Run pipeline first!")
    st.stop()

# ---------------------------------------------------------
# 4. MAIN ANALYSIS
# ---------------------------------------------------------
st.title(f"📊 Explorer: {selected_name.split(' ')[1:]}")
st.info(dataset_context.get(selected_name, ""))
st.caption(f"Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Raw Data", "📈 Statistics", "🔍 Data Quality", "Advanced Analysis", "Model Evaluation"])

# --- TAB 1: RAW DATA ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        if 'Role' in df.columns:
            role_filter = st.multiselect("Filter by Role", sorted(df['Role'].unique()))
            if role_filter: df = df[df['Role'].isin(role_filter)]
    with col2:
        if 'State' in df.columns:
            state_filter = st.multiselect("Filter by State", sorted(df['State'].unique()))
            if state_filter: df = df[df['State'].isin(state_filter)]

    st.dataframe(df, use_container_width=True)

# --- TAB 2: STATISTICS ---
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔢 Numerical Stats")
        st.dataframe(df.describe(), use_container_width=True)
    with c2:
        st.subheader("🔠 Text Analysis")
        obj_cols = df.select_dtypes(include=['object']).columns.tolist()
        if obj_cols:
            target = st.selectbox("Select Column", obj_cols)
            st.write(df[target].value_counts().head(10))
        else:
            st.info("No text columns.")

# --- TAB 3: DATA QUALITY (With Heatmap!) ---
with tab3:
    st.subheader("Data Health Dashboard")
    
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    
    # 1. THE MISSING VALUES BAR CHART
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ❌ Missing Values Count")
        if nulls.empty:
            st.success("✅ Dataset is 100% Clean!")
        else:
            st.warning(f"Found missing values in {len(nulls)} columns.")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(x=nulls.values, y=nulls.index, ax=ax, palette="Reds_r")
            ax.set_xlabel("Count of Missing Rows")
            st.pyplot(fig)

    # 2. THE DISTRIBUTION PLOT
    with c2:
        st.markdown("### 📊 Value Distribution")
        num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        priority = ['Real_Wage', 'Salary', 'Unemployment_Rate', 'Cost of Living Index']
        best_col = next((c for c in priority if c in num_cols), num_cols[0] if num_cols else None)
        
        if best_col:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.histplot(df[best_col], kde=True, ax=ax2, color="blue")
            ax2.set_title(f"Histogram: {best_col}")
            st.pyplot(fig2)

    st.divider()

    # 3. THE HEATMAP (New Feature!)
    st.markdown("### 🔥 Missingness Heatmap")
    st.caption("This visualization helps you see patterns. **Yellow lines** indicate missing data.")
    
    # We create a figure for the heatmap
    fig_heat, ax_heat = plt.subplots(figsize=(12, 6))
    
    # Draw the heatmap (df.isnull() returns True/False matrix)
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap='viridis', ax=ax_heat)
    
    st.pyplot(fig_heat)

with tab4:
    st.header("💡 Deep Dive: Salary Insights")
    
    # Only show this if we are on the Master Dataset
    if {'Salary', 'Cost of Living Index', 'Real_Wage', 'Role'}.issubset(df.columns):
        
        # 1. SCATTER PLOT: THE "VALUE" MATRIX
        st.subheader("1. The 'Value' Matrix: Cost vs. Pay")
        st.caption("Are you getting paid enough to live there? **Top-Left** is the ideal spot (High Pay, Low Cost).")
        
        fig_scatter = px.scatter(
            df,
            x="Cost of Living Index",
            y="Salary",
            color="Role",
            size="Real_Wage", # Larger bubble = Better deal
            hover_data=["City_Key", "State", "Real_Wage"],
            trendline="ols", # Adds a regression line to show the trend
            title="Nominal Salary vs. Cost of Living (Size = Real Purchasing Power)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.divider()

        # 2. BOX PLOT: SALARY RANGES
        st.subheader("2. Salary Ranges by Role")
        st.caption("Comparing the spread of salaries. The box shows the median and the middle 50%.")
        
        fig_box = px.box(
            df,
            x="Role",
            y="Salary",
            color="Role",
            points="all", # Show individual dots too
            title="Salary Distribution per Role"
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.divider()
        
        # 3. CORRELATION HEATMAP (FIXED)
        st.subheader("3. Correlation Matrix")
        
        # Define the Wishlist of columns we want to correlate
        target_cols = ['Salary', 'Real_Wage', 'Unemployment_Rate', 'Cost of Living Index', 'Rent Index']
        
        # KEY FIX: Only select columns that ACTUALLY EXIST in the dataframe
        valid_corr_cols = [c for c in target_cols if c in df.columns]
        
        if len(valid_corr_cols) > 1:
            corr_matrix = df[valid_corr_cols].corr()
            fig_corr = px.imshow(
                corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r",
                title="Correlation Heatmap (1.0 = Perfect Correlation)"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("Not enough numeric columns found for correlation analysis.")

    else:
        st.info("Select the **Final Cleaned Master** dataset to see advanced analytics.")
    
    # In app/pages/1_📊_Data_Explorer.py
# ... inside the tabs ...

with tab5: # or a new tab
    st.subheader("🤖 Model Evaluation Metrics")
    st.caption("Visual proof of the Machine Learning model's accuracy on unseen data.")
    
    # Load the image we just generated
    import os
    # Go up to project root to find models folder
    model_img_path = "models/model_performance.png"
    
    if os.path.exists(model_img_path):
        st.image(model_img_path, caption="Predicted vs. Actual Salary (Linearity indicates accuracy)", use_container_width=True)
    else:
        st.warning("Model performance chart not found. Run '04_train_models.py' again.")