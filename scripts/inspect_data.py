import pandas as pd
import os

def inspect_datasets():
    print("🔬 INSPECTING YOUR RAW DATASETS\n")
    print("="*60)

    # 1. Setup Paths
    current_folder = os.path.dirname(os.path.abspath(__file__))
    project_folder = os.path.dirname(current_folder)
    data_folder = os.path.join(project_folder, 'data')

    # List of files we expect
    files = ["raw_jobs.csv", "economy_data.csv", "Cost_of_living_index.csv"]

    for filename in files:
        file_path = os.path.join(data_folder, filename)
        
        # Check if file exists first
        if os.path.exists(file_path):
            print(f"📂 FILE: {filename}")
            try:
                df = pd.read_csv(file_path)
                
                # A. Shape (How big is it?)
                print(f"   📐 Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
                
                # B. Missing Values (The "Nulls" you asked about)
                print("   ❓ Missing Values per Column:")
                print(df.isnull().sum())
                
                # C. The "Head" (First 3 rows sample)
                print("\n   👀 Sample Data (First 3 rows):")
                print(df.head(3))
                
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"❌ MISSING: Could not find {filename}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    inspect_datasets()