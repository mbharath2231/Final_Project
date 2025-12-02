import pandas as pd
import os

def finalize_dataset():
    print("🧹 FINAL CLEANUP: Removing unwanted columns...")
    
    # 1. Load the messy master file
    current_script = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(os.path.dirname(current_script), 'data')
    df = pd.read_csv(os.path.join(data_folder, 'master_dataset.csv'))
    
    # 2. Define columns to DROP
    drop_cols = [
        'redirect_url', 'adref', '__CLASS__', 'salary_is_predicted',
        'location.__CLASS__', 'location.area', 
        'company.__CLASS__', 
        'category.label', 'category.__CLASS__', 'category.tag'
    ]
    
    # Drop them (errors='ignore' prevents crash if column missing)
    df = df.drop(columns=drop_cols, errors='ignore')
    
    # 3. RENAME columns for clarity
    df = df.rename(columns={
        'company.display_name': 'Company',
        'location.display_name': 'Location',
        'salary_min': 'Salary',
        'merge_city': 'City_Key'
    })
    
    # 4. HANDLE RENT INDEX (Optional: Fill with 0 or Drop)
    # We will fill with 0 so it doesn't break charts, but you could also drop it.
    df['Rent Index'] = df['Rent Index'].fillna(0)
    
    # 5. SAVE
    output_path = os.path.join(data_folder, 'clean_master_dataset.csv')
    df.to_csv(output_path, index=False)
    
    print(f"✨ Success! Saved polished data to: {output_path}")
    print(f"   Columns: {list(df.columns)}")

if __name__ == "__main__":
    finalize_dataset()