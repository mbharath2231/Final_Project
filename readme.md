# 💰 Real-Wage Career Calculator

### *Don't just chase the highest salary. Chase the highest value.*

## 📖 Project Overview
The **Real-Wage Career Calculator** is a data science application designed to help job seekers understand the true purchasing power of a salary offer. 

A \$120,000 salary in New York City is often worth *less* than \$90,000 in Austin, Texas, once taxes and cost of living are factored in. This tool scrapes live job data, integrates it with government economic statistics, and uses Machine Learning to predict the "Real Wage" of various tech roles across the US.

## 🚀 Features
* **Live Market Data:** Fetches real-time job listings from the Adzuna API.
* **Real-Wage Engine:** Adjusts nominal salaries using State-Level Cost of Living indices.
* **Salary Predictor:** A Random Forest model that predicts the fair market rate for a role in a specific city.
* **Skill Analyzer:** Uses NLP to identify which keywords (e.g., "AWS", "Docker") correlate with higher pay.
* **Interactive Map:** Visualizes job hotspots and remote work opportunities.

## 📊 Data Sources (3-Source Integration)
This project integrates three distinct datasets into a single master record:
1.  **Job Listings (Adzuna API):** Source of job titles, companies, raw salaries, and descriptions.
2.  **Economic Risk (BLS API):** Bureau of Labor Statistics data for Unemployment Rates by Metro Area.
3.  **Cost of Living (Numbeo Dataset):** Static indices for rent and consumer prices.

## 🛠️ Methodology & Pipeline
The project utilizes a robust **ETL Pipeline** (`scripts/03_clean_merge.py`) to process the data:

### 1. Data Cleaning & Integration
* **Fuzzy Matching / State Extraction:** Standardized over 300+ unique city names (e.g., "St. Louis" vs "Saint Louis") to ensure successful merging with economic data.
* **State-Level Imputation:** If a specific city's economic data was missing, the pipeline calculates the average for that **State** (e.g., filling a missing Texas city with the TX average) rather than a generic national average.

### 2. Machine Learning Models
* **Salary Prediction (Regression):** A `RandomForestRegressor` trained on Role and State to predict salary outcomes ($R^2 \approx 0.78$).
* **Skill Valuation (NLP):** A dictionary-based extraction method combined with Linear Regression to quantify the dollar value of specific technical skills.

## 💻 Installation & Usage

### Prerequisites
* Python 3.10+
* Adzuna API Key (Free)
* BLS API Key (Free)

### Setup
1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Real-Wage-Calculator.git](https://github.com/YOUR_USERNAME/Real-Wage-Calculator.git)
    cd Real-Wage-Calculator
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure Keys:
    * Open `scripts/config.py` and paste your API keys.

4.  Run the Data Pipeline (Optional - Pre-computed data is included):
    ```bash
    python scripts/03_clean_merge.py
    python scripts/04_train_models.py
    ```

5.  **Launch the App:**
    ```bash
    streamlit run app/main.py
    ```

## 📂 File Structure
```text
├── app/
│   └── main.py              # The Streamlit Dashboard application
├── data/
│   ├── cleaned_master.csv   # The final processed dataset
│   └── raw_jobs_multi.csv   # Raw API fetch results
├── models/
│   ├── salary_model.pkl     # Trained Random Forest Model
│   └── top_skills.csv       # NLP analysis results
├── scripts/
│   ├── 01_fetch_jobs.py     # Adzuna API Scraper
│   ├── 02_fetch_economy.py  # BLS API Scraper
│   ├── 03_clean_merge.py  # ETL & Cleaning Logic
│   ├── 04_train_models.py   # ML Training Logic
│   └── config.py            # API Keys & Reference Maps
└── requirements.txt         # Project dependencies