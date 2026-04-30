import streamlit as st

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Real-Wage Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. HEADER
st.title("🧭 The Real-Wage Career Calculator")
st.subheader("A Data Science Approach to Finding Your True Purchasing Power")
st.divider()

# 3. THE NARRATIVE (The "Why")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 📖 The Problem: The "Money Illusion"
    Graduating Data Scientists often face a dilemma: **High Salary vs. High Cost of Living.**
    
    Traditional job boards only show you the **Nominal Salary** (the gross number). They fail to account for the **Real Purchasing Power** of that income.
    
    ### 💡 The Solution
    This application is a **Decision Support System** that scrapes live market data, integrates economic risk factors, and uses Machine Learning to predict the *true* value of a job offer.
    """)

st.divider()

# 4. DATA PIPELINE VISUALIZATION
st.header("🛠️ How It Works: The Data Pipeline")
st.caption("This project integrates three disparate data sources into a single analytical engine.")

# We use columns to create a "Diagram" look
c1, c2, c3, c4, c5 = st.columns([1, 0.2, 1, 0.2, 1])

with c1:
    st.markdown("#### 📥 1. Ingestion")
    st.success("**Adzuna API**")
    st.caption("Live Job Listings (Text & Salary)")
    st.success("**BLS API**")
    st.caption("Unemployment Data (Risk)")
    st.success("**Numbeo**")
    st.caption("Cost of Living Indices")

with c2:
    st.markdown("<h1 style='text-align: center; color: grey;'>➔</h1>", unsafe_allow_html=True)

with c3:
    st.markdown("#### ⚙️ 2. Processing")
    st.warning("**ETL Pipeline**")
    st.caption("• Fuzzy City Matching")
    st.caption("• State-Level Imputation")
    st.caption("• NLP Skill Extraction")
    st.caption("• 'Real Wage' Calculation")

with c4:
    st.markdown("<h1 style='text-align: center; color: grey;'>➔</h1>", unsafe_allow_html=True)

with c5:
    st.markdown("#### 🚀 3. Application")
    st.error("**The Dashboard**")
    st.caption("• Salary Prediction (ML)")
    st.caption("• Interactive Maps")
    st.caption("• Skill Valuation")

st.divider()

# 5. KEY FEATURES
st.header("🌟 Key Features")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("### 🤖 ML Salary Predictor")
    st.write("A **Random Forest Regressor** ($R^2 \\approx 0.80$) that predicts the fair market salary for any role in any US city, helping you negotiate better offers.")

with f2:
    st.markdown("### 🧠 NLP Skill Analyzer")
    st.write("A text-mining engine that scans thousands of job descriptions to identify **High-Value Keywords** (e.g., 'Kubernetes') that statistically boost your pay.")

with f3:
    st.markdown("### 🗺️ Interactive Geography")
    st.write("A **3D Map** powered by PyDeck that visualizes job density and salary hotspots, filtering out remote/generic listings for precision.")

st.divider()

st.markdown("""
<div style="text-align: center; color: grey;">
    <i>Built with ❤️ for the STT 811 Final Project</i>
</div>
""", unsafe_allow_html=True)