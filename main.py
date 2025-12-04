import streamlit as st
import pandas as pd
import numpy as np
import pickle
import pydeck as pdk
import os

# ---------------------------------------------------------
# 1. APP CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Real-Wage Career Calculator",
    page_icon="💰",
    layout="wide"
)

# Custom CSS to make it look professional
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOAD RESOURCES
# ---------------------------------------------------------

current_script = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_script)
data_folder = os.path.join(current_script, 'data')
models_folder = os.path.join(current_script, 'models')

print("Current", current_script)
print(data_folder)

@st.cache_data
def load_data():
    # Load the Cleaned Dataset
    # We go up one level from 'app' folder to find 'data'
    return pd.read_csv(f"{data_folder}/cleaned_master_dataset.csv")

@st.cache_resource
def load_models():
    # Load ML Models & Artifacts
    with open(f"{models_folder}/salary_model.pkl", 'rb') as f:
        model = pickle.load(f)
    with open(f"{models_folder}/model_columns.pkl", 'rb') as f:
        model_cols = pickle.load(f)
    skills = pd.read_csv(f"{models_folder}/top_skills.csv")
    return model, model_cols, skills

# try:
df = load_data()
salary_model, model_cols, top_skills = load_models()
# except FileNotFoundError:
#     st.error("⚠️ Error: Missing files! Make sure you ran the pipeline and training scripts.")
#     st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR (User Inputs)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🎛️ Career Settings")
    
    # ROLE SELECTOR
    available_roles = sorted(df['Role'].unique())
    selected_role = st.selectbox("I am a...", available_roles, index=0)
    
    # Filter Data for this Role
    role_df = df[df['Role'] == selected_role]
    
    # CITY SELECTOR (For Comparison)
    available_cities = sorted(role_df['City_Key'].unique())
    # Smart Defaults: Try to pick major cities if they exist in the data
    default_try = ["new york", "austin", "san francisco"]
    defaults = [c for c in default_try if c in available_cities]
    
    selected_cities = st.multiselect("Compare Cities", available_cities, default=defaults)
    
    st.divider()
    st.caption(f"Analyzing {len(role_df)} jobs for {selected_role}")
    
    # Show 'Remote' Toggle
    show_remote = st.toggle("Include Remote Jobs", value=True)
    if not show_remote:
        # Assuming we can filter by State='Unknown' or similar logic if you had a 'work_type' column
        # For now, we'll just filter out Generic locations if coordinates are missing
        role_df = role_df.dropna(subset=['Latitude'])

# ---------------------------------------------------------
# 4. MAIN DASHBOARD
# ---------------------------------------------------------
st.title("💰 The Real-Wage Calculator")
st.markdown("### *Don't just chase the highest salary. Chase the highest value.*")

# A. KEY METRICS (Top Row)
# ---------------------------------------
if selected_cities:
    # Filter for the specific cities selected
    metrics_df = role_df[role_df['City_Key'].isin(selected_cities)]
else:
    metrics_df = role_df # Show all if nothing selected

if not metrics_df.empty:
    avg_salary = metrics_df['Salary'].mean()
    avg_real = metrics_df['Real_Wage'].mean()
    avg_risk = metrics_df['Unemployment_Rate'].mean()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg. Nominal Salary", f"${avg_salary:,.0f}", help="The dollar amount on the offer letter.")
    c2.metric("Avg. Real Purchasing Power", f"${avg_real:,.0f}", 
              delta=f"{(avg_real - avg_salary):,.0f} vs Nominal",
              help="Salary adjusted for Cost of Living. Green means you are 'richer' than you look.")
    c3.metric("Market Stability (Unemployment)", f"{avg_risk:.1f}%", delta_color="inverse")
    
    st.divider()

# ... inside Home.py ...

