import requests
import pandas as pd
import time
import os

ADZUNA_ID = "4754d954"
ADZUNA_KEY = "ccada37fb80ad1dca86725f13f365a45"

def fetch_mega_role_data():
    print("🕵️ STARTING MEGA-ROLE DATA FETCH (9 Categories)...")
    
    # 1. THE EXPANDED ROLE LIST
    roles_to_search = [
        # Data Family
        "Data Scientist",
        "Data Analyst",
        "Data Engineer",
        "Machine Learning Engineer",
        "Business Analyst",
        
        # The New Additions
        "AI Engineer",         # Trending!
        "DevOps Engineer",     # High demand
        "Database Engineer",   # Stability
        "Software Engineer"    # The Baseline
    ]
    
    all_jobs_raw = []
    
    # 2. LOOP THROUGH EACH ROLE
    for role in roles_to_search:
        print(f"\n🔎 Searching for: {role.upper()}")
        
        # Fetch 10 pages per role (100 jobs per role)
        for page in range(1, 11):
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
            params = {
                "app_id": ADZUNA_ID,
                "app_key": ADZUNA_KEY,
                "results_per_page": 10,
                "what": role,
                "content-type": "application/json"
            }
            
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data:
                        found_count = len(data['results'])
                        print(f"   ... Page {page}: Found {found_count} jobs")
                        
                        # Tag jobs with the specific role
                        for job in data['results']:
                            job['search_role'] = role 
                            all_jobs_raw.append(job)
                else:
                    print(f"   ❌ Error on Page {page}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Connection failed: {e}")
            
            time.sleep(1) # Be polite!

    # 3. SAVE THE MASSIVE DATASET
    if all_jobs_raw:
        # Flatten the data
        df = pd.json_normalize(all_jobs_raw)
        
        # Path Logic
        current_folder = os.path.dirname(os.path.abspath(__file__))
        project_folder = os.path.dirname(current_folder)
        data_folder = os.path.join(project_folder, 'data')
        
        # We overwrite the previous multi file
        output_path = os.path.join(data_folder, 'raw_jobs_multi.csv')
        df.to_csv(output_path, index=False)
        
        print("\n" + "="*50)
        print(f"🎉 SUCCESS! Collected {len(df)} total jobs.")
        print(f"💾 Saved to: {output_path}")
        print("="*50)
        
        # Verification Report
        print("\n📊 Job Counts by Role:")
        print(df['search_role'].value_counts())
        
    else:
        print("❌ No jobs found.")

if __name__ == "__main__":
    fetch_mega_role_data()