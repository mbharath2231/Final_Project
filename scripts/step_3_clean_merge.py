import pandas as pd
import numpy as np
import os
import ast

def run_salary_upgrade_pipeline():
    print("💎 STARTING GOLD-STANDARD PIPELINE (With Coordinates)...")
    
    # 1. LOAD DATA
    current_script = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script)
    data_folder = os.path.join(project_root, 'data')
    
    try:
        jobs_df = pd.read_csv(os.path.join(data_folder, "raw_jobs_multi.csv"))
        econ_df = pd.read_csv(os.path.join(data_folder, "economy_data.csv"))
        col_df = pd.read_csv(os.path.join(data_folder, "cost_of_living.csv"))
    except FileNotFoundError:
        print("❌ Error: Missing raw data files.")
        return

    # ---------------------------------------------------------
    # 2. CREATE REFERENCE STATE MAP
    # ---------------------------------------------------------
    city_to_state = {
        'New York': 'NY', 'Los Angeles': 'CA', 'Chicago': 'IL', 'Dallas': 'TX', 'Houston': 'TX',
        'Washington DC': 'DC', 'Miami': 'FL', 'Philadelphia': 'PA', 'Atlanta': 'GA', 'Boston': 'MA',
        'Phoenix': 'AZ', 'San Francisco': 'CA', 'Seattle': 'WA', 'San Diego': 'CA', 'Denver': 'CO',
        'Austin': 'TX', 'San Jose': 'CA', 'Nashville': 'TN', 'Charlotte': 'NC', 'Raleigh': 'NC',
        'Portland': 'OR', 'Minneapolis': 'MN', 'Detroit': 'MI', 'Tampa': 'FL', 'Orlando': 'FL',
        'Baltimore': 'MD', 'St. Louis': 'MO', 'Pittsburgh': 'PA', 'Sacramento': 'CA', 'Las Vegas': 'NV',
        'San Antonio': 'TX', 'Kansas City': 'MO', 'Columbus': 'OH', 'Indianapolis': 'IN', 'Cleveland': 'OH',
        'Cincinnati': 'OH', 'Salt Lake City': 'UT', 'Madison': 'WI', 'Milwaukee': 'WI', 'Buffalo': 'NY',
        'Richmond': 'VA', 'Virginia Beach': 'VA', 'Providence': 'RI', 'Hartford': 'CT', 'New Orleans': 'LA',
        'Louisville': 'KY', 'Memphis': 'TN', 'Oklahoma City': 'OK', 'Tulsa': 'OK', 'Albuquerque': 'NM',
        'Tucson': 'AZ', 'El Paso': 'TX', 'Honolulu': 'HI', 'Omaha': 'NE'
    }
    
    print("   ... Building Reference State Economics")
    econ_df['State_Ref'] = econ_df['City'].map(city_to_state)
    ref_state_econ = econ_df.groupby('State_Ref')['Unemployment_Rate'].mean().to_dict()
    
    numbeo_city_col = 'City' if 'City' in col_df.columns else col_df.columns[0]
    col_df['State_Ref'] = col_df[numbeo_city_col].apply(lambda x: city_to_state.get(str(x).split(',')[0].strip(), None))
    ref_state_cost = col_df.groupby('State_Ref')['Cost of Living Index'].mean().to_dict()

    # ---------------------------------------------------------
    # 3. JOB PROCESSING
    # ---------------------------------------------------------
    print("   ... Parsing Job Locations")
    
    state_map_full = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'California': 'CA', 'Colorado': 'CO', 
        'Connecticut': 'CT', 'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 
        'Illinois': 'IL', 'Indiana': 'IN', 'Massachusetts': 'MA', 'Maryland': 'MD', 'Michigan': 'MI',
        'Minnesota': 'MN', 'Missouri': 'MO', 'Nevada': 'NV', 'New Jersey': 'NJ', 'New York': 'NY', 
        'North Carolina': 'NC', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 
        'Tennessee': 'TN', 'Texas': 'TX', 'Virginia': 'VA', 'Washington': 'WA', 'Wisconsin': 'WI'
    }

    def parse_location(row):
        city, state = "Unknown", "Unknown"
        try:
            area_str = row.get('location.area', "[]")
            area_list = ast.literal_eval(area_str) if isinstance(area_str, str) else area_str
            
            if isinstance(area_list, list) and len(area_list) > 1:
                for item in reversed(area_list):
                    if item in state_map_full: state = state_map_full[item]
                    elif item in state_map_full.values(): state = item
                
                clean_items = [x for x in area_list if x not in state_map_full and x != 'US']
                if clean_items: city = clean_items[-1]
        except: pass
        return pd.Series([city.lower().strip(), state])

    jobs_df[['City_Key', 'State']] = jobs_df.apply(parse_location, axis=1)
    
    # 4. MERGE DATA
    print("   ... Merging Data")
    
    def clean_key(val): return str(val).lower().strip().replace("st.", "saint")
    
    jobs_df['City_Key'] = jobs_df['City_Key'].apply(clean_key)
    econ_df['City_Key'] = econ_df['City'].apply(clean_key)
    col_df['City_Key'] = col_df[numbeo_city_col].apply(clean_key)

    master_df = pd.merge(jobs_df, econ_df[['City_Key', 'Unemployment_Rate']], on='City_Key', how='left')
    
    col_grouped = col_df.groupby('City_Key')[['Cost of Living Index', 'Rent Index']].mean().reset_index()
    master_df = pd.merge(master_df, col_grouped, on='City_Key', how='left')

    # ---------------------------------------------------------
    # 5. IMPUTATION
    # ---------------------------------------------------------
    print("   ... Performing Reference-Based Imputation")
    
    def get_state_unemp(state): return ref_state_econ.get(state, np.nan)
    def get_state_cost(state): return ref_state_cost.get(state, np.nan)

    master_df['State_Unemp'] = master_df['State'].apply(get_state_unemp)
    master_df['Unemployment_Rate'] = master_df['Unemployment_Rate'].fillna(master_df['State_Unemp'])
    
    master_df['State_Cost'] = master_df['State'].apply(get_state_cost)
    master_df['Cost of Living Index'] = master_df['Cost of Living Index'].fillna(master_df['State_Cost'])
    
    master_df['Unemployment_Rate'] = master_df['Unemployment_Rate'].fillna(3.8)
    master_df['Cost of Living Index'] = master_df['Cost of Living Index'].fillna(75)
    master_df['Rent Index'] = master_df['Rent Index'].fillna(master_df['Cost of Living Index'] * 0.35)

    # ---------------------------------------------------------
    # 6. SALARY & REAL WAGE
    # ---------------------------------------------------------
    print("   ... Calculating Salaries & Real Wage")
    
    master_df['salary_min'] = pd.to_numeric(master_df['salary_min'], errors='coerce')
    master_df['salary_max'] = pd.to_numeric(master_df['salary_max'], errors='coerce')
    
    # Filter hourly
    master_df = master_df[master_df['salary_min'] > 15000]
    
    # Avg Salary
    master_df['Avg_Salary'] = master_df[['salary_min', 'salary_max']].mean(axis=1)
    
    # Impute Salary
    master_df['Avg_Salary'] = master_df.groupby('search_role')['Avg_Salary'].transform(lambda x: x.fillna(x.median()))
    master_df['Avg_Salary'] = master_df['Avg_Salary'].fillna(master_df['Avg_Salary'].median())

    # Real Wage
    master_df['Real_Wage'] = master_df['Avg_Salary'] / (master_df['Cost of Living Index'] / 100)

    # ---------------------------------------------------------
    # 7. SAVE (WITH COORDINATES)
    # ---------------------------------------------------------
    
    # The List of Columns to KEEP (Added Latitude/Longitude)
    cols = ['search_role', 'company.display_name', 'Location_Original', 'City_Key', 'State', 
            'Avg_Salary', 'Real_Wage', 'Unemployment_Rate', 'Cost of Living Index', 'description',
            'latitude', 'longitude'] # <--- SAVED HERE
    
    # Rename for App
    rename_map = {
        'search_role': 'Role', 'company.display_name': 'Company',
        'location.display_name': 'Location_Original', 
        'latitude': 'Latitude', 'longitude': 'Longitude',
        'Avg_Salary' : 'Salary'
    }
    
    # Keep and Rename
    valid_cols = [c for c in cols if c in master_df.columns]
    master_df = master_df[valid_cols].rename(columns=rename_map)

    output_path = os.path.join(data_folder, 'cleaned_master_dataset.csv')
    master_df.to_csv(output_path, index=False)
    
    print("\n" + "="*50)
    print("🎉 PIPELINE UPDATED. Coordinates Preserved.")
    print(f"   📄 Saved to: {output_path}")
    print("="*50)

if __name__ == "__main__":
    run_salary_upgrade_pipeline()