# B. VISUALIZATIONS (Middle Row)
# ---------------------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"📍 Map: Where are the {selected_role} jobs?")
    
    # 1. Filter valid data
    map_data = role_df.dropna(subset=['Latitude', 'Longitude'])
    
    # 2. DEBUG: Check if we actually have data
    if map_data.empty:
        st.warning("No GPS data available. (Try running the pipeline again!)")
    else:
        # Display the count so you know it's working
        st.caption(f"Plotting {len(map_data)} locations...")

        # 3. Define the Map Layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position='[Longitude, Latitude]', # This string syntax is correct for PyDeck
            get_color=[0, 100, 255, 160],         # <--- FIX: Removed quotes (Must be a List, not String)
            get_radius=25000,                     # Radius in meters (25km)
            pickable=True,                        # Enables Hover
            auto_highlight=True
        )

        # 4. Set the Initial View
        view_state = pdk.ViewState(
            latitude=38.0,
            longitude=-96.0,
            zoom=3,
            pitch=0,
        )

        # 5. Render
        st.pydeck_chart(pdk.Deck(
            map_style=None, # <--- FIX: 'None' uses Streamlit's default theme (Safest option)
            initial_view_state=view_state,
            layers=[layer],
            tooltip={
                "html": "<b>City:</b> {City_Key}<br/>"
                        "<b>Avg Salary:</b> ${Salary}<br/>"
                        "<b>Real Wage:</b> ${Real_Wage}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
        ))

with col_right:
    st.subheader("🧠 Top Value Skills")
    st.caption("Keywords that boost salary prediction:")
    
    # Display the top skills nicely
    st.dataframe(
        top_skills.head(10).style.format({'value': '+${:,.0f}'}),
        hide_index=True,
        use_container_width=True
    )

st.divider()

# C. THE AI PREDICTOR (Interactive Tool)
# ---------------------------------------
st.subheader("🤖 AI Salary Predictor")
st.info("Select a city below, and our AI will predict your salary based on market trends.")

with st.form("predict_form"):
    c1, c2 = st.columns(2)
    with c1:
        pred_city = st.selectbox("Target City", sorted(df['City_Key'].unique()))
    with c2:
        # We assume the Role is the one selected in Sidebar
        st.text_input("Role", value=selected_role, disabled=True)
        
    submitted = st.form_submit_button("Predict My Worth")
    
    if submitted:
        # 1. Create a "Blank" Input Row with all 0s
        input_data = pd.DataFrame(0, index=[0], columns=model_cols)
        
        # 2. Fill in the One-Hot Encoded columns
        # We need to match the column names exactly: "Role_Data Scientist"
        role_col = f"Role_{selected_role}"
        
        # Note: We used 'State' in the final training script, not City_Key
        # So we need to look up the State for this City first!
        # Find the state for the selected city
        city_row = df[df['City_Key'] == pred_city].iloc[0]
        pred_state = city_row['State']
        state_col = f"State_{pred_state}"
        
        # Set them to 1 if they exist in the model
        if role_col in input_data.columns:
            input_data[role_col] = 1
        if state_col in input_data.columns:
            input_data[state_col] = 1
            
        # 3. Predict
        prediction = salary_model.predict(input_data)[0]
        
        st.success(f"## 🎯 Predicted Salary: **${prediction:,.0f}**")
        st.caption(f"Based on: Role='{selected_role}' and Market='{pred_state}'")

# D. RAW DATA EXPLORER
# ---------------------------------------
with st.expander("📄 View Raw Job Listings"):
    # We create a display-friendly version
    display_cols = ['Company', 'Location_Original', 'Salary', 'Real_Wage', 'Unemployment_Rate']
    
    # Safety Check: Only show columns that actually exist
    valid_cols = [c for c in display_cols if c in role_df.columns]
    
    st.dataframe(
        role_df[valid_cols]
        .sort_values('Real_Wage', ascending=False)
        .rename(columns={'Location_Original': 'Location'}) # Rename it just for the UI!
    )