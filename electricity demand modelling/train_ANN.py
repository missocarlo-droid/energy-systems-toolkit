import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from merge_matrices import merge_peak_RAMP_and_ANN_to_matrix
import pdb

# --- 1. DATA PREPARATION ---
# Load your sensitivity matrix (31 days x stove columns)
df = pd.read_csv("Simulation_Results/RAMP_peaks_matrix_500-900.csv")

# Input (X): Stove counts from column headers
X = np.array(df.columns).astype(float).reshape(-1, 1) 
# Target (y): 31-day peak vectors (Transpose to get 1 row per stove count)
y = df.T.values 

# --- 2. SCALING ---
# We use separate scalers for Input and Output to help the NN converge
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y)

# Split 15% of data to verify that the model generalizes to "unseen" stove counts
X_train, X_val, y_train, y_val = train_test_split(
    X_scaled, y_scaled, test_size=0.15, random_state=42
)

# --- 3. TRAIN THE VECTOR-OUTPUT NN ---
# Funnel architecture: (128 -> 64 -> 32)
# 'tanh' is smoother for power curves; 'learning_rate_init=0.01' for faster convergence
model = MLPRegressor(
    hidden_layer_sizes=(128, 64, 32), 
    activation='tanh', 
    solver='adam',
    #alpha=0.1, # L2 regularization to prevent overfitting
    learning_rate_init=0.01,
    learning_rate='adaptive',
    max_iter=10000,
    early_stopping=True,
    #n_iter_no_change=25,
    validation_fraction=0.1,
    random_state=42
)

print("Training model... please wait.")
model.fit(X_train, y_train)

# --- 4. PERFORMANCE ASSESSMENT ---
# Predict on the full training set (re-transformed to Watts)
y_pred_scaled = model.predict(X_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled)

# Mathematical Metrics
mae = mean_absolute_error(y, y_pred)
r2 = r2_score(y, y_pred)
actual_std = np.std(y)
pred_std = np.std(y_pred)

print("\n" + "="*30)
print(f"--- Global Performance Report ---")
print(f"Overall R^2 Score: {r2:.4f}")
print(f"Mean Absolute Error: {mae:.2f} Watts")
print(f"Variance Capture Ratio: {pred_std/actual_std:.2%}")
print("="*30)


# --- 5. VISUAL CHECKS ---
# Plot 1: 31-Day Profile Check for a middle sample
sample_idx = len(X) // 2 
stoves = X[sample_idx][0]

plt.figure(figsize=(12, 5))
plt.plot(range(1, 32), y[sample_idx], 'bo-', label='Actual Simulation', alpha=0.6)
plt.plot(range(1, 32), y_pred[sample_idx], 'rx--', label='NN Reconstruction', linewidth=2)

plt.title(f'Performance Check: 31-Day Peak Profile for {int(stoves)} Stoves')
plt.xlabel('Day of Month')
plt.ylabel('Peak Power (Watts)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Plot 2: Residual Analysis (Check for bias)
residuals = y - y_pred
plt.figure(figsize=(10, 4))
plt.scatter(X, np.mean(residuals, axis=1), color='purple', alpha=0.6)
plt.axhline(0, color='red', linestyle='--')
plt.title("Residual Bias Check (Goal: Points scattered around 0)")
plt.xlabel("Number of Stoves")
plt.ylabel("Avg Error (Watts)")
plt.show()


# --- 6. SAVE MODEL AND SCALERS ---
joblib.dump(model, 'PEAK_vector_model.pkl')
joblib.dump(scaler_X, 'scaler_X_stoves.pkl')
joblib.dump(scaler_y, 'scaler_y_peaks.pkl')
print("\nModel and both Scalers saved successfully.")