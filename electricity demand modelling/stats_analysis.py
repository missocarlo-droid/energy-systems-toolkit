import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from run_ANN import generate_missing_peaks
from merge_matrices import merge_peak_RAMP_and_ANN_to_matrix
import pdb

RampMatrix = pd.read_csv("Simulation_Results/RAMP_peaks_matrix_500-900.csv")
RampMatrix.columns = RampMatrix.columns.astype(int)
RampMatrix.index = range(len(RampMatrix))

existing_stoves = RampMatrix.columns.astype(int).tolist()

# Generate only the new 5-step columns
AnnMatrix = generate_missing_peaks(
    model_path='PEAK_vector_model.pkl',
    scaler_x_path='scaler_X_stoves.pkl',
    scaler_y_path='scaler_y_peaks.pkl',
    existing_stoves=existing_stoves,
    start=500,
    end=900,
    step=5
)

df = merge_peak_RAMP_and_ANN_to_matrix(AnnMatrix, RampMatrix)

df.to_csv("Simulation_Results/master_peaks_matrix.csv", index=False)

#pdb.set_trace()
threshold = 850500 # Example threshold in Watts
tol = 5.0 # Risk Tolerance in percent

# 1. Calculate Stats for each Stove Count
stats = []
# Assuming 'df' is your original matrix where columns = stove counts
for col in df.columns:
    peaks = df[col].dropna().values
    mu = np.mean(peaks)
    sigma = np.std(peaks)
    
    # Calculate 5th and 95th percentiles (Empirical from your 31 days)
    p5 = np.percentile(peaks, 5)
    p95 = np.percentile(peaks, 95)

    prob_exceeding = 1 - norm.cdf(threshold, mu, sigma)
    
    stats.append({
        'Stoves': int(col),
        'Mean_Peak': mu,
        'Std_Dev': sigma,
        '5th_Percentile': p5,
        '95th_Percentile': p95,
        'Risk_Exceeding_Threshold': prob_exceeding*100
    })

stats_df = pd.DataFrame(stats)

# 2. Plotting the Gaussian Clouds
plt.figure(figsize=(12, 6))

# Pick a few stove counts to visualize (e.g., start, middle, end)
sample_stoves = [stats_df['Stoves'].iloc[0], 
                 #stats_df['Stoves'].iloc[len(stats_df)//4], 
                 stats_df['Stoves'].iloc[len(stats_df)//2],
                 #stats_df['Stoves'].iloc[3*len(stats_df)//4],
                 stats_df['Stoves'].iloc[-1]]

for s in sample_stoves:
    row = stats_df[stats_df['Stoves'] == s].iloc[0]
    mu, sigma = row['Mean_Peak'], row['Std_Dev']
    
    # Create the x-axis range for this specific bell curve
    x = np.linspace(mu - 4*sigma, mu + 4*sigma, 100)
    y = norm.pdf(x, mu, sigma)
    
    line = plt.plot(x, y, label=f'{s} Stoves', linewidth=2)
    plt.fill_between(x, y, alpha=0.2, color=line[0].get_color())
    
    # Mark the 95th percentile (The "Danger Zone")
    plt.axvline(row['95th_Percentile'], color=line[0].get_color(), 
                linestyle='--', alpha=0.5)

plt.title('Probability Clouds: Distribution of Peaks per Stove Count')
plt.xlabel('Peak Power (Watts)')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.show()

# Optional: Plot the Risk Curve
stats_df['Risk_Smoothed'] = stats_df['Risk_Exceeding_Threshold'].rolling(window=5, center=True).mean().fillna(stats_df['Risk_Exceeding_Threshold'])
plt.figure(figsize=(10, 5))
#plt.plot(stats_df['Stoves'], stats_df['Risk_Exceeding_Threshold'], marker='o', color='red', linewidth=2)
plt.plot(stats_df['Stoves'], stats_df['Risk_Smoothed'], marker='o', color='red', linewidth=2)
plt.axhline(5, color='orange', linestyle='--', label='5% Risk Threshold')
plt.xlabel('Number of Stoves')
plt.ylabel('Probability of Exceeding Limit (%)')
plt.title(f'Risk Profile: Probability of Tripping at {threshold} Watts')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# 3. Output the Percentile Table
#print("\n--- Safety Limits Table (Watts) ---")
#print(stats_df[['Stoves', '5th_Percentile', 'Mean_Peak', '95th_Percentile', 'Risk_Exceeding_Threshold']].to_string(index=False))
# save to CSV if needed
stats_df.to_csv("stove_peak_stats.csv", index=False)


def find_max_safe_stoves(risk_df, tolerance_percent=1.0):
    """
    Finds the highest number of stoves where the risk of 
    exceeding the limit is below the tolerance_percent.
    """
    # Filter for rows where risk is less than or equal to tolerance
    safe_options = risk_df[risk_df['Risk_Smoothed'] <= tolerance_percent]
    
    if not safe_options.empty:
        # Get the row with the maximum number of stoves
        best_row = safe_options.sort_values(by='Stoves', ascending=False).iloc[0]
        return best_row
    else:
        return None

safe_deployment = find_max_safe_stoves(stats_df, tolerance_percent=tol)

if safe_deployment is not None:
    print(f"\n✅ DECISION SUPPORT (Target Risk: {tol}%):")
    print(f"To stay below {threshold} Watts with {100-tol}% confidence,")
    print(f"you should deploy NO MORE THAN {int(safe_deployment['Stoves'])} stoves.")
    print(f"Current Risk at this level: {safe_deployment['Risk_Smoothed']:.2f}%")
else:
    print(f"\n⚠️ WARNING: No safe stove count found for a {tol}% risk level at this limit.")

danger_zone = stats_df[stats_df['Risk_Smoothed'] > 50].head(1)
if not danger_zone.empty:
    print(f"\n⚠️ CRITICAL POINT: At {int(danger_zone['Stoves'].values[0])} stoves, "
          f"you have a >50% chance of exceeding the threshold.")
    
#calculate the average gap between the 95th and 50th percentiles as % of the mean peak

stats_df['Gap_95_50'] = stats_df['95th_Percentile'] - stats_df['Mean_Peak']
avg_gap = stats_df['Gap_95_50'].mean()
avg_gap_percent = (avg_gap / stats_df['Mean_Peak'].mean() * 100) if stats_df['Mean_Peak'].mean() != 0 else 0
print(f"\n📊 ANALYSIS INSIGHT: On average, the gap between the mean peak and the 95th percentile is {avg_gap:.2f} Watts, or {avg_gap_percent:.2f}% of the mean peak.")

#calculte the % rate of increase of the variance as the number of stoves increases
stats_df['Variance_Rate'] = stats_df['Std_Dev'].pct_change() * 100
avg_variance_rate = stats_df['Variance_Rate'].mean()  
print(f"\n📈 VARIANCE INSIGHT: On average, the variance of the peaks increases by {avg_variance_rate:.2f}% as the number of stoves increases.")