import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from config import TECH_SKILLS

class CustomKNNRegressor:
    """A K-Nearest Neighbors Regressor built from scratch using pure NumPy."""
    def __init__(self, k=5):
        self.k = k
        self.X_train = None
        self.y_train = None
        
    def fit(self, X, y):
        # FORCE arrays to float64 so NumPy math doesn't crash on boolean data
        self.X_train = np.array(X, dtype=np.float64)
        self.y_train = np.array(y, dtype=np.float64)
        
    def predict(self, X):
        # Force incoming test data to float64
        X_np = np.array(X, dtype=np.float64)
        predictions = []
        for x in X_np:
            # Calculate Euclidean distance
            distances = np.linalg.norm(self.X_train - x, axis=1)
            k_indices = np.argsort(distances)[:self.k]
            k_nearest_targets = self.y_train[k_indices]
            predictions.append(np.mean(k_nearest_targets))
        return np.array(predictions)

def train_final_models():
    print("🤖 STARTING ML PIPELINE...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'cleaned_master_dataset.csv')
    models_dir = os.path.join(base_dir, 'models')
    if not os.path.exists(models_dir): os.makedirs(models_dir)

    df = pd.read_csv(data_path)
    df = df.dropna(subset=['Salary', 'description'])

    # ==========================================
    # 2. FEATURE ENGINEERING
    # ==========================================
    print("   ... Engineering Features from Text")
    df['desc_clean'] = df['description'].str.lower()
    
    # Create binary columns for each tech skill (This makes the model much smarter)
    skill_cols = []
    for skill in TECH_SKILLS:
        col_name = f"skill_{skill.lower()}"
        escaped = skill.lower().replace("+", "\+")
        df[col_name] = df['desc_clean'].str.contains(rf"\b{escaped}\b", regex=True).astype(int)
        skill_cols.append(col_name)

    # Combine categorical data with our new engineered skills
    features_df = pd.get_dummies(df[['Role', 'State']], drop_first=True)
    X = pd.concat([features_df, df[skill_cols]], axis=1)
    y = df['Salary']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ==========================================
    # 3. COMPARING & TUNING MODELS (Rubric #3)
    # ==========================================
    print("   ... Training Model 1: Hand-Created KNN (Baseline)")
    custom_knn = CustomKNNRegressor(k=5)
    custom_knn.fit(X_train, y_train)
    knn_pred = custom_knn.predict(X_test)
    knn_r2 = r2_score(y_test, knn_pred)

    print("   ... Training Model 2: Sklearn Linear Regression")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_r2 = r2_score(y_test, lr_pred)

    print("   ... Training Model 3: Random Forest with GridSearchCV")
    # Define hyperparameter grid for tuning
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [10, 20, None]
    }
    grid_search = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=3, n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    rf_best = grid_search.best_estimator_
    rf_pred = rf_best.predict(X_test)
    rf_r2 = r2_score(y_test, rf_pred)
    
    print(f"      🏆 Custom KNN R²: {knn_r2:.2f}")
    print(f"      🏆 Linear Reg R²: {lr_r2:.2f}")
    print(f"      🏆 Tuned Forest R²: {rf_r2:.2f} (Best Params: {grid_search.best_params_})")

    knn_mae = mean_absolute_error(y_test, knn_pred)
    lr_mae = mean_absolute_error(y_test, lr_pred)
    rf_mae = mean_absolute_error(y_test, rf_pred)

    # Save Metrics for ALL THREE Models
    metrics = {
        "Custom KNN": {"R²": knn_r2, "MAE": knn_mae},
        "Linear Regression": {"R²": lr_r2, "MAE": lr_mae},
        "Random Forest (Tuned)": {"R²": rf_r2, "MAE": rf_mae},
        "Winner": "Random Forest (Tuned)"
    }
    
    with open(os.path.join(models_dir, 'model_comparison.pkl'), 'wb') as f:
        pickle.dump(metrics, f)

    # Save the best model
    with open(os.path.join(models_dir, 'salary_model.pkl'), 'wb') as f:
        pickle.dump(rf_best, f)
    with open(os.path.join(models_dir, 'model_columns.pkl'), 'wb') as f:
        pickle.dump(X.columns.tolist(), f)

    # Save Skills Data (Keep your existing visualizer code intact)
    skill_data = []
    for skill in TECH_SKILLS:
        col = f"skill_{skill.lower()}"
        if df[col].sum() > 2:
            val = df[df[col]==1]['Salary'].mean() - df[df[col]==0]['Salary'].mean()
            skill_data.append({'word': skill, 'value': val})
    pd.DataFrame(skill_data).sort_values('value', ascending=False).to_csv(os.path.join(models_dir, 'top_skills.csv'), index=False)
    
    print("🎉 DONE. Full Machine Learning Pipeline Complete.")

if __name__ == "__main__":
    train_final_models()