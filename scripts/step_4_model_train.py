import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression

def train_production_models():
    print("🤖 STARTING PRODUCTION MODEL TRAINING...")

    # 1. SETUP PATHS
    current_script = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script)
    data_path = os.path.join(project_root, 'data', 'cleaned_master_dataset.csv')
    models_folder = os.path.join(project_root, 'models')
    
    if not os.path.exists(models_folder):
        os.makedirs(models_folder)

    # 2. LOAD DATA
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print("❌ Error: 'final_model_data.csv' not found.")
        return

    # ---------------------------------------------------------
    # MODEL A: SALARY PREDICTOR (Random Forest)
    # ---------------------------------------------------------
    print("   ... Training Salary Predictor (Random Forest)")
    
    # Features: Role (e.g. "Data Scientist") + State (e.g. "CA")
    # Note: We use State instead of City to make the model more robust/generalizable
    features = ['Role', 'State'] 
    target = 'Salary'
    
    # One-Hot Encode Categorical Features
    # This turns "Role" -> "Role_Data Scientist", "Role_DevOps", etc.
    train_df = df.dropna(subset=[target])
    X = pd.get_dummies(train_df[features], drop_first=True)
    y = train_df[target]
    
    # Train
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    # Save Model & Column List
    # We need the column list to know how to format input in the App
    with open(os.path.join(models_folder, 'salary_model.pkl'), 'wb') as f:
        pickle.dump(rf_model, f)
        
    with open(os.path.join(models_folder, 'model_columns.pkl'), 'wb') as f:
        pickle.dump(X.columns.tolist(), f)
        
    print(f"      ✅ Salary Model Saved. (R² Accuracy: {rf_model.score(X, y):.2f})")

    # ---------------------------------------------------------
    # MODEL B: SKILL EXTRACTOR (NLP)
    # ---------------------------------------------------------
    print("   ... Training Skill Analyzer (NLP)")
    
    # 1. Vectorize Descriptions (Turn words into numbers)
    # stop_words='english' removes common words like "the", "and"
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    
    descriptions = df['description'].fillna('')
    X_text = tfidf.fit_transform(descriptions)
    y_salary = df['Salary'].fillna(df['Salary'].mean())
    
    # 2. Train Linear Regression to find "Dollar Value" of each word
    lr_model = LinearRegression()
    lr_model.fit(X_text, y_salary)
    
    # 3. Extract Top Skills
    # We map the coefficient (value) back to the word
    feature_names = tfidf.get_feature_names_out()
    coefficients = lr_model.coef_
    
    word_values = pd.DataFrame({'word': feature_names, 'value': coefficients})
    
    # Filter for interesting skills (remove generic words if possible)
    # We take top 50 positive values
    top_skills = word_values.sort_values('value', ascending=False).head(50)
    
    top_skills.to_csv(os.path.join(models_folder, 'top_skills.csv'), index=False)
    
    print("      ✅ Skill Analyzer Saved.")
    print("\n" + "="*50)
    print("🎉 MODELS READY. You can now build the App!")
    print("="*50)

if __name__ == "__main__":
    train_production_models()