import pandas as pd

def merge_peak_RAMP_and_ANN_to_matrix(synthetic_peaks, peakMatrix):
    # Standardize the Synthetic Matrix
    if not synthetic_peaks.empty:
        synthetic_peaks.columns = synthetic_peaks.columns.astype(int)
        # Match the original index exactly (0-30)
        synthetic_peaks.index = range(len(synthetic_peaks))

        # --- 4. Merge and Sort ---
        master_peak_matrix = pd.concat([peakMatrix, synthetic_peaks], axis=1)
        master_peak_matrix = master_peak_matrix.sort_index(axis=1)

        print("Merge successful. Matrix shape:", master_peak_matrix.shape)
    else:
        master_peak_matrix = peakMatrix

    return master_peak_matrix