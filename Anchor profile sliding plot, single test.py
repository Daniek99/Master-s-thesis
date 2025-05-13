# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 19:55:26 2025

This code plots the displacements of anchor profiles as a function of time against the RC frame. 
The plot is for a single test run at a time. 

"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# === Settings ===
data_folder = r"C:\Users\danie\Documents\Master\Numerisk analyse\Tester\Config2Disp[1]"
SAVE_PLOTS = False
THRESHOLD = 0.3  # mm

# === File to Analyze ===
file_name = "ACQ_20240911_1644_Test21_T_CORR.xlsx"
file_path = os.path.join(data_folder, file_name)
print(f"\nProcessing file: {file_name}")

# Extract "TestXX" from file name
match = re.search(r"(Test\d+)", file_name)
test_label = match.group(1) if match else file_name

# Earthquake intensity lookup
test_intensity_lookup = {
    "Test02": 0.04, "Test03": 0.09, "Test04": 0.09, "Test05": 0.09, "Test06": 0.18,
    "Test07": 0.18, "Test08": 0.18, "Test09": 0.27, "Test10": 0.27, "Test11": 0.36,
    "Test12": 0.36, "Test13": 0.36, "Test14": 0.09, "Test15": 0.18, "Test16": 0.18,
    "Test17": 0.18, "Test18": 0.27, "Test19": 0.27, "Test20": 0.27, "Test21": 0.36,
    "Test22": 0.45, "Test23": 0.18, "Test24": 0.27, "Test25": 0.36, "Test26": 0.45,
    "Test27": 0.18, "Test28": 0.18
}
intensity_g = test_intensity_lookup.get(test_label, None)
intensity_label = f"{intensity_g:.2f} g" if intensity_g is not None else test_label

# Output folder
save_plot_folder = os.path.join(data_folder, "Disp2Plots")
os.makedirs(save_plot_folder, exist_ok=True)

try:
    # Load data
    df = pd.read_excel(file_path)
    if "Time (s)" not in df.columns:
        raise ValueError("Missing 'Time (s)' column.")

    if "accT" not in df.columns:
        raise ValueError("Acceleration column 'accT' not found in the file.")
    accel_series = df["accT"] / 1000  # Convert from mg to g

    time_series = df["Time (s)"]
    disp2_columns = [col for col in df.columns if col.startswith("Disp[2]")]
    valid_columns = []

    # Normalize and filter based on threshold
    df_disp2_normalized = pd.DataFrame()
    for col in disp2_columns:
        normalized = df[col] - df[col].iloc[0]
        if normalized.abs().max() >= THRESHOLD:
            df_disp2_normalized[col] = normalized
            valid_columns.append(col)
        else:
            print(f"Skipped {col} — all values within ±{THRESHOLD} mm")

    if not valid_columns:
        print("No valid Disp[2] columns after thresholding.")
    else:
        # Sort 1F above 2F
        valid_columns.sort(key=lambda col: (col.endswith("2F"), col))
        num_plots = len(valid_columns)

        fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3 * num_plots), sharex=True)
        if num_plots == 1:
            axes = [axes]

        plt.suptitle(f"{test_label} - L'Aquila {intensity_label}\n Relative displacement: Anchor profile of Friction Damper and RC frame",
                     fontsize=14, fontweight="bold")

        for i, col in enumerate(valid_columns):
            ax_disp = axes[i]
            series = df_disp2_normalized[col]
            ax_disp.plot(time_series, series, label=col)

            # Max
            max_idx = series.idxmax()
            max_time = time_series[max_idx]
            max_value = series[max_idx]
            # Max
            ax_disp.plot(max_time, max_value, 'o', color='red', markersize=8, label="Max disp")
            ax_disp.annotate(f"t = {max_time:.1f}s\n{max_value:.1f} mm", xy=(max_time, max_value),
                             xytext=(max_time + 0.5, max_value + 2), fontsize=8,
                             arrowprops=dict(arrowstyle="->", color="red"))

            # Min
            min_idx = series.idxmin()
            min_time = time_series[min_idx]
            min_value = series[min_idx]
            # Min
            ax_disp.plot(min_time, min_value, 'o', color='blue', markersize=8, label="Min disp")
            ax_disp.annotate(f"t = {min_time:.1f}s\n{min_value:.1f} mm", xy=(min_time, min_value),
                             xytext=(min_time + 0.5, min_value - 2), fontsize=8,
                             arrowprops=dict(arrowstyle="->", color="blue"))

            ax_disp.set_ylabel("Displacement (mm)")
            ax_disp.set_title(col)
            ax_disp.set_ylim(-3, 3)
            ax_disp.legend(loc="upper left")
            ax_disp.grid(True)

            # Acceleration overlay
            ax_accel = ax_disp.twinx()
            ax_accel.plot(time_series, accel_series, color="gray", alpha=0.3, label="Acceleration (g)")
            ax_accel.set_ylabel("Acceleration (g)", color="gray")
            ax_accel.tick_params(axis='y', labelcolor="gray")

            # Align y=0 on both axes
            disp_ylim = ax_disp.get_ylim()
            accel_min = accel_series.min()
            accel_max = accel_series.max()
            zero_pos_disp = (0 - disp_ylim[0]) / (disp_ylim[1] - disp_ylim[0])
            accel_range = accel_max - accel_min
            upper = 0 + (1 - zero_pos_disp) * accel_range
            lower = 0 - zero_pos_disp * accel_range
            ax_accel.set_ylim(lower - 0.1, upper + 0.1)
            ax_accel.legend(loc="upper right")

        axes[-1].set_xlabel("Time (s)")
        xticks = np.arange(0, 51, 5)
        for ax in axes:
            ax.set_xticks(xticks)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        if SAVE_PLOTS:
            plot_filename = f"{test_label}_disp2_stacked_plot.png"
            save_path = os.path.join(save_plot_folder, plot_filename)
            plt.savefig(save_path)
            print(f"Saved stacked plot to: {save_path}")

        plt.show()

except Exception as e:
    print(f"⚠️ Error processing {file_name}: {e}")
