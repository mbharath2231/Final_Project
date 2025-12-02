import requests
import pandas as pd
import json
import time
import os

BLS_API_KEY = "f6f87ced7a0c4da49d713c60b8c4d9cf"

def fetch_expanded_economy():
    print("📉 STARTING EXPANDED FETCH (90+ Cities)...")
    
    # ---------------------------------------------------------
    # 1. THE HARDCODED DICTIONARY (92 Cities)
    # ---------------------------------------------------------
    series_map = {
        # --- TIER 1: MAJOR HUBS ---
        "New York": "LAUMT363562000000003", "Los Angeles": "LAUMT063108000000003",
        "Chicago": "LAUMT171698000000003", "Dallas": "LAUMT481910000000003",
        "Houston": "LAUMT482642000000003", "Washington DC": "LAUMT114790000000003",
        "Miami": "LAUMT123310000000003", "Philadelphia": "LAUMT423798000000003",
        "Atlanta": "LAUMT131206000000003", "Boston": "LAUMT257165000000003",
        "Phoenix": "LAUMT043806000000003", "San Francisco": "LAUMT064186000000003",
        "Seattle": "LAUMT534266000000003", "San Diego": "LAUMT064174000000003",
        
        # --- TIER 2: TECH & BUSINESS CENTERS ---
        "Denver": "LAUMT081974000000003", "Austin": "LAUMT481242000000003",
        "San Jose": "LAUMT064194000000003", "Nashville": "LAUMT473498000000003",
        "Charlotte": "LAUMT371674000000003", "Raleigh": "LAUMT373958000000003",
        "Portland": "LAUMT413890000000003", "Minneapolis": "LAUMT273346000000003",
        "Detroit": "LAUMT261982000000003", "Tampa": "LAUMT124530000000003",
        "Orlando": "LAUMT123674000000003", "Baltimore": "LAUMT241258000000003",
        "St. Louis": "LAUMT294118000000003", "Pittsburgh": "LAUMT423830000000003",
        "Sacramento": "LAUMT064090000000003", "Las Vegas": "LAUMT322982000000003",
        "San Antonio": "LAUMT484170000000003", "Kansas City": "LAUMT292814000000003",
        "Columbus": "LAUMT391814000000003", "Indianapolis": "LAUMT182690000000003",
        "Cleveland": "LAUMT391746000000003", "Cincinnati": "LAUMT391714000000003",
        
        # --- TIER 3: MEDIUM & EMERGING CITIES (The "Hidden Gems") ---
        "Boise": "LAUMT161426000000003",       "Salt Lake City": "LAUMT494162000000003",
        "Des Moines": "LAUMT191978000000003",  "Madison": "LAUMT553154000000003",
        "Milwaukee": "LAUMT553334000000003",   "Buffalo": "LAUMT361538000000003",
        "Richmond": "LAUMT514006000000003",    "Virginia Beach": "LAUMT514726000000003",
        "Providence": "LAUMT447720000000003",  "Hartford": "LAUMT097345000000003",
        "New Orleans": "LAUMT223538000000003", "Louisville": "LAUMT213114000000003",
        "Memphis": "LAUMT473282000000003",     "Oklahoma City": "LAUMT403642000000003",
        "Tulsa": "LAUMT404614000000003",       "Albuquerque": "LAUMT351074000000003",
        "Tucson": "LAUMT044606000000003",      "El Paso": "LAUMT482134000000003",
        "Omaha": "LAUMT313654000000003",       "Honolulu": "LAUMT152798000000003",
        "Anchorage": "LAUMT021126000000003",   "Spokane": "LAUMT534406000000003",
        "Little Rock": "LAUMT053078000000003", "Knoxville": "LAUMT472894000000003",
        "Grand Rapids": "LAUMT262434000000003","Albany": "LAUMT361058000000003",
        "Rochester": "LAUMT364038000000003",   "Syracuse": "LAUMT364506000000003",
        "Allentown": "LAUMT421090000000003",   "Harrisburg": "LAUMT422542000000003",
        "Scranton": "LAUMT424254000000003",    "Charleston": "LAUMT451670000000003",
        "Greenville": "LAUMT452486000000003",  "Columbia": "LAUMT451790000000003",
        "Chattanooga": "LAUMT471686000000003", "Birmingham": "LAUMT011382000000003",
        "Huntsville": "LAUMT012662000000003",  "Jacksonville": "LAUMT122726000000003",
        "Cape Coral": "LAUMT121598000000003",  "Sarasota": "LAUMT123584000000003",
        "Dayton": "LAUMT391938000000003",      "Toledo": "LAUMT394578000000003",
        "Akron": "LAUMT391042000000003",       "Worcester": "LAUMT257960000000003",
        "Springfield MA": "LAUMT257810000000003", "New Haven": "LAUMT097570000000003",
        "Bridgeport": "LAUMT097195000000003",  "Stamford": "LAUMT097195000000003"
    }
    
    all_series = list(series_map.values())
    print(f"   ✅ Loaded {len(all_series)} cities manually.")

    # ---------------------------------------------------------
    # 2. BATCH FETCH (50 per batch to respect API limits)
    # ---------------------------------------------------------
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    final_results = []
    
    for i, batch_ids in enumerate(chunker(all_series, 50)):
        print(f"       Batch {i+1}: Fetching {len(batch_ids)} cities...")
        
        headers = {'Content-type': 'application/json'}
        data = json.dumps({
            "seriesid": batch_ids,
            "startyear": "2024", 
            "endyear": "2024",
            "registrationkey": BLS_API_KEY
        })
        
        try:
            p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
            json_data = p.json()
            
            if 'Results' in json_data:
                for series in json_data['Results']['series']:
                    series_id = series['seriesID']
                    # Lookup city name
                    found = [k for k, v in series_map.items() if v == series_id]
                    city_name = found[0] if found else "Unknown"
                    
                    if len(series['data']) > 0:
                        latest = series['data'][0]
                        final_results.append({
                            "City": city_name,
                            "Unemployment_Rate": float(latest['value']),
                            "Month": latest['periodName']
                        })
            
            time.sleep(1) # Polite pause

        except Exception as e:
            print(f"       ❌ Batch Error: {e}")

    # ---------------------------------------------------------
    # 3. SAVE TO CSV
    # ---------------------------------------------------------
    if final_results:
        df_final = pd.DataFrame(final_results)
        
        # Path Logic
        current_folder = os.path.dirname(os.path.abspath(__file__))
        project_folder = os.path.dirname(current_folder)
        output_path = os.path.join(project_folder, 'data', 'economy_data.csv')
        
        df_final.to_csv(output_path, index=False)
        
        print("\n" + "="*50)
        print(f"🎉 SUCCESS! Downloaded data for {len(df_final)} cities.")
        print(f"💾 Saved to: {output_path}")
        print("="*50)
    else:
        print("❌ No data collected. Check API Key.")

if __name__ == "__main__":
    fetch_expanded_economy()