import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from config import TECH_SKILLS

def train_final_models():
    print("🤖 STARTING FINAL TRAINING (With Interactive Data Export)...")

    # 1. SETUP
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'cleaned_master_dataset.csv')
    models_dir = os.path.join(base_dir, 'models')
    if not os.path.exists(models_dir): os.makedirs(models_dir)

    df = pd.read_csv(data_path)
    
    # 2. SALARY MODEL
    print("   ... Training & Competing Models")
    features = ['Role', 'State']
    target = 'Salary'
    
    df_clean = df.dropna(subset=[target])
    X = pd.get_dummies(df_clean[features], drop_first=True)
    y = df_clean[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model A: Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_r2 = r2_score(y_test, lr_pred)
    lr_mae = mean_absolute_error(y_test, lr_pred)
    
    # Model B: Random Forest (Tuned)
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_r2 = r2_score(y_test, rf_pred)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    
    winner = "Random Forest" if rf_r2 > lr_r2 else "Linear Regression"
    print(f"      🏆 Winner: {winner} (R²: {max(rf_r2, lr_r2):.2f})")

    # --- NEW: SAVE PREDICTIONS FOR INTERACTIVE PLOT ---
    print("   ... Saving Test Data for App Visualization")
    eval_df = pd.DataFrame({
        "Actual_Salary": y_test,
        "Linear_Prediction": lr_pred,
        "Forest_Prediction": rf_pred
    })
    eval_df.to_csv(os.path.join(models_dir, 'test_predictions.csv'), index=False)

    # Save Best Model
    final_model = rf if winner == "Random Forest" else lr
    with open(os.path.join(models_dir, 'salary_model.pkl'), 'wb') as f:
        pickle.dump(final_model, f)
    with open(os.path.join(models_dir, 'model_columns.pkl'), 'wb') as f:
        pickle.dump(X.columns.tolist(), f)
        
    # Save Metrics
    metrics = {
        "Linear Regression": {"R²": lr_r2, "MAE": lr_mae},
        "Random Forest": {"R²": rf_r2, "MAE": rf_mae},
        "Winner": winner
    }
    with open(os.path.join(models_dir, 'model_comparison.pkl'), 'wb') as f:
        pickle.dump(metrics, f)

    # 3. SKILL EXTRACTOR
    print("   ... Training Skill Analyzer")
    df['desc_clean'] = df['description'].fillna("").str.lower()
    skill_data = []
    for skill in TECH_SKILLS:
        escaped = skill.lower().replace("+", "\+")
        mask = df['desc_clean'].str.contains(rf"\b{escaped}\b", regex=True)
        if mask.sum() > 2:
            val = df[mask]['Salary'].mean() - df[~mask]['Salary'].mean()
            skill_data.append({'word': skill, 'value': val})
            
    pd.DataFrame(skill_data).sort_values('value', ascending=False).to_csv(os.path.join(models_dir, 'top_skills.csv'), index=False)
    
    print("🎉 DONE. Interactive Data Ready.")

if __name__ == "__main__":
    train_final_models()