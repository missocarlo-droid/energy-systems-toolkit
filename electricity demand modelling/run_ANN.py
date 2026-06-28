import pandas as pd
import joblib
import numpy as np

def generate_missing_peaks(model_path, scaler_x_path, scaler_y_path, existing_stoves, start, end, step=5):
    """
    Generates synthetic 31-day peaks for stove counts not present in existing_stoves.
    """
    # 1. Load the Model and Scaler
    model = joblib.load(model_path)
    scaler_X = joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    
    # 2. Define the target grid (e.g., 500, 505, 510...)
    target_stoves = np.arange(start, end + step, step)
    
    # 3. Identify which ones are missing
    # We convert both to sets to find the difference
    missing_stoves = sorted(list(set(target_stoves) - set(existing_stoves)))
    
    if not missing_stoves:
        print("No missing stove counts found for the given step.")
        return pd.DataFrame()

    # 4. Predict for missing values
    X_missing = np.array(missing_stoves).reshape(-1, 1)
    X_scaled = scaler_X.transform(X_missing)
    
    # Generate the 31-day vectors
    synthetic_data_scaled = model.predict(X_scaled)

    # The scaler expects the same shape as the output (StoveCounts, 31)
    synthetic_data_watts = scaler_y.inverse_transform(synthetic_data_scaled)
    
    # 5. Format into a DataFrame
    synthetic_df = pd.DataFrame(
        synthetic_data_watts.T, 
        columns=missing_stoves,
        index=[f"Day_{i+1}" for i in range(31)]
    )
    
    return synthetic_df