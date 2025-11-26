import requests
import pandas as pd

ADZUNA_ID = "4754d954"
ADZUNA_KEY = "ccada37fb80ad1dca86725f13f365a45"

print("First one")

def get_jobs_safely():
    print("🕵️ Connecting to Adzuna...")
    
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    
    params = {
        "app_id": ADZUNA_ID,
        "app_key": ADZUNA_KEY,
        "results_per_page": 10,
        "what": "Data Scientist",
        "content-type": "application/json"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # 1. Get the raw data
        raw_data = response.json()
        
        # 2. DEBUG PRINT: Check what we actually got
        print(f" DataType Received: {type(raw_data)}")
        
        # 3. Handle the data based on its type
        jobs_list = []
        
        if isinstance(raw_data, dict):
            # Normal behavior: It's a dictionary, look for 'results'
            if 'results' in raw_data:
                jobs_list = raw_data['results']
            else:
                print("⚠️ Dictionary found, but no 'results' key inside.")
                print("Keys found:", raw_data.keys())
                
        elif isinstance(raw_data, list):
            # Abnormal behavior: It's already a list (maybe from a different endpoint)
            jobs_list = raw_data
            
        # 4. Check if we found jobs
        if jobs_list:
            print(f"✅ Success! Found {len(jobs_list)} jobs.")
            
            # Print the first one to prove it works
            first_job = jobs_list[0]
            print(f"   Sample: {first_job.get('title')} at {first_job.get('company', {}).get('display_name')}")
            
            # Save to CSV
            df = pd.DataFrame(jobs_list)
            df.head()
            # Pick only useful columns if they exist
            cols = ['title', 'company', 'location', 'salary_min', 'description']
            # Only select columns that actually exist in the data
            valid_cols = [c for c in cols if c in df.columns] 
            print(valid_cols)
            # Note: Company/Location are often nested dictionaries, so we keep the raw DF for now
            # to avoid errors. We will clean it in Phase 2.
            df.to_csv("data/raw_jobs.csv", index=False)
            print("💾 Saved to data/raw_jobs.csv")
            
        else:
            print("❌ Connection worked, but the list of jobs is empty.")
            
    else:
        print(f"❌ Error Code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    get_jobs_safely()