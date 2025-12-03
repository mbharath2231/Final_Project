import pandas as pd
import numpy as np
import os
import ast
# Import ALL necessary config dictionaries
from config import STATE_MAP, CITY_TO_STATE, STATE_COORDS

def run_pipeline():
    print("⚙️ STARTING PIPELINE (Using Config for Coordinates)...")
    
    # 1. LOAD
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    jobs = pd.read_csv(os.path.join(data_dir, "raw_jobs_multi.csv"))
    econ = pd.read_csv(os.path.join(data_dir, "economy_data.csv"))
    cost = pd.read_csv(os.path.join(data_dir, "cost_of_living.csv"))

    # 2. ENRICH ECONOMY WITH STATES
    econ['State_Ref'] = econ['City'].map(CITY_TO_STATE)
    ref_econ = econ.groupby('State_Ref')['Unemployment_Rate'].mean().to_dict()
    
    c_col = 'City' if 'City' in cost.columns else cost.columns[0]
    cost['State_Ref'] = cost[c_col].apply(lambda x: CITY_TO_STATE.get(str(x).split(',')[0].strip()))
    ref_cost = cost.groupby('State_Ref')['Cost of Living Index'].mean().to_dict()

    # 3. PARSE JOB LOCATIONS
    def parse_loc(row):
        city, state = "Unknown", "Unknown"
        try:
            area = ast.literal_eval(row.get('location.area', "[]"))
            if isinstance(area, list) and len(area) > 1:
                # Find State
                for item in reversed(area):
                    if item in STATE_MAP: state = STATE_MAP[item]
                    elif item in STATE_MAP.values(): state = item
                # Find City
                clean_items = [x for x in area if x not in STATE_MAP and x != 'US']
                if clean_items: city = clean_items[-1]
        except: pass
        return pd.Series([city.lower().strip(), state])

    jobs[['City_Key', 'State']] = jobs.apply(parse_loc, axis=1)

    # 4. MERGE
    def clean_key(val): return str(val).lower().strip().replace("st.", "saint")
    jobs['City_Key'] = jobs['City_Key'].apply(clean_key)
    econ['City_Key'] = econ['City'].apply(clean_key)
    cost['City_Key'] = cost[c_col].apply(clean_key)

    df = pd.merge(jobs, econ[['City_Key', 'Unemployment_Rate']], on='City_Key', how='left')
    cost_grp = cost.groupby('City_Key')[['Cost of Living Index']].mean().reset_index()
    df = pd.merge(df, cost_grp, on='City_Key', how='left')

    # 5. IMPUTE (State -> National)
    df['State_Unemp'] = df['State'].map(ref_econ)
    df['Unemployment_Rate'] = df['Unemployment_Rate'].fillna(df['State_Unemp']).fillna(3.8)
    
    df['State_Cost'] = df['State'].map(ref_cost)
    df['Cost of Living Index'] = df['Cost of Living Index'].fillna(df['State_Cost']).fillna(75)

    # 6. SALARY & REAL WAGE
    df['salary_min'] = pd.to_numeric(df['salary_min'], errors='coerce')
    df = df[df['salary_min'] > 15000] # Filter hourly
    
    df['Salary'] = df.groupby('search_role')['salary_min'].transform(lambda x: x.fillna(x.median()))
    df['Salary'] = df['Salary'].fillna(df['Salary'].median())
    
    df['Real_Wage'] = df['Salary'] / (df['Cost of Living Index'] / 100)

    # 7. FIX MISSING COORDINATES (Using STATE_COORDS from Config)
    def fill_lat(row):
        if pd.notna(row['latitude']): return row['latitude']
        return STATE_COORDS.get(row['State'], (None, None))[0]

    def fill_lon(row):
        if pd.notna(row['longitude']): return row['longitude']
        return STATE_COORDS.get(row['State'], (None, None))[1]

    df['latitude'] = df.apply(fill_lat, axis=1)
    df['longitude'] = df.apply(fill_lon, axis=1)
    
    # Fill remaining (Totally Unknown) with US Center
    df['latitude'] = df['latitude'].fillna(39.8)
    df['longitude'] = df['longitude'].fillna(-98.5)

    # 8. SAVE CLEAN FILE
    rename_map = {'search_role': 'Role', 'company.display_name': 'Company', 
                  'location.display_name': 'Location', 'latitude': 'Latitude', 'longitude': 'Longitude'}
    
    final_cols = ['Role', 'Company', 'Location', 'City_Key', 'State', 'Salary', 'Real_Wage', 
                  'Unemployment_Rate', 'Cost of Living Index', 'description', 'Latitude', 'Longitude']
    
    cols_to_keep = [c for c in final_cols if c in df.rename(columns=rename_map).columns]
    
    df_clean = df.rename(columns=rename_map)[cols_to_keep]
    df_clean.to_csv(os.path.join(data_dir, 'cleaned_master_dataset.csv'), index=False)
    print("🎉 SUCCESS! Pipeline Finished.")

if __name__ == "__main__":
    run_pipeline()