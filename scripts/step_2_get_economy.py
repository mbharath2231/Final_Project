import requests
import json
import pandas as pd
import os  # <--- NEW TOOL: Helps us find folders on your computer

# ==========================================
# 👇 PASTE YOUR BLS KEY HERE
# ==========================================
BLS_API_KEY = "f6f87ced7a0c4da49d713c60b8c4d9cf"

def get_economy_data():
    print("📉 Connecting to Bureau of Labor Statistics...")
    
    # 1. The Map: "City Name" -> "BLS Series ID"
    series_map = {
        "New York": "LAUMT363562000000003",
        "Los Angeles": "LAUMT063108000000003",
        "Chicago": "LAUMT171698000000003",
        "Austin": "LAUMT481242000000003",
        "San Francisco": "LAUMT064186000000003",
        "Seattle": "LAUMT534266000000003",
        "Detroit": "LAUMT261982000000003",
        "Boston": "LAUMT257165000000003"
    }
    
    # 2. The Payload
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": list(series_map.values()), 
        "startyear": "2024", 
        "endyear": "2024",
        "registrationkey": BLS_API_KEY
    })
    
    # 3. Send Request
    try:
        url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 200:
            json_data = response.json()
            
            # Check for API errors
            if json_data['status'] != "REQUEST_SUCCEEDED":
                print(f"⚠️ BLS Message: {json_data['message']}")

            clean_data = []
            
            if 'Results' in json_data:
                for series in json_data['Results']['series']:
                    series_id = series['seriesID']
                    # Find City Name
                    city_name = [k for k, v in series_map.items() if v == series_id][0]
                    
                    if len(series['data']) > 0:
                        latest = series['data'][0]
                        clean_data.append({
                            "City": city_name,
                            "Unemployment_Rate": float(latest['value']),
                            "Month": latest['periodName']
                        })
                        print(f"   Found data for {city_name}: {latest['value']}%")
            
            # --- THE FIX IS HERE ---
            if clean_data:
                df = pd.DataFrame(clean_data)
                
                # 1. Get the folder where THIS script is running (F:\Final_Project\scripts)
                current_folder = os.path.dirname(os.path.abspath(__file__))
                
                # 2. Go UP one level to the project folder (F:\Final_Project)
                project_folder = os.path.dirname(current_folder)
                
                # 3. Go DOWN into the data folder (F:\Final_Project\data)
                data_folder = os.path.join(project_folder, 'data')
                
                # 4. Create the 'data' folder if it doesn't exist (Safety net)
                if not os.path.exists(data_folder):
                    os.makedirs(data_folder)
                    print(f"   Created missing folder: {data_folder}")
                
                # 5. Define the full path for the CSV
                output_path = os.path.join(data_folder, 'economy_data.csv')
                
                df.to_csv(output_path, index=False)
                print(f"🎉 Success! Saved to: {output_path}")
            else:
                print("❌ No data found. (Check your API Key)")
                
        else:
            print(f"❌ Error Code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ A crash occurred: {e}")

if __name__ == "__main__":
    get_economy_data()