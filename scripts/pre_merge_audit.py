import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def audit_raw_data():
    print("🔬 STARTING PRE-MERGE AUDIT...")
    
    # 1. SETUP PATHS
    current_script = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script)
    data_folder = os.path.join(project_root, 'data')
    
    # 2. LOAD FILES
    files = {
        "Jobs Data": "raw_jobs_multi.csv",
        "Economy Data": "economy_data.csv",
        "Cost of Living": "Cost_of_living_index.csv"
    }
    
    # Create a subplot for each file
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Missing Values Breakdown (Before Merging)', fontsize=16)
    
    for i, (name, filename) in enumerate(files.items()):
        filepath = os.path.join(data_folder, filename)
        
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            
            # Calculate Nulls (as percentage)
            nulls = df.isnull().mean() * 100
            nulls = nulls[nulls > 0] # Only show columns with missing data
            
            if len(nulls) > 0:
                sns.barplot(x=nulls.index, y=nulls.values, ax=axes[i], palette="viridis")
                axes[i].set_title(f"{name}\n({len(df)} Rows)")
                axes[i].set_ylabel("% Missing")
                axes[i].set_ylim(0, 100)
                axes[i].tick_params(axis='x', rotation=45)
            else:
                axes[i].text(0.5, 0.5, "No Missing Values! ✅", 
                             ha='center', va='center', fontsize=12)
                axes[i].set_title(f"{name}")
        else:
            axes[i].text(0.5, 0.5, "FILE NOT FOUND ❌", 
                         ha='center', va='center', fontsize=12, color='red')

    plt.tight_layout()
    output_path = os.path.join(project_root, 'pre_merge_audit.png')
    plt.savefig(output_path)
    print(f"🖼️  Saved Audit Chart to: {output_path}")
    print("   (Open this image to see the 'Before' state)")

if __name__ == "__main__":
    audit_raw_data()