import pandas as pd
import os

def debug_city_names():
    print("🕵️ INSPECTING CITY NAMES FOR MISMATCHES...")
    
    # 1. Load Data
    current_script = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(os.path.dirname(current_script), 'data')
    
    jobs_df = pd.read_csv(os.path.join(data_folder, "raw_jobs_multi.csv"))
    econ_df = pd.read_csv(os.path.join(data_folder, "economy_data.csv"))
    col_df = pd.read_csv(os.path.join(data_folder, "cost_of_living.csv"))
    
    # 2. Define the SAME cleaning function you use in your pipeline
    def clean_city_test(row):
        if pd.isna(row): return "unknown"
        c = str(row).lower().strip()
        c = c.split(',')[0].strip() # Remove state
        c = c.replace("st.", "saint")
        return c

    # 3. Apply Cleaning
    # Jobs (Adzuna)
    loc_col = 'location.display_name' if 'location.display_name' in jobs_df.columns else 'location'
    jobs_cities = set(jobs_df[loc_col].apply(clean_city_test).unique())
    
    # Economy (BLS)
    econ_cities = set(econ_df['City'].apply(clean_city_test).unique())
    
    # Cost of Living (Numbeo)
    numbeo_col = 'City' if 'City' in col_df.columns else col_df.columns[0]
    col_cities = set(col_df[numbeo_col].apply(clean_city_test).unique())
    
    # 4. DIAGNOSTICS
    print("\n🔍 SAMPLE CITIES (Top 5 from each file):")
    print(f"   Jobs File:    {list(jobs_cities)[:5]}")
    print(f"   Economy File: {list(econ_cities)[:5]}")
    print(f"   Cost File:    {list(col_cities)[:5]}")
    
    print("\n⚠️ MATCH FAILURE ANALYSIS:")
    # Check specific major cities to see why they fail
    test_cities = ["new york", "san francisco", "austin", "chicago", "boston"]
    
    print(f"{'CITY':<15} | {'IN JOBS?':<10} | {'IN ECONOMY?':<12} | {'IN COST?':<10}")
    print("-" * 55)
    
    for city in test_cities:
        in_jobs = "✅" if city in jobs_cities else "❌"
        in_econ = "✅" if city in econ_cities else "❌"
        in_cost = "✅" if city in col_cities else "❌"
        print(f"{city:<15} | {in_jobs:<10} | {in_econ:<12} | {in_cost:<10}")

if __name__ == "__main__":
    debug_city_names()