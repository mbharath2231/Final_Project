import requests
import pandas as pd
import time
import os

# ==========================================
# 👇 PASTE YOUR KEYS HERE
# ==========================================
ADZUNA_APP_ID  = "4754d954"
ADZUNA_APP_KEY = "ccada37fb80ad1dca86725f13f365a45"

def fetch_all_columns():
    print("🕵️ Fetching ALL available data for 50 jobs...")
    
    all_jobs_raw = []
    
    # Loop through 5 pages
    for page in range(1, 10):
        print(f"   ... Requesting Page {page}")
        
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": 10,
            "what": "Software Engineer",
            "content-type": "application/json"
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    # EXTEND the list with the raw dictionaries
                    # We don't filter anything here. We take it all.
                    all_jobs_raw.extend(data['results'])
            else:
                print(f"   ❌ Error on page {page}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            
        time.sleep(1)

    # --- SAVE ALL COLUMNS ---
    if all_jobs_raw:
        # MAGIC LINE: This flattens the nested JSON into distinct columns
        # e.g., 'company': {'display_name': 'Google'} becomes column 'company.display_name'
        df = pd.json_normalize(all_jobs_raw)
        
        # Calculate Path
        current_folder = os.path.dirname(os.path.abspath(__file__))
        project_folder = os.path.dirname(current_folder)
        output_path = os.path.join(project_folder, 'data', 'raw_jobs_full.csv')
        
        df.to_csv(output_path, index=False)

        print(df.head())
        
        # print("\n" + "="*50)
        # print(f"🎉 Success! Fetched {len(df)} jobs with {len(df.columns)} columns.")
        # print(f"💾 Saved to: {output_path}")
        # print("="*50)
        
        # print("\n👇 HERE ARE THE COLUMNS YOU NOW HAVE:")
        # for col in df.columns:
        #     print(f"   - {col}")
        
    else:
        print("❌ No jobs found.")

if __name__ == "__main__":
    fetch_all_columns